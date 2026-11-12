import zipfile,os,re,io,sys,tomllib,collections
D=sys.argv[1]; ver={}; reqs=[]
def key(v):
  out=[]
  for p in re.split(r'[.\-+_]',str(v)):
    out.append((0,int(p),'') if p.isdigit() else (-1 if re.match(r'(alpha|beta|pre|rc|snapshot)',p,re.I) else 1,0,p.lower()))
  return out
def cmp(a,b):
  ka,kb=key(a),key(b); n=max(len(ka),len(kb)); ka+= [(0,0,'')]*(n-len(ka)); kb+=[(0,0,'')]*(n-len(kb))
  return (ka>kb)-(ka<kb)
def inrange(v,r):
  r=r.strip()
  if r in('*',''): return True
  for part in re.findall(r'[\[(][^\])]*[\])]',r) or [r]:
    if not part[0] in '[(': return cmp(v,part)>=0
    lo,_,hi=part[1:-1].partition(',')
    if ',' not in part:
      if cmp(v,lo)==0: return True; continue
    ok=True
    if lo.strip(): c=cmp(v,lo.strip()); ok&= c>0 or (c==0 and part[0]=='[')
    if hi.strip(): c=cmp(v,hi.strip()); ok&= c<0 or (c==0 and part[-1]==']')
    if ok: return True
  return False
def scan(z,owner,top):
  n='META-INF/neoforge.mods.toml'
  if n in z.namelist():
    try: d=tomllib.loads(z.read(n).decode('utf8','ignore'))
    except Exception: d={}
    mf=z.read('META-INF/MANIFEST.MF').decode('utf8','ignore') if 'META-INF/MANIFEST.MF' in z.namelist() else ''
    iv=re.search(r'Implementation-Version:\s*(\S+)',mf)
    for m in d.get('mods',[]):
      v=str(m.get('version','')); 
      if '${file.jarVersion}' in v and iv: v=iv.group(1)
      if m['modId'] not in ver or cmp(v,ver[m['modId']][0])>0 or not top and ver[m['modId']][1].endswith('(jij)')==False and False: ver[m['modId']]=(v,owner)
    if top:
      for mid,l in d.get('dependencies',{}).items():
        for x in (l if isinstance(l,list) else []):
          ty=str(x.get('type','required' if x.get('mandatory',True) else 'optional')).lower()
          reqs.append((owner,x.get('modId'),ty,x.get('versionRange','*')))
  for n in z.namelist():
    if n.startswith('META-INF/') and n.endswith('.jar'):
      try: scan(zipfile.ZipFile(io.BytesIO(z.read(n))),owner+'(jij)',False)
      except Exception: pass
for f in sorted(os.listdir(D)):
  if f.endswith('.jar'): scan(zipfile.ZipFile(os.path.join(D,f)),f,True)
ver['minecraft']=('1.21.1','');ver['neoforge']=(sys.argv[2],'')
bad=0
for o,mid,ty,r in reqs:
  if mid in('java','minecraft','neoforge') or '$' in r or '*' in r or r.startswith('>'): continue
  have=ver.get(mid)
  if ty=='required' and not have: print('MISSING',o,'needs',mid,r);bad+=1
  elif have and ty in('required','optional') and not inrange(have[0],r): print('RANGE',o,'needs',mid,r,'has',have[0]);bad+=1
  elif have and ty=='incompatible' and inrange(have[0],r): print('INCOMPAT',o,'vs',mid,r,'has',have[0]);bad+=1
print('problems',bad,'mods',len(ver))
