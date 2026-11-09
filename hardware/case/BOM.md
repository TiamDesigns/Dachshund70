# Dachshund70 case BOM (rev 2, with the November 2026 fixes)

Everything that goes into the case and holds it together, for the default layout (split spacebar). The PCBs
are line items only; their parts are in each board's own BOM (`hardware/<board>/`). Sizes are in mm, from the
Fusion model. Masses use 2.70 g/cm³ for aluminium, 8.50 for C360 brass, 4.43 for Ti-6Al-4V, 1.2 for the printed
resin and 7.9 for stainless screws. Finish and anodise colours are Tiam's choice.

## Made parts

| Qty | Part | Material | Size, volume | Process | File |
|---:|---|---|---|---|---|
| 1 | Top block | 6061-T6 aluminium | 347.9 × 155.2 × 24.5, 166.0 cm³ (448 g) | CNC 3-axis (5-axis or a ball-end for the slopes), bead-blast, anodise | `step/Dachshund70-Case-Top.step` |
| 1 | Bottom block | 6061-T6 aluminium | 347.9 × 155.2 × 15.1, 295.9 cm³ (799 g) | CNC, bead-blast, anodise | `step/Dachshund70-Case-Bottom.step` |
| 1 | Accent ring | 6061 or 5052 aluminium sheet, 1.6 thick | outline 347.9 × 155.2, opening 320 × 122.6, 23.0 cm³ (62 g) | Laser cut from flat sheet, anodise in the accent colour | `step/Dachshund70-Case-Ring.step`, `dxf/Dachshund70-Case-Ring.dxf` |
| 6 | Gasket retainer | 6061-T6 aluminium | 44.1 × 4.55 × 4.1, R1.1 corners, 0.82 cm³ (2.2 g each, 13.3 g the six) | CNC (or cut from 4.1 bar), anodise | `step/Dachshund70-Case-Gasket-Retainer.step` |
| 1 | Weight | C360 brass (Ti-6Al-4V, steel or aluminium possible) | face 185.0 × 40.0 (R4), flange 216.0 × 53.0 (R5), 5.1 / 6.4 / 7.7 thick, 51.1 cm³: brass 435 g, Ti-6Al-4V 227 g, steel 401 g, aluminium 138 g | CNC; polished face with a 0.4 chamfer round the edge; dachshund silhouette 0.3 deep (flat floor bead-blasted), 0.4 wide detail grooves 0.5 deep, "Dachshund70" text 0.3 deep (Fredoka SemiBold, SIL OFL, 7.8 tall) | `step/Dachshund70-Case-Weight.step`, `dxf/Dachshund70-Weight-Engraving.dxf` |
| 1 | Knob | 6061 aluminium | Ø19.2 × 15.1, 3.73 cm³ (10.1 g) | CNC, form-knurl, anodise | `step/Dachshund70-Case-Knob.step` |
| 1 | Encoder cover | 6061 aluminium | 16.9 × 25.9 × 19.7 with its foot and rear ear, 2.32 cm³ (6.3 g) | CNC, anodise in the accent colour | `step/Dachshund70-Case-Encoder-Cover.step` |
| 1 | Power switch slider cap | 3D-printed resin (or machined POM) | 3.6 × 2.6 stadium, 2.2 long, 0.016 cm³ | SLA print, or turn/mill in POM | `step/Dachshund70-Case-Switch-Cap.step` |
| 1 | LED light guide | Opaque black SLA or SLS resin | 30.6 × 6.05 × 10.05, 1.03 cm³ (1.2 g) | 3D print | `step/Dachshund70-Case-LED-Guide.step` |

Notes on the made parts:

- Gasket retainers: one under each of the plate's six nubs (front and back), all the same part. Each fills the
  opening under its nub's pocket region (44.3 × 4.65, R1.0 corners, open from below) from the ring's top up to the
  sock floor (local z 3.5): its top is the floor under both socks and the nub's clearance, it seats against the top
  block's step at 3.5, and the ring clamps it from below. 0.1 clear at its ends and outer side; its inner side is flush
  with the top block's pocket wall, 0.75 from the PCB's edge.
- Weight: it drops in from inside through a window in the bottom block, its 1.5 mm flange resting on a stepped
  ledge pocket (ledges at z 3.68 front, 5.01 middle, 6.34 back, matching the floor's steps; the risers sit 0.1 behind
  the flange's steps, R1.0 in their corners and on the flange's), and sits 0.1 under the floor. Four M2 × 4 countersunk
  screws from inside, at x ±103.5 and y 2.5 / 30.5 (local frame), in 90° countersinks 4.0 → 2.2 (0.9 deep, a 0.6 land
  left in the flange), into M2 taps in the ledges: drill Ø1.6 to the screw tip + 1.0, thread to tip + 0.5 (2.5 of
  thread; 1.0 and 2.4 of floor left under the drill points). No screw heads show on the bottom.
- Knob: D-bore 6.0 with the flat at 4.5 (across the flat) for the PEC12R's 6 mm D shaft, blind, ending 0.3 past the
  shaft's tip, behind a Ø7.6 × 4.9 hub bore; push-on (rotary-broach the D, or wire-EDM it before the blind end is
  faced). The knurl is to be form-knurled, diamond, about 0.8 pitch (the model shows 64 flutes and 14 rings).
- Encoder cover: 19.2 wide with R7 top corners, tangent to the knob's sides and top; cavity 13.1 wide for the PEC12R
  body (+0.3, R0.5 corners, R1.0 at its closed end), ear pockets R0.6. Its foot sits on the encoder module and takes
  the module's two M2 screws (taps Ø1.6 through the foot, 1.0 wall); its rear ear goes into a pocket in the top
  block's back wall and takes 2 × M2 × 6 up into the top block (taps drilled 4.0 deep, 1.2 under the top face). Walls
  at least 1.0 everywhere; 0.15 to the knob, 0.15 to the plate, 0.17 to the encoder's frame ears.
- Switch cap: a light press fit on the PCM12 lever (pocket 1.3 × 1.0, 0.05 under the lever, R0.2 corners) plus a drop
  of cyanoacrylate; walls 0.8 round the pocket. It stands 0.3 proud of the back face and rides in a stadium slot
  5.5 × 3.0 (0.2 clear all round, 1.5 travel). Three grooves 0.3 wide × 0.3 deep, 1.1 apart, leave 0.8 ribs.
- Light guide: one channel per LED (five, Ø2.3): straight up from the LED through a 3.7 square spigot in the plate's
  4 × 4 window (0.15 clear) to 0.09 over the PCB, then one S bend to its roof hole. Walls at least 0.7 (spigots) and
  1.15 (ends), corners R1.15 in an R1.0 pocket.
- Ring: every wall square to the sheet; 8 × Ø3.4 screw holes and 12 joint slots 12.2 × 1.7 (the blocks' tabs are
  11.8 × 1.3: 0.2 a side). The back-centre slot is at x −45.

## Bought parts

| Qty | Part | Notes |
|---:|---|---|
| 4 | M3 × 12 countersunk, DIN 7991, stainless | Bottom block to top block, along the front, flush with the bottom face; 6.0 of the screw in the top block, taps threaded 7.5 and drilled 9.0 deep from its bottom face (tip + 1.5 / tip + 3) |
| 4 | M3 × 20 countersunk, DIN 7991, stainless | The same along the back (the block is 23 mm tall there); 4.75 in the top block, taps threaded 6.25 and drilled 7.75 deep |
| 4 | M2 × 4 countersunk, DIN 965, stainless | The weight, from inside, into the ledge taps (above) |
| 2 | M3 × 6 button head (ISO 7380) | USB-C daughterboard into the two taps on its ledge (x −16.5 and 19.0); the pocket is open from above, so drive them before the ring and the top block go on |
| 2 | M2 × 6 pan head (ISO 7045), stainless | Encoder cover to the top block, up through the cover's rear ear |
| 2 | M2 × 5 pan head (ISO 7045), stainless | Encoder module to the cover's foot, up through the module's holes. The heads need the mainboard's two Ø4.2 clearance holes moved 0.74 onto the module's holes (see below) |
| 1 | Rubber or TPU rail with adhesive, 300 × 5.8 × 2.0 | Near the front edge, in a 1.0 pocket, 1.0 proud |
| 1 | Rubber or TPU rail with adhesive, 269.4 × 5.8 × 2.0 | Near the back edge, x −150 to 119.4 (it stops 3.0 short of the battery bay), in a 1.0 pocket, 1.0 proud |
| 12 | Gasket socks, silicone, 8 × 5 × 5 outside, pocket 6.5 × 2.8 × 1.2 | Moulded (stock). One on each of the plate's prongs, lying along the plate edge, on the gasket retainers |
| 1 | LiPo cell EEMB LP803450, 52.0 × 34.5 × 8.3 plus a 4.5 protection board | Flat in the battery bay (x 122.7 to 160, y 2.0 to 61.3, floor 1.0, R3 corners), long side front to back, held with foam tape (0.9 of play at its sides). Its top overlaps J1 by about 0.7 (see below). JST-PH polarity varies between vendors: check it against J2 |
| 1 | E-paper panel, GoodDisplay GDEY0213B74 (2.13", 250 × 122) with driver board | Drops in from below, taped under the roof's window |
| 1 | Double-sided tape, 0.2 mm (3M 9448A or tesa 4965) | Screen glass to the roof |
| 1 | JST-SH 4-pin cable, about 100 mm, both ends plugged | USB-C daughterboard to J1 |
| 1 | Power slide switch PCM12SMTR (on the USB-C daughterboard) | Its lever takes the slider cap |
| 79 | MX-style hot-swap switches | 77 with the 6.25 u spacebar |
| 5 | 2 u screw-in (PCB-mount) stabilizers | Backspace, Enter, left Shift, the 2.75 u space and the 2.25 u right Mod. With the 6.25 u spacebar: one 6.25 u stabilizer for the space, plus Backspace, Enter and left Shift |
| 1 | Keycap set, Cherry profile | Needs the split spacebar's 1.25 u Mod, 2.75 u space and 2.25 u Mod (or a 6.25 u space) |

Open points from the November 2026 check (board changes, not case changes):

- Mainboard: its Ø4.2 head-clearance holes for the encoder module's screws are at local (128.95, 41.25) and
  (128.95, 57.85), 0.74 off the module's holes at (128.375, 41.71) and (128.375, 58.31), so the M2 heads hit the board.
  Move them to KiCad (306.625, 57.84) and (306.625, 41.24).
- Mainboard: J1 (JST-SH, underside, KiCad x 328.5 to 333.5, y 82.8 to 91.0) sits over the battery bay; the
  LP803450's top overlaps it by about 0.7 mm. Move J1 off the bay or use a 7.3 mm cell.

## Masses

| Part | Mass |
|---|---:|
| Top block | 448 g |
| Bottom block | 799 g |
| Accent ring | 62 g |
| Knob | 10.1 g |
| Encoder cover | 6.3 g |
| Gasket retainers (6) | 13.3 g |
| LED guide, switch cap (resin) | 1.3 g |
| Rails (rubber, about 1.2 g/cm³) | 7.9 g |
| Screws (8 × M3 CSK, 4 × M2 CSK, 4 × M2 pan, 2 × M3 button) | 9.8 g |
| Case without the weight | 1358 g |
| Weight, brass / Ti-6Al-4V | 435 g / 227 g |
| Case with the weight, brass / Ti-6Al-4V | 1793 g / 1584 g |
| Boards, plate, battery, switches, keycaps, screen (estimate) | about 620 g |
| Complete keyboard, brass / Ti-6Al-4V (estimate) | about 2.41 kg / 2.20 kg |

The estimate: mainboard 100 g (FR4 from the model) + 10 g of parts, plate 61 g, 77 switches 254 g, hot-swap sockets
27 g, stabilizers 14 g, PBT keycaps 114 g (from the model's volumes), cell 29 g, screen, encoder and USB-C boards 15 g.

## PCBs

| Qty | Board | Folder |
|---:|---|---|
| 1 | Mainboard | `hardware/Dachshund70/` |
| 1 | USB-C daughterboard | `hardware/Dachshund70-USB/` |
| 1 | Encoder module | `hardware/Dachshund70-Encoder/` |
| 1 | Switch plate (FR4) | `hardware/Dachshund70-Plate/` |
| 1 | 2.4 GHz dongle (separate, not in the case) | `hardware/Dachshund70-Dongle/` |
