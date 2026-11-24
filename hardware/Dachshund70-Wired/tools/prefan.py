# Staircase fan-out of the RP2040's left-hand pins (B.Cu) to two staggered via columns.
import json, sys
g = json.load(open(sys.argv[1]))
U = [p for p in g['pads'] if p['ref'] == 'U1' and p['num'] and p['num'] != '57']
left = sorted([p for p in U if p['x'] < 311], key=lambda p: p['y'])
assert len(left) == 14, len(left)
yc = sum(p['y'] for p in left) / 14
xpad = left[0]['x']
tracks, vias = [], []
W = 0.15
for k, p in enumerate(left):
    y = p['y']; n = p['net']
    if k <= 6:
        yp = yc - 0.8 * (6.5 - k); xk = xpad - 1.16 - 0.4 * k
    else:
        yp = yc + 0.8 * (k - 6.5); xk = xpad - 1.16 - 0.4 * (13 - k)
    xv = 304.6 if k % 2 == 0 else 303.8
    pts = [(xpad - 0.15, y), (xk, y), (xk, yp), (xv, yp)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if abs(x1 - x2) + abs(y1 - y2) > 1e-6:
            tracks.append([round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3), W, 1, n])
    if n == '+3V3':
        tracks[:] = [t for t in tracks if not (t[6] == n and abs(t[1] - y) < 1e-6 and len(tracks) and False)]
    vias.append([xv, round(yp, 3), n])
right = sorted([p for p in U if p['x'] > 317], key=lambda p: p['y'])
assert len(right) == 14
xr = right[0]['x']
for k, p in enumerate(right):
    y = p['y']; n = p['net']
    if k <= 6:
        yp = yc - 0.8 * (6.5 - k); xk = xr + 1.16 + 0.4 * k
    else:
        yp = yc + 0.8 * (k - 6.5); xk = xr + 1.16 + 0.4 * (13 - k)
    xv = 321.6 if k % 2 == 0 else 322.4
    pts = [(xr + 0.15, y), (xk, y), (xk, yp), (xv, yp)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if abs(x1 - x2) + abs(y1 - y2) > 1e-6:
            tracks.append([round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3), W, 1, n])
    if n == '+3V3':
        tracks[:] = [t for t in tracks if not (t[6] == n and abs(t[1] - y) < 1e-6 and len(tracks) and False)]
    vias.append([xv, round(yp, 3), n])
tracks = [t for t in tracks if t[6] != '+3V3']; vias = [v for v in vias if v[2] != '+3V3']
# TESTEN (pin 19) straight into the exposed pad
p19 = [p for p in U if p['num'] == '19'][0]
tracks.append([p19['x'], p19['y'], p19['x'], round(yc - 1.5 if p19['y'] < yc else yc + 1.5, 3), W, 1, 'GND'])
json.dump({'tracks': tracks, 'vias': vias}, open(sys.argv[2], 'w'))
print(len(tracks), len(vias), [p['net'] for p in left])
