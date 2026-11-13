import json,sys,glob,re,collections;sys.path.insert(0,'.');import snbt
L=json.load(open("/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village/kubejs/assets/ftbquestlocalizer/lang/en_us.json"))
W=re.compile(r'botania|\bmana\b|mana[ -]|slime|plort|largo|tarr\b|apothecary|lexica|petal|flugel|terrasteel|elementium|manasteel',re.I)
hits=collections.defaultdict(list)
for k,v in L.items():
    m=re.match(r'ftbquests\.chapter\.([a-z_]+)\.quest([0-9A-F]+)\.',k)
    if m and W.search(v): hits[(m.group(1),m.group(2))].append(v[:110])
for f in sorted(glob.glob('out/chapters/*.snbt')):
    ch=f.split('/')[-1][:-5]
    for q in snbt.loads(open(f).read())['quests']:
        h=hits.get((ch,q['id'].lstrip('0')))
        if h: print(ch,q['id'],[t.get('type')+':'+str(t.get('item',''))[:40] for t in q.get('tasks',[])],'|',' // '.join(h)[:300])
