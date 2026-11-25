# Dachshund70 e-paper adapter

Rev 1.2 (2026-11-25). Joins the wired mainboard's screen connector (`hardware/Dachshund70-Wired/`, J4) to Good
Display's [GDEY027T91-FT11](https://www.good-display.com/product/611.html): a 2.7" e-paper (SSD1680, 264 × 176,
70.42 × 45.8 × 2.1 mm, picture 57.29 × 38.19 mm) with an FT6336U capacitive touch panel and a 4-LED front light. It
fits the right-hand column between the knob and the arrow keys with the picture as wide as the knob. (Rev 1.0 was
for the 3.7" GDEY037T03-FT21, rev 1.1 for the 2.9" GDEY029T94-FT01; both were too big for the case.) The panel comes
bare on three FPCs, so this board carries the e-paper's booster circuit and the front light's driver. KiCad 10,
2 layers, 44 × 30 mm (narrower than the panel, to sit behind it), every part on the top. ERC 0; DRC clean
(0 violations, 0 unconnected, schematic parity clean). Not ordered, not tested.

## Connectors

All are Hirose FH12 0.5 mm FPC sockets (bottom contact). J3 (touch), J2 (e-paper) and J4 (front light) face the top
edge (y = 100), at x 105.4, 122 and 138.6; J1 (mainboard) faces the bottom edge (y = 130) at x 122.

| Ref | To | Pins |
|---|---|---|
| J1 | mainboard J4, FH12-16S (16-way 0.5 mm FFC) | 1-2 +3V3, 3 GND, 4 TP_RST, 5 GND, 6 TP_INT, 7 TP_SCL, 8 TP_SDA, 9 FL_PWM, 10 not used (TP_EN), 11 EPD_BUSY, 12 EPD_RST, 13 EPD_DC, 14 EPD_MOSI, 15 EPD_SCK, 16 EPD_CS |
| J2 | e-paper FPC, FH12-24S | Good Display's standard 24-pin pinout (SSD1680): 2 GDR, 3 RESE, 5 VDHR, 8 BS (to GND: 4-wire SPI), 9 BUSY, 10 RST, 11 D/C, 12 CS, 13 SCL, 14 SDA, 15 VDDIO, 16 VDD, 17 GND, 18 VDDD, 19 VPP, 20 VSH, 21 VGH, 22 VSL, 23 VGL, 24 VCOM; 1, 4, 6 and 7 not connected |
| J3 | touch FPC, FH12-6S | 1 GND, 2 +3V3, 3 TP_RST, 4 TP_INT, 5 TP_SDA, 6 TP_SCL (pull-ups are on the mainboard) |
| J4 | front-light FPC, FH12-6S | 1-2 LED+ (FL_VOUT), 3-4 not connected, 5-6 LED- (FL_FB) |

## Circuits

- **E-paper booster**, Good Display's reference for its 24-pin panels: L1 10 µH (2520, 1 A), Q1 Si1308EDL switched by
  GDR with R1 2.2 Ω current sense on RESE, D3 to VGH, and the C10 / D1 / D2 charge pump to VGL (MBR0530 Schottkys),
  with 1 µF (50 V) on VDHR, VDDD, VPP, VSH, VGH, VSL, VGL, VCOM and the 3.3 V supply.
- **Front light**: the FT11's four LEDs are in series (up to 12 V, 15 mA), so U1 (TPS61040, LCSC C7722) boosts 3.3 V
  and regulates their current: L2 10 µH, D4 MBR0530, C13 1 µF 50 V on the output, R2 82 Ω from the LEDs' cathode to
  ground (1.233 V / 82 Ω = 15 mA). FL_PWM (GPIO40) drives the TPS61040's EN to dim it with PWM (keep it under about
  1 kHz); R3 (100k) holds it off at reset.
- **Touch**: straight through, with C12 (100 nF) at J3.

## Layout

Two layers with ground pours on both, every ground pad joined solid (`Dachshund70-EPD.kicad_dru`), and one via per
cut-off pour area. Routed with the mainboard's grid router (`tools/`: placement in `epd_place.json`, net order in
`plan.json`, `epost.sh` for prune, pour, stitch and DRC).

## Open checks

- **Touch and front-light pinouts.** Good Display's drawing shows the tails but not their pin tables, which are in the
  FT11's spec PDF ([companyfile 1670](https://www.good-display.com/companyfile/1670.html)), not readable online. J3 and
  J4 assume the pinouts of Good Display's other touch/front-light panels. Check both before ordering, and whether
  either tail arrives contacts-up (then turn the socket or reverse its pin order).
- **Front-light open circuit.** The TPS61040 has no over-voltage limit: with the LEDs unplugged its output can rise
  to the switch's 28 V rating. C13 is 50 V; don't run the light without the panel attached.
- **FPC tails.** The 24-pin tail is 12.5 mm wide and about 30 mm long, the touch tail about 36 mm, both leaving the
  panel's bottom end; check they reach J2 and J3 when folded behind the panel in the case model.
- **Booster values.** From Good Display's 24-pin reference (DESPI-C02); check R1 (2.2 Ω here) and L1 against the
  panel's datasheet.
- **FFC to the mainboard.** J1's pin n is the mainboard J4's pin n; pick the FFC type (same-side or opposite-side
  contacts) for how the two boards face each other in the case.
- **Mounting.** No holes: the case decides how the board and panel are held.
