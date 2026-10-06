"""Classical control: batched geometric position controller and L1 adaptation.

GeometricController maps a position/velocity/acceleration reference to a
collective-thrust + body-rate (CTBR) command. Gains are per-drone arrays so
meta-learning can tune them task by task. With adaptive=True it adds the
classical adaptive-control baseline, a piecewise-constant L1 augmentation:
it estimates a lumped acceleration disturbance (payload, wind, weak motor)
from a velocity state predictor and cancels its low-pass-filtered value.
"""
import numba as nb
import numpy as np

from .config import DEFAULT_GAINS, DEFAULT_PLATFORM, DEFAULT_TIMING, GRAVITY, Gains, Platform

L1_AS = 10.0      # predictor pole, 1/s
L1_CUTOFF = 5.0   # low-pass filter bandwidth, rad/s


class GeometricController:
    def __init__(self, n, platform: Platform = DEFAULT_PLATFORM, gains: Gains = DEFAULT_GAINS,
                 dt=DEFAULT_TIMING.control_dt, adaptive=False):
        self.n, self.pf, self.dt, self.adaptive = n, platform, dt, adaptive
        self.set_gains(gains.as_array())
        self.reset()

    def set_gains(self, g):
        g = np.asarray(g, dtype=np.float64)
        self.g = np.ascontiguousarray(np.tile(g, (self.n, 1)) if g.ndim == 1 else g)

    def reset(self, v=None):
        n = self.n
        self.integ = np.zeros((n, 3))
        self.last_T = np.full(n, self.pf.hover_thrust)
        self.v_hat = np.zeros((n, 3)) if v is None else np.array(v, dtype=np.float64)
        self.d_filt = np.zeros((n, 3))

    def __call__(self, p, v, R, p_ref, v_ref, a_ref, yaw_ref=None):
        n = self.n
        T = np.empty(n)
        rates = np.empty((n, 3))
        yaw = np.zeros(n) if yaw_ref is None else np.asarray(yaw_ref, dtype=np.float64)
        e = np.exp(-L1_AS * self.dt)
        _controller_kernel(
            np.ascontiguousarray(p), np.ascontiguousarray(v), np.ascontiguousarray(R),
            np.ascontiguousarray(p_ref, dtype=np.float64), np.ascontiguousarray(v_ref, dtype=np.float64),
            np.ascontiguousarray(a_ref, dtype=np.float64), yaw, self.g, self.integ,
            self.adaptive, self.v_hat, self.d_filt, self.last_T, -L1_AS * e / (1 - e),
            1 - np.exp(-L1_CUTOFF * self.dt), L1_AS, self.dt, self.pf.mass, GRAVITY,
            np.tan(np.radians(self.pf.max_tilt_deg)), 4 * self.pf.max_motor_thrust,
            self.pf.max_rate, T, rates)
        self.last_T = T.copy()
        return T, rates

    def notify_applied_thrust(self, T):
        """Tell the L1 predictor the thrust actually sent (e.g. after a residual)."""
        self.last_T = np.asarray(T, dtype=np.float64).copy()


@nb.njit(cache=True, fastmath=True)
def _controller_kernel(p, v, R, p_ref, v_ref, a_ref, yaw, g, integ, adaptive, v_hat, d_filt,
                       last_T, l1_gain, l1_alpha, a_s, dt, mass, grav, tan_tilt, T_max, max_rate,
                       T_out, rates_out):
    n = p.shape[0]
    a = np.zeros(3)
    b3d = np.zeros(3)
    b1d = np.zeros(3)
    b2d = np.zeros(3)
    for i in range(n):
        kp = (g[i, 0], g[i, 0], g[i, 1])
        kd = (g[i, 2], g[i, 2], g[i, 3])
        ki = (g[i, 4], g[i, 4], g[i, 5])
        for k in range(3):
            ep = min(max(p_ref[i, k] - p[i, k], -2.0), 2.0)
            ev = v_ref[i, k] - v[i, k]
            integ[i, k] = min(max(integ[i, k] + ep * dt, -4.0), 4.0)
            a[k] = a_ref[i, k] + kp[k] * ep + kd[k] * ev + ki[k] * integ[i, k]
        a[2] += grav
        if adaptive:
            for k in range(3):
                verr = v_hat[i, k] - v[i, k]
                sigma = l1_gain * verr
                d_filt[i, k] += l1_alpha * (sigma - d_filt[i, k])
                am = R[i, k, 2] * last_T[i] / mass + sigma - a_s * verr
                if k == 2:
                    am -= grav
                v_hat[i, k] += am * dt
                a[k] -= d_filt[i, k]
        # tilt and vertical-acceleration limits
        a[2] = max(a[2], 0.3 * grav)
        h = np.sqrt(a[0] * a[0] + a[1] * a[1])
        max_h = tan_tilt * a[2]
        if h > max_h:
            a[0] *= max_h / h
            a[1] *= max_h / h
        T = mass * (a[0] * R[i, 0, 2] + a[1] * R[i, 1, 2] + a[2] * R[i, 2, 2])
        T_out[i] = min(max(T, 0.0), T_max)
        na = np.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
        for k in range(3):
            b3d[k] = a[k] / na
        c, s = np.cos(yaw[i]), np.sin(yaw[i])
        # b2d = b3d x b1c, with b1c = (c, s, 0)
        b2d[0] = -b3d[2] * s
        b2d[1] = b3d[2] * c
        b2d[2] = b3d[0] * s - b3d[1] * c
        nb2 = np.sqrt(b2d[0] ** 2 + b2d[1] ** 2 + b2d[2] ** 2)
        for k in range(3):
            b2d[k] /= nb2
        b1d[0] = b2d[1] * b3d[2] - b2d[2] * b3d[1]
        b1d[1] = b2d[2] * b3d[0] - b2d[0] * b3d[2]
        b1d[2] = b2d[0] * b3d[1] - b2d[1] * b3d[0]
        # E = Rd^T R - R^T Rd ; e_R = 0.5 vee(E)
        # (Rd^T R)[r,c] = sum_k Rd[k,r] R[k,c] with Rd columns b1d,b2d,b3d
        A = np.zeros((3, 3))
        for r in range(3):
            for cc in range(3):
                acc = 0.0
                for k in range(3):
                    if r == 0:
                        rd = b1d[k]
                    elif r == 1:
                        rd = b2d[k]
                    else:
                        rd = b3d[k]
                    acc += rd * R[i, k, cc]
                A[r, cc] = acc
        e0 = 0.5 * (A[2, 1] - A[1, 2])
        e1 = 0.5 * (A[0, 2] - A[2, 0])
        e2 = 0.5 * (A[1, 0] - A[0, 1])
        rates_out[i, 0] = min(max(-g[i, 6] * e0, -max_rate), max_rate)
        rates_out[i, 1] = min(max(-g[i, 6] * e1, -max_rate), max_rate)
        rates_out[i, 2] = min(max(-g[i, 6] * e2, -max_rate), max_rate)
