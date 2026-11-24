# Dachshund70 wired mainboard

Rev 1.0 (2026-11-24). A wired-only mainboard next to the tri-mode one (`hardware/Dachshund70/`, unchanged): no
radio, no battery, an RP2040, an SK6812MINI-E under every key and hot-swap sockets on every key. KiCad 10, 2 layers,
same outline as mainboard rev 1.4 (x 19 to 326, y 39 to 160.1, the MCU column on the right), every part on the back,
so it drops into the same plate, case and flex.

Status: schematic ERC 0; board DRC clean (0 violations, 0 unconnected, schematic parity clean, kicad-cli 10.0.3).
Not ordered, not tested. No firmware yet: the RP2040 port is in `SCHEDULED_TASKS.md`.

## What's on it

- **RP2040** (U1, QFN-56) with a W25Q128JVSIQ flash (U2, 16 MB), 12 MHz crystal (Y1), the usual decoupling,
  BOOT (SW1, QSPI_SS to GND through 1k) and RESET (SW2) buttons, and SWDIO/SWCLK test pads (TP5, TP6). The RP2040's
  ROM has a UF2 bootloader (hold BOOT at reset, or double-tap RESET once firmware supports it), so flashing stays
  drag-and-drop.
- **77 keys**, 6.25u spacebar only (no split layout), Kailh-pattern hot-swap sockets (HanElectricity
  CPG151101S11-2, C49352235) on every key, a 1N4148W per key, COL2ROW.
- **77 SK6812MINI-E** reverse-mount LEDs (LED1-LED77), one under each key at the switch's LED window
  (key centre + 5.08 mm), through a 3.4 mm light cutout, each with a 100 nF cap. The chain is serpentine:
  LED1 is Delete, the top row runs right to left, the next left to right, and so on; LED77 is Right arrow.
- **LED power:** an AO3401A (Q1) switches VBUS to LED_5V, driven by a 2N7002 (Q2) from GPIO21 (LED_EN, 100k
  pull-down so the LEDs stay off through reset and USB suspend). R6/C19 slow its turn-on so the 77 LED caps and
  C18 (22 µF) don't pull VBUS down. A 74AHCT1G125 (U4) powered from LED_5V lifts the 3.3 V data to 5 V (33 Ω out).
- **3.3 V** from an ME6211C33 (U3, 500 mA) on VBUS.
- **Connectors**, all at the edge with their mouths out, in rev 1.4's places:
  - J1 (JST-SH 6P) to the hub board or the old USB-C board: 1 VBUS, 2 D−, 3 D+, 4 GND, 5-6 not connected.
    The old daughterboard (`hardware/Dachshund70-USB`) still fits for a Lite build; its slide switch does nothing.
  - J4 (FH12-12S FFC) to the screen board: 1 +3V3, 2 +3V3, 3 GND, 4 TFT_SCK, 5 GND, 6 GND, 7 +3V3, 8 TFT_DC,
    9 TFT_BL, 10 GND, 11 TFT_MOSI, 12 GND. There's no CS line (the screen board ties the panel's CS low; it is the
    only device on that SPI bus) and no 5 V (the panel and its backlight run from 3.3 V).
  - J5 (JST-SH 5P) encoder, unchanged: 1 COL14, 2 ENC_A, 3 GND, 4 ENC_B, 5 ENC_SW (push switch at row 0, col 14
    through D114).

## Pin map (RP2040)

| GPIO | Net | | GPIO | Net |
|---|---|---|---|---|
| 0-11 | COL0-COL11 | | 21 | LED_EN |
| 12 | ROW0 | | 22 | ENC_A |
| 13 | ROW1 | | 23 | ENC_B |
| 14 | ROW2 | | 24 | LED data (PIO, through U4) |
| 15 | ROW3 | | 25 | TFT backlight (PWM) |
| 16 | COL12 | | 26 | TFT SCK (SPI1) |
| 17 | COL13 | | 27 | TFT MOSI (SPI1 TX) |
| 18 | COL14 | | 28 | not connected (was TFT CS) |
| 19 | ROW4 | | 29 | TFT DC |
| 20 | ROW5 | | | |

Rows and columns follow `boards/Dachshund70/README.md`'s matrix (row 5, col 6 is the 6.25u spacebar; row 5 cols 4
and 8 are gone with the split layout).

## Power budget

The board is bus-powered through the hub (or a plain USB-C board). 77 LEDs at full white would draw about 2.8 A,
far over USB's 500 mA (or 900 mA / 1.5 A on hosts that offer it), and on the hub the keyboard shares the PC's port
with the back ports. The firmware must cap the LEDs' total brightness, for example to about 300 mA at the default,
and turn LED_EN off in USB suspend. There's no battery, so the old battery-life limits no longer apply.

## Layout notes

- Two layers. The matrix runs mostly as horizontal tracks on the front and vertical ones on the back; the RP2040's
  left and right sides fan out in a staircase to two staggered via columns (`tools/prefan.py`).
- Ground: a pour on both layers, with one via per cut-off pour area (no via grid), placed by `tools/stitch.py`,
  plus short ground links where a pad sat in a cut-off island. Ground pads too boxed in for two thermal spokes join
  the pour solid (rule in `Dachshund70-Wired.kicad_dru`).
- Netclasses: Default 0.15 mm track and clearance (inside JLCPCB's 2-layer limits), Power (LED_5V, VBUS) 0.5 mm.
- Crowded reference texts (the column's passives, the stabilisers) are hidden; the fab layer keeps them.

## How it was made

The schematic was built with the KiCad MCP (Konnect): parts placed and checked through it, with the repetitive key,
LED and label grids written by script. Freerouting couldn't run on this PC, so the board was routed by a small grid
router in `tools/` (multi-source Dijkstra on a 0.1 mm grid, both layers, rip-up and reroute, then dead-end pruning).
To rebuild from the schematic: `tools/pipeline.sh` (placement in `tools/sync.py`, routing plan `tools/plan2.json`).
Its paths point at a scratch folder; edit `S=` first.

## Open checks

- USB D+/D− are routed as ordinary 0.15 mm tracks, not an impedance-controlled pair. Fine for 12 Mbit/s full speed
  over a few centimetres.
- 3D models and the case: the hub board and the screen board change the case (`SCHEDULED_TASKS.md`).
