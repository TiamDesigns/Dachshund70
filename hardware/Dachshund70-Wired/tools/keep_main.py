# For the named nets, keep only the copper connected to the net's biggest connected piece (tracks, vias and the
# pads they land on); the rest is dropped so the router re-routes those pins. usage: keep_main.py geom in out net...
import json, sys, math
from matplotlib.path import Path
g = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2])); names = sys.argv[4:]
for name in names:
    pads = []
    for p in g['pads']:
        if p['net'] != name: continue
        for L, polys in p['poly'].items():
            for poly in polys:
                if len(poly) > 2: pads.append((int(L), Path(poly)))
    T = [t for t in r['tracks'] if t[6] == name]; V = [v for v in r['vias'] if v[2] == name]
    items = [('t', t) for t in T] + [('v', v) for v in V]
    par = list(range(len(items)))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    def ends(it):
        k, o = it
        return [(o[5], o[0], o[1]), (o[5], o[2], o[3])] if k == 't' else [(0, o[0], o[1]), (1, o[0], o[1])]
    def near(a, b):
        return a[0] == b[0] and math.hypot(a[1] - b[1], a[2] - b[2]) < 0.1
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if any(near(a, b) for a in ends(items[i]) for b in ends(items[j])): par[f(i)] = f(j)
    # pads join everything that lands on them
    for L, P in pads:
        hit = [i for i in range(len(items)) if any(e[0] == L and P.contains_point((e[1], e[2]), radius=0.07) for e in ends(items[i]))]
        for i in hit[1:]: par[f(i)] = f(hit[0])
    groups = {}
    for i in range(len(items)): groups.setdefault(f(i), []).append(i)
    main = max(groups.values(), key=len) if groups else []
    keep = {id(items[i][1]) for i in main}
    before = len(T) + len(V)
    r['tracks'] = [t for t in r['tracks'] if t[6] != name or id(t) in keep]
    r['vias'] = [v for v in r['vias'] if v[2] != name or id(v) in keep]
    print(name, 'pieces', len(groups), 'dropped', before - len(main))
json.dump(r, open(sys.argv[3], 'w'))
