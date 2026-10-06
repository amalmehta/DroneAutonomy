"""Point-to-point navigation through unknown cluttered rooms (batched).

The modular stack per drone:
  depth camera -> occupancy map -> A* global path -> carrot point 1.5 m ahead
  -> local policy (RL / meta-RL, or a classical follower) -> velocity command
  -> classical geometric controller -> thrust + body rates -> dynamics.

planner="oracle"  carrot from a Dijkstra field on the true map (fast; training)
planner="mapping" carrot from A* on the map built online from depth (evaluation)
planner="none"    end-to-end baseline: the "carrot" is just the goal direction
"""
import numpy as np

from ..config import DEFAULT_PLATFORM, DEFAULT_TIMING, Platform, Timing
from ..control import GeometricController
from ..dynamics import QuadSim, yaw_rotation
from ..mapping import OccupancyMap
from ..perception import DepthCamera, render_depth
from ..planning import NEIGH, NEIGH_COST, astar, carrot_on_path, dijkstra_field, field_carrot_kernel, inflate, \
    line_free, nearest_free, to_cell
from ..tasks import TaskBatch
from ..world import DRONE_RADIUS, ROOM, Worlds, collides, generate, true_occupancy

RES = 0.2
LOOKAHEAD = 1.5
V_MAX = np.array([1.5, 1.0, 0.6])    # forward, lateral, vertical (m/s)
YAW_RATE_MAX = 1.2
GOAL_TOL = 0.5
LEASH = 0.5
OCC_THRESHOLD = 0.6  # log-odds; one hit marks a voxel occupied
REPULSE_RANGE, REPULSE_GAIN = 1.0, 0.8
CLEARANCE = 0.15   # m of safety margin beyond the drone radius when planning


class WorldPool:
    """Pre-generated worlds with their true-map distance fields."""

    def __init__(self, n, seed, density=1.0):
        rng = np.random.default_rng(seed)
        self.worlds = generate(n, rng, density)
        fields = []
        for i in range(n):
            # exact clearance: voxel centres closer than radius + margin are blocked
            blocked = true_occupancy(self.worlds, i, RES, DRONE_RADIUS + CLEARANCE)
            g = nearest_free(blocked, to_cell(self.worlds.goal[i], RES, blocked.shape))
            fields.append(dijkstra_field(blocked, g, NEIGH, NEIGH_COST).astype(np.float32) * RES)
        self.fields = np.stack(fields)
        self.n = n

    def take(self, idx):
        w = self.worlds
        return Worlds(w.cyl[idx], w.box[idx], w.start[idx], w.goal[idx]), self.fields[idx]


class NavEnv:
    cam = DepthCamera()
    obs_dim = DepthCamera().rows * DepthCamera().cols + 16
    act_dim = 3

    def __init__(self, n, pool: WorldPool, planner="oracle", local="policy", adaptive=False, horizon=300,
                 platform: Platform = DEFAULT_PLATFORM, timing: Timing = DEFAULT_TIMING, seed=0,
                 replan_every=5, map_cam=DepthCamera(cols=48, rows=24)):
        assert planner in ("oracle", "mapping", "none") and local in ("policy", "classical")
        self.n, self.pool, self.planner, self.local = n, pool, planner, local
        self.horizon, self.pf, self.tm = horizon, platform, timing
        self.rng = np.random.default_rng(seed)
        self.sim = QuadSim(n, platform, timing, seed=seed + 1)
        self.ctrl = GeometricController(n, platform, dt=timing.control_dt, adaptive=adaptive)
        self.ticks = int(round(timing.nav_policy_dt / timing.control_dt))
        self.rays = self.cam.body_rays()
        self.map_cam, self.map_rays = map_cam, map_cam.body_rays()
        self.replan_every = replan_every

    # ------------------------------------------------------------------- API
    def reset(self, tasks: TaskBatch, gains=None, seed=None, world_idx=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
            self.sim.rng = np.random.default_rng(seed + 1)
        n = self.n
        idx = self.rng.integers(0, self.pool.n, n) if world_idx is None else np.asarray(world_idx)
        self.world_idx = idx
        self.worlds, self.fields = self.pool.take(idx)
        self.sim.set_tasks(tasks)
        start, goal = self.worlds.start, self.worlds.goal
        d = goal - start
        self.yaw = np.arctan2(d[:, 1], d[:, 0])
        self.sim.reset(start, yaw=self.yaw)
        self.ctrl.reset()
        if gains is not None:
            self.ctrl.set_gains(gains)
        self.p_ref = start.copy()
        self.k = 0
        self.done = np.zeros(n, bool)
        self.success = np.zeros(n, bool)
        self.collision = np.zeros(n, bool)
        self.t_goal = np.full(n, np.nan)
        self.path_len = np.zeros(n)
        self.prev_action = np.zeros((n, 3))
        self.geo = self._geodesic(self.sim.p)
        self.geo0 = self.geo.copy()
        if self.planner == "mapping":
            self.maps = [OccupancyMap(RES) for _ in range(n)]
            self.paths = [None] * n
            self.blocked = [None] * n
            self._update_maps()
            self._replan()
        self.traj = [self.sim.p.copy()]
        return self._obs()

    def step(self, action=None):
        n = self.n
        alive = ~self.done
        if self.local == "classical":
            a = self._classical_action()
        else:
            a = np.clip(action, -1, 1)
        a = np.where(alive[:, None], a, 0.0)
        v_yaw = a * V_MAX
        Ry = yaw_rotation(self.yaw)
        v_cmd = np.einsum("nij,nj->ni", Ry, v_yaw)
        # yaw follows the carrot so the camera looks along the route
        to_c = self.carrot - self.sim.p
        desired_yaw = np.arctan2(to_c[:, 1], to_c[:, 0])
        dyaw = (desired_yaw - self.yaw + np.pi) % (2 * np.pi) - np.pi
        yaw_step = np.clip(dyaw, -YAW_RATE_MAX * self.tm.nav_policy_dt, YAW_RATE_MAX * self.tm.nav_policy_dt)
        hit = np.zeros(n, bool)
        p_before = self.sim.p.copy()
        for k in range(self.ticks):
            self.yaw = self.yaw + yaw_step / self.ticks
            self.p_ref = self.p_ref + v_cmd * self.tm.control_dt
            off = self.p_ref - self.sim.p
            dist = np.linalg.norm(off, axis=1, keepdims=True)
            self.p_ref = self.sim.p + off * np.minimum(1.0, LEASH / np.maximum(dist, 1e-9))
            T, rates = self.ctrl(self.sim.p, self.sim.v, self.sim.R, self.p_ref, v_cmd, np.zeros((n, 3)), self.yaw)
            self.sim.step(T, rates)
            hit |= collides(self.sim.p, self.worlds)
        self.k += 1
        frozen = self.done.copy()
        self.sim.p[frozen] = p_before[frozen]
        self.sim.v[frozen] = 0
        self.path_len += np.where(alive, np.linalg.norm(self.sim.p - p_before, axis=1), 0)

        geo = self._geodesic(self.sim.p)
        progress = np.clip(self.geo - geo, -1.0, 1.0)
        self.geo = geo
        reached = np.linalg.norm(self.sim.p - self.worlds.goal, axis=1) < GOAL_TOL
        hit &= alive
        reached &= alive & ~hit
        depth = self._depth()
        dmin = depth.min(1)
        reward = (progress - 0.01 - 0.1 * np.maximum(0, 0.8 - dmin)
                  - 0.02 * ((a - self.prev_action) ** 2).sum(1) + 5.0 * reached - 5.0 * hit)
        reward = np.where(alive, reward, 0.0)
        self.collision |= hit
        self.success |= reached
        self.t_goal = np.where(reached, self.k * self.tm.nav_policy_dt, self.t_goal)
        self.done |= hit | reached
        self.prev_action = a
        if self.planner == "mapping":
            self._update_maps()
            if self.k % self.replan_every == 0:
                self._replan()
        self.traj.append(self.sim.p.copy())
        obs = self._obs(depth)
        timeout = self.k >= self.horizon
        return obs, reward, self.done | timeout, {"crashed": self.done.copy(), "collision": self.collision.copy()}

    def metrics(self):
        return {"success": self.success.copy(), "collision": self.collision.copy(),
                "time": self.t_goal.copy(), "path_len": self.path_len.copy(),
                "remaining": np.where(self.success, 0.0, np.minimum(self.geo, self.geo0) / np.maximum(self.geo0, 1e-6))}

    # ------------------------------------------------------------- internals
    def _geodesic(self, p):
        c = to_cell(p, RES, self.fields.shape[1:])
        d = self.fields[np.arange(self.n), c[:, 0], c[:, 1], c[:, 2]].astype(np.float64)
        fallback = np.linalg.norm(p - self.worlds.goal, axis=1) * 1.5
        return np.where(np.isfinite(d), d, fallback)

    def _depth(self):
        return render_depth(self.cam, self.sim.p, self.sim.R, self.worlds, self.rng, self.rays)

    @property
    def carrot(self):
        if self.planner == "none":
            d = self.worlds.goal - self.sim.p
            L = np.linalg.norm(d, axis=1, keepdims=True)
            return self.sim.p + d * np.minimum(1.0, LOOKAHEAD / np.maximum(L, 1e-9))
        if self.planner == "oracle":
            cells = to_cell(self.sim.p, RES, self.fields.shape[1:])
            out = np.empty_like(cells)
            field_carrot_kernel(self.fields, cells, int(LOOKAHEAD / RES), NEIGH, out)
            c = (out + 0.5) * RES
            near = np.linalg.norm(self.worlds.goal - self.sim.p, axis=1) < LOOKAHEAD
            c[near] = self.worlds.goal[near]
            return c
        out = []
        for i, (pth, p, g) in enumerate(zip(self.paths, self.sim.p, self.worlds.goal)):
            c = g
            if pth is not None:
                for la in (LOOKAHEAD, 1.0, 0.6, 0.3):  # shorten until in line of sight
                    c = carrot_on_path(pth, p, la)
                    if line_free(self.blocked[i], p, c, RES, skip=0.3):
                        break
            out.append(c)
        return np.stack(out)

    def _update_maps(self):
        rng = self.rng
        ranges = render_depth(self.map_cam, self.sim.p, self.sim.R, self.worlds, rng, self.map_rays, invalid=np.nan)
        dirs = np.einsum("nij,mj->nmi", self.sim.R, self.map_rays)
        for i in range(self.n):
            if not self.done[i]:
                self.maps[i].integrate(self.sim.p[i], dirs[i], ranges[i], self.map_cam.max_range)

    def _replan(self):
        r_cells = int(np.ceil((DRONE_RADIUS + CLEARANCE) / RES))
        for i in range(self.n):
            if self.done[i]:
                continue
            blocked = inflate(self.maps[i].occupied(OCC_THRESHOLD), r_cells)
            # the room walls are known a priori (a cage of known size)
            blocked[:r_cells], blocked[-r_cells:], blocked[:, :r_cells], blocked[:, -r_cells:] = True, True, True, True
            blocked[:, :, :1], blocked[:, :, -r_cells:] = True, True
            # the drone's own voxel neighbourhood and the goal are known to be flyable
            for centre, r in ((self.sim.p[i], 1), (self.worlds.goal[i], r_cells)):
                c = to_cell(centre, RES, blocked.shape)
                lo, hi = np.maximum(c - r, 0), c + r + 1
                blocked[lo[0]:hi[0], lo[1]:hi[1], max(lo[2], 1):hi[2]] = False
            self.blocked[i] = blocked
            path = astar(blocked, self.sim.p[i], self.worlds.goal[i], RES)
            if path is not None:
                self.paths[i] = path

    def _front_min(self, depth):
        """Closest return in the central half of the image (what lies ahead)."""
        img = depth.reshape(-1, self.cam.rows, self.cam.cols)
        r, c = self.cam.rows, self.cam.cols
        return img[:, r // 4: r - r // 4, c // 4: c - c // 4].reshape(len(depth), -1).min(1)

    def _classical_action(self):
        """Classical local planner: pure pursuit of the carrot plus a depth-based
        repulsive field (artificial potential), slowing down near obstacles."""
        Ry = yaw_rotation(self.yaw)
        to_c = np.einsum("nji,nj->ni", Ry, self.carrot - self.sim.p)
        L = np.linalg.norm(to_c, axis=1, keepdims=True)
        depth = self._depth()
        dmin = self._front_min(depth)
        speed = np.clip((dmin - 0.5) / 1.0, 0.3, 1.0)
        # only fly where the camera can see: turn toward the carrot first
        heading = np.arctan2(to_c[:, 1], to_c[:, 0])
        speed = speed * np.clip(np.cos(heading), 0.0, 1.0) ** 4
        v = to_c / np.maximum(L, 1e-9) * speed[:, None] * np.minimum(1.0, L / 0.5)
        # repulsion from every depth return closer than REPULSE_RANGE (body ~ yaw frame)
        push = np.maximum(0.0, REPULSE_RANGE - depth) / REPULSE_RANGE      # (n, m)
        v -= REPULSE_GAIN * (push[:, :, None] * self.rays[None]).sum(1) / max(1, self.rays.shape[0] // 16)
        return np.clip(v / V_MAX, -1, 1)

    def _obs(self, depth=None):
        depth = self._depth() if depth is None else depth
        Ry = yaw_rotation(self.yaw)
        to_yaw = lambda v: np.einsum("nji,nj->ni", Ry, v)
        carrot_rel = to_yaw(self.carrot - self.sim.p)
        goal_rel = to_yaw(self.worlds.goal - self.sim.p)
        return np.column_stack([
            depth / self.cam.max_range,
            carrot_rel / LOOKAHEAD, np.clip(goal_rel / 10.0, -1.5, 1.5), to_yaw(self.sim.v) / 1.5,
            to_yaw(self.sim.R[:, :, 2]), self.sim.p[:, 2:3] / ROOM[2], self.prev_action,
        ]).astype(np.float32)
