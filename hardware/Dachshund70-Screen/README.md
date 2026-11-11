# Dachshund70 screen board

A small board that carries the 2.13" e-paper panel's driver circuit and joins the panel to the mainboard
with one flat cable. It replaces Adafruit's eInk Breakout Friend (#4224) and the eight hand-soldered wires
from the old J4 header. KiCad 10 project, 2 layers, 0.8 mm FR4, 21.0 × 34.0 mm with R1 corners.

- **Panel:** GoodDisplay GDEY0213B74 (SSD1680, 250 × 122). The GDEY0213B74H (296 × 144, same outline, pins and
  controller) also fits J1, but GoodDisplay lists it as end of life.
- **Every part is on the bottom side**, facing the mainboard. The top side is a plain ground pour, taped to the
  back of the panel.
- **Same coordinates as the mainboard.** The board is drawn where it sits in the case, straight over the
  mainboard (x 311.0 to 332.0, y 69.2 to 103.2 KiCad mm), so its STEP drops into the case model at the same x
  and y (`python hardware/export_step.py` writes `hardware/step/Dachshund70-Screen.step` with the mainboard's
  origin).

## Circuit

It's the SSD1680 reference circuit, as on Adafruit's 2.13" eInk Bonnet and in GoodDisplay's specification:

- L1 (10 µH), Q1 (AO3400A) and R1 (0.47 Ω) form the boost converter. The SSD1680 switches Q1 through GDR and
  senses its current on RESE.
- D3 rectifies VGH (about +20 V). C9 with D1 and D2 pumps VGL (about −20 V).
- The panel's rails (VDD, VSH1, VSH2, VSL, VGH, VGL and VCOM) each get a 1 µF capacitor. Those that swing to ±20 V
  are 25 V 0603 parts. C1 (10 µF) and C10 (100 nF) decouple 3V3.
- BS1 is tied low, so the panel runs 4-wire SPI, as with the Friend. Panel pins 1, 4, 6, 7 and 19 (NC, the
  temperature sensor's I2C, VPP and a test pin) stay open.

The firmware doesn't change. Build with
`-DEXTRA_DTC_OVERLAY_FILE=displays/eink-2in13-v4-portrait.overlay` as before.

## Cable

The mainboard's J4 is now an 8-pin 0.5 mm FFC socket (Hirose FH12-8S-0.5SH(55)), on its top side under the
plate's screen notch. The screen board's J2 is the same socket on its bottom side, at the same x and y
(centre (327.9, 94.9)). Both mouths face −x. The cable leaves J4, loops up through the plate's notch and turns
back into J2: a C-shaped loop.

- Use a **0.5 mm pitch, 8-way FFC with contacts on the same side at both ends** (often called type A). Each
  conductor stays at the same y, so J4 pin n meets J2 pin 9 − n. The schematics already account for that.
- The length still has to be set from the case model: the gap between the two boards plus the loop. Buy a
  few lengths around it; FFCs are cheap.

| J4 pin (mainboard) | J2 pin (screen board) | Net | MCU pin | Panel pin |
| --- | --- | --- | --- | --- |
| 1 | 8 | +3V3 | | 15, 16 |
| 2 | 7 | GND | | 8, 17 |
| 3 | 6 | DISP_DIN | P0.21 | 14 (SDA) |
| 4 | 5 | DISP_CLK | P0.19 | 13 (SCL) |
| 5 | 4 | DISP_CS | P0.20 | 12 |
| 6 | 3 | DISP_DC | P0.23 | 11 |
| 7 | 2 | DISP_RST | P0.22 | 10 |
| 8 | 1 | DISP_BUSY | P0.24 | 9 |

J4 keeps the old header's pin order, so `boards/Dachshund70/` and the display overlays are unchanged. An I2C
OLED module would now need a small adapter to the FFC.

## Geometry

- **J1** (panel socket, Hirose FH12-24S-0.5SH(55)) is centred at (322.35, 75.65), with its pad row at y 77.5.
  Pin 1 is at x 316.6 and pin 24 at x 328.1. Its mouth faces −y, toward the back, where the panel's tail folds
  round under the glass. The pad row is meant to sit 10.65 mm inside the glass's back edge.
- **J2** (cable socket) has its pad row at x 329.75, y 93.15 (pin 8, 3V3) to 96.65 (pin 1, BUSY).
- The board fills the old driver-board pocket and stays left of the radio's antenna (x > 333).

## Routing

The board is hand-routed in `gen_screen.py`.

- The six signals drop straight down from J1 and step right into J2 under its body, so none of them cross.
- On the top layer, three long rails cross over the signal bundle: VGH, VGL and 3V3. The rest of the top
  layer is ground pour.
- The boost loop is kept tight, on the left: L1, Q1, D3 and C9 are all within 5 mm.
- Track widths are 0.4 mm for SW and 3V3, 0.25 mm for the panel rails and 0.2 mm for signals. Vias are
  0.6/0.3 mm.

## Mainboard changes

The changes are in `move_j4.py`, kept as a record of a one-off edit:

- J4 changed from the 1 × 8 2.54 mm header at (309.11, 112.5) to the FH12-8S socket at (327.9, 94.9), which is
  2.7 mm behind the SWD header J3 so its body clears J3.
- The schematic symbol is now `Conn_01x08_MountingPin`, with MP on GND.
- The eight display nets are rerouted:
  - DIN, CLK and CS run down between J3 and the socket's front mounting pad.
  - DC, RST and BUSY run down right of the pad.
  - All six then run west under J3 to the old vias, which moved so that the runs stack in pin order.
- 3V3 comes from J3 pin 1. A via at the old pin 1 keeps J3's 3V3 joined to the rest of the 3V3 net.
- Three GND stitching vias were removed because they were in the way.

The plate lost its J4 slot: the socket sits in the screen notch, which was already open.

## Status

The board has been checked in KiCad only. Nothing is ordered, made or fitted.

- **Screen board:** ERC 0. DRC with schematic parity and every severity: 0 violations and 0 unconnected items.
- **Mainboard after the change:** DRC with schematic parity: 0 unconnected items and 0 parity issues. Apart
  from the library-footprint mismatch warnings it always shows, it's clean. ERC: no new messages.

## Open checks before ordering

- **Panel FPC orientation.** Check which face of the GDEY0213B74's tail carries the contacts, and that pin 1
  lands on J1 pin 1 once the tail folds round. Check too which side the FH12-24S's contacts are on (Hirose's
  drawing). If they don't meet the tail's contacts, J1 needs the FH12 variant with contacts on the other side,
  or its pin order reversed.
- **FFC against the sockets.** Check the same thing for J2 and J4: with same-side contacts and the C-shaped
  loop, both sockets must have their contacts on the same side as the cable's contacts at each end.
- **Panel tail length and position.** Measure the panel to confirm that 10.65 mm from the glass edge to J1's
  pad row matches the tail.
- **LCSC numbers to confirm or fill:**
  - Filled in: AO3400A C20917, 10 µF C19702, 1 µF 25 V 0603 C15849, 4.7 µF 25 V C1779. Confirm these.
  - Still blank: J1 and J2 (FH12-24S and FH12-8S), L1 (FNR3015S100MT) and R1. Check R1's MPN as well: it should
    be the 0.47 Ω part (UNI-ROYAL 0603WAFR470T5E).
- **Current.** The boost runs from the mainboard's 3V3 (REGOUT0) during a refresh. Measure the peak current with
  the other 3.3 V loads running.
- **Case.** The Fusion model still has the Friend: replace it with `Dachshund70-Screen.step`, place the FFC
  loop and check the parts' clearance to the plate (it floats ±1 mm).

## Regenerating

Run with KiCad 10's Python, from the repo root:

```
"C:/Program Files/KiCad/10.0/bin/python.exe" hardware/Dachshund70-Screen/gen_screen.py
```

This rewrites the schematic and the whole board: placement, the routes in `ROUTES` and `VIAS`, and the filled
pours. Then check it:

```
kicad-cli pcb drc --schematic-parity --severity-all Dachshund70-Screen.kicad_pcb
```
