"""One-off edit of the mainboard: J4, the hand-wired 2.54 mm display header, becomes an
8-pin 0.5 mm FFC socket for the screen board (Hirose FH12-8S, top side, under the plate notch) and the
eight display nets are rerouted to it. Kept for the record; run it once, in KiCad 10's Python, from the
repo root. The schematic side is done separately (J4's symbol becomes Conn_01x08_MountingPin, MP to GND).

J4's pins sit at the same x and y as the screen board's J2 (the FFC loops round between them), so pin n
here meets J2 pin 9 - n. Pin 1 (3V3) is at the back (smaller y), pin 8 (BUSY) at the front. The
socket sits under the plate's screen notch, 2.7 mm behind the SWD header J3 so its body clears J3.
"""
import pcbnew

PCB = "hardware/Dachshund70/Dachshund70.kicad_pcb"
FP_DIR = "/usr/share/kicad/footprints/Connector_FFC-FPC.pretty"
FP_NAME = "Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal"
XY = (327.9, 94.9)           # pads y 93.15-96.65, clear of J3 (the SWD header, from y 100.4)
M, F = pcbnew.ToMM, pcbnew.FromMM

b = pcbnew.LoadBoard(PCB)
nets = {n: b.FindNet(n) for n in ("+3V3", "GND", "/DISP_DIN", "/DISP_CLK", "/DISP_CS", "/DISP_DC", "/DISP_RST",
                                  "/DISP_BUSY")}
DISP = [n for n in nets if n.startswith("/DISP")]


TRACKS = list(b.GetTracks())    # looked up once: pcbnew's track list can't be re-read after a Remove
REMOVE = []


def P(x, y):
    return pcbnew.VECTOR2I(F(x), F(y))


def near(a, xy, tol=0.002):
    return abs(M(a.x) - xy[0]) < tol and abs(M(a.y) - xy[1]) < tol


def find_track(net, layer, a, c):
    for t in TRACKS:
        if t in REMOVE:
            continue
        if t.GetClass() == "PCB_VIA" or t.GetNetname() != net or t.GetLayerName() != layer:
            continue
        if (near(t.GetStart(), a) and near(t.GetEnd(), c)) or (near(t.GetStart(), c) and near(t.GetEnd(), a)):
            return t
    raise SystemExit("no track %s %s %r %r" % (net, layer, a, c))


def find_via(net, xy):
    for t in TRACKS:
        if t.GetClass() == "PCB_VIA" and t.GetNetname() == net and near(t.GetPosition(), xy, 0.01):
            return t
    raise SystemExit("no via %s %r" % (net, xy))


def drop_track(net, layer, a, c):
    REMOVE.append(find_track(net, layer, a, c))


def move_end(net, layer, a, c, old, new):
    """Move the end of track a-c that sits at old to new."""
    t = find_track(net, layer, a, c)
    if near(t.GetStart(), old):
        t.SetStart(P(*new))
    else:
        t.SetEnd(P(*new))


def track(net, layer, pts, w):
    for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(P(ax, ay))
        t.SetEnd(P(cx, cy))
        t.SetWidth(F(w))
        t.SetLayer(pcbnew.F_Cu if layer == "F" else pcbnew.B_Cu)
        t.SetNet(nets[net])
        b.Add(t)


def via(net, x, y):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(P(x, y))
    v.SetWidth(F(0.6))
    v.SetDrill(F(0.3))
    v.SetNet(nets[net])
    b.Add(v)


# ---- the old header and every F.Cu stub to it
old = b.FindFootprintByReference("J4")
path = old.GetPath()
for t in TRACKS:
    if t.GetClass() != "PCB_VIA" and t.GetLayerName() == "F.Cu" and t.GetNetname() in DISP:
        if M(t.GetStart().y) > 104.0 or M(t.GetEnd().y) > 104.0:      # the display runs below y 104 only
            REMOVE.append(t)
for n, xy in (("/DISP_DIN", (304.126, 111.2844)), ("/DISP_CLK", (303.4476, 109.2921)),
              ("/DISP_CS", (302.8174, 107.3224)), ("/DISP_BUSY", (302.2158, 105.4471))):
    REMOVE.append(find_via(n, xy))
for gx, gy in ((323.85, 95.25), (321.150933, 109.600499), (302.0277, 108.961626)):   # GND stitching in the way
    REMOVE.append(find_via("GND", (gx, gy)))
b.Remove(old)

# 3V3 used to pass through the header's pin 1 on its way to J3 (F.Cu in, B.Cu out): a via there now

# B.Cu ends of the four F.Cu runs: the vias move so the runs come out DIN on top, BUSY at the bottom
drop_track("/DISP_DIN", "B.Cu", (304.126, 111.2844), (304.3172, 111.0932))
move_end("/DISP_DIN", "B.Cu", (304.3172, 111.0932), (304.3172, 80.2828), (304.3172, 111.0932), (304.3172, 105.81))
track("/DISP_DIN", "B", [(304.3172, 105.81), (304.126, 106.0)], 0.25)          # clear of ROW4 at x 304.77
move_end("/DISP_CLK", "B.Cu", (303.4476, 109.2921), (303.4476, 88.3391), (303.4476, 109.2921), (303.4476, 106.5))
track("/DISP_CLK", "B", [(303.4476, 106.5), (303.5476, 106.8)], 0.25)
drop_track("/DISP_CS", "B.Cu", (302.8636, 107.2762), (302.8174, 107.3224))
move_end("/DISP_CS", "B.Cu", (302.8636, 88.3939), (302.8636, 107.2762), (302.8636, 107.2762), (302.8636, 107.58))
move_end("/DISP_BUSY", "B.Cu", (302.2158, 105.4471), (302.2158, 88.3849), (302.2158, 105.4471), (302.2158, 109.4))
# DC: its B.Cu run from the north now stops at a via at y 108.2
drop_track("/DISP_DC", "B.Cu", (321.81, 112.5), (323.8355, 110.4745))
move_end("/DISP_DC", "B.Cu", (323.8355, 110.4745), (323.8355, 100.5464), (323.8355, 110.4745), (323.8355, 108.2))
# RST: its B.Cu run now stops at a via at y 108.8 instead of looping south of the old header
for a, c in (((324.35, 112.5), (322.0256, 114.8244)), ((322.0256, 114.8244), (309.2719, 114.8244)),
             ((309.2719, 114.8244), (307.9155, 113.468)), ((307.9155, 113.468), (307.9155, 113.1497)),
             ((307.9155, 113.1497), (307.9155, 112.8313)), ((307.9155, 112.8313), (307.9155, 109.0255)),
             ((307.9155, 109.0255), (309.5086, 107.4324))):
    drop_track("/DISP_RST", "B.Cu", a, c)
track("/DISP_RST", "B", [(309.5086, 107.4324), (309.5086, 108.8)], 0.25)
for n, x, y in (("+3V3", 309.11, 112.5), ("/DISP_DIN", 304.126, 106.0), ("/DISP_CLK", 303.5476, 106.8), ("/DISP_CS", 302.8636, 107.58),
                ("/DISP_BUSY", 302.2158, 109.4), ("/DISP_DC", 323.8355, 108.2), ("/DISP_RST", 309.5086, 108.8)):
    via(n, x, y)

for t in REMOVE:
    b.Remove(t)

# ---- the new socket
fp = pcbnew.FootprintLoad(FP_DIR, FP_NAME)
fp.SetFPIDAsString("Connector_FFC-FPC:" + FP_NAME)
fp.SetReference("J4")
fp.SetValue("Screen board")
fp.GetField(pcbnew.FIELD_T_DATASHEET).SetText(
    "https://www.hirose.com/product/document?clcode=CL0580-1255-6-55&productname=FH12-8S-0.5SH(55)&series=FH12"
    "&documenttype=Catalog&lang=en&documentid=D31690_en")
fp.GetField(pcbnew.FIELD_T_DESCRIPTION).SetText(
    "Screen board cable port: 8-pin 0.5 mm FFC, same-side contacts "
    "(pin 1 3V3, 2 GND, 3 DIN, 4 CLK, 5 CS, 6 DC, 7 RST, 8 BUSY)")
for fname, fval in (("MPN", "Hirose FH12-8S-0.5SH(55)"), ("LCSC", "")):
    fld = pcbnew.PCB_FIELD(fp, fp.GetNextFieldOrdinal(), fname)
    fld.SetText(fval)
    fld.SetVisible(False)
    fld.SetLayer(pcbnew.F_Fab)
    fp.Add(fld)
fp.SetPath(path)
fp.SetPosition(P(*XY))
b.Add(fp)
for r in (90, 270):          # pads on the +x side, so the mouth faces -x
    fp.SetOrientationDegrees(r)
    p1 = [p for p in fp.Pads() if p.GetNumber() == "1"][0]
    if M(p1.GetPosition().x) > XY[0]:
        break
PIN = {"1": "+3V3", "2": "GND", "3": "/DISP_DIN", "4": "/DISP_CLK", "5": "/DISP_CS", "6": "/DISP_DC",
       "7": "/DISP_RST", "8": "/DISP_BUSY", "MP": "GND"}
for p in fp.Pads():
    p.SetNet(nets[PIN[p.GetNumber()]])
    if p.GetNumber() != "MP":
        print("pad", p.GetNumber(), M(p.GetPosition().x), M(p.GetPosition().y))
fp.Reference().SetPosition(P(XY[0] - 1.6, XY[1]))
fp.Reference().SetTextAngleDegrees(90)

# ---- routes. Rows under the socket body; 3V3, DIN, CLK and CS go down between J3 and the front mounting
# pad, DC, RST and BUSY right of it, then jog left under the pad; all run west under J3.
PX = 329.75                  # pad centres
W = 0.18
track("+3V3", "F", [(323.0, 106.0), (323.85, 106.0), (323.85, 93.15), (PX, 93.15)], 0.25)
track("/DISP_DIN", "F", [(PX, 94.15), (324.29, 94.15), (324.29, 106.8), (304.926, 106.8), (304.126, 106.0)], W)
track("/DISP_CLK", "F", [(PX, 94.65), (324.68, 94.65), (324.68, 107.19), (303.9376, 107.19), (303.5476, 106.8)], W)
track("/DISP_CS", "F", [(PX, 95.15), (325.07, 95.15), (325.07, 107.58), (302.8636, 107.58)], W)
track("/DISP_DC", "F", [(PX, 95.65), (327.95, 95.65), (327.95, 99.85), (325.6, 102.2), (325.6, 108.2),
                        (323.8355, 108.2)], W)
track("/DISP_RST", "F", [(PX, 96.15), (328.55, 96.15), (328.55, 99.85), (326.2, 102.2), (326.2, 108.8),
                         (309.5086, 108.8)], W)
# GND: the front mounting pad sits in a pocket of the pour, and pin 2 between two tracks; a via each
track("GND", "F", [(326.5, 98.55), (325.8, 97.3)], 0.3)
track("GND", "F", [(PX, 93.65), (331.0, 93.65)], 0.2)
via("GND", 325.8, 97.3)
via("GND", 331.0, 93.65)
track("/DISP_BUSY", "F", [(PX, 96.65), (PX, 97.1), (329.15, 97.7), (329.15, 99.85), (326.8, 102.2), (326.8, 109.4),
                          (302.2158, 109.4)], W)

b.BuildConnectivity()
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(PCB)
print("saved")
