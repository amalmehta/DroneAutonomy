"""I-06: score every tracking method on a mild out-of-distribution split (one problem/method/seed per call)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_exp import save  # noqa: E402

import numpy as np  # noqa: E402

from drone_autonomy.benchmark import _load  # noqa: E402
from drone_autonomy.tasks import TaskBatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"
MILD = {"mass_scale": (1.30, 1.35), "motor_eff_min": (0.70, 0.75), "drag_scale": (2.0, 2.3),
        "wind_speed": (2.5, 3.0), "gust_std": (0.8, 0.95), "latency_steps": (3, 4)}


def mild_tasks(n=32, seed=30003):
    rng = np.random.default_rng(seed)
    u = lambda k: rng.uniform(*MILD[k], n)
    eff = rng.uniform(0.95, 1.0, (n, 4))
    eff[np.arange(n), rng.integers(0, 4, n)] = u("motor_eff_min")
    heading, speed = rng.uniform(0, 2 * np.pi, n), u("wind_speed")
    wind = np.column_stack([speed * np.cos(heading), speed * np.sin(heading), np.zeros(n)])
    return TaskBatch(mass_scale=u("mass_scale"), motor_eff=eff, drag_scale=u("drag_scale"), wind=wind,
                     gust_std=u("gust_std"), latency_steps=rng.integers(3, 5, n))


def main(problem, method, seed):
    t0 = time.time()
    m = _load(problem, method, seed)
    if m is None:
        return
    stages = 3 if getattr(m, "adapts", True) else 0
    curve = m.adaptation_curve(mild_tasks(), stages, E=10, E_eval=4, seed=1000 + seed)
    res = {"problem": problem, "method": method, "seed": seed, "wall_s": time.time() - t0,
           "rmse": [float(np.mean(s["rmse"])) for s in curve], "crashed": [float(np.mean(s["crashed"])) for s in curve],
           "rmse_per_task": [np.mean(np.asarray(s["rmse"]), axis=1).tolist() for s in curve],
           "episodes_used": [int(s["episodes_used"]) for s in curve]}
    save(OUT / f"{problem}_{method}_seed{seed}.json", res)
    print(problem, method, seed, res["rmse"], res["crashed"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
