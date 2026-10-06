"""Batched rigid-body quadrotor simulator (NumPy).

Every array has a leading batch dimension n, so hundreds of drones -- each
with its own task parameters -- are stepped together. The command interface
is collective thrust + body rates (CTBR), the same setpoint PX4 accepts in
offboard mode, so policies trained here talk to the real flight stack in the
same units.

Pipeline per physics step (500 Hz):
  latency buffer -> onboard body-rate PI loop -> X-mixer -> motor lag
  -> per-motor efficiency -> rigid-body dynamics with drag, wind and gusts.
"""
import numba as nb
import numpy as np

from .config import DEFAULT_PLATFORM, DEFAULT_TIMING, GRAVITY, Platform, Timing
from .tasks import TaskBatch, nominal_tasks

E3 = np.array([0.0, 0.0, 1.0])
MAX_LATENCY = 6
GUST_TAU = 0.5  # s, Ornstein-Uhlenbeck correlation time


def skew(v):
    z = np.zeros(v.shape[:-1])
    return np.stack([
        np.stack([z, -v[..., 2], v[..., 1]], -1),
        np.stack([v[..., 2], z, -v[..., 0]], -1),
        np.stack([-v[..., 1], v[..., 0], z], -1),
    ], -2)


def so3_exp(phi):
    """Rodrigues' formula, batched over leading dims."""
    th = np.linalg.norm(phi, axis=-1, keepdims=True)
    small = th < 1e-8
    th_safe = np.where(small, 1.0, th)
    K = skew(phi / th_safe)
    s = np.where(small, 0.0, np.sin(th))[..., None]
    c = np.where(small, 0.0, 1 - np.cos(th))[..., None]
    return np.eye(3) + s * K + c * (K @ K)


def orthonormalize(R):
    x = R[..., :, 0]
    y = R[..., :, 1]
    x = x / np.linalg.norm(x, axis=-1, keepdims=True)
    z = np.cross(x, y)
    z = z / np.linalg.norm(z, axis=-1, keepdims=True)
    y = np.cross(z, x)
    return np.stack([x, y, z], -1)


def yaw_rotation(yaw):
    c, s = np.cos(yaw), np.sin(yaw)
    R = np.zeros(yaw.shape + (3, 3))
    R[..., 0, 0], R[..., 0, 1] = c, -s
    R[..., 1, 0], R[..., 1, 1] = s, c
    R[..., 2, 2] = 1.0
    return R


def mixer(platform: Platform):
    """Map motor thrusts f (4) -> [T, tau_x, tau_y, tau_z]. PX4 quad-X order."""
    a = platform.arm_length / np.sqrt(2)
    x = np.array([a, -a, a, -a])
    y = np.array([-a, a, a, -a])
    s = np.array([1.0, 1.0, -1.0, -1.0]) * platform.yaw_moment_coeff
    return np.stack([np.ones(4), y, -x, s])


class QuadSim:
    def __init__(self, n: int, platform: Platform = DEFAULT_PLATFORM,
                 timing: Timing = DEFAULT_TIMING, seed: int = 0):
        self.n, self.pf, self.tm = n, platform, timing
        self.rng = np.random.default_rng(seed)
        self.M = mixer(platform)
        self.Minv = np.linalg.inv(self.M)
        self.J_nom = np.array(platform.inertia)
        self.set_tasks(nominal_tasks(n))
        self.reset(np.zeros((n, 3)) + [0, 0, 1.0])

    # ------------------------------------------------------------------ setup
    def set_tasks(self, tasks: TaskBatch):
        assert len(tasks) == self.n
        self.tasks = tasks
        self.mass = self.pf.mass * tasks.mass_scale
        # payload sits near the centre: inertia grows more slowly than mass
        self.J = self.J_nom[None] * (1 + 0.5 * (tasks.mass_scale - 1))[:, None]
        self.kdrag = self.pf.drag_coeff * tasks.drag_scale
        self.eff = tasks.motor_eff
        self.lat = tasks.latency_steps.astype(int)

    def reset(self, p, yaw=None, v=None):
        n = self.n
        self.p = np.array(p, dtype=np.float64).reshape(n, 3)
        self.v = np.zeros((n, 3)) if v is None else np.array(v, dtype=np.float64)
        self.R = yaw_rotation(np.zeros(n) if yaw is None else np.asarray(yaw, float))
        self.w = np.zeros((n, 3))
        self.w_int = np.zeros((n, 3))
        hover = self.mass * GRAVITY / 4.0 / self.eff.mean(1)
        self.f_motor = np.repeat(hover[:, None], 4, 1)
        self.gust = np.zeros((n, 3))
        self.cmd_buf = np.zeros((MAX_LATENCY + 1, n, 4))
        self.cmd_buf[:, :, 0] = self.pf.hover_thrust
        self.acc = np.zeros((n, 3))
        self.t = 0.0

    # --------------------------------------------------------------- stepping
    def step(self, thrust_cmd, rate_cmd):
        """Advance one controller tick (control_dt) with a CTBR command."""
        cmd = np.concatenate([np.asarray(thrust_cmd, float).reshape(-1, 1), rate_cmd], 1)
        self.cmd_buf = np.roll(self.cmd_buf, 1, axis=0)
        self.cmd_buf[0] = cmd
        applied = self.cmd_buf[self.lat, np.arange(self.n)]
        sub = self.tm.substeps
        noise = self.rng.standard_normal((self.n, sub, 3))
        pf = self.pf
        _physics_kernel(self.p, self.v, self.R, self.w, self.w_int, self.f_motor, self.gust, self.acc,
                        applied, noise, self.mass, self.J, self.J_nom, self.kdrag, self.eff,
                        self.tasks.wind, self.tasks.gust_std, self.M, self.Minv,
                        np.array(pf.rate_gain), pf.rate_int_gain, pf.max_rate, pf.max_motor_thrust, pf.motor_tau,
                        GRAVITY, GUST_TAU, self.tm.physics_dt, sub)
        self.t += self.tm.control_dt

    # ----------------------------------------------------------------- helpers
    def tilt(self):
        return np.arccos(np.clip(self.R[:, 2, 2], -1, 1))

    def yaw(self):
        return np.arctan2(self.R[:, 1, 0], self.R[:, 0, 0])


@nb.njit(cache=True, fastmath=True)
def _physics_kernel(p, v, R, w, w_int, f_motor, gust, acc_out, cmd, noise, mass, J, J_nom, kdrag, eff,
                    wind, gust_std, M, Minv, rate_gain, rate_ki, max_rate, f_max, motor_tau, g, gust_tau,
                    dt, substeps):
    n = p.shape[0]
    tau_c = np.zeros(3)
    wc = np.zeros(3)
    f = np.zeros(4)
    Rn = np.zeros((3, 3))
    Ex = np.zeros((3, 3))
    for i in range(n):
        T_c = cmd[i, 0]
        for k in range(3):
            wc[k] = min(max(cmd[i, 1 + k], -max_rate), max_rate)
        for s in range(substeps):
            # onboard body-rate PI loop (as in PX4) with nominal inertia + gyro feedforward
            for k in range(3):
                w_int[i, k] = min(max(w_int[i, k] + (wc[k] - w[i, k]) * dt, -0.5), 0.5)
            jw0 = J_nom[0] * w[i, 0]; jw1 = J_nom[1] * w[i, 1]; jw2 = J_nom[2] * w[i, 2]
            tau_c[0] = J_nom[0] * (rate_gain[0] * (wc[0] - w[i, 0]) + rate_ki * w_int[i, 0]) + (w[i, 1] * jw2 - w[i, 2] * jw1)
            tau_c[1] = J_nom[1] * (rate_gain[1] * (wc[1] - w[i, 1]) + rate_ki * w_int[i, 1]) + (w[i, 2] * jw0 - w[i, 0] * jw2)
            tau_c[2] = J_nom[2] * (rate_gain[2] * (wc[2] - w[i, 2]) + rate_ki * w_int[i, 2]) + (w[i, 0] * jw1 - w[i, 1] * jw0)
            # PX4-style desaturation: keep roll/pitch, scale yaw down, then shift thrust
            yaw_scale = 1.0
            for m in range(4):
                frp = Minv[m, 0] * T_c + Minv[m, 1] * tau_c[0] + Minv[m, 2] * tau_c[1]
                fy = Minv[m, 3] * tau_c[2]
                fc = frp + fy
                if fc > f_max and fy > 0.0:
                    yaw_scale = min(yaw_scale, max(0.0, (f_max - frp) / fy))
                elif fc < 0.0 and fy < 0.0:
                    yaw_scale = min(yaw_scale, max(0.0, -frp / fy))
            hi = -1e9
            lo = 1e9
            for m in range(4):
                fc = (Minv[m, 0] * T_c + Minv[m, 1] * tau_c[0] + Minv[m, 2] * tau_c[1]
                      + yaw_scale * Minv[m, 3] * tau_c[2])
                f[m] = fc
                hi = max(hi, fc)
                lo = min(lo, fc)
            shift = 0.0
            if hi > f_max and lo >= 0.0:
                shift = max(f_max - hi, -lo)
            elif lo < 0.0 and hi <= f_max:
                shift = min(-lo, f_max - hi)
            for m in range(4):
                fc = min(max(f[m] + shift, 0.0), f_max)
                f_motor[i, m] += (fc - f_motor[i, m]) * (dt / motor_tau)
                f[m] = f_motor[i, m] * eff[i, m]
            T = 0.0
            tq0 = 0.0; tq1 = 0.0; tq2 = 0.0
            for m in range(4):
                T += M[0, m] * f[m]
                tq0 += M[1, m] * f[m]
                tq1 += M[2, m] * f[m]
                tq2 += M[3, m] * f[m]
            # Ornstein-Uhlenbeck gusts
            sq = gust_std[i] * np.sqrt(2.0 * dt / gust_tau)
            for k in range(3):
                gust[i, k] += -gust[i, k] * (dt / gust_tau) + sq * noise[i, s, k]
            for k in range(3):
                vrel = v[i, k] - wind[i, k] - gust[i, k]
                a = R[i, k, 2] * T / mass[i] - kdrag[i] / mass[i] * vrel
                if k == 2:
                    a -= g
                acc_out[i, k] = a
                v[i, k] += a * dt
                p[i, k] += v[i, k] * dt
            # rotational dynamics with true (payload-scaled) inertia
            jw0 = J[i, 0] * w[i, 0]; jw1 = J[i, 1] * w[i, 1]; jw2 = J[i, 2] * w[i, 2]
            w0 = w[i, 0] + dt * (tq0 - (w[i, 1] * jw2 - w[i, 2] * jw1)) / J[i, 0]
            w1 = w[i, 1] + dt * (tq1 - (w[i, 2] * jw0 - w[i, 0] * jw2)) / J[i, 1]
            w2 = w[i, 2] + dt * (tq2 - (w[i, 0] * jw1 - w[i, 1] * jw0)) / J[i, 2]
            w[i, 0] = w0; w[i, 1] = w1; w[i, 2] = w2
            # R <- R exp(w dt)
            px = w0 * dt; py = w1 * dt; pz = w2 * dt
            th = np.sqrt(px * px + py * py + pz * pz)
            if th > 1e-10:
                ax = px / th; ay = py / th; az = pz / th
                sn = np.sin(th); cs = 1.0 - np.cos(th)
                Ex[0, 0] = 1 - cs * (ay * ay + az * az); Ex[0, 1] = -sn * az + cs * ax * ay; Ex[0, 2] = sn * ay + cs * ax * az
                Ex[1, 0] = sn * az + cs * ax * ay; Ex[1, 1] = 1 - cs * (ax * ax + az * az); Ex[1, 2] = -sn * ax + cs * ay * az
                Ex[2, 0] = -sn * ay + cs * ax * az; Ex[2, 1] = sn * ax + cs * ay * az; Ex[2, 2] = 1 - cs * (ax * ax + ay * ay)
                for r in range(3):
                    for c in range(3):
                        Rn[r, c] = R[i, r, 0] * Ex[0, c] + R[i, r, 1] * Ex[1, c] + R[i, r, 2] * Ex[2, c]
                for r in range(3):
                    for c in range(3):
                        R[i, r, c] = Rn[r, c]
            # ground contact
            if p[i, 2] < 0.0:
                p[i, 2] = 0.0
                v[i, 0] = 0.0; v[i, 1] = 0.0
                if v[i, 2] < 0.0:
                    v[i, 2] = 0.0
        # re-orthonormalize (Gram-Schmidt on columns)
        nx = np.sqrt(R[i, 0, 0] ** 2 + R[i, 1, 0] ** 2 + R[i, 2, 0] ** 2)
        for r in range(3):
            R[i, r, 0] /= nx
        d = R[i, 0, 0] * R[i, 0, 1] + R[i, 1, 0] * R[i, 1, 1] + R[i, 2, 0] * R[i, 2, 1]
        for r in range(3):
            R[i, r, 1] -= d * R[i, r, 0]
        ny = np.sqrt(R[i, 0, 1] ** 2 + R[i, 1, 1] ** 2 + R[i, 2, 1] ** 2)
        for r in range(3):
            R[i, r, 1] /= ny
        R[i, 0, 2] = R[i, 1, 0] * R[i, 2, 1] - R[i, 2, 0] * R[i, 1, 1]
        R[i, 1, 2] = R[i, 2, 0] * R[i, 0, 1] - R[i, 0, 0] * R[i, 2, 1]
        R[i, 2, 2] = R[i, 0, 0] * R[i, 1, 1] - R[i, 1, 0] * R[i, 0, 1]
