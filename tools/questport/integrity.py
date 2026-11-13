import sys,glob,os,zipfile,collections;sys.path.insert(0,'.');import snbt
d=sys.argv[1]; ROOT="/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village"
ids=collections.Counter(); deps=[]; imgs=set(); tables=set()
for f in glob.glob(d+'/**/*.snbt',recursive=True):
    v=snbt.loads(open(f).read())
    def walk(o):
        if isinstance(o,dict):
            if 'id' in o and isinstance(o['id'],str) and len(o['id'])==16 and all(c in '0123456789ABCDEF' for c in o['id']): ids[o['id']]+=1
            for x in o.get('dependencies',[]): deps.append((os.path.basename(f),x))
            if 'image' in o: imgs.add(o['image'])
            if 'table_id' in o: tables.add(int(str(o['table_id']).rstrip('L')))
            for x in o.values(): walk(x)
        elif isinstance(o,list):
            for x in o: walk(x)
    walk(v)
print('dup ids',[i for i,c in ids.items() if c>1][:5]); print('broken deps',[x for x in deps if x[1] not in ids][:10])
print('broken tables',[t for t in tables if '%016X'%t not in ids][:5])
have=set()
for dp,_,fns in os.walk(ROOT+'/kubejs/assets'):
    for fn in fns: have.add(os.path.relpath(os.path.join(dp,fn),ROOT+'/kubejs/assets'))
miss=[i for i in imgs if (i.split(':')[0]+'/'+i.split(':')[1]) not in have]
print('images',len(imgs),'missing in kubejs/assets',miss[:20])
