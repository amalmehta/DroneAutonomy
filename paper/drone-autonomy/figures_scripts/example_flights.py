"""Fig. 3: one recorded full-stack flight: true room, map built from depth, final A* plan, flown track."""
import base64
import json

import numpy as np

import figure_style as fs
from common import ROOT, VENUE, VENUE_DIR

FLIGHT = 0  # Room 1 of website/data/demo.json: nominal drone, reached goal


def main():
    d = json.loads((ROOT / "website" / "data" / "demo.json").read_text())
    f = d["flights"][FLIGHT]
    nx, ny = d["meta"]["grid"]
    res = d["meta"]["res"]
    fig, ax = fs.figure(VENUE, width="column", aspect=0.66)
    import matplotlib.pyplot as plt
    for b in f["boxes"]:
        hanging = b[2] > 0.1
        ax.add_patch(plt.Rectangle(b[:2], b[3] - b[0], b[4] - b[1], fc="#bbbbbb", ec="none", alpha=0.35 if hanging else 0.7))
    for c in f["pillars"]:
        ax.add_patch(plt.Circle(c[:2], c[2], fc="#bbbbbb", ec="none", alpha=0.7))
    snap = f["snaps"][-1]
    bits = np.unpackbits(np.frombuffer(base64.b64decode(snap["occ"]), np.uint8))[: nx * ny].reshape(nx, ny)
    xs, ys = np.nonzero(bits)
    ax.scatter((xs + 0.5) * res, (ys + 0.5) * res, s=2.2, marker="s", color="#000000", lw=0, label="mapped (depth)")
    if snap["path"]:
        p = np.array(snap["path"])
        ax.plot(p[:, 0], p[:, 1], ls="--", color=fs.PALETTE[1], lw=1.0, label="final A* plan")
    tr = np.array([fr["p"] for fr in f["frames"]])
    ax.plot(tr[:, 0], tr[:, 1], color=fs.PALETTE[0], lw=1.4, label="flown track")
    ax.plot(*f["start"][:2], "o", mfc="none", mec="k", ms=4)
    ax.plot(*f["goal"][:2], "*", color="k", ms=6)
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.set_aspect("equal")
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    fig.legend(loc="outside lower center", ncol=3, handlelength=1.6)
    fs.save(fig, VENUE_DIR / "figures" / "example_flights.pdf")


if __name__ == "__main__":
    main()
