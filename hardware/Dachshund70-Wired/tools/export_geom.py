# Dumps copper-relevant geometry of a board for the grid router (KiCad python).
import pcbnew, sys, json
b = pcbnew.LoadBoard(sys.argv[1])
mm = pcbnew.ToMM
out = {'pads': [], 'outline': [], 'holes': [], 'tracks': [], 'vias': []}
LAY = {pcbnew.F_Cu: 0, pcbnew.B_Cu: 1}
for f in b.GetFootprints():
    for p in f.Pads():
        q = p.GetPosition()
        rec = {'ref': f.GetReference(), 'num': p.GetNumber(), 'net': p.GetNetname(),
               'x': mm(q.x), 'y': mm(q.y), 'layers': [], 'poly': {}, 'drill': 0}
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH):
            ds = p.GetDrillSize(); rec['drill'] = mm(max(ds.x, ds.y))
            rec['npth'] = p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
        for L, li in LAY.items():
            if p.IsOnLayer(L) and p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH:
                ps = pcbnew.SHAPE_POLY_SET()
                p.TransformShapeToPolygon(ps, L, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_INSIDE)
                pts = []
                for i in range(ps.OutlineCount()):
                    o = ps.Outline(i)
                    pts.append([[mm(o.CPoint(j).x), mm(o.CPoint(j).y)] for j in range(o.PointCount())])
                rec['layers'].append(li); rec['poly'][li] = pts
        out['pads'].append(rec)
ps = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(ps, False)
for i in range(ps.OutlineCount()):
    o = ps.Outline(i)
    out['outline'].append([[mm(o.CPoint(j).x), mm(o.CPoint(j).y)] for j in range(o.PointCount())])
    for h in range(ps.HoleCount(i)):
        hh = ps.Hole(i, h)
        out['holes'].append([[mm(hh.CPoint(j).x), mm(hh.CPoint(j).y)] for j in range(hh.PointCount())])
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition(); out['vias'].append([mm(p.x), mm(p.y), mm(t.GetWidth(pcbnew.F_Cu)), t.GetNetname()])
    else:
        s, e = t.GetStart(), t.GetEnd()
        out['tracks'].append([mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()), LAY.get(t.GetLayer(), -1), t.GetNetname()])
json.dump(out, open(sys.argv[2], 'w'))
print('pads', len(out['pads']), 'outlines', len(out['outline']), 'holes', len(out['holes']), 'tracks', len(out['tracks']))
