set -e
S="${S:?set S to a scratch folder holding these tools, template.kicad_pcb, wired.net, keys.json and ex_outp.json}"
KP="/c/Program Files/KiCad/10.0/bin/python.exe"; KC="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
B=hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_pcb
q(){ grep -v -e handler -e leak || true; }
(cd "$S" && python -c "
import json,sys;a=json.load(open('pre2350.json'));b=json.load(open(sys.argv[1]))
json.dump({'tracks':a['tracks']+b['tracks'],'vias':a['vias']+b['vias']},open('r_all.json','w'))" $1 && python prune_json.py gnew.json r_all.json r_pruned.json && python -c "
import json;a=json.load(open('pre2350.json'));b=json.load(open('r_pruned.json'))
k=lambda t:tuple(t)
st={k(t) for t in b['tracks']};sv={k(v) for v in b['vias']}
b['tracks']+=[t for t in a['tracks'] if k(t) not in st];b['vias']+=[v for v in a['vias'] if k(v) not in sv]
json.dump(b,open('r_pruned.json','w'))")
cp "$S/t2350.kicad_pcb" $B
"$KP" "$S/apply_routes.py" $B "$S/r_pruned.json" 2>&1 | q
"$KP" "$S/pour.py" $B 2>&1 | q
"$KP" "$S/stitch.py" $B 2>&1 | q
"$KP" "$S/finalfill.py" $B 2>&1 | q
"$KC" pcb drc --severity-all --schematic-parity --format json -o "$S/drc2350.json" $B >/dev/null 2>&1 || true
python "$S/drcsum.py" "$S/drc2350.json"
"$KP" "$S/rmvias.py" $B "$S/drc2350.json" 2>&1 | q
"$KC" pcb drc --severity-all --schematic-parity --format json -o "$S/drc2350.json" $B >/dev/null 2>&1 || true
python "$S/drcsum.py" "$S/drc2350.json"
