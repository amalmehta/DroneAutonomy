"""I-02: navigation adaptation curves with the inner step scaled (one configuration per call)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_exp import save  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

from drone_autonomy.benchmark import _load  # noqa: E402
from drone_autonomy.tasks import fixed_eval_tasks  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"


def main(method, scale, E):
    t0 = time.time()
    m = _load("navigation", method, 0)
    with torch.no_grad():
        m.alpha = [a * scale for a in m.alpha] if method != "metasgd" else m.alpha
        if method == "metasgd":
            for a in m.alpha:
                a.mul_(scale)
    curve = m.adaptation_curve(fixed_eval_tasks(16, "test"), 3, E=E, E_eval=4, seed=1000)
    res = {"method": method, "scale": scale, "E": E, "wall_s": time.time() - t0,
           "success": [float(np.mean(s["success"])) for s in curve],
           "collision": [float(np.mean(s["collision"])) for s in curve],
           "episodes_used": [int(s["episodes_used"]) for s in curve]}
    save(OUT / f"{method}_scale{scale}_E{E}.json", res)
    print(res)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]))
