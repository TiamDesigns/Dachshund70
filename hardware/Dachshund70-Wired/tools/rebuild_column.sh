set -e
S="${S:?set S to a scratch folder holding these tools, template.kicad_pcb, wired.net, keys.json and ex_outp.json}"; KP="/c/Program Files/KiCad/10.0/bin/python.exe"
q(){ grep -v -e handler -e leak || true; }
cp "$S/template.kicad_pcb" "$S/t2350.kicad_pcb"
"$KP" "$S/sync.py" "$S" "$S/t2350.kicad_pcb" 2>&1 | q
"$KP" "$S/export_geom.py" "$S/t2350.kicad_pcb" "$S/gnew.json" 2>&1 | q
(cd "$S" && python prefan.py gnew.json pre2350.json && python comps.py gnew.json ex_outp.json ex_c.json ex_fx.json && python -c "import json;a=json.load(open('pre2350.json'));b=json.load(open('ex_fx.json'));json.dump({'tracks':a['tracks']+b['tracks'],'vias':a['vias']+b['vias']},open('pre2350.json','w'))" && python router.py gnew.json plan_column.json r2350.json pre2350.json ex_c.json > r2350.log 2>&1; tail -1 r2350.log)
bash "$S/post.sh" r2350.json | grep -v -e silk_ -e lib_footprint -e "^pass" | tail -4
B=hardware/Dachshund70-Wired/Dachshund70-Wired.kicad_pcb
"$KP" "$S/export_geom.py" $B "$S/gfin.json" 2>&1 | q
(cd "$S" && python - <<'PY'
import json
g=json.load(open('gfin.json')); pre=json.load(open('pre2350.json'))
pt={tuple(t) for t in pre['tracks']}; pv={tuple(v) for v in pre['vias']}
T=[t for t in g['tracks'] if tuple(t) not in pt]
V=[[v[0],v[1],v[3]] for v in g['vias'] if (v[0],v[1],v[3]) not in pv]
json.dump({'tracks':T,'vias':V},open('ex_fin.json','w'))
PY
MAXRIP=0 python router.py gnew.json plan_gnd.json r_gnd.json pre2350.json ex_fin.json > rg.log 2>&1; grep -c FAIL rg.log || true)
bash "$S/post.sh" r_gnd.json | grep -v -e silk_ -e lib_footprint -e "^pass"
