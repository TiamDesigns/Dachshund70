import pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1])
for z in b.Zones(): z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[1]); print('refilled')
