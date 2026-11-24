# Joins router track ends that stop inside a test pad (TP*) to the pad's centre, so they connect for certain.
# usage: snap.py geom.json routes.json
import json, sys
g = json.load(open(sys.argv[1])); r = json.load(open(sys.argv[2]))
tps = [p for p in g['pads'] if p['ref'].startswith('TP') and p['net']]
add = []
for t in r['tracks']:
    for x, y in ((t[0], t[1]), (t[2], t[3])):
        for p in tps:
            d2 = (p['x'] - x) ** 2 + (p['y'] - y) ** 2
            if p['net'] == t[6] and 1e-6 < d2 < 0.7 ** 2 and t[5] in p['layers']:
                add.append([x, y, p['x'], p['y'], t[4], t[5], t[6]])
r['tracks'] += add
json.dump(r, open(sys.argv[2], 'w')); print('snapped', len(add))
