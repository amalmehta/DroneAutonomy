"""3D occupancy mapping from depth images (log-odds voxel grid).

Each depth ray marks the voxels it passes through as more likely free and
its endpoint (if it hit something before max range) as more likely occupied.
Free-space carving stops one voxel short of a hit and skips dropped-out
pixels, so grazing rays and stereo dropouts don't erase thin obstacles.
Unknown space stays at log-odds 0; the planner treats it optimistically.
"""
import numba as nb
import numpy as np

from .world import ROOM

L_FREE, L_OCC, L_MIN, L_MAX = -0.4, 0.85, -2.0, 3.5


@nb.njit(cache=True)
def integrate_kernel(grid, res, origin, dirs, ranges, max_range):
    nx, ny, nz = grid.shape
    step = res * 0.5
    for k in range(dirs.shape[0]):
        r = ranges[k]
        if not np.isfinite(r):
            continue  # dropout: no information
        hit = r < max_range - 1e-3
        # carve free space only up to one voxel short of a hit, so rays grazing
        # a surface don't erase it
        n_steps = int(max(r - res, 0.0) / step) if hit else int(r / step)
        last = (-1, -1, -1)
        for s in range(n_steps):
            t = s * step
            a = int((origin[0] + dirs[k, 0] * t) / res)
            b = int((origin[1] + dirs[k, 1] * t) / res)
            c = int((origin[2] + dirs[k, 2] * t) / res)
            if a < 0 or b < 0 or c < 0 or a >= nx or b >= ny or c >= nz:
                break
            if (a, b, c) != last:
                grid[a, b, c] = max(L_MIN, grid[a, b, c] + L_FREE)
                last = (a, b, c)
        if hit:
            a = int((origin[0] + dirs[k, 0] * r) / res)
            b = int((origin[1] + dirs[k, 1] * r) / res)
            c = int((origin[2] + dirs[k, 2] * r) / res)
            if 0 <= a < nx and 0 <= b < ny and 0 <= c < nz:
                grid[a, b, c] = min(L_MAX, grid[a, b, c] + L_OCC)


class OccupancyMap:
    def __init__(self, res=0.2):
        self.res = res
        self.shape = tuple(np.ceil(ROOM / res).astype(int))
        self.logodds = np.zeros(self.shape, dtype=np.float32)

    def integrate(self, origin, dirs, ranges, max_range):
        integrate_kernel(self.logodds, self.res, np.asarray(origin, float),
                         np.ascontiguousarray(dirs), np.asarray(ranges, float), max_range)

    def occupied(self, threshold=0.5):
        return self.logodds > threshold

    def known_fraction(self):
        return float((self.logodds != 0).mean())
