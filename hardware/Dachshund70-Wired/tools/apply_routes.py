# Adds router output (tracks, vias) to a board. usage: apply_routes.py board routes.json [--clear]
import pcbnew, sys, json
b = pcbnew.LoadBoard(sys.argv[1]); r = json.load(open(sys.argv[2]))
if '--clear' in sys.argv:
    for t in list(b.GetTracks()): b.Remove(t)
nets = b.GetNetsByName()
F = pcbnew.FromMM
for x1, y1, x2, y2, w, L, n in r['tracks']:
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(F(x1), F(y1))); t.SetEnd(pcbnew.VECTOR2I(F(x2), F(y2)))
    t.SetWidth(F(w)); t.SetLayer(pcbnew.F_Cu if L == 0 else pcbnew.B_Cu)
    t.SetNet(nets[n]); b.Add(t)
for x, y, n in r['vias']:
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(F(x), F(y))); v.SetDrill(F(0.3)); v.SetWidth(F(0.6))
    v.SetNet(nets[n]); b.Add(v)
b.Save(sys.argv[1])
print('tracks', len(r['tracks']), 'vias', len(r['vias']))
