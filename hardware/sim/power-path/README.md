# Power-path simulation (ngspice)

A circuit-level model of how the keyboard gets its power: the USB-C daughterboard (F1 polyfuse,
USBLC6 clamp, SW1 power switch), the 6-pin cable, and the mainboard's load-sharing path (D8 B5819W
from VBUS, Q1 AO3401A from the switched battery, R3 on Q1's gate), the MCP73831 charger, the
nRF52840's VDDH load and the LED string behind U3. It runs the cases that matter before ordering:
battery only, USB only, USB while charging, plugging in and unplugging.

It can't simulate the nRF52840 itself or the firmware: the module is a fixed current load (30 mA:
module, radio and display), and the LEDs are 216 mA when on (6 LEDs, every channel full). Part
models are fitted to datasheet typicals, so trust the results to tens of millivolts.

## Run

    python hardware/sim/power-path/run.py [--out DIR]

Needs `ngspice` on PATH (KiCad installs it; on Windows it's in `C:\Program Files\KiCad\10.0\bin`, or set
`NGSPICE`). It takes about a minute and prints the table in `results.txt`. With `--out` it also writes a
CSV of each unplug transient for plotting. Change a case's parameters in `run.py`; the circuit and every
parameter are described in `power_path.lib`.

## Results (2026-11-09, R3 = 10k)

- **Battery only:** VSYS is 15–35 mV below the cell with the LEDs off, and 0.11–0.19 V below it with
  every LED on full (cell resistance, the cable twice, SW1 and Q1). At a 3.0 V cell with the LEDs on,
  VSYS is 2.81 V and the LEDs dim, as expected.
- **USB only:** VSYS is 4.71 V (LEDs off) or 4.52 V (on) from a 5.0 V port. From a worst-case 4.75 V
  port with a long cable and a hot polyfuse, it's 4.16 V with the LEDs on, which is still fine for VDDH
  (2.5–5.5 V) and the LEDs.
- **USB while charging (303 mA):** the host supplies 336 mA with the LEDs off, or **552 mA with every
  LED on full**. That's above the 500 mA the board asks for in its USB descriptor, though under F1's
  750 mA hold current. Only all LEDs at full white while charging gets there. Q1 stays off, and the
  cell doesn't feed VSYS, even at 4.15 V from a weak port.
- **Plugging in:** the hot-plug current peaks at 4–8 A for a few microseconds (9.4 µF on VBUS, plus the
  VSYS caps through D8). That's normal for USB. VBUS doesn't overshoot past 5.7 V even with a 2 µH,
  low-resistance cable; the nRF's VBUS pin is rated to 5.8 V and the charger to 7 V.
- **Unplugging:** VSYS dips to about 0.6 V below the cell (Q1's body diode) until VBUS falls far enough
  to turn Q1 on. With R3 = 10k that takes 11–47 ms. With the old 100k it took 0.2–1.9 s. With a
  high-threshold Q1 (Vth −1.3 V) and a cell at 3.3 V or less, Q1 never turned on at all, and VSYS stayed
  on the body diode (2.69 V from a 3.3 V cell, 2.38 V from 3.0 V, below VDDH's 2.5 V minimum).
- **Why R3 is now 10k:** on battery, D8's reverse leakage flows into VBUS and R3, which lifts Q1's gate.
  A 1 A Schottky leaks tens of µA at room temperature (the model's 20 µA; the datasheet only promises
  under 1 mA at 40 V), and the leakage roughly doubles every 10 °C. With 100k, 20 µA already holds VBUS at
  2.0 V (Vgs −1.36 V), and 10 µA more turns Q1 off, so the keyboard runs through the body diode: 0.6 V
  lost, VSYS 2.83 V from a 3.5 V cell. With 10k, Q1 stays fully on up to about 100 µA of extra leakage.
  The cost is 0.5 mA from USB through R3, and nothing on battery.

## Bring-up check

On battery with USB unplugged, measure TP1 (VBUS) and TP4 (VSYS). VBUS should be a few hundred mV
at most, and VSYS within 50 mV of TP3 (VBAT_SW) at idle. If VBUS is within about 1.5 V of VSYS, Q1 is
only half on.
