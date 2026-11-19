# PETG prototype (case rev 3, clean model)

STL files for a home print of the case on a 256 mm bed (Bambu A1). The STL files themselves are kept out of git
(the knurled roller alone is ~48 MB); they are in the project's shared files and are regenerated from the Fusion model.

- The bottom shell, both top shells (A: sloped sides, B: flat sides with the G80 thumb slope; print one) and the
  accent ring are split at x = 44 mm from the board's centre: the left half is about 218 × 158 mm, the right 142 × 158.
  The cut misses every gasket bar, foot pocket, screw and the USB-C pocket.
- Joining: Ø1.9 holes, 8 mm deep each side, across the cut: push in 16 mm lengths of 1.75 mm filament as dowels, then
  glue the halves (CA or epoxy for PETG).
- No heat-set inserts in the PETG prototype: every screw hole is a pilot hole to screw straight into the PETG
  (Ø1.7 for M2, Ø2.5 for M3). The production case uses heat-set inserts (`../drawings/`).
- Gasket retainers (6; B2 and B3 have a notch at the back for a case screw): flat bars 3.1 mm thick, print them flat (countersinks down, no
  supports). Each screws up into its pocket in the top shell with 2 × M2×6 countersunk screws (Ø1.7 pilots in the
  PETG top shell; M2 inserts in production) and sits flush with the top shell's underside, above the ring. The top
  shell has a fitted pocket for each sock, so top shell, plate, socks and retainers go together as one
  sub-assembly; the ring and the bottom shell have no notches for them.
- Screws (countersunk machine screws, DIN 7991, straight into the PETG pilots): 4 × M3×10 (case front) and
  4 × M3×18 (case back), at the same x in both rows, heads 0.3 below the bottom face (Ø6.6 × 90° countersinks; if a
  head still stands proud on your print, run a 90° countersink bit by hand or scale the hole); 12 × M2×6 (retainers); 2 × M2×6 countersunk (encoder cover); M2×5 pan or cap head for the encoder module (2),
  screen frame (2) and USB-C board (2).
- Also printed whole: the encoder rail and the screen rail (on their flat base), the 6 retainers, encoder cover, screen tray, screen frame, LED guide (black), roller, power slider button.
- The files are in the keyboard's assembly position: lay each piece flat in the slicer (top shells face down,
  bottom shell on its base).

## Versions

Copies in the project's shared files carry a version tag (`...-v01.stl`), bumped on every new export of the set.

- v01 (2026-11-17): feet centred on the screw rows, 5 mm gasket room, plate R5.5, screen tray supported on all sides.
- v02 (2026-11-18): bottom shell cleaned (wall band rebuilt, no slivers; USB-C bay and cable slot with vertical walls, no ledges); the screen rail and the encoder rail are separate printed parts, screwed to the base (encoder rail 2 × M2×8, screen rail 3 × M2×12, countersunk from the top, into the base).
- v03 (2026-11-18): fitted to mainboard rev 1.3 and screen board rev 3.0 (PR #86): the screen tray has a window for the screen board (taped to the panel's back), the top shell a pocket for the board's front edge and LED row, and the LED light guide now sits on the board (s 19.55 up).
- v04 (2026-11-18): countersinks recut for DIN 7991 M3 heads (dk 6.0): Ø6.6 at the bottom face, 90°, so heads sit 0.3 below flush, with room for PLA shrink and for anodize or e-coat build-up. The back screws moved to the front row's x (-151.5, -46.47, 58.57, 163.6; even 105.03 pitch), and the back feet to the front feet's x (midway between the screws), so both rows line up. Back screws 2 and 3 now pass the B2 and B3 retainers: the top shell has a boss there for the insert and those two retainers have a notch. New: TopA, Bottom, Ring halves, retainers B1-F3, Ring DXF and the three STEPs.
- v05 (2026-11-18): bottom only. A 0.75 mm floor pocket (R1) under the battery JST PH, which hangs below mainboard rev 1.4 (PR #86) and touched the floor by 0.25 mm. New: Bottom halves and the Bottom STEP.
- Plate print v01 (2026-11-19): the R5.5 plate (1.51 thick, same as the FR4 plate, so MX switch clips hold) split in two to fit the A1 bed: left 214.5 x 130.7, right 116.8 x 130.7. The split steps through the webs between cutouts (x 42.5-55.25), at least 1.6 from any cutout; the halves just butt together, and the switches and PCB hold them in line. Print flat, 100% infill or 4+ walls. Files: Dachshund70-Plate-print-left-v01.stl, -right-v01.stl.
