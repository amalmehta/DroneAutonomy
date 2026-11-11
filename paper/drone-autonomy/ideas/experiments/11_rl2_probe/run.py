"""I-11: linear probes from RL^2's GRU state to the task parameters, per episode of a trial."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common_exp import save  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402

from drone_autonomy.benchmark import _load  # noqa: E402
from drone_autonomy.tasks import sample_tasks  # noqa: E402

OUT = Path(__file__).resolve().parent / "results"
PARAMS = ["mass_scale", "weakest_motor", "wind_speed", "latency"]


def cv_r2(X, y, folds=5, lam=1.0, seed=0):
    idx = np.random.default_rng(seed).permutation(len(y))
    pred = np.zeros_like(y)
    for f in range(folds):
        te = idx[f::folds]
        tr = np.setdiff1d(idx, te)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        A = (X[tr] - mu) / sd
        w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (y[tr] - y[tr].mean()))
        pred[te] = ((X[te] - mu) / sd) @ w + y[tr].mean()
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


@torch.no_grad()
def main():
    t0 = time.time()
    m = _load("navigation", "rl2", 0)
    tasks = sample_tasks(64, np.random.default_rng(40004), "train")  # held-out draw from the training ranges
    env = m.problem.env(len(tasks))
    n = env.n
    h, states, early = None, [], None
    prev_a = np.zeros((n, m.ad), np.float32)
    prev_r = np.zeros(n, np.float32)
    success = []
    for k in range(3):
        obs = env.reset(tasks, seed=500 + k)
        first = np.ones(n, np.float32)
        for t in range(env.horizon):
            x = np.concatenate([obs, prev_a, prev_r[:, None], first[:, None]], 1).astype(np.float32)
            mu, _, h = m.net(torch.as_tensor(x)[None], h)
            a = mu[0].numpy()
            obs, r, _, info = env.step(a)
            prev_a, prev_r, first = np.clip(a, -1, 1).astype(np.float32), r.astype(np.float32), np.zeros(n, np.float32)
            if k == 0 and t == 9:
                early = h[0].numpy().copy()
        states.append(h[0].numpy().copy())
        success.append(float(env.metrics()["success"].mean()))
    f = tasks.features()
    y = {"mass_scale": f[:, 0], "weakest_motor": f[:, 1], "wind_speed": f[:, 3], "latency": f[:, 5]}
    res = {"wall_s": None, "success_per_episode": success,
           "r2_after_10_steps": {p: cv_r2(early, y[p]) for p in PARAMS},
           "r2_end_of_episode": [{p: cv_r2(s, y[p]) for p in PARAMS} for s in states]}
    res["wall_s"] = time.time() - t0
    save(OUT / "rl2_probe.json", res)
    print(res)


if __name__ == "__main__":
    main()
