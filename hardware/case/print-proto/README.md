# PETG prototype (case rev 3, Fusion v82)

STL files for a home print of the case on a 256 mm bed (Bambu A1). The STL files themselves are kept out of git
(the knurled roller alone is ~48 MB); they are in the project's shared files and are regenerated from the Fusion model.

- The bottom shell, both top shells (A: sloped sides, B: flat sides with the G80 thumb slope; print one) and the
  accent ring are split at x = 44 mm from the board's centre: the left half is about 218 × 158 mm, the right 142 × 158.
  The cut misses every gasket bar, foot pocket, screw and the USB-C pocket.
- Joining: Ø1.9 holes, 8 mm deep each side, across the cut: push in 16 mm lengths of 1.75 mm filament as dowels, then
  glue the halves (CA or epoxy for PETG).
- No heat-set inserts: every screw hole is a pilot hole to screw straight into the PETG. Ø1.7 for M2, Ø2.5 for M3.
- Screws: 8 × M3 × 10 countersunk (DIN 7991) for the case; 2 × M2 × 6 countersunk for the encoder cover;
  4 × M2 × 5 pan head (screen frame and tray: 2; USB-C board: 2, 3.0 mm pilots).
- Also printed whole: encoder cover, screen tray, screen frame, LED guide (black), roller, power slider button.
- The files are in the keyboard's assembly position: lay each piece flat in the slicer (top shells face down,
  bottom shell on its base).
