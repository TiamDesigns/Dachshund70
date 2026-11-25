# Dachshund70 wired mainboard

Rev 1.4 (2026-11-24). A wired-only mainboard next to the tri-mode one (`hardware/Dachshund70/`, unchanged): no
radio, no battery, an RP2350B, an SK6812MINI-E under every key and hot-swap sockets on every key. KiCad 10, 2 layers,
same outline as mainboard rev 1.4 (x 19 to 326, y 39 to 160.1, the MCU column on the right), every part on the back,
so it drops into the same plate, case and flex.

Status: schematic ERC 0; board DRC clean (0 violations, 0 unconnected, schematic parity clean, kicad-cli 10.0.3).
Not ordered, not tested. No firmware yet: the RP2350 port is in `SCHEDULED_TASKS.md`.

Rev 1.0 had an RP2040 and a small SPI TFT; rev 1.1 swaps in the RP2350B so the screen can be a 2.41" AMOLED
(450 × 600, RM690B0 driver) on quad SPI, which the RP2040 couldn't drive at a useful frame rate. Rev 1.2 adds the
touch version of that screen: J4 grows to 16 pins for its touch controller's I2C, interrupt and reset. Rev 1.3
switches the screen to e-paper with capacitive touch, since the screen is mostly for changing settings; rev 1.4
picks the panel: Good Display's 2.9" GDEY029T94-FT01 (296 × 128, capacitive touch, front light), which fits the 2u
column above the arrows (the 3.7" GDEY037T03-FT21 made the keyboard too wide). Both keep rev
1.2's copper and GPIOs, with the screen lines renamed.

## What's on it

- **RP2350B** (U1, QFN-80, 10 × 10 mm) with a W25Q128JVSIQ flash (U2, 16 MB), 12 MHz crystal (Y1, ABM8-272-T3,
  15 pF, 1k on XOUT), its own 1.1 V switching regulator (L1 3.3 µH, C9 4.7 µF in, C10 4.7 µF out, VREG_AVDD
  through R11 33 Ω with C27), 100 nF on the power pins, BOOT (SW1, QSPI_SS to GND through 1k) and RESET (SW2)
  buttons, and SWDIO/SWCLK test pads (TP5, TP6). The ROM has a UF2 bootloader (hold BOOT at reset), so flashing
  stays drag-and-drop.
- **77 keys**, 6.25u spacebar only (no split layout), Kailh-pattern hot-swap sockets (HanElectricity
  CPG151101S11-2, C49352235) on every key, a 1N4148W per key, COL2ROW.
- **77 SK6812MINI-E** reverse-mount LEDs (LED1-LED77), one under each key at the switch's LED window
  (key centre + 5.08 mm), through a 3.4 mm light cutout, each with a 100 nF cap. The chain is serpentine:
  LED1 is Delete, the top row runs right to left, the next left to right, and so on; LED77 is Right arrow.
- **LED power:** an AO3401A (Q1) switches VBUS to LED_5V, driven by a 2N7002 (Q2) from GPIO1 (LED_EN, 100k
  pull-down so the LEDs stay off through reset and USB suspend). R6/C19 slow its turn-on so the 77 LED caps and
  C18 (22 µF) don't pull VBUS down. A 74AHCT1G125 (U4) powered from LED_5V lifts the 3.3 V data to 5 V (33 Ω out).
- **3.3 V** from an ME6211C33 (U3, 500 mA) on VBUS.
- **Connectors**, all at the edge with their mouths out, in rev 1.4's places:
  - J1 (JST-SH 6P) to the hub board or the old USB-C board: 1 VBUS, 2 D−, 3 D+, 4 GND, 5-6 not connected.
    The old daughterboard (`hardware/Dachshund70-USB`) still fits for a Lite build; its slide switch does nothing.
  - J4 (FH12-16S FFC, LCSC C596731) to the screen: 1-2 +3V3, 3 GND, 4 TP_RST, 5 GND, 6 TP_INT, 7 TP_SCL,
    8 TP_SDA, 9 FL_PWM (front light), 10 TP_EN, 11 EPD_BUSY, 12 EPD_RST, 13 EPD_DC, 14 EPD_MOSI, 15 EPD_SCK, 16 EPD_CS.
    The e-paper's SPI is on the RP2350's SPI0 pins (CS GPIO33, SCK 34, MOSI 35) and its touch controller (I2C,
    an FT6336U) on I2C1 (GPIO42/43) with 4.7k pull-ups on the board (R12, R13). The twelve lines run as one bus
    with no crossings (J4's order is the chip's, reversed). J4 sits 1.5 mm lower than rev 1.1's 12-pin one (centre
    y 119.4). The panel comes bare on its own FPCs (e-paper, touch, front light), so a small adapter board goes between:
    see Open checks.
  - J5 (JST-SH 5P) encoder, unchanged: 1 COL14, 2 ENC_A, 3 GND, 4 ENC_B, 5 ENC_SW (push switch at row 0, col 14
    through D114).

## Pin map (RP2350B)

| GPIO | Net | | GPIO | Net |
|---|---|---|---|---|
| 0 | LED data (PIO, through U4) | | 33 | EPD_CS (SPI0 CSn) |
| 1 | LED_EN | | 34 | EPD_SCK (SPI0) |
| 2-3 | not connected | | 35 | EPD_MOSI (SPI0 TX) |
| 4-14 | COL4-COL14 | | 36 | EPD_DC |
| 15-20 | ROW0-ROW5 | | 37 | EPD_RST |
| 21-24 | COL0-COL3 | | 38 | EPD_BUSY |
| 25-26 | ENC_A, ENC_B | | 39 | TP_EN (touch power, optional) |
| 27-32 | not connected | | 40 | FL_PWM (front light dimming, on J4 pin 9) |
| | | | 42, 43 | TP_SDA, TP_SCL (I2C1) |
| | | | 44, 45 | TP_INT, TP_RST |
| | | | 41, 46, 47 | not connected (ADC pins free) |

The schematic is the reference: the left side of the chip carries the matrix (COL4-COL14, ROW0-ROW5) and the right
side the screen and touch, so neither crosses the other. Scan the matrix with pull-ups (drive rows low, read columns): the
RP2350's erratum E9 makes its internal pull-downs unreliable.

Rows and columns follow `boards/Dachshund70/README.md`'s matrix (row 5, col 6 is the 6.25u spacebar; row 5 cols 4
and 8 are gone with the split layout).

## Power budget

The board is bus-powered through the hub (or a plain USB-C board). 77 LEDs at full white would draw about 2.8 A,
far over USB's 500 mA (or 900 mA / 1.5 A on hosts that offer it), and on the hub the keyboard shares the PC's port
with the back ports. The firmware must cap the LEDs' total brightness, for example to about 300 mA at the default,
and turn LED_EN off in USB suspend. There's no battery, so the old battery-life limits no longer apply.

## Layout notes

- Two layers. The matrix runs mostly as horizontal tracks on the front and vertical ones on the back. The
  RP2350B's left (matrix) and right (screen) pins fan out in a staircase to staggered via columns. Its power pins
  join short rings inside the pad ring: +3V3 in three arcs tied together on the front under the chip, +1V1 in an
  arch over the exposed pad, and PGND straight into the exposed pad. The regulator's inductor and caps sit at the
  chip's bottom-right corner, next to VREG_LX/VREG_FB/VREG_AVDD, with their grounds on short links to vias.
- The screen and touch lines (e-paper SPI, touch I2C) leave the chip's right side and J4's pins in a staircase to via columns and run
  between them as a fixed twelve-line bus on the front, nested so no two cross. The crystal is turned so XIN and
  XOUT are short, with a ground guard under it between them.
- Ground: a pour on both layers, with one via per cut-off pour area (no via grid), placed by `tools/stitch.py`,
  plus short ground links where a pad sat in a cut-off island. Ground pads too boxed in for two thermal spokes join
  the pour solid (rule in `Dachshund70-Wired.kicad_dru`).
- Netclasses: Default 0.15 mm track and clearance (inside JLCPCB's 2-layer limits), Power (LED_5V, VBUS) 0.5 mm.
- Crowded reference texts (the column's passives, the stabilisers) are hidden; the fab layer keeps them.

## How it was made

The schematic was built with the KiCad MCP (Konnect): parts placed and checked through it, with the repetitive key,
LED and label grids written by script. Freerouting couldn't run on this PC, so the board was routed by a small grid
router in `tools/` (multi-source Dijkstra on a 0.1 mm grid, both layers, rip-up and reroute, then dead-end pruning).
For revs 1.1 and 1.2 only the MCU column was re-placed and re-routed (above the USB connector, plus J4's corner);
the keys, LEDs and the rest of the lower column kept rev 1.0's routing. `tools/rebuild_column.sh` re-does that from the schematic: placement in `tools/sync.py`
and `tools/col.json`, fixed fan-outs, power rings, the screen bus and ground links in `tools/prefan.py`, rev 1.0's routing cut out of
the column (`tools/cut.py`), routing plan `tools/plan_column.json` (the net order `tools/orders.py` found that
routes everything), then pour, one ground via per cut-off island (`tools/stitch.py`) and removal of one-sided vias.
It needs rev 1.0's board geometry as `geom_old.json` and the scratch folder in `S`.

## Open checks

- **Screen:** Good Display GDEY029T94-FT01: 2.9" e-paper, 296 × 128, 79.0 × 36.7 × 2.15 mm outline, 66.9 × 29.1 mm
  picture, FT6336U capacitive touch, 4-LED front light. The adapter board is `hardware/Dachshund70-EPD/` (its README
  lists the checks before ordering). The case window is the 2u column above the arrows (case thread).
- **L1:** the footprint is Murata's DFE201610P land pattern standing in for the Abracon AOTA-B201610S3R3-101-T
  (same 2016 size). Check the land pattern and the polarity dot against Abracon's drawing before ordering.

- USB D+/D− are routed as ordinary 0.15 mm tracks, not an impedance-controlled pair. Fine for 12 Mbit/s full speed
  over a few centimetres.
- 3D models and the case: the hub board and the screen board change the case (`SCHEDULED_TASKS.md`).
