import zipfile,io,os,sys,json,struct,re,collections
D=sys.argv[1]
classes=set(); owner_pk={}  # all class names
mixins=[]  # (jar, mixin class bytes name, bytes)
def cp_classes(b):
  # parse constant pool, return set of class names + descriptors types
  out=set()
  try:
    n=struct.unpack('>H',b[8:10])[0]; i=10; k=1; utf={}; cls=[]
    while k<n:
      t=b[i]
      if t==1:
        l=struct.unpack('>H',b[i+1:i+3])[0]; utf[k]=b[i+3:i+3+l].decode('utf8','ignore'); i+=3+l
      elif t in(7,8,16,19,20): 
        if t==7: cls.append(struct.unpack('>H',b[i+1:i+3])[0])
        i+=3
      elif t==15: i+=4
      elif t in(3,4,9,10,11,12,17,18): i+=5
      elif t in(5,6): i+=9; k+=1
      else: return out
      k+=1
    for c in cls:
      s=utf.get(c,'')
      out.add(s.lstrip('[').removeprefix('L').removesuffix(';'))
    for s in utf.values():
      for m in re.findall(r'L([a-z][\w/$]+);',s): out.add(m)
      if re.fullmatch(r'[a-z][\w]*(/[\w$]+){2,}',s): out.add(s)
  except Exception: pass
  return out
def scan(z,jar):
  names=z.namelist()
  for n in names:
    if n.endswith('.class'): classes.add(n[:-6])
  pk=[]
  for n in names:
    if n.endswith('.json') and 'mixin' in n.lower() and '/' not in n.strip('/'):
      try: j=json.loads(z.read(n)); 
      except Exception: continue
      p=j.get('package')
      if p: pk.append(p.replace('.','/'))
  for p in pk:
    for n in names:
      if n.startswith(p+'/') and n.endswith('.class'): mixins.append((jar,n,z.read(n)))
  for n in names:
    if n.endswith('.jar') and n.startswith('META-INF/'):
      try: scan(zipfile.ZipFile(io.BytesIO(z.read(n))),jar)
      except Exception: pass
for f in sorted(os.listdir(D)):
  if f.endswith('.jar'): scan(zipfile.ZipFile(os.path.join(D,f)),f)
# package roots owned by present mods: 3-segment prefixes of present classes
roots=collections.Counter('/'.join(c.split('/')[:3]) for c in classes)
issues=collections.defaultdict(set)
for jar,n,b in mixins:
  for c in cp_classes(b):
    if c.startswith(('net/minecraft','com/mojang','java/','javax/','sun/','jdk/','org/spongepowered','net/neoforged','org/objectweb','it/unimi','com/google','org/slf4j','org/apache','io/netty','org/joml','org/lwjgl','kotlin/','com/llamalad7')): continue
    r='/'.join(c.split('/')[:3])
    if roots.get(r,0)>=5 and c not in classes and '$' not in c.split('/')[-1][:1]:
      issues[jar].add(c)
for j,s in sorted(issues.items()): print(j,'->',sorted(s)[:4],len(s))
print('mixin classes scanned',len(mixins),'jars with issues',len(issues))
