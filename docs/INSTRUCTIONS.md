# Instructions

## Setup

Needs Python 3.10+ and [uv](https://docs.astral.sh/uv/) (or plain `pip`). Everything runs on a CPU; no GPU is used.

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -e ".[test]"
```

On an Intel Mac, PyTorch wheels stop at 2.2.2 and need `numpy<2`, which `pyproject.toml` already pins. Numba 0.60 is the last release with Intel-Mac wheels; if `uv` tries to build a newer `llvmlite` from source, install `numba==0.60.0` explicitly.

## Check it works

```bash
.venv/bin/python -m pytest -q tests
```

Ten tests cover hover and free fall, controller convergence, the task splits, depth ray-casting, collision checks, occupancy mapping, A* and a Meta-SGD second-order step. They take about a minute.

## Record the website demo

```bash
.venv/bin/drone-autonomy demo
```

This flies the full classical stack (depth camera → occupancy map → A* → local planner → controller) through four rooms and writes `website/data/demo.json`. To view the site locally:

```bash
python3 -m http.server 8765 --directory website
```

Then open http://localhost:8765.

## Train

One run:

```bash
.venv/bin/drone-autonomy train --problem tracking_residual --method maml --seed 0
```

- Problems: `tracking_residual` (combo 1: meta-learned residual on the classical controller), `tracking_gains` (combo 2: meta-learned controller gains), `navigation` (combo 3: meta-RL local planner).
- Methods: `maml`, `fomaml`, `anil`, `metasgd`, `reptile`, `pearl`, `rl2`, the domain-randomised baseline `dr`, and `e2e_dr` (end-to-end, navigation only). `drone_autonomy/methods.py` lists which methods apply to which problem and their iteration budgets.

Many runs in parallel (one single-threaded process per run):

```bash
.venv/bin/drone-autonomy sweep --problems tracking_residual tracking_gains --seeds 0 1 --workers 12
```

Checkpoints and JSON-lines logs go to `runs/<problem>/<method>/seed<k>/`. Add `--skip-done` to resume a sweep.

## Figures

```bash
.venv/bin/drone-autonomy figures
```

This regenerates `docs/images/` from the recorded data.

## Website

`.github/workflows/pages.yml` publishes `website/` to GitHub Pages on every push to `main` that touches it.
