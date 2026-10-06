"""Record real simulator flights for the website's replay viewer.

Writes website/data/demo.json with:
  flights   full-stack navigation episodes (depth camera -> occupancy map ->
            A* -> local planner -> geometric controller -> dynamics), with the
            map and plan captured as the drone builds them
  tracking  one figure-eight flown by the classical controller and by the L1
            adaptive controller under a heavy, windy, weak-motor task
"""
import base64
import json
from pathlib import Path

import numpy as np

from .envs.navigation import RES, WorldPool, NavEnv, OCC_THRESHOLD
from .envs.tracking import TrackingEnv
from .tasks import TaskBatch, nominal_tasks, fixed_eval_tasks

OUT = Path("website/data/demo.json")
SNAP_EVERY = 5   # policy steps (0.5 s) between map/plan snapshots
Z_BAND = (0.6, 2.2)  # m, slab of the 3D map projected to the top-down view


def _pack(mask2d):
    return base64.b64encode(np.packbits(mask2d.astype(np.uint8).ravel())).decode()


def _r(x, d=2):
    return np.round(np.asarray(x, dtype=float), d).tolist()


def record_flights(n_worlds=4, seed=0):
    pool = WorldPool(n_worlds, seed=2)
    tasks = TaskBatch.concat([nominal_tasks(n_worlds // 2), fixed_eval_tasks(n_worlds - n_worlds // 2, "test")])
    env = NavEnv(n_worlds, pool, planner="mapping", local="classical", seed=seed)
    env.reset(tasks, seed=seed, world_idx=np.arange(n_worlds))
    z0, z1 = int(Z_BAND[0] / RES), int(Z_BAND[1] / RES)
    frames = [[] for _ in range(n_worlds)]
    snaps = [[] for _ in range(n_worlds)]
    finished = np.full(n_worlds, -1)

    def capture(k):
        depth = env._depth()
        for i in range(n_worlds):
            if finished[i] >= 0:
                continue
            frames[i].append({"p": _r(env.sim.p[i]), "yaw": round(float(env.yaw[i]), 3),
                              "c": _r(env.carrot[i]),
                              "d": base64.b64encode(np.clip(depth[i] / env.cam.max_range * 255, 0, 255)
                                                    .astype(np.uint8).tobytes()).decode()})
            if k % SNAP_EVERY == 0:
                occ = env.maps[i].occupied(OCC_THRESHOLD)[:, :, z0:z1].any(2)
                path = env.paths[i]
                snaps[i].append({"k": k, "occ": _pack(occ), "path": None if path is None else _r(path)})

    capture(0)
    for k in range(1, env.horizon + 1):
        _, _, done, _ = env.step()
        capture(k)
        newly = env.done & (finished < 0)
        finished[newly] = k
        if env.done.all():
            break
    m = env.metrics()
    w = env.worlds
    feats = tasks.features()
    flights = []
    for i in range(n_worlds):
        flights.append({
            "world": int(i),
            "start": _r(w.start[i]), "goal": _r(w.goal[i]),
            "pillars": [_r(c) for c in w.cyl[i] if c[2] > 0],
            "boxes": [_r(b) for b in w.box[i] if b[3] > b[0]],
            "task": {"mass_scale": round(float(feats[i, 0]), 2), "weakest_motor": round(float(feats[i, 1]), 2),
                     "drag_scale": round(float(feats[i, 2]), 2), "wind": round(float(feats[i, 3]), 2),
                     "gust": round(float(feats[i, 4]), 2), "latency_ms": int(feats[i, 5]) * 10},
            "outcome": "reached goal" if m["success"][i] else ("collision" if m["collision"][i] else "timed out"),
            "time_s": None if not np.isfinite(m["time"][i]) else round(float(m["time"][i]), 1),
            "path_len": round(float(m["path_len"][i]), 1),
            "frames": frames[i], "snaps": snaps[i],
        })
    return flights, {
        "grid": [int(s) for s in env.maps[0].shape[:2]], "res": RES, "dt": env.tm.nav_policy_dt,
        "cam": {"cols": env.cam.cols, "rows": env.cam.rows, "hfov": env.cam.hfov_deg, "max_range": env.cam.max_range},
    }


def record_tracking(seed=3):
    task = TaskBatch(mass_scale=np.array([1.25]), motor_eff=np.array([[0.8, 1.0, 0.98, 0.97]]),
                     drag_scale=np.array([1.5]), wind=np.array([[2.0, 0.8, 0.0]]),
                     gust_std=np.array([0.5]), latency_steps=np.array([2]))
    out = {"task": {"mass_scale": 1.25, "weakest_motor": 0.8, "wind": 2.15, "gust": 0.5, "latency_ms": 20}}
    for name, adaptive in (("classical", False), ("l1", True)):
        env = TrackingEnv(1, mode="none", adaptive=adaptive, horizon=300, seed=seed)
        env.reset(task, seed=seed)
        A = np.zeros((1, 3, 2))
        A[0, 0, 0], A[0, 1, 1] = 1.0, 0.4          # figure-eight: y at twice x's frequency
        w = np.zeros((1, 3, 2))
        w[0, 0, 0], w[0, 1, 1] = 2 * np.pi * 0.25, 2 * np.pi * 0.5
        w[0, 2] = 1.0
        env.ref_A, env.ref_w = A, w
        P, R, E = [], [], []
        for _ in range(env.horizon):
            env.step(None)
            pr, _, _ = env.reference(env.t)
            P.append(env.sim.p[0].copy()); R.append(pr[0]); E.append(np.linalg.norm(env.sim.p[0] - pr[0]))
        out[name] = {"p": _r(P), "rmse": round(float(np.sqrt(np.mean(np.square(E)))), 3)}
        out["ref"] = _r(R)
    out["dt"] = 0.02
    return out


def demo(seed=0):
    flights, meta = record_flights(seed=seed)
    data = {"meta": meta, "flights": flights, "tracking": record_tracking()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    for f in flights:
        print(f"world {f['world']}: {f['outcome']} in {f['time_s']} s, {len(f['frames'])} frames")
    print(f"tracking RMSE classical {data['tracking']['classical']['rmse']} m, L1 {data['tracking']['l1']['rmse']} m")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")
