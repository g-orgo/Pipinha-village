"""List every id cited by a quests folder that the 1.21.1 instance does not register.
Usage: python3 -I validate.py <quests_dir> [--all]"""
import sys, glob, os, re, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snbt
K, kjs = pickle.load(open(os.path.dirname(os.path.abspath(__file__)) + '/known.pkl', 'rb'))
ROOT = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village"
TROPHIES = {'trofers:' + f[:-5] for f in os.listdir(ROOT + '/kubejs/data/trofers/trofers')}
VARIANTS = set(re.findall(r'"title\.longwings\.([a-z_]+)"', open(ROOT + '/../Pipinha\'s Village/kubejs/assets/ftbquestlocalizer/lang/en_us.json').read()))
FILTER_ITEM = re.compile(r'(item|item_tag)\(([^()]+)\)')
bad = collections.defaultdict(list); seen = collections.Counter()

def chk(kind, i, where):
    i = str(i); seen[kind] += 1
    if kind != 'tag' and i.startswith('#'): kind, i = 'tag', i[1:]
    if kind == 'tag' or kind == 'biome_tag': return
    if i not in K[kind]: bad[(kind, i)].append(where)

def stack(st, where):
    if isinstance(st, str): chk('item', st, where); return
    if not isinstance(st, dict) or 'id' not in st: return
    chk('item', st['id'], where)
    comp = st.get('components', {})
    f = comp.get('ftbfiltersystem:filter')
    if f:
        for kind, a in FILTER_ITEM.findall(f):
            if kind == 'item': chk('item', a, where + ' (filter)')
    t = comp.get('trofers:trophy')
    if t and t not in TROPHIES: bad[('trophy', t)].append(where)

def walk(o, where):
    if isinstance(o, dict):
        for k, x in o.items():
            if k in ('item', 'icon'): stack(x, where)
            elif k == 'to_observe' and o.get('observe_type') == '5': chk('entity', x, where)
            elif k == 'entity': chk('entity', x, where)
            elif k == 'dimension': chk('dimension', x, where)
            elif k == 'biome': chk('biome', x, where)
            elif k == 'structure': chk('structure', x, where)
            elif k == 'block': chk('item', x, where)
            walk(x, where)
    elif isinstance(o, list):
        for x in o: walk(x, where)

d = sys.argv[1]
for f in sorted(glob.glob(d + '/**/*.snbt', recursive=True)):
    walk(snbt.loads(open(f, encoding='utf-8').read()), os.path.relpath(f, d))
print('checked', dict(seen), 'unknown', len(bad))
for (kind, i), w in sorted(bad.items()):
    print(f'{kind}\t{i}\t{len(w)}\t{",".join(sorted(set(w)))[:120]}')
