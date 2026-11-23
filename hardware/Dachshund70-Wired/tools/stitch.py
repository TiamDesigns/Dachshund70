# One GND via per cut-off pour area. Finds the islands of the two GND pours, joins them through the existing GND
# vias and plated holes, and puts one via in each island that is still cut off, where it overlaps a joined island
# on the other layer. Repeats until nothing more can be joined, refilling each time.
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
F, T = pcbnew.FromMM, pcbnew.ToMM
gnd = b.FindNet('GND')
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)

def shrunk(ps, d):
    c = pcbnew.SHAPE_POLY_SET(ps)
    c.Deflate(F(d), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, F(0.01))
    return c

total = []
for it in range(12):
    zones = {z.GetLayer(): z for z in b.Zones()}
    fill = {L: zones[L].GetFilledPolysList(L) for L in LAYERS}
    nodes = [(L, i) for L in LAYERS for i in range(fill[L].OutlineCount())]
    parent = {n: n for n in nodes}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def where(L, p):
        for i in range(fill[L].OutlineCount()):
            if fill[L].Outline(i).PointInside(p, F(0.01)): return (L, i)
    links = [t.GetPosition() for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == gnd.GetNetCode()]
    links += [p.GetPosition() for f in b.GetFootprints() for p in f.Pads()
              if p.GetNetCode() == gnd.GetNetCode() and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    for p in links:
        a, c = where(pcbnew.F_Cu, p), where(pcbnew.B_Cu, p)
        if a and c: parent[find(a)] = find(c)
    # outline area as a size measure; the biggest group is the main pour
    area = {n: abs(fill[n[0]].Outline(n[1]).Area()) for n in nodes}
    groups = {}
    for n in nodes: groups.setdefault(find(n), []).append(n)
    main = max(groups, key=lambda g: sum(area[n] for n in groups[g]))
    safe = {L: shrunk(fill[L], 0.36) for L in LAYERS}
    added = 0
    for g, members in groups.items():
        if g == main: continue
        placed = False
        for (L, i) in sorted(members, key=lambda n: -area[n]):
            other = pcbnew.B_Cu if L == pcbnew.F_Cu else pcbnew.F_Cu
            ol = fill[L].Outline(i); bb = ol.BBox(); step = F(0.25)
            x = bb.GetLeft()
            while x < bb.GetRight() and not placed:
                y = bb.GetTop()
                while y < bb.GetBottom():
                    q = pcbnew.VECTOR2I(x, y)
                    if ol.PointInside(q) and safe[L].Contains(q) and safe[other].Contains(q):
                        w = where(other, q)
                        if w and find(w) == main:
                            v = pcbnew.PCB_VIA(b); v.SetPosition(q); v.SetDrill(F(0.3)); v.SetWidth(F(0.6))
                            v.SetNet(gnd); b.Add(v); total.append((round(T(q.x), 2), round(T(q.y), 2))); placed = True; break
                    y += step
                x += step
            if placed: break
        added += placed
    print('pass', it, 'islands', len(groups) - 1, 'vias added', added)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    if not added: break
b.Save(sys.argv[1])
print('total vias', len(total))
