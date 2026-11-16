"""Move the status LEDs D3-D7 (and their capacitors C14-C18) to a new pitch, carrying their routing along.

Run with KiCad's Python from the repo root:

    "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70/move_leds.py

Case rev 3 (2026-11-16): 7.5 mm pitch centred under the screen window (local x 151.309,
KiCad 329.559), was 8.525. Every track end and via in the LED strip (y 124-136, x >= 309)
moves with the LED nearest to it, so the chain keeps its pattern and stays connected;
anything outside the strip (U4, C19, the long LED_VDD and LED_D5 runs) stays put.
Zones are refilled afterwards. Run once: it reads the current positions.
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "Dachshund70.kicad_pcb")
CENTRE = 329.559
PITCH = 7.5
LEDS = ("D3", "D4", "D5", "D6", "D7")
CAPS = ("C14", "C15", "C16", "C17", "C18")
STRIP = (309.0, 124.0, 1e9, 136.0)   # x0, y0, x1, y1 (mm)

mm, FromMM = pcbnew.ToMM, pcbnew.FromMM


def main():
    b = pcbnew.LoadBoard(BOARD)
    old = [mm(b.FindFootprintByReference(r).GetPosition().x) for r in LEDS]
    new = [CENTRE + PITCH * (k - 2) for k in range(5)]
    dx = [n - o for n, o in zip(new, old)]

    def shift_for(x, y):
        if not (STRIP[0] <= x <= STRIP[2] and STRIP[1] <= y <= STRIP[3]):
            return 0.0
        k = min(range(5), key=lambda i: abs(x - old[i]))
        return dx[k]

    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            p = t.GetPosition()
            d = shift_for(mm(p.x), mm(p.y))
            if d:
                t.SetPosition(pcbnew.VECTOR2I(p.x + FromMM(d), p.y))
        else:
            for get, put in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
                p = get()
                d = shift_for(mm(p.x), mm(p.y))
                if d:
                    put(pcbnew.VECTOR2I(p.x + FromMM(d), p.y))
    for refs in (LEDS, CAPS):
        for r, d in zip(refs, dx):
            fp = b.FindFootprintByReference(r)
            p = fp.GetPosition()
            fp.SetPosition(pcbnew.VECTOR2I(p.x + FromMM(d), p.y))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(BOARD, b)
    for r, o, n in zip(LEDS, old, new):
        print(f"{r}: x {o:.3f} -> {n:.3f}")


if __name__ == "__main__":
    main()
