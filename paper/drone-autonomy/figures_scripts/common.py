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
