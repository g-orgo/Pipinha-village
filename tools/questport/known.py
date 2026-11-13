"""Registry ids known to the 1.21.1 instance: mod jars (+jarjar), vanilla jar, KubeJS."""
import io, json, os, re, zipfile, pickle
ROOT = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village"
VANILLA = "/var/home/Orgo/Documentos/curseforge/minecraft/Install/versions/1.21.1/1.21.1.jar"
K = {k: set() for k in ('item', 'entity', 'biome', 'structure', 'dimension', 'modid', 'block')}
LANG = re.compile(r'"(item|block|entity)\.([a-z0-9_.-]+)\.([a-z0-9_./-]+)"\s*:')

def scan(zf):
    for n in zf.namelist():
        p = n.split('/')
        if n.startswith('META-INF/jarjar/') and n.endswith('.jar'):
            scan(zipfile.ZipFile(io.BytesIO(zf.read(n)))); continue
        if n in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
            K['modid'] |= set(re.findall(r'modId\s*=\s*["\']([a-z0-9_.-]+)', zf.read(n).decode('utf-8', 'replace')))
        if len(p) < 4 or not n.endswith('.json'): continue
        b = p[-1][:-5]
        if p[0] == 'assets' and p[2:4] == ['models', 'item']: K['item'].add(p[1] + ':' + '/'.join(p[4:])[:-5])
        elif p[0] == 'assets' and p[2] == 'blockstates': K['block'].add(p[1] + ':' + b)
        elif p[0] == 'assets' and p[2] == 'lang' and b == 'en_us':
            for t, ns, path in LANG.findall(zf.read(n).decode('utf-8', 'replace')):
                if '.' in path: continue
                K['entity' if t == 'entity' else 'item'].add(ns + ':' + path)
        elif p[0] == 'data' and p[2:4] == ['worldgen', 'biome']: K['biome'].add(p[1] + ':' + '/'.join(p[4:])[:-5])
        elif p[0] == 'data' and p[2:4] == ['worldgen', 'structure']: K['structure'].add(p[1] + ':' + '/'.join(p[4:])[:-5])
        elif p[0] == 'data' and p[2] == 'dimension': K['dimension'].add(p[1] + ':' + b)

for fn in sorted(os.listdir(ROOT + '/mods')):
    if fn.endswith('.jar'):
        try: scan(zipfile.ZipFile(ROOT + '/mods/' + fn))
        except Exception as e: print('skip', fn, e)
scan(zipfile.ZipFile(VANILLA))
K['dimension'] |= {'minecraft:overworld', 'minecraft:the_nether', 'minecraft:the_end'}
# KubeJS: data folders and registrations in startup scripts.
for dp, _, fns in os.walk(ROOT + '/kubejs/data'):
    for f in fns:
        rel = os.path.relpath(os.path.join(dp, f), ROOT + '/kubejs/data').split(os.sep)
        if f.endswith('.json') and len(rel) >= 3:
            ns = rel[0]
            if rel[1:3] == ['worldgen', 'biome']: K['biome'].add(ns + ':' + '/'.join(rel[3:])[:-5])
            if rel[1:3] == ['worldgen', 'structure']: K['structure'].add(ns + ':' + '/'.join(rel[3:])[:-5])
            if rel[1] == 'dimension': K['dimension'].add(ns + ':' + f[:-5])
kjs = {}
CREATE = re.compile(r"""(StartupEvents\.registry\(\s*['"]([a-z_:]+)['"])|\.create\(\s*['"]([a-z0-9_.-]+:[a-z0-9_/.-]+)['"]|\.create\(\s*['"]([a-z0-9_/.-]+)['"]""")
for dp, _, fns in os.walk(ROOT + '/kubejs/startup_scripts'):
    for f in fns:
        if not f.endswith('.js'): continue
        t = open(os.path.join(dp, f), encoding='utf-8', errors='replace').read()
        reg = 'item'
        for m in CREATE.finditer(t):
            if m.group(2): reg = m.group(2).split(':')[-1]; continue
            i = m.group(3) or ('kubejs:' + m.group(4))
            kjs.setdefault(i, reg)
            (K['entity'] if reg == 'entity_type' else K['item']).add(i)
# society:* items registered from template literals: take the pack's own lang, item models and textures.
SA = ROOT + '/kubejs/assets/society'
for t, ns, path in LANG.findall(open(SA + '/lang/en_us.json', encoding='utf-8').read() + open(SA + '/lang/en_us_template.json', encoding='utf-8').read()):
    if ns == 'society' and '.' not in path: K['entity' if t == 'entity' else 'item'].add('society:' + path)
for sub in ('models/item', 'textures/item', 'textures/block', 'blockstates'):
    for dp, _, fns in os.walk(SA + '/' + sub):
        for f in fns:
            if f.endswith(('.json', '.png')): K['item'].add('society:' + f.rsplit('.', 1)[0])
pickle.dump((K, kjs), open(os.path.dirname(os.path.abspath(__file__)) + '/known.pkl', 'wb'))
print({k: len(v) for k, v in K.items()}, len(kjs))
