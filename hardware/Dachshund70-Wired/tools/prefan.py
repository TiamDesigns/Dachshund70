# Fixed pre-routes around the RP2350B (U1, QFN-80, on the back):
#  - staircase fan-outs of the left (matrix) and right (screen) signal pins to staggered via columns (B.Cu)
#  - an inner +3V3 ring in three arcs and a +1V1 arch inside the pad ring, joined to the pins by short spokes,
#    with the +3V3 arcs tied together on F.Cu under the chip
#  - PGND (pin 62) into the exposed pad, a GND via in the exposed pad, VREG_LX to L1, VREG_FB to a via
# usage: prefan2.py geom.json pre.json
import json, sys
g = json.load(open(sys.argv[1]))
U = {p['num']: p for p in g['pads'] if p['ref'] == 'U1' and p['num']}
cx = sum(U[str(k)]['x'] for k in (1, 41)) / 2; cy = sum(U[str(k)]['y'] for k in (21, 61)) / 2
T, V = [], []
def tr(pts, w, L, n):
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if abs(x1 - x2) + abs(y1 - y2) > 1e-6:
            T.append([round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3), w, L, n])
def via(x, y, n): V.append([round(x, 3), round(y, 3), n])
PWR = ('+3V3', '+1V1', 'GND')
def sig(p): return p['net'] not in PWR and not p['net'].startswith('unconnected')

def stair(pins, side, xv0, xv1, step=0.35, pitch=0.8, first=1.1, yc=None):
    """Spreads pins (one side, any gaps between them) to a via each at `pitch`, without crossings: pins that move
    up take ranks from the top down, pins that move down from the bottom up, so inner verticals stay short."""
    pins = sorted(pins, key=lambda p: p['y']); N = len(pins); mid = (N - 1) / 2
    yc = yc if yc is not None else sum(p['y'] for p in pins) / N
    xpad = pins[0]['x']
    yp = [yc + pitch * (k - mid) for k in range(N)]
    up = [k for k in range(N) if yp[k] < pins[k]['y'] - 1e-6]
    down = [k for k in range(N) if yp[k] > pins[k]['y'] + 1e-6][::-1]
    rank = {k: 0 for k in range(N)}
    for i, k in enumerate(up): rank[k] = i
    for i, k in enumerate(down): rank[k] = i
    for k, p in enumerate(pins):
        xk = xpad + side * (first + step * rank[k])
        xv = xv0 if k % 2 == 0 else xv1
        tr([(p['x'], p['y']), (xk, p['y']), (xk, yp[k]), (xv, yp[k])], 0.15, 1, p['net'])
        via(xv, yp[k], p['net'])
    return [(V[-N + k][0], V[-N + k][1], pins[k]['net']) for k in range(N)]

left = [p for p in U.values() if p['x'] < cx - 4 and sig(p)]
right = [p for p in U.values() if p['x'] > cx + 4 and sig(p) and p['net'].startswith(('/DISP', '/TP_'))]
stair(left, -1, 305.0, 304.2)
ubus = stair(right, +1, 322.9, 323.7)

# inner rings
R3, R1 = 3.55, 2.55
xl, xr, yt, yb = cx - R3, cx + R3, cy - R3, cy + R3
P = lambda n: U[str(n)]
W3, W1 = 0.2, 0.2
# arc TL: left side from pin 15 level-ish down to just above pin 10's spoke, over the top to pin 29
tr([(xl, P(15)['y']), (xl, yt), (P(29)['x'], yt)], W3, 1, '+3V3')
# arc TR: right side between pin 41 and pin 50
tr([(xr, P(41)['y']), (xr, P(50)['y'])], W3, 1, '+3V3')
# arc B: left side below pin 10's spoke, along the bottom to pin 64
tr([(xl, P(5)['y']), (xl, yb), (P(68)['x'], yb)], W3, 1, '+3V3')
for n in (15, 5):  tr([(P(n)['x'], P(n)['y']), (xl, P(n)['y'])], W3, 1, '+3V3')
for n in (24, 29): tr([(P(n)['x'], P(n)['y']), (P(n)['x'], yt)], W3, 1, '+3V3')
for n in (41, 50): tr([(P(n)['x'], P(n)['y']), (xr, P(n)['y'])], W3, 1, '+3V3')
# arc R: right side below pin 51's spoke, pins 59 and 60, with a via tied on F.Cu to the TR arc's via
tr([(xr, P(51)['y'] + 1.6), (xr, P(59)['y'])], W3, 1, '+3V3')
tr([(P(59)['x'], P(59)['y']), (xr, P(59)['y'])], W3, 1, '+3V3')
tr([(P(59)['x'], P(59)['y']), (P(59)['x'] + 0.6, P(59)['y']), (P(60)['x'] + 0.6, P(60)['y']), (P(60)['x'], P(60)['y'])], W3, 1, '+3V3')
vR = (xr, P(51)['y'] + 1.6); via(*vR, '+3V3')
for n in (76, 69, 68): tr([(P(n)['x'], P(n)['y']), (P(n)['x'], yb)], W3, 1, '+3V3')
# +1V1 arch over the exposed pad: pins 10 (left), 32 (top), 51 (right)
a, b = cx - R1, cx + R1; yt1 = cy - R1
tr([(P(10)['x'], P(10)['y']), (a, P(10)['y']), (a, yt1), (b, yt1), (b, P(51)['y']), (P(51)['x'], P(51)['y'])], 0.15, 1, '+1V1')
tr([(P(32)['x'], P(32)['y']), (P(32)['x'], yt1)], 0.15, 1, '+1V1')
via(b, cy + 0.4, '+1V1'); tr([(b, P(51)['y']), (b, cy + 0.4)], 0.15, 1, '+1V1')
# +3V3 arcs joined on F.Cu under the chip
vTL, vBL, vTR = (xl, yt), (xl, yb), (xr, (P(41)['y'] + P(50)['y']) / 2)
for v in (vTL, vBL, vTR): via(*v, '+3V3')
tr([vBL, vTL, (xr, yt), vTR, vR], 0.3, 0, '+3V3')
# GND: PGND into the exposed pad, one via in the pad
p62 = P(62)
tr([(p62['x'], p62['y']), (p62['x'], yb + 0.65), (cx + 1.5, cy + 1.3)], 0.2, 1, 'GND')
via(cx, cy, 'GND')
# VREG_LX to L1 pad 1, VREG_FB to a via
L1 = {p['num']: p for p in g['pads'] if p['ref'] == 'L1'}
p63 = P(63)
tr([(p63['x'], p63['y']), (p63['x'], L1['1']['y']), (L1['1']['x'], L1['1']['y'])], 0.25, 1, '/VREG_LX')
p65 = P(65)
tr([(p65['x'], p65['y']), (p65['x'], p65['y'] + 1.0), (p65['x'] + 0.2, p65['y'] + 1.65)], 0.15, 1, '+1V1')
via(p65['x'] + 0.2, p65['y'] + 1.65, '+1V1')

# GND: short links from the regulator caps and the screen/USB connectors' ground pins to vias or mounting pads
def pad(ref, num): return [p for p in g['pads'] if p['ref'] == ref and p['num'] == num][0]
def pc(ref, num): q = pad(ref, num); return (q['x'], q['y'])
gv1 = (322.6, 97.6); via(*gv1, 'GND')
tr([pc('C27', [q['num'] for q in g['pads'] if q['ref'] == 'C27' and q['net'] == 'GND'][0]), gv1], 0.2, 1, 'GND')
tr([pc('C10', '2'), gv1], 0.2, 1, 'GND')
gv3 = (323.0, 102.2); via(*gv3, 'GND')
c7 = pc('C7', '2'); tr([c7, (c7[0], gv3[1]), gv3], 0.2, 1, 'GND'); tr([pc('C8', '2'), gv3], 0.2, 1, 'GND')
c9 = pc('C9', '2'); gv4 = (c9[0], c9[1] + 0.95); via(*gv4, 'GND'); tr([c9, gv4], 0.2, 1, 'GND')
j3, j5 = pc('J4', '3'), pc('J4', '5')
j4sig = [q for q in g['pads'] if q['ref'] == 'J4' and q['num'] not in ('MP',) and sig(q)]
mps = sorted(q['y'] for q in g['pads'] if q['ref'] == 'J4' and q['num'] == 'MP')
jbus = stair(j4sig, +1, 324.3, 325.1, pitch=0.6)
# screen and touch bus on F.Cu: J4's order is the chip's reversed, so the lines nest as U-shapes in lanes left of
# both via columns (the first line from the top of the chip takes the leftmost lane and J4's bottom pin)
jn = {n: (x, y) for x, y, n in jbus}
for k, (x, y, n) in enumerate(ubus):
    lane = 318.6 + 0.3 * k; xj, yj = jn[n]
    tr([(x, y), (lane, y), (lane, yj), (xj, yj)], 0.15, 0, n)
gj = (j3[0] - 1.7, (j3[1] + j5[1]) / 2); via(*gj, 'GND')
tr([j3, (j3[0] - 1.0, j3[1]), gj], 0.2, 1, 'GND'); tr([j5, (j5[0] - 1.0, j5[1]), gj], 0.2, 1, 'GND')
j14 = pc('J1', '4')
# VREG_AVDD: pin 61 to R11 and C27
p61 = P(61); r = pc('R11', '2'); c27 = pc('C27', '1')
tr([(p61['x'], p61['y']), (p61['x'], 96.65), (r[0], 96.65), r], 0.2, 1, '/VREG_AVDD'); tr([(c27[0], 96.65), c27], 0.2, 1, '/VREG_AVDD')
tr([j14, (322.6, j14[1]), (322.6, 109.4), (324.2, 110.0)], 0.2, 1, 'GND')

# R11.1 to the +3V3 link between pins 59 and 60
r1 = pc('R11', '1'); tr([r1, (r1[0], 95.3), (P(60)['x'] + 0.6, 95.3), (P(60)['x'] + 0.6, P(60)['y'])], 0.2, 1, '+3V3')
def gpad(ref): return [(q['x'], q['y']) for q in g['pads'] if q['ref'] == ref and q['net'] == 'GND'][0]
# C5 and C11 grounds: a via each
c5 = gpad('C5'); v5 = (c5[0] - 1.1, c5[1]); via(*v5, 'GND'); tr([c5, v5], 0.2, 1, 'GND')
c11 = gpad('C11'); v11 = (c11[0] + 0.9, c11[1]); via(*v11, 'GND'); tr([c11, v11], 0.2, 1, 'GND')
# crystal: a ground guard between XIN and XOUT under the crystal, joining its two ground pads, and one via
yg = sorted(((q['x'], q['y']) for q in g['pads'] if q['ref'] == 'Y1' and q['net'] == 'GND'), key=lambda t: t[1])
(tlx, tly), (brx, bry) = yg[0], yg[1]
ym = (tly + bry) / 2
tr([(brx, bry), (brx, ym), (tlx, ym), (tlx, tly)], 0.2, 1, 'GND')
gy = (tlx - 1.45, tly); via(*gy, 'GND'); tr([(tlx, tly), gy], 0.2, 1, 'GND')
c13 = gpad('C13'); tr([c13, (gy[0], c13[1]), gy], 0.2, 1, 'GND') if abs(c13[0] - gy[0]) > 0.3 else tr([c13, gy], 0.2, 1, 'GND')
json.dump({'tracks': T, 'vias': V}, open(sys.argv[2], 'w'))
print('centre', cx, cy, 'tracks', len(T), 'vias', len(V), 'left', len(left), 'right', len(right))
