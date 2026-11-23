set -e
S="C:/Users/tiamb/AppData/Local/Temp/claude/7bb13776520ca846/c86065fe-51b3-4b75-b864-e09e96020a3c/scratchpad"
KP="/c/Program Files/KiCad/10.0/bin/python.exe"; KC="/c/Program Files/KiCad/10.0/bin/kicad-cli.exe"
B=hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_pcb
q(){ grep -v -e handler -e leak || true; }
cp "$S/placed.kicad_pcb" $B
"$KP" "$S/apply_routes.py" $B "$S/routes_pruned.json" 2>&1 | q
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
