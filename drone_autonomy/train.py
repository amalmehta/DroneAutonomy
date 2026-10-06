"""Train one (problem, method, seed) and save a checkpoint + JSON-lines log."""
import json
import os
import time
from pathlib import Path

import torch

from .methods import ITERS, build

RUNS = Path(os.environ.get("DRONE_AUTONOMY_RUNS", "runs"))


def run_dir(problem, method, seed):
    return RUNS / problem / method / f"seed{seed}"


def train(problem, method, seed=0, iters=None, log_every=1, quiet=False):
    torch.set_num_threads(1)
    out = run_dir(problem, method, seed)
    out.mkdir(parents=True, exist_ok=True)
    m = build(problem, method, seed)
    iters = iters or ITERS[problem][method]
    log = open(out / "log.jsonl", "w")
    t0 = time.time()
    for it in range(iters):
        stats = m.train_step()
        stats.update(iteration=it, wall=time.time() - t0)
        log.write(json.dumps(stats) + "\n")
        log.flush()
        if not quiet and it % log_every == 0:
            short = {k: round(v, 3) for k, v in stats.items() if isinstance(v, float)}
            print(f"[{problem}/{method}/s{seed}] {it}/{iters} {short}", flush=True)
        if (it + 1) % 25 == 0 or it == iters - 1:
            torch.save(m.state_dict(), out / "checkpoint.pt")
    log.close()
    return out


def load(problem, method, seed=0):
    from .methods import DERIVED
    m = build(problem, method, seed)
    src = DERIVED.get(method, method)
    path = run_dir(problem, src, seed) / "checkpoint.pt"
    if path.exists():
        m.load_state_dict(torch.load(path))
    return m
