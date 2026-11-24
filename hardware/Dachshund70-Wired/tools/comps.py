# For each net, splits existing routing (tracks, vias) plus the pads it touches into connected pieces. Keeps only the
# piece with the most pads per net (the router reconnects the rest from their pads). usage: comps.py geom routes out
import json, sys
from matplotlib.path import Path
g = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2]))
pads = {}
for i, p in enumerate(g['pads']):
    for L, polys in p['poly'].items():
        for poly in polys:
            if len(poly) > 2: pads.setdefault(p['net'], []).append((i, int(L), Path(poly)))
def onseg(t, x, y, tol):
    x1, y1, x2, y2 = t[:4]; dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
    u = 0 if L2 == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
    return (x1 + u * dx - x) ** 2 + (y1 + u * dy - y) ** 2 < tol * tol
out_t, out_v, report = [], [], []
fx_t, fx_v = [], []
nets = {t[6] for t in r['tracks']} | {v[2] for v in r['vias']}
for n in nets:
    T = [t for t in r['tracks'] if t[6] == n]; V = [v for v in r['vias'] if v[2] == n]
    items = [('t', t) for t in T] + [('v', v) for v in V]
    par = list(range(len(items)))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    def u(a, b): par[f(a)] = f(b)
    padof = {}
    for a, (ka, A) in enumerate(items):
        pts = [(A[0], A[1]), (A[2], A[3])] if ka == 't' else [(A[0], A[1])]
        layers = [A[5]] if ka == 't' else [0, 1]
        for b in range(a + 1, len(items)):
            kb, B = items[b]
            if kb == 't':
                lb = [B[5]]
                if not set(layers) & set(lb): continue
                if any(onseg(B, x, y, 0.1) for x, y in pts) or (ka == 't' and any(onseg(A, x, y, 0.1) for x, y in ((B[0], B[1]), (B[2], B[3])))): u(a, b)
            else:
                if ka == 't' and onseg(A, B[0], B[1], 0.1): u(a, b)
                if ka == 'v' and abs(A[0] - B[0]) + abs(A[1] - B[1]) < 0.05: u(a, b)
        for pi, L, P in pads.get(n, []):
            if L in layers and any(P.contains_point((x, y), radius=0.1) for x, y in pts):
                padof.setdefault(pi, []).append(a)
    # join items through shared pads
    for pi, lst in padof.items():
        for a in lst[1:]: u(lst[0], a)
    groups = {}
    for a in range(len(items)): groups.setdefault(f(a), []).append(a)
    npads = {k: len({pi for pi, lst in padof.items() if f(lst[0]) == k}) for k in groups}
    best = max(groups, key=lambda k: (npads[k], len(groups[k])))
    if len([k for k in groups if npads[k] > 0]) > 1 and n != 'GND':
        report.append((n, sorted(npads.values(), reverse=True)))
    keepk = {best} if n != 'GND' else set(groups)
    for k in groups:
        for a in groups[k]:
            if k in keepk: (out_t if items[a][0] == 't' else out_v).append(items[a][1])
            elif npads[k] > 0: (fx_t if items[a][0] == 't' else fx_v).append(items[a][1])
json.dump({'tracks': out_t, 'vias': out_v}, open(sys.argv[3], 'w'))
if len(sys.argv) > 4: json.dump({'tracks': fx_t, 'vias': fx_v}, open(sys.argv[4], 'w')); print('fixed pieces', len(fx_t), len(fx_v))
print('split nets', len(report)); [print(x) for x in report]
print('kept', len(out_t), len(out_v))
