# Dachshund70 screen board

Rev 3.0 (2026-11-17). The board under the 2.7" Sharp memory LCD: the panel's socket, its 5 V supply and the
five layer and battery LEDs. It joins the mainboard with one 12-way flat cable. KiCad 10 project, 2 layers,
0.8 mm FR4, 40.0 × 47.0 mm (x 309 to 349, y 88 to 135 KiCad mm) with R1 corners.

Why a separate board again: the mainboard is held by the switches and moves with the plate's flex, and the
screen is fixed in the case. From mainboard rev 1.3 the mainboard keeps only the keys, the MCU, power and the
connectors, so the same mainboard can go into a cheaper Dachshund70 Lite with no screen and no encoder.

- **Panel:** Sharp LS027B7DH01 (400 × 240, 2.7", 62.8 × 42.82 × 1.64 mm glass, 58.8 × 35.28 mm picture). It
  stands on end beside the knob, so the picture is 240 × 400 in portrait. The firmware build is
  `-DEXTRA_DTC_OVERLAY_FILE=displays/sharp-ls027b7dh01-portrait.overlay`.
- **Every part is on the bottom side.** The top side is a plain ground pour, taped to the back of the panel;
  the LEDs shine up through cut-outs in the board (reverse mount).
- **Same coordinates as the mainboard.** The board is drawn where it sits in the case, so its STEP drops into
  the case model at the same x and y (`python hardware/export_step.py`).

Rev 1.0 (PR #83) drove the 2.13" e-paper; rev 2.0 (PR #84) was this panel without the LEDs; PR #85 moved the
circuit onto the mainboard (rev 1.2), which rev 1.3 undoes.

## Circuit

- **5 V supply.** The panel runs from 5 V. U1, a TI TPS61222 (fixed 5 V boost), makes it from the mainboard's
  3V3, with L1 (4.7 µH), C1 (10 µF in) and C2 (10 µF out).
- **Enable.** U1's EN is VLCD_EN, from the MCU's P0.24 (the overlays' BUSY), with R1 (100 kΩ) pulling it up,
  so the 5 V is on unless the firmware drives it low.
- **Logic.** 3.3 V logic straight into the panel. EXTMODE is tied high, so VCOM follows EXTCOMIN (1 Hz).
- **Sharp's capacitors.** C3 (1 µF), C4 and C5 (100 nF), close to J1.
- **LEDs.** D1 (layer) and D2 to D5 (battery gauge 25/50/75/100%), SK6812MINI-E reverse mount at 7.5 mm pitch
  in a row at y 130.5, x 314.56 to 344.56, each with a 100 nF cap (C6 to C10). They are LEDs 1 to 5 of the
  chain: the data comes from the Caps Lock LED (D2 on the mainboard, LED 0) on the cable as LED_DIN. LED_VDD is
  the mainboard's switched LED supply (its load switch and level buffer stay on the mainboard).

## Cable

Mainboard J4 and this board's J2 are both Hirose FH12-12S-0.5SH(55) (12-way, 0.5 mm). J4 is on the mainboard's
top side at its right edge, mouth +x, pads at x 319.45, y 109.25 (pin 12) to 114.75 (pin 1). J2 is on this
board's bottom side at the same y, 6 mm further right (pads at x 325.45), also mouth +x. The cable leaves J4,
loops up and back into J2: a C-shaped loop past the mainboard's right edge (x 326).

- Use a **0.5 mm pitch, 12-way FFC with contacts on the same side at both ends** (type A). Each conductor
  keeps its y, so **J2 pin n = J4 pin 13 − n**. The schematics already account for that.
- Length: set it from the case model (gap between the boards plus the loop), and buy a few lengths around it.

| J4 pin (mainboard) | Mainboard net | MCU pin | J2 pin (screen) | Screen net | Panel pin |
| --- | --- | --- | --- | --- | --- |
| 1, 2 | LED_VDD | | 12, 11 | LED_VDD | |
| 3 | GND | | 10 | GND | 9, 10 |
| 4 | LED_DOUT (from D2) | (P0.06 via D2) | 9 | LED_DIN | |
| 5 | GND | | 8 | GND | |
| 6 | DISP_RST | P0.22 | 7 | DISP | 5 |
| 7 | DISP_DC | P0.23 | 6 | EXTCOMIN | 4 |
| 8 | DISP_CS | P0.20 | 5 | SCS (active high) | 3 |
| 9 | DISP_DIN | P0.21 | 4 | SI | 2 |
| 10 | DISP_CLK | P0.19 | 3 | SCLK | 1 |
| 11 | DISP_BUSY | P0.24 | 2 | VLCD_EN (U1's EN) | |
| 12 | +3V3 | | 1 | +3V3 (U1 input) | |

Panel pins 6, 7 (VDDA, VDD) and 8 (EXTMODE) are on +5V. Without the screen board (the Lite), J4 can be left
unfitted: Caps Lock still works, and the firmware is built without a display overlay.

## Geometry

- **J1** (panel socket, FH12-10S) is at (314.6, 110.6), mouth −x, pads at x 316.45 from pin 10 (y 108.35) to
  pin 1 (y 112.85). **J1 pin n = panel pin 11 − n**, assuming the tail folds back under the glass's left edge
  with pin 1 at the top (check it, below).
- The boost (U1, L1, C1, C2, R1) is at the top right, around (330, 96).
- The board stays inside the glass (about x 308 to 351, y 63 to 126) except its LED row, which sits below the
  glass at y 130.5, where the five LEDs light the case's holes.

## Routing

Autorouted with Freerouting 1.9, then hand-fixed. The routes are in `screen_routes.py` (`ROUTES`, `VIAS`), which
`gen_screen.py` reads. Power (+5V, +3V3, LED_VDD) is 0.3 mm; signals 0.2 mm; vias 0.6/0.3 mm. The LED chain and
power are routed by hand. The ground pours on both sides are stitched on a 2.5 mm grid; 0.5 mm keep-outs run
along the edges and ±2 mm around each LED cut-out (`Dachshund70-Screen.kicad_dru` allows 0.3 mm from the cut-outs).

## Status

Checked in KiCad only; nothing is ordered, made or fitted. ERC: 0. DRC with schematic parity and every severity:
0 violations, 0 unconnected items.

## Open checks before ordering

- **Panel FPC: pin 1, contact face, pitch, tail position and length**, from Sharp's Figure 8-1 or a panel in
  hand. If pin 1 lands at the bottom of J1, swap `SOCKET` in `gen_screen.py` and reroute.
- **FFC contact sides**: with a type-A cable in a C loop, J4 (top side) and J2 (bottom side) must face the
  cable's contacts at each end.
- **LCSC numbers:** J1/J2 (FH12-10S, FH12-12S), U1 (TPS61222DCKR) and L1 (FNR3015S4R7MT) are still blank.
- **Case:** the board pocket, the cable loop past the mainboard's right edge and the LED holes at x 314.56 +
  7.5 i, y 130.5.

## Regenerating

Run with KiCad 10's Python, from the repo root:

```
"C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70-Screen/gen_screen.py
```

This rewrites the schematic and the whole board: placement, the routes from `screen_routes.py`, and the filled
pours. Then check it:

```
kicad-cli pcb drc --schematic-parity --severity-all Dachshund70-Screen.kicad_pcb
kicad-cli sch erc --severity-all Dachshund70-Screen.kicad_sch
```
