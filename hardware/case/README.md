# Dachshund70 case (rev 2)

A gasket-mount aluminium case at 4°, with a brass weight in the bottom, an accent ring at the seam, a
2.13" e-paper screen and five status LEDs beside the knob, and a rotary knob on the right end. **The case is
designed in Fusion 360, and the Fusion model is the source of truth**, not the STEP files. The native
archive is `fusion/Dachshund70-Case-rev2.f3d`; the STEP, DXF and render files here are exports of it.

The first design (a CadQuery script, `gen_case.py`, at 7°) is gone: its geometry, files and renders were
replaced by this one. Git history has it.

![Top three-quarter view](renders/01-top-three-quarter.png)

## Files

| Folder | What |
| --- | --- |
| `fusion/Dachshund70-Case-rev2.f3d` | The Fusion archive: the full parametric model, with the boards, plate, battery, screen, knob and both keycap sets. Open it in Fusion to change anything |
| `fusion/scripts/` | The Python scripts that build the model and export these files (see "Rebuilding") |
| `step/` | STEP files, all in one frame (below), so they import on top of each other |
| `dxf/` | Flat DXFs for the ring (laser) and the weight's engraving (engraver) |
| `renders/` | Views of the model |
| `BOM.md` | Every part: material, finish, process, quantity, screws, gaskets, feet, the slider button |

### `step/`

| File | What |
| --- | --- |
| `Dachshund70-Case-Top.step` | Top block (aluminium): the bezel, key opening, sock pockets and the retainer openings under them with the retainers' ear pockets and M2 taps, screen window and drop-in opening, LED holes and guide pocket, the encoder cover's opening, its front boss, back-ear pocket and two M2 taps, screw taps |
| `Dachshund70-Case-Bottom.step` | Bottom block (aluminium): the stepped floor, battery bay, USB-C opening, slider channel and lever slot, weight window and ledge pocket, rail pockets, screw holes |
| `Dachshund70-Case-Ring.step` | The accent ring (1.6 mm sheet) |
| `Dachshund70-Case-Weight.step` | The brass weight with its engraving |
| `Dachshund70-Case-Knob.step` | The knurled knob |
| `Dachshund70-Case-Encoder-Cover.step` | The cover over the encoder: the v33 hood (a Ø19.2 half-cylinder on the knob's axis); the encoder module screws to its foot, and one M2 on each side, under the plate, holds it to the top block |
| `Dachshund70-Case-Gasket-Retainer.step` | One of the six identical gasket retainers with its two screw ears (the one at the back-left nub, at its assembly position) |
| `Dachshund70-Case-Slider-Button.step` | The power slider button on the switch's lever (printed or POM) |
| `Dachshund70-Case-LED-Guide.step` | The light guide over the five status LEDs (3D printed) |
| `Dachshund70-Case-Assembly.step` | Everything: boards, plate, battery, screen, the keycaps with the 6.25 u spacebar, the case parts, screws and rails (64 MB, so import it with care) |
| `Dachshund70-Keycaps.step` | The keycap set with the split bottom row (1.25 u, 2.75 u and 2.25 u keys), in the assembly's frame |
| `Dachshund70-Keycaps-6.25u.step` | The keycap set with the 6.25 u spacebar (this is the one inside the assembly), in the same frame |

Every part is at its assembly position. The frame is Fusion's world frame: the desk is Z = 0, X runs along the
keyboard (X = 0 is the board's centre, KiCad x 178.25), Y points to the back and Z is up. The board and
the plate sit in it tilted 4° about X. In the board's own frame, KiCad x = local x + 178.25 and
KiCad y = 99.55 − local y.

### `dxf/`

- `Dachshund70-Case-Ring.dxf`: the ring flattened and seen from above, in mm at true size, with closed
  outlines only: layer `RING_OUTLINE` (the outside) and `RING_HOLES` (the opening, 8 screw holes and 12 joint
  slots). Lines, arcs and circles, no splines. Origin at the board's centre.
- `Dachshund70-Weight-Engraving.dxf`: the engraving as seen from below (the way it reads), in mm, origin at
  the centre of the weight's face: `PAW` (the paw print: four toe beans over a main pad, five closed outlines) and
  `TEXT` ("Dachshund70" in Fredoka SemiBold, with the counters of a, d, D and 0 as inner loops). Closed polylines.
  Every recess is 0.3 deep with a flat (bead-blasted) floor.

## Key dimensions

- Typing angle: 4°, built into the case; the bottom is flat. The walls of every part are square to the plate
  (parallel to its normal), so the end, front and back faces lean with the board.
- Footprint: 347.9 × 155.2 mm in the plate's plane (X −173.8 to 174.1). Heights above the desk: the bottom
  block is 15.1 tall (Z 0 to 15.1), the top block 24.5 (Z 4.6 to 29.1 at the knob's hump); the bezel's top edge is
  9.9 above the desk at the front and 20.8 at the back.
- Accent ring: 1.6 mm sheet in a slot between the blocks, at local z −2.2 to −0.6 in the board's frame (its edge
  shows as a thin gold line round the case). Outline 347.9 × 155.2, opening 320 × 122.6.
- Mounting: the plate sits on twelve silicone gasket socks (8 × 5 × 5 mm) on its prongs, in pockets in the top
  block. Each nub is a 24 mm neck with two 2.8 arms (prongs at ±27.25 from the nub's centre, the socks reaching 5.9
  past the plate edge). Under each nub the whole region (neck, arms and both socks) is one opening from below to the
  sock tops (z 8.1), 64.3 × 5.3, with 1.25 or more round the arms and 4.0 or more of aluminium to the bezel's outside,
  and a 6061 gasket retainer (64.1 × 5.2 × 4.1, R1.1 corners, 0.1 clear in its R1.0 pocket) fills it from the ring up
  to the sock floor (local z 3.5): it is the floor under both socks and the nub, it seats against the top block's step
  at 3.5 and the ring clamps it. All six are the same part. Each is screwed up into the top block with two M2 × 8
  countersunk screws (DIN 965) through two ears on its outer side at ±18.0 from its centre (R2.8 lobes 2.0 thick, local z
  −0.6 to 1.4, R1.0 where they meet the bar, in pockets 0.1 clear), the heads flush with its underside so the ring still
  seats flat. The taps (Ø1.6) are drilled to z 9.4 (the tip + 2), 5.9 of thread, with 1.7 or more of metal above them. 4 × M3 × 12 along the front (x ±50.5, ±151.5) and 4 × M3 × 20 along the back (x −151.5, −61.35, +39.5, +151.5: the middle two moved
  off ±50.5 for the longer retainers)
  (countersunk, from below) hold the blocks together through the ring; their taps are drilled to the screw tip + 3
  and threaded to the tip + 1.5.
- Ring joint: twelve slots 12.2 × 1.7 in the ring for the blocks' 11.8 × 1.3 tabs (0.2 a side). The back-centre pair
  sits at x −45, clear of the daughterboard's opening.
- Floor: stepped, one world-horizontal step per switch row under the keys (3.0 at the front to 7.9 at the back);
  flat and hollow under the screen and knob.
- Battery bay: x 122.7 to 160, y 2.0 to 61.3 (its back wall ends at the cavity wall, so there's no lip), floor at Z 1.0,
  R3 corners and the cavity's own R5.75 at the back right, for an EEMB LP803450 (52.0 × 34.5 × 8.3 plus a 4.5
  protection board) laid flat, its long side front to back, at x 123.6 to 158.1, y 2.92 to 59.42 (0.9 of play at the
  sides for the R3 corners: foam-tape it). The floor stays at 1.0. J1 (the JST-SH on the mainboard's underside) is
  now on the front sidebar at KiCad (333.5, 118.5), 17.6 from the cell; J5 at (329.8, 49.54) is 2.0 over it.
- Weight: brass, face 185.0 × 76.1 (R4 corners, y −40.4 to 35.7: from the number row's top edge to the Shift row's
  bottom edge, local y 35.74 and −40.46, square to the desk), flange 216.0 × 80.9 (R5, y −42.9 to 38.0), 87.5 cm³
  (87.4 cm³ with the paw print and the M3 countersinks: brass 743 g, Ti-6Al-4V 387 g). It drops in from inside through a window in the floor; its top sits 0.1 under the
  floor: sloped like the floor in front of y −21.0 (3.8 at the face's front edge, 3.7 thick there), then 5.2, 6.5 and
  7.8 at the steps. The flange rests on ledges 1.5 under that: sloped at the front (z 2.2 to 3.68), then 3.68, 5.01
  and 6.34 (the risers 0.1 behind the flange's steps, R1.0 where they meet the sides); 2.2 of floor under the front
  ledge. Four M3 countersunk screws (DIN 965, Ø5.5 heads) from inside, at the corners of the flange's ends, heads
  flush with the weight's top in 90° countersinks Ø5.7 to Ø3.4 that leave a 0.35 land in the 1.5 flange: M3 × 6 at the
  back corners (±102.5, 33.0) on the 6.34 ledge, 4.5 of thread (1.5 × d), and M3 × 5 at (±102.5, 13.0), the front of
  the 5.01 ledge, 3.5 of thread. The taps are Ø2.5 with flat bottoms at z 1.04 and 1.0 (the screw tips + 0.8 and + 0.5;
  use a bottoming tap), so 1.0 of floor stays under them, and 2.8 or more of metal round them. The front corners can't
  take an M3: from the desk to the weight's top is under 4 mm there (5.2 up to y −2), so the front pair sits as far
  forward as a 3.5 mm thread allows. No screw heads show underneath. The engraving: a paw print (four toe beans over
  a main pad, 46.1 × 43.2, in the dog's old place: bottom at y −16.6, centred in x) above "Dachshund70" (10.5 tall),
  all 0.3 deep with flat floors; the gaps between the pads are 2.2 or more.
- Knob and cover: Ø19.2 × 15.1 knurled knob on the encoder's 20 mm D shaft (D-bore 6.0 with the flat at 4.5). Above
  the plate the cover is the v33 hood, its outside unchanged: a Ø19.2 half-cylinder on the knob's axis (local y 50.03,
  z 13.4) from x 130.245 to 143.505 (0.15 from the knob), open at the knob end, flat sides down to the plate's top
  (z 6.6), an R1.5 round on the closed end and small notches at the bottom of the front and back walls for the
  PEC12R's frame ears. Inside: 2.6 walls, a flat ceiling at z 21.0 (2.0 under the crown) and, over the body's top
  corners (9.17 from the axis), an arc coaxial with the hood at R9.33, so the wall there is 0.27 (0.15 clear, the most a
  Ø19.2 hood allows). The cavity (x 132.245 to the open end, 14.0 wide, R0.5 at its closed end) and the notches run
  straight through from below: no undercuts. Below the plate's top it is the v35 cover: walls tangent to the knob down
  to the encoder module's PCB, frame-ear pockets, and a foot (x 127.15 to 132.2, up to z 7.5 outside the hood) that
  takes the module's two M2 × 5 socket-head screws (DIN 912, Ø3.8 × 2.0 heads; taps Ø1.6 through, R1.8 bosses, on the
  module's holes). Their heads stand in the mainboard's Ø4.2 lobe (the front one, 0.15 clear) and its corner notch (the
  back one, 0.73 clear), 0.2 below the board; the cell is 4.3 under the front one, J5 2.9 beside it. The cover screws up
  into the top block with one M2 × 8 countersunk screw (DIN 965) on each side of the axis, through flat ears (heads
  flush in 90° countersinks Ø4.0 to a Ø2.2 clearance): the front one at (131.2, 35.8), an R2.7 ear z 2.9 to 4.8, into a
  Ø5.0 boss that hangs from the top block through the plate's encoder notch; the back one at (139.25, 64.4), 2.6 thick
  (z 2.2 to 4.8), in a pocket in the back wall. Since round 5 the front ear, its screw and the boss are 1.5, 2.9 and 1.7
  from the plate in plan wherever it floats (±1.0 on the socks), and the ear is 1.39 over the mainboard. Both
  taps are Ø1.6 drilled to z 12.2 (1.0 under the top face), 5.4 of thread. Clearances: 1.7 to the keycaps pressed 4.0 (3.2 at rest), 0.15 to the plate, knob and encoder body,
  0.36 to its frame ears. The top block's opening follows the hood (0.25 round it, R1.75 corners at the closed end).
- Screen: GoodDisplay GDEY0213B74 on end beside the knob, behind a window with a 45° frame (a 0.3 land at the
  glass, no knife edge); the glass and its driver board drop in from below through an opening the glass's size
  (29.8 × 59.8, R1.0). Five LEDs under it in an evenly spaced row, with a printed light guide (below).
- Power switch: a PCM12 slide switch on the USB-C daughterboard (battery on/off). A printed (or POM) pill button,
  10.7 × 6.0 and 0.85 thick, flush with the back face, slides 1.5 in a channel beside the USB-C with the lead-in's own
  outline (12.6 × 6.4, R3.2 ends, 1.0 deep, R0.25 rim), on the USB-C's centre height (z 9.23): 0.2 clear top and bottom,
  0.15 off the floor. A stem on its back (2.5 × 1.8, 0.83 under the centre line, at the lever's height) goes through a
  4.4 × 2.2 slot (R0.5 corners) and holds the lever in a 1.4 × 0.89 pocket. The button hides the slot at both ends of
  its travel. No undercuts: channel and slot are plain pockets cut from the back face.
- USB-C: an opening in the back face with a 12.6 × 6.4 lead-in recess 1.0 deep (2.0 of aluminium under the ring), and
  the daughterboard on a ledge (2 M3 taps). Since round 5 the board sits 1.0 lower: its underside at z 6.0 above the desk
  (was 7.0), the port's centre at z 9.23 (was 10.23); the opening, lead-in, ledge, leg relief and taps moved with it
  (1.2 of floor under the taps). The pocket is open from above over the board (x −21.4 to 33.4), so its two M3 × 6
  screws go in before the ring and the top block.
- Feet: two rubber rails near the front and back edges, in 1.0 mm pockets: 300 × 5.8 × 2.0 at the front, 269.4 × 5.8 × 2.0
  at the back (it stops at x 119.4, its pocket 3.0 short of the battery bay).
- LEDs and light guide: the LEDs (D3 to D7, reverse-mount SK6812MINI-E) span the Sharp screen's window at an even
  8.525 pitch: KiCad x 312.51, 321.035, 329.56, 338.085 and 346.61, y 130.5 (world x 134.26, 142.785, 151.31,
  159.835 and 168.36). D6 and D7 sit on a small tab of the mainboard (to x 349.3) under the widened sidebar, and the
  plate has an edge notch for D6 instead of a window. The roof's five Ø3 light holes are on the same axes, square to the plate, so each hole is straight over its
  LED. The guide is opaque black resin, its block 30.6 × 6.05 × 5.0 in the roof pocket and five 3.7 square spigots in
  the plate's 4 × 4 windows (0.15 clear, down to the PCB's top). Each channel is one straight Ø2.1 bore from its LED to
  its hole, so the walls are 0.8 at the spigots and 1.9 or more in the block; its pocket has R1.0 corners and the guide
  R1.15. The plate and mainboard float, so the block's underside is at z 7.8 and the spigots end at z 2.8 (1.2 over the
  plate and the PCB at rest). The LEDs sit in their 3.4 PCB cutouts in the mainboard STEP: body 2.8 × 3.2, 0.3 / 0.1 clear, top 0.75 under
  the PCB's top face, pins on the bottom pads.
- Inside corners: every inside vertical corner is radiused (R1.0 where a part sits 0.3 clear, R0.64 to R0.8 in the
  daughterboard pocket and leg relief, R3 in the battery bay).
- Part list: [BOM.md](BOM.md).

## Rebuilding and re-exporting

The scripts in `fusion/scripts/` drive Fusion's Python API. Each starts with a `REPO` path to edit (the repo
root, with a trailing slash). Run them from Fusion's Scripts dialog, or through the Fusion MCP's `script`
execute (each defines `run(_context)`).

- `build_case2.py`: clears the timeline and rebuilds every case part from parameters (the dict at the top, the
  plate outline's numbers and the floor steps). `place_models.py` and `make_models.py` import the board STEP
  files from `hardware/step/` and make the stand-ins (battery, screen, knob); `post_build.py` (`stage1()`,
  then `stage2()`, in one call after the build) imports the keycap files, builds the two spacebar sets and
  places everything at the 4° tilt. Don't create timeline items, appearances or planes after `stage2()`.
  The keycap sets it imports are `step/Dachshund70-Keycaps*.step`; they come from this model (the old CadQuery
  `keycaps.py` is gone), so a rebuild needs them in the repo as they are. The rebuild path from these scripts
  has not been re-run end to end since the files were moved here: the `.f3d` is the dependable copy.
  The November 2026 fixes, the second round (retainer ears, encoder cover v35, the 76.1 mm weight), the third (the
  current mainboard, the v33 hood on the v35 mounting) and the fourth (M2 cover screws, socket-head module screws, M3
  weight screws at the corners, the paw print, the LEDs centred under the screen with straight guide channels, and the
  plate and mainboard PCB bodies from that board change) and the fifth (v37: the 24 mm-neck plate and the 64.1 mm
  retainers with their openings, the back M3 screws at x −61.35 and +39.5, the cover's front mount at x 131.2, the
  daughterboard 1.0 lower, the slider button and its channel, the light guide clear of the floating plate, J5 and the
  module's J1 moved, the encoder cable stand-in) were made in the `.f3d` as features at the end of the timeline;
  their numbers are mirrored at the top of `build_case2.py` (`COVER_V35`, `COVER_HOOD`, `RETAINER_EARS`, `ROUND5`) and in its
  weight section. `build_case2.py` mirrors
  their numbers where that was simple: the ring slots and moved tab, the M3 tap depth, the rails, the battery bay's size
  and the cell's place, the lead-in, the switch slot and cap, the weight (face, flange, M3 corner screws, the paw print),
  the screen drop-in opening and window land, and no module posts. Only in the `.f3d`: the gasket retainers, their
  ears and screws and their openings, the encoder cover (dome, foot, ears, cavity) and its opening, front boss, back
  pocket and taps in the top block, the weight's sloped front part and ledge, the light guide's channels, the
  daughterboard opening, the knob's D-bore, the R3/R5.75 bay corners, the weight ledges' corner radii, and the
  inside-corner fillets.
- `export_all.py`: writes the part STEP files, the assembly, both keycap sets and the `.f3d`.
- `export_dxf.py`: writes the two DXFs.
- `check_a.py`: the clash check. `run_checks(log)` tests the plate, every board part, the battery, the screen and both
  keycap sets (at rest and pressed 4.0 along the plate's normal) against the case parts, the case parts against each
  other and the screws against the boards and caps; the plate, the mainboard (it hangs from the switches) and the caps
  are also checked floating 1.0 up and down on the socks (caps at rest + 1.0, pressed 4.0 − 1.0), and
  `plate_clearance(log)` gives each part's gap to the plate's swept volume. Known hit: the encoder shaft in the knob's
  D-bore (the model's shaft is round). Round 5 (v37): no other hits against the case. Board against board, floating:
  the mainboard at +1.0 hits the encoder module's PCB (0.29 apart at rest, see BOM.md's open points), its J4 header
  model touches the e-paper driver (no header is fitted), and at −1.0 a SOT-23-5 and the battery plug touch the cell.
- `shots.py`, `underside.py`: the camera helper and an underside view used while designing.
- Placement: the boards, battery, screen and keycaps are placed by setting occurrence transforms, which Fusion doesn't
  keep when a timeline item is added (they go back to where they were imported). After adding features, put them back
  (the plate is now its own `Dachshund70-Plate` occurrence, from `hardware/step/Dachshund70-Plate.step`, at local
  z 4.995) before checking or exporting, and capture them (Position > Capture, or `design.snapshots.add()`). The
  mainboard occurrence is still the first import (named `Dachshund60F-Assembly` in Fusion; the spacebar sets use its
  stabilizer and switch components, so deleting it deletes them too): its PCB body was replaced by the current one
  with a base feature (twice: after #67, and for the LED move in 1611d2c), and J1, J5, D3 to D7 and the 0402 capacitors
  that moved with them (C14 to C18 and one more) were moved to their current places. The plate's body was swapped the
  same way for 1611d2c's plate (its LED windows moved).
- `dog_proto.py` + `dog_outline.txt`: the old dachshund engraving's control points and a quick PIL preview of it (the
  weight now has the paw print; its control points are `PAW_PAD` and `PAW_TOES` in `build_case2.py`).

After a board changes: run `python hardware/export_step.py` for the new board STEPs, rebuild (or move the
parts in Fusion), then re-export. The model's imported board occurrences are the ones to replace.

Not checked against real parts: the gasket retainers' clamp height (4.1, no squeeze allowance), sock squeeze, the plug lead-in against real cables, the screw-in stabilizers'
clearance, the slider button's travel and fit on the PCM12 lever (and the PCM12's travel, taken as 1.5), the screen's real sizes (the panel's from
GoodDisplay's drawing; the picture's position along it is an estimate), the light guide against the plate's
LED windows, and the radio's range through the aluminium over the antenna.

## Display

A bare 2.13" e-paper panel (GoodDisplay GDEY0213B74, SSD1680, 250 × 122, black on white) standing on end
beside the knob: 29.2 × 59.2 mm, with a 23.7 × 48.6 mm picture. In portrait that's 120 × 248 pixels, 12 × 15
cells of text with the 10 × 16 font. Build the firmware with
`-DEXTRA_DTC_OVERLAY_FILE=displays/eink-2in13-v4-portrait.overlay`, which turns the picture in software.

- Driver: the panel's boost circuit is on our own screen board (`hardware/Dachshund70-Screen/`, 21.0 × 34.0 ×
  0.8 mm, KiCad x 311.0 to 332.0, y 69.2 to 103.2), taped flat to the panel's back with its parts facing down.
  The panel's tail plugs into its J1. The Fusion model still has Adafruit's eInk Breakout Friend (#4224, about
  34.7 × 21.5 mm) in that place, so swap in `hardware/step/Dachshund70-Screen.step`.
- Mount: the panel sits in a locating frame under the roof, behind a window with a 45° bevel, held by thin
  double-sided tape (0.2 mm, such as 3M 9448A or tesa 4965) on its border. Check that the screen board's parts
  clear the plate, which floats ±1 mm.
- Cable: one 8-way 0.5 mm FFC with contacts on the same side at both ends. It runs from the mainboard's J4
  (an FH12-8S socket at KiCad (327.9, 94.9), mouth facing −x) up through the plate's screen notch, and loops back
  into the screen board's J2, which sits straight above J4. Set its length from the model. J4's pins are
  unchanged: 1 3V3, 2 GND, 3 DIN, 4 CLK, 5 CS, 6 DC, 7 RST, 8 BUSY.
- Refresh: e-paper keeps its picture with no power, and a refresh takes about a second, so the firmware redraws
  at most every 3 s (`CONFIG_KB_SCREEN_EPD_MIN_INTERVAL_MS`). That suits the layer, lock, battery and
  connection status it shows.
- The screen board stays clear of the radio module's antenna (KiCad x > 333, y 67–79 mm); only the panel's
  glass reaches over the antenna's left end.
- Sizes are nominal: measure your parts and correct the screen pocket in the Fusion model (`build_case2.py`)
  before machining. If the text comes out upside down, set `rotation = <270>` in the overlay.
- Other screens: Pimoroni's 1.12" 128 × 128 SH1107 OLED (overlay `oled-sh1107-128x128`, 8 text rows) fits the
  sidebar; OLED modules use J4 pins 1–4 (3V3, GND, DIN = SDA, CLK = SCL), now through an FFC adapter. They
  need a different pocket.

## Making it

- Top and bottom blocks: 6061-T6 aluminium, 3-axis CNC with a ball-end mill for the slopes, bead-blasted and
  anodised. The ring is laser-cut from 1.6 mm sheet from the DXF and anodised in the accent colour. The weight
  is brass (C360) with a polished face (743 g); steel, aluminium and Ti-6Al-4V weigh 686, 236 and 387 g.
- Setups: the top block is machined from its bottom face (the ring plane, square to the plate) and its top; the
  bottom block from the top, the bottom and the back face (USB-C and switch openings). The bottom block's cavity
  walls are square to the plate, so in a level setup its back wall leans 4° over the floor (about 0.7 mm over its
  height): cut it in a 4° tilted setup or with a 4° tapered cutter. The window's 45° frame leaves conical corners
  from a V cutter.
- Screws are tapped, not inserts. For a printed prototype open the holes to 4.2 mm for M3 × 4 heat-set
  inserts and print the blocks in pieces (each is 347.9 mm long).
- Antenna: the top block over the antenna stays aluminium. The ground plane under the keys and the metal over
  the antenna cost some range; a test with the real case is still needed, and a polycarbonate window in the
  roof over the antenna is the fallback.
- Battery: it stays more than 50 mm from the radio module; next to or under the antenna it would detune it.
