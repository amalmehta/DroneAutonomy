"""Simulated depth camera modelled on the Intel RealSense D435i.

Rays are cast analytically against each drone's world (pillars, boxes, room
walls, floor, ceiling) in a numba kernel. Noise follows active-stereo
behaviour: Gaussian with std growing quadratically in range, plus random
dropouts that read as max range.
"""
from dataclasses import dataclass

import numba as nb
import numpy as np

from .world import ROOM, Worlds


@dataclass(frozen=True)
class DepthCamera:
    cols: int = 16
    rows: int = 8
    hfov_deg: float = 87.0
    vfov_deg: float = 58.0
    max_range: float = 5.0
    min_range: float = 0.2
    noise_quad: float = 0.008   # std = noise_quad * d^2  (m)
    dropout: float = 0.02

    def body_rays(self):
        """Unit ray directions in the body frame (x forward, y left, z up)."""
        az = np.radians(np.linspace(self.hfov_deg / 2, -self.hfov_deg / 2, self.cols))
        el = np.radians(np.linspace(self.vfov_deg / 2, -self.vfov_deg / 2, self.rows))
        A, E = np.meshgrid(az, el)
        d = np.stack([np.ones_like(A), np.tan(A), np.tan(E)], -1).reshape(-1, 3)
        return d / np.linalg.norm(d, axis=1, keepdims=True)


@nb.njit(cache=True, fastmath=True)
def raycast_kernel(origin, dirs, cyl, box, room, max_range, out):
    """origin (n,3); dirs (n, m, 3) world-frame unit rays; out (n, m) ranges."""
    n, m = dirs.shape[0], dirs.shape[1]
    for i in range(n):
        ox, oy, oz = origin[i, 0], origin[i, 1], origin[i, 2]
        for k in range(m):
            dx, dy, dz = dirs[i, k, 0], dirs[i, k, 1], dirs[i, k, 2]
            t = max_range
            # room interior: exit through walls / floor / ceiling
            if dx > 1e-9:
                t = min(t, (room[0] - ox) / dx)
            elif dx < -1e-9:
                t = min(t, -ox / dx)
            if dy > 1e-9:
                t = min(t, (room[1] - oy) / dy)
            elif dy < -1e-9:
                t = min(t, -oy / dy)
            if dz > 1e-9:
                t = min(t, (room[2] - oz) / dz)
            elif dz < -1e-9:
                t = min(t, -oz / dz)
            # vertical cylinders (2D circle test, full height)
            a = dx * dx + dy * dy
            if a > 1e-12:
                for j in range(cyl.shape[1]):
                    r = cyl[i, j, 2]
                    if r <= 0:
                        continue
                    fx, fy = ox - cyl[i, j, 0], oy - cyl[i, j, 1]
                    b = fx * dx + fy * dy
                    c = fx * fx + fy * fy - r * r
                    disc = b * b - a * c
                    if disc >= 0:
                        th = (-b - np.sqrt(disc)) / a
                        if 0 < th < t:
                            t = th
            # axis-aligned boxes (slab method)
            for j in range(box.shape[1]):
                if box[i, j, 3] < box[i, j, 0]:
                    continue
                tmin, tmax = -1e9, 1e9
                ok = True
                for ax in range(3):
                    o = origin[i, ax]
                    d = dirs[i, k, ax]
                    lo, hi = box[i, j, ax], box[i, j, 3 + ax]
                    if abs(d) < 1e-12:
                        if o < lo or o > hi:
                            ok = False
                            break
                    else:
                        t1, t2 = (lo - o) / d, (hi - o) / d
                        if t1 > t2:
                            t1, t2 = t2, t1
                        tmin = max(tmin, t1)
                        tmax = min(tmax, t2)
                if ok and tmax >= max(tmin, 0.0) and 0 < tmin < t:
                    t = tmin
            out[i, k] = t


def render_depth(cam: DepthCamera, p, R, worlds: Worlds, rng=None, rays=None, invalid=None):
    """Depth image (n, rows*cols) in metres for drones at p with attitude R.

    Dropped-out pixels read `invalid` (default: max range, which is what the
    policy sees; the mapper passes NaN so dropouts never carve free space)."""
    rays = cam.body_rays() if rays is None else rays
    dirs = np.einsum("nij,mj->nmi", R, rays)
    out = np.empty(dirs.shape[:2])
    raycast_kernel(np.ascontiguousarray(p), np.ascontiguousarray(dirs), worlds.cyl, worlds.box,
                   ROOM, cam.max_range, out)
    if rng is not None:
        no_return = out >= cam.max_range  # nothing within range: stays 'far', no noise
        out = np.where(no_return, out, out + cam.noise_quad * out ** 2 * rng.standard_normal(out.shape))
        out = np.where(no_return, out, np.minimum(out, cam.max_range - 0.01))
        drop = rng.random(out.shape) < cam.dropout
    else:
        drop = np.zeros(out.shape, bool)
    out = np.clip(out, cam.min_range, cam.max_range)
    out[drop] = cam.max_range if invalid is None else invalid
    return out
