"""Le blockstates/modelos de item de todos os jars (mods + vanilla) e grava registry.json:
{"blocks": {id: {prop: [values]}}, "items": [ids], "loot_tables": [ids]}"""
import json, zipfile, glob, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JARS = sorted(glob.glob(os.path.join(ROOT, 'mods', '*.jar')))
JARS.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'Install', 'versions', '1.20.1', '1.20.1.jar'))
BS = re.compile(r'^assets/([^/]+)/blockstates/(.+)\.json$')
IM = re.compile(r'^assets/([^/]+)/models/item/(.+)\.json$')
LT = re.compile(r'^data/([^/]+)/loot_tables/(.+)\.json$')
blocks, items, loots = {}, set(), set()

def add_when(props, when):
    if not isinstance(when, dict): return
    for k, v in when.items():
        if k in ('OR', 'AND'):
            for w in v: add_when(props, w)
        else:
            props.setdefault(k, set()).update(str(v).lower().split('|'))

for j in JARS:
    try: z = zipfile.ZipFile(j)
    except Exception as e: print('skip', j, e); continue
    for n in z.namelist():
        m = BS.match(n)
        if m:
            bid = f'{m.group(1)}:{m.group(2)}'
            try: d = json.loads(z.read(n).decode('utf-8', 'replace'))
            except Exception: d = {}
            props = {}
            for key in (d.get('variants') or {}):
                for kv in key.split(','):
                    if '=' in kv:
                        k, v = kv.split('=', 1); props.setdefault(k.strip(), set()).add(v.strip())
            for part in d.get('multipart') or []:
                add_when(props, part.get('when'))
            old = blocks.get(bid, {})
            for k, v in props.items(): old.setdefault(k, set()).update(v)
            blocks[bid] = old
            continue
        m = IM.match(n)
        if m: items.add(f'{m.group(1)}:{m.group(2)}'); continue
        m = LT.match(n)
        if m: loots.add(f'{m.group(1)}:{m.group(2)}')

# blocos KubeJS (registrados por script) tem assets em kubejs/assets
for f in glob.glob(os.path.join(ROOT, 'kubejs', 'assets', '*', 'blockstates', '*.json')):
    ns = f.split(os.sep)[-3]; blocks.setdefault(f'{ns}:{os.path.basename(f)[:-5]}', {})
for f in glob.glob(os.path.join(ROOT, 'kubejs', 'assets', '*', 'models', 'item', '*.json')):
    ns = f.split(os.sep)[-4]; items.add(f'{ns}:{os.path.basename(f)[:-5]}')
# blocos registrados por script KubeJS (StartupEvents.registry("block") em kubejs/startup_scripts,
# ex.: society:aging_cask, society:charging_rod). Sem jar, entao as propriedades vem do proprio script:
# booleanProperty/integerProperty, o tipo "cardinal" (facing horizontal) e os "when" do blockstateJson.
KJS_CREATE = re.compile(r'\.create\(\s*["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\'](?:\s*,\s*["\'](\w+)["\'])?')
KJS_BOOL = re.compile(r'booleanProperty\.create\(\s*["\'](\w+)["\']')
KJS_INT = re.compile(r'integerProperty\.create\(\s*["\'](\w+)["\']\s*,\s*(\d+)\s*,\s*(\d+)')
KJS_WHEN = re.compile(r'when:\s*\{([^}]*)\}')
KJS_KV = re.compile(r'(\w+)\s*:\s*(true|false|"[^"]*"|\'[^\']*\'|\d+)')
HORIZONTAL = ['north', 'south', 'east', 'west']
for dp, _, fs in os.walk(os.path.join(ROOT, 'kubejs', 'startup_scripts')):
    for fn in fs:
        if not fn.endswith('.js'): continue
        src = open(os.path.join(dp, fn), encoding='utf-8', errors='replace').read()
        for seg in src.split('StartupEvents.registry(')[1:]:
            if not re.match(r'''["']block["']''', seg): continue
            seg = seg.split('StartupEvents.registry(')[0]
            starts = [m for m in KJS_CREATE.finditer(seg)]
            for i, m in enumerate(starts):
                end = starts[i + 1].start() if i + 1 < len(starts) else len(seg)
                chunk = seg[m.start():end]
                props = {}
                for k in KJS_BOOL.findall(chunk): props.setdefault(k, set()).update(['false', 'true'])
                for k, lo, hi in KJS_INT.findall(chunk): props.setdefault(k, set()).update(str(n) for n in range(int(lo), int(hi) + 1))
                if m.group(2) == 'cardinal' or 'HORIZONTAL_FACING' in chunk: props.setdefault('facing', set()).update(HORIZONTAL)
                elif 'BlockProperties.FACING' in chunk: props.setdefault('facing', set()).update(HORIZONTAL + ['up', 'down'])
                if 'BlockProperties.AXIS' in chunk: props.setdefault('axis', set()).update(['x', 'y', 'z'])
                for when in KJS_WHEN.findall(chunk):
                    for k, v in KJS_KV.findall(when):
                        props.setdefault(k, set()).add(v.strip('"\'').lower())
                old = blocks.get(m.group(1), {})
                for k, v in props.items(): old.setdefault(k, set()).update(v)
                blocks[m.group(1)] = old

# itens/blocos que o modpack remove via KubeJS contam como inexistentes
src = open(os.path.join(ROOT, 'kubejs', 'startup_scripts', 'globalRemovedItems.js')).read()
removed = set(re.findall(r'["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\']', src.split('global.removedItems')[1].split('];')[0]))
# modulos do Quark desligados em config/quark-common.toml (Hedges, More Stone Variants, New Stone Types, crates)
QUARK_OFF = re.compile(r'^quark:(.*_hedge|.*(limestone|jasper|shale|myalite).*|(polished_|chiseled_)?(calcite|tuff|dripstone).*|'
                       r'(chiseled_)?(andesite|diorite|granite)_(bricks|pillar).*|(apple|potato|carrot|beetroot)_crate)$')
removed |= {b for b in blocks if QUARK_OFF.match(b)}
for r in removed:
    blocks.pop(r, None); items.discard(r)
out = {'blocks': {b: {k: sorted(v) for k, v in p.items()} for b, p in sorted(blocks.items())},
       'items': sorted(items | set(blocks)), 'loot_tables': sorted(loots)}
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'registry.json'), 'w'))
print(len(out['blocks']), 'blocks', len(out['items']), 'items', len(loots), 'loot tables')
