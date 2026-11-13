"""Casas da vila a partir de schematics (substituem as casas geradas antes em vila.py).

Fonte: SRC (pasta com .schem/.nbt). Cada entrada de CASAS diz a janela (em chunks) recortada do
schematic e a altura do chao. O recorte:
- fatia 0 = chao (grama/caminho do proprio schematic; buraco vira grama), o que estiver abaixo sai;
- moveis vanilla viram moveis de mod e comodos vazios sao mobiliados (vanilla_furni.py);
- 4 rotacoes por casa (o Lost Cities nao gira predios);
- casa de 1 chunk vira predio; maior vira multibuilding (buildings[x][z], um predio por chunk);
- cada chunk sobe em partes de 6 fatias (FLOORHEIGHT do Lost Cities) com condicao "floor": k,
  e o resto vai na parte "top".

Uso: python3 schematics.py  (depois de convert/houses/cozy_expansion/vila, antes do finalize)
     python3 schematics.py --stats   (so converte e mostra o que mudou, sem gravar)
"""
import collections
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapping as M
import mix as MIX
import schem
import vanilla_furni as VF
import clutter as CL
import loot as L

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit', 'lostcities')
SRC = os.path.join(ROOT, 'sunlit_tools', 'schematics')
FLOOR_H = 6

# key, arquivo, janela (x0, z0 no schematic; cw x cl chunks), chao (y do schematic ou None = auto), peso,
# porao (camadas abaixo do chao que viram cellar do Lost Cities, max 6; o terreno do schematic vem junto)
CASAS = [
    dict(key='vermelha', file='m-pinkhouse.nbt', x0=0, z0=0, cw=1, cl=1, ground=0, weight=0.6, cellar=0),
    dict(key='fada', file='cozy-fairy-hut.schem', x0=-3, z0=-1, cw=1, cl=1, ground=0, weight=0.5),
    dict(key='robella', file='robella-house1.schem', x0=-3, z0=-3, cw=2, cl=2, ground=0, weight=0.7),
    dict(key='cerejeira', file='cherry-robella.schem', x0=-1, z0=-1, cw=2, cl=2, ground=0, weight=0.6),
    dict(key='serrana', file='dtbh-cottage.schem', x0=0, z0=-4, cw=2, cl=2, ground=3, weight=0.7, cellar=0),
    dict(key='medieval', file='medieval-cozy-house.schem', x0=7, z0=1, cw=2, cl=2, ground=12, weight=0.6, cellar=6),
    dict(key='moderna', file='cozymdoerncabin.schem', x0=3, z0=8, cw=3, cl=2, ground=6, weight=0.3),
    dict(key='solar', file='copper-cottage.schem', x0=78, z0=34, cw=3, cl=2, ground=35, weight=0.15, cellar=6),
]
# Themed versions of every house: same building, different interior (vanilla_furni theme + clutter.py catalog).
# Each house gets 5 of the 7 themes, rotating, so every theme shows up across the village.
THEME_CODE = {'encantamento': 'enc', 'alquimia': 'alq', 'create': 'cre', 'ferreiro': 'fer', 'artesao': 'art',
              'biblioteca': 'bib', 'fazendeiro': 'faz'}
_themes = list(THEME_CODE)
CASAS = CASAS + [dict(c, key=c['key'] + THEME_CODE[t], base=c['key'], theme=t, weight=round(c['weight'] * 0.35, 3))
                 for i, c in enumerate(CASAS) for t in (_themes[(i * 2 + k) % len(_themes)] for k in range(5))]
# Special towns, outside the rotation (not in THEME_CODE): one extra building each on a base that suits it.
# floricultura: small cottage; adega: house with cellar; torre_raio: the tallest house (solar, 41 layers).
# laticinio: moderna; vinicola: medieval; celeiro_neve: vermelha; cabana_pescador: robella; alfaiataria: fada; seringueiro: serrana.
_BASE = {c['key']: c for c in CASAS}
CASAS = CASAS + [
    dict(_BASE['cerejeira'], key='floricultura', base='cerejeira', theme='floricultura', weight=0.25),
    dict(_BASE['medieval'], key='adega', base='medieval', theme='adega', weight=0.25),
    dict(_BASE['solar'], key='torre_raio', base='solar', theme='torre_raio', weight=0.25),
    dict(_BASE['moderna'], key='laticinio', base='moderna', theme='laticinio', weight=0.25),
    dict(_BASE['medieval'], key='vinicola', base='medieval', theme='vinicola', weight=0.25),
    dict(_BASE['vermelha'], key='celeiro_neve', base='vermelha', theme='celeiro_neve', weight=0.25),
    dict(_BASE['robella'], key='cabana_pescador', base='robella', theme='cabana_pescador', weight=0.25),
    dict(_BASE['fada'], key='alfaiataria', base='fada', theme='alfaiataria', weight=0.25),
    dict(_BASE['serrana'], key='seringueiro', base='serrana', theme='seringueiro', weight=0.25),
]
ROTS = (0, 90, 180, 270)
# colorways: cada casa sai em NCOLORS cores de casca (c0 = cor do tipo, legada;
# c1/c2 = segundas passadas de cor). Registradas como predios separados para o
# Lost Cities sortear por chunk (nenhuma garantia de raio: com area 19x19 e K cores
# a repeticao exata e inevitavel, mas com 3x tipos ela fica rara e distante).
NCOLORS = 3


def ckey(key, i):
    return key if i == 0 else f'{key}_c{i}'
# casa sem porta de verdade (entrada aberta): lado da frente na rotacao 0
FRONT_R0 = {'moderna': 'south'}
FRONTS_JS = os.path.join(ROOT, 'kubejs', 'startup_scripts', 'sunlitTownsFronts.js')
FRONTS = {}


def is_multi(c):
    return c['cw'] * c['cl'] > 1


def bname(key, rot, cx, cz):
    return f'sunlit:vila_{key}/r{rot}c{cx}{cz}'


# nomes usados pelo convert.py nos citystyles (predios de 1 chunk e multibuildings)
NAMES = [bname(ckey(c['key'], i), r, 0, 0) for c in CASAS if not is_multi(c) for r in ROTS for i in range(NCOLORS)]
MULTIS = [f'sunlit:multi_vila_{ckey(c["key"], i)}_r{r}' for c in CASAS if is_multi(c) for r in ROTS for i in range(NCOLORS)]
WEIGHT = {**{bname(ckey(c['key'], i), r, 0, 0): round(c['weight'] / NCOLORS, 4) for c in CASAS for r in ROTS for i in range(NCOLORS)},
          **{f'sunlit:multi_vila_{ckey(c["key"], i)}_r{r}': round(c['weight'] / NCOLORS, 4) for c in CASAS for r in ROTS for i in range(NCOLORS)}}

LEGACY = {'minecraft:short_grass': 'minecraft:grass', 'minecraft:grass_path': 'minecraft:dirt_path'}
SURFACE = re.compile(r'^minecraft:(grass_block|dirt_path|podzol|coarse_dirt|moss_block|mycelium|rooted_dirt)$')


# ---------------------------------------------------------------- recorte
def auto_ground(g, x0, z0, w, l):
    c = collections.Counter()
    H = len(g)
    for y in range(H - 1):
        for z in range(max(0, z0), min(len(g[0]), z0 + l)):
            for x in range(max(0, x0), min(len(g[0][0]), x0 + w)):
                if SURFACE.match(VF.bid(g[y][z][x])) and VF.is_air(g[y + 1][z][x]):
                    c[y] += 1
    return c.most_common(1)[0][0]


def crop(cfg):
    """grade a partir de gy - porao; a camada `cel` (= porao) e o chao. Retorna (grade, gy, cel)."""
    W, H, L, g, bes = schem.load(os.path.join(SRC, cfg['file']))
    w, l = cfg['cw'] * 16, cfg['cl'] * 16
    x0, z0 = cfg['x0'], cfg['z0']
    gy = cfg['ground'] if cfg['ground'] is not None else auto_ground(g, x0, z0, w, l)
    # 'dig': a casa nao tem subsolo no schematic mas ganha porao escavado (ex. vermelha):
    # as camadas abaixo do chao viram FILLER e o RETOUCH escava a sala nele
    cel = min(cfg.get('cellar', 0), FLOOR_H if cfg.get('dig') else gy, FLOOR_H)
    top = gy
    for y in range(gy, H):
        for z in range(max(0, z0), min(L, z0 + l)):
            for x in range(max(0, x0), min(W, x0 + w)):
                if not VF.is_air(g[y][z][x]):
                    top = y
    h = top - gy + 1 + cel
    out = [[[schem.AIR] * w for _ in range(l)] for _ in range(h)]
    for y in range(h):
        for z in range(l):
            for x in range(w):
                sx, sz = x + x0, z + z0
                sy = y + gy - cel
                if 0 <= sx < W and 0 <= sz < L and sy >= 0 and not (cfg.get('dig') and y < cel):
                    s = g[sy][sz][sx]
                    b = VF.bid(s)
                    out[y][z][x] = LEGACY[b] + s[len(b):] if b in LEGACY else s
                elif y < cel:
                    out[y][z][x] = FILLER
    for z in range(l):
        for x in range(w):
            s = out[cel][z][x]
            if not (VF.is_air(s) or VF.passable(s)):
                continue
            # buraco no chao vira grama, menos a boca da escada do porao (vazio construido embaixo)
            below = out[cel - 1][z][x] if cel else None
            if below is not None and (VF.is_air(below) or not re.match(r'^minecraft:(dirt|stone|grass_block|gravel|andesite|diorite|granite|coarse_dirt)$', VF.bid(below))):
                continue
            out[cel][z][x] = 'minecraft:grass_block[snowy=false]'
    return out, gy, cel


def convert_states(g, salt=''):
    cache = {}
    if salt:
        M.SALT = salt
    for sl in g:
        for row in sl:
            for i, s in enumerate(row):
                if s not in cache:
                    r = M.convert_state(s)
                    r = M.swap_material(r) if r else r
                    cache[s] = r if r else schem.AIR
                row[i] = cache[s]


def dominant_wood(g):
    c = collections.Counter()
    for sl in g:
        for row in sl:
            for s in row:
                n = VF.nm(s)
                if n.endswith(('_planks', '_log', '_wood', '_stairs', '_slab')):
                    w = VF.wood_of(s, None)
                    if w:
                        c[w] += 1
    return c.most_common(1)[0][0] if c else 'oak'


# ---------------------------------------------------------------- rotacao (horario, visto de cima)
CW = {'north': 'east', 'east': 'south', 'south': 'west', 'west': 'north'}
CURVES = {'south_east', 'south_west', 'north_west', 'north_east'}


def rot_dir(d, k):
    for _ in range(k):
        d = CW.get(d, d)
    return d


def rot_state(state, k):
    if k == 0 or '[' not in state:
        return state
    b, p = M.parse(state)
    q = {}
    for key, val in p.items():
        if key in CW:
            q[rot_dir(key, k)] = val
        elif key == 'facing':
            q[key] = rot_dir(val, k)
        elif key == 'axis' and k % 2 and val in ('x', 'z'):
            q[key] = 'z' if val == 'x' else 'x'
        elif key == 'rotation' and val.isdigit():
            q[key] = str((int(val) + 4 * k) % 16)
        elif key == 'shape' and any(t in val for t in CW):
            parts = val.split('_')
            if parts[0] == 'ascending':
                q[key] = 'ascending_' + rot_dir(parts[1], k)
            elif val in ('north_south', 'east_west'):
                q[key] = val if k % 2 == 0 else ('east_west' if val == 'north_south' else 'north_south')
            else:
                a, c = rot_dir(parts[0], k), rot_dir(parts[1], k)
                q[key] = f'{a}_{c}' if f'{a}_{c}' in CURVES else f'{c}_{a}'
        else:
            q[key] = val
    return M.fmt(b, q)


def rotate(g, loot, k):
    for _ in range(k):
        H, L, W = len(g), len(g[0]), len(g[0][0])
        ng = [[[None] * L for _ in range(W)] for _ in range(H)]
        nl = {}
        for y in range(H):
            for z in range(L):
                for x in range(W):
                    nx, nz = L - 1 - z, x
                    ng[y][nz][nx] = rot_state(g[y][z][x], 1)
                    if (x, y, z) in loot:
                        nl[(nx, y, nz)] = loot[(x, y, z)]
        g, loot = ng, nl
    return g, loot


# ---------------------------------------------------------------- frente da casa (para o KubeJS virar a casa para a rua)
SIDES = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}
OPP_SIDE = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}


def fronts(g, cel):
    """lados (north/south/west/east) para onde abrem as portas externas do terreo, o principal primeiro.
    A porta e externa quando um lado do eixo dela da para ceu aberto e o outro fica coberto."""
    H, L, W = len(g), len(g[0]), len(g[0][0])

    def sky(x, y, z):
        return all(VF.is_air(g[yy][z][x]) for yy in range(y, H))

    score = collections.Counter()
    for y in range(cel, min(H, cel + FLOOR_H)):
        for z in range(L):
            for x in range(W):
                s = g[y][z][x]
                if not re.search(r'_door\[.*half=lower', s) or 'trapdoor' in s:
                    continue
                f = re.search(r'facing=(\w+)', s).group(1)
                open_ = {}
                for side in (f, OPP_SIDE[f]):
                    dx, dz = SIDES[side]
                    n = 0
                    for k in range(1, 8):
                        nx, nz = x + dx * k, z + dz * k
                        if not (0 <= nx < W and 0 <= nz < L):
                            n += 8 - k
                            break
                        n += sky(nx, y + 2, nz)
                    open_[side] = n
                if open_[f] == open_[OPP_SIDE[f]]:
                    continue
                out = max(open_, key=open_.get)
                edge = {'north': z, 'south': L - 1 - z, 'west': x, 'east': W - 1 - x}[out]
                score[out] += 1 + 1 / (1 + edge) + (1 if y - cel <= 2 else 0)
    if not score:
        return []
    top = max(score.values())
    return [s for s, v in score.most_common() if v >= 0.6 * top]


def write_fronts():
    with open(FRONTS_JS, 'w', encoding='utf-8') as f:
        f.write('// GERADO por sunlit_tools/towns/schematics.py (nao editar a mao).\n'
                '// Casas da vila de schematic: por rotacao, tamanho em chunks [x, z] e lados com porta para fora\n'
                '// (o principal primeiro). sunlitTownsLostCities.js usa isso para virar a casa para a rua.\n')
        f.write('global.sunlitFronts = ' + json.dumps(FRONTS, sort_keys=True) + ';\n')


# ---------------------------------------------------------------- escrita
POOL = [chr(c) for c in list(range(33, 127)) + list(range(161, 256)) + list(range(0x391, 0x3CA)) + list(range(0x410, 0x450))
        if chr(c) not in '"\\G']
FILLER = 'minecraft:dirt'


def entry(state, loot):
    # propriedades que o bloco nao tem (ex.: stacks em displaydelight:plated_*) saem aqui, antes de gravar
    bid, props = M.parse(state)
    if props:
        state = M.fmt(bid, M.clean_props(bid, props))
    if loot:
        return {'block': state, 'loot': f'sunlit:{loot}'}
    mixed = MIX.blocks_for(state)
    return {'blocks': mixed} if mixed else {'block': state}


def write_json(kind, rl, obj):
    p = os.path.join(DATA, kind, *rl.split(':', 1)[1].split('/')) + '.json'
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f)


def write_chunk(key, rot, cx, cz, g, loot, cel=0):
    """g ja recortado para o chunk (16x16), porao nas `cel` primeiras camadas; grava partes/paletas/predio."""
    H = len(g) - cel
    nparts = max(2, math.ceil(H / FLOOR_H) + (1 if H % FLOOR_H == 0 else 0))
    name = bname(key, rot, cx, cz)
    parts = []

    def emit(tag, ys):
        pal, by = {'G': {'block': FILLER}}, {}
        chars = iter(POOL)
        slices = []
        for y in ys:
            sl = []
            for z in range(16):
                row = []
                for x in range(16):
                    s = g[y][z][x] if 0 <= y < len(g) else (FILLER if y < 0 else schem.AIR)
                    if VF.is_air(s):
                        row.append(' ')
                        continue
                    e = entry(s, loot.get((x, y, z)))
                    key_e = json.dumps(e, sort_keys=True)
                    if key_e not in by:
                        c = next(chars)
                        by[key_e] = c
                        pal[c] = e
                    row.append(by[key_e])
                sl.append(''.join(row))
            slices.append(sl)
        prl = f'{name}_{tag}'
        write_json('palettes', prl + '_palette', {'palette': [dict(char=c, **e) for c, e in pal.items()]})
        write_json('parts', prl, {'xsize': 16, 'zsize': 16, 'refpalette': prl + '_palette', 'slices': slices})
        return prl

    if cel:
        # porao: 6 fatias, as de baixo sao terra e as `cel` de cima sao o porao do schematic
        prl = emit('cellar', range(cel - FLOOR_H, cel))
        parts.append({'top': False, 'cellar': True, 'ground': False, 'part': prl, 'floor': -1})
    # partes: 0 = terreo, 1..n-2 = andares, n-1 = topo (o que sobrar; pode ser so ar)
    for k in range(nparts):
        lo = cel + k * FLOOR_H
        ys = range(lo, min(len(g), lo + FLOOR_H)) if k < nparts - 1 else range(lo, max(len(g), lo + 1))
        tag = 'ground' if k == 0 else ('top' if k == nparts - 1 else f'f{k}')
        prl = emit(tag, ys)
        pe = {'top': tag == 'top', 'cellar': False, 'ground': tag == 'ground', 'part': prl}
        if tag.startswith('f'):
            pe['floor'] = k
        parts.append(pe)
    write_json('buildings', name, {'filler': 'G', 'rubber': ' ', 'allowDoors': False, 'allowFillers': True,
                                   'overrideFloors': True, 'minfloors': nparts - 1, 'maxfloors': nparts - 1,
                                   'mincellars': 1 if cel else 0, 'maxcellars': 1 if cel else 0, 'parts': parts})
    return name


# ---------------------------------------------------------------- retoques por casa (grade ja convertida, antes da rotacao)
def table_row(block, x0, x1, z0, z1):
    """mesa de tampo continuo: props de conexao (refurbished table / cfm coffee table) pelos vizinhos"""
    out = {}
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            p = dict(east=x < x1, north=z > z0, south=z < z1, west=x > x0)
            if block.startswith('cfm:'):
                p['tall'] = False
            out[(x, z)] = block + '[' + ','.join(f'{k}={str(v).lower()}' for k, v in sorted(p.items())) + ']'
    return out


def retouch_vermelha(v):
    # floreira de laje de andesito boiando 1 bloco fora da fachada sul (z15), sob as janelas
    for x, y, z in v.cells():
        if z == 15 and VF.nm(v.get(x, y, z)) == 'polished_andesite_slab':
            v.set(x, y, z, VF.AIR)
    # chamine de dispenser no telhado -> fogueira acesa (dispenser parecendo entupido).
    # So la em cima (os de baixo sao da contracao da porta, com a mesma moldura de alcapao).
    top = len(v.g) - 6
    for x, y, z in v.cells():
        if y < top or VF.bid(v.get(x, y, z)) != 'minecraft:dispenser':
            continue
        below = v.get(x, y - 1, z)
        if y == 0 or VF.is_air(below) or not VF.floorlike(below):
            continue
        v.set(x, y, z, 'minecraft:campfire[facing=north,lit=true]')
        v.stats['chamine_virou_fogueira'] += 1
    # sem porao: com ground=0 a grade comeca no terreno (camada 0), as palafitas de quartzo
    # sao as camadas 1-2 e o piso da casa e a camada 3; nada e escavado.
    # luminaria de funil + beacon pendurada no teto (e a lanterna presa num alcapao ao lado) -> lanterna com corrente
    for x, y, z in v.cells():
        if VF.nm(v.get(x, y, z)) == 'beacon' and VF.nm(v.get(x, y + 1, z)) == 'hopper':
            v.set(x, y + 1, z, 'minecraft:chain[axis=y]')
            v.set(x, y, z, 'minecraft:lantern[hanging=true]')
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if VF.nm(v.get(x + dx, y, z + dz)) == 'lantern' and VF.nm(v.get(x + dx, y + 1, z + dz)).endswith('_trapdoor'):
                    v.set(x + dx, y + 1, z + dz, 'minecraft:chain[axis=y]')
    # banheiro do 2o andar (x9-15, z6-11, y9-16): vidro de cor vira parede, cortinas de alcapao interiores somem,
    # beacons do teto viram laje de carvalho (o teto ao redor e laje de carvalho)
    for x, y, z in v.cells():
        if not (9 <= x <= 15 and 6 <= z <= 11 and 9 <= y <= 16):
            continue
        nm = VF.nm(v.get(x, y, z))
        if nm in ('light_gray_stained_glass', 'light_blue_stained_glass'):
            v.set(x, y, z, 'minecraft:magenta_concrete')
            v.stats['vidro_virou_parede'] += 1
        elif nm.endswith('_trapdoor') and 10 <= x <= 14 and 8 <= z <= 10:
            v.set(x, y, z, VF.AIR)
            v.stats['alcapao_interno_removido'] += 1
    for x, y, z in v.cells():
        if VF.nm(v.get(x, y, z)) == 'beacon' and 9 <= x <= 15 and 6 <= z <= 11 and y >= 16:
            v.set(x, y, z, 'minecraft:oak_slab[type=bottom]')
            v.stats['beacon_virou_laje'] += 1
    # atico (y18): sai o trapdoor de cada canto do banheiro e o buraco que eles formam (vira concreto de parede)
    for x, y, z in ((7, 19, 6), (8, 19, 6), (7, 19, 8), (8, 19, 8)):
        if VF.nm(v.get(x, y, z)).endswith('_trapdoor'):
            v.set(x, y, z, VF.AIR)
            v.stats['alcapao_canto_removido'] += 1
    if VF.is_air(v.get(8, 18, 8)):
        v.set(8, 18, 8, 'minecraft:magenta_concrete')
    # atico: a mesa e a cadeira saem da metade leste (x8-15) e vao para a oeste (x0-7)
    for x, z in ((10, 8), (10, 9)):
        if VF.bid(v.get(x, 18, z)) == 'refurbished_furniture:oak_table':
            v.set(x, 18, z, VF.AIR)
    if 'another_furniture' in VF.bid(v.get(9, 18, 9)) and 'chair' in VF.nm(v.get(9, 18, 9)):
        v.set(9, 18, 9, VF.AIR)
    for (x, z), s in table_row('refurbished_furniture:oak_table', 6, 6, 11, 12).items():
        if VF.is_air(v.get(x, 18, z)) or VF.nm(v.get(x, 18, z)).endswith('carpet'):
            v.set(x, 18, z, s)
    if VF.is_air(v.get(5, 18, 11)):
        v.set(5, 18, 11, 'another_furniture:oak_chair[facing=east,tucked=false,variant=1]')
        v.stats['cadeira_atico'] += 1
    # mesas de jantar: cadeira solta (frente livre, sem mesa) sai; cada mesa em linha ganha cadeira nas pontas livres
    tables = {}
    for x, y, z in v.cells():
        if VF.bid(v.get(x, y, z)) == 'refurbished_furniture:oak_table':
            tables.setdefault(y, set()).add((x, z))
    vec = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}
    for x, y, z in v.cells():
        s = v.get(x, y, z)
        m = re.search(r'facing=(\w+)', s)
        if not m or 'chair' not in VF.nm(s) or not VF.bid(s).startswith('another_furniture:'):
            continue
        dx, dz = vec[m.group(1)]
        if VF.is_air(v.get(x + dx, y, z + dz)) and any(
                abs(x - tx) <= 2 and abs(z - tz) <= 2 for tx, tz in tables.get(y, ())):
            v.set(x, y, z, VF.AIR)
            v.stats['cadeira_solta_removida'] += 1
    for y, cells in tables.items():
        seen = set()
        for start in sorted(cells):
            if start in seen:
                continue
            comp, stack = [], [start]
            seen.add(start)
            while stack:
                p = stack.pop()
                comp.append(p)
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (p[0] + dx, p[1] + dz)
                    if q in cells and q not in seen:
                        seen.add(q)
                        stack.append(q)
            xs = [p[0] for p in comp]
            zs = [p[1] for p in comp]
            if len(set(xs)) == 1:
                ends = [((xs[0], min(zs) - 1), 'south'), ((xs[0], max(zs) + 1), 'north')]
            elif len(set(zs)) == 1:
                ends = [((min(xs) - 1, zs[0]), 'east'), ((max(xs) + 1, zs[0]), 'west')]
            else:
                continue
            for (cx, cz), facing in ends:
                if VF.is_air(v.get(cx, y, cz)):
                    v.set(cx, y, cz, f'another_furniture:oak_chair[facing={facing},tucked=false,variant=1]')
                    v.stats['cadeira_colocada'] += 1
    # cozinha: cada balcao, gaveta, pia e armario fica com a frente para o piso livre e as costas na parede
    for x, y, z in v.cells():
        s = v.get(x, y, z)
        m = re.search(r'facing=(\w+)', s)
        if 'kitchen' not in VF.nm(s) or not m:
            continue

        def ok(f):
            dx, dz = vec[f]
            return VF.is_air(v.get(x + dx, y, z + dz)) and not VF.is_air(v.get(x - dx, y, z - dz))

        if ok(m.group(1)):
            continue
        opts = [f for f in vec if ok(f)]
        if opts:
            v.set(x, y, z, s.replace(f'facing={m.group(1)}', f'facing={opts[0]}'))
            v.stats['cozinha_virada'] += 1
    # kitchen: a unit whose front faces a solid block turns to an open neighbour with floor; with none, it becomes wall
    for x, y, z in v.cells():
        s = v.get(x, y, z)
        m = re.search(r'facing=(\w+)', s)
        if 'kitchen' not in VF.nm(s) or 'sink' in VF.nm(s) or not m:
            continue
        dx, dz = vec[m.group(1)]
        if VF.is_air(v.get(x + dx, y, z + dz)):
            continue
        opts = [f for f, (a, b) in vec.items()
                if VF.is_air(v.get(x + a, y, z + b)) and not VF.is_air(v.get(x + a, y - 1, z + b))]
        if opts:
            v.set(x, y, z, s.replace(f'facing={m.group(1)}', f'facing={opts[0]}'))
        else:
            v.set(x, y, z, 'minecraft:magenta_concrete')
        v.stats['cozinha_frente_parede'] += 1


def retouch_moderna(v):
    """moveis montados com bloco vanilla que o vanilla_furni nao reconhece (coordenadas desta casa)"""
    AIR = VF.AIR
    for x, y, z in v.cells():
        n = VF.nm(v.get(x, y, z))
        if n == 'ancient_debris':  # cabeceira/divisoria do quarto
            v.set(x, y, z, 'minecraft:dark_oak_planks')
        elif n == 'anvil':  # bigorna com folha em cima = vaso de planta
            v.set(x, y, z, 'minecraft:decorated_pot[facing=north,waterlogged=false]')
    # sala de jantar: mesa de escadas invertidas 9x3 (x19..27, z6..8) e cadeiras de escada de quartzo so de um
    # lado -> mesa 9x2 com cadeiras dos dois lados
    for x in range(19, 28):
        v.set(x, 1, 6, AIR)
        v.set(x, 1, 9, AIR)
    for (x, z), s in table_row('refurbished_furniture:dark_oak_table', 19, 27, 7, 8).items():
        v.set(x, 1, z, s)
    for x in (20, 22, 24, 26):
        v.set(x, 1, 6, 'another_furniture:birch_chair[facing=south,tucked=false,variant=1]')
        v.set(x, 1, 9, 'another_furniture:birch_chair[facing=north,tucked=false,variant=1]')
    v.set(21, 2, 7, 'minecraft:candle[candles=3,lit=true]')
    v.set(25, 2, 8, 'minecraft:potted_azure_bluet')
    # sala da lareira: sofa de granito com encosto de alcapao (x36..37, z5..9) -> sofa de verdade virado
    # para a lareira; mesa de centro de vidro fume com tapete (x39..40, z6..8) -> mesa de centro
    for z in range(5, 10):
        for x in (36, 37):
            v.set(x, 1, z, AIR)
            v.set(x, 2, z, AIR)
        v.set(37, 1, z, 'another_furniture:white_sofa[facing=east,type=single]')
    for (x, z), s in table_row('cfm:dark_oak_coffee_table', 39, 40, 6, 8).items():
        v.set(x, 1, z, s)
        v.set(x, 2, z, AIR)
    # cama vermelha deitada em cima do consolo da lareira
    v.set(42, 4, 4, AIR)
    v.set(42, 4, 5, 'minecraft:candle[candles=3,lit=true]')
    # quarto: criados-mudos de escada de deepslate e "abajur" de end rod
    for x in (7, 10):
        v.set(x, 1, 11, 'refurbished_furniture:dark_oak_drawer[facing=north,left=false,open=false,right=false]')
        v.set(x, 2, 11, 'refurbished_furniture:white_lamp[powered=false]')


def retouch_medieval(v):
    """o terreo e um salao aberto com cozinha em U e peninsula de pedra; o auto-mobiliar via comodos vazios e
    espalhava cama em cima da peninsula, cama/bau/escrivaninha no salao e privada/cama nas baias do estabulo"""
    AIR = VF.AIR
    # tudo que o vanilla_furni inventou no salao (y11-12) e nas baias (y7)
    for x, y, z in [(20, 11, 13), (15, 11, 17), (17, 11, 17), (18, 11, 17), (16, 11, 18), (17, 11, 18), (19, 11, 18),
                    (15, 11, 20), (25, 11, 21), (26, 11, 21), (26, 11, 22), (15, 11, 23), (16, 11, 23),
                    (6, 7, 14), (6, 7, 15), (4, 7, 15)]:
        v.set(x, y, z, AIR)
    # bebedouros do estabulo voltam a ser caldeirao com agua
    v.set(4, 7, 16, 'minecraft:water_cauldron[level=3]')
    v.set(6, 7, 16, 'minecraft:water_cauldron[level=3]')
    # vaso de tulipa na prateleira de laje (o vanilla_furni trocou por barril)
    v.set(24, 14, 12, 'minecraft:potted_orange_tulip')
    # cozinha: bancada da parede norte (x20-26, z12) e da parede leste (x26, z13-15); tampo de carpete sai
    v.set(20, 11, 12, 'refurbished_furniture:spruce_kitchen_drawer[facing=north,open=false]')
    for x in (22, 23, 25, 26):
        v.set(x, 11, 12, 'refurbished_furniture:spruce_kitchen_cabinetry[facing=north,shape=default]')
    v.set(24, 11, 12, 'refurbished_furniture:spruce_kitchen_sink[facing=north]')
    v.set(26, 11, 13, 'refurbished_furniture:spruce_kitchen_drawer[facing=east,open=false]')
    v.set(26, 11, 14, 'refurbished_furniture:spruce_kitchen_cabinetry[facing=east,shape=default]')
    v.set(26, 11, 15, 'refurbished_furniture:spruce_kitchen_storage_cabinet[facing=east,hinge=left,open=false]')
    for x, z in [(20, 12), (22, 12), (23, 12), (25, 12), (26, 13), (26, 14), (26, 15)]:
        v.set(x, 12, z, AIR)
    v.set(24, 12, 12, AIR)
    # peninsula de pedra 5x2 com carpete (x22-26, z16-17) -> mesa de jantar com cadeiras dos dois lados
    for (x, z), s in table_row('refurbished_furniture:spruce_table', 22, 26, 16, 17).items():
        v.set(x, 11, z, s)
        v.set(x, 12, z, AIR)
    for x in (23, 25):
        v.set(x, 11, 15, 'another_furniture:spruce_chair[facing=south,tucked=false,variant=1]')
        v.set(x, 11, 18, 'another_furniture:spruce_chair[facing=north,tucked=false,variant=1]')
    v.set(23, 12, 16, 'minecraft:candle[candles=3,lit=true]')
    v.set(25, 12, 17, 'minecraft:potted_azure_bluet')
    # canto de leitura na ala oeste (livre da escada em caracol)
    v.set(15, 11, 17, 'another_furniture:spruce_chair[facing=south,tucked=false,variant=3]')
    v.set(17, 11, 17, 'another_furniture:spruce_chair[facing=south,tucked=false,variant=3]')
    for (x, z), s in table_row('refurbished_furniture:spruce_table', 15, 17, 18, 18).items():
        v.set(x, 11, z, s)
    v.set(16, 12, 18, 'minecraft:lantern[hanging=false]')
    # stall (x0-10, z11-17): the slab roof tops out at y11 (source y17); anything above it goes, roof slabs/stairs stay
    for x, y, z in list(v.cells()):
        if 0 <= x <= 10 and 11 <= z <= 17 and y >= 11 and not VF.is_air(v.get(x, y, z)) \
                and not (y == 11 and VF.nm(v.get(x, y, z)).endswith(('_stairs', '_slab', 'trapdoor'))):
            v.set(x, y, z, AIR)
            v.stats['estabulo_acima_telhado'] += 1
    # floating blocks: no support below or on the sides, removed (loose leaves, trapdoors, slabs in the air)
    for x, y, z in list(v.cells()):
        s = v.get(x, y, z)
        if y == 0 or VF.is_air(s) or 'hanging=true' in s or 'chain' in s or not VF.is_air(v.get(x, y - 1, z)):
            continue
        # hatch and stairs of the cellar (underground, y<6) are the way down: they stay even when hanging in air
        if y < 6 and (VF.nm(s).endswith('trapdoor') or VF.nm(s).endswith('_stairs')):
            continue
        if all(VF.is_air(v.get(x + dx, y, z + dz)) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            v.set(x, y, z, AIR)
            v.stats['bloco_flutuante_removido'] += 1
    # suporte em cadeia: o que nao esta ligado ao chao (y<=6) por blocos vizinhos sai, em cascata
    # (jardineira de janela presa a uma fila de lajes soltas no ar, com a planta e as flores por cima)
    ligados = set()
    fila = [(x, y, z) for x, y, z in v.cells() if y <= 6]
    ligados.update(fila)
    while fila:
        x, y, z = fila.pop()
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            p = (x + dx, y + dy, z + dz)
            if p not in ligados and v.inside(*p) and not VF.is_air(v.get(*p)):
                ligados.add(p)
                fila.append(p)
    for x, y, z in list(v.cells()):
        if y > 6 and (x, y, z) not in ligados and not VF.is_air(v.get(x, y, z)):
            v.set(x, y, z, AIR)
            v.stats['sem_apoio_removido'] += 1
    # jardineira de janela (grama sobre alcapao de topo): so existe apoiada numa parede; sem parede embaixo o alcapao
    # e a grama saem, junto com as flores e plantas em vaso em cima (grama nunca fica suspensa como vaso)
    for x, y, z in list(v.cells()):
        if y > 6 and VF.nm(v.get(x, y, z)) == 'grass_block' and VF.nm(v.get(x, y - 1, z)).endswith('trapdoor'):
            t = v.get(x, y - 1, z)
            if 'half=top' in t and VF.is_air(v.get(x, y - 2, z)):
                v.set(x, y, z, AIR)
                # o alcapao so sai se nao encosta em parede nenhuma (as lajes da cornija contam como parede)
                if all(VF.is_air(v.get(x + dx, y - 1, z + dz)) or VF.nm(v.get(x + dx, y - 1, z + dz)).endswith('trapdoor') for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    v.set(x, y - 1, z, AIR)
                if not VF.is_air(v.get(x, y + 1, z)):
                    v.set(x, y + 1, z, AIR)
                v.stats['jardineira_suspensa_removida'] += 1
    # poco no piso (y6) sobre o caminho da escada do porao: alcapao fechado, com y5 e y7 livres por baixo do topo
    floor_wood = 'spruce'
    for x, z in ((15, 19), (15, 20), (16, 18), (16, 21), (17, 21)):
        s = str(v.get(x, 6, z))
        if s.startswith('minecraft:') and s.endswith('_planks'):
            floor_wood = s[len('minecraft:'):-len('_planks')]
            break
    for z in (19, 20):
        if VF.is_air(v.get(16, 6, z)):
            v.set(16, 6, z, 'minecraft:%s_trapdoor[facing=east,half=top,open=false,waterlogged=false]' % floor_wood)
            v.stats['alcapao_piso_porao'] += 1


def ladder_mouths(house, v, cel):
    """boca de escada do porao sem escada: coluna de ar DENTRO de um comodo do terreo ate o
    piso do porao, ganha escada (ladder) para descer/subir. Sem isso o porao existe mas nao
    tem acesso. Depressao de terreno fora de comodo nao conta."""
    if not cel:
        return 0
    rooms = {c for (cx, cy, cz) in house.room_kind if cy == cel for c in [(cx, cz)]}
    n = 0
    for (x, z) in sorted(rooms):
        if not VF.is_air(v.get(x, cel, z)) or not VF.is_air(v.get(x, cel - 1, z)):
            continue
        depth = 0
        y = cel - 1
        while y >= 0 and VF.is_air(v.get(x, y, z)):
            depth += 1
            y -= 1
        if depth < 2 or y < 0 or not VF.floorlike(v.get(x, y, z)):
            continue
        walls = [d for d, (dx, dz) in VF.DIRS.items()
                 if VF.wallish(v.get(x + dx, cel, z + dz))]
        if len(walls) < 2:
            continue
        d = walls[0]
        for yy in range(cel - 1, cel - 1 - depth, -1):
            v.set(x, yy, z, f'minecraft:ladder[facing={VF.OPP[d]}]')
        n += 1
    return n


def retouch_fada(v):
    # a cabana vinha com ~24 lanternas num so chunk (parecia arvore de natal):
    # afina para umas 8 espalhadas (distancia minima 7 entre elas)
    spots = [(x, y, z) for x, y, z in v.cells() if 'lantern' in VF.nm(v.get(x, y, z))]
    keep = []
    for s in sorted(spots):
        if all(abs(s[0] - k[0]) + abs(s[1] - k[1]) + abs(s[2] - k[2]) >= 7 for k in keep):
            keep.append(s)
    for x, y, z in set(spots) - set(keep):
        v.set(x, y, z, VF.AIR)
        v.stats['lanterna_afinada'] += 1


def retouch_robella(v):
    # privada/lavatorio do terreo grudado em cerca (corrimao da varanda) ou com
    # 3+ lados abertos = nasceu para fora (problema antigo da varanda da frente);
    # as de banheiro fechado ficam
    for x, y, z in v.cells():
        s = v.get(x, y, z)
        n = VF.nm(s)
        if y > 2 or ('toilet' not in n and 'basin' not in n):
            continue
        air = sum(1 for d in VF.DIRS if VF.is_air(v.nb(x, y, z, d)))
        fence = any('fence' in VF.nm(v.nb(x, y, z, d)) for d in VF.DIRS)
        if air >= 3 or fence:
            v.set(x, y, z, VF.AIR)
            v.stats['privada_externa_removida'] += 1
    # wall grudado em vidro de janela com ar do outro lado = pilar externo na
    # frente da janela (a arcada da fachada); sai, o arco de cima continua de viga
    for x, y, z in v.cells():
        s = v.get(x, y, z)
        if not VF.nm(s).endswith('_wall'):
            continue
        for d in VF.DIRS:
            if 'glass' not in v.nb(x, y, z, d):
                continue
            dx, dz = VF.DIRS[VF.OPP[d]]
            if VF.is_air(v.get(x + dx, y, z + dz)):
                v.set(x, y, z, VF.AIR)
                v.stats['parede_na_janela'] += 1
                break
    # passarela de tabuas flutuando ao lado da chamine (nao e telhado) -> sai
    for x in (18, 19):
        for z in range(14, 20):
            if VF.nm(v.get(x, 19, z)).endswith('_planks') and VF.is_air(v.get(x, 18, z)):
                v.set(x, 19, z, VF.AIR)
                v.stats['tabua_da_chamine'] += 1
    # poco de acesso sem uso no terreo (vao fechado com ar embaixo) -> piso
    for x, y, z in v.cells():
        if y != 1 or not VF.is_air(v.get(x, y, z)) or not VF.is_air(v.get(x, y - 1, z)):
            continue
        nbs = [v.nb(x, y, z, d) for d in VF.DIRS]
        if sum(1 for b in nbs if not VF.is_air(b)) < 3:
            continue
        if any(re.search(r'_door$|ladder|_stairs$', VF.nm(b)) for b in nbs):
            continue
        v.set(x, y, z, 'minecraft:oak_planks')
        v.stats['buraco_no_piso'] += 1


def retouch_serrana(v):
    """toilet and lever that ended up on the west porch become air; the ladder in the
    double-height west room (x12 z15, y3..9) climbs into the ceiling with no floor above, so it goes too"""
    for x, y, z in ((9, 2, 21), (8, 1, 24)):
        v.set(x, y, z, VF.AIR)
        v.stats['serrana_fora_removido'] += 1
    for y in range(3, 10):
        if VF.nm(v.get(12, y, 15)) == 'ladder':
            v.set(12, y, 15, VF.AIR)
            v.stats['serrana_escada_removida'] += 1


CEREJEIRA_TERRAIN = re.compile(r'^(grass_block|dirt|podzol|dirt_path|coarse_dirt|gravel|clay|moss_block|rooted_dirt)$')
CEREJEIRA_PLANT = re.compile(r'(grass|fern|flower|tulip|allium|bluet|daisy|cornflower|lily_of_the_valley|orchid|'
                             r'dandelion|poppy|sapling|mushroom|berry_bush|dead_bush|azalea|petals|wither_rose|'
                             r'lilac|peony|rose_bush|pitcher_plant|torchflower)$')


def retouch_cerejeira(v):
    """ground=0: layer 0 is the grade terrain (street level) and the house deck is layer 1 (planks and slabs).
    The terrain mound outside the house box (terrain at layers >=1) is flattened to grade. Plants left floating
    over the removed mound go too, except a lone topmost plant that drops to layer 1 over grade terrain."""
    # grid coords of the house box (crop(): grid x = schematic x + 1, grid z = schematic z + 1, gy = 0):
    # schematic x5..17, z7..23 -> grid x6..18, z8..24
    bx0, bx1, bz0, bz1 = 6, 18, 8, 24
    for x, y, z in list(v.cells()):
        if y < 1 or (bx0 <= x <= bx1 and bz0 <= z <= bz1):
            continue
        if CEREJEIRA_TERRAIN.match(VF.nm(v.get(x, y, z))):
            v.set(x, y, z, VF.AIR)
            v.stats['cerejeira_morro_aplainado'] += 1
    for x in range(v.W):
        for z in range(v.L):
            if bx0 <= x <= bx1 and bz0 <= z <= bz1:
                continue
            while True:
                floating = [y for y in range(1, v.H)
                            if CEREJEIRA_PLANT.search(VF.nm(v.get(x, y, z))) and VF.is_air(v.get(x, y - 1, z))]
                if not floating:
                    break
                y = max(floating)
                plants = [yy for yy in range(v.H) if CEREJEIRA_PLANT.search(VF.nm(v.get(x, yy, z)))]
                if len(plants) == 1 and y > 1 and VF.is_air(v.get(x, 1, z)) and \
                        CEREJEIRA_TERRAIN.match(VF.nm(v.get(x, 0, z))):
                    v.set(x, 1, z, v.get(x, y, z))
                    v.set(x, y, z, VF.AIR)
                    v.stats['cerejeira_planta_desceu'] += 1
                else:
                    v.set(x, y, z, VF.AIR)
                    v.stats['cerejeira_planta_flutuante_removida'] += 1
    # wood/log that hangs over air down to the ground layer (no solid between it and the ground) is a
    # floating hull log: the copies with a wood swap (create: jungle) left a row of them above the grass
    for x, y, z in list(v.cells()):
        nm = VF.nm(v.get(x, y, z))
        if y < 2 or not (nm.endswith(('_log', '_wood')) and not nm.endswith('_planks')):
            continue
        if not VF.is_air(v.get(x, y - 1, z)):
            continue
        k = y - 1
        while k > 0 and VF.is_air(v.get(x, k, z)):
            k -= 1
        if k == 0 and not VF.is_air(v.get(x, 0, z)):
            v.set(x, y, z, VF.AIR)
            v.stats['cerejeira_madeira_suspensa_removida'] += 1


def fix_windows(v):
    """2026-10-10 (pedido do dono, 3a vez): janela nunca tem wall no meio e persiana dos
    dois lados. Vale para TODAS as casas (o retouch_robella so limpava a robella)."""
    for x, y, z in v.cells():
        if not VF.nm(v.get(x, y, z)).endswith('_wall'):
            continue
        removed = False
        for d in ('north', 'south', 'east', 'west'):
            nb = v.nb(x, y, z, d)
            if 'glass' not in nb and 'pane' not in nb:
                continue
            dx, dz = VF.DIRS[VF.OPP[d]]
            other = v.get(x + dx, y, z + dz)
            # montante entre dois vidros (janela 3x3 com pilar no meio) ou pilar grudado
            # no vidro com ar do outro lado (arcada na frente da janela): sai
            if 'glass' in other or 'pane' in other or VF.is_air(other):
                v.set(x, y, z, VF.AIR)
                v.stats['parede_na_janela'] += 1
                removed = True
                break
        if removed:
            continue
    # persiana (trapdoor aberto) de um lado so do vidro -> espelha a que existe
    for x, y, z in list(v.cells()):
        n = VF.nm(v.get(x, y, z))
        if 'glass' not in n and 'pane' not in n:
            continue
        for d, opp in (('east', 'west'), ('west', 'east'), ('north', 'south'), ('south', 'north')):
            dx, dz = VF.DIRS[d]
            ox, oz = VF.DIRS[opp]
            a, b = v.get(x + dx, y, z + dz), v.get(x + ox, y, z + oz)
            na, nb_ = VF.nm(a), VF.nm(b)
            if na.endswith('_trapdoor') and VF.props(a).get('open') == 'true' and not nb_.endswith('_trapdoor'):
                if VF.is_air(b) or 'glass' in nb_ or 'pane' in nb_:
                    v.set(x + ox, y, z + oz, a)
                    v.stats['persiana_espelhada'] += 1


def _solid(v, x, y, z):
    return v.inside(x, y, z) and not VF.is_air(v.get(x, y, z))


def retouch_floricultura(v):
    """cerejeira retouch first, then the greenhouse: the roof stairs and slabs of the top layer become glass panes"""
    retouch_cerejeira(v)
    top = max(y for x, y, z in v.cells() if not VF.is_air(v.get(x, y, z)))
    for x, y, z in list(v.cells()):
        s = v.get(x, y, z)
        if y == top and VF.nm(s).endswith(('_stairs', '_slab')):
            v.set(x, y, z, 'minecraft:glass_pane')
            v.stats['floricultura_vidro'] += 1


def retouch_adega(v):
    """medieval retouch first, then two casks (aging and ancient) against a wall on the lowest floor layer
    (the cellar when there is one), at least 3 blocks apart; the lowest spots come first"""
    retouch_medieval(v)
    spots = []
    for x, y, z in sorted(v.cells(), key=lambda c: (c[1], c[0], c[2])):
        if VF.is_air(v.get(x, y, z)) and _solid(v, x, y - 1, z) and any(_solid(v, x + dx, y, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            if all(abs(x - a) + abs(z - b) >= 3 for a, _, b in spots):
                spots.append((x, y, z))
        if len(spots) == 2:
            break
    # casks face away from the wall they stand against
    dirs = {(1, 0): 'east', (-1, 0): 'west', (0, -1): 'north', (0, 1): 'south'}
    for (x, y, z), cask in zip(spots, ('society:aging_cask', 'society:ancient_cask')):
        dx, dz = next(d for d in dirs if _solid(v, x + d[0], y, z + d[1]))
        v.set(x, y, z, f'{cask}[facing={dirs[(-dx, -dz)]}]')
        v.stats['adega_barrica'] += 1


def retouch_torre_raio(v):
    """charging rod on the highest block of the roof (near the middle of the grid) with a lightning rod above it"""
    cells = [c for c in v.cells() if not VF.is_air(v.get(*c))]
    cx = sum(c[0] for c in cells) / len(cells)
    cz = sum(c[2] for c in cells) / len(cells)
    # highest roof block that still has room above it inside the grid (the top layer may touch the grid edge)
    free = [c for c in cells if v.inside(c[0], c[1] + 1, c[2]) and VF.is_air(v.get(c[0], c[1] + 1, c[2]))]
    if not free:
        return
    top = max(c[1] for c in free)
    x, y, z = min((c for c in free if c[1] == top), key=lambda c: (c[0] - cx) ** 2 + (c[2] - cz) ** 2)
    v.set(x, y + 1, z, 'society:charging_rod[facing=north]')
    v.stats['torre_carregador'] += 1
    # one lightning rod beside the charging rod (same layer), on the first free side
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if v.inside(x + dx, y + 1, z + dz) and VF.is_air(v.get(x + dx, y + 1, z + dz)):
            v.set(x + dx, y + 1, z + dz, 'minecraft:lightning_rod')
            v.stats['torre_para_raios'] += 1
            break


_DIRS = {(1, 0): 'east', (-1, 0): 'west', (0, -1): 'north', (0, 1): 'south'}


def _wall_spots(v, n, gap=3):
    """up to n free cells on the lowest floor layers that touch a solid block, at least gap blocks apart (lowest first)"""
    spots = []
    for x, y, z in sorted(v.cells(), key=lambda c: (c[1], c[0], c[2])):
        if VF.is_air(v.get(x, y, z)) and _solid(v, x, y - 1, z) and any(_solid(v, x + dx, y, z + dz) for dx, dz in _DIRS):
            if all(abs(x - a) + abs(z - b) >= gap for a, _, b in spots):
                spots.append((x, y, z))
        if len(spots) == n:
            break
    return spots


def _face_away(v, x, y, z, block):
    """block facing away from the first solid side of its cell"""
    dx, dz = next(d for d in _DIRS if _solid(v, x + d[0], y, z + d[1]))
    v.set(x, y, z, f'{block}[facing={_DIRS[(-dx, -dz)]}]')


def retouch_laticinio(v):
    """moderna retouch first, then a cheese press and a mayonnaise machine against the walls of the lowest floor layer"""
    retouch_moderna(v)
    for (x, y, z), block in zip(_wall_spots(v, 2), ('society:cheese_press', 'society:mayonnaise_machine')):
        _face_away(v, x, y, z, block)
        v.stats['laticinio_maquina'] += 1


def retouch_vinicola(v):
    """medieval retouch first, then two wine kegs and a preserves jar against the walls of the lowest floor layer"""
    retouch_medieval(v)
    for (x, y, z), block in zip(_wall_spots(v, 3), ('society:wine_keg', 'society:wine_keg', 'society:preserves_jar')):
        _face_away(v, x, y, z, block)
        v.stats['vinicola_barrica'] += 1


def retouch_celeiro_neve(v):
    """vermelha retouch first, then a feeding trough against a wall and one or two cold blocks on the free cells beside it"""
    retouch_vermelha(v)
    spots = _wall_spots(v, 1)
    if not spots:
        return
    x, y, z = spots[0]
    _face_away(v, x, y, z, 'society:feeding_trough')
    v.stats['celeiro_cocho'] += 1
    free = [(x + dx, y, z + dz) for dx, dz in _DIRS if v.inside(x + dx, y, z + dz) and VF.is_air(v.get(x + dx, y, z + dz))]
    for (cx, cy, cz), block in zip(free[:2], ('minecraft:packed_ice', 'minecraft:blue_ice')):
        v.set(cx, cy, cz, block)
        v.stats['celeiro_gelo'] += 1


def retouch_cabana_pescador(v):
    """robella retouch first, then a fish pond, a fish pond basket and a crab trap against the walls of the lowest floor layer"""
    retouch_robella(v)
    spots = _wall_spots(v, 3)
    if len(spots) < 3:
        return
    _face_away(v, *spots[0], 'society:fish_pond')
    v.set(*spots[1], 'society:fish_pond_basket')
    _face_away(v, *spots[2], 'crabbersdelight:crab_trap')
    v.stats['cabana_pesca'] += 1


def retouch_alfaiataria(v):
    """fada retouch first, then a sewing table against a wall and two wool blocks on the next free spots"""
    retouch_fada(v)
    spots = _wall_spots(v, 3)
    if not spots:
        return
    _face_away(v, *spots[0], 'legendarysurvivaloverhaul:sewing_table')
    for (x, y, z), block in zip(spots[1:], ('minecraft:white_wool', 'minecraft:gray_wool')):
        v.set(x, y, z, block)
    v.stats['alfaiataria_mesa'] += 1


def retouch_seringueiro(v):
    """serrana retouch first, then up to two tappers on free cells beside the logs, two barrels against the walls,
    and a small orchard of four fruit saplings on the lowest free cells (not blacklisted)"""
    retouch_serrana(v)
    logs = [c for c in v.cells() if VF.nm(v.get(*c)).endswith('_log')]
    tappers = 0
    for x, y, z in logs:
        for dx, dz in _DIRS:
            if tappers < 2 and v.inside(x + dx, y, z + dz) and VF.is_air(v.get(x + dx, y, z + dz)):
                _face_away(v, x + dx, y, z + dz, 'society:tapper')
                tappers += 1
                v.stats['seringueiro_sangrador'] += 1
                break
    for (x, y, z), block in zip(_wall_spots(v, 2), ('minecraft:barrel[facing=up]', 'minecraft:barrel[facing=up]')):
        v.set(x, y, z, block)
        v.stats['seringueiro_barril'] += 1
    orchard = [c for c in sorted(v.cells(), key=lambda c: (c[1], c[0], c[2]))
               if VF.is_air(v.get(*c)) and _solid(v, c[0], c[1] - 1, c[2])]
    picked = []
    for c in orchard:
        if all(abs(c[0] - a) + abs(c[2] - b) >= 2 for a, _, b in picked):
            picked.append(c)
        if len(picked) == 4:
            break
    for (x, y, z), sapling in zip(picked, ('pamhc2trees:apple_sapling', 'pamhc2trees:orange_sapling',
                                           'pamhc2trees:cherry_sapling', 'pamhc2trees:lemon_sapling')):
        v.set(x, y, z, sapling)
        v.stats['seringueiro_pomar'] += 1


RETOUCH = {'vermelha': retouch_vermelha, 'moderna': retouch_moderna, 'medieval': retouch_medieval,
           'robella': retouch_robella, 'fada': retouch_fada, 'serrana': retouch_serrana,
           'cerejeira': retouch_cerejeira, 'floricultura': retouch_floricultura, 'adega': retouch_adega,
           'torre_raio': retouch_torre_raio, 'laticinio': retouch_laticinio, 'vinicola': retouch_vinicola,
           'celeiro_neve': retouch_celeiro_neve, 'cabana_pescador': retouch_cabana_pescador,
           'alfaiataria': retouch_alfaiataria, 'seringueiro': retouch_seringueiro}


def build(cfg, write=True):
    g, gy, cel = crop(cfg)
    convert_states(g, salt=cfg['key'])
    wood = dominant_wood(g)
    v = VF.Vox(g)
    house = VF.House(v, cfg['key'], wood=wood, variant=cfg.get('variant', 0), theme=cfg.get('theme'))
    house.ground = cel
    stats = house.run()
    # roof layers (top 6 of the schematic): a retouch may not punch holes in stairs, slabs or trapdoors there
    roof_from = len(v.g) - 6
    roof = {(x, y, z): v.get(x, y, z) for x, y, z in v.cells() if y >= roof_from}
    rkey = cfg['key'] if cfg['key'] in RETOUCH else cfg.get('base', cfg['key'])  # special towns use their own key
    if rkey in RETOUCH:
        RETOUCH[rkey](v)
    for (x, y, z), s0 in roof.items():
        if VF.is_air(v.get(x, y, z)) and not VF.is_air(s0) and VF.nm(s0).endswith(('_stairs', '_slab', 'trapdoor')):
            v.set(x, y, z, s0)
            v.stats['telhado_restaurado'] += 1
    fix_windows(v)
    # dense furnishing of every room (walking paths kept free); rooms are mapped again after the retouch
    house.map_rooms()
    CL.Clutter(house, theme=cfg.get('theme')).run()
    stats['escada_porao'] = ladder_mouths(house, v, cel)
    if not write:
        return stats, v, wood, gy
    for i in range(NCOLORS):
        ck = ckey(cfg['key'], i)
        if i == 0:
            gg = v.g
        else:
            M.SALT = f"{cfg['key']}|c{i}"
            cache = {}
            gg = []
            for sl in v.g:
                nsl = []
                for row in sl:
                    nrow = []
                    for s in row:
                        if s not in cache:
                            cache[s] = M.recolor(s)
                        nrow.append(cache[s])
                    nsl.append(nrow)
                gg.append(nsl)
        for rot in ROTS:
            rg, rl = rotate(gg, v.loot, rot // 90)
            W, L = len(rg[0][0]), len(rg[0])
            cw, cl = W // 16, L // 16
            fr = fronts(rg, cel)
            if not fr and cfg.get('base', cfg['key']) in FRONT_R0:
                fr = [rot_dir(FRONT_R0[cfg.get('base', cfg['key'])], rot // 90)]
            FRONTS.setdefault(ck, {})[str(rot)] = {'dims': [cw, cl], 'fronts': fr}
            names = [[None] * cl for _ in range(cw)]
            for cx in range(cw):
                for cz in range(cl):
                    sub = [[row[cx * 16:(cx + 1) * 16] for row in sl[cz * 16:(cz + 1) * 16]] for sl in rg]
                    sl_loot = {(x - cx * 16, y, z - cz * 16): t for (x, y, z), t in rl.items()
                               if cx * 16 <= x < cx * 16 + 16 and cz * 16 <= z < cz * 16 + 16}
                    names[cx][cz] = write_chunk(ck, rot, cx, cz, sub, sl_loot, cel)
            if cw * cl > 1:
                write_json('multibuildings', f'sunlit:multi_vila_{ck}_r{rot}', {'dimx': cw, 'dimz': cl, 'buildings': names})
    return stats, v, wood, gy


def main():
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--stats' not in sys.argv
    for cfg in CASAS:
        if only and cfg['key'] not in only:
            continue
        stats, v, wood, gy = build(cfg, write)
        print(f"{cfg['key']}: {v.W}x{v.L}x{v.H} chao y{gy} madeira {wood} | " + ', '.join(f'{k} {n}' for k, n in sorted(stats.items())))
    if write and not only:
        write_fronts()
        L.write_theme_files()
        print('frentes: ' + ', '.join(f"{k} {[FRONTS[k][str(r)]['fronts'][:1] for r in ROTS]}" for k in FRONTS))
    print('casas de schematic gravadas' if write else '(so estatisticas)')


if __name__ == '__main__':
    main()
