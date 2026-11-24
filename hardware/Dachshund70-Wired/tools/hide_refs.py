# Hides the reference text of parts too crowded for it (column passives, stabilisers); the fab layer keeps them.
import pcbnew, sys
HIDE = set(sys.argv[2].split(','))
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for f in b.GetFootprints():
    if f.GetReference() in HIDE: f.Reference().SetVisible(False); n += 1
b.Save(sys.argv[1]); print('hidden', n)
