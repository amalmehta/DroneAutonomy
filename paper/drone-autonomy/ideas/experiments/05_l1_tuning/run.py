"""I-05: grid-search the L1 augmentation's predictor pole and filter bandwidth on training tasks."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_exp import save  # noqa: E402

import numpy as np  # noqa: E402

import drone_autonomy.control as C  # noqa: E402
from drone_autonomy.envs.tracking import TrackingEnv  # noqa: E402
from drone_autonomy.tasks import fixed_eval_tasks, sample_tasks  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"


def score(tasks, a_s, cutoff, seed=0):
    C.L1_AS, C.L1_CUTOFF = a_s, cutoff  # module-level settings read by the controller at call time
    n = len(tasks) * 4
    env = TrackingEnv(n, mode="none", adaptive=True)
    env.reset(tasks.repeat(4), seed=seed)
    for _ in range(env.horizon):
        env.step(None)
    m = env.metrics()
    return float(m["rmse"].mean()), float(m["crashed"].mean())


def main():
    t0 = time.time()
    train = sample_tasks(32, np.random.default_rng(0), "train")
    grid = []
    for a_s in (5.0, 10.0, 20.0, 40.0):
        for cutoff in (2.0, 5.0, 10.0, 20.0, 40.0):
            rmse, crash = score(train, a_s, cutoff)
            grid.append({"a_s": a_s, "cutoff": cutoff, "train_rmse": rmse, "train_crash": crash})
            print(grid[-1], flush=True)
    best = min(grid, key=lambda g: g["train_rmse"])
    out = {"grid": grid, "best": best, "wall_s": None}
    for name, (a_s, cutoff) in (("default", (10.0, 5.0)), ("tuned", (best["a_s"], best["cutoff"]))):
        for split in ("test", "ood"):
            rmse, crash = score(fixed_eval_tasks(32, split), a_s, cutoff, seed=1000)
            out[f"{name}_{split}_rmse"], out[f"{name}_{split}_crash"] = rmse, crash
    out["wall_s"] = time.time() - t0
    save(OUT / "l1_tuning.json", out)
    print({k: v for k, v in out.items() if k != "grid"})


if __name__ == "__main__":
    main()
