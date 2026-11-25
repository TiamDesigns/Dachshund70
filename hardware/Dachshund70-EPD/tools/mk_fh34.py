# Writes KiCad footprints for Hirose FH34SRJ-nS-0.5SH (dual-contact 0.5 mm FPC, 1 mm high), from the EasyEDA/LCSC
# land patterns of C324726 (24P) and C224194 (6P): signal pads at y 0, pin 1 at +x, fixing tabs 2.5 mm toward the
# FPC entry (+y), body from y -0.8 to +3.0.
import uuid, os, sys
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
def U(): return str(uuid.uuid4())
def fp(n, padw, lcsc):
    name = f'Hirose_FH34SRJ-{n}S-0.5SH_1x{n:02d}-1MP_P0.50mm_Horizontal'
    half = (n - 1) * 0.25; tab = half + 1.0
    bx = tab + 0.25; L = []
    L.append(f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "dachshund70")\n\t(layer "F.Cu")')
    L.append(f'\t(descr "Hirose FH34SRJ-{n}S-0.5SH(50), {n} contacts, 0.5 mm pitch, dual contact (top and bottom), 1 mm high, back flip lock; land pattern from LCSC {lcsc} (EasyEDA). FPC enters from +y.")')
    L.append('\t(tags "connector Hirose FH34SRJ FPC dual contact")\n\t(attr smd)')
    for ref, y, txt in (('Reference', -2.2, 'REF**'), ('Value', 4.6, name)):
        L.append(f'\t(property "{ref}" "{txt}"\n\t\t(at 0 {y} 0)\n\t\t(layer "{"F.SilkS" if ref == "Reference" else "F.Fab"}")\n\t\t(uuid "{U()}")\n\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)')
    for i in range(1, n + 1):
        x = half - (i - 1) * 0.5
        L.append(f'\t(pad "{i}" smd rect\n\t\t(at {x:.3f} 0)\n\t\t(size {padw} 1.0)\n\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t\t(uuid "{U()}")\n\t)')
    for x in (-tab, tab):
        L.append(f'\t(pad "MP" smd rect\n\t\t(at {x:.3f} 2.5)\n\t\t(size 0.6 1.0)\n\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t\t(uuid "{U()}")\n\t)')
    def line(x1, y1, x2, y2, layer, w):
        L.append(f'\t(fp_line\n\t\t(start {x1:.3f} {y1:.3f})\n\t\t(end {x2:.3f} {y2:.3f})\n\t\t(stroke (width {w}) (type solid))\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)')
    # body (fab)
    for a, b in (((-bx, -0.8), (bx, -0.8)), ((bx, -0.8), (bx, 3.0)), ((bx, 3.0), (-bx, 3.0)), ((-bx, 3.0), (-bx, -0.8))):
        line(*a, *b, 'F.Fab', 0.1)
    # courtyard
    cx, cy0, cy1 = bx + 0.25, -0.8 - 0.25, 3.0 + 0.25
    for a, b in (((-cx, cy0), (cx, cy0)), ((cx, cy0), (cx, cy1)), ((cx, cy1), (-cx, cy1)), ((-cx, cy1), (-cx, cy0))):
        line(*a, *b, 'F.CrtYd', 0.05)
    # silk: sides between pad row and tabs, and a pin-1 mark beside pin 1
    for s in (-1, 1):
        line(s * (bx + 0.1), 0.4, s * (bx + 0.1), 1.8, 'F.SilkS', 0.12)
    line(half + 0.1, -0.9, half + 0.4, -0.9, 'F.SilkS', 0.12)
    L.append('\t(embedded_fonts no)\n)')
    open(os.path.join(out, name + '.kicad_mod'), 'w', encoding='utf8').write('\n'.join(L) + '\n')
    print(name)
fp(24, 0.25, 'C324726')
fp(6, 0.3, 'C224194')
