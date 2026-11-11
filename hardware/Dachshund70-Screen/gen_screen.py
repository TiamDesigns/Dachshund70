"""Generate the Dachshund70 screen board: schematic, then the routed board.

The screen board carries a 2.13" SSD1680 e-paper panel (GoodDisplay GDEY0213B74,
or the GDEY0213B74H, which has the same pins): the panel's boost circuit, its
24-pin FPC socket and an 8-pin FFC socket for the cable to the mainboard's J4.
It replaces the Adafruit eInk Breakout Friend and the hand-soldered wires.

Run with KiCad 10's own Python (it ships the pcbnew module), from the repo root:

    "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70-Screen/gen_screen.py

or in the kicad/kicad:10.0 Docker image. It overwrites the .kicad_sch and the
whole .kicad_pcb: placement, the hand routing in ROUTES and VIAS, and the
filled ground pours. Check with
`kicad-cli pcb drc --schematic-parity --severity-all Dachshund70-Screen.kicad_pcb`.

Coordinates are the mainboard's (KiCad mm, y down): the board lies in the
case's screen pocket right over the mainboard, so its STEP drops into the
case model at the same x and y. Its top face is taped to the panel's back and
every part is on the bottom side, facing the mainboard.
"""

import os
import re
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "Dachshund70-Screen"
SYMDIR = os.environ.get("KICAD_SYMBOL_DIR", "/usr/share/kicad/symbols")
FPDIR = os.environ.get("KICAD_FOOTPRINT_DIR", "/usr/share/kicad/footprints")

# ---------------------------------------------------------------- the circuit
# Boost and charge-pump circuit for SSD1680 panels, as on Adafruit's 2.13"
# eInk Bonnet and GoodDisplay's reference design: L1/Q1/R1 make VGH and VSH
# from 3V3 (the SSD1680 drives the gate through GDR and senses the current on
# RESE); C10/D1/D2 pump the negative rails. Panel pins 1, 4, 6, 7 and 19 stay
# open (NC, the temperature-sensor I2C and VPP, a test pin); BS1 is low for
# 4-wire SPI.

# Panel FPC pin -> net (GoodDisplay GDEY0213B74 specification, section 5)
PANEL = {
    1: None, 2: "GDR", 3: "RESE", 4: None, 5: "VSH2", 6: None, 7: None, 8: "GND",
    9: "DISP_BUSY", 10: "DISP_RST", 11: "DISP_DC", 12: "DISP_CS", 13: "DISP_CLK",
    14: "DISP_DIN", 15: "+3V3", 16: "+3V3", 17: "GND", 18: "VDD", 19: None,
    20: "VSH1", 21: "VGH", 22: "VSL", 23: "VGL", 24: "VCOM",
}

# The FFC socket's pin -> net. It sits right over the mainboard's J4 (the same
# footprint, upside down), and the 0.5 mm FFC loops round between them, so each
# pin meets the J4 pin at the same y: pin n here is J4 pin 9 - n (see README).
MAINBOARD_J4 = {1: "+3V3", 2: "GND", 3: "DISP_DIN", 4: "DISP_CLK", 5: "DISP_CS",
                6: "DISP_DC", 7: "DISP_RST", 8: "DISP_BUSY"}
CABLE = {n: MAINBOARD_J4[9 - n] for n in range(1, 9)}

# ref: (lib_id, value, footprint, mpn, lcsc, {pin: net}, (x, y) on the sheet,
#       board (x, y, rotation, side))
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
PARTS = {
    "J1": ("Connector_Generic_MountingPin:Conn_01x24_MountingPin", "E-paper panel (FPC 24P 0.5 mm)",
           "Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal",
           "Hirose FH12-24S-0.5SH(55)", "", dict(PANEL, MP="GND")),
    "J2": ("Connector_Generic_MountingPin:Conn_01x08_MountingPin", "Mainboard J4 (FFC 8P 0.5 mm, same side)",
           "Connector_FFC-FPC:Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal",
           "Hirose FH12-8S-0.5SH(55)", "", dict(CABLE, MP="GND")),
    "L1": ("Device:L", "10uH", "Inductor_SMD:L_Changjiang_FNR3015S",
           "Changjiang FNR3015S100MT (10 uH, 3 x 3 x 1.5 mm, 0.9 A)", "", {1: "+3V3", 2: "SW"}),
    "Q1": ("Transistor_FET:AO3400A", "AO3400A", "Package_TO_SOT_SMD:SOT-23",
           "AOS AO3400A", "C20917", {1: "GDR", 2: "RESE", 3: "SW"}),
    "R1": ("Device:R", "0.47", "Resistor_SMD:R_0603_1608Metric",
           "UNI-ROYAL 0603WAFR470T5E (0.47 ohm, 1 %)", "", {1: "RESE", 2: "GND"}),
    "D1": ("Device:D_Schottky", "B5819W", "Diode_SMD:D_SOD-123", "B5819W SL", "C8598", {1: "PVGL", 2: "VGL"}),
    "D2": ("Device:D_Schottky", "B5819W", "Diode_SMD:D_SOD-123", "B5819W SL", "C8598", {1: "GND", 2: "PVGL"}),
    "D3": ("Device:D_Schottky", "B5819W", "Diode_SMD:D_SOD-123", "B5819W SL", "C8598", {1: "VGH", 2: "SW"}),
    "C1": ("Device:C", "10uF", C0603, "Samsung CL10A106KP8NNNC (10 uF, 10 V, X5R)", "C19702", {1: "+3V3", 2: "GND"}),
    "C2": ("Device:C", "1uF", C0402, "Samsung CL05A105KA5NQNC (1 uF, 25 V, X5R)", "C52923", {1: "VDD", 2: "GND"}),
    "C3": ("Device:C", "1uF 25V", C0603, "Samsung CL10A105KA8NNNC (1 uF, 25 V, X5R)", "C15849", {1: "VSH1", 2: "GND"}),
    "C4": ("Device:C", "1uF", C0402, "Samsung CL05A105KA5NQNC (1 uF, 25 V, X5R)", "C52923", {1: "VSH2", 2: "GND"}),
    "C5": ("Device:C", "1uF 25V", C0603, "Samsung CL10A105KA8NNNC (1 uF, 25 V, X5R)", "C15849", {1: "VSL", 2: "GND"}),
    "C6": ("Device:C", "1uF 25V", C0603, "Samsung CL10A105KA8NNNC (1 uF, 25 V, X5R)", "C15849", {1: "VGH", 2: "GND"}),
    "C7": ("Device:C", "1uF 25V", C0603, "Samsung CL10A105KA8NNNC (1 uF, 25 V, X5R)", "C15849", {1: "VGL", 2: "GND"}),
    "C8": ("Device:C", "1uF", C0402, "Samsung CL05A105KA5NQNC (1 uF, 25 V, X5R)", "C52923", {1: "VCOM", 2: "GND"}),
    "C9": ("Device:C", "4.7uF 25V", "Capacitor_SMD:C_0805_2012Metric",
           "Samsung CL21A475KAQNNNC (4.7 uF, 25 V, X5R)", "C1779", {1: "SW", 2: "PVGL"}),
    "C10": ("Device:C", "100nF", "Capacitor_SMD:C_0402_1005Metric", "Samsung CL05B104KO5NNNC", "C1525",
            {1: "+3V3", 2: "GND"}),
}

# Board placement: x, y, rotation, side ("B" = bottom). Mainboard coordinates.
BOARD_OUTLINE = (311.0, 69.2, 332.0, 103.2)     # x0, y0, x1, y1: inside the case's old driver-board pocket
BOARD_CORNER_R = 1.0
THICKNESS = 0.8
CABLE_XY = (327.9, 94.9)                         # J2 here = J4 on the mainboard, the same x and y
PLACE = {
    # the panel socket's mouth faces the back edge, where the panel's tail folds round; pin 1 on the left
    # (seen from above), its pad row 10.65 mm inside the glass's back edge (see README, "Panel tail")
    "J1": (322.35, 75.65, 0, "B"),
    "J2": (CABLE_XY[0], CABLE_XY[1], None, "B"),          # orientation set so the mouth faces -x
    # Others: (x, y, (pad, dx, dy), "B"): the rotation is the one that puts that pad on the (dx, dy) side
    # boost, left of the signal bundle
    "Q1": (317.55, 82.6, ("3", 0, 1), "B"),
    "C4": (318.6, 79.6, ("1", 0, -1), "B"),
    "R1": (319.6, 86.2, ("1", 0, -1), "B"),
    "L1": (313.9, 82.6, ("2", 1, 0), "B"),
    "D3": (317.55, 87.1, ("2", 0, -1), "B"),
    "C9": (315.0, 86.6, ("1", 0, -1), "B"),
    "D2": (314.3, 90.75, ("2", 1, 0), "B"),
    "D1": (314.3, 93.3, ("1", 1, 0), "B"),
    "C7": (312.4, 96.4, ("1", 0, -1), "B"),
    "C6": (319.6, 90.0, ("1", 0, -1), "B"),
    "C1": (312.5, 86.6, ("1", 0, -1), "B"),
    # panel rails, right of the bundle
    "C2": (325.4, 80.9, ("1", 0, -1), "B"),
    "C5": (327.7, 81.0, ("1", 0, -1), "B"),
    "C3": (326.6, 84.2, ("1", 0, -1), "B"),
    "C8": (329.4, 83.8, ("1", 0, -1), "B"),
    "C10": (325.2, 87.6, ("1", -1, 0), "B"),
}


# ---------------------------------------------------------------- routing
# Hand-routed (two layers). Every part is on B.Cu; F.Cu, under the panel, carries the GND pour and three
# long rails (VGH, VGL, 3V3) that hop over the signal bundle. (net, layer, width, [(x, y), ...])
SIG = ("DISP_BUSY", "DISP_RST", "DISP_DC", "DISP_CS", "DISP_CLK", "DISP_DIN")
ROUTES = [
    # signals: straight down from the panel socket, then right into the FFC socket under its body (a staircase,
    # so nothing crosses)
    *[(n, "B", 0.2, [(320.6 + 0.5 * i, 77.5), (320.6 + 0.5 * i, 96.65 - 0.5 * i), (329.75, 96.65 - 0.5 * i)])
      for i, n in enumerate(SIG)],
    ("+3V3", "B", 0.3, [(323.6, 77.9), (324.1, 77.9)]),
    ("+3V3", "B", 0.3, [(323.85, 77.9), (323.85, 93.15), (329.75, 93.15)]),
    ("+3V3", "B", 0.3, [(323.85, 87.6), (324.72, 87.6)]),                      # C10
    ("+3V3", "F", 0.4, [(323.85, 93.0), (317.0, 93.0), (313.4, 89.4), (313.4, 85.55), (312.6, 84.75)]),
    ("+3V3", "B", 0.4, [(312.75, 82.6), (312.6, 84.75), (312.5, 85.8)]),        # L1, C1
    # boost
    ("GDR", "B", 0.25, [(317.1, 77.5), (317.1, 80.4), (316.6, 80.9), (316.6, 81.662)]),
    ("RESE", "B", 0.25, [(317.6, 77.5), (317.6, 80.6), (318.5, 81.5), (318.5, 81.662), (319.6, 82.8),
                         (319.6, 85.375)]),
    ("VSH2", "B", 0.25, [(318.6, 77.5), (318.6, 79.12)]),
    ("SW", "B", 0.4, [(315.05, 83.5), (317.55, 83.5)]),
    ("SW", "B", 0.4, [(317.55, 83.537), (317.55, 85.45)]),
    ("SW", "B", 0.4, [(315.05, 83.5), (315.0, 85.65)]),
    ("VGH", "B", 0.25, [(317.55, 88.75), (317.55, 90.0)]),
    ("VGH", "B", 0.25, [(317.55, 89.0), (319.6, 89.0)]),
    ("VGH", "F", 0.25, [(317.55, 90.0), (321.85, 85.7), (321.85, 79.0), (325.85, 79.0), (326.6, 78.25),
                        (326.6, 76.0)]),
    ("VGH", "B", 0.25, [(326.6, 76.0), (326.6, 77.5)]),
    ("PVGL", "B", 0.25, [(315.0, 87.55), (315.95, 88.5), (315.95, 93.3)]),
    ("VGL", "B", 0.25, [(312.65, 93.3), (312.4, 95.625), (313.6, 95.6)]),
    ("VGL", "F", 0.25, [(313.6, 95.6), (311.9, 93.9), (311.9, 75.2), (327.6, 75.2)]),
    ("VGL", "B", 0.25, [(327.6, 75.2), (327.6, 77.5)]),
    # panel rails on the right
    ("VDD", "B", 0.25, [(325.1, 77.5), (325.1, 79.9), (325.4, 80.2), (325.4, 80.42)]),
    ("VSH1", "B", 0.25, [(326.1, 77.5), (326.1, 82.5), (326.6, 83.0), (326.6, 83.425)]),
    ("VSL", "B", 0.25, [(327.1, 77.5), (327.1, 79.4), (327.7, 80.0), (327.7, 80.225)]),
    ("VCOM", "B", 0.25, [(328.1, 77.5), (328.1, 78.6), (329.4, 79.9), (329.4, 83.32)]),
    # ground: pads to their vias
    ("GND", "B", 0.3, [(320.1, 77.5), (320.1, 76.1)]),
    ("GND", "B", 0.3, [(324.6, 77.5), (324.6, 76.1)]),
    ("GND", "B", 0.3, [(318.6, 80.08), (319.6, 80.4)]),
    ("GND", "B", 0.3, [(319.6, 87.025), (318.6, 87.1)]),
    ("GND", "B", 0.3, [(319.6, 90.775), (319.6, 91.7)]),
    ("GND", "B", 0.3, [(312.5, 87.375), (312.65, 88.75), (312.65, 90.75)]),
    ("GND", "B", 0.3, [(312.4, 97.175), (312.4, 98.1)]),
    ("GND", "B", 0.3, [(325.4, 81.38), (325.4, 82.3)]),
    ("GND", "B", 0.3, [(327.7, 81.775), (327.7, 82.7)]),
    ("GND", "B", 0.3, [(326.6, 84.975), (326.6, 85.9)]),
    ("GND", "B", 0.3, [(329.4, 84.28), (329.4, 85.2)]),
    ("GND", "B", 0.3, [(325.68, 87.6), (326.5, 87.6)]),
    ("GND", "B", 0.3, [(329.75, 93.65), (331.05, 93.65)]),
]
VIAS = [
    ("+3V3", 323.85, 93.0), ("+3V3", 312.6, 84.75), ("VGH", 317.55, 90.0), ("VGH", 326.6, 76.0),
    ("VGL", 313.6, 95.6), ("VGL", 327.6, 75.2),
    *[("GND", x, y) for x, y in (
        (320.1, 76.1), (324.6, 76.1), (319.6, 80.4), (318.6, 87.1), (319.6, 91.7), (312.65, 88.75), (312.4, 98.1),
        (325.4, 82.3), (327.7, 82.7), (326.6, 85.9), (329.4, 85.2), (326.5, 87.6), (331.05, 93.65),
        # stitching
        (330.8, 80.0), (330.8, 90.0), (329.0, 92.0), (319.5, 95.0), (316.5, 96.5), (313.0, 79.7), (322.0, 101.8),
        (328.5, 102.2), (319.6, 102.2))],
]


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
        if net in ("+3V3", "GND"):
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

    notes = [
        "Dachshund70 screen board: SSD1680 e-paper boost (L1, Q1, R1, D1-D3, C9) and panel socket J1.",
        "J2: 8-pin 0.5 mm FFC to the mainboard's J4 (same-side contacts). J2 pin n = J4 pin 9 - n.",
        "Panel pins 1, 4, 6, 7, 19 open (NC, TSCL, TSDA, VPP). BS1 low: 4-wire SPI.",
        "C3-C8 25 V: VGH/VSH reach about +20 V, VGL/VSL about -20 V.",
    ]
    for i, t in enumerate(notes):
        items.append(["text", q(t), ["exclude_from_sim", "no"], ["at", "25.4", "%.2f" % (172.72 + 3.81 * i), "0"],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left", "bottom"]], ["uuid", q(U())]])

    sch = ["kicad_sch", ["version", "20260306"], ["generator", q("eeschema")], ["generator_version", q("10.0")],
           ["uuid", q(root_uuid)], ["paper", q("A4")],
           ["title_block", ["title", q("Dachshund70 screen board")], ["date", q("2026-11-11")], ["rev", q("1.0")],
            ["comment", "1", q("2.13in SSD1680 e-paper (GDEY0213B74 / GDEY0213B74H): boost, FPC socket, FFC to the mainboard")]],
           ["lib_symbols"] + list(used_libs.values())]
    sch += items
    sch += [["sheet_instances", ["path", q("/"), ["page", q("1")]]], ["embedded_fonts", "no"]]
    return sch, sym_uuids


SHEET_XY = {
    "J1": (63.5, 101.6), "J2": (215.9, 50.8),
    "L1": (127.0, 50.8), "Q1": (139.7, 76.2), "R1": (149.86, 96.52), "D1": (190.5, 76.2), "D2": (190.5, 96.52),
    "D3": (162.56, 50.8), "C9": (177.8, 66.04), "C1": (101.6, 50.8), "C2": (114.3, 116.84),
    "C3": (127.0, 116.84), "C4": (139.7, 116.84), "C5": (152.4, 116.84), "C6": (165.1, 116.84),
    "C7": (177.8, 116.84), "C8": (190.5, 116.84), "C10": (101.6, 76.2)
}


def main():
    sch_path = os.path.join(HERE, NAME + ".kicad_sch")
    root_uuid = None
    if os.path.exists(sch_path):
        m = re.search(r'\(uuid "([^"]+)"\)', open(sch_path, encoding="utf-8").read())
        root_uuid = m.group(1) if m else None
    root_uuid = root_uuid or U()
    sch, sym_uuids = build_schematic(root_uuid, SHEET_XY)
    with open(sch_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(sch) + "\n")
    print("wrote", sch_path)
    build_board(sym_uuids)


# ---------------------------------------------------------------- board
def build_board(sym_uuids):
    import pcbnew
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
        lib, name = fpid.split(":")
        fp = pcbnew.FootprintLoad(os.path.join(FPDIR, lib + ".pretty"), name)
        fp.SetFPIDAsString(fpid)
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
        if ref == "J2":
            # mouth (the actuator, +y in the library footprint) toward -x, so the pads end up on the +x side
            place(fp, x, y, None, side)
            for r in (90, 270):
                fp.SetOrientationDegrees(r)
                if pads_centre(fp, "1")[0] > x:
                    break
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
                n = "unconnected-(%s-Pin_%s-Pad%s)" % (ref, num, num)
            elif n not in ("+3V3", "GND"):
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
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
        ol = z.Outline()
        ol.NewOutline()
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
        b.Add(z)

    def nn(name):
        return net(name if name in ("+3V3", "GND") else "/" + name)
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

    # silkscreen on the parts' side
    t = pcbnew.PCB_TEXT(b)
    t.SetText("Dachshund70\nscreen v1.0")
    t.SetLayer(pcbnew.B_SilkS)
    t.SetMirrored(True)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
    t.SetTextThickness(pcbnew.FromMM(0.12))
    t.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(315.6), pcbnew.FromMM(100.6)))
    b.Add(t)

    b.BuildConnectivity()
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(pcb_path)
    print("wrote", pcb_path)


if __name__ == "__main__":
    main()
