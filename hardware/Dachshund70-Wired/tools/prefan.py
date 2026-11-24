# Fixed pre-routes around the RP2350B (U1, QFN-80, on the back):
#  - staircase fan-outs of the left (matrix) and right (screen) signal pins to staggered via columns (B.Cu)
#  - an inner +3V3 ring in three arcs and a +1V1 arch inside the pad ring, joined to the pins by short spokes,
#    with the +3V3 arcs tied together on F.Cu under the chip
#  - PGND (pin 62) into the exposed pad, a GND via in the exposed pad, VREG_LX to L1, VREG_FB to a via
# usage: prefan.py geom.json pre.json
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

def stair(pins, side, xv0, xv1, step=0.35, pitch=0.8, first=1.1):
    pins = sorted(pins, key=lambda p: p['y']); N = len(pins); mid = (N - 1) / 2
    yc = sum(p['y'] for p in pins) / N
    xpad = pins[0]['x']
    for k, p in enumerate(pins):
        yp = yc + pitch * (k - mid)
        rank = k if k <= mid else N - 1 - k
        xk = xpad + side * (first + step * rank)
        xv = xv0 if k % 2 == 0 else xv1
        tr([(p['x'], p['y']), (xk, p['y']), (xk, yp), (xv, yp)], 0.15, 1, p['net'])
        via(xv, yp, p['net'])

left = [p for p in U.values() if p['x'] < cx - 4 and sig(p)]
right = [p for p in U.values() if p['x'] > cx + 4 and sig(p) and p['net'].startswith('/DISP')]
stair(left, -1, 305.0, 304.2)
stair(right, +1, 322.2, 323.0)

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
tr([(xl, P(5)['y']), (xl, yb), (P(64)['x'], yb)], W3, 1, '+3V3')
for n in (15, 5):  tr([(P(n)['x'], P(n)['y']), (xl, P(n)['y'])], W3, 1, '+3V3')
for n in (24, 29): tr([(P(n)['x'], P(n)['y']), (P(n)['x'], yt)], W3, 1, '+3V3')
for n in (41, 50): tr([(P(n)['x'], P(n)['y']), (xr, P(n)['y'])], W3, 1, '+3V3')
for n in (76, 69, 68, 64): tr([(P(n)['x'], P(n)['y']), (P(n)['x'], yb)], W3, 1, '+3V3')
# +1V1 arch over the exposed pad: pins 10 (left), 32 (top), 51 (right)
a, b = cx - R1, cx + R1; yt1 = cy - R1
tr([(P(10)['x'], P(10)['y']), (a, P(10)['y']), (a, yt1), (b, yt1), (b, P(51)['y']), (P(51)['x'], P(51)['y'])], 0.15, 1, '+1V1')
tr([(P(32)['x'], P(32)['y']), (P(32)['x'], yt1)], 0.15, 1, '+1V1')
via(b, cy + 0.4, '+1V1'); tr([(b, P(51)['y']), (b, cy + 0.4)], 0.15, 1, '+1V1')
# +3V3 arcs joined on F.Cu under the chip
vTL, vBL, vTR = (xl, yt), (xl, yb), (xr, (P(41)['y'] + P(50)['y']) / 2)
for v in (vTL, vBL, vTR): via(*v, '+3V3')
tr([vBL, vTL, (xr, yt), vTR], 0.3, 0, '+3V3')
# GND: PGND into the exposed pad, one via in the pad
p62 = P(62)
tr([(p62['x'], p62['y']), (p62['x'], yb - 0.35), (cx + 1.5, cy + 1.3)], 0.2, 1, 'GND')
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
gv1 = (321.5, 97.5); via(*gv1, 'GND')
tr([pc('C27', [q['num'] for q in g['pads'] if q['ref'] == 'C27' and q['net'] == 'GND'][0]), gv1], 0.2, 1, 'GND')
tr([pc('C10', '2'), gv1], 0.2, 1, 'GND')
gv2 = (322.7, 94.9); via(*gv2, 'GND')
tr([pc('C4', '2'), pc('C5', '2'), gv2], 0.2, 1, 'GND')
gv3 = (321.3, 102.4); via(*gv3, 'GND')
tr([pc('C7', '2'), gv3], 0.2, 1, 'GND'); tr([pc('C8', '2'), gv3], 0.2, 1, 'GND')
c9 = pc('C9', '2'); gv4 = (c9[0], c9[1] + 0.95); via(*gv4, 'GND'); tr([c9, gv4], 0.2, 1, 'GND')
j3, j5 = pc('J4', '3'), pc('J4', '5')
tr([j3, (321.0, j3[1]), (321.0, 114.6), (322.0, 113.9)], 0.2, 1, 'GND'); tr([j5, (321.0, j5[1]), (321.0, j3[1])], 0.2, 1, 'GND')
j14 = pc('J1', '4')
# VREG_AVDD: pin 61 to R11 and C27
p61 = P(61); r = pc('R11', '2'); c27 = pc('C27', '1')
tr([(p61['x'], p61['y']), (p61['x'], 96.65), (r[0], 96.65), r], 0.2, 1, '/VREG_AVDD'); tr([(c27[0], 96.65), c27], 0.2, 1, '/VREG_AVDD')
tr([j14, (322.6, j14[1]), (322.6, 109.4), (324.2, 110.0)], 0.2, 1, 'GND')

# crystal grounds: one via under each side
y4, y2 = pc('Y1', '4'), pc('Y1', '2')
via(y4[0], y4[1] + 1.1, 'GND'); tr([y4, (y4[0], y4[1] + 1.1)], 0.2, 1, 'GND')
via(y2[0], y2[1] - 1.25, 'GND'); tr([y2, (y2[0], y2[1] - 1.25)], 0.2, 1, 'GND'); tr([pc('C14', '2'), y2], 0.2, 1, 'GND')
c13 = pc('C13', '2'); via(c13[0], c13[1] - 1.0, 'GND'); tr([c13, (c13[0], c13[1] - 1.0)], 0.2, 1, 'GND')
json.dump({'tracks': T, 'vias': V}, open(sys.argv[2], 'w'))
print('centre', cx, cy, 'tracks', len(T), 'vias', len(V), 'left', len(left), 'right', len(right))
