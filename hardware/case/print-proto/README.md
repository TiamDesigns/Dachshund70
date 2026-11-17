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
- Gasket retainers (6, all the same part): flat bars 3.1 mm thick, print them flat (countersinks down, no
  supports). Each screws up into its pocket in the top shell with 2 × M2×8 countersunk screws (Ø1.7 pilots in the
  PETG top shell; M2 inserts in production) and sits flush with the top shell's underside, above the ring. The top
  shell has a fitted pocket for each sock, so top shell, plate, socks and retainers go together as one
  sub-assembly; the ring and the bottom shell have no notches for them.
- Screws (countersunk machine screws, DIN 7991, straight into the PETG pilots): 4 × M3×10 (case front) and
  4 × M3×18 (case back), all flush with the bottom; 12 × M2×8 (retainers); 2 × M2×6 countersunk (encoder cover); M2×5 pan or cap head for the encoder module (2),
  screen frame (2) and USB-C board (2).
- Also printed whole: the 6 retainers, encoder cover, screen tray, screen frame, LED guide (black), roller, power slider button.
- The files are in the keyboard's assembly position: lay each piece flat in the slicer (top shells face down,
  bottom shell on its base).
