# Adds GND pours on both copper layers (whole board), fills them and saves.
import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
F = pcbnew.FromMM
bb = b.GetBoardEdgesBoundingBox()
gnd = b.FindNet('GND')
for z in list(b.Zones()):
    b.Remove(z)
for L in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b)
    z.SetLayer(L); z.SetNet(gnd)
    o = z.Outline(); o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(x, y)
    z.SetLocalClearance(F(0.2)); z.SetMinThickness(F(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(F(0.2)); z.SetThermalReliefSpokeWidth(F(0.25))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print('zones', len(list(b.Zones())))
