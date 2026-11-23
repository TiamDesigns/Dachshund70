"""Grid maze router for the Dachshund70 wired mainboard (2 layers).

geom.json (from export_geom.py) -> routes.json (tracks and vias). Nets are routed one connection at a time
with a multi-source Dijkstra over a 0.1 mm grid, both copper layers, vias between them. Clearances are
modelled by dilating every obstacle by clearance + half the track width, so the router only moves centre lines.
"""
import json, sys, math, time
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, sparse
from scipy.sparse.csgraph import dijkstra

G = 0.1                     # grid pitch, mm
CLR = 0.15                  # copper clearance, mm (Default netclass)
HW = 0.075                  # half width of the narrowest track (keep-outs are built for it)
MARGIN = 0.02               # extra safety on every keep-out
VIA_D, VIA_DRILL = 0.6, 0.3
HOLE_CLR = 0.25
EDGE_CLR, CUT_CLR = 0.5, 0.3
VIA_COST = 3.0              # mm-equivalent
WIDTH = {'LED_5V': 0.5, 'VBUS': 0.5, '+3V3': 0.2, 'GND': 0.3, '+1V1': 0.2}

geom = json.load(open(sys.argv[1]))
order = json.load(open(sys.argv[2]))          # list of net names in routing order
out_path = sys.argv[3]

allx = [p[0] for o in geom['outline'] for p in o]; ally = [p[1] for o in geom['outline'] for p in o]
X0, Y0 = min(allx) - 1, min(ally) - 1
NX, NY = int((max(allx) + 1 - X0) / G) + 1, int((max(ally) + 1 - Y0) / G) + 1

def to_px(pts):
    return [((x - X0) / G - 0.5, (y - Y0) / G - 0.5) for x, y in pts]

def raster_full(polys):
    im = Image.new('1', (NX, NY), 0); d = ImageDraw.Draw(im)
    for p in polys: d.polygon(to_px(p), fill=1, outline=1)
    return np.array(im, dtype=bool)

# --- board edge distance (outer outline and the LED light cutouts) ---
inside = raster_full(geom['outline'])
holes = raster_full(geom['holes']) if geom['holes'] else np.zeros_like(inside)
d_out = ndimage.distance_transform_edt(inside) * G
d_cut = ndimage.distance_transform_edt(~holes) * G
def edge_ok(r):  # r = half width            # centre lines that keep r mm of copper (half width) clear of both edges
    return (d_out >= EDGE_CLR + r + MARGIN + 0.08) & (d_cut >= CUT_CLR + r + MARGIN + 0.08)

nets = {}
def nid(name):
    if name not in nets: nets[name] = len(nets) + 1
    return nets[name]

keep = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]   # 0 free, -2 blocked, n only net n
own = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]    # copper of net n (pads, tracks)

from matplotlib.path import Path as MPath
def sdist(polys, r):
    """Signed distance (mm, negative inside) from every cell centre in a window to the polygons; a polygon of
    one point is a circle centre. Returns (dist, window)."""
    xs = [x for p in polys for x, _ in p]; ys = [y for p in polys for _, y in p]
    pad = r + 3 * G
    i0 = max(0, int((min(xs) - pad - X0) / G)); i1 = min(NX, int((max(xs) + pad - X0) / G) + 2)
    j0 = max(0, int((min(ys) - pad - Y0) / G)); j1 = min(NY, int((max(ys) + pad - Y0) / G) + 2)
    cx = X0 + (np.arange(i0, i1) + 0.5) * G; cy = Y0 + (np.arange(j0, j1) + 0.5) * G
    PX, PY = np.meshgrid(cx, cy)
    best = np.full(PX.shape, 1e9)
    for poly in polys:
        P = np.array(poly, float)
        if len(P) == 1:
            d = np.hypot(PX - P[0, 0], PY - P[0, 1])
        elif len(P) == 2:
            (ax, ay), (bx, by) = P; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-12
            t = np.clip(((PX - ax) * dx + (PY - ay) * dy) / L2, 0, 1)
            d = np.hypot(PX - ax - t * dx, PY - ay - t * dy)
        else:
            A = P; B = np.roll(P, -1, axis=0)
            d = np.full(PX.shape, 1e9)
            for (ax, ay), (bx, by) in zip(A, B):
                dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-12
                t = np.clip(((PX - ax) * dx + (PY - ay) * dy) / L2, 0, 1)
                d = np.minimum(d, np.hypot(PX - ax - t * dx, PY - ay - t * dy))
            ins = MPath(P).contains_points(np.c_[PX.ravel(), PY.ravel()]).reshape(PX.shape)
            d = np.where(ins, -d, d)
        best = np.minimum(best, d)
    return best, (j0, j1, i0, i1)

def local_mask(polys, r):
    d, w = sdist(polys, r)
    return d <= r + 1e-9, w

def stamp(layer, mask, win, n):
    j0, j1, i0, i1 = win
    k = keep[layer][j0:j1, i0:i1]
    if n < 0:
        k[mask] = -2; return
    free = mask & (k == 0); k[free] = n
    clash = mask & (k != n) & (k != 0); k[clash] = -2

def stamp_own(layer, mask, win, n):
    j0, j1, i0, i1 = win
    own[layer][j0:j1, i0:i1][mask] = n

def seg_poly(x1, y1, x2, y2, r):
    """Capsule outline around a segment."""
    a = math.atan2(y2 - y1, x2 - x1)
    pts = []
    for k in range(9):
        t = a - math.pi / 2 + k * math.pi / 8; pts.append((x2 + r * math.cos(t), y2 + r * math.sin(t)))
    for k in range(9):
        t = a + math.pi / 2 + k * math.pi / 8; pts.append((x1 + r * math.cos(t), y1 + r * math.sin(t)))
    return pts

# --- pads ---
pins = {}          # net -> list of pins; a pin = list of (layer, j, i) terminal cells
for p in geom['pads']:
    if p.get('npth') or (p['drill'] and not p['layers']):
        r = p['drill'] / 2 + HOLE_CLR + HW + MARGIN
        m, w = local_mask([[(p['x'], p['y'])]], r)
        stamp(0, m, w, -1); stamp(1, m, w, -1)
        continue
    n = nid(p['net']) if p['net'] else -1
    if p['drill']:   # plated hole: keep the via-sized area clear on both layers
        pass
    term = []
    for L in p['layers']:
        polys = p['poly'][str(L)] if str(L) in p['poly'] else p['poly'][L]
        m, w = local_mask(polys, CLR + HW + MARGIN)
        stamp(L, m, w, n)
        dd, wc = sdist(polys, 0)
        core = dd <= 0
        stamp_own(L, core, wc, max(n, 0))
        if n > 0:
            er = dd <= -0.03
            if er.sum() == 0: er = core
            jj, ii = np.nonzero(er)
            term += [(L, j + wc[0], i + wc[2]) for j, i in zip(jj, ii)]
    if n > 0 and term:
        pins.setdefault(p['net'], []).append({'cells': term, 'ref': p['ref'] + '.' + p['num'], 'x': p['x'], 'y': p['y']})

fails = {}
FINE = {p['net'] for p in geom['pads'] if p['ref'] in ('U1', 'J4') and p['net']}
disk2 = ndimage.generate_binary_structure(2, 1)

def disk(r):
    k = int(math.ceil(r / G)); y, x = np.ogrid[-k:k + 1, -k:k + 1]
    return (x * x + y * y) * G * G <= r * r + 1e-9

TREES = {}      # net -> cells already connected (kept between passes)
DONE = {}       # net -> refs of pins already in the tree
ROUTES = {}     # net -> {'tracks': [...], 'vias': [...]}
base_keep = [k.copy() for k in keep]; base_own = [o.copy() for o in own]
trk = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]   # first net whose track keep-out covers a cell
trk2 = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]  # a second, different net

def mark(L, win, m, n):
    j0, j1, i0, i1 = win
    t1 = trk[L][j0:j1, i0:i1]; t2 = trk2[L][j0:j1, i0:i1]
    t2[m & (t1 != 0) & (t1 != n)] = n
    t1[m & (t1 == 0)] = n
from collections import deque, Counter
QUEUE = deque(); RIPS = Counter(); PEN = 20.0; MAXRIP = 400; total = [0]
INV = {}
PRE = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {'tracks': [], 'vias': []}
PRE_TREE, PRE_DONE = {}, {}
def seg_cells(L, x1, y1, x2, y2):
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / (G / 2)))
    return {(L, int(round((y1 + (y2 - y1) * t / n - Y0) / G - 0.5)), int(round((x1 + (x2 - x1) * t / n - X0) / G - 0.5))) for t in range(n + 1)}
def stamp_pre():
    for x1, y1, x2, y2, w, L, name in PRE['tracks']: stamp_track(L, x1, y1, x2, y2, w, nets[name])
    for x, y, name in PRE['vias']: stamp_via(x, y, nets[name])

def region_pin(x0, y0, x1, y1, L):
    i0, i1 = int((x0 - X0) / G), int((x1 - X0) / G); j0, j1 = int((y0 - Y0) / G), int((y1 - Y0) / G)
    cells = [(L, j, i) for j in range(j0, j1) for i in range(i0, i1)]
    return {'cells': cells, 'ref': 'region', 'x': (x0 + x1) / 2, 'y': (y0 + y1) / 2}

def stamp_track(L, x1, y1, x2, y2, w, n):
    m, win = local_mask([[(x1, y1), (x2, y2)]], w / 2 + CLR + HW + MARGIN)
    stamp(L, m, win, n)
    mark(L, win, m, n)
    core, wc = local_mask([[(x1, y1), (x2, y2)]], w / 2)
    stamp_own(L, core, wc, n)

def stamp_via(x, y, n):
    m, win = local_mask([[(x, y)]], VIA_D / 2 + CLR + HW + MARGIN)
    j0, j1, i0, i1 = win
    for L in (0, 1):
        stamp(L, m, win, n); mark(L, win, m, n)
    core, wc = local_mask([[(x, y)]], VIA_D / 2)
    stamp_own(0, core, wc, n); stamp_own(1, core, wc, n)

def rebuild():
    for L in (0, 1):
        keep[L][:] = base_keep[L]; own[L][:] = base_own[L]; trk[L][:] = 0; trk2[L][:] = 0
    stamp_pre()
    for name, r in ROUTES.items():
        n = nets[name]
        for x1, y1, x2, y2, w, L, _ in r['tracks']: stamp_track(L, x1, y1, x2, y2, w, n)
        for x, y, _ in r['vias']: stamp_via(x, y, n)

def rip(v):
    ROUTES.pop(v, None); TREES.pop(v, None); DONE.pop(v, None); fails.pop(v, None)

def route_net(name, refs=None, region=None):
    n = nets[name]; w = WIDTH.get(name, 0.15); extra = w / 2 - HW
    plist = [q for q in pins.get(name, []) if refs is None or q['ref'].split('.')[0] in refs]
    plist = [q for q in plist if q['ref'] not in DONE.setdefault(name, set())]
    plist.sort(key=lambda q: (q['x'], q['y']))
    if region: plist.append(region_pin(*region))
    if name not in TREES and name in PRE_TREE:
        TREES[name] = set(PRE_TREE[name]); DONE[name] = set(PRE_DONE[name])
        plist = [q for q in plist if q['ref'] not in DONE[name]]
    if name in TREES:
        tree = TREES[name]; todo = plist
    else:
        if len(plist) < 2: return
        tree = set(plist[0]['cells']); DONE[name].add(plist[0]['ref']); todo = plist[1:]
    TREES[name] = tree
    while todo:
        tx = np.array([c[2] for c in tree]); ty = np.array([c[1] for c in tree])
        def dist(q):
            qi = (q['x'] - X0) / G; qj = (q['y'] - Y0) / G
            return np.min(np.abs(tx - qi) + np.abs(ty - qj))
        todo.sort(key=dist); tgt = todo.pop(0)
        res = None
        for marg in (40, 120, 400):
            res = connect(n, name, w, extra, tree, tgt, marg)
            if res: break
        if not res and total[0] < MAXRIP:
            soft = connect(n, name, w, extra, tree, tgt, 400, soft=True)
            pass
            if soft and not isinstance(soft[0], str):
                res = soft; soft = None
            if soft:
                victims = [v for v in soft if RIPS[v] < 8]
                if victims and len(victims) == len(soft):
                    for v in victims:
                        rip(v); RIPS[v] += 1; total[0] += 1; QUEUE.append([v, None, None])
                    rebuild()
                    for marg in (40, 120, 400):
                        res = connect(n, name, w, extra, tree, tgt, marg)
                        if res: break
        if not res:
            fails.setdefault(name, []).append(tgt['ref']); continue
        for c in res: tree.add(c)
        if tgt['ref'] != 'region':
            tree.update(tgt['cells']); DONE[name].add(tgt['ref'])

def shifted(arr, dj, di, H, W, first):
    if first:
        return arr[0:H - dj, 0:W - di] if di >= 0 else arr[0:H - dj, -di:W]
    return arr[dj:H, di:W] if di >= 0 else arr[dj:H, 0:W + di]

def connect(n, name, w, extra, tree, tgt, marg, soft=False):
    tl = list(tree)
    tj = np.array([c[1] for c in tl]); ti = np.array([c[2] for c in tl])
    qj = np.mean([c[1] for c in tgt['cells']]); qi = np.mean([c[2] for c in tgt['cells']])
    near = tl[int(np.argmin(np.abs(tj - qj) + np.abs(ti - qi)))]
    cells = [near] + tgt['cells']
    forced = [near] + ([] if tgt['ref'] == 'region' else tgt['cells'])
    js = [c[1] for c in cells]; is_ = [c[2] for c in cells]
    j0 = max(0, min(js) - marg); j1 = min(NY, max(js) + marg + 1)
    i0 = max(0, min(is_) - marg); i1 = min(NX, max(is_) + marg + 1)
    H, W = j1 - j0, i1 - i0
    eo = edge_ok(w / 2)[j0:j1, i0:i1]
    K = base_keep if soft else keep
    OW = base_own if soft else own
    pas, pen = [], []
    for L in (0, 1):
        k = K[L][j0:j1, i0:i1]
        p = ((k == 0) | (k == n)) & eo
        if extra > 1e-6:
            p = ndimage.binary_erosion(p, structure=disk(extra + 0.07), border_value=1)
        pas.append(p)
        kk = keep[L][j0:j1, i0:i1]
        if soft:
            rc = np.zeros(len(nets) + 2); 
            for v, c in RIPS.items(): rc[nets[v]] = c
            pp = np.zeros(kk.shape)
            for T in (trk[L][j0:j1, i0:i1], trk2[L][j0:j1, i0:i1]):
                o = (T > 0) & (T != n)
                pp += np.where(o, 1 + 2 * rc[np.clip(T, 0, None)], 0)
            pen.append(pp * PEN * G)
        else:
            pen.append(None)
    for L, j, i in forced:
        if j0 <= j < j1 and i0 <= i < i1: pas[L][j - j0, i - i0] = True
    vr = VIA_D / 2 - HW + 0.05
    veo = (d_out[j0:j1, i0:i1] >= EDGE_CLR + VIA_D / 2 + MARGIN + 0.08) & (d_cut[j0:j1, i0:i1] >= CUT_CLR + VIA_D / 2 + MARGIN + 0.08)
    base = [((K[L][j0:j1, i0:i1] == 0) | (K[L][j0:j1, i0:i1] == n)) for L in (0, 1)]
    vok = ndimage.binary_erosion(base[0] & base[1], structure=disk(vr), border_value=1) & veo
    for L in (0, 1):   # no via in any pad; a via may sit on this net's own track
        o = OW[L][j0:j1, i0:i1]
        vok &= ((o == 0) | (o == n)) & (base_own[L][j0:j1, i0:i1] == 0)
    idx = -np.ones((2, H, W), np.int64)
    N = 0
    for L in (0, 1):
        m = pas[L]; c = int(m.sum()); idx[L][m] = np.arange(N, N + c); N += c
    rows, cols, wts = [], [], []
    for L in (0, 1):
        hcost, vcost = (1.0, 2.5) if L == 0 else (2.5, 1.0)
        for dj, di, cst in ((0, 1, hcost), (1, 0, vcost), (1, 1, 1.6), (1, -1, 1.6)):
            a = shifted(idx[L], dj, di, H, W, True); b = shifted(idx[L], dj, di, H, W, False)
            m = (a >= 0) & (b >= 0)
            wt = np.full(int(m.sum()), cst * G)
            if soft:
                wt = wt + (shifted(pen[L], dj, di, H, W, True)[m] + shifted(pen[L], dj, di, H, W, False)[m]) / 2
            rows.append(a[m]); cols.append(b[m]); wts.append(wt)
    m = vok & (idx[0] >= 0) & (idx[1] >= 0)
    vw = np.full(int(m.sum()), VIA_COST)
    if soft: vw = vw + pen[0][m] + pen[1][m]
    rows.append(idx[0][m]); cols.append(idx[1][m]); wts.append(vw)
    A = sparse.coo_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(N, N)).tocsr()
    src = [idx[L, j - j0, i - i0] for L, j, i in tree if j0 <= j < j1 and i0 <= i < i1]
    src = [s for s in src if s >= 0]
    dst = [idx[L, j - j0, i - i0] for L, j, i in tgt['cells'] if j0 <= j < j1 and i0 <= i < i1]
    dst = [s for s in dst if s >= 0]
    if not src or not dst: return None
    dist, pred, _ = dijkstra(A, directed=False, indices=src, min_only=True, return_predecessors=True)
    dd = dist[dst]; k = int(np.argmin(dd))
    if not np.isfinite(dd[k]): return None
    node = dst[k]; path = []
    while node >= 0:
        path.append(node); node = pred[node]
    Ls, Js, Is = np.nonzero(idx >= 0)
    order_ids = idx[Ls, Js, Is]
    lut = np.empty(N, np.int64); lut[order_ids] = np.arange(len(order_ids))
    cells = []
    for nd in path[::-1]:
        q = lut[nd]; cells.append((int(Ls[q]), int(Js[q]) + j0, int(Is[q]) + i0))
    if soft:
        if not INV: INV.update({v: k for k, v in nets.items()})
        hit = set()
        def owners(L, j, i, r):
            k = int(math.ceil(r / G))
            for T in (trk[L], trk2[L]):
                blk = T[max(0, j - k):j + k + 1, max(0, i - k):i + k + 1]
                for o in np.unique(blk):
                    if o > 0 and o != n: hit.add(INV[o])
            blk = base_keep[L][max(0, j - k):j + k + 1, max(0, i - k):i + k + 1]
            if ((blk != 0) & (blk != n)).any(): hit.add('?')
        for a, (L, j, i) in enumerate(cells):
            owners(L, j, i, max(extra + 0.07, 0))
            if a and cells[a - 1][0] != L:      # a via here
                owners(0, j, i, vr); owners(1, j, i, vr)
        if '?' in hit:
            hit.discard('?')
            if not hit: return None
        if hit: return sorted(hit)
        # nothing but this net's own copper in the way: the path is legal as it is
    emit(cells, n, name, w)
    return cells

def cxy(j, i): return X0 + (i + 0.5) * G, Y0 + (j + 0.5) * G

def emit(cells, n, name, w):
    r = ROUTES.setdefault(name, {'tracks': [], 'vias': []})
    runs = [[cells[0]]]
    for c in cells[1:]:
        if c[0] != runs[-1][-1][0]:
            x, y = cxy(c[1], c[2]); r['vias'].append([round(x, 3), round(y, 3), name])
            stamp_via(x, y, n)
            runs.append([c])
        else:
            runs[-1].append(c)
    for run in runs:
        if len(run) < 2: continue
        L = run[0][0]
        pts = [run[0]]
        for a, b, c in zip(run, run[1:], run[2:]):
            if (b[1] - a[1], b[2] - a[2]) != (c[1] - b[1], c[2] - b[2]): pts.append(b)
        pts.append(run[-1])
        for a, b in zip(pts, pts[1:]):
            x1, y1 = cxy(a[1], a[2]); x2, y2 = cxy(b[1], b[2])
            r['tracks'].append([round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3), w, L, name])
            stamp_track(L, x1, y1, x2, y2, w, n)

for x1, y1, x2, y2, w, L, name in PRE['tracks']:
    PRE_TREE.setdefault(name, set()).update(seg_cells(L, x1, y1, x2, y2))
for x, y, name in PRE['vias']:
    PRE_TREE.setdefault(name, set()).update(seg_cells(0, x, y, x, y) | seg_cells(1, x, y, x, y))
for name, cs in PRE_TREE.items():
    for q in pins.get(name, []):
        if cs & set(q['cells']): PRE_DONE.setdefault(name, set()).add(q['ref']); cs.update(q['cells'])
stamp_pre()
t0 = time.time()
for step in order:
    QUEUE.append(step if not isinstance(step, str) else [step, None, None])
while QUEUE:
    name, refs, region = QUEUE.popleft()
    if name not in nets: print('no such net', name); continue
    t = time.time(); route_net(name, refs, region)
    print(f'{name} {refs or ""}: {time.time() - t:.1f}s rips {total[0]}', flush=True)
tracks = [t for r in ROUTES.values() for t in r['tracks']]
vias = [v for r in ROUTES.values() for v in r['vias']]
fl = [(k, v) for k, vs in fails.items() for v in vs]
json.dump({'tracks': tracks, 'vias': vias, 'fails': fl}, open(out_path, 'w'))
print('done', len(tracks), 'tracks', len(vias), 'vias', len(fl), 'fails', f'{time.time() - t0:.0f}s')
for f in fl: print('FAIL', f)
