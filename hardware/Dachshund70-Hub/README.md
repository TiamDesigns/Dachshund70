# Dachshund70 USB hub board

Rev 1.0 (2026-11-24). Goes on the back of the case in place of the USB-C daughterboard, for the wired mainboard
(`hardware/Dachshund70-Wired/`). KiCad 10, 2 layers, 80 × 22 mm, every part on top, every port's mouth on the back
edge (y = 0). ERC 0; DRC clean (0 violations, 0 unconnected, schematic parity clean). Not ordered, not tested.

## Ports

| Ref | Port | Hub port | |
|---|---|---|---|
| J1 | USB-C, to the PC | upstream | CC1/CC2 5.1k pull-downs, USBLC6 (U2), 1.1 A PTC (F1) |
| J2 | JST-SH 6P, to the keyboard (mainboard J1) | 1 | 1 VBUS, 2 D−, 3 D+, 4 GND, 5-6 not connected |
| J3 | USB-A | 2 | USBLC6 (U4) |
| J4 | USB-A | 3 | USBLC6 (U5) |
| J5 | USB-C | 4 | USBLC6 (U6); 56k Rp on CC1/CC2 (default USB power, 500 mA) |

## Hub

- **CH334F** (U1, QFN-24): USB 2.0, high-speed upstream and downstream, one transaction translator per port
  (MTT), so the keyboard's full-speed traffic doesn't hold up a high-speed mouse (an 8 kHz mouse runs at high
  speed and passes straight through). All three back ports and the keyboard share the one 480 Mbit/s link to the PC.
- Bus-powered: PSELF tied low. RESET#/CDP left open (internal pull-up, as the datasheet recommends).
  OVCUR#, PWREN# and the LED pins are not used.
- 12 MHz crystal (Y1) with no load capacitors: the CH334 has them built in (datasheet 1.1).
- V5 from VBUS (10 µF + 100 nF), VDD33 from its own LDO (1 µF + 100 nF).

## Port power

The three back ports share an SY6280AAC current-limited switch (U3, always on, ISET 6.8k) with 3 × 22 µF on
its output; the keyboard port takes VBUS before the switch, so a short on a back port can't reset the keyboard.
Upstream VBUS has 10 µF at most on it (USB's inrush limit).

Everything is powered from the PC's one port: about 500 mA from a USB-A port on the PC, 1.5-3 A from a USB-C port
that offers it. The keyboard's RGB comes out of the same budget (see the mainboard README).

## Open checks

- **SY6280AAC:** the pin order in `Dachshund70-Hub.kicad_sym` (1 OUT, 2 GND, 3 ISET, 4 EN, 5 IN) and the current
  limit (6.8k, expected to give about 1 A) are from memory; check both against Silergy's datasheet before ordering.
- **USB-A footprint:** the XKB U231-091N-4BLRA00-S (C2880618) is a 9-pin (USB 3) receptacle; only pins 1-4 are
  used. Check its front edge against the drawing (placed so its mouth is flush with the board edge).
- USB D+/D− are short 0.15 mm tracks, not impedance-controlled pairs. Keep the board's track lengths short as now;
  if high-speed devices misbehave, make the pairs 90 Ω differential.
- The case needs a new back opening for 2 × USB-A, 2 × USB-C and the board's 80 mm width (case thread).
