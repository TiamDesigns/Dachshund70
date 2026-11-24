# Cuts rev 1.0's routing out of the area being rebuilt and drops copper that now overlaps a new pad.
# usage: cut.py geom_new.json geom_old.json out.json
import json, sys
from matplotlib.path import Path
g = json.load(open(sys.argv[1])); o = json.load(open(sys.argv[2]))
def inbox(x, y): return (x > 302.8 and y < 112.5) or (x > 316.5 and y < 125.0)
def tin(t): return any(inbox(t[0] + (t[2] - t[0]) * k / 20, t[1] + (t[3] - t[1]) * k / 20) for k in range(21))
newnets = {p['net'] for p in g['pads']}
keep = [t for t in o['tracks'] if not tin(t) and t[6] in newnets]
kv = [[v[0], v[1], v[3]] for v in o['vias'] if not inbox(v[0], v[1]) and v[3] in newnets]
pads = [(p['net'], int(L), Path(poly)) for p in g['pads'] if p['x'] > 302.8 for L, polys in p['poly'].items() for poly in polys if len(poly) > 2]
def hits(t):
    for n, L, P in pads:
        if n == t[6] or L != t[5]: continue
        for k in range(11):
            if P.contains_point((t[0] + (t[2] - t[0]) * k / 10, t[1] + (t[3] - t[1]) * k / 10), radius=t[4] / 2 + 0.15): return True
    return False
bad = [t for t in keep if max(t[0], t[2]) > 302.8 and hits(t)]
keep = [t for t in keep if t not in bad]
kv = [v for v in kv if not (v[0] > 302.8 and any(n != v[2] and P.contains_point((v[0], v[1]), radius=0.45) for n, L, P in pads))]
json.dump({'tracks': keep, 'vias': kv}, open(sys.argv[3], 'w'))
print('kept', len(keep), len(kv), 'dropped for new pads', len(bad))
