"""Procedural indoor worlds: a walled room with pillars (vertical cylinders)
and boxes (crates, shelves, tables), batched with one world per drone.

Primitives are padded arrays so numba kernels can loop over them:
  cyl  (n, Kc, 3)  [cx, cy, radius]     radius 0 = unused slot
  box  (n, Kb, 6)  [x0, y0, z0, x1, y1, z1]  x1 < x0 = unused slot
"""
from dataclasses import dataclass

import numba as nb
import numpy as np

ROOM = np.array([14.0, 8.0, 3.0])   # m, x/y/z extent of the cage-like room
DRONE_RADIUS = 0.35                 # m, X500 with props ~ 0.6 m span + margin
MAX_CYL, MAX_BOX = 14, 10


@dataclass
class Worlds:
    cyl: np.ndarray
    box: np.ndarray
    start: np.ndarray   # (n, 3)
    goal: np.ndarray    # (n, 3)

    def __len__(self):
        return len(self.start)


def generate(n, rng, density=1.0):
    """density scales the obstacle count (1.0 ~ 10 pillars + 6 boxes)."""
    cyl = np.zeros((n, MAX_CYL, 3))
    box = np.zeros((n, MAX_BOX, 6))
    box[:, :, 3] = -1.0  # mark unused
    start = np.zeros((n, 3))
    goal = np.zeros((n, 3))
    for i in range(n):
        side = rng.random() < 0.5
        s = np.array([1.0, rng.uniform(1.0, ROOM[1] - 1.0), rng.uniform(0.9, 1.4)])
        g = np.array([ROOM[0] - 1.0, rng.uniform(1.0, ROOM[1] - 1.0), rng.uniform(0.9, 1.4)])
        if side:
            s[0], g[0] = g[0], s[0]
        start[i], goal[i] = s, g
        kc = min(MAX_CYL, rng.poisson(10 * density))
        kb = min(MAX_BOX, rng.poisson(6 * density))
        j = 0
        tries = 0
        while j < kc and tries < 200:
            tries += 1
            c = np.array([rng.uniform(2.2, ROOM[0] - 2.2), rng.uniform(0.3, ROOM[1] - 0.3), rng.uniform(0.12, 0.45)])
            if _clear_of_endpoints(c[:2], c[2], s, g):
                cyl[i, j] = c
                j += 1
        j = 0
        tries = 0
        while j < kb and tries < 200:
            tries += 1
            size = rng.uniform([0.4, 0.4, 0.5], [1.6, 1.6, 3.0])
            lo = np.array([rng.uniform(2.0, ROOM[0] - 2.0 - size[0]), rng.uniform(0.0, ROOM[1] - size[1]), 0.0])
            if rng.random() < 0.25:  # hanging obstacle (duct, light rig): forces 3D avoidance
                lo[2] = rng.uniform(1.9, 2.3)
                size[2] = ROOM[2] - lo[2]
            hi = lo + size
            centre = (lo[:2] + hi[:2]) / 2
            if _clear_of_endpoints(centre, np.linalg.norm(size[:2]) / 2, s, g):
                box[i, j, :3], box[i, j, 3:] = lo, np.minimum(hi, ROOM)
                j += 1
    return Worlds(cyl, box, start, goal)


def _clear_of_endpoints(xy, r, s, g, margin=1.2):
    return (np.linalg.norm(xy - s[:2]) > r + margin) and (np.linalg.norm(xy - g[:2]) > r + margin)


@nb.njit(cache=True)
def collision_kernel(p, cyl, box, room, radius, out):
    """out[i] = True if a drone sphere at p[i] intersects anything."""
    for i in range(p.shape[0]):
        x, y, z = p[i, 0], p[i, 1], p[i, 2]
        hit = (x < radius or y < radius or z < 0.1 or x > room[0] - radius
               or y > room[1] - radius or z > room[2] - radius)
        if not hit:
            for j in range(cyl.shape[1]):
                r = cyl[i, j, 2]
                if r > 0 and (x - cyl[i, j, 0]) ** 2 + (y - cyl[i, j, 1]) ** 2 < (r + radius) ** 2:
                    hit = True
                    break
        if not hit:
            for j in range(box.shape[1]):
                if box[i, j, 3] < box[i, j, 0]:
                    continue
                dx = max(box[i, j, 0] - x, 0.0, x - box[i, j, 3])
                dy = max(box[i, j, 1] - y, 0.0, y - box[i, j, 4])
                dz = max(box[i, j, 2] - z, 0.0, z - box[i, j, 5])
                if dx * dx + dy * dy + dz * dz < radius * radius:
                    hit = True
                    break
        out[i] = hit


def collides(p, worlds: Worlds, radius=DRONE_RADIUS):
    out = np.zeros(len(p), dtype=np.bool_)
    collision_kernel(np.ascontiguousarray(p), worlds.cyl, worlds.box, ROOM, radius, out)
    return out


@nb.njit(cache=True)
def occupancy_kernel(cyl, box, room, res, inflate, grid):
    """Rasterise one world (index 0 of cyl/box) into a voxel grid of size res."""
    nx, ny, nz = grid.shape
    for a in range(nx):
        x = (a + 0.5) * res
        for b in range(ny):
            y = (b + 0.5) * res
            for c in range(nz):
                z = (c + 0.5) * res
                occ = (x < inflate or y < inflate or z < inflate or x > room[0] - inflate
                       or y > room[1] - inflate or z > room[2] - inflate)
                if not occ:
                    for j in range(cyl.shape[0]):
                        r = cyl[j, 2]
                        if r > 0 and (x - cyl[j, 0]) ** 2 + (y - cyl[j, 1]) ** 2 < (r + inflate) ** 2:
                            occ = True
                            break
                if not occ:
                    for j in range(box.shape[0]):
                        if box[j, 3] < box[j, 0]:
                            continue
                        dx = max(box[j, 0] - x, 0.0, x - box[j, 3])
                        dy = max(box[j, 1] - y, 0.0, y - box[j, 4])
                        dz = max(box[j, 2] - z, 0.0, z - box[j, 5])
                        if dx * dx + dy * dy + dz * dz < inflate * inflate:
                            occ = True
                            break
                grid[a, b, c] = occ


def true_occupancy(worlds: Worlds, i, res, inflate):
    shape = tuple(np.ceil(ROOM / res).astype(int))
    grid = np.zeros(shape, dtype=np.bool_)
    occupancy_kernel(worlds.cyl[i], worlds.box[i], ROOM, res, inflate, grid)
    return grid
