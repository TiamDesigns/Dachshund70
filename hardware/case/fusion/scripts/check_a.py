"""Clash check: every board part, the plate, both keycap sets (at rest and pressed), the battery and the screen
against the case parts, by intersection volume. Run it in Fusion (or through the Fusion MCP) on the open design:
run_checks(log) writes one line per group, with the hits (part, case part, mm3) above the threshold.

Pressed = every cap moved 4.0 mm along the plate's normal (full MX travel). Screws sit in tapped holes whose
drills are smaller than the thread, so screws are only checked against the boards, plate and caps.
"""
import adsk.core, adsk.fusion, math, time

TBM = adsk.fusion.TemporaryBRepManager.get()
INTER = adsk.fusion.BooleanTypes.IntersectionBooleanType
TILT = 4.0
S, C = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
TRAVEL = 4.0
CASE = ['Top shell', 'Bottom shell', 'Accent ring', 'Encoder cover', 'HW Wheel', 'HW LED guide', 'HW Accent weight bar',
        'HW Power slider cap'] + ['Gasket retainer %d' % i for i in range(1, 7)]


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


def pressed(b):
    t = TBM.copy(b)
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(0, TRAVEL * S / 10, -TRAVEL * C / 10)    # along the plate's normal, down
    TBM.transform(t, m)
    return t


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
