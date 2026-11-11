"""Shared paths and loaders for the figure, table and value scripts."""
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1].parent          # project root (…/drone_autonomy)
RESULTS = ROOT / "results"
VENUE_DIR = Path(os.environ.get("VENUE_DIR", HERE.parent / "ieee-conf"))
VENUE = os.environ.get("VENUE", "ieee")

ORDER = ["classical", "l1", "classical_l1", "dr", "dr_finetune", "e2e_dr", "e2e_dr_finetune",
         "maml", "fomaml", "anil", "metasgd", "reptile", "pearl", "rl2"]
LABEL = {"classical": "Classical (nominal gains)", "l1": "Classical + L1", "classical_l1": "Classical + L1",
         "dr": "DR (no adaptation)", "dr_finetune": "DR + fine-tune", "e2e_dr": "End-to-end DR",
         "e2e_dr_finetune": "End-to-end DR + fine-tune", "maml": "MAML", "fomaml": "FOMAML", "anil": "ANIL",
         "metasgd": "Meta-SGD", "reptile": "Reptile", "pearl": "PEARL", "rl2": "RL$^2$"}
GAINS_LABEL = dict(LABEL, dr="DR gains (no adaptation)", dr_finetune="DR gains + fine-tune")


# Training budget: environment steps per iteration = episodes per iteration x horizon.
# DR: 16 tasks x 10 episodes; MAML family: 2 x that (pre + post); Reptile: 3 x that;
# PEARL: 2 episodes x 8 tasks (+ one warm-up episode on 32 tasks); RL^2: 48 trials x 3 episodes.
HORIZON = {"tracking_residual": 200, "tracking_gains": 200, "navigation": 300}
EPISODES_PER_ITER = {"dr": 160, "e2e_dr": 160, "maml": 320, "fomaml": 320, "anil": 320, "metasgd": 320,
                     "reptile": 480, "pearl": 16, "rl2": 144}


def train_steps(problem, method, iters):
    return iters * EPISODES_PER_ITER[method] * HORIZON[problem] + (32 * HORIZON[problem] if method == "pearl" else 0)


def summary():
    return json.loads((RESULTS / "summary.json").read_text())


def rows(problem):
    rs = {r["method"]: r for r in summary()[problem]}
    return [rs[m] for m in ORDER if m in rs]


def runs(problem):
    out = {}
    for f in sorted((RESULTS / problem).glob("*_seed*.json")):
        r = json.loads(f.read_text())
        out.setdefault(r["method"], []).append(r)
    return out
