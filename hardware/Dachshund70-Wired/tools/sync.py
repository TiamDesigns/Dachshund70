# Loads every schematic footprint into the wired mainboard with its nets, and places it.
import pcbnew,re,sys,json,os
S,BRD=sys.argv[1],sys.argv[2]
net=open(S+'/wired.net',encoding='utf8').read()
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
K=json.load(open(S+'/keys.json')); keys={k[0]:k for k in K['keys']}; chain=K['chain']
rowsy=sorted(set(round(k[2],2) for k in K['keys']))
ledidx={r:i+1 for i,r in enumerate(chain)}
place={}
for r,k in keys.items():
    X,Y=k[1],k[2]; place[r]=(X,Y,0,False)
    place['D'+r[2:]]=(X-7.5,Y+4.0,90,True)
    rev=rowsy.index(round(Y,2))%2==0   # chain runs right to left on rows 0, 2, 4
    n=ledidx[r]
    place[f'LED{n}']=(X,Y+5.08,180 if rev else 0,True)
    place[f'C{100+n}']=(X+5.0,Y+5.08,90,True)
for r,xy in {'ST1':(286.7,73.338),'ST2':(284.319,111.438),'ST3':(41.431,130.488),'ST4':(150.969,149.538)}.items(): place[r]=(*xy,0,False)
col={ # MCU column, all on the back. x 304.5-325.5, y 61.5-139
 'J5':(313,64.075,0),'U4':(307.2,115.6,0),'R9':(307.2,112.6,0),'C22':(310.4,115.6,90),
 'SW1':(310.0,72.6,0),'SW2':(320.0,72.6,0),'J3':(321.4,81,90),
 'Y1':(308.0,80.5,0),'C13':(306.2,77.6,0),'C14':(309.8,77.6,0),'R3':(311.4,80.5,90),'R4':(313.6,77.6,0),'R5':(320.0,77.6,0),
 'U1':(314.0,91.0,0),
 'C1':(305.6,98.0,0),'C2':(305.6,84.4,0),'C3':(313.8,85.0,0),'C4':(321.4,97.8,0),'C5':(321.4,99.2,0),'C6':(313.9,99.4,90),
 'C7':(316.0,85.0,0),'C8':(313.9,97.4,90),'C9':(317.6,98.4,0),'C10':(317.6,97.2,0),'C11':(319.6,97.2,0),'C12':(319.6,98.4,0),
 'U2':(309.0,104.0,90),'C15':(305.6,104.0,90),'R10':(312.6,104.0,90),'R1':(316.8,100.0,0),'R2':(316.8,101.6,0),
 'J1':(322.925,106.5,-90),'U3':(315.4,112.2,0),'C16':(315.4,108.6,0),'C17':(315.4,115.8,0),
 'J4':(321.305,117.9,-90),'C23':(316.6,118.4,90),'C20':(306.0,65.6,90),'C21':(306.0,68.8,90),'D114':(315.0,70.0,90),
 'Q1':(309.5,121.0,0),'Q2':(309.5,126.0,0),'R6':(306.2,121.0,90),'C19':(312.8,121.0,90),'R7':(312.8,126.0,90),'R8':(306.2,126.0,90),
 'C18':(314.0,131.0,0),'TP1':(307.0,131.0,0),'TP2':(310.2,134.2,0),'TP3':(317.6,134.2,0),'TP4':(320.8,131.0,0)}
for r,(x,y,a) in col.items(): place[r]=(x,y,a,True)
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
