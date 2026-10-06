"""Fig. 2: performance against adaptation data on held-out tasks, for the three combinations."""
import numpy as np

import figure_style as fs
from common import LABEL, VENUE, VENUE_DIR, runs

P = fs.PALETTE
STYLE = {  # color, marker, linestyle
    "classical": ("#000000", None, ":"), "l1": ("#000000", None, "--"), "classical_l1": ("#000000", None, "--"),
    "dr": (P[0], None, "-."), "dr_finetune": (P[0], "s", "-"), "e2e_dr": (P[5], None, "-."),
    "e2e_dr_finetune": (P[5], "s", "-"),
    "maml": (P[1], "o", "-"), "fomaml": (P[1], "^", "--"), "anil": (P[4], "D", "-"), "metasgd": (P[3], "v", "-"),
    "reptile": (P[6], "P", "-"), "pearl": (P[2], "X", "-"), "rl2": (P[2], "*", "--"),
}
PANELS = [("tracking_residual", "rmse", 100, "(a) Residual on controller", "RMSE (cm)"),
          ("tracking_gains", "rmse", 100, "(b) Controller gains", "RMSE (cm)"),
          ("navigation", "success", 100, "(c) Local planner (privileged planner)", "success (%)")]


def curve(rs, key, scale):
    stages = min(len(r["test"]) for r in rs)
    xs, mu, half = [], [], []
    for s in range(stages):
        v = np.concatenate([np.asarray(r["test"][s][key], float) for r in rs])
        v = v[np.isfinite(v)] * scale
        xs.append(rs[0]["test"][s]["episodes_used"])
        mu.append(v.mean())
        half.append(1.96 * v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)
    return np.array(xs), np.array(mu), np.array(half)


def main():
    fig, axs = fs.figure(VENUE, width="text", aspect=0.36, ncols=3)
    handles = {}
    for ax, (problem, key, scale, title, ylabel) in zip(axs, PANELS):
        for m, rs in sorted(runs(problem).items(), key=lambda kv: list(STYLE).index(kv[0])):
            c, mk, ls = STYLE[m]
            x, mu, h = curve(rs, key, scale)
            if len(x) == 1:
                line = ax.axhline(mu[0], color=c, ls=ls, lw=1.0)
            else:
                line, = ax.plot(x, mu, color=c, marker=mk, ls=ls, lw=1.1, ms=3)
                ax.fill_between(x, mu - h, mu + h, color=c, alpha=0.10, lw=0)
            handles[m] = line
        ax.set_xscale("symlog", linthresh=1)
        ax.set_xlim(0, 32)
        ax.set_xticks([0, 1, 3, 10, 30])
        ax.set_xticklabels(["0", "1", "3", "10", "30"])
        ax.set_xlabel("adaptation episodes")
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left")
        ax.grid(alpha=0.25, lw=0.5)
    order = [m for m in STYLE if m in handles and m != "classical_l1"]
    fig.legend([handles[m] for m in order], [LABEL[m] for m in order], loc="outside lower center", ncol=7,
               handlelength=2.2, columnspacing=1.0)
    fs.save(fig, VENUE_DIR / "figures" / "adaptation_curves.pdf")


if __name__ == "__main__":
    main()
