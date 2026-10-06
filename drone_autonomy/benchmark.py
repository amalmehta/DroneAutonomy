"""Benchmark: adaptation curves on fixed held-out (test) and out-of-distribution
(ood) task sets, for every method and seed. Results go to results/<problem>/.

Tracking problems: stage s = after s adaptation updates of E=10 episodes each
(PEARL: s episodes of context; RL^2: episode s+1 of a trial).

Navigation is scored twice:
  'oracle'     adaptation curves with the privileged planner (fast)
  'fullstack'  the complete depth -> map -> A* stack in unseen test rooms,
               before and after one adaptation stage (exploration flights use
               the privileged planner, like a calibration flight in a known room)
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch

from .methods import DERIVED, TRAINED, UNTRAINED, build
from .tasks import fixed_eval_tasks
from .train import run_dir

RESULTS = Path("results")
N_TASKS = {"tracking_residual": 32, "tracking_gains": 32, "navigation": 24}
FULLSTACK_TASKS = 12


def methods_for(problem):
    derived = [d for d, src in DERIVED.items() if src in TRAINED[problem]]
    return UNTRAINED[problem] + TRAINED[problem] + derived


def _summ(stats):
    """Per-task means (so CIs are over tasks) of every metric."""
    out = {}
    for k, v in stats.items():
        if k == "episodes_used":
            out[k] = int(v)
            continue
        a = np.asarray(v, dtype=float)
        out[k] = np.nanmean(a, axis=1).tolist() if a.ndim == 2 else a.tolist()
    return out


def _load(problem, method, seed):
    """Build a method for evaluation (navigation: in the unseen test rooms) and load its checkpoint."""
    from .methods import problem_for
    P = problem_for(problem, method, split="test") if problem == "navigation" else problem_for(problem, method)
    m = build(problem, method, seed, problem=P, warm=False)
    if method in TRAINED[problem] or method in DERIVED:
        path = run_dir(problem, DERIVED.get(method, method), seed) / "checkpoint.pt"
        if not path.exists():
            return None
        m.load_state_dict(torch.load(path))
    return m


def bench_one(problem, method, seed, quick=False):
    torch.set_num_threads(1)
    out_path = RESULTS / problem / f"{method}_seed{seed}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 6 if quick else N_TASKS[problem]
    res = {"problem": problem, "method": method, "seed": seed}
    m = _load(problem, method, seed)
    if m is None:
        return None
    stages = 3 if getattr(m, "adapts", True) else 0
    for split in ("test", "ood"):
        tasks = fixed_eval_tasks(n, split)
        curve = m.adaptation_curve(tasks, stages, E=10, E_eval=2 if quick else 4, seed=1000 + seed)
        res[split] = [_summ(c) for c in curve]
    if problem == "navigation":
        res["fullstack"] = fullstack(method, seed, m, quick)
    out_path.write_text(json.dumps(res))
    return out_path


def fullstack(method, seed, m, quick=False):
    from .rl.nav_problem import Navigation
    n = 4 if quick else FULLSTACK_TASKS
    local = "classical" if method.startswith("classical") else "policy"
    planner = "none" if method.startswith("e2e") else "mapping"
    ev = Navigation(planner=planner, split="test", local=local, adaptive=(method == "classical_l1"))
    if method.startswith("classical"):
        from .rl.meta.gradient import Fixed
        m = Fixed(ev, name=method)
    out = {}
    for split in ("test", "ood"):
        tasks = fixed_eval_tasks(n, split)
        stages = 1 if getattr(m, "adapts", False) else 0
        curve = m.adaptation_curve(tasks, stages, E=10, E_eval=1, seed=2000 + seed, eval_problem=ev)
        out[split] = [_summ(c) for c in curve]
    return out


def bench_all(problems, seeds, workers=8, quick=False, methods=None):
    jobs = [(p, m, s) for p in problems for m in methods_for(p) if methods is None or m in methods
            for s in (seeds if m not in UNTRAINED[p] else seeds[:1])]

    def run(job):
        p, m, s = job
        r = subprocess.run([sys.executable, "-c",
                            f"from drone_autonomy.benchmark import bench_one; print(bench_one({p!r}, {m!r}, {s}, {quick}))"],
                           capture_output=True, text=True)
        tag = "ok  " if r.returncode == 0 and "None" not in r.stdout else ("skip" if r.returncode == 0 else "FAIL")
        print(f"{tag} {p}/{m}/seed{s}" + ("" if r.returncode == 0 else "\n" + r.stderr[-1500:]), flush=True)

    print(f"{len(jobs)} benchmark jobs on {workers} workers", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(run, jobs))
