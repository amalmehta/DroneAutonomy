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
