"""Ground vias where they're needed, not on a grid across the whole board.

Two-layer boards pour GND on both sides. A pour is cut into islands by the
tracks of other nets, and an island only belongs to the ground net once a via,
a through-hole pad or a track joins it to the rest. This module adds the
fewest vias that do that: one per island (or GND pad) that would otherwise be
cut off, picked from a list of candidate places that are known to fit. Islands
smaller than MIN_ISLAND_MM2 with no pad on them get no via; the zone filler
drops them.

As a library (gen_screen.py uses it):

    import gnd_vias
    added = gnd_vias.join_ground(board, candidates)   # candidates: [(x_mm, y_mm), ...]

On an existing board, run with KiCad 10's own Python from the repo root:

    "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/gnd_vias.py hardware/Dachshund70/Dachshund70.kicad_pcb

(one board per run).

That takes every GND via that isn't the end of a GND track (the stitching),
removes it, puts back only the ones that join an island to ground, refills the
pours and saves the board. Check it with
`kicad-cli pcb drc --schematic-parity --severity-all <board>.kicad_pcb` afterwards.
"""

import sys

import pcbnew

MIN_ISLAND_MM2 = 4.0
VIA_SIZE = 0.6
VIA_DRILL = 0.3


class _Sets:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, a):
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def join(self, a, b):
        self.p[self.find(a)] = self.find(b)


def _cu_layers(item):
    return [layer for layer in (pcbnew.F_Cu, pcbnew.B_Cu) if item.IsOnLayer(layer)]


def _make_via(board, net, x, y, size=VIA_SIZE, drill=VIA_DRILL):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
    v.SetWidth(pcbnew.FromMM(size))
    v.SetDrill(pcbnew.FromMM(drill))
    v.SetNet(net)
    return v


def join_ground(board, candidates, net_name="GND", size=VIA_SIZE, drill=VIA_DRILL):
    """Add GND vias from `candidates` ((x, y) in mm, or internal units if ints > 1e5) until every GND
    pad and every pour island of at least MIN_ISLAND_MM2 is joined to the main ground. Returns the vias
    added. The board's pours are left filled."""
    net = board.FindNet(net_name)
    code = net.GetNetCode()
    zones = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetCode() == code]
    modes = [z.GetIslandRemovalMode() for z in zones]
    for z in zones:
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    # nodes: pour islands, GND pads, GND tracks and the GND vias already on the board
    nodes = []   # (kind, layers, shape per layer, bbox, area mm2)
    for z in zones:
        for layer in _cu_layers(z):
            fill = z.GetFilledPolysList(layer)
            for i in range(fill.OutlineCount()):
                isl = fill.Subset(i, i + 1)
                bb = isl.BBox()
                nodes.append(("island", [layer], {layer: isl}, bb, isl.Area() / 1e12))
    for f in board.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() == code:
                ls = _cu_layers(p)
                if ls:
                    nodes.append(("pad", ls, {l: p.GetEffectiveShape(l) for l in ls}, p.GetBoundingBox(), 0))
    for t in board.GetTracks():
        if t.GetNetCode() == code:
            ls = _cu_layers(t)
            nodes.append(("track", ls, {l: t.GetEffectiveShape(l) for l in ls}, t.GetBoundingBox(), 0))

    def touches(a, b):
        if not a[3].Intersects(b[3]):
            return False
        for layer in a[1]:
            if layer in b[2]:
                sa, sb = a[2][layer], b[2][layer]
                if a[0] == "island":
                    if sa.Collide(sb, 0):
                        return True
                elif sb.Collide(sa, 0):
                    return True
        return False

    sets = _Sets(len(nodes))
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if nodes[i][0] == "island" and nodes[j][0] == "island":
                continue   # islands of one zone never touch; F and B islands only meet through a via
            if touches(nodes[i], nodes[j]):
                sets.join(i, j)

    def pads_in(root):
        return sum(1 for k, n in enumerate(nodes) if n[0] == "pad" and sets.find(k) == root)

    def wanted(k):
        n = nodes[k]
        return n[0] != "island" or n[4] >= MIN_ISLAND_MM2

    roots = {sets.find(k) for k in range(len(nodes))}
    main = max(roots, key=pads_in)

    def to_iu(c):
        x, y = c
        if isinstance(x, int) and abs(x) > 100000:
            return x, y
        return pcbnew.FromMM(x), pcbnew.FromMM(y)

    cands = []
    for c in candidates:
        x, y = to_iu(c)
        v = _make_via(board, net, x, y, size, drill)
        probe = ("via", [pcbnew.F_Cu, pcbnew.B_Cu],
                 {l: v.GetEffectiveShape(l) for l in (pcbnew.F_Cu, pcbnew.B_Cu)}, v.GetBoundingBox(), 0)
        hit = []
        for k, n in enumerate(nodes):
            if n[0] == "island":
                if n[3].Contains(v.GetPosition()) and n[2][n[1][0]].Contains(v.GetPosition()):
                    hit.append(k)
            elif touches(probe, n):
                hit.append(k)
        if hit:
            cands.append((v, hit))

    added = []
    changed = True
    while changed:
        changed = False
        main = sets.find(main)
        for v, hit in cands:
            if v in added:
                continue
            rs = {sets.find(k) for k in hit}
            if main not in rs:
                continue
            gain = [k for k in hit if sets.find(k) != main and wanted(k)]
            if not gain:
                continue
            for k in hit:
                sets.join(k, main)
            main = sets.find(main)
            board.Add(v)
            added.append(v)
            changed = True

    for z, m in zip(zones, modes):
        z.SetIslandRemovalMode(m)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    left = [k for k in range(len(nodes)) if nodes[k][0] == "pad" and sets.find(k) != sets.find(main)]
    if left:
        print("warning: %d GND pads aren't joined to the main ground by a candidate via" % len(left))
    return added


def thin(path):
    board = pcbnew.LoadBoard(path)
    code = board.FindNet("GND").GetNetCode()
    tracks = [t for t in board.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetCode() == code]
    ends = {(p.x, p.y) for t in tracks for p in (t.GetStart(), t.GetEnd())}
    free = [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetCode() == code
            and (t.GetPosition().x, t.GetPosition().y) not in ends]
    sizes = {(v.GetWidth(pcbnew.F_Cu), v.GetDrill()) for v in free}
    size, drill = max(sizes) if sizes else (pcbnew.FromMM(VIA_SIZE), pcbnew.FromMM(VIA_DRILL))
    cands = [(v.GetPosition().x, v.GetPosition().y) for v in free]
    for v in free:
        board.Remove(v)
    added = join_ground(board, cands, size=pcbnew.ToMM(size), drill=pcbnew.ToMM(drill))
    board.Save(path)
    print("%s: %d stitching vias, %d kept" % (path, len(free), len(added)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: gnd_vias.py <board>.kicad_pcb   (one board per run: pcbnew can't load a second)")
    thin(sys.argv[1])
