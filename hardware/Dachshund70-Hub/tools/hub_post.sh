S="C:/Users/tiamb/AppData/Local/Temp/claude/7bb13776520ca846/c86065fe-51b3-4b75-b864-e09e96020a3c/scratchpad"; KP="/c/Program Files/KiCad/10.0/bin/python.exe"; HB=hardware/Dachshund70-Hub/Dachshund70-Hub.kicad_pcb; q(){ grep -v -e handler -e leak || true; }
(cd "$S" && python prune_json.py hgeom.json $1 hroutes_p.json)
cp "$S/hub_placed.kicad_pcb" $HB
"$KP" "$S/apply_routes.py" $HB "$S/hroutes_p.json" 2>&1 | q
"$KP" "$S/pour.py" $HB 2>&1 | q; "$KP" "$S/stitch.py" $HB 2>&1 | q; "$KP" "$S/finalfill.py" $HB 2>&1 | q
"/c/Program Files/KiCad/10.0/bin/kicad-cli.exe" pcb drc --severity-all --schematic-parity --format json -o "$S/hdrc2.json" $HB >/dev/null 2>&1
python - "$S" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1]+'/hdrc2.json'))
print(collections.Counter(x['type'] for x in d['violations']),len(d['unconnected_items']),len(d['schematic_parity']))
for x in d['violations']:
    if not x['type'].startswith('silk'): print(x['type'],[i['description'][:50] for i in x['items']])
for u in d['unconnected_items']: print([i['description'][:45] for i in u['items']])
PY
