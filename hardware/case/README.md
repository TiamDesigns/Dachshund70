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
| `BOM.md` | Every part: material, finish, process, quantity, screws, gaskets, feet, the switch cap |

### `step/`

| File | What |
| --- | --- |
| `Dachshund70-Case-Top.step` | Top block (aluminium): the bezel, key opening, sock pockets and the retainer openings under them, screen window and drop-in opening, LED holes and guide pocket, encoder cutout, the cover's ear pocket and taps, screw taps |
| `Dachshund70-Case-Bottom.step` | Bottom block (aluminium): the stepped floor, battery bay, USB-C opening, power switch slot, weight window and ledge pocket, rail pockets, screw holes |
| `Dachshund70-Case-Ring.step` | The accent ring (1.6 mm sheet) |
| `Dachshund70-Case-Weight.step` | The brass weight with its engraving |
| `Dachshund70-Case-Knob.step` | The knurled knob |
| `Dachshund70-Case-Encoder-Cover.step` | The cover over the encoder, tangent to the knob; the encoder module screws to its foot, and it screws to the top block |
| `Dachshund70-Case-Gasket-Retainer.step` | One of the six identical gasket retainers (the one at the back-left nub, at its assembly position) |
| `Dachshund70-Case-Switch-Cap.step` | The cap on the power switch's lever (printed or POM) |
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
  the centre of the weight's face: `DOG_SILHOUETTE` (the recess's outline), `DOG_DETAIL` (the ear, chest, leg
  grooves and eye) and `TEXT` ("Dachshund70" in Fredoka SemiBold, with the counters of a, d, D and 0 as inner loops). Closed
  polylines. The silhouette is 0.3 deep (flat floor), the grooves and eye 0.5 deep and the text 0.3.

## Key dimensions

- Typing angle: 4°, built into the case; the bottom is flat. The walls of every part are square to the plate
  (parallel to its normal), so the end, front and back faces lean with the board.
- Footprint: 347.9 × 155.2 mm in the plate's plane (X −173.8 to 174.1). Heights above the desk: the bottom
  block is 15.1 tall (Z 0 to 15.1), the top block 24.5 (Z 4.6 to 29.1 at the knob's hump); the bezel's top edge is
  9.9 above the desk at the front and 20.8 at the back.
- Accent ring: 1.6 mm sheet in a slot between the blocks, at local z −2.2 to −0.6 in the board's frame (its edge
  shows as a thin gold line round the case). Outline 347.9 × 155.2, opening 320 × 122.6.
- Mounting: the plate sits on twelve silicone gasket socks (8 × 5 × 5 mm) on its prongs, in pockets in the top
  block. Under each nub the whole pocket region (both socks and the nub's clearance) is open from below, 44.3 × 4.65,
  and a 6061 gasket retainer (44.1 × 4.55 × 4.1, R1.1 corners, 0.1 clear in its R1.0 pocket) fills it from the ring up
  to the sock floor (local z 3.5): it is the floor under both socks and the nub, it seats against the top block's step
  at 3.5 and the ring clamps it. All six are the same part. 4 × M3 × 12 along the front and 4 × M3 × 20 along the back
  (countersunk, from below) hold the blocks together through the ring; their taps are drilled to the screw tip + 3
  and threaded to the tip + 1.5.
- Ring joint: twelve slots 12.2 × 1.7 in the ring for the blocks' 11.8 × 1.3 tabs (0.2 a side). The back-centre pair
  sits at x −45, clear of the daughterboard's opening.
- Floor: stepped, one world-horizontal step per switch row under the keys (3.0 at the front to 7.9 at the back);
  flat and hollow under the screen and knob.
- Battery bay: x 122.7 to 160, y 2.0 to 61.3 (its back wall ends at the cavity wall, so there's no lip), floor at Z 1.0,
  R3 corners and the cavity's own R5.75 at the back right, for an EEMB LP803450 (52.0 × 34.5 × 8.3 plus a 4.5
  protection board) laid flat, its long side front to back, at x 123.6 to 158.1, y 2.92 to 59.42 (0.9 of play at the
  sides for the R3 corners: foam-tape it). The floor stays at 1.0: raised to 1.5 the cell would touch J1 and J2. The
  cell's top (Z 9.5) already overlaps J1 (the JST-SH on the mainboard's underside, Z 8.8 to 9.4 over it) by about
  0.7 mm, as it did before; a 7.3 mm cell or J1 moved off the bay fixes that.
- Weight: brass, face 185.0 × 40.0 (R4 corners, y −16.5 to 23.5), flange 216.0 × 53.0 (R5, y −19 to 34), 51.1 cm³
  (brass 435 g, Ti-6Al-4V 227 g). It drops in from inside through a window in the floor; its flange rests on stepped
  ledges at z 3.68, 5.01 and 6.34 (the risers 0.1 behind the flange's steps, R1.0 where they meet the sides) and its
  top sits 0.1 under the floor. Four M2 × 4 countersunk screws (DIN 965) from inside, at (±103.5, 2.5) and
  (±103.5, 30.5), in countersinks that leave a 0.6 land in the 1.5 flange, into M2 taps drilled Ø1.6 to the tip + 1.0
  (1.0 and 2.4 of floor under the drill point). No screw heads show underneath. The dog and the text are scaled by
  40/30.6; the grooves stay 0.4 wide.
- Knob and cover: Ø19.2 × 15.1 knurled knob on the encoder's 20 mm D shaft (D-bore 6.0 with the flat at 4.5). The
  cover is 19.2 wide with R7 top corners, tangent to the knob at its sides and top (a round dome can't keep 1 mm of
  wall over the encoder body's corners, 9.18 from the axis). The encoder module screws up into the cover's foot
  (2 × M2 × 5 through the module's holes; the front tap sits 0.08 toward the plate's bay so its wall keeps 0.15 to
  the plate), and the cover screws up into the top block through its rear ear (2 × M2 × 6 into taps 4.0 deep, 1.2
  under the top face). The old M2 posts in the top block are gone.
- Screen: GoodDisplay GDEY0213B74 on end beside the knob, behind a window with a 45° frame (a 0.3 land at the
  glass, no knife edge); the glass and its driver board drop in from below through an opening the glass's size
  (29.8 × 59.8, R1.0). Five LEDs under it in an evenly spaced row, with a printed light guide (below).
- Power switch: a PCM12 slide switch on the USB-C daughterboard, its lever carrying a printed (or POM) 3.6 × 2.6 cap
  (0.8 walls round the lever pocket) that rides in a 5.5 × 3.0 stadium slot in the back face (1.5 travel, 0.2 clear).
- USB-C: an opening in the back face with a 12.6 × 6.4 lead-in recess 1.0 deep (6.4 keeps 1.0 of aluminium under the
  ring), and the daughterboard on a ledge (2 M3 taps). The pocket is open from above over the board (x −21.4 to 33.4),
  so its two M3 × 6 screws go in before the ring and the top block.
- Feet: two rubber rails near the front and back edges, in 1.0 mm pockets: 300 × 5.8 × 2.0 at the front, 269.4 × 5.8 × 2.0
  at the back (it stops at x 119.4, its pocket 3.0 short of the battery bay).
- LED light guide: opaque black resin. Each channel (Ø2.3) runs straight up from its LED through a spigot in the plate's
  4 × 4 window (3.7 square, 0.15 clear, down to 0.09 over the PCB), then one S bend between z 6.9 and 10.9 to its roof
  hole; walls at least 0.7 at the spigots and 1.15 at the ends, no breakouts. Its pocket has R1.0 corners and the
  guide R1.15. The LEDs (D3 to D7, reverse-mount SK6812MINI-E) sit in their 3.4 PCB cutouts in the mainboard STEP:
  body 2.8 × 3.2, 0.3 / 0.1 clear, top 0.75 under the PCB's top face, pins on the bottom pads.
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
  The November 2026 fixes were made in the `.f3d` as features at the end of the timeline. `build_case2.py` mirrors
  their numbers where that was simple: the ring slots and moved tab, the M3 tap depth, the rails, the battery bay's size
  and the cell's place, the lead-in, the switch slot and cap, the weight (face, flange, M2 screws, engraving scale),
  the screen drop-in opening and window land, and no module posts. Only in the `.f3d`: the gasket retainers and
  their openings, the encoder cover's new shape (foot, rear ear, cavity, ear pockets) and its ear pocket and taps in
  the top block, the light guide's channels, the daughterboard opening, the knob's D-bore, the R3/R5.75 bay corners,
  the weight ledges' corner radii, and the inside-corner fillets.
- `export_all.py`: writes the part STEP files, the assembly, both keycap sets and the `.f3d`.
- `export_dxf.py`: writes the two DXFs.
- `shots.py`, `check_a.py`, `underside.py`: the camera helper and the clearance checks used while designing.
- `dog_proto.py` + `dog_outline.txt`: the dachshund outline's control points and a quick PIL preview of it.

After a board changes: run `python hardware/export_step.py` for the new board STEPs, rebuild (or move the
parts in Fusion), then re-export. The model's imported board occurrences are the ones to replace.

Not checked against real parts: the gasket retainers' clamp height (4.1, no squeeze allowance), sock squeeze, the plug lead-in against real cables, the screw-in stabilizers'
clearance, the switch cap's travel and fit on the PCM12 lever, the screen's real sizes (the panel's from
GoodDisplay's drawing; the picture's position along it is an estimate), the light guide against the plate's
LED windows, and the radio's range through the aluminium over the antenna.

## Display

A bare 2.13" e-paper panel (GoodDisplay GDEY0213B74, SSD1680, 250 × 122, black on white) standing on end
beside the knob: 29.2 × 59.2 mm, with a 23.7 × 48.6 mm picture. In portrait that's 120 × 248 pixels, 12 × 15
cells of text with the 10 × 16 font. Build the firmware with
`-DEXTRA_DTC_OVERLAY_FILE=displays/eink-2in13-v4-portrait.overlay`, which turns the picture in software.

- Driver: the panel needs a driver board. The model has Adafruit's eInk Breakout Friend (#4224, about
  34.7 × 21.5 mm) taped flat to the panel's back, its parts facing down. Waveshare's 2.13" V4 module (the same
  panel on a board) runs the same firmware, but its board is too big for the sidebar.
- Mount: the panel sits in a locating frame under the roof, behind a window with a 45° bevel, held by thin
  double-sided tape (0.2 mm, such as 3M 9448A or tesa 4965) on its border. The driver board's parts clear the
  plate by about 0.3 mm in the model, so check that with the real board.
- Wiring, from J4's holes (no header, since JLC doesn't fit it) to the Friend: 1 3V3 → VIN, 2 GND → GND, 3 DIN →
  MOSI, 4 CLK → SCK, 5 CS → ECS, 6 DC → D/C, 7 RST → RST, 8 BUSY → BUSY. The Friend's SRAM and SD card selects
  (SRCS, SDCS) stay unconnected; check that the board pulls them high. Route the wires flat along the plate's
  J4 slot to the board's front edge, about 80 mm long so the top block can lie upside down next to the board
  while you fit the screen.
- Refresh: e-paper keeps its picture with no power, and a refresh takes about a second, so the firmware redraws
  at most every 3 s (`CONFIG_KB_SCREEN_EPD_MIN_INTERVAL_MS`). That suits the layer, lock, battery and
  connection status it shows.
- The driver board stays clear of the radio module's antenna (KiCad x > 333, y 67–79 mm); only the panel's
  glass reaches over the antenna's left end.
- Sizes are nominal: measure your parts and correct the screen pocket in the Fusion model (`build_case2.py`)
  before machining. If the text comes out upside down, set `rotation = <270>` in the overlay.
- Other screens: Pimoroni's 1.12" 128 × 128 SH1107 OLED (overlay `oled-sh1107-128x128`, 8 text rows) fits the
  sidebar; OLED modules use J4 pins 1–4 (3V3, GND, DIN = SDA, CLK = SCL). They need a different pocket.

## Making it

- Top and bottom blocks: 6061-T6 aluminium, 3-axis CNC with a ball-end mill for the slopes, bead-blasted and
  anodised. The ring is laser-cut from 1.6 mm sheet from the DXF and anodised in the accent colour. The weight
  is brass (C360) with a polished face (435 g); steel, aluminium and Ti-6Al-4V weigh 401, 138 and 227 g.
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
