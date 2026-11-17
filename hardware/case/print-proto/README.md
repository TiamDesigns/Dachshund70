# PETG prototype (case rev 3, clean model)

STL files for a home print of the case on a 256 mm bed (Bambu A1). The STL files themselves are kept out of git
(the knurled roller alone is ~48 MB); they are in the project's shared files and are regenerated from the Fusion model.

- The bottom shell, both top shells (A: sloped sides, B: flat sides with the G80 thumb slope; print one) and the
  accent ring are split at x = 44 mm from the board's centre: the left half is about 218 × 158 mm, the right 142 × 158.
  The cut misses every gasket bar, foot pocket, screw and the USB-C pocket.
- Joining: Ø1.9 holes, 8 mm deep each side, across the cut: push in 16 mm lengths of 1.75 mm filament as dowels, then
  glue the halves (CA or epoxy for PETG).
- No heat-set inserts (also in the production design): every screw goes straight into a pilot hole with a
  thread-forming screw for plastics (30° PT-type thread). Pilots: Ø2.5 for K30 (3 mm), Ø1.8 for K22 (2.2 mm).
- Gasket retainers (6: B1-B3, F1-F3) are plain flat bars, 5.7 mm thick: print them flat, no supports. They sit in
  1.0 mm pockets in the bottom shell and carry the socks from below. The walls that locate each sock on three sides
  (outside and both ends) are now part of the top shell and hang down round the socks; the top shell clamps the bars
  through those walls (0.05 clear), so the bars need no screws.
- Screws, three types (EJOT PT / Würth WN 54xx or any 30° plastic thread-forming equivalent):
  8 × K30×10 countersunk, Torx (case: front flush, back in Ø6.2 × 9.7 counterbores so all eight are the same);
  2 × K22×6 countersunk (encoder cover); 6 × K22×6 pan head (encoder module 2, screen frame 2, USB-C board 2).
- Also printed whole: the 6 retainers, encoder cover, screen tray, screen frame, LED guide (black), roller, power slider button.
- The files are in the keyboard's assembly position: lay each piece flat in the slicer (top shells face down,
  bottom shell on its base).
