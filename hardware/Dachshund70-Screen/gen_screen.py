"""Generate the Dachshund70 screen board: schematic, then the routed board.

The screen board (rev 3.0) carries a 2.7" Sharp memory LCD (LS027B7DH01,
400 x 240): the panel's 5 V supply (a TPS61222 boost from the mainboard's
3V3), its 10-pin FPC socket, the five status LEDs (layer, battery gauge) and
a 12-pin FFC socket for the cable to the mainboard's J4.

Run with KiCad 10's own Python (it ships the pcbnew module), from the repo root:

    "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70-Screen/gen_screen.py

or in the kicad/kicad:10.0 Docker image. It overwrites the .kicad_sch and the
whole .kicad_pcb: placement, the routing in screen_routes.py (ROUTES and
VIAS) and the filled ground pours. It reads the mainboard's J4 to set J2's
place and pin order, so rerun it after moving J4. Check with
`kicad-cli pcb drc --schematic-parity --severity-all Dachshund70-Screen.kicad_pcb`.

Coordinates are the mainboard's (KiCad mm, y down): the board is held by the
case under the panel and over the mainboard's right-hand edge, so its STEP
drops into the case model at the same x and y. Every part is on the bottom
side; the LEDs shine up through their cut-outs.
"""

import os
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "Dachshund70-Screen"
SYMDIR = os.environ.get("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")
FPDIR = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints")

# ---------------------------------------------------------------- the circuit
# Sharp's LS027B7DH01 runs from 5 V (VDD and VDDA, 4.8 to 5.5 V) and takes 3.3 V logic (VIH from 2.7 V).
# U1 (TPS61222, fixed 5 V) boosts the mainboard's 3V3; FB goes straight to VOUT, as the datasheet says for the
# fixed versions. The panel draws tens of microamps, so U1's 5.5 uA quiescent current is most of the cost.
# U1's EN comes from J4-8 (the e-paper overlays' BUSY), pulled up by R1, so the 5 V is on unless the firmware
# drives that pin low. EXTMODE is tied high: VCOM is inverted by the EXTCOMIN pulse, not over SPI.
# C3, C4 and C5 are the capacitors Sharp asks for (VDD >= 1 uF, VDDA >= 0.1 uF, DISP 0.1 uF), close to J1.

# Panel FPC pin -> net (Sharp LS027B7DH01 specification, "Input/output terminals")
PANEL = {
    1: "SCLK", 2: "SI", 3: "SCS", 4: "EXTCOMIN", 5: "DISP", 6: "+5V", 7: "+5V", 8: "+5V", 9: "GND",
    10: "GND",
}

# The mainboard's J4 (rev 1.3): a 12-pin FH12 on its top side at the right-hand edge, mouth facing +x. Its
# net names are the e-paper ones (DIN, CLK, CS, DC, RST, BUSY); here they carry the Sharp's SI, SCLK, SCS,
# EXTCOMIN, DISP and the boost enable, plus the LED chain (data out of the Caps Lock LED, and its supply).
MAINBOARD_J4 = {1: "LED_VDD", 2: "LED_VDD", 3: "GND", 4: "LED_DIN", 5: "GND", 6: "DISP", 7: "EXTCOMIN", 8: "SCS",
                9: "SI", 10: "SCLK", 11: "VLCD_EN", 12: "+3V3"}
# J2 sits 6 mm right of J4 (the FFC's loop is longer by that), so there is room between J1 and J2 for the
# signals, which keep the same top-to-bottom order in both sockets.
J2_DX = 6.0
MAINBOARD = os.path.join(HERE, "..", "Dachshund70", "Dachshund70.kicad_pcb")
POWER = ("+3V3", "+5V", "GND")

# J1's pads run the other way from the panel's pins: the tail folds back under the glass, so (looking down on
# the board) panel pin 1 lands at the top, where J1's pad 10 is. J1 pin n = panel pin 11 - n (see README).
SOCKET = {n: PANEL[11 - n] for n in range(1, 11)}

# ref: (lib_id, value, footprint, mpn, lcsc, {pin: net}). J2's pins are filled in by cable_map().
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
LED_FP = "Dachshund70:LED_SK6812MINI-E_3.2x2.8mm_P1.5mm_ReverseMount_Cutout3.4"
LED_NAMES = ("Layer", "Battery 1", "Battery 2", "Battery 3", "Battery 4")
PARTS = {
    "J1": ("Connector_Generic_MountingPin:Conn_01x10_MountingPin", "Memory LCD (FPC 10P 0.5 mm)",
           "Connector_FFC-FPC:Hirose_FH12-10S-0.5SH_1x10-1MP_P0.50mm_Horizontal",
           "Hirose FH12-10S-0.5SH(55)", "", dict(SOCKET, MP="GND")),
    "J2": ("Connector_Generic_MountingPin:Conn_01x12_MountingPin", "Mainboard J4 (FFC 12P 0.5 mm, same side)",
           "Connector_FFC-FPC:Hirose_FH12-12S-0.5SH_1x12-1MP_P0.50mm_Horizontal",
           "Hirose FH12-12S-0.5SH(55)", "", {}),
    "U1": ("Regulator_Switching:TPS61222DCK", "TPS61222DCK", "Package_TO_SOT_SMD:SOT-363_SC-70-6",
           "TI TPS61222DCKR (5 V boost)", "",
           {1: "+3V3", 2: "+5V", 3: "GND", 4: "+5V", 5: "SW", 6: "VLCD_EN"}),
    "L1": ("Device:L", "4.7uH", "Inductor_SMD:L_Changjiang_FNR3015S",
           "Changjiang FNR3015S4R7MT (4.7 uH, 3 x 3 x 1.5 mm)", "", {1: "+3V3", 2: "SW"}),
    "R1": ("Device:R", "100k", "Resistor_SMD:R_0402_1005Metric", "UNI-ROYAL 0402WGF1003TCE", "C25741",
           {1: "+3V3", 2: "VLCD_EN"}),
    "C1": ("Device:C", "10uF", C0603, "Samsung CL10A106KP8NNNC (10 uF, 10 V, X5R)", "C19702",
           {1: "+3V3", 2: "GND"}),
    "C2": ("Device:C", "10uF", C0603, "Samsung CL10A106KP8NNNC (10 uF, 10 V, X5R)", "C19702",
           {1: "+5V", 2: "GND"}),
    "C3": ("Device:C", "1uF", C0402, "Samsung CL05A105KA5NQNC (1 uF, 25 V, X5R)", "C52923", {1: "+5V", 2: "GND"}),
    "C4": ("Device:C", "100nF", C0402, "Samsung CL05B104KO5NNNC", "C1525", {1: "+5V", 2: "GND"}),
    "C5": ("Device:C", "100nF", C0402, "Samsung CL05B104KO5NNNC", "C1525", {1: "DISP", 2: "GND"}),
}
# The five status LEDs (reverse-mount SK6812MINI-E, the mainboard's footprint), a chain fed from the
# mainboard's Caps Lock LED: D1 (layer), then D2-D5 (battery 25/50/75/100 %). Each has its own 100 nF.
for i, name in enumerate(LED_NAMES):
    din = "LED_DIN" if i == 0 else "LED_D%d" % i
    dout = None if i == 4 else "LED_D%d" % (i + 1)
    PARTS["D%d" % (i + 1)] = ("LED:SK6812MINI-E", "SK6812MINI-E (%s)" % name, LED_FP, "OPSCO SK6812MINI-E",
                             "C5149201", {1: "GND", 2: din, 3: "LED_VDD", 4: dout})
    PARTS["C%d" % (i + 6)] = ("Device:C", "100nF", C0402, "Samsung CL05B104KO5NNNC", "C1525",
                             {1: "LED_VDD", 2: "GND"})

# Board placement: x, y, rotation, side ("B" = bottom). Mainboard coordinates.
# The board hangs from the case under the glass (KiCad x 308 to 351, y 63 to 126) and its LEDs: it does not
# touch the mainboard, which floats with the plate. Its top edge stays below the radio's antenna (the
# mainboard's U1, KiCad x 322-326, y 74-84).
BOARD_OUTLINE = (309.0, 88.0, 349.0, 135.0)     # x0, y0, x1, y1
BOARD_CORNER_R = 1.0
THICKNESS = 0.8
LED_X0, LED_PITCH, LED_Y = 314.559, 7.5, 130.5   # the case's light holes (unchanged from mainboard rev 1.2)
PLACE = {
    # The panel's FPC leaves its long edge on the left (in portrait) and folds back under the glass into J1,
    # whose mouth faces -x (see README, "Panel tail").
    "J1": (314.6, 110.6, None, "B"),
    "J2": (None, None, None, "B"),                        # straight over the mainboard's J4, mouth facing +x
    # the boost, above the sockets
    "U1": (330.5, 96.0, 180, "B"),
    "L1": (326.85, 96.0, ("2", 1, 0), "B"),
    "C1": (333.3, 95.4, ("1", 0, -1), "B"),
    "C2": (328.9, 98.6, ("1", 1, 0), "B"),
    "R1": (334.5, 99.0, ("1", 1, 0), "B"),
    # the panel's own capacitors, beside J1
    "C5": (318.6, 104.6, ("1", 0, -1), "B"),
    "C3": (317.6, 117.2, ("1", 0, -1), "B"),
    "C4": (319.1, 117.2, ("1", 0, -1), "B"),
}
for i in range(5):
    x = LED_X0 + LED_PITCH * i
    PLACE["D%d" % (i + 1)] = (x, LED_Y, 90, "B")
    PLACE["C%d" % (i + 6)] = (x, 125.9, 180, "B")


def cable_map():
    """J2 pin -> net. J2 sits straight over the mainboard's J4, both mouths facing +x, and a same-side FFC
    loops between them (C shape), so each conductor keeps its y: J2's pad at a given y gets the net of J4's
    pad at that y."""
    import pcbnew
    main = pcbnew.LoadBoard(MAINBOARD)
    j4 = main.FindFootprintByReference("J4")
    j4pads = {p.GetNumber(): p.GetPosition() for p in j4.Pads() if p.GetNumber().isdigit()}
    tmp = pcbnew.BOARD()
    fp = _load_fp(PARTS["J2"][2])
    tmp.Add(fp)
    _place_mouth(fp, pcbnew.ToMM(j4.GetPosition().x) + J2_DX, pcbnew.ToMM(j4.GetPosition().y), "B", +1)
    out = {}
    for p in fp.Pads():
        if not p.GetNumber().isdigit():
            continue
        y = p.GetPosition().y
        n4 = min(j4pads, key=lambda k: abs(j4pads[k].y - y))
        assert abs(j4pads[n4].y - y) < 1000, "J2 and J4 pads don't line up"
        out[int(p.GetNumber())] = MAINBOARD_J4[int(n4)]
    PARTS["J2"][5].update(out)
    PARTS["J2"][5]["MP"] = "GND"
    PLACE["J2"] = (pcbnew.ToMM(j4.GetPosition().x) + J2_DX, pcbnew.ToMM(j4.GetPosition().y), None, "B")
    return out


def _load_fp(fpid):
    import pcbnew
    lib, name = fpid.split(":")
    path = os.path.join(HERE, "..", "Dachshund70", "lib", lib + ".pretty") if lib == "Dachshund70" \
        else os.path.join(FPDIR, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    fp.SetFPIDAsString(fpid)
    return fp


def _place_mouth(fp, x, y, side, sign):
    """FH12 with its mouth (the actuator, +y in the library footprint) toward sign*x: pads on the other side."""
    import pcbnew
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    if side == "B" and not fp.IsFlipped():
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    for r in (90, 270):
        fp.SetOrientationDegrees(r)
        ps = [p for p in fp.Pads() if p.GetNumber() == "1"]
        if (pcbnew.ToMM(ps[0].GetPosition().x) - x) * sign < 0:
            return
    raise SystemExit("no orientation")


# ---------------------------------------------------------------- routing
# Two layers, every part on B.Cu; F.Cu (under the panel) is mostly ground pour. Routed with Freerouting
# (2026-11-17) from the placement above, then copied here so the board regenerates: (net, layer, width, [(x, y), ...]).
from screen_routes import ROUTES, VIAS  # noqa: E402

sys.path.insert(0, os.path.join(HERE, ".."))


# ---------------------------------------------------------------- s-expressions
def parse(text):
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            v = stack.pop()
            stack[-1].append(v)
        else:
            stack[-1].append(t)
    return stack[0][0]


def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(i, list) for i in x):
        return "\t" * ind + "(" + " ".join(x) + ")"
    head = []
    rest = []
    for i in x:
        (rest if (isinstance(i, list) or rest) else head).append(i)
    s = "\t" * ind + "(" + " ".join(head)
    for i in rest:
        s += "\n" + (dump(i, ind + 1) if isinstance(i, list) else "\t" * (ind + 1) + i)
    return s + "\n" + "\t" * ind + ")"


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def uq(s):
    return s[1:-1] if s.startswith('"') else s


_libs = {}


def lib_symbol(lib_id):
    """The symbol from KiCad's library, flattened (no 'extends') and renamed lib:name."""
    lib, name = lib_id.split(":")
    if lib not in _libs:
        tree = parse(open(os.path.join(SYMDIR, lib + ".kicad_sym"), encoding="utf-8").read())
        _libs[lib] = {uq(s[1]): s for s in tree if isinstance(s, list) and s[0] == "symbol"}
    syms = _libs[lib]
    s = [list(i) if isinstance(i, list) else i for i in syms[name]]
    ext = [i for i in s if isinstance(i, list) and i[0] == "extends"]
    if ext:
        parent = syms[uq(ext[0][1])]
        pname = uq(parent[1])
        props = {uq(i[1]): i for i in s if isinstance(i, list) and i[0] == "property"}
        out = ["symbol", q(name)]
        for i in parent[2:]:
            if isinstance(i, list) and i[0] == "property" and uq(i[1]) in props:
                out.append(props.pop(uq(i[1])))
            elif isinstance(i, list) and i[0] == "symbol":
                sub = list(i)
                sub[1] = q(uq(sub[1]).replace(pname, name, 1))
                out.append(sub)
            else:
                out.append(i)
        # any child-only property goes before the unit sub-symbols
        idx = max(k for k, i in enumerate(out) if isinstance(i, list) and i[0] == "property") + 1
        for p in props.values():
            out.insert(idx, p)
            idx += 1
        s = out
    s[1] = q(lib_id)
    return s


def pins_of(sym):
    """{number: (x, y, angle)} of the symbol's pins, symbol coordinates (y up)."""
    out = {}

    def walk(n):
        for i in n:
            if isinstance(i, list):
                if i[0] == "pin":
                    at = next(j for j in i if isinstance(j, list) and j[0] == "at")
                    num = next(j for j in i if isinstance(j, list) and j[0] == "number")
                    out[uq(num[1])] = (float(at[1]), float(at[2]), int(float(at[3])))
                else:
                    walk(i)
    walk(sym)
    return out


# ---------------------------------------------------------------- schematic
def U():
    return str(uuid.uuid4())


def prop(name, value, x, y, hide=False, ang=0):
    p = ["property", q(name), q(value), ["at", "%.2f" % x, "%.2f" % y, str(ang)]]
    if hide:
        p.append(["hide", "yes"])
    p.append(["effects", ["font", ["size", "1.27", "1.27"]]])
    return p


def build_schematic(root_uuid, sheet_xy):
    items = []
    used_libs = {}
    pwr_n = [0]
    sym_uuids = {}

    def instance(ref, lib_id, x, y, value, fp="", mpn="", lcsc="", hide_ref=False, rot=0):
        used_libs[lib_id] = lib_symbol(lib_id)
        uid = U()
        sym = ["symbol", ["lib_id", q(lib_id)], ["at", "%.2f" % x, "%.2f" % y, str(rot)], ["unit", "1"],
               ["exclude_from_sim", "no"], ["in_bom", "no" if ref.startswith("#") else "yes"],
               ["on_board", "no" if ref.startswith("#") else "yes"], ["dnp", "no"], ["uuid", q(uid)],
               prop("Reference", ref, x + 2.54, y - 1.27, hide=hide_ref),
               prop("Value", value, x + 2.54, y + 1.27),
               prop("Footprint", fp, x, y, hide=True),
               prop("Datasheet", "", x, y, hide=True)]
        if mpn:
            sym.append(prop("MPN", mpn, x, y, hide=True))
        if lcsc or (mpn and not ref.startswith("#")):
            sym.append(prop("LCSC", lcsc, x, y, hide=True))
        for num in pins_of(used_libs[lib_id]):
            sym.append(["pin", q(num), ["uuid", q(U())]])
        sym.append(["instances", ["project", q(NAME), ["path", q("/" + root_uuid), ["reference", q(ref)], ["unit", "1"]]]])
        items.append(sym)
        sym_uuids[ref] = uid
        return used_libs[lib_id]

    def attach(net, px, py, ang):
        """Hang a power symbol, a label or a no-connect on the pin end at (px, py)."""
        if net is None:
            items.append(["no_connect", ["at", "%.2f" % px, "%.2f" % py], ["uuid", q(U())]])
            return
        if net in POWER:
            pwr_n[0] += 1
            # pins pointing left/right get a short wire so the symbol stands clear
            if ang in (0, 180):
                dx = -2.54 if ang == 0 else 2.54
                items.append(["wire", ["pts", ["xy", "%.2f" % px, "%.2f" % py], ["xy", "%.2f" % (px + dx), "%.2f" % py]],
                              ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
                px += dx
            instance("#PWR%03d" % pwr_n[0], "power:" + net, px, py, net, hide_ref=True)
            return
        # label: text on the far side of the pin end
        lang = {0: 180, 180: 0, 90: 270, 270: 90}[ang]
        just = "right bottom" if lang == 180 else ("left bottom" if lang == 0 else "left bottom")
        items.append(["label", q(net), ["at", "%.2f" % px, "%.2f" % py, str(lang)],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify"] + just.split()], ["uuid", q(U())]])

    for ref, (lib_id, value, fp, mpn, lcsc, nets) in PARTS.items():
        x, y = sheet_xy[ref]
        sym = instance(ref, lib_id, x, y, value, fp, mpn, lcsc)
        for num, (sx, sy, ang) in pins_of(sym).items():
            key = int(num) if num.isdigit() else num
            if key not in nets:
                raise SystemExit("%s pin %s has no net" % (ref, num))
            attach(nets[key], x + sx, y - sy, ang)

    # power flags: the 3V3 and GND come in on the cable
    for i, net in enumerate(("+3V3", "GND")):
        fx, fy = 40.64 + 12.7 * i, 30.48
        pwr_n[0] += 1
        instance("#FLG%02d" % (i + 1), "power:PWR_FLAG", fx, fy, "PWR_FLAG", hide_ref=True)
        if net == "GND":
            items.append(["wire", ["pts", ["xy", "%.2f" % fx, "%.2f" % fy], ["xy", "%.2f" % fx, "%.2f" % (fy + 2.54)]],
                          ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
            instance("#PWR%03d" % pwr_n[0], "power:GND", fx, fy + 2.54, "GND", hide_ref=True)
        else:
            items.append(["wire", ["pts", ["xy", "%.2f" % fx, "%.2f" % fy], ["xy", "%.2f" % fx, "%.2f" % (fy + 2.54)]],
                          ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
            instance("#PWR%03d" % pwr_n[0], "power:+3V3", fx, fy + 2.54, "+3V3", hide_ref=True)
            # the +3V3 symbol's pin points up, so it sits on the wire's lower end
    # LED_VDD comes in on the cable too
    fx, fy = 78.74, 30.48
    instance("#FLG04", "power:PWR_FLAG", fx, fy, "PWR_FLAG", hide_ref=True)
    items.append(["wire", ["pts", ["xy", "%.2f" % fx, "%.2f" % fy], ["xy", "%.2f" % fx, "%.2f" % (fy + 2.54)]],
                  ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
    attach("LED_VDD", fx, fy + 2.54, 90)
    # and SW: U1's L pin is a power input, fed only through L1
    fx, fy = 66.04, 30.48
    instance("#FLG03", "power:PWR_FLAG", fx, fy, "PWR_FLAG", hide_ref=True)
    items.append(["wire", ["pts", ["xy", "%.2f" % fx, "%.2f" % fy], ["xy", "%.2f" % fx, "%.2f" % (fy + 2.54)]],
                  ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
    attach("SW", fx, fy + 2.54, 90)

    notes = [
        "Dachshund70 screen board: 5 V for the Sharp LS027B7DH01 memory LCD (U1, L1, C1, C2), panel socket J1, status LEDs D1-D5.",
        "J2: 12-pin 0.5 mm FFC to the mainboard's J4 (same-side contacts, C loop): J2 pin n = J4 pin 13 - n.",
        "VLCD_EN (mainboard DISP_BUSY, P0.24) enables U1; R1 holds it high. EXTMODE high: VCOM follows the EXTCOMIN pulse.",
        "LED_DIN is the data out of the mainboard's Caps Lock LED: D1 layer, D2-D5 battery 25/50/75/100 %.",
        "C3 (VDD), C4 (VDDA) and C5 (DISP) are the capacitors from Sharp's specification, next to J1.",
        "J1 pin n = panel pin 11 - n: the panel's tail folds back under the glass.",
    ]
    for i, t in enumerate(notes):
        items.append(["text", q(t), ["exclude_from_sim", "no"], ["at", "25.4", "%.2f" % (172.72 + 3.81 * i), "0"],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left", "bottom"]], ["uuid", q(U())]])

    sch = ["kicad_sch", ["version", "20260306"], ["generator", q("eeschema")], ["generator_version", q("10.0")],
           ["uuid", q(root_uuid)], ["paper", q("A4")],
           ["title_block", ["title", q("Dachshund70 screen board")], ["date", q("2026-11-17")], ["rev", q("3.0")],
            ["comment", "1", q("2.7in Sharp memory LCD (LS027B7DH01): 5 V boost, FPC socket, 5 status LEDs, FFC to the mainboard")]],
           ["lib_symbols"] + list(used_libs.values())]
    sch += items
    sch += [["sheet_instances", ["path", q("/"), ["page", q("1")]]], ["embedded_fonts", "no"]]
    return sch, sym_uuids


SHEET_XY = {
    "J1": (63.5, 101.6), "J2": (215.9, 76.2),
    **{"D%d" % (i + 1): (63.5 + 30.48 * i, 152.4) for i in range(5)},
    **{"C%d" % (i + 6): (63.5 + 30.48 * i, 172.72) for i in range(5)},
    "U1": (139.7, 63.5), "L1": (127.0, 50.8), "R1": (114.3, 76.2),
    "C1": (101.6, 63.5), "C2": (165.1, 63.5), "C3": (101.6, 116.84), "C4": (114.3, 116.84),
    "C5": (127.0, 116.84),
}


def main():
    sch_path = os.path.join(HERE, NAME + ".kicad_sch")
    root_uuid = None
    if os.path.exists(sch_path):
        m = re.search(r'\(uuid "([^"]+)"\)', open(sch_path, encoding="utf-8").read())
        root_uuid = m.group(1) if m else None
    root_uuid = root_uuid or U()
    cable_map()
    sch, sym_uuids = build_schematic(root_uuid, SHEET_XY)
    with open(sch_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(sch) + "\n")
    print("wrote", sch_path)
    build_board(sym_uuids)


# ---------------------------------------------------------------- board
def build_board(sym_uuids):
    import pcbnew
    import gnd_vias
    pcb_path = os.path.join(HERE, NAME + ".kicad_pcb")
    b = pcbnew.BOARD()
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(pcbnew.FromMM(THICKNESS))
    b.SetCopperLayerCount(2)
    nets = {}

    def net(name):
        if name not in nets:
            n = pcbnew.NETINFO_ITEM(b, name)
            b.Add(n)
            nets[name] = n
        return nets[name]

    def place(fp, x, y, rot, side):
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        if rot is not None:
            fp.SetOrientationDegrees(rot)

    def pads_centre(fp, num):
        ps = [p for p in fp.Pads() if p.GetNumber() == num]
        return pcbnew.ToMM(ps[0].GetPosition().x), pcbnew.ToMM(ps[0].GetPosition().y)

    for ref, (lib_id, value, fpid, mpn, lcsc, pnets) in PARTS.items():
        fp = _load_fp(fpid)
        fp.SetReference(ref)
        fp.SetValue(value)
        for fname, fval in (("MPN", mpn), ("LCSC", lcsc)):
            fld = pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), fname)
            fld.SetText(fval)
            fld.SetVisible(False)
            fld.SetLayer(pcbnew.B_Fab if PLACE[ref][3] == "B" else pcbnew.F_Fab)
            fp.Add(fld)
        fp.SetPath(pcbnew.KIID_PATH("/" + sym_uuids[ref]))
        x, y, rot, side = PLACE[ref]
        b.Add(fp)
        if ref in ("J1", "J2"):
            # J1's mouth faces -x (the panel's tail comes round the board's left edge), J2's +x (the FFC's
            # loop is right of the mainboard's edge)
            _place_mouth(fp, x, y, side, -1 if ref == "J1" else +1)
        elif isinstance(rot, tuple):
            pad, dx, dy = rot
            place(fp, x, y, None, side)
            for r in (0, 90, 180, 270):
                fp.SetOrientationDegrees(r)
                px, py = pads_centre(fp, pad)
                if (px - x) * dx + (py - y) * dy > 0.1:
                    break
            else:
                raise SystemExit("no rotation puts %s pad %s toward %r" % (ref, pad, (dx, dy)))
        else:
            place(fp, x, y, rot, side)
        for p in fp.Pads():
            num = p.GetNumber()
            key = int(num) if num.isdigit() else num
            n = pnets.get(key)
            if n is None:       # the schematic's name for a pin with a no-connect flag
                n = ("unconnected-(%s-DOUT-Pad4)" % ref) if ref.startswith("D") else \
                    "unconnected-(%s-Pin_%s-Pad%s)" % (ref, num, num)
            elif n not in POWER:
                n = "/" + n     # local labels
            p.SetNet(net(n))
        fp.Reference().SetVisible(True)
        fp.Reference().SetLayer(pcbnew.B_Fab if side == "B" else pcbnew.F_Fab)

    # outline
    x0, y0, x1, y1 = BOARD_OUTLINE
    r = BOARD_CORNER_R
    def seg(ax, ay, bx, by):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ax), pcbnew.FromMM(ay)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(bx), pcbnew.FromMM(by)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.05))
        b.Add(s)
    def arc(cx, cy, sx, sy, ang):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_ARC)
        s.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(cx), pcbnew.FromMM(cy)))
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(sx), pcbnew.FromMM(sy)))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T), True)
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.05))
        b.Add(s)
    seg(x0 + r, y0, x1 - r, y0); arc(x1 - r, y0 + r, x1 - r, y0, 90)
    seg(x1, y0 + r, x1, y1 - r); arc(x1 - r, y1 - r, x1, y1 - r, 90)
    seg(x1 - r, y1, x0 + r, y1); arc(x0 + r, y1 - r, x0 + r, y1, 90)
    seg(x0, y1 - r, x0, y0 + r); arc(x0 + r, y0 + r, x0, y0 + r, 90)

    # ground pours on both sides (the top one faces the panel's back)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net("GND"))
        z.SetIsFilled(False)
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        z.SetMinThickness(pcbnew.FromMM(0.2))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)   # solid: reflowed, and the LED pads have little room
        z.SetThermalReliefGap(pcbnew.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
        ol = z.Outline()
        ol.NewOutline()
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
        b.Add(z)

    # keep-outs for tracks and vias: a 0.5 mm strip inside the outline (the board's copper-to-edge rule)
    # and 0.3 mm round each LED's light cut-out, so the router keeps to the rules
    def keepout(bx0, by0, bx1, by1, name):
        k = pcbnew.ZONE(b)
        k.SetIsRuleArea(True)
        k.SetDoNotAllowTracks(True)
        k.SetDoNotAllowVias(True)
        k.SetDoNotAllowZoneFills(False)
        k.SetDoNotAllowPads(False)
        k.SetDoNotAllowFootprints(False)
        k.SetLayerSet(pcbnew.LSET.AllCuMask())
        k.SetZoneName(name)
        kol = k.Outline()
        kol.NewOutline()
        for (px, py) in ((bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)):
            kol.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
        b.Add(k)
    e = 0.5
    keepout(x0, y0, x1, y0 + e, "edge strip")
    keepout(x0, y1 - e, x1, y1, "edge strip")
    keepout(x0, y0, x0 + e, y1, "edge strip")
    keepout(x1 - e, y0, x1, y1, "edge strip")
    for i in range(5):
        lx = LED_X0 + LED_PITCH * i
        keepout(lx - 2.0, LED_Y - 2.0, lx + 2.0, LED_Y + 2.0, "D%d light cut-out" % (i + 1))

    def nn(name):
        return net(name if name in POWER else "/" + name)
    for name, layer, w, pts in ROUTES:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(ax), pcbnew.FromMM(ay)))
            t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(bx), pcbnew.FromMM(by)))
            t.SetWidth(pcbnew.FromMM(w))
            t.SetLayer(pcbnew.F_Cu if layer == "F" else pcbnew.B_Cu)
            t.SetNet(nn(name))
            b.Add(t)
    for name, x, y in VIAS:
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        v.SetWidth(pcbnew.FromMM(0.6))
        v.SetDrill(pcbnew.FromMM(0.3))
        v.SetNet(nn(name))
        b.Add(v)

    STITCH = 2.5
    # ground vias: the places on a 2.5 mm grid where one fits 0.25 mm clear of other nets' copper, the
    # cut-outs and the edge are only candidates; gnd_vias keeps the few that join a pour island or a GND
    # pad to the rest of the ground, so the board isn't covered in a grid of vias
    b.BuildConnectivity()
    gnd = net("GND")
    others = [t for t in b.GetTracks() if t.GetNetCode() != gnd.GetNetCode()]
    others += [p for f in b.GetFootprints() for p in f.Pads() if p.GetNetCode() != gnd.GetNetCode()]
    keepouts = [z for z in b.Zones() if z.GetIsRuleArea()]
    cands = []
    gx = x0 + 1.5
    while gx < x1 - 1.0:
        gy = y0 + 1.5
        while gy < y1 - 1.0:
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(gx), pcbnew.FromMM(gy)))
            v.SetWidth(pcbnew.FromMM(0.6))
            v.SetDrill(pcbnew.FromMM(0.3))
            v.SetNet(gnd)
            shape = v.GetEffectiveShape(pcbnew.F_Cu)
            clear = pcbnew.FromMM(0.25)
            hit = any(o.GetEffectiveShape(o.GetLayer() if o.GetClass() != "PAD" else pcbnew.B_Cu).Collide(shape, clear)
                      for o in others)
            hit = hit or any(z.Outline().Collide(v.GetPosition(), pcbnew.FromMM(0.3)) for z in keepouts)
            hit = hit or any(f.HitTest(v.GetPosition()) and f.GetReference().startswith(("J", "U", "L"))
                             for f in b.GetFootprints())
            if not hit:
                cands.append((gx, gy))
            gy += STITCH
        gx += STITCH

    # silkscreen on the parts' side
    t = pcbnew.PCB_TEXT(b)
    t.SetText("Dachshund70\nscreen v3.0")
    t.SetLayer(pcbnew.B_SilkS)
    t.SetMirrored(True)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
    t.SetTextThickness(pcbnew.FromMM(0.12))
    t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(340.0), pcbnew.FromMM(112.0)))
    b.Add(t)

    # saved and loaded again before the pours are filled: KiCad's zone filler crashes on a board with no
    # project behind it (seen on Windows)
    b.Save(pcb_path)
    b = pcbnew.LoadBoard(pcb_path)
    added = gnd_vias.join_ground(b, cands)
    b.Save(pcb_path)
    print("wrote %s (%d ground vias from %d candidates)" % (pcb_path, len(added), len(cands)))


if __name__ == "__main__":
    main()
