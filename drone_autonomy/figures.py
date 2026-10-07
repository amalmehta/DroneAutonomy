"""Figures for the README, paper and website, drawn from recorded data only."""
import base64
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DEMO = Path("website/data/demo.json")
IMAGES = Path("docs/images")
INK, ACCENT, TRACK, MAP, TRUTH = "#16212b", "#d9530f", "#0f7c86", "#26323c", "#9fb0b5"


def _occ(snap, nx, ny):
    bits = np.unpackbits(np.frombuffer(base64.b64decode(snap["occ"]), np.uint8))[: nx * ny]
    return bits.reshape(nx, ny).astype(bool)


def flight_figure(data, out, flights=(0, 3)):
    nx, ny = data["meta"]["grid"]
    res = data["meta"]["res"]
    fig, axs = plt.subplots(1, len(flights), figsize=(6.2 * len(flights), 3.9))
    for ax, i in zip(np.atleast_1d(axs), flights):
        f = data["flights"][i]
        for b in f["boxes"]:
            ax.add_patch(plt.Rectangle(b[:2], b[3] - b[0], b[4] - b[1], color=TRUTH, alpha=0.25 if b[2] > 0.1 else 0.45, lw=0))
        for c in f["pillars"]:
            ax.add_patch(plt.Circle(c[:2], c[2], color=TRUTH, alpha=0.45, lw=0))
        occ = _occ(f["snaps"][-1], nx, ny)
        xs, ys = np.nonzero(occ)
        ax.scatter((xs + 0.5) * res, (ys + 0.5) * res, s=7, marker="s", color=MAP, lw=0, label="mapped from depth")
        path = f["snaps"][-1]["path"]
        if path:
            p = np.array(path)
            ax.plot(p[:, 0], p[:, 1], "--", color=ACCENT, lw=1.6, label="final A* plan")
        tr = np.array([fr["p"] for fr in f["frames"]])
        ax.plot(tr[:, 0], tr[:, 1], color=TRACK, lw=2.2, label="flown track")
        ax.plot(*f["start"][:2], "o", mfc="none", mec=INK, ms=9)
        ax.plot(*f["goal"][:2], "*", color=INK, ms=11)
        t = f["task"]
        cond = "nominal drone" if t["mass_scale"] == 1 and t["wind"] == 0 else \
            f"payload ×{t['mass_scale']}, wind {t['wind']} m/s, motor {int(t['weakest_motor'] * 100)}%"
        ax.set_title(f"Room {i + 1}: {f['outcome']}" + (f" in {f['time_s']} s" if f["time_s"] else "") + f"\n{cond}",
                     fontsize=10, color=INK)
        ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.set_aspect("equal")
        ax.set_xticks(range(0, 15, 2)); ax.set_yticks(range(0, 9, 2))
        ax.tick_params(labelsize=8, colors="#5b6871")
        for s in ax.spines.values():
            s.set_color("#d3dad8")
    np.atleast_1d(axs)[0].legend(loc="lower left", fontsize=7.5, frameon=False, ncol=3, bbox_to_anchor=(0, -0.3))
    fig.text(0.99, 0.01, "grey: true obstacles (palest boxes hang above 1.9 m) · ○ start · ★ goal",
             ha="right", fontsize=7.5, color="#5b6871")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def tracking_figure(data, out):
    T = data["tracking"]
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    ref = np.array(T["ref"])
    ax.plot(ref[:, 0], ref[:, 1], "--", color=INK, lw=1.4, label="reference")
    for key, color, name in (("classical", ACCENT, "classical, fixed gains"), ("l1", TRACK, "classical + L1 adaptive")):
        p = np.array(T[key]["p"])
        ax.plot(p[:, 0], p[:, 1], color=color, lw=2, label=f"{name}: {T[key]['rmse'] * 100:.1f} cm RMS")
    t = T["task"]
    ax.set_title(f"Figure-eight with payload ×{t['mass_scale']}, one motor at {int(t['weakest_motor'] * 100)}%, "
                 f"{t['wind']} m/s wind", fontsize=9, color=INK)
    ax.set_xlabel("x (m)", fontsize=8); ax.set_ylabel("y (m)", fontsize=8)
    ax.set_aspect("equal"); ax.tick_params(labelsize=8)
    ax.legend(fontsize=7.5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def make_all():
    IMAGES.mkdir(parents=True, exist_ok=True)
    data = json.loads(DEMO.read_text())
    flight_figure(data, IMAGES / "flights.png")
    tracking_figure(data, IMAGES / "tracking.png")
    print(f"wrote {IMAGES}/flights.png, {IMAGES}/tracking.png")
    if RESULTS.exists():
        make_results()


# ----------------------------------------------------------------- results
RESULTS = Path("results")
PAPER_FIGS = Path("paper/figures")
PALETTE = {  # one hue per family: classical greys, baselines blue, MAML family warm, context methods green/purple
    "classical": "#7d8a90", "l1": "#3d4a52", "classical_l1": "#3d4a52",
    "dr": "#2c6fbb", "dr_finetune": "#6aa3e0", "e2e_dr": "#1b3f73", "e2e_dr_finetune": "#5a7fb5",
    "maml": "#d9530f", "fomaml": "#f08c4a", "anil": "#b8860b", "metasgd": "#c2185b", "reptile": "#8d6e63",
    "pearl": "#2f7d32", "rl2": "#6a3fa0",
}
METRIC = {"tracking_residual": ("rmse", "tracking RMSE (m)", 1.0), "tracking_gains": ("rmse", "tracking RMSE (m)", 1.0),
          "navigation": ("success", "success rate", 1.0)}


def load_results(problem):
    out = {}
    for f in sorted((RESULTS / problem).glob("*_seed*.json")):
        r = json.loads(f.read_text())
        out.setdefault(r["method"], []).append(r)
    return out


def curve(runs, split, key):
    """Mean and 95% CI (over tasks x seeds) per stage; x = episodes of adaptation data."""
    stages = min(len(r[split]) for r in runs)
    xs, mu, lo, hi = [], [], [], []
    for s in range(stages):
        vals = np.concatenate([np.asarray(r[split][s][key], float) for r in runs])
        vals = vals[np.isfinite(vals)]
        m = vals.mean()
        se = vals.std(ddof=1) / np.sqrt(len(vals)) if len(vals) > 1 else 0.0
        xs.append(runs[0][split][s]["episodes_used"]); mu.append(m); lo.append(m - 1.96 * se); hi.append(m + 1.96 * se)
    return np.array(xs), np.array(mu), np.array(lo), np.array(hi)


def adaptation_figure(problem, out):
    from .methods import LABELS
    res = load_results(problem)
    if not res:
        return None
    key, ylabel, _ = METRIC[problem]
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
    for ax, split, title in zip(axs, ("test", "ood"), ("held-out tasks", "out-of-distribution tasks")):
        for meth, runs in res.items():
            x, mu, lo, hi = curve(runs, split, key)
            c = PALETTE.get(meth, "#444")
            xp = np.maximum(x, 0) + 1
            if len(x) == 1:
                ax.axhline(mu[0], color=c, lw=1.4, ls=":" if meth.startswith("classical") or meth == "l1" else "--",
                           label=LABELS.get(meth, meth))
            else:
                ax.plot(xp, mu, "-o", color=c, ms=3.5, lw=1.8, label=LABELS.get(meth, meth))
                ax.fill_between(xp, lo, hi, color=c, alpha=0.12, lw=0)
        ax.set_xscale("log")
        ax.set_xlabel("adaptation episodes + 1 (log)", fontsize=8)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(title, fontsize=9, color=INK)
        ax.tick_params(labelsize=7.5)
        ax.grid(alpha=0.25, lw=0.6)
    axs[1].legend(fontsize=7, frameon=False, loc="center left", bbox_to_anchor=(1.02, 0.5))
    fig.tight_layout()
    fig.savefig(out, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return out


def summary(problem):
    """Final numbers per method: pre-adaptation and best-budget post-adaptation, test and OOD."""
    from .methods import LABELS
    res = load_results(problem)
    key = METRIC[problem][0]
    rows = []
    for meth, runs in res.items():
        row = {"method": meth, "label": LABELS.get(meth, meth), "seeds": len(runs)}
        for split in ("test", "ood"):
            x, mu, lo, hi = curve(runs, split, key)
            row[f"{split}_pre"], row[f"{split}_post"] = float(mu[0]), float(mu[-1])
            row[f"{split}_post_ci"] = float(hi[-1] - mu[-1])
            row[f"{split}_episodes"] = int(x[-1])
            row[f"{split}_curve"] = [float(v) for v in mu]
            if "crashed" in runs[0][split][-1]:
                row[f"{split}_crash"] = float(np.mean([np.mean(r[split][-1]["crashed"]) for r in runs]))
            if "collision" in runs[0][split][-1]:
                row[f"{split}_collision"] = float(np.mean([np.mean(r[split][-1]["collision"]) for r in runs]))
        if "fullstack" in runs[0]:
            for split in ("test", "ood"):
                fs = [r["fullstack"][split] for r in runs]
                row[f"full_{split}_success_pre"] = float(np.mean([np.mean(f[0]["success"]) for f in fs]))
                row[f"full_{split}_success_post"] = float(np.mean([np.mean(f[-1]["success"]) for f in fs]))
                row[f"full_{split}_collision_post"] = float(np.mean([np.mean(f[-1]["collision"]) for f in fs]))
        rows.append(row)
    return rows


def make_results():
    PAPER_FIGS.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = {}
    for problem in ("tracking_residual", "tracking_gains", "navigation"):
        f = adaptation_figure(problem, PAPER_FIGS / f"adaptation_{problem}.pdf")
        if f:
            adaptation_figure(problem, IMAGES / f"adaptation_{problem}.png")
            out[problem] = summary(problem)
    (RESULTS / "summary.json").write_text(json.dumps(out, indent=1))
    Path("website/data").mkdir(parents=True, exist_ok=True)
    Path("website/data/results.json").write_text(json.dumps(out))
    print("results figures:", ", ".join(out) or "none yet")
