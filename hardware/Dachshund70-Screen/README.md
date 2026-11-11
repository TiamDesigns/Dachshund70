# Dachshund70 screen board

A small board that powers the 2.7" Sharp memory LCD and joins it to the mainboard with one flat cable. KiCad 10
project, 2 layers, 0.8 mm FR4, 21.0 × 34.0 mm with R1 corners.

- **Panel:** Sharp LS027B7DH01 (400 × 240, 2.7", 62.8 × 42.82 × 1.64 mm glass, 58.8 × 35.28 mm picture, about
  173 ppi). It stands on end beside the knob, so the picture is 240 × 400 in portrait. A memory LCD redraws a
  full frame in about 50 ms and holds its picture for a few microwatts, so the firmware treats it like an OLED,
  not like e-paper: no refresh limit, no flashing.
- **Every part is on the bottom side**, facing the mainboard. The top side is a plain ground pour, taped to the
  back of the panel.
- **Same coordinates as the mainboard.** The board is drawn where it sits in the case, straight over the
  mainboard (x 311.0 to 332.0, y 69.2 to 103.2 KiCad mm), so its STEP drops into the case model at the same x
  and y (`python hardware/export_step.py` writes `hardware/step/Dachshund70-Screen.step` with the mainboard's
  origin).

Rev 1.0 of this board (in git history, PR #83) drove the 2.13" GDEY0213B74 e-paper panel instead.

## Circuit

- **5 V supply.** The panel runs from 5 V (VDD and VDDA, 4.8 to 5.5 V). U1, a TI TPS61222 (fixed 5 V boost,
  SC-70-6), makes it from the mainboard's 3V3, with L1 (4.7 µH), C1 (10 µF in) and C2 (10 µF out), as in TI's
  5 V example. FB goes straight to VOUT, as the datasheet says for the fixed versions.
- **Enable.** U1's EN comes from J4 pin 8 (the e-paper overlays' BUSY, P0.24) as VLCD_EN, and R1 (100 kΩ) pulls
  it up to 3V3. The Sharp overlay leaves that pin alone, so the 5 V is always on. The firmware could drive it low
  to cut the panel's power in deep sleep, but then the panel loses its picture.
- **Logic.** The panel takes 3.3 V logic straight (VIH from 2.7 V; Sharp recommends about 3 V). No level shifter.
- **VCOM.** EXTMODE is tied high, so VCOM follows the EXTCOMIN pulse from the MCU (Zephyr's `sharp,ls0xx` driver
  toggles it at 1 Hz).
- **Sharp's capacitors.** C3 (1 µF, VDD), C4 (100 nF, VDDA) and C5 (100 nF, DISP), placed close to J1.
- **Power.** The panel draws about 50 µW holding a picture and about 175 µW updating once a second. With U1's
  5.5 µA quiescent current, the screen costs about 0.03 to 0.08 mA while typing and 20 to 40 µA asleep.

The firmware build is
`-DEXTRA_DTC_OVERLAY_FILE=displays/sharp-ls027b7dh01-portrait.overlay`.

## Cable

The mainboard's J4 is an 8-pin 0.5 mm FFC socket (Hirose FH12-8S-0.5SH(55)), on its top side under the plate's
screen notch. The screen board's J2 is the same socket on its bottom side, at the same x and y (centre
(327.9, 94.9)). Both mouths face −x. The cable leaves J4, loops up through the plate's notch and turns back into
J2: a C-shaped loop.

- Use a **0.5 mm pitch, 8-way FFC with contacts on the same side at both ends** (often called type A). Each
  conductor stays at the same y, so J4 pin n meets J2 pin 9 − n. The schematics already account for that.
- The length still has to be set from the case model: the gap between the two boards plus the loop. Buy a
  few lengths around it; FFCs are cheap.

J4 and the mainboard are unchanged from rev 1.0. Its pins keep their e-paper names in the mainboard schematic; the
Sharp panel uses them like this:

| J4 pin (mainboard) | Mainboard net | MCU pin | J2 pin (screen board) | Screen board net | Panel pin |
| --- | --- | --- | --- | --- | --- |
| 1 | +3V3 | | 8 | +3V3 (U1 input) | |
| 2 | GND | | 7 | GND | 9, 10 |
| 3 | DISP_DIN | P0.21 | 6 | SI | 2 |
| 4 | DISP_CLK | P0.19 | 5 | SCLK | 1 |
| 5 | DISP_CS | P0.20 | 4 | SCS (active high) | 3 |
| 6 | DISP_DC | P0.23 | 3 | EXTCOMIN | 4 |
| 7 | DISP_RST | P0.22 | 2 | DISP | 5 |
| 8 | DISP_BUSY | P0.24 | 1 | VLCD_EN (U1's EN) | |

Panel pins 6 and 7 (VDDA, VDD) and 8 (EXTMODE) are on +5V.

## Geometry

- **The panel's tail.** In landscape the LS027B7DH01's FPC leaves a long edge (the bottom one). Stood on end, that
  edge is on the left. The tail folds back under the glass (Sharp allows bends 0.8 to 6.0 mm from the glass edge,
  inner radius at least 0.45 mm) and runs right into J1.
- **J1** (panel socket, Hirose FH12-10S-0.5SH(55)) is centred at (316.6, 93.7) with its mouth facing −x, toward
  the board's left edge. Its pad row is at x 318.45, from pad 10 at y 91.45 to pad 1 at y 95.95.
- **J1's pins run the other way from the panel's: J1 pin n = panel pin 11 − n.** Looking down on the board,
  the fold puts panel pin 1 at the top (smaller y), where J1's pad 10 is. That assumes pin 1 is on the left of
  the tail when you look at the panel's face in landscape with the tail at the bottom: check it (see below).
- **J2** (cable socket) has its pad row at x 329.75, y 93.15 (pin 8, 3V3) to 96.65 (pin 1, VLCD_EN).
- The board stays left of the radio's antenna (x > 333) and well inside the glass (about x 308 to 351 and y 62
  to 125, if the case thread's 39 mm sidebar holds).

## Routing

The board is hand-routed in `gen_screen.py`.

- The five signals run right from J1, then step down a staircase into J2 under its body. SCLK and SI swap
  order between the two sockets, so SCLK hops over SI on the top layer: the only crossing.
- The boost sits above the sockets: U1 in the middle, L1 to its left, C1 and the 3V3 rail above.
- 3V3 runs from J2 up the right-hand side under J2's body, then along the top of the board.
- On the top layer, apart from the SCLK hop, two tracks cross the ground pour: +5V from the boost down to J1
  and its capacitors, and VLCD_EN from J2 up to U1.
- Track widths are 0.4 mm for SW, 0.3 mm for 3V3, +5V and ground stubs, 0.2 mm for signals. Vias are
  0.6/0.3 mm.

## Mainboard changes

None for the Sharp panel. J4 became an FFC socket in rev 1.0; `move_j4.py` records that one-off edit.

## Status

The board has been checked in KiCad only. Nothing is ordered, made or fitted.

- ERC: 0. DRC with schematic parity and every severity: 0 violations and 0 unconnected items.

## Open checks before ordering

- **Panel FPC: pin 1, contact face and pitch.** From Sharp's drawing, or a panel in hand: which end of the tail
  is pin 1, which face carries the contacts, and the pitch (0.5 mm is assumed). If pin 1 lands at the bottom of
  J1 instead, swap J1's pin map in `gen_screen.py` (`SOCKET`) and reroute. Then check the FH12-10S's contact side
  against the tail's contacts after the fold. Sharp's recommended sockets are SMK CFP-4610-0150F (bottom
  contact) and Molex 51441-1093.
- **Panel tail position and length.** Where along the long edge the tail leaves, and how long it is, so that
  it reaches J1 after the fold. J1 sits at y 93.7, about the middle of the glass's length.
- **FFC against the sockets.** As in rev 1.0: with same-side contacts and the C-shaped loop, J2 and J4 must
  have their contacts on the same side as the cable's contacts at each end.
- **LCSC numbers to confirm or fill:**
  - Filled in: 10 µF C19702, 1 µF C52923, 100 nF C1525, 100 kΩ C25741. Confirm these.
  - Still blank: J1 and J2 (FH12-10S and FH12-8S), U1 (TPS61222DCKR) and L1 (FNR3015S4R7MT).
- **Case.** The screen pocket, window and board pocket in the Fusion model are drawn for the 2.13" e-paper. They
  need the LS027B7DH01's 62.8 × 42.82 mm glass, the folded tail on the left, and this board under it. Then place
  the FFC loop and check the parts' clearance to the plate (it floats ±1 mm).
- **On hardware:** which way up the text comes out (`rotation` in the overlay), and that the picture holds with
  EXTCOMIN at 1 Hz.

## Regenerating

Run with KiCad 10's Python, from the repo root:

```
"C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70-Screen/gen_screen.py
```

This rewrites the schematic and the whole board: placement, the routes in `ROUTES` and `VIAS`, and the filled
pours. Then check it:

```
kicad-cli pcb drc --schematic-parity --severity-all Dachshund70-Screen.kicad_pcb
kicad-cli sch erc --severity-all Dachshund70-Screen.kicad_sch
```
