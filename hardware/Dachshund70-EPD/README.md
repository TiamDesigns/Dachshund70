# Dachshund70 e-paper adapter

Rev 1.0 (2026-11-24). Joins the wired mainboard's screen connector (`hardware/Dachshund70-Wired/`, J4) to Good
Display's GDEY037T03-FT21: a 3.7" e-paper, 240 × 416, with an FT6336U capacitive touch panel and a front light. The
panel comes bare on three FPCs, so this board carries the e-paper's booster circuit and the front light's driver.
KiCad 10, 2 layers, 46 × 28 mm, every part on the top. ERC 0; DRC clean (0 violations, 0 unconnected, schematic
parity clean). Not ordered, not tested.

## Connectors

All are Hirose FH12 0.5 mm FPC sockets (bottom contact). The three panel sockets face one long edge (y = 100), the
mainboard socket the other.

| Ref | To | Pins |
|---|---|---|
| J1 | mainboard J4, FH12-16S (16-way 0.5 mm FFC) | 1-2 +3V3, 3 GND, 4 TP_RST, 5 GND, 6 TP_INT, 7 TP_SCL, 8 TP_SDA, 9 FL_PWM, 10 not used (TP_EN), 11 EPD_BUSY, 12 EPD_RST, 13 EPD_DC, 14 EPD_MOSI, 15 EPD_SCK, 16 EPD_CS |
| J2 | e-paper FPC, FH12-24S | Good Display's 24-pin pinout (UC8253): 2 GDR, 3 RESE, 5 VDHR, 8 BS (to GND: 4-wire SPI), 9 BUSY, 10 RST, 11 D/C, 12 CS, 13 SCL, 14 SDA, 15 VDDIO, 16 VDD, 17 GND, 18 VDDD, 19 VPP, 20 VSH, 21 VGH, 22 VSL, 23 VGL, 24 VCOM; 1, 4, 6 and 7 not connected |
| J3 | touch FPC, FH12-6S | 1 GND, 2 +3V3, 3 TP_RST, 4 TP_INT, 5 TP_SDA, 6 TP_SCL (pull-ups are on the mainboard) |
| J4 | front-light FPC, FH12-6S | 1-2 LED+ (+3V3), 3-4 not connected, 5-6 LED− |

## Circuits

- **E-paper booster**, Good Display's reference for its 24-pin panels: L1 10 µH (2520, 1 A), Q1 Si1308EDL switched by
  GDR with R1 2.2 Ω current sense on RESE, D3 to VGH, and the C10 / D1 / D2 charge pump to VGL (MBR0530 Schottkys),
  with 1 µF (50 V) on VDHR, VDDD, VPP, VSH, VGH, VSL, VGL, VCOM and the 3.3 V supply.
- **Front light**: nine LEDs in parallel in the panel, Vf 2.5-3.1 V, 60 mA typical. Q2 (AO3400A) switches their
  cathodes through R2 (15 Ω, which keeps the current under about 55 mA at the lowest Vf), driven by FL_PWM from the
  RP2350 (GPIO40), with R3 (100k) holding it off at reset. Dim it with PWM.
- **Touch**: straight through, with C12 (100 nF) at J3.

## Layout

Two layers with ground pours on both, every ground pad joined solid (`Dachshund70-EPD.kicad_dru`), and one via per
cut-off pour area. Routed with the mainboard's grid router (`tools/`: placement in `epd_place.json`, net order in
`plan.json`, `epost.sh` for prune, pour, stitch and DRC).

## Open checks

- **FPC orientation.** The panel's tails must reach J2, J3 and J4 with their contacts facing the sockets' contacts
  (bottom contact). Check each tail's length, bend and contact side against Good Display's drawing and the case
  model before ordering; turn a socket round, or mirror its pin order, if a tail arrives face up.
- **Booster values.** From Good Display's 24-pin reference (DESPI-C02); check R1 (2.2 Ω here) and the inductor
  against GDEY037T03's own datasheet.
- **FFC to the mainboard.** J1's pin n is the mainboard J4's pin n; pick the FFC type (same-side or opposite-side
  contacts) for how the two boards face each other in the case.
- **Mounting.** No holes yet: the case thread decides how the board and panel are held.
