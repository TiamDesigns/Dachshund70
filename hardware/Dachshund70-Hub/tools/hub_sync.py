# Loads every schematic footprint into the wired mainboard with its nets, and places it.
import pcbnew,re,sys,json,os
S,BRD=sys.argv[1],sys.argv[2]
net=open(S+'/hub.net',encoding='utf8').read()
STOCK='C:/Program Files/KiCad/10.0/share/kicad/footprints/'
PROJ={'Keyswitch':'hardware/Dachshund70/lib/keyswitch.pretty','Dachshund70':'hardware/Dachshund70/lib/Dachshund70.pretty'}
def tok(s):
    i=0;out=[];st=[out]
    for m in re.finditer(r'\(|\)|"((?:[^"\\]|\\.)*)"|[^\s()"]+',s):
        t=m.group(0)
        if t=='(': n=[];st[-1].append(n);st.append(n)
        elif t==')': st.pop()
        elif t.startswith('"'): st[-1].append(m.group(1).replace('\\"','"'))
        else: st[-1].append(t)
    return out[0]
T=tok(net)
def find(l,k): return [x for x in l if isinstance(x,list) and x and x[0]==k]
comps={}
for c in find(find(T,'components')[0],'comp'):
    d={x[0]:x[1:] for x in c[1:] if isinstance(x,list)}
    flds={}
    for fl in find(c,'fields'):
        for f in find(fl,'field'):
            flds[f[1][1]]=f[2] if len(f)>2 else ''
    comps[d['ref'][0]]=dict(value=d['value'][0],fp=d.get('footprint',[''])[0],ts=d['tstamps'][0],fields=flds)
pads={}
for n in find(find(T,'nets')[0],'net'):
    name=find(n,'name')[0][1]
    for nd in find(n,'node'):
        pads[(find(nd,'ref')[0][1],find(nd,'pin')[0][1])]=name
b=pcbnew.LoadBoard(BRD)
pass
nets={}
def getnet(name):
    if name not in nets:
        ni=pcbnew.NETINFO_ITEM(b,name); b.Add(ni); nets[name]=ni
    return nets[name]
# Hub board: 80 x 22 mm, every port's mouth on the back edge (y = 0), parts on top.
W, H = 80.0, 22.0
def edge(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
    s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1))); s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    s.SetWidth(pcbnew.FromMM(0.05)); b.Add(s)
for a, c in (((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))): edge(*a, *c)
place = {r: (x, y, a, False) for r, (x, y, a) in {
 'J3': (9.0, 6.6, 180), 'J4': (26.0, 6.6, 180), 'J5': (41.0, 2.375, 180), 'J1': (65.0, 2.375, 180),
 'H1': (53.0, 5.0, 0), 'H2': (75.5, 15.5, 0), 'J2': (64.0, 18.5, 0),
 'U1': (53.0, 15.0, 0), 'Y1': (48.9, 10.4, 90), 'C3': (56.2, 18.8, 90), 'C4': (57.4, 18.8, 90), 'C5': (52.4, 11.0, 0), 'C6': (54.9, 11.0, 0),
 'U3': (34.0, 17.5, 0), 'R4': (34.0, 20.2, 0), 'C8': (30.6, 17.5, 90), 'C1': (37.4, 16.0, 90), 'C2': (39.8, 16.0, 90), 'C7': (42.2, 16.0, 90),
 'U4': (9.0, 17.5, 90), 'U5': (26.0, 17.5, 90), 'U6': (44.2, 12.2, 90), 'U2': (60.0, 11.4, 90),
 'R5': (38.5, 8.9, 90), 'R6': (42.4, 8.9, 90), 'R1': (63.0, 9.2, 90), 'R2': (68.0, 9.2, 90),
 'F1': (71.5, 9.5, 90), 'FB1': (73.5, 5.0, 90)}.items()}
miss=[]
for ref,c in comps.items():
    lib,name=c['fp'].split(':')
    path=PROJ.get(lib, STOCK+lib+'.pretty')
    fp=pcbnew.FootprintLoad(path,name)
    if fp is None: miss.append((ref,c['fp'])); continue
    fp.SetReference(ref); fp.SetValue(c['value']); fp.SetFPIDAsString(c['fp'])
    fp.SetPath(pcbnew.KIID_PATH('/'+c['ts']))
    for k,v in c['fields'].items():
        if k in ('LCSC','MPN','Description','Datasheet'):
            fp.SetField(k,v)
    for fld in fp.GetFields():
        if fld.GetName() in ('LCSC','MPN','Description','Datasheet'): fld.SetVisible(False)
    if ref.startswith('LED') or (ref.startswith('C') and ref[1:].isdigit() and 101<=int(ref[1:])<=177):
        fp.Reference().SetVisible(False)   # 154 per-key parts: no room for their names under the keys
    b.Add(fp)
    for p in fp.Pads():
        nm=pads.get((ref,p.GetNumber()))
        if nm: p.SetNet(getnet(nm))
    if ref in place:
        x,y,a,back=place[ref]
        if back: fp.Flip(fp.GetPosition(),pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x),pcbnew.FromMM(y)))
        fp.SetOrientationDegrees(a)
    else: miss.append((ref,'noplace'))
b.Save(BRD)
print('fps',len(list(b.GetFootprints())),'nets',len(nets),'miss',miss)
