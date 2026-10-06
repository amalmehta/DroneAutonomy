"""Global planning on voxel grids: inflation, A*, path shortcutting, carrots,
plus a Dijkstra distance-to-goal field used as the privileged training-time
planner (equivalent to A* on the true map, but answers every start at once).
"""
import numba as nb
import numpy as np

NEIGH = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)
                  if (a, b, c) != (0, 0, 0)], dtype=np.int64)
NEIGH_COST = np.sqrt((NEIGH ** 2).sum(1)).astype(np.float64)


@nb.njit(cache=True)
def inflate(occ, r_cells):
    """Dilate occupied voxels by r_cells (cube structuring element, separable)."""
    nx, ny, nz = occ.shape
    a = occ.copy()
    b = np.zeros_like(occ)
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if a[x, y, z]:
                    for d in range(max(0, x - r_cells), min(nx, x + r_cells + 1)):
                        b[d, y, z] = True
    c = np.zeros_like(occ)
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if b[x, y, z]:
                    for d in range(max(0, y - r_cells), min(ny, y + r_cells + 1)):
                        c[x, d, z] = True
    out = np.zeros_like(occ)
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                if c[x, y, z]:
                    for d in range(max(0, z - r_cells), min(nz, z + r_cells + 1)):
                        out[x, y, d] = True
    return out


@nb.njit(cache=True)
def _heap_push(hk, hv, size, key, val):
    i = size
    hk[i] = key
    hv[i] = val
    while i > 0:
        p = (i - 1) // 2
        if hk[p] <= hk[i]:
            break
        hk[p], hk[i] = hk[i], hk[p]
        hv[p], hv[i] = hv[i], hv[p]
        i = p
    return size + 1


@nb.njit(cache=True)
def _heap_pop(hk, hv, size):
    key, val = hk[0], hv[0]
    size -= 1
    hk[0] = hk[size]
    hv[0] = hv[size]
    i = 0
    while True:
        l, r, m = 2 * i + 1, 2 * i + 2, i
        if l < size and hk[l] < hk[m]:
            m = l
        if r < size and hk[r] < hk[m]:
            m = r
        if m == i:
            break
        hk[m], hk[i] = hk[i], hk[m]
        hv[m], hv[i] = hv[i], hv[m]
        i = m
    return key, val, size


@nb.njit(cache=True)
def astar_kernel(blocked, start, goal, neigh, ncost):
    """A* on a 26-connected voxel grid. Returns flat cell indices start->goal (empty if none)."""
    nx, ny, nz = blocked.shape
    N = nx * ny * nz
    g = np.full(N, np.inf)
    parent = np.full(N, -1, np.int64)
    closed = np.zeros(N, np.bool_)
    cap = N * 8
    hk = np.empty(cap)
    hv = np.empty(cap, np.int64)
    s = (start[0] * ny + start[1]) * nz + start[2]
    t = (goal[0] * ny + goal[1]) * nz + goal[2]
    g[s] = 0.0
    size = _heap_push(hk, hv, 0, 0.0, s)
    while size > 0:
        _, u, size = _heap_pop(hk, hv, size)
        if closed[u]:
            continue
        closed[u] = True
        if u == t:
            break
        a = u // (ny * nz)
        b = (u // nz) % ny
        c = u % nz
        for k in range(neigh.shape[0]):
            x, y, z = a + neigh[k, 0], b + neigh[k, 1], c + neigh[k, 2]
            if x < 0 or y < 0 or z < 0 or x >= nx or y >= ny or z >= nz:
                continue
            if blocked[x, y, z]:
                continue
            v = (x * ny + y) * nz + z
            ng = g[u] + ncost[k]
            if ng < g[v] and size < cap:
                g[v] = ng
                parent[v] = u
                h = np.sqrt((x - goal[0]) ** 2 + (y - goal[1]) ** 2 + (z - goal[2]) ** 2)
                size = _heap_push(hk, hv, size, ng + h, v)
    if not closed[t]:
        return np.empty(0, np.int64)
    path = [t]
    while path[-1] != s:
        path.append(parent[path[-1]])
    out = np.empty(len(path), np.int64)
    for i in range(len(path)):
        out[i] = path[len(path) - 1 - i]
    return out


@nb.njit(cache=True)
def dijkstra_field(blocked, goal, neigh, ncost):
    """Distance (in cells) from every free voxel to goal; inf where unreachable."""
    nx, ny, nz = blocked.shape
    N = nx * ny * nz
    d = np.full(N, np.inf)
    closed = np.zeros(N, np.bool_)
    cap = N * 8
    hk = np.empty(cap)
    hv = np.empty(cap, np.int64)
    t = (goal[0] * ny + goal[1]) * nz + goal[2]
    d[t] = 0.0
    size = _heap_push(hk, hv, 0, 0.0, t)
    while size > 0:
        _, u, size = _heap_pop(hk, hv, size)
        if closed[u]:
            continue
        closed[u] = True
        a = u // (ny * nz)
        b = (u // nz) % ny
        c = u % nz
        for k in range(neigh.shape[0]):
            x, y, z = a + neigh[k, 0], b + neigh[k, 1], c + neigh[k, 2]
            if x < 0 or y < 0 or z < 0 or x >= nx or y >= ny or z >= nz or blocked[x, y, z]:
                continue
            v = (x * ny + y) * nz + z
            nd = d[u] + ncost[k]
            if nd < d[v] and size < cap:
                d[v] = nd
                size = _heap_push(hk, hv, size, nd, v)
    return d.reshape(nx, ny, nz)


def to_cell(p, res, shape):
    c = np.floor(np.asarray(p) / res).astype(np.int64)
    return np.clip(c, 0, np.array(shape) - 1)


def nearest_free(blocked, cell, max_r=4):
    """Closest unblocked cell (planner start/goal may sit inside inflation)."""
    if not blocked[tuple(cell)]:
        return cell
    best, bd = cell, np.inf
    for d in np.argwhere(~blocked[max(0, cell[0] - max_r):cell[0] + max_r + 1,
                                  max(0, cell[1] - max_r):cell[1] + max_r + 1,
                                  max(0, cell[2] - max_r):cell[2] + max_r + 1]):
        c = d + np.maximum(0, cell - max_r)
        dist = np.sum((c - cell) ** 2)
        if dist < bd:
            best, bd = c, dist
    return best


def astar(blocked, start_xyz, goal_xyz, res):
    """World-frame A* path (k, 3) between two points, or None."""
    s = nearest_free(blocked, to_cell(start_xyz, res, blocked.shape))
    g = nearest_free(blocked, to_cell(goal_xyz, res, blocked.shape))
    idx = astar_kernel(blocked, s, g, NEIGH, NEIGH_COST)
    if len(idx) == 0:
        return None
    nx, ny, nz = blocked.shape
    cells = np.stack([idx // (ny * nz), (idx // nz) % ny, idx % nz], 1)
    pts = (cells + 0.5) * res
    pts[0], pts[-1] = start_xyz, goal_xyz
    return shortcut(blocked, pts, res)


def line_free(blocked, a, b, res, skip=0.0):
    """True if the segment a->b avoids blocked voxels (ignoring its first `skip` m,
    so a drone already inside an inflation margin can still steer out)."""
    L = np.linalg.norm(b - a)
    n = int(np.ceil(L / (res * 0.5))) + 1
    for t in np.linspace(0, 1, n):
        if t * L < skip:
            continue
        c = to_cell(a + t * (b - a), res, blocked.shape)
        if blocked[tuple(c)]:
            return False
    return True


def shortcut(blocked, pts, res):
    """Greedy line-of-sight smoothing; endpoints inside inflation are tolerated."""
    out = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1 and not line_free(blocked, pts[i], pts[j], res):
            j -= 1
        out.append(pts[j])
        i = j
    return np.array(out)


def carrot_on_path(path, p, lookahead=1.5):
    """Point at arc length `lookahead` beyond the closest point of the path to p."""
    seg_a, seg_b = path[:-1], path[1:]
    d = seg_b - seg_a
    L = np.maximum((d ** 2).sum(1), 1e-12)
    t = np.clip(((p - seg_a) * d).sum(1) / L, 0, 1)
    proj = seg_a + t[:, None] * d
    k = int(np.argmin(((proj - p) ** 2).sum(1)))
    remaining = lookahead
    cur = proj[k]
    for j in range(k, len(path) - 1):
        nxt = path[j + 1]
        seg = np.linalg.norm(nxt - cur)
        if seg >= remaining:
            return cur + (nxt - cur) * (remaining / max(seg, 1e-9))
        remaining -= seg
        cur = nxt
    return path[-1].copy()


@nb.njit(cache=True)
def _segment_free(field, i, a0, b0, c0, a1, b1, c1):
    n = max(abs(a1 - a0), abs(b1 - b0), abs(c1 - c0)) * 2 + 1
    for s in range(n + 1):
        t = s / n
        a = int(round(a0 + (a1 - a0) * t))
        b = int(round(b0 + (b1 - b0) * t))
        c = int(round(c0 + (c1 - c0) * t))
        if not np.isfinite(field[i, a, b, c]):
            return False
    return True


@nb.njit(cache=True)
def field_carrot_kernel(field, cells, steps, neigh, out):
    """Greedy descent of a distance field from each start cell for up to `steps`
    moves; returns the furthest cell along it still in straight-line sight."""
    nx, ny, nz = field.shape[1], field.shape[2], field.shape[3]
    for i in range(cells.shape[0]):
        a0, b0, c0 = cells[i, 0], cells[i, 1], cells[i, 2]
        a, b, c = a0, b0, c0
        oa, ob, oc = a0, b0, c0
        for _ in range(steps):
            best = field[i, a, b, c]
            ba, bb, bc = a, b, c
            for k in range(neigh.shape[0]):
                x, y, z = a + neigh[k, 0], b + neigh[k, 1], c + neigh[k, 2]
                if 0 <= x < nx and 0 <= y < ny and 0 <= z < nz and field[i, x, y, z] < best:
                    best = field[i, x, y, z]
                    ba, bb, bc = x, y, z
            if ba == a and bb == b and bc == c:
                break
            a, b, c = ba, bb, bc
            if not np.isfinite(field[i, a0, b0, c0]) or _segment_free(field, i, a0, b0, c0, a, b, c):
                oa, ob, oc = a, b, c
            elif oa != a0 or ob != b0 or oc != c0:
                break
        out[i, 0], out[i, 1], out[i, 2] = oa, ob, oc
