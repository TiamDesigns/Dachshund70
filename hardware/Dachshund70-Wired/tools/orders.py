# Tries the column routing in several net orders and keeps the one with the fewest failed connections.
import json, random, subprocess, sys, re, shutil
base = json.load(open('plan2350.json'))
pri = lambda n: (0 if n.startswith(('/ROW', '/COL')) else 1 if n.startswith('/QSPI') else 2 if n.startswith(('/DISP', '/TP_')) else 4 if n in ('+3V3', 'LED_5V', 'VBUS', '+1V1') else 3)
best = None
for seed in range(int(sys.argv[1])):
    rnd = random.Random(seed); p = [list(x) for x in base]
    if seed:
        groups = {}
        for x in p: groups.setdefault(pri(x[0]), []).append(x)
        for g in groups.values(): rnd.shuffle(g)
        keys = sorted(groups)
        if seed % 2: keys = [1, 3, 0, 2, 4]   # some runs route the flash and the misc lines before the matrix
        p = [x for k in keys for x in groups.get(k, [])]
    json.dump(p, open('plan_try.json', 'w'))
    with open('try.log', 'w') as f:
        subprocess.run([sys.executable, 'router.py', 'gnew.json', 'plan_try.json', 'r_try.json', 'pre2350.json', 'ex_c.json'], stdout=f, stderr=subprocess.STDOUT)
    fails = len({m for m in re.findall(r"FAIL \('([^']+)', '([^']+)'\)", open('try.log').read())})
    print(seed, fails, flush=True)
    if best is None or fails < best[0]:
        best = (fails, seed); shutil.copy('r_try.json', 'r_best.json'); shutil.copy('try.log', 'best.log'); shutil.copy('plan_try.json', 'plan_best.json')
    if fails == 0: break
print('best', best)
