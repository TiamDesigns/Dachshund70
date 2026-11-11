"""Generate the Dachshund70 screen board: schematic, then the routed board.

The screen board carries a 2.7" Sharp memory LCD (LS027B7DH01, 400 x 240):
the panel's 5 V supply (a TPS61222 boost from the mainboard's 3V3), its
10-pin FPC socket and an 8-pin FFC socket for the cable to the mainboard's J4.

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

# The FFC socket's pin -> net. It sits right over the mainboard's J4 (the same footprint, upside down), and
# the 0.5 mm FFC loops round between them, so each pin meets the J4 pin at the same y: pin n here is J4
# pin 9 - n (see README). The mainboard's names for J4's pins are the e-paper ones (DIN, CLK, CS, DC, RST,
# BUSY); here they carry the Sharp's SI, SCLK, SCS, EXTCOMIN, DISP and the boost enable.
MAINBOARD_J4 = {1: "+3V3", 2: "GND", 3: "SI", 4: "SCLK", 5: "SCS", 6: "EXTCOMIN", 7: "DISP", 8: "VLCD_EN"}
CABLE = {n: MAINBOARD_J4[9 - n] for n in range(1, 9)}
POWER = ("+3V3", "+5V", "GND")

# J1's pads run the other way from the panel's pins: the tail folds back under the glass, so (looking down on
# the board) panel pin 1 lands at the top, where J1's pad 10 is. J1 pin n = panel pin 11 - n (see README).
SOCKET = {n: PANEL[11 - n] for n in range(1, 11)}

# ref: (lib_id, value, footprint, mpn, lcsc, {pin: net})
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
PARTS = {
    "J1": ("Connector_Generic_MountingPin:Conn_01x10_MountingPin", "Memory LCD (FPC 10P 0.5 mm)",
           "Connector_FFC-FPC:Hirose_FH12-10S-0.5SH_1x10-1MP_P0.50mm_Horizontal",
           "Hirose FH12-10S-0.5SH(55)", "", dict(SOCKET, MP="GND")),
    "J2": ("Connector_Generic_MountingPin:Conn_01x08_MountingPin", "Mainboard J4 (FFC 8P 0.5 mm, same side)",
           "Connector_FFC-FPC:Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal",
           "Hirose FH12-8S-0.5SH(55)", "", dict(CABLE, MP="GND")),
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

# Board placement: x, y, rotation, side ("B" = bottom). Mainboard coordinates.
BOARD_OUTLINE = (311.0, 69.2, 332.0, 103.2)     # x0, y0, x1, y1: the case's screen-board pocket
BOARD_CORNER_R = 1.0
THICKNESS = 0.8
CABLE_XY = (327.9, 94.9)                         # J2 here = J4 on the mainboard, the same x and y
PLACE = {
    # The panel's FPC leaves its long edge on the left (in portrait) and folds back under the glass into J1,
    # whose mouth faces -x (see README, "Panel tail").
    "J1": (316.6, 93.7, None, "B"),
    "J2": (CABLE_XY[0], CABLE_XY[1], None, "B"),          # orientation set so the mouth faces -x
    # Others: (x, y, (pad, dx, dy), "B"): the rotation is the one that puts that pad on the (dx, dy) side
    # the boost, above the sockets
    "U1": (319.5, 84.0, 180, "B"),                        # VIN top right, EN top left
    "L1": (315.85, 84.0, ("2", 1, 0), "B"),
    "C1": (322.3, 83.4, ("1", 0, -1), "B"),
    "C2": (317.9, 86.6, ("1", 1, 0), "B"),
    "R1": (326.5, 88.6, ("1", 1, 0), "B"),
    # the panel's own capacitors, below the signal bundle
    "C5": (321.0, 97.7, ("1", 0, -1), "B"),
    "C3": (320.6, 101.2, ("1", 0, -1), "B"),
    "C4": (322.1, 101.2, ("1", 0, -1), "B"),
}


# ---------------------------------------------------------------- routing
# Hand-routed (two layers). Every part is on B.Cu; F.Cu, under the panel, is a ground pour that also carries
# three hops: SCLK over SI (the one crossing), +5V from the boost to the panel socket, and the boost enable.
# (net, layer, width, [(x, y), ...])
J1X = 318.45                                     # J1's pad row
J2X = 329.75                                     # J2's pad row
ROUTES = [
    # signals: right from the panel socket, then down a staircase into the FFC socket under its body
    ("SI", "B", 0.2, [(J1X, 91.95), (324.6, 91.95), (324.6, 94.15), (J2X, 94.15)]),
    ("SCLK", "B", 0.2, [(J1X, 91.45), (319.75, 91.45), (320.2, 91.0)]),
    ("SCLK", "F", 0.2, [(320.2, 91.0), (323.3, 93.3)]),
    ("SCLK", "B", 0.2, [(323.3, 93.3), (323.3, 94.65), (J2X, 94.65)]),
    ("SCS", "B", 0.2, [(J1X, 92.45), (322.0, 92.45), (322.0, 95.15), (J2X, 95.15)]),
    ("EXTCOMIN", "B", 0.2, [(J1X, 92.95), (321.5, 92.95), (321.5, 95.65), (J2X, 95.65)]),
    ("DISP", "B", 0.2, [(J1X, 93.45), (321.0, 93.45), (321.0, 96.15), (J2X, 96.15)]),
    ("DISP", "B", 0.2, [(321.0, 96.15), (321.0, 97.22)]),                       # C5
    # boost enable: J2 pin 1, R1's pull-up, U1's EN
    ("VLCD_EN", "B", 0.2, [(J2X, 96.65), (324.3, 96.65), (323.6, 97.3)]),
    ("VLCD_EN", "F", 0.2, [(323.6, 97.3), (324.2, 96.7), (324.2, 89.4), (325.0, 88.6)]),
    ("VLCD_EN", "B", 0.2, [(325.0, 88.6), (325.99, 88.6)]),
    ("VLCD_EN", "F", 0.2, [(325.0, 88.6), (325.0, 82.3), (324.0, 81.3), (319.6, 81.3), (318.663, 82.5)]),
    ("VLCD_EN", "B", 0.2, [(318.663, 82.5), (318.663, 83.35)]),
    # 3V3: up from J2 under its body, to R1, then along the top to U1's VIN, C1 and L1
    ("+3V3", "B", 0.3, [(J2X, 93.15), (328.6, 93.15), (328.6, 81.8), (314.7, 81.8), (314.7, 82.65)]),
    ("+3V3", "B", 0.3, [(328.6, 88.6), (327.01, 88.6)]),
    ("+3V3", "B", 0.3, [(320.337, 83.35), (320.337, 81.8)]),
    ("+3V3", "B", 0.3, [(322.3, 82.625), (322.3, 81.8)]),
    # boost
    ("SW", "B", 0.4, [(318.663, 84.0), (317.0, 84.0)]),
    ("+5V", "B", 0.2, [(320.337, 84.0), (319.5, 84.0), (319.5, 84.65), (318.663, 84.65)]),   # FB to VOUT
    ("+5V", "B", 0.3, [(318.663, 84.65), (318.663, 86.6), (319.85, 86.6)]),
    # 5 V over to the panel socket (pins 6-8 = J1 pads 5-3) and its capacitors
    ("+5V", "F", 0.3, [(319.85, 86.6), (319.3, 87.15), (319.3, 93.6), (320.3, 94.45)]),
    ("+5V", "B", 0.25, [(J1X, 93.95), (319.6, 93.95), (319.6, 94.95), (J1X, 94.95)]),
    ("+5V", "B", 0.25, [(J1X, 94.45), (320.3, 94.45)]),
    ("+5V", "F", 0.3, [(320.3, 94.45), (319.4, 95.35), (319.4, 98.9), (320.3, 99.8), (321.35, 99.8)]),
    ("+5V", "B", 0.25, [(321.35, 99.8), (320.6, 100.72)]),
    ("+5V", "B", 0.25, [(321.35, 99.8), (322.1, 100.72)]),
    # ground: pads to their vias
    ("GND", "B", 0.25, [(J1X, 95.45), (319.6, 95.45), (319.6, 95.95), (J1X, 95.95)]),
    ("GND", "B", 0.25, [(319.6, 95.95), (320.35, 96.0)]),
    ("GND", "B", 0.3, [(J2X, 93.65), (331.05, 93.65)]),
    ("GND", "B", 0.3, [(320.337, 84.65), (321.6, 85.3)]),
    ("GND", "B", 0.3, [(322.3, 84.175), (321.6, 85.3)]),
    ("GND", "B", 0.3, [(317.125, 86.6), (316.1, 87.2)]),
]
VIAS = [
    ("SCLK", 320.2, 91.0), ("SCLK", 323.3, 93.3),
    ("VLCD_EN", 323.6, 97.3), ("VLCD_EN", 325.0, 88.6), ("VLCD_EN", 318.663, 82.5),
    ("+5V", 319.85, 86.6), ("+5V", 320.3, 94.45), ("+5V", 321.35, 99.8),
    *[("GND", x, y) for x, y in (
        (320.35, 96.0), (331.05, 93.65), (321.6, 85.3), (316.1, 87.2),
        # stitching
        (313.0, 72.0), (318.0, 72.0), (324.0, 72.0), (330.0, 72.0), (313.0, 79.0), (322.0, 78.5),
        (330.5, 80.0), (330.5, 88.0), (313.0, 86.5), (316.5, 88.0), (313.0, 101.5), (325.0, 101.8),
        (330.5, 101.8))],
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
    # and SW: U1's L pin is a power input, fed only through L1
    fx, fy = 66.04, 30.48
    instance("#FLG03", "power:PWR_FLAG", fx, fy, "PWR_FLAG", hide_ref=True)
    items.append(["wire", ["pts", ["xy", "%.2f" % fx, "%.2f" % fy], ["xy", "%.2f" % fx, "%.2f" % (fy + 2.54)]],
                  ["stroke", ["width", "0"], ["type", "default"]], ["uuid", q(U())]])
    attach("SW", fx, fy + 2.54, 90)

    notes = [
        "Dachshund70 screen board: 5 V for the Sharp LS027B7DH01 memory LCD (U1, L1, C1, C2) and panel socket J1.",
        "J2: 8-pin 0.5 mm FFC to the mainboard's J4 (same-side contacts). J2 pin n = J4 pin 9 - n.",
        "J4-8 (VLCD_EN) enables U1; R1 holds it high. EXTMODE high: VCOM follows the EXTCOMIN pulse.",
        "C3 (VDD), C4 (VDDA) and C5 (DISP) are the capacitors from Sharp's specification, next to J1.",
        "J1 pin n = panel pin 11 - n: the panel's tail folds back under the glass.",
    ]
    for i, t in enumerate(notes):
        items.append(["text", q(t), ["exclude_from_sim", "no"], ["at", "25.4", "%.2f" % (172.72 + 3.81 * i), "0"],
                      ["effects", ["font", ["size", "1.27", "1.27"]], ["justify", "left", "bottom"]], ["uuid", q(U())]])

    sch = ["kicad_sch", ["version", "20260306"], ["generator", q("eeschema")], ["generator_version", q("10.0")],
           ["uuid", q(root_uuid)], ["paper", q("A4")],
           ["title_block", ["title", q("Dachshund70 screen board")], ["date", q("2026-11-11")], ["rev", q("2.0")],
            ["comment", "1", q("2.7in Sharp memory LCD (LS027B7DH01): 5 V boost, FPC socket, FFC to the mainboard")]],
           ["lib_symbols"] + list(used_libs.values())]
    sch += items
    sch += [["sheet_instances", ["path", q("/"), ["page", q("1")]]], ["embedded_fonts", "no"]]
    return sch, sym_uuids


SHEET_XY = {
    "J1": (63.5, 101.6), "J2": (215.9, 76.2),
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
        if ref in ("J1", "J2"):
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
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
        ol = z.Outline()
        ol.NewOutline()
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
        b.Add(z)

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

    # silkscreen on the parts' side
    t = pcbnew.PCB_TEXT(b)
    t.SetText("Dachshund70\nscreen v2.0")
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
