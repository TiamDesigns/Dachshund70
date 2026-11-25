import FreeCAD as App, Part, Mesh, MeshPart, math
E=r"<work>/exports/"
O=r"<work>/print-v15/"
V='v15'
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
