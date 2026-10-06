"""Run many training jobs as parallel single-threaded processes."""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .methods import ITERS, TRAINED
from .train import run_dir


def _done(problem, method, seed):
    log = run_dir(problem, method, seed) / "log.jsonl"
    return log.exists() and sum(1 for _ in open(log)) >= ITERS[problem][method]


def sweep(problems, methods, seeds, workers=8, skip_done=False):
    jobs = [(p, m, s) for p in problems for m in (methods or TRAINED[p]) if m in TRAINED[p] for s in seeds]
    if skip_done:
        jobs = [j for j in jobs if not _done(*j)]
    Path("runs").mkdir(exist_ok=True)

    def run(job):
        p, m, s = job
        out = run_dir(p, m, s)
        out.mkdir(parents=True, exist_ok=True)
        with open(out / "stdout.txt", "w") as f:
            r = subprocess.run([sys.executable, "-m", "drone_autonomy.cli", "train", "--problem", p,
                                "--method", m, "--seed", str(s)], stdout=f, stderr=subprocess.STDOUT,
                               env={**__import__("os").environ, "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        print(f"{'ok ' if r.returncode == 0 else 'FAIL'} {p}/{m}/seed{s}", flush=True)
        return r.returncode

    print(f"{len(jobs)} jobs on {workers} workers", flush=True)
    with ThreadPoolExecutor(workers) as ex:
        codes = list(ex.map(run, jobs))
    print(f"finished: {codes.count(0)} ok, {len(codes) - codes.count(0)} failed", flush=True)
