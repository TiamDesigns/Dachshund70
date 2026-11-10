"""Clash check: every board part, the plate, both keycap sets (at rest and pressed), the battery and the screen
against the case parts, by intersection volume. Run it in Fusion (or through the Fusion MCP) on the open design:
run_checks(log) writes one line per group, with the hits (part, case part, mm3) above the threshold.

Pressed = every cap moved 4.0 mm along the plate's normal (full MX travel). Screws sit in tapped holes whose
drills are smaller than the thread, so screws are only checked against the boards, plate and caps.

Floating: the plate, the mainboard (it hangs from the switches) and the keycaps sit on the gasket socks, so they are
also checked moved FLOAT (1.0 mm) up and down along the plate's normal: at rest + FLOAT, and pressed with - FLOAT.
plate_clearance(log) reports the smallest gap from each case part and screw to the plate in that range.
"""
import adsk.core, adsk.fusion, math, time

TBM = adsk.fusion.TemporaryBRepManager.get()
INTER = adsk.fusion.BooleanTypes.IntersectionBooleanType
TILT = 4.0
S, C = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
TRAVEL = 4.0
FLOAT = 1.0
CASE = ['Top shell', 'Bottom shell', 'Accent ring', 'Encoder cover', 'HW Wheel', 'HW LED guide', 'HW Accent weight bar',
        'HW Power slider button'] + ['Gasket retainer %d' % i for i in range(1, 7)]


def bb(b):
    x = b.boundingBox
    return [v * 10 for v in (x.minPoint.x, x.minPoint.y, x.minPoint.z, x.maxPoint.x, x.maxPoint.y, x.maxPoint.z)]


def overlap_bb(a, b, m=0.0):
    return all(a[i] <= b[i + 3] + m and b[i] <= a[i + 3] + m for i in range(3))


def inter_vol(a, b):
    """Volume in mm3 of the intersection of two bodies (a copy of an occurrence's body is already in world space)."""
    try:
        ca, cb = TBM.copy(a), TBM.copy(b)
        TBM.booleanOperation(ca, cb, INTER)
        v = ca.volume * 1000.0
        return v if v > 0 else 0.0
    except Exception:
        return 0.0


def pressed(b, d=TRAVEL):
    t = TBM.copy(b)
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0, d * S / 10, -d * C / 10)    # along the plate's normal, down
    TBM.transform(t, m)
    return t


def floated(b, d):
    """moved d mm up (d > 0) or down along the plate's normal"""
    return pressed(b, -d)


def occ_bodies(o):
    out = []

    def walk(x):
        for b in x.bRepBodies:
            out.append((x.name, b))
        for ch in x.childOccurrences:
            walk(ch)
    walk(o)
    return out


def run_checks(log, thr=0.0001):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    root = des.rootComponent
    case = {n: root.bRepBodies.itemByName(n) for n in CASE if root.bRepBodies.itemByName(n)}
    caseb = {n: bb(b) for n, b in case.items()}
    t0 = time.time()
    total = [0]

    def test(label, items, shells=None):
        hit = []
        for nm, b in items:
            bx = bb(b)
            for sn in (shells or case):
                if sn in case and overlap_bb(bx, caseb[sn]):
                    v = inter_vol(b, case[sn])
                    if v > thr:
                        hit.append((nm, sn, round(v, 4)))
        total[0] += len(hit)
        log.write('%s: %d bodies, %d hits %s (%.0fs)\n' % (label, len(items), len(hit), hit[:12], time.time() - t0))
        log.flush()

    def occ(prefix):
        return [o for o in root.occurrences if o.name.split(' ')[0].split(':')[0].endswith(prefix)]

    asm = occ('-Assembly')[0]
    asm_items = occ_bodies(asm)
    plate = [(n, b) for o in occ('-Plate') for n, b in occ_bodies(o)] + [(n, b) for n, b in asm_items if 'Plate_PCB' in n]
    test('plate', plate)
    test('mainboard and its parts', asm_items)
    for d in (FLOAT, -FLOAT):
        test('plate %+.1f' % d, [(n, floated(b, d)) for n, b in plate])
        test('mainboard and its parts %+.1f' % d, [(n, floated(b, d)) for n, b in asm_items])
    for key in ('-Encoder', '-USB'):
        for o in occ(key):
            test(o.name, occ_bodies(o))
    for o in root.occurrences:
        if o.name.startswith(('Battery', 'E-paper')):
            test(o.name, occ_bodies(o))
    for nm in ('HW Screen FPC',):
        b = root.bRepBodies.itemByName(nm)
        if b:
            test(nm, [(nm, b)])
    # case parts against each other (touching faces give 0)
    pairs = []
    names = list(case)
    for i, a in enumerate(names):
        for b2 in names[i + 1:]:
            if overlap_bb(caseb[a], caseb[b2]):
                v = inter_vol(case[a], case[b2])
                if v > thr:
                    pairs.append((a, b2, round(v, 4)))
    total[0] += len(pairs)
    log.write('case parts vs each other: %d hits %s\n' % (len(pairs), pairs))
    # screws: against the boards, plate and caps only
    screws = [(b.name, b) for b in root.bRepBodies if b.name.startswith('HW M')]
    boards = asm_items + plate + [x for k in ('-Encoder', '-USB') for o in occ(k) for x in occ_bodies(o)]
    sh = []
    for sn, s in screws:
        for n, b in boards:
            if overlap_bb(bb(s), bb(b)):
                v = inter_vol(s, b)
                if v > thr:
                    sh.append((sn, n, round(v, 4)))
    total[0] += len(sh)
    log.write('screws vs boards and plate: %d screws, %d hits %s\n' % (len(screws), len(sh), sh[:12]))
    # keycaps: every set, at rest and pressed
    caps = []
    for o in root.occurrences:
        if o.name.startswith(('Keycaps', 'Spacebar')):
            caps += [(o.name + '/' + n, b) for n, b in occ_bodies(o) if not n.startswith(('SW_', 'Stabilizer'))]
    test('keycaps at rest', caps)
    pc = [(n, pressed(b)) for n, b in caps]
    test('keycaps pressed 4.0', pc)
    test('keycaps at rest, plate +%.1f' % FLOAT, [(n, floated(b, FLOAT)) for n, b in caps])
    test('keycaps pressed 4.0, plate -%.1f' % FLOAT, [(n, pressed(b, TRAVEL + FLOAT)) for n, b in caps])
    sc = [(sn, s) for sn, s in screws]
    ph = []
    for n, b in pc:
        for sn, s in sc:
            if overlap_bb(bb(b), bb(s)):
                v = inter_vol(b, s)
                if v > thr:
                    ph.append((n, sn, round(v, 4)))
    total[0] += len(ph)
    log.write('pressed keycaps vs screws: %d hits %s\n' % (len(ph), ph[:12]))
    log.write('TOTAL hits %d (%.0fs)\n' % (total[0], time.time() - t0))
    return total[0]


def battery_vs_board(log):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    root = des.rootComponent
    batt = [o for o in root.occurrences if o.name.startswith('Battery')][0]
    asm = [o for o in root.occurrences if o.name.split(' ')[0].endswith('-Assembly')][0]
    bb_ = [b for b in batt.bRepBodies]
    hits = {}
    for n, b in occ_bodies(asm):
        x = bb(b)
        for cell in bb_:
            if overlap_bb(x, bb(cell)):
                v = inter_vol(b, cell)
                if v > 0.0001:
                    hits.setdefault(n, []).append(round(v, 2))
    log.write('battery vs board parts: %s' % hits + chr(10))


def plate_clearance(log, parts=None, shift=FLOAT, steps=8, margin=3.0):
    """Smallest gap (mm) from each named part to the plate anywhere in its +-shift float. The plate is clipped to each
    part's box (+ margin) first and swept in 2 * steps positions, so this stays quick."""
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    root = des.rootComponent
    plate = [b for o in root.occurrences if o.name.split(' ')[0].split(':')[0].endswith('-Plate') for _, b in occ_bodies(o)][0]
    names = parts or ['Encoder cover', 'HW M2x8 CSK screw cover front', 'HW M2x8 CSK screw cover back',
                      'HW M2x5 SHCS module 1', 'HW M2x5 SHCS module 2', 'HW Wheel']
    mm = adsk.core.Application.get().measureManager
    out = []
    for n in names:
        b = root.bRepBodies.itemByName(n)
        if b is None:
            continue
        x = bb(b)
        lo = [v - margin for v in x[:3]]
        hi = [v + margin for v in x[3:]]
        clip = TBM.createBox(adsk.core.OrientedBoundingBox3D.create(
            adsk.core.Point3D.create(*[(a + c) / 20 for a, c in zip(lo, hi)]), adsk.core.Vector3D.create(1, 0, 0),
            adsk.core.Vector3D.create(0, 1, 0), *[(c - a) / 10 for a, c in zip(lo, hi)]))
        piece = TBM.copy(plate)
        TBM.booleanOperation(piece, clip, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        if piece.volume <= 0:
            continue
        swept = TBM.copy(piece)
        for k in range(1, steps + 1):
            for sg in (1, -1):
                TBM.booleanOperation(swept, floated(piece, sg * shift * k / steps), adsk.fusion.BooleanTypes.UnionBooleanType)
        out.append((n, round(mm.measureMinimumDistance(b, swept).value * 10, 2)))
    out.sort(key=lambda t: t[1])
    log.write('gap to the plate swept +-%.1f: %s\n' % (shift, out))
    return out
