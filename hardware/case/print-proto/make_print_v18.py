import FreeCAD as App, Part, Mesh, MeshPart, math
E=r"<work>/exports/"
O=r"<work>/print-v18/"
V='v18'
c=math.cos(math.radians(4)); s=math.sin(math.radians(4))
X0=44.0
def box(x0,y0,z0,x1,y1,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))
BIG=500
def halves(sh):
    L=sh.common(box(-BIG,-BIG,-BIG,X0,BIG,BIG)); R=sh.common(box(X0,-BIG,-BIG,BIG,BIG,BIG)); return L,R
def slot_rect(y,z,wy,hz,depth=11.3):
    return box(X0-depth,y-wy/2,z-hz/2,X0+depth,y+wy/2,z+hz/2)
def pin(y,z,d=1.9,depth=8.0):
    return Part.makeCylinder(d/2,2*depth,App.Vector(X0-depth,y,z),App.Vector(1,0,0))
def save(shape,name,tol=0.02):
    shape=shape.removeSplitter() if hasattr(shape,'removeSplitter') else shape
    m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=tol,AngularDeflection=math.radians(8),Relative=False)
    m.write(O+name); print(name, round(shape.Volume/1000,1),'cm3', shape.BoundBox)
# ---- bottom shell: three flat keys (8x3) in the floor, a filament pin in the back wall
b=Part.read(E+'bottom.step')
cut=None
for y in (15.0,30.0,45.0):
    t=slot_rect(y,3.75,8.3,3.3); cut=t if cut is None else cut.fuse(t)
cut=cut.fuse(pin(78.0,11.5))
b=b.cut(cut)
L,R=halves(b)
save(L,'Dachshund70-Rev3-Bottom-PETG-left-%s.stl'%V); save(R,'Dachshund70-Rev3-Bottom-PETG-right-%s.stl'%V)
# ---- top shell A: one square key (4x4) at the back, two filament pins at the front
t=Part.read(E+'topA.step')
cut=slot_rect(67.75,19.75,4.3,4.3).fuse(pin(-73.0,6.5)).fuse(pin(-68.0,13.0))
t=t.cut(cut)
L,R=halves(t)
save(L,'Dachshund70-Rev3-TopA-PETG-left-%s.stl'%V); save(R,'Dachshund70-Rev3-TopA-PETG-right-%s.stl'%V)
# ---- accent ring: dovetail tab on the left half in each band (built in the plate frame, then tilted 4 deg)
ring=Part.read(E+'ring.step')
def dovetail(yc,grow=0.0):
    n=3.0+grow; h=5.0+grow; d=7.0+grow
    pts=[App.Vector(X0-1.0,yc-n,-5),App.Vector(X0+d,yc-h,-5),App.Vector(X0+d,yc+h,-5),App.Vector(X0-1.0,yc+n,-5),App.Vector(X0-1.0,yc-n,-5)]
    f=Part.Face(Part.makePolygon(pts)); pr=f.extrude(App.Vector(0,0,10))
    m=App.Matrix(); m.rotateX(math.radians(4)); pr=pr.transformGeometry(m); pr.translate(App.Vector(0,0.0738,9.2702))
    return pr
tabs=dovetail(-69.5).fuse(dovetail(70.75)); socks=dovetail(-69.5,0.1).fuse(dovetail(70.75,0.1))
Lr=ring.common(box(-BIG,-BIG,-BIG,X0,BIG,BIG).fuse(tabs)); Rr=ring.common(box(X0,-BIG,-BIG,BIG,BIG,BIG)).cut(socks)
save(Lr,'Dachshund70-Rev3-Ring-PETG-left-%s.stl'%V); save(Rr,'Dachshund70-Rev3-Ring-PETG-right-%s.stl'%V)
# ---- keys to print (lying flat): 3 flat keys 8 x 3 x 22 and 1 square key 4 x 4 x 22, 0.4 chamfered ends
def key(w,h,l=22.0):
    k=Part.makeBox(l,w,h)
    try: k=k.makeChamfer(0.4,[e for e in k.Edges if abs(e.Length-w)<1e-6 or abs(e.Length-h)<1e-6])
    except Exception as ex: print('chamfer skipped',ex)
    return k
keys=[]
for i in range(3):
    k=key(8.0,3.0); k.translate(App.Vector(0,i*12,0)); keys.append(k)
k=key(4.0,4.0); k.translate(App.Vector(0,36,0)); keys.append(k)
save(Part.makeCompound(keys),'Dachshund70-Rev3-Joint-keys-%s.stl'%V)
# ---- wired plate: stepped split through the webs between switch cutouts (KiCad coords; STEP Y = -KiCad y)
pl=Part.read(r"<work>/wplate-v01.step")
bands=[(0,61.43,224.785),(61.43,82.86,229.55),(82.86,101.91,219.03),(101.91,120.96,224.785),(120.96,140.01,215.265),(140.01,200,209.94)]
left=None
for y0,y1,xs in bands:
    t=box(0,-y1,-5,xs,-y0,5); left=t if left is None else left.fuse(t)
PL=pl.common(left); PR=pl.cut(left)
save(PL,'Dachshund70-Wired-Plate-print-left-%s.stl'%V,0.01); save(PR,'Dachshund70-Wired-Plate-print-right-%s.stl'%V,0.01)

t=Part.read(E+'tray.step')
m=App.Matrix(); m.rotateX(math.radians(-4)); t=t.transformGeometry(m)
bb=t.BoundBox; t.translate(App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
save(t,'Dachshund70-Rev3-Screen-tray-%s.stl'%V,0.01)
