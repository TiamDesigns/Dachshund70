# Builds a fix-up pass: takes the routed result, removes the given nets' router tracks near DRC clearance spots
# (and whole nets listed in RIP), and writes EX for another router run. usage: fixpass.py routes.json drc.json out.json RIP,NETS
import json, sys
r = json.load(open(sys.argv[1])); d = json.load(open(sys.argv[2])); rip = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else set()
spots = []
for x in d['violations']:
    if x['type'] in ('clearance', 'shorting_items', 'tracks_crossing'):
        for i in x['items']:
            if i['description'].startswith('Track') or i['description'].startswith('Via'):
                net = i['description'].split('[')[1].split(']')[0]
                spots.append((net, i['pos']['x'], i['pos']['y']))
def near(t, net):
    return any(n == net and min((t[0] - x) ** 2 + (t[1] - y) ** 2, (t[2] - x) ** 2 + (t[3] - y) ** 2) < 1.5 ** 2 for n, x, y in spots)
T = [t for t in r['tracks'] if t[6] not in rip and not near(t, t[6])]
V = [v for v in r['vias'] if v[2] not in rip and not any(n == v[2] and (v[0] - x) ** 2 + (v[1] - y) ** 2 < 1.0 for n, x, y in spots)]
print('removed', len(r['tracks']) - len(T), 'tracks', len(r['vias']) - len(V), 'vias; spots', spots)
json.dump({'tracks': T, 'vias': V}, open(sys.argv[3], 'w'))
