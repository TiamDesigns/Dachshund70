# Sets the adapter's netclasses and board rules (a fresh pcbnew board saves a default project file).
import json, sys
p = sys.argv[1]; w = json.load(open(sys.argv[2])); d = json.load(open(p))
c = dict(w['net_settings']['classes'][0]); c['name'] = 'Default'; c['clearance'] = 0.15; c['track_width'] = 0.15
pw = dict(c); pw['name'] = 'Power'; pw['track_width'] = 0.25; pw['priority'] = 0
d['net_settings']['classes'] = [c, pw]
d['net_settings']['netclass_patterns'] = [{'netclass': 'Power', 'pattern': n} for n in ('+3V3', '/SW', '/FL_K', '/FL_D', '/RESE')]
d.setdefault('board', {})['design_settings'] = w['board']['design_settings']
json.dump(d, open(p, 'w'), indent=2)
