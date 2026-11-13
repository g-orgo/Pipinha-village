import re
"""Validacao offline do datapack sunlit_towns: tudo que o Lost Cities vai ler precisa existir."""
import json, os, glob, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapping as M
import itemcheck as IC

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PACK = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data')
errors = collections.Counter()
samples = {}


def err(kind, msg):
    errors[kind] += 1
    samples.setdefault(kind, msg)


def rl_path(rl, kind):
    ns, p = rl.split(':', 1) if ':' in rl else ('lostcities', rl)
    return os.path.join(PACK, ns, 'lostcities', kind, p + '.json')


def has(rl, kind):
    if ':' not in rl or rl.startswith('lostcities:'):
        return True  # asset do proprio Lost Cities
    return os.path.exists(rl_path(rl, kind))


pal_chars = {}
for f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'palettes', '**', '*.json'), recursive=True):
    parts = os.path.relpath(f, PACK)[:-5].split(os.sep)
    ns, rel = parts[0], '/'.join(parts[3:])
    chars = set()
    for e in json.load(open(f))['palette']:
        chars.add(e['char'])
        states = [e['block']] if 'block' in e else [b['block'] for b in e.get('blocks', [])]
        if e.get('blocks') and sum(b.get('random', 0) for b in e['blocks']) < 128:
            err('lista random com soma < 128', f'{os.path.basename(f)} {e["char"]}')
        for s in states:
            bid, props = M.parse(s)
            if bid == 'minecraft:air':
                continue
            if 'concrete_powder' in bid:
                err('concrete powder nas cidades (desmancha)', s)
            if 'terracotta' in bid:
                err('terracota nas cidades (vira concreto)', s)
            if not M.exists(bid):
                err('bloco inexistente', s)
            vp = M.valid_props(bid)
            for k, v in props.items():
                if k not in vp or v not in vp[k]:
                    err('propriedade invalida', s)
        if 'loot' in e and not has(e['loot'], 'conditions'):
            err('condicao de loot ausente', e['loot'])
        for it in (e.get('tag') or {}).get('Items', []) if isinstance(e.get('tag'), dict) else []:
            if not M.item_ok(it.get('id', '')):
                err('item invalido em NBT', it.get('id'))
    pal_chars[f'{ns}:{rel}'] = chars

common = pal_chars.get('sunlit:common', set())
for f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'parts', '**', '*.json'), recursive=True):
    p = json.load(open(f))
    ref = p.get('refpalette')
    chars = set(common)
    if ref:
        if ref not in pal_chars:
            err('paleta ausente', ref)
        chars |= pal_chars.get(ref, set())
    used = {c for sl in p['slices'] for row in sl for c in row}
    miss = used - chars - {' '}
    if miss:
        err('char sem paleta', f'{os.path.basename(f)} {sorted(miss)}')

for f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'buildings', '**', '*.json'), recursive=True):
    b = json.load(open(f))
    for pr in b.get('parts', []) + b.get('parts2', []):
        if not has(pr['part'], 'parts'):
            err('parte ausente', pr['part'])
    # predio com floor explicito em todas as partes precisa cobrir 0..maxfloors
    # e ter uma parte top:true (senao o chunk quebra com
    # "Misconfiguration! No part condition matches": floor==floors exige top)
    parts = b.get('parts', [])
    if parts and all('floor' in p for p in parts) and b.get('mincellars', 0) == 0:
        have = {p['floor'] for p in parts}
        for slot in range(0, (b.get('maxfloors', 0) or 0) + 1):
            if slot not in have:
                err('andar sem parte (floor condition)', f'{os.path.basename(f)} floor={slot}')
        if not any(p.get('top') for p in parts):
            err('predio sem telhado (top:true ausente)', os.path.basename(f))
for f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'multibuildings', '*.json')):
    for row in json.load(open(f))['buildings']:
        for b in row:
            if not has(b, 'buildings'):
                err('predio ausente (multi)', b)
for f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'scattered', '*.json')):
    s = json.load(open(f))
    if 'multibuilding' in s and not has(s['multibuilding'], 'multibuildings'):
        err('multi ausente (scattered)', s['multibuilding'])
    for b in s.get('buildings', []):
        if not has(b, 'buildings'):
            err('predio ausente (scattered)', b)

kinds = {'buildings': 'buildings', 'multibuildings': 'multibuildings', 'parks': 'parts', 'fountains': 'parts',
         'fronts': 'parts', 'stairs': 'parts', 'bridges': 'parts', 'largebridges': 'parts', 'raildungeons': 'parts'}
for f in glob.glob(os.path.join(PACK, 'sunlit', 'lostcities', 'citystyles', '*.json')):
    cs = json.load(open(f))
    if not os.path.exists(rl_path(cs['style'], 'styles')):
        err('style ausente', cs['style'])
    for k, lst in cs['selectors'].items():
        for x in lst:
            if not has(x['value'], kinds.get(k, 'parts')):
                err(f'{k} ausente', x['value'])
    for k, v in cs.get('streetblocks', {}).get('parts', {}).items():
        for x in v:
            if not has(x, 'parts'):
                err('rua ausente', x)
ws = json.load(open(os.path.join(PACK, 'sunlit', 'lostcities', 'worldstyles', 'towns.json')))
for c in ws['citystyles']:
    if not has(c['citystyle'], 'citystyles'):
        err('citystyle ausente', c['citystyle'])
for s in ws['scattered']['list']:
    if not (has(s['name'], 'scattered')):
        err('scattered ausente', s['name'])
for k, v in ws['parts']['highways'].items():
    for x in v:
        if not has(x, 'parts'):
            err('rodovia ausente', x)

for f in glob.glob(os.path.join(PACK, 'sunlit', 'loot_tables', '**', '*.json'), recursive=True):
    for pool in json.load(open(f))['pools']:
        if not pool['entries']:
            err('loot vazio', f)
        for e in pool['entries']:
            if not M.item_ok(e['name']):
                err('item de loot invalido', e['name'])
# CROP_BLACKLIST: no banned crop, fruit, seed or sapling in palettes, parts, buildings, lots or loot.
# The error names the file (building or loot table) and the block id.
_crop_scan = [f for f in glob.glob(os.path.join(PACK, '*', 'lostcities', '**', '*.json'), recursive=True)
              + glob.glob(os.path.join(PACK, 'sunlit', 'loot_tables', '**', '*.json'), recursive=True)]
for f in sorted(set(_crop_scan)):
    _txt = open(f, encoding='utf-8').read()
    for _tok in sorted(set(re.findall(r'"([a-z0-9_.-]+:[a-z0-9_./-]+)', _txt))):
        if _tok in IC.CROP_BLACKLIST:
            err('cultura proibida (CROP_BLACKLIST)', f'{os.path.relpath(f, PACK)}: {_tok}')

for f in glob.glob(os.path.join(PACK, 'sunlit', 'lostcities', 'conditions', '*.json')):
    for v in json.load(open(f))['values']:
        ns, p = v['value'].split(':')
        if not os.path.exists(os.path.join(PACK, ns, 'loot_tables', p + '.json')):
            err('loot table ausente', v['value'])

# partes de rodovia do proprio Lost Cities (curva, T) usam sunlit:common como paleta
import zipfile, re
_jar = sorted(glob.glob(os.path.join(ROOT, 'mods', 'lostcities-*.jar')))[-1]
_z = zipfile.ZipFile(_jar)
for n in _z.namelist():
    if re.search(r'/lostcities/parts/highway_(bridge|open|tunnel)', n) and n.endswith('.json'):
        p = json.loads(_z.read(n))
        if p.get('refpalette'):
            continue
        miss = {c for sl in p['slices'] for row in sl for c in row} - common - {' '}
        if miss:
            err('char sem paleta (parte do Lost Cities)', f'{n.rsplit("/", 1)[1]} {sorted(miss)}')

# partes de parque: convencao da camada do chao (polish.rule_park_ground) e nada solto no ar depois que o
# KubeJS baixa o parque 1 bloco. Foi o erro que mais voltou (horta, curral, praca com meia laje).
import polish as P
import lcparts as LP
_store = LP.Store()
for _name, (_path, _part) in _store.parts.items():
    if not _name.startswith('sunlit:parks/'):
        continue
    for _p in P.park_problems(LP.Grid(_store, _name, _part)):
        err('parque fora da convencao do chao', f'{_name}: {_p}')

# multibuildings: Lost Cities gives every chunk the floors/cellars of the top-left chunk; a building of another
# height has no part for some floor and the chunk aborts ("No part condition matches")
for _f in glob.glob(os.path.join(PACK, 'sunlit', 'lostcities', 'multibuildings', '**', '*.json'), recursive=True):
    _m = json.load(open(_f, encoding='utf-8'))
    _sig = set()
    for _col in _m['buildings']:
        for _b in _col:
            _p = rl_path(_b, 'buildings')
            if os.path.exists(_p):
                _d = json.load(open(_p, encoding='utf-8'))
                _sig.add((_d.get('minfloors'), _d.get('maxfloors'), _d.get('mincellars', 0), _d.get('maxcellars', 0)))
    if len(_sig) > 1:
        err('multibuilding com andares diferentes', f'{os.path.basename(_f)}: {sorted(_sig, key=str)}')

# building filler: Lost Cities fills below the building with this char from the CITY STYLE palette (sunlit:common);
# a char that only exists in a part palette resolves to null and the chunk aborts (NPE in makeRoomForBuilding)
for _f in glob.glob(os.path.join(PACK, 'sunlit', 'lostcities', 'buildings', '**', '*.json'), recursive=True):
    _fl = json.load(open(_f, encoding='utf-8')).get('filler')
    if _fl and _fl not in common:
        err('filler fora da paleta do estilo', f'{os.path.relpath(_f, PACK)}: {_fl!r}')

# no maximo 3 containers com loot por parte/andar (polish.rule_loot_cap, 2026-10-09)
for _name, (_path, _part) in _store.parts.items():
    if re.match(r'sunlit:(parks|fountains)/', _name):
        continue
    _g = LP.Grid(_store, _name, _part)
    _n = sum(1 for _y in range(_g.H) for _z in range(_g.Z) for _x in range(_g.X)
             if (_g.entry(_y, _z, _x) or {}).get('loot') and len(_g.opts(_y, _z, _x)) == 1)
    if _n > 3:
        err('loot demais no andar (max 3)', f'{_name}: {_n}')

# cebola so na loja (regra do modpack): nada de cebola plantada, em saco ou em caixote nas cidades
for _f in glob.glob(os.path.join(PACK, '*', 'lostcities', 'palettes', '**', '*.json'), recursive=True):
    for _e in json.load(open(_f, encoding='utf-8')).get('palette', []):
        _ids = [_e.get('block', '')] + [b.get('block', '') for b in _e.get('blocks', [])]
        if any('onion' in i for i in _ids):
            err('cebola nas cidades', f'{os.path.relpath(_f, PACK)}: {_ids}')

# Windows nao extrai caminho > 260; a instancia ja ocupa ~70 chars la
for r, _, fs in os.walk(os.path.dirname(PACK)):
    for f in fs:
        rel = os.path.relpath(os.path.join(r, f), ROOT)
        if len(rel) > 120:
            err('caminho longo demais para o Windows', rel)

# casas da vila enterradas: no part do terreo (y0 = nivel do chao, porao fica abaixo dele)
def _bname_of(b):
    return (b or '').split('[')[0].split(':')[-1]

_SOLID_SKIP = ('air', 'door', 'trapdoor', 'stairs', 'slab', 'fence', 'fence_gate', 'pane', 'glass',
               'ladder', 'torch', 'sign', 'carpet', 'flower', 'grass', 'sapling', 'button', 'lever')

def _is_solid(b):
    n = _bname_of(b)
    if not n or 'air' in n:
        return False
    return not any(s in n for s in _SOLID_SKIP)

_FRONT = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}

def buried_errors(bname, part_name, g):
    """Return (kind, detail) tuples for buried doors, windows, stairs and fences in a ground part grid."""
    out = []
    for _y in range(g.H):
        for _z in range(g.Z):
            for _x in range(g.X):
                _b = g.b(_y, _z, _x) or ''
                _n = _bname_of(_b)
                where = f'{bname}: {part_name} y{_y} z{_z} x{_x}'
                if _n.endswith('_door') and 'half=lower' in _b and _y <= 0:
                    # the cell the player stands on (in front of the door) is solid at ground level
                    m = re.search(r'facing=(north|south|east|west)', _b)
                    if m:
                        dz, dx = _FRONT[m.group(1)][1], _FRONT[m.group(1)][0]
                        front = g.b(_y, _z + dz, _x + dx)
                        if _is_solid(front):
                            out.append(('porta enterrada', f'{where} frente={_bname_of(front)}'))
                if ('glass' in _n or _n.endswith('_pane')) and _y <= 0:
                    out.append(('janela enterrada', f'{where} {_b}'))
                if (_n.endswith('_stairs') or _n.endswith('_fence')) and _y <= 0:
                    # cells below the ground line (y<0) are earth, so they count as solid
                    cells = [(_y + 1, _z, _x), (_y - 1, _z, _x), (_y, _z + 1, _x),
                             (_y, _z - 1, _x), (_y, _z, _x + 1), (_y, _z, _x - 1)]
                    nb = [g.b(*c) if c[0] >= 0 or g.b(*c) is not None else 'minecraft:stone' for c in cells]
                    if all(_is_solid(c) for c in nb):
                        out.append(('escada/cerca enterrada', f'{where} {_b}'))
    return out

def table_on_table_errors(bname, part_name, g):
    """Mesa com outra mesa logo em cima: mobiliario empilhado, sempre um erro do gerador."""
    out = []
    for _y in range(g.H - 1):
        for _z in range(g.Z):
            for _x in range(g.X):
                _n = _bname_of(g.b(_y, _z, _x) or '')
                _up = _bname_of(g.b(_y + 1, _z, _x) or '')
                if 'table' in _n and 'table' in _up:
                    out.append(('mesa sobre mesa', f'{bname}: {part_name} y{_y} z{_z} x{_x}'))
    return out

import lcparts as _L
_store = _L.Store()

def _grid(part_name):
    _pp = rl_path(part_name, 'parts')
    if not os.path.exists(_pp):
        return None
    return _L.Grid(_store, part_name, json.load(open(_pp, encoding='utf-8')))

def floor_ladder_errors(bname, part_name, g, maxcellars, cg):
    """escada na fatia 0 do terreo sem porao debaixo: buraco no chao (mesma regra do polish.rule_floor_ladder)"""
    out = []
    for _z in range(g.Z):
        for _x in range(g.X):
            if 'ladder' not in _bname_of(g.b(0, _z, _x) or ''):
                continue
            _top = cg.b(cg.H - 1, _z, _x) if cg is not None else None
            if maxcellars != 0 and _top is not None and (_L.block_is_air(_top) or 'ladder' in _top):
                continue
            out.append(('escada no chao sem porao', f'{bname}: {part_name} z{_z} x{_x}'))
    return out

for _bf in glob.glob(os.path.join(PACK, '*', 'lostcities', 'buildings', '**', '*.json'), recursive=True):
    _bname = os.path.relpath(_bf, PACK)
    _d = json.load(open(_bf, encoding='utf-8'))
    _parts = [_pe for _key in ('parts', 'parts2') for _pe in _d.get(_key, [])]
    _cellars = [_pe['part'] for _pe in _parts if _pe.get('cellar')]
    _cg = _grid(_cellars[0]) if _cellars else None
    _mc = _d.get('maxcellars', 0)
    for _pe in _parts:
        _g = _grid(_pe['part'])
        if _g is None:
            continue
        for _k, _dd in table_on_table_errors(_bname, _pe['part'], _g):
            err(_k, _dd)
        if not _pe.get('ground'):
            continue
        if os.path.basename(_bf).startswith('vila_'):
            for _k, _dd in buried_errors(_bname, _pe['part'], _g):
                err(_k, _dd)
        for _k, _dd in floor_ladder_errors(_bname, _pe['part'], _g, _mc, _cg):
            err(_k, _dd)

# decor empilhado em armazenamento/bancada (partes sunlit:lote/*, ex. parques e feira)
_DECOR_RE = re.compile(r'hay_block|lantern|flower_pot|potted_|candle')
_SUPPORT_RE = re.compile(r'barrel|chest|crate|hay_block|composter|mincer|cabinet|stove|crafting_table|smoker|'
                         r'furnace|cutting_board|loom|smithing|fletching|grindstone|anvil|_bale|_bag|keg|basket|press')

def stacked_decor_errors(bname, part_name, g):
    """decor em cima de armazenamento/bancada. Excecoes: feno sobre feno (pilha de fardos), pote de flor
    sobre barril ou caixote, e lanterna pendurada (hanging=true)."""
    out = []
    for _y in range(g.H - 1):
        for _z in range(g.Z):
            for _x in range(g.X):
                _up = g.b(_y + 1, _z, _x) or ''
                _dn = _bname_of(g.b(_y, _z, _x) or '')
                _un = _bname_of(_up)
                if not _DECOR_RE.search(_un) or not _SUPPORT_RE.search(_dn):
                    continue
                if 'hay_block' in _un and 'hay_block' in _dn:
                    continue
                if 'flower_pot' in _un and ('barrel' in _dn or 'crate' in _dn):
                    continue
                if 'lantern' in _un and 'hanging=true' in _up:
                    continue
                out.append(('decor sobre armazenamento', f'{bname}: {part_name} y{_y + 1} z{_z} x{_x} {_un} sobre {_dn}'))
    return out

for _pf in glob.glob(os.path.join(PACK, '*', 'lostcities', 'parts', 'lote', '**', '*.json'), recursive=True):
    _pname = 'sunlit:' + os.path.relpath(_pf, os.path.join(PACK, 'sunlit', 'lostcities', 'parts')).replace(os.sep, '/')[:-5]
    _g = _grid(_pname)
    if _g is None:
        continue
    for _k, _dd in stacked_decor_errors(_pname, _pname, _g):
        err(_k, _dd)

# lista de lotes (sunlitTownsLotes.js, gerada pelo complexes.py): nenhum predio de vila pode entrar
_LOTE_JS = os.path.join(ROOT, 'kubejs', 'startup_scripts', 'sunlitTownsLotes.js')
_lote_txt = open(_LOTE_JS, encoding='utf-8').read()
_lote_keys = json.loads(_lote_txt.split('global.sunlitLoteBuildings = ', 1)[1].split(';', 1)[0])
for _key in _lote_keys:
    if not _key.startswith('sunlit:'):
        continue
    if 'vila_' in _key:
        err('lote de vila', f'{_key} (nome com vila_)')
        continue
    _bf = os.path.join(PACK, 'sunlit', 'lostcities', 'buildings', _key[len('sunlit:'):] + '.json')
    if not os.path.exists(_bf):
        continue
    _bd = json.load(open(_bf, encoding='utf-8'))
    for _pe in _bd.get('parts', []) + _bd.get('parts2', []):
        if _pe.get('ground') and _pe['part'].startswith('sunlit:vila_'):
            err('lote de vila', f'{_key} (terreo {_pe["part"]})')

# porao real (>= 30 celulas de ar) sem escada de acesso: mesma regra do cellar_access.py (multipredio conta como um)
import cellar_access as _CA
for _grp in _CA.analyze(_store):
    if not _grp['ok']:
        err('porão sem acesso', _grp['label'])

if errors:
    for k, n in errors.items():
        print(f'ERRO {k}: {n}  ex: {samples[k]}')
    sys.exit(1)
print('OK: nenhum problema encontrado')
