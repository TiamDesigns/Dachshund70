set -e
S="${S:?set S to a scratch folder holding these tools and the mainboard tools (router, prune_json, apply_routes, pour, stitch, finalfill, drcsum)}"; KP="/c/Program Files/KiCad/10.0/bin/python.exe"; KC="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
B=hardware/Dachshund70-EPD/Dachshund70-EPD.kicad_pcb
q(){ grep -v -e handler -e leak || true; }
(cd "$S" && python prune_json.py egeom.json $1 eroutes_p.json)
"$KC" sch export netlist -o "$S/epd.net" hardware/Dachshund70-EPD/Dachshund70-EPD.kicad_sch >/dev/null 2>&1
"$KP" "$S/epd_sync.py" "$S/epd.net" $B "$S/epd_place.json" 2>&1 | q
"$KP" "$S/apply_routes.py" $B "$S/eroutes_p.json" 2>&1 | q
"$KP" "$S/pour.py" $B 2>&1 | q
"$KP" "$S/stitch.py" $B 2>&1 | q
"$KP" "$S/finalfill.py" $B 2>&1 | q
python "$S/epd_pro.py" hardware/Dachshund70-EPD/Dachshund70-EPD.kicad_pro hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_pro
"$KC" pcb drc --severity-all --schematic-parity --format json -o "$S/edrc.json" $B >/dev/null 2>&1 || true
python "$S/drcsum.py" "$S/edrc.json" silk_over_copper,silk_overlap
