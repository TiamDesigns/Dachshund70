# Dachshund70 encoder module

The roller encoder on its own small board, cabled to the mainboard. Introduced with mainboard Rev 1.1,
which no longer carries the encoder. KiCad 10 project, 2 layers, 1.6 mm FR4.

- **Encoder:** SW1, Bourns PEC12R-2230F-S0024 (shaft parallel to the board, 24 detents, 24 pulses per turn,
  30 mm shaft, push switch pressed along the shaft; no LCSC listing, so source it globally or solder it by hand).
  The 30 mm shaft carries the 2u roller (about 25 mm long, on 19 mm of shaft). Same body and footprint as the
  20 mm PEC12R-2220F-S0024 it replaces (`../3dmodels/Bourns_PEC12R-2x30F-S_standin.step`). Through-hole; its two
  frame tabs are on GND.
- **Cable port:** J1, JST SH 1.0 mm, 5 pins, side entry (SM05B-SRSS-TB), on the **bottom** side, its mouth facing
  +u (toward the shaft). The mainboard's J5 faces it across the notch on the same line, so the cable runs straight
  under the module: about 25 mm overall (housing end to end), 5 parallel wires with both latches on the same side,
  which makes it a reversed cable (J1 pin n to J5 pin 6 − n; the pin numbers below are matched to that). Crimp it
  from SHR-05V-S housings and SSH-003T contacts with 30–32 AWG wire, or shorten a pre-made reversed cable.
  Trim the encoder's through-hole pins to 0.5 mm or less on the bottom: the cable runs right under them (it touches
  the push switch's uncut pins in the model, 0.3 under the A/B/C pins).
- **Nothing else.** The 10 nF debounce capacitors on A and B and the push-switch diode D114 stay on the
  mainboard, so the pin map and the firmware did not change. No expansion ports on either board.

| J5 pin (mainboard) | J1 pin (module) | Net | Encoder pad | MCU pin |
| --- | --- | --- | --- | --- |
| 1 | 5 | COL14 | S1 (push switch) | matrix column 14, with diode D114 on the mainboard |
| 2 | 4 | ENC_A | A | P0.11 |
| 3 | 3 | GND | C (common) | |
| 4 | 2 | ENC_B | B | P0.12 |
| 5 | 1 | ENC_SW | S2 (push switch) | matrix row 0 through D114 |

## Geometry

Module coordinates: u runs along the shaft, toward the hub end of the board (+x of the mainboard's old
encoder); v runs across it (+y); (0, 0) is the board's top-left corner seen from above. Z is measured up
from the PCB's top face.

- Outline 22.5 (u) × 22.0 (v) mm, 1.5 mm corner radius. The right edge is the hub end of the shaft; the wheel
  starts there and the board has nothing under it.
- Encoder pad C at (15.0, 11.0). Body rear face u = 11.5, front face u = 17.5, hub to u = 22.5, shaft tip at
  u = 41.5 (30 mm shaft). Shaft axis at v = 11.0 and 10.0 mm above the PCB top.
- Two mounting holes, 2.2 mm (M2), at (2.7, 2.7) and (2.7, 19.3). The 12.5 mm-wide encoder body spans
  v 4.75 to 17.25.
- J1's pad row at u = 1.3, v = 9 (pin 1) to 13 (pin 5); its body is u 0.8 to 5.8 and its mouth faces +u, so the
  plug sits under the module's left half and the cable leaves toward +u, under the encoder (mainboard x 309.7).
  (Before round 5 it faced -u, into the mainboard's notch edge, where no plug could go in.)
- On the mainboard, J5 is on the back to the right of the corner notch: footprint at (329.8, 49.54) rot 90, pad
  row at x = 331.8 mm, y = 47.54 (pin 5) to 51.54 (pin 1), on the same line as J1 (centre y 49.54, the shaft's
  axis), mouth at x 327.3 facing -x into the notch. The two mouths are 17.6 mm apart; the cable drops 1.8 mm from
  J1 (under the module, z 1.8) to J5 (under the mainboard), and the plate is 7.4 mm above it (6.4 when it floats
  down 1 mm). The notch is open to the mainboard's top edge, x 304.0 to 326.4 mm and y 39.0 to
  57.0 mm, so the module (left edge at x 303.905) sits in it, with a 4.2 mm lobe at (306.6, 57.8) for the
  head of its lower M2 screw (its post is at y 57.82); the upper screw head is inside the notch.

## Status

DRC (kicad-cli, with schematic parity): 0 errors and 0 unconnected items. The only messages are the
library-footprint mismatch on SW1 (the board copy of the footprint is the project's own, like the mainboard's)
and the missing MPN fields that the mainboard also shows. ERC: 0. Not ordered, made or fitted.

LCSC part numbers are blank: the encoder has no LCSC listing (see PROGRESS.md, 2026-10-28), and J1's number
is still to be confirmed, so JLC would source both globally or you solder the encoder by hand.
