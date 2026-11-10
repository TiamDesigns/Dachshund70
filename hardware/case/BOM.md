# Dachshund70 case BOM (rev 2, with the November 2026 fixes and the second round)

Everything that goes into the case and holds it together, for the default layout (split spacebar). The PCBs
are line items only; their parts are in each board's own BOM (`hardware/<board>/`). Sizes are in mm, from the
Fusion model. Masses use 2.70 g/cm³ for aluminium, 8.50 for C360 brass, 4.43 for Ti-6Al-4V, 1.2 for the printed
resin and 7.9 for stainless screws. Finish and anodise colours are Tiam's choice.

## Made parts

| Qty | Part | Material | Size, volume | Process | File |
|---:|---|---|---|---|---|
| 1 | Top block | 6061-T6 aluminium | 347.9 × 155.2 × 24.5, 157.1 cm³ (424 g) | CNC 3-axis (5-axis or a ball-end for the slopes), bead-blast, anodise | `step/Dachshund70-Case-Top.step` |
| 1 | Bottom block | 6061-T6 aluminium | 347.9 × 155.2 × 15.1, 257.5 cm³ (695 g) | CNC, bead-blast, anodise | `step/Dachshund70-Case-Bottom.step` |
| 1 | Accent ring | 6061 or 5052 aluminium sheet, 1.6 thick | outline 347.9 × 155.2, opening 320 × 122.6, 23.0 cm³ (62 g) | Laser cut from flat sheet, anodise in the accent colour | `step/Dachshund70-Case-Ring.step`, `dxf/Dachshund70-Case-Ring.dxf` |
| 6 | Gasket retainer | 6061-T6 aluminium | 64.1 × 5.2 × 4.1 bar, R1.1 corners, with two screw ears (64.1 × 9.9 overall), 1.43 cm³ (3.9 g each, 23.2 g the six) | CNC, anodise | `step/Dachshund70-Case-Gasket-Retainer.step` |
| 1 | Weight | C360 brass (Ti-6Al-4V, steel or aluminium possible) | face 185.0 × 76.1 (R4), flange 216.0 × 80.9 (R5), 3.7 (sloped) / 5.1 / 6.4 / 7.7 thick, 87.4 cm³: brass 743 g, Ti-6Al-4V 387 g, steel 686 g, aluminium 236 g | CNC; polished face with a 0.4 chamfer round the edge; a paw print (four toe beans over a main pad, 46.1 × 43.2) 0.3 deep (flat floors bead-blasted), "Dachshund70" text 0.3 deep (Fredoka SemiBold, SIL OFL, 10.5 tall, under the paw); four M3 countersinks in the flange's ends | `step/Dachshund70-Case-Weight.step`, `dxf/Dachshund70-Weight-Engraving.dxf` |
| 1 | Knob | 6061 aluminium | Ø19.2 × 15.1, 3.73 cm³ (10.1 g) | CNC, form-knurl, anodise | `step/Dachshund70-Case-Knob.step` |
| 1 | Encoder cover | 6061 aluminium | Ø19.2 hood 13.3 long (the v33 shape) on a foot, 16.9 × 35.6 × 20.8 with its two ears, 2.04 cm³ (5.5 g) | CNC, anodise in the accent colour | `step/Dachshund70-Case-Encoder-Cover.step` |
| 1 | Power slider button | 3D-printed resin (or machined POM) | 10.7 × 6.0 pill (R3.0 ends), 0.85 thick, with a 2.5 × 1.8 stem on its back, 0.053 cm³ | SLA print, or mill in POM | `step/Dachshund70-Case-Slider-Button.step` |
| 1 | LED light guide | Opaque black SLA or SLS resin | 30.6 × 6.05 × 8.85, 0.89 cm³ (1.1 g) | 3D print | `step/Dachshund70-Case-LED-Guide.step` |

Notes on the made parts:

- Gasket retainers: one under each of the plate's six nubs (front and back), all the same part. Each fills the
  opening under its nub's pocket region (64.3 × 5.3, R1.0 corners, open from below, up to the sock tops at z 8.1:
  the 24 mm neck, both arms and both socks, which reach 5.9 past the plate edge, with 1.25 or more round the arms;
  4.0 or more of aluminium between it and the bezel's outside) from the ring's top up to the
  sock floor (local z 3.5): its top is the floor under both socks and the nub's clearance, it seats against the top
  block's step at 3.5, and the ring clamps it from below. 0.1 clear at its ends and outer side; its inner side is flush
  with the top block's pocket wall, 0.75 from the PCB's edge. Two ears on its outer side at ±18.0 from its centre
  (R2.8, 2.0 thick, flush with its underside, R1.0 where they meet the bar, with room for that in the pockets) each take an M2 × 8 countersunk screw up
  into the top block (90° countersink 4.0, head flush, 1.2 land; tap Ø1.6 drilled to the tip + 2, 5.9 of thread). The
  ears sit in pockets 0.1 clear, well away from the socks, the nub arms, the ring's slots and the M3 screws. With the
  24 mm necks the back middle and right bars reached the back M3 screws at x −50.5 and +50.5, so those two moved to
  x −61.35 and +39.5 (between the bars, clear of the daughterboard pocket and the slider).
- Weight: its face runs from the number row's top edge to the Shift row's bottom edge (world y −40.4 to 35.7). It
  drops in from inside through a window in the bottom block, its 1.5 mm flange resting on a ledge pocket (sloped at the
  front with the floor, z 2.2 to 3.68, then 3.68, 5.01 and 6.34, matching the floor's steps; the risers sit 0.1 behind
  the flange's steps, R1.0 in their corners and on the flange's), and sits 0.1 under the floor. The ledges keep 2.2 of
  floor under them at the front and over 7 of wall to the rails' pockets, the front screws and the battery bay. Four M3
  countersunk screws (DIN 965) from inside, at the corners of the flange's ends, in 90° countersinks 5.7 → 3.4 (1.15
  deep, a 0.35 land left in the 1.5 flange), heads flush with the weight's top: M3 × 6 at the back corners (x ±102.5,
  y 33.0) on the 6.34 ledge, 4.5 of thread, and M3 × 5 at x ±102.5, y 13.0 (the front of the 5.01 ledge), 3.5 of
  thread. Taps Ø2.5 with flat bottoms at the screw tip + 0.8 / + 0.5 (z 1.04 / 1.0, so 1.0 of floor under them; use a
  bottoming tap), 2.8 or more of metal round them. The front corners have under 4 mm from the desk to the weight's top,
  too little for an M3, so the front pair sits as far forward as 3.5 of thread allows. No screw heads show on the bottom.
- Knob: D-bore 6.0 with the flat at 4.5 (across the flat) for the PEC12R's 6 mm D shaft, blind, ending 0.3 past the
  shaft's tip, behind a Ø7.6 × 4.9 hub bore; push-on (rotary-broach the D, or wire-EDM it before the blind end is
  faced). The knurl is to be form-knurled, diamond, about 0.8 pitch (the model shows 64 flutes and 14 rings).
- Encoder cover: above the plate it is the v33 hood, unchanged outside: a Ø19.2 half-cylinder on the knob's axis
  (local y 50.03, z 13.4) from x 130.245 to 143.505, open at the knob end, with flat sides down to the plate's top
  (local z 6.6), an R1.5 round on the closed end and small notches at the bottom of the front and back walls (for the
  PEC12R's frame ears). Inside: walls 2.6, a flat ceiling at z 21.0 (2.0 under the crown), and an arc coaxial with the
  hood at R9.33 over the body's top corners, which are 9.17 from the axis: the wall there is 0.27, the most any Ø19.2
  hood can keep at 0.15 clearance. The cavity is straight from below (x 132.245 to the open end, 14.0 wide, R0.5 at
  its closed end) and the notches run through to the bottom (R0.5 corners), so there are no undercuts. Below the
  plate's top it is the v35 cover: walls tangent to the knob down to the module's PCB, frame-ear pockets, the foot that
  takes the module's two M2 screws (taps Ø1.6 through, R1.8 bosses on the module's holes, R0.8 where they meet the
  foot), and one flat ear each side of the axis with an M2 × 8 countersunk screw (DIN 965; 90° countersink 4.0 → Ø2.2
  clearance) up into the top block: the front one (R2.7 ear at local (131.2, 35.8), z 2.9 to 4.8, 1.9 thick) into a Ø5.0
  boss that hangs through the plate's notch (1.7 of metal round the tap); ear, screw and boss are 1.5, 2.9 and 1.7 from
  the plate in plan wherever it floats (±1.0), and the ear is 1.39 over the mainboard; the back one (2.6 thick, z 2.2
  to 4.8) in a pocket in the back wall; taps
  Ø1.6 drilled to the tip + 2 (1.0 under the top face), 5.4 of thread. The top
  block's opening follows the hood 0.25 clear (R1.75 corners at the closed end). Clearances: 0.15 to the knob and the
  encoder body, 0.36 to the frame ears, 0.15 beside the plate's web and module reliefs (the foot and its two module-screw
  bosses, which the plate's edge passes sideways as it floats), 1.7 to the keycaps pressed 4.0 (3.2 at rest). Setups: from
  below (cavity, notches, ear pockets, taps), the outside (hood and sides) and the ears' undersides.
- Slider button: a pill 10.7 × 6.0 (R3.0 ends), 0.85 thick, flush with the back face (R0.3 round its face), in a
  channel with the USB-C lead-in's outline (12.6 × 6.4, R3.2 ends, 1.0 deep square to the back face, R0.25 rim) on the
  USB-C's centre height (z 9.23 above the desk): 0.2 clear top and bottom, 0.15 off the floor, 1.5 travel plus 0.2 at
  each end. A stem 2.5 × 1.8 (R0.5 edges) on its back, 0.83 below the button's centre line, passes through a 4.4 × 2.2
  slot (R0.5 corners) in the channel's floor and takes the PCM12's lever in a pocket 1.4 × 0.89 (0.05 a side, 0.7 of
  engagement), a light press fit plus a drop of cyanoacrylate, like the old cap. The button covers the slot at both ends
  of its travel (2.4 or more of overlap). Channel and slot are plain pockets from the back face (a Ø6 end mill and
  a Ø1.0 one), no undercuts; the button is held by the lever only, as the cap was.
- Light guide: one straight Ø2.1 channel per LED (five), from the LED (D3 to D7, KiCad x 311.75 to 333.75 at a 5.5
  pitch, centred under the screen) through a 3.7 square spigot in the plate's 4 × 4 window (0.15 clear) to its roof
  hole, which is on the same axis. The plate and the mainboard float on the socks, so the block's underside is at z 7.8
  (1.2 over the plate) and the spigots stop at z 2.8 (1.2 over the PCB): 0.2 left at +1.0, and the plate's window
  still sleeves the spigot at −1.0. Walls 0.8 at the spigots and 1.9 or more in the block, corners R1.15 in an R1.0 pocket.
- Ring: every wall square to the sheet; 8 × Ø3.4 screw holes and 12 joint slots 12.2 × 1.7 (the blocks' tabs are
  11.8 × 1.3: 0.2 a side). The back-centre slot is at x −45.

## Bought parts

| Qty | Part | Notes |
|---:|---|---|
| 4 | M3 × 12 countersunk, DIN 7991, stainless | Bottom block to top block, along the front, flush with the bottom face; 6.0 of the screw in the top block, taps threaded 7.5 and drilled 9.0 deep from its bottom face (tip + 1.5 / tip + 3) |
| 4 | M3 × 20 countersunk, DIN 7991, stainless | The same along the back (the block is 23 mm tall there), at x −151.5, −61.35, +39.5 and +151.5; 4.75 in the top block, taps threaded 6.25 and drilled 7.75 deep |
| 2 | M3 × 6 countersunk, DIN 965, stainless | The weight's back corners, from inside, into the 6.34 ledge's taps (4.5 of thread) |
| 2 | M3 × 5 countersunk, DIN 965, stainless | The weight's front pair (y 13.0), from inside, into the 5.01 ledge's taps (3.5 of thread) |
| 12 | M2 × 8 countersunk, DIN 965, stainless | The six gasket retainers to the top block, two each, up through their ears, heads flush with the retainers' underside (drive them before the ring goes on) |
| 2 | M2 × 8 countersunk, DIN 965, stainless | The encoder cover to the top block, one each side of the axis, up through its ears into the front boss and the back wall (5.4 of thread) |
| 2 | M3 × 6 button head (ISO 7380) | USB-C daughterboard into the two taps on its ledge (x −16.5 and 19.0, the ledge at z 6.0 above the desk, 1.2 of floor under the taps); the pocket is open from above, so drive them before the ring and the top block go on |
| 2 | M2 × 5 socket head cap screw, DIN 912 / ISO 4762, stainless | Encoder module to the cover's foot, up through the module's holes. Their Ø3.8 × 2.0 heads sit in the mainboard's corner notch (the back one, 0.73 clear) and its Ø4.2 lobe (the front one, 0.15 clear), 0.2 below the board: the cell is 4.3 under the front one and J5 2.9 beside it |
| 1 | Rubber or TPU rail with adhesive, 300 × 5.8 × 2.0 | Near the front edge, in a 1.0 pocket, 1.0 proud |
| 1 | Rubber or TPU rail with adhesive, 269.4 × 5.8 × 2.0 | Near the back edge, x −150 to 119.4 (it stops 3.0 short of the battery bay), in a 1.0 pocket, 1.0 proud |
| 12 | Gasket socks, silicone, 8 × 5 × 5 outside, pocket 6.5 × 2.8 × 1.2 | Moulded (stock). One on each of the plate's prongs, lying along the plate edge, on the gasket retainers |
| 1 | LiPo cell EEMB LP803450, 52.0 × 34.5 × 8.3 plus a 4.5 protection board | Flat in the battery bay (x 122.7 to 160, y 2.0 to 61.3, floor 1.0, R3 corners), long side front to back, held with foam tape (0.9 of play at its sides). J1 is now on the front sidebar, clear of it. JST-PH polarity varies between vendors: check it against J2 |
| 1 | E-paper panel, GoodDisplay GDEY0213B74 (2.13", 250 × 122) with driver board | Drops in from below, taped under the roof's window |
| 1 | Double-sided tape, 0.2 mm (3M 9448A or tesa 4965) | Screen glass to the roof |
| 1 | JST-SH 4-pin cable, about 100 mm, both ends plugged | USB-C daughterboard to J1 |
| 1 | Power slide switch PCM12SMTR (on the USB-C daughterboard) | Its lever takes the slider button |
| 1 | JST-SH 5-pin cable, about 25 mm overall, reversed (pin 1 to pin 5), parallel wires, both latches the same side | Encoder module J1 to the mainboard's J5, straight under the module (SHR-05V-S housings, SSH-003T contacts, 30–32 AWG); trim the encoder's pins to 0.5 or less underneath |
| 79 | MX-style hot-swap switches | 77 with the 6.25 u spacebar |
| 5 | 2 u screw-in (PCB-mount) stabilizers | Backspace, Enter, left Shift, the 2.75 u space and the 2.25 u right Mod. With the 6.25 u spacebar: one 6.25 u stabilizer for the space, plus Backspace, Enter and left Shift |
| 1 | Keycap set, Cherry profile | Needs the split spacebar's 1.25 u Mod, 2.75 u space and 2.25 u Mod (or a 6.25 u space) |

Open points from the November 2026 check (board changes, not case changes):

- Plate (done in this round): the encoder notch now runs forward to KiCad y 67.25 between x 305.25 and 322.25 for the
  cover's walls and its front boss, and the two module reliefs are Ø3.9 on the module's real holes
  (`hardware/Dachshund70-Plate/`).
- Mainboard (done): the case model now has the current mainboard (after #67: the corner notch at KiCad x 304 to 326.4,
  y 39 to 57 with its Ø4.2 lobe at (306.6, 57.8), J1 at (333.5, 118.5) on the front sidebar, J5 at (329.8, 46.5)). The
  module's M2 socket heads clear it (0.15 in the lobe, 0.73 in the notch), and J1 is 17.6 from the cell.
- Round 5 (done): J5 moved to (329.8, 49.54) and the module's J1 turned to face it, so the cable runs straight under
  the module (it couldn't plug in before); the plate's notch runs forward to y 104.5 from x 305.25 to the right edge.
- Still open (round 5's clash check, plate and mainboard floating ±1.0 on the socks): the encoder module (fixed to the
  cover) overhangs the mainboard by 3.5 mm at KiCad y 57 to 60.5, only 0.29 above it, so the mainboard hits it at
  +1.0. The module can't be trimmed (the PEC12R's front tab pad reaches y 57.4) or raised (the knob and hood are 0.15
  apart). Fix on the mainboard: deepen its notch to y 60.9 or more (the bus of tracks along y 57.7 to 61.6 moves). And
  at −1.0 a SOT-23-5 (0.78 above the cell at rest) and the JST-PH battery plug touch the cell: a thinner cell or
  parts moved off the cell's footprint.

## Masses

| Part | Mass |
|---|---:|
| Top block | 424 g |
| Bottom block | 695 g |
| Accent ring | 62 g |
| Knob | 10.1 g |
| Encoder cover | 5.5 g |
| Gasket retainers (6) | 23.2 g |
| LED guide, slider button (resin) | 1.1 g |
| Rails (rubber, about 1.2 g/cm³) | 7.9 g |
| Screws (12 × M3 CSK, 14 × M2 CSK, 2 × M2 socket head, 2 × M3 button) | 13.3 g |
| Case without the weight | 1242 g |
| Weight, brass / Ti-6Al-4V | 743 g / 387 g |
| Case with the weight, brass / Ti-6Al-4V | 1985 g / 1629 g |
| Boards, plate, battery, switches, keycaps, screen (estimate) | about 620 g |
| Complete keyboard, brass / Ti-6Al-4V (estimate) | about 2.60 kg / 2.25 kg |

The estimate: mainboard 100 g (FR4 from the model) + 10 g of parts, plate 59 g, 77 switches 254 g, hot-swap sockets
27 g, stabilizers 14 g, PBT keycaps 114 g (from the model's volumes), cell 29 g, screen, encoder and USB-C boards 15 g.

## PCBs

| Qty | Board | Folder |
|---:|---|---|
| 1 | Mainboard | `hardware/Dachshund70/` |
| 1 | USB-C daughterboard | `hardware/Dachshund70-USB/` |
| 1 | Encoder module | `hardware/Dachshund70-Encoder/` |
| 1 | Switch plate (FR4) | `hardware/Dachshund70-Plate/` |
| 1 | 2.4 GHz dongle (separate, not in the case) | `hardware/Dachshund70-Dongle/` |
