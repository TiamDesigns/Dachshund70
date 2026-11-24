# Re-routes the nets a router run failed on, with rip-up, on top of that run's output. usage: retry.py log routes.json out.json
import json, sys, re, subprocess, os
fails = []
for line in open(sys.argv[1]):
    m = re.match(r"FAIL \('([^']+)'", line)
    if m and m.group(1) not in fails: fails.append(m.group(1))
r = json.load(open(sys.argv[2])); r.pop('fails', None)
r['tracks'] = [t for t in r['tracks'] if t[6] not in fails]; r['vias'] = [v for v in r['vias'] if v[2] not in fails]
json.dump(r, open('ex_retry.json', 'w')); json.dump([[n, None, None] for n in fails], open('plan_retry.json', 'w'))
print('retry', fails)
if not fails:
    json.dump(r, open(sys.argv[3], 'w')); sys.exit()
with open('retry.log', 'w') as f:
    subprocess.run([sys.executable, 'router.py', 'gnew.json', 'plan_retry.json', sys.argv[3], 'pre2350.json', 'ex_retry.json'], stdout=f, stderr=subprocess.STDOUT)
print(open('retry.log').read().splitlines()[-1])
