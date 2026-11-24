# Builds the e-paper adapter board from its netlist: outline, footprints with nets, placement.
# usage: epd_sync.py netlist board place.json
import pcbnew, re, sys, json
NET, BRD, PL = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
STOCK = 'C:/Program Files/KiCad/10.0/share/kicad/footprints/'
def tok(s):
    out = []; st = [out]
    for m in re.finditer(r'\(|\)|"((?:[^"\\]|\\.)*)"|[^\s()"]+', s):
        t = m.group(0)
        if t == '(': n = []; st[-1].append(n); st.append(n)
        elif t == ')': st.pop()
        elif t.startswith('"'): st[-1].append(m.group(1))
        else: st[-1].append(t)
    return out[0]
T = tok(open(NET, encoding='utf8').read())
def find(l, k): return [x for x in l if isinstance(x, list) and x and x[0] == k]
comps = {}
for c in find(find(T, 'components')[0], 'comp'):
    d = {x[0]: x[1:] for x in c[1:] if isinstance(x, list)}
    flds = {}
    for fl in find(c, 'fields'):
        for f in find(fl, 'field'): flds[f[1][1]] = f[2] if len(f) > 2 else ''
    comps[d['ref'][0]] = dict(value=d['value'][0], fp=d['footprint'][0], ts=d['tstamps'][0], fields=flds)
pads = {}
for n in find(find(T, 'nets')[0], 'net'):
    name = find(n, 'name')[0][1]
    for nd in find(n, 'node'): pads[(find(nd, 'ref')[0][1], find(nd, 'pin')[0][1])] = name
b = pcbnew.BOARD()
F = pcbnew.FromMM
x0, y0, x1, y1, r = PL['outline']
def seg(a, c):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(F(0.05))
    s.SetStart(pcbnew.VECTOR2I(F(a[0]), F(a[1]))); s.SetEnd(pcbnew.VECTOR2I(F(c[0]), F(c[1]))); b.Add(s)
def arc(c, st, ang):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(F(0.05))
    s.SetCenter(pcbnew.VECTOR2I(F(c[0]), F(c[1]))); s.SetStart(pcbnew.VECTOR2I(F(st[0]), F(st[1])))
    s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(ang, pcbnew.DEGREES_T)); b.Add(s)
seg((x0 + r, y0), (x1 - r, y0)); seg((x1, y0 + r), (x1, y1 - r)); seg((x1 - r, y1), (x0 + r, y1)); seg((x0, y1 - r), (x0, y0 + r))
arc((x1 - r, y0 + r), (x1 - r, y0), 90); arc((x1 - r, y1 - r), (x1, y1 - r), 90)
arc((x0 + r, y1 - r), (x0 + r, y1), 90); arc((x0 + r, y0 + r), (x0, y0 + r), 90)
nets = {}
def getnet(name):
    if name not in nets:
        ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); nets[name] = ni
    return nets[name]
miss = []
for ref, c in comps.items():
    lib, name = c['fp'].split(':')
    fp = pcbnew.FootprintLoad(STOCK + lib + '.pretty', name)
    fp.SetReference(ref); fp.SetValue(c['value']); fp.SetFPIDAsString(c['fp']); fp.SetPath(pcbnew.KIID_PATH('/' + c['ts']))
    for k, v in c['fields'].items():
        if k in ('LCSC', 'MPN', 'Description', 'Datasheet'): fp.SetField(k, v)
    for fld in fp.GetFields():
        if fld.GetName() in ('LCSC', 'MPN', 'Description', 'Datasheet'): fld.SetVisible(False)
    fp.Value().SetVisible(False)
    b.Add(fp)
    for p in fp.Pads():
        nm = pads.get((ref, p.GetNumber()))
        if nm: p.SetNet(getnet(nm))
    if ref in PL['parts']:
        x, y, a = PL['parts'][ref]
        fp.SetPosition(pcbnew.VECTOR2I(F(x), F(y))); fp.SetOrientationDegrees(a)
    else: miss.append(ref)
ds = b.GetDesignSettings()
b.Save(BRD)
print('fps', len(list(b.GetFootprints())), 'nets', len(nets), 'unplaced', miss)
