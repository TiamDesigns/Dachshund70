"""Simulate the Dachshund70 power path in ngspice and print a results table.

    python hardware/sim/power-path/run.py [--out DIR]

Needs ngspice on PATH (KiCad ships it; or set NGSPICE). The circuit is in
power_path.lib; each case below sets its parameters. See README.md.
"""
import argparse
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
NGSPICE = os.environ.get("NGSPICE", "ngspice")

NOMINAL = dict(VHOST=5.0, RCABLE=0.15, LCABLE=0.5e-6, RFUSE=0.25, VCELL=3.7, RCELL=0.15, BATT=1, SWON=1,
               R3=10e3, ILEAK=0.0, INRF=0.03, ILED=0.0, LEDON=0, QVTO=-0.9,
               TPLUG=100.0, TUNPLUG=101.0)
WORST_USB = dict(VHOST=4.75, RCABLE=0.25, RFUSE=0.6)   # USB 2.0 port minimum, long cable, hot fuse
LEDS_MAX = dict(ILED=0.216, LEDON=1)                     # 6 LEDs, all channels full (about 12 mA each)

VECS = ["v(vsys)", "v(vbus)", "v(vbat)", "v(vbat_sw)", "v(led_vdd)", "i(vihost)", "i(vibat)"]


def simulate(params, tstop=3.0, tmax=1e-3):
    p = dict(NOMINAL)
    p.update(params)
    with tempfile.TemporaryDirectory() as tmp:
        data = os.path.join(tmp, "out.txt")
        lines = ["* case", *(f".param {k}={v}" for k, v in p.items()),
                 f".include {os.path.join(HERE, 'power_path.lib')}",
                 f".tran 10u {tstop} 0 {tmax}",
                 ".options reltol=1e-4",
                 ".control", "set wr_singlescale", "set wr_vecnames", "run",
                 f"wrdata {data} {' '.join(VECS)}", ".endc", ".end"]
        cir = os.path.join(tmp, "case.cir")
        with open(cir, "w") as f:
            f.write("\n".join(lines) + "\n")
        r = subprocess.run([NGSPICE, "-b", cir], capture_output=True, text=True)
        if not os.path.exists(data):
            raise SystemExit(f"ngspice failed:\n{r.stdout}\n{r.stderr}")
        rows = open(data).read().split("\n")
    head = rows[0].split()
    cols = {h: [] for h in head}
    for row in rows[1:]:
        if row.strip():
            for h, v in zip(head, row.split()):
                cols[h].append(float(v))
    return cols


def at(c, key, t):
    ts = c["time"]
    i = min(range(len(ts)), key=lambda k: abs(ts[k] - t))
    return c[key][i]


def window(c, key, t0, t1):
    return [v for t, v in zip(c["time"], c[key]) if t0 <= t <= t1]


def steady(c):
    t = c["time"][-1]
    return {k: at(c, k, t) for k in VECS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write a CSV of each transient case here")
    args = ap.parse_args()
    report = []

    def line(name, text):
        report.append(f"{name:<46} {text}")
        print(report[-1], flush=True)

    print("== Steady state, battery only (switch on, no USB)")
    for vcell in (4.2, 3.7, 3.3, 3.0):
        for leds in (False, True):
            c = simulate(dict(VCELL=vcell, **(LEDS_MAX if leds else {})), tstop=5.0, tmax=5e-3)
            s = steady(c)
            line(f"cell {vcell} V, LEDs {'max' if leds else 'off'}",
                 f"VSYS {s['v(vsys)']:.3f} V (drop {vcell - s['v(vsys)']:.3f}), LED_VDD {s['v(led_vdd)']:.3f} V, "
                 f"cell current {s['i(vibat)'] * 1000:.0f} mA")

    print("== Steady state, USB")
    usb_cases = [("USB 5.0 V, no cell", dict(BATT=0, TPLUG=0)),
                 ("USB 4.75 V worst, no cell", dict(BATT=0, TPLUG=0, **WORST_USB)),
                 ("USB 5.0 V, cell 3.7 V charging", dict(TPLUG=0)),
                 ("USB 4.75 V worst, cell 3.7 V charging", dict(TPLUG=0, **WORST_USB)),
                 ("USB 4.75 V worst, cell 4.15 V", dict(TPLUG=0, VCELL=4.15, **WORST_USB)),
                 ("USB 5.0 V, cell 3.7 V, switch off", dict(TPLUG=0, SWON=0))]
    for name, prm in usb_cases:
        for leds in (False, True):
            c = simulate(dict(prm, **(LEDS_MAX if leds else {})), tstop=0.05)
            s = steady(c)
            line(f"{name}, LEDs {'max' if leds else 'off'}",
                 f"VBUS {s['v(vbus)']:.3f}, VSYS {s['v(vsys)']:.3f}, LED_VDD {s['v(led_vdd)']:.3f} V, "
                 f"host {s['i(vihost)'] * 1000:.0f} mA, cell {s['i(vibat)'] * 1000:+.0f} mA")

    print("== Plug in at 0.5 s (cell 3.7 V): inrush and VBUS overshoot")
    for lc, rc in ((0.5e-6, 0.15), (1e-6, 0.1), (1e-6, 0.05), (2e-6, 0.05)):
        for batt in (1, 0):
            c = simulate(dict(TPLUG=0.5, LCABLE=lc, RCABLE=rc, BATT=batt), tstop=0.52, tmax=2e-7)
            ih = window(c, "i(vihost)", 0.5, 0.52)
            vb = window(c, "v(vbus)", 0.5, 0.52)
            line(f"cable {lc * 1e6:.1f} uH {rc} ohm, {'cell 3.7 V' if batt else 'no cell'}",
                 f"peak host current {max(ih):.2f} A, VBUS peak {max(vb):.2f} V")

    print("== Unplug at 0.5 s: VSYS dip while Q1 waits for VBUS to fall")
    for vcell in (3.7, 3.3, 3.0):
        for r3 in (100e3, 10e3):
            for vto in (-0.9, -1.3):
                for leds in (False, True):
                    prm = dict(VCELL=vcell, R3=r3, QVTO=vto, TPLUG=0, TUNPLUG=0.5, **(LEDS_MAX if leds else {}))
                    c = simulate(prm, tstop=2.5, tmax=2e-4)
                    vs = window(c, "v(vsys)", 0.5, 2.5)
                    ts = window(c, "time", 0.5, 2.5)
                    vmin = min(vs)
                    final = vs[-1]
                    below = [t for t, v in zip(ts, vs) if v < final - 0.1]
                    dur = (max(below) - 0.5) if below else 0.0
                    line(f"cell {vcell} V, R3 {r3 / 1e3:.0f}k, Vth {vto}, LEDs {'max' if leds else 'off'}",
                         f"VSYS min {vmin:.3f} V, back within 0.1 V of {final:.3f} V after {dur * 1000:.0f} ms")
                    if args.out:
                        os.makedirs(args.out, exist_ok=True)
                        fn = f"unplug_{vcell}V_R3_{r3 / 1e3:.0f}k_vth{-vto}_leds{int(leds)}.csv"
                        with open(os.path.join(args.out, fn), "w") as f:
                            f.write("time," + ",".join(VECS) + "\n")
                            for i in range(len(c["time"])):
                                f.write(",".join(f"{c[k][i]:.6g}" for k in ["time", *VECS]) + "\n")

    print("== Battery only: extra D8 leakage (on top of the model's ~20 uA) pulling Q1's gate up through R3")
    for leak in (0.0, 10e-6, 30e-6, 100e-6, 300e-6):
        for r3 in (100e3, 10e3):
            c = simulate(dict(VCELL=3.5, ILEAK=leak, R3=r3, **LEDS_MAX), tstop=3.0, tmax=5e-3)
            s = steady(c)
            line(f"extra leak {leak * 1e6:.0f} uA, R3 {r3 / 1e3:.0f}k, cell 3.5 V, LEDs max",
                 f"VBUS {s['v(vbus)']:.2f} V, Vgs {s['v(vbus)'] - s['v(vsys)']:.2f} V, VSYS {s['v(vsys)']:.3f} V")

    with open(os.path.join(args.out or tempfile.gettempdir(), "results.txt"), "w") as f:
        f.write("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
