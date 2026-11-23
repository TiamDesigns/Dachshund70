set -e
S="C:/Users/tiamb/AppData/Local/Temp/claude/7bb13776520ca846/c86065fe-51b3-4b75-b864-e09e96020a3c/scratchpad"
KP="/c/Program Files/KiCad/10.0/bin/python.exe"; KC="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
B=hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_pcb
q(){ grep -v "handler\|leak" || true; }
"$KC" sch export netlist -o "$S/wired.net" hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_sch >/dev/null
cp "$S/template.kicad_pcb" "$S/placed.kicad_pcb"
"$KP" "$S/sync.py" "$S" "$S/placed.kicad_pcb" 2>&1 | q
"$KP" "$S/export_geom.py" "$S/placed.kicad_pcb" "$S/geom.json" 2>&1 | q
(cd "$S" && python prefan.py geom.json pre.json && python router.py geom.json plan2.json routes6.json pre.json > route6.log 2>&1; tail -1 route6.log; grep -c FAIL route6.log || true)
(cd "$S" && python -c "
import json;a=json.load(open('pre.json'));b=json.load(open('routes6.json'))
json.dump({'tracks':a['tracks']+b['tracks'],'vias':a['vias']+b['vias']},open('routes_all.json','w'))")
cp "$S/placed.kicad_pcb" $B
"$KP" "$S/apply_routes.py" $B "$S/routes_all.json" 2>&1 | q
"$KP" "$S/prune.py" $B 2>&1 | q
"$KP" "$S/pour.py" $B 2>&1 | q
"$KP" "$S/stitch.py" $B 2>&1 | q
"$KP" "$S/finalfill.py" $B 2>&1 | q
"$KC" pcb drc --severity-all --schematic-parity --format json -o "$S/drc10.json" $B >/dev/null 2>&1 || true
python - "$S" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1]+'/drc10.json'))
print(collections.Counter(x['type'] for x in d['violations']))
u=d['unconnected_items']; print('unconn',len(u))
for x in u[:12]: print([i['description'][:45] for i in x['items']])
PY
