"""Trajectory tracking under task-specific dynamics (batched).

The classical geometric controller always flies the drone. On top of it the
environment supports two meta-learning hooks:

* mode="residual": a policy adds a bounded correction to the controller's
  thrust + body-rate command every 20 ms (combo 1: meta-RL residual on classical).
* mode="gains": no per-step policy; each episode uses a gain vector chosen
  per drone (combo 2: meta-learned classical gains).

All n drones reset together and run a fixed horizon (synchronised episodes),
which is what episodic meta-RL algorithms want.
"""
import numpy as np

from ..config import DEFAULT_PLATFORM, DEFAULT_TIMING, Platform, Timing
from ..control import GeometricController
from ..dynamics import QuadSim
from ..tasks import TaskBatch

CENTER = np.array([0.0, 0.0, 1.5])
CRASH_ERR = 1.5           # m from the reference
CRASH_TILT = np.radians(70)
RESID_THRUST = 0.25       # x hover thrust
RESID_RATE = np.array([1.0, 1.0, 0.5])  # rad/s


class TrackingEnv:
    obs_dim = 29
    act_dim = 4

    def __init__(self, n, mode="residual", adaptive=False, horizon=200,
                 platform: Platform = DEFAULT_PLATFORM, timing: Timing = DEFAULT_TIMING, seed=0):
        assert mode in ("residual", "gains", "none")
        self.n, self.mode, self.horizon = n, mode, horizon
        self.pf, self.tm = platform, timing
        self.rng = np.random.default_rng(seed)
        self.sim = QuadSim(n, platform, timing, seed=seed + 1)
        self.ctrl = GeometricController(n, platform, dt=timing.control_dt, adaptive=adaptive)
        self.ticks = int(round(timing.tracking_policy_dt / timing.control_dt))

    # -------------------------------------------------------------- reference
    def _sample_refs(self):
        n = self.n
        K = 2
        A = self.rng.uniform(0.2, 1.0, (n, 3, K))
        A[:, 2] *= 0.3
        om = 2 * np.pi * self.rng.uniform(0.1, 0.5, (n, 3, K))
        sign = self.rng.choice([-1.0, 1.0], (n, 3, K))
        vmax = np.array([2.0, 2.0, 0.6])
        speed = (A * om).sum(-1)
        A *= np.minimum(1.0, vmax / speed)[..., None]
        hover = self.rng.random(n) < 0.15  # pure disturbance-rejection episodes
        A[hover] = 0.0
        self.ref_A, self.ref_w = A * sign, om

    def reference(self, t):
        A, w = self.ref_A, self.ref_w
        p = CENTER + (A * (1 - np.cos(w * t))).sum(-1)
        v = (A * w * np.sin(w * t)).sum(-1)
        a = (A * w * w * np.cos(w * t)).sum(-1)
        return p, v, a

    # ------------------------------------------------------------------- API
    def reset(self, tasks: TaskBatch, gains=None, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
            self.sim.rng = np.random.default_rng(seed + 1)
        self.tasks = tasks
        self.sim.set_tasks(tasks)
        self._sample_refs()
        self.sim.reset(np.tile(CENTER, (self.n, 1)))
        self.ctrl.reset()
        if gains is not None:
            self.ctrl.set_gains(gains)
        self.t = 0.0
        self.k = 0
        self.prev_action = np.zeros((self.n, 4))
        self.last_cmd = np.zeros((self.n, 4))
        self.done = np.zeros(self.n, bool)
        self.sq_err = np.zeros(self.n)
        self.steps_alive = np.zeros(self.n)
        return self._obs()

    def step(self, action=None):
        n = self.n
        a = np.zeros((n, 4)) if action is None else np.clip(action, -1, 1)
        if self.mode != "residual":
            a = np.zeros((n, 4))
        for _ in range(self.ticks):
            p_ref, v_ref, a_ref = self.reference(self.t)
            T, rates = self.ctrl(self.sim.p, self.sim.v, self.sim.R, p_ref, v_ref, a_ref)
            self.last_cmd = np.column_stack([T / self.pf.hover_thrust - 1, rates])
            T = T + RESID_THRUST * self.pf.hover_thrust * a[:, 0]
            rates = rates + RESID_RATE * a[:, 1:]
            self.ctrl.notify_applied_thrust(T)
            self.sim.step(T, rates)
            self.t += self.tm.control_dt
        self.k += 1
        p_ref, v_ref, _ = self.reference(self.t)
        err = np.linalg.norm(self.sim.p - p_ref, axis=1)
        crashed = (err > CRASH_ERR) | (self.sim.tilt() > CRASH_TILT) | (self.sim.p[:, 2] < 0.05) \
            | ~np.isfinite(err)
        alive = ~self.done
        reward = np.where(alive, np.exp(-np.nan_to_num(err, nan=9.0) / 0.25)
                          - 0.01 * (a ** 2).sum(1), 0.0)
        reward = np.where(alive & crashed, 0.0, reward)
        self.sq_err += np.where(alive, np.nan_to_num(err, nan=CRASH_ERR) ** 2, 0.0)
        self.steps_alive += alive
        self.done |= crashed
        self._freeze_crashed(p_ref)
        self.prev_action = a
        timeout = self.k >= self.horizon
        info = {"err": err, "crashed": self.done.copy()}
        return self._obs(), reward, self.done.copy() | timeout, info

    def _freeze_crashed(self, p_ref):
        d = self.done
        if d.any():  # park crashed drones on the reference so the batch stays finite
            self.sim.p[d] = p_ref[d]
            self.sim.v[d] = 0.0
            self.sim.w[d] = 0.0
            self.sim.R[d] = np.eye(3)

    def _obs(self):
        p_ref, v_ref, a_ref = self.reference(self.t)
        s = self.sim
        return np.column_stack([
            np.clip(p_ref - s.p, -1.5, 1.5), np.clip(v_ref - s.v, -3, 3), 0.3 * s.v,
            s.R[:, :, 0], s.R[:, :, 2], 0.3 * s.w, 0.2 * a_ref,
            self.prev_action, self.last_cmd * np.array([1, 0.3, 0.3, 0.3]),
        ]).astype(np.float32)

    def metrics(self):
        """Per-drone RMSE (crashed drones count CRASH_ERR for the rest of the episode)."""
        remaining = self.horizon - self.steps_alive
        rmse = np.sqrt((self.sq_err + remaining * CRASH_ERR ** 2) / self.horizon)
        return {"rmse": rmse, "crashed": self.done.copy()}
