# Removes vias that DRC reports as dangling (connected on one layer only). usage: rmvias.py board drc.json
import pcbnew, sys, json
b = pcbnew.LoadBoard(sys.argv[1]); d = json.load(open(sys.argv[2]))
pos = [(i['pos']['x'], i['pos']['y']) for x in d['violations'] if x['type'] == 'via_dangling' for i in x['items']]
n = 0
for t in list(b.GetTracks()):
    if t.GetClass() == 'PCB_VIA':
        p = t.GetPosition(); x, y = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        if any(abs(x - a) < 0.01 and abs(y - c) < 0.01 for a, c in pos): b.Remove(t); n += 1
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[1]); print('removed vias', n)
