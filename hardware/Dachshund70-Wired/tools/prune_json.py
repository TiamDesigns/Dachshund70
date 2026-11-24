# Removes dead-end copper from router output before it goes on the board: track ends that touch nothing of
# their net (track, via or pad), and vias joined on one layer only. usage: prune_json.py geom.json routes.json out.json
import json, sys
from matplotlib.path import Path
g = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2]))
pads = []
for p in g['pads']:
    for L, polys in p['poly'].items():
        for poly in polys:
            if len(poly) > 2: pads.append((p['net'], int(L), Path(poly)))
def on_pad(net, L, x, y):
    return any(n == net and l == L and P.contains_point((x, y), radius=0.07) for n, l, P in pads)
def key(x, y): return (round(x, 3), round(y, 3))
def on_seg(t, x, y):
    x1, y1, x2, y2 = t[:4]
    dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
    if L2 == 0: return (x1 - x) ** 2 + (y1 - y) ** 2 < 0.08 ** 2
    u = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / L2))
    return ((x1 + u * dx - x) ** 2 + (y1 + u * dy - y) ** 2) < 0.08 ** 2
tracks, vias = list(r['tracks']), list(r['vias'])
removed = 0
while True:
    ends = {}
    for t in tracks:
        for e in ((t[0], t[1]), (t[2], t[3])):
            ends.setdefault((t[6], t[5]) + key(*e), []).append(t)
    vset = {(v[2],) + key(v[0], v[1]) for v in vias}
    dead_t = []
    for t in tracks:
        for x, y in ((t[0], t[1]), (t[2], t[3])):
            k = (t[6], t[5]) + key(x, y)
            if len(ends[k]) > 1 or any(v[2] == t[6] and (v[0] - x) ** 2 + (v[1] - y) ** 2 < 0.3 ** 2 for v in vias) or on_pad(t[6], t[5], x, y): continue
            if any(o is not t and o[6] == t[6] and o[5] == t[5] and on_seg(o, x, y) for o in tracks): continue
            dead_t.append(t); break
    dead_v = []
    for v in vias:
        n = v[2]; layers = 0
        if n == 'GND': continue   # stitching vias join the pours
        for L in (0, 1):
            if any(o[6] == n and o[5] == L and min((o[0] - v[0]) ** 2 + (o[1] - v[1]) ** 2, (o[2] - v[0]) ** 2 + (o[3] - v[1]) ** 2) < 0.3 ** 2 for o in tracks) or on_pad(n, L, v[0], v[1]) or \
               any(o[6] == n and o[5] == L and on_seg(o, v[0], v[1]) for o in tracks): layers += 1
        if layers < 2: dead_v.append(v)
    if not dead_t and not dead_v: break
    ids_t = {id(t) for t in dead_t}; ids_v = {id(v) for v in dead_v}
    tracks = [t for t in tracks if id(t) not in ids_t]; vias = [v for v in vias if id(v) not in ids_v]
    removed += len(dead_t) + len(dead_v)
json.dump({'tracks': tracks, 'vias': vias}, open(sys.argv[3], 'w'))
print('pruned', removed, 'left', len(tracks), len(vias))
