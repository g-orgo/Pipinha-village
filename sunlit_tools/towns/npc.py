"""Blueprints de NPC (Portable Blueprints) como predios do Lost Cities.

Fonte: config/portable_blueprints/world_injection_worn_blueprints/<tipo>_<set>.bp
(9 profissoes de NPC x 3 variantes = 27 construcoes; sao as mesmas casas que o
carpinteiro vende na loja de predios).

O .bp e um JSON com BlocksData/NotSolidBlocksData (estados) e BlocksNBT (block
entities). O conversor:
- normaliza o estado (so propriedades que o bloco tem) e troca ids que nao
  existem no modpack por equivalentes estaticos (everycomp/diagonal/removidos);
- copycat vira o material que ele imita (o Lost Cities nao carrega o NBT);
- bau/barril/armario vira loot tematico `sunlit:<tema>`;
- o chao em volta vira gramado e a casa entra centralizada na grade de chunks;
- 4 rotacoes (o Lost Cities nao gira predios), mesmo esquema das casas de
  schematic (schematics.py): parte ground/fN/top, 6 fatias por andar;
- grava as frentes em kubejs/startup_scripts/sunlitTownsNpcFronts.js para o
  sunlitTownsLostCities.js virar a casa para a rua;
- registra os predios em TODOS os citystyles com peso maior que as casas
  importadas (o pedido do dono: aparecerem no Lost Cities com rate maior).

Uso: python3 npc.py [--stats]     (antes do polish.py; o polish ainda passa)
"""
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapping as M
import schematics as SC
import vanilla_furni as VF

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit', 'lostcities')
SRC = os.path.join(ROOT, 'config', 'portable_blueprints', 'world_injection_worn_blueprints')
FRONTS_JS = os.path.join(ROOT, 'kubejs', 'startup_scripts', 'sunlitTownsNpcFronts.js')
FLOOR_H = 6
AIR = 'minecraft:air'
GRASS = 'minecraft:grass_block[snowy=false]'

# tipo de NPC -> variantes e tema do loot
NPCS = {
    'carpenter': ('workshop', 'carpinteiro'),
    'blacksmith': ('workshop', 'ferreiro'),
    'shepherd': ('farm', 'pastor'),
    'market': ('grocery', 'mercado'),
    'fisher': ('dock', 'pescador'),
    'banker': ('bank', 'banqueiro'),
    'librarian': ('school', 'bibliotecario'),
    'witch': ('cellar', 'bruxa'),
    'trader': ('luxury', 'comerciante'),
}
SETS = ('basic', 'pineconetown', 'rural')
# codigo curto da variante: o caminho do datapack no Windows nao pode passar de 120 chars
SET_CODE = {'basic': 'b', 'pineconetown': 'p', 'rural': 'r'}
TYPE_CODE = {'carpenter': 'carp', 'blacksmith': 'smith', 'shepherd': 'shep', 'market': 'mkt', 'fisher': 'fish',
             'banker': 'bank', 'librarian': 'libr', 'witch': 'witch', 'trader': 'trad'}
# peso por rotacao: acima das casas importadas (0.03-0.09) e das casas de
# schematic; cada tipo/predio tem 4 rotacoes, entao o peso do predio e 4x.
WEIGHT_BUILDING = 0.08
WEIGHT_MULTI = 0.10
NS = 'sunlit:'

RE_BID = re.compile(r'<bid>(.*?)</bid>')
RE_PROP = re.compile(r'<propertie><name>(.*?)</name><value>(.*?)</value>', re.S)
RE_POS = re.compile(r'x=(-?\d+),y=(-?\d+),z=(-?\d+)$')
RE_MAT = re.compile(r'Material:\{Name:"([^"]+)"')
RE_MATPROPS = re.compile(r'Material:\{Name:"[^"]+"(?:,Properties:\{([^}]*)\})?\}')
RE_BEID = re.compile(r'(?:^|[,{])id:"([^"]+)"')

# containers que o Lost Cities sabe colocar loot (mesmo LOOT_OK do polish.py)
LOOT_OK = re.compile(
    r'^minecraft:(chest|trapped_chest|barrel|dispenser|dropper|hopper|[a-z_]*shulker_box)$|^lootr:|'
    r'^refurbished_furniture:[a-z_]*(drawer|storage_cabinet|crate|fridge|freezer|cooler|storage_jar|mail_box|post_box|'
    r'recycle_bin|stove|microwave|toaster|workbench|cutting_board|frying_pan|plate)$|'
    r'^cfm:[a-z_]*(cabinet|cooler|crate|freezer|fridge|kitchen_drawer|mail_box)$|^another_furniture:[a-z_]*_drawer$|'
    r'^farmersdelight:([a-z_]*_cabinet|wooden_basket)$|^furniture:[a-z_]*(cabinet|coffer|dresser)$|'
    r'^redeco:[a-z_]*(cabinet|drawers|side_table|trash_bin)$|^supplementaries:(sack|safe)$|'
    r'^cluttered:cardboard_box[a-z_]*$|^(meadow|vinery|beachparty):[a-z_]*cabinet$|^vinery:[a-z_]*basket$|'
    r'^farm_and_charm:(crafting_bowl|mincer)$|'
    r'^(bakery|brewery):(cabinet|drawer|wall_cabinet)$|^quark:[a-z_]+_(trapped_)?chest$|^vinery:(storage_pot|dark_cherry_barrel)$|'
    r'^cluttered:kitchen_set_[a-z_]+?_(cabinet|cabinet_glass|cabinet_mini|cabinet_inner_corner|cabinet_open|counter|'
    r'counter_outer_corner_left|counter_outer_corner_right)$')

# blocos que o blueprint usa e o modpack nao tem (versao diferente / mod ausente)
EXPLICIT = {
    'doapi:storage': 'minecraft:barrel',
    'meadow:storage': 'minecraft:barrel',
    'vinery:storage': 'minecraft:barrel',
    'society:salmonberry_crate': 'minecraft:barrel',
    'society:cranberry_crate': 'minecraft:barrel',
    'society:boysenberry_crate': 'minecraft:barrel',
    'society:crystalberry_crate': 'minecraft:barrel',
    'society:oak_supply_crate': 'minecraft:barrel',
    'farmersdelight:basket': 'farmersdelight:wooden_basket',
    'displaydelight:shepherds_pie': 'minecraft:cake',
    'herbalbrews:drink_block_entity': 'herbalbrews:copper_tea_kettle',
    'farm_and_charm:stove_block': 'farm_and_charm:stove',
    'railways:smokestack': 'railways:smokestack_woodburner',
    'minecraft:lava': 'minecraft:magma_block',
    'minecraft:fire': AIR,
    'minecraft:soul_fire': AIR,
}

WOOD_ALIAS = dict(M.WOOD_ALIAS, **{
    'chestnut': 'dark_oak', 'grimwood': 'dark_oak', 'laurel': 'jungle', 'kousa': 'birch', 'aspen': 'birch',
    'morado': 'jungle', 'rosewood': 'cherry', 'yucca': 'acacia', 'holly': 'spruce', 'fir': 'spruce',
    'pineconetown': 'spruce',
})


# ---------------------------------------------------------------- leitura do .bp
def parse_value(val):
    """`<bid>x</bid>null` / `<bid>x</bid><properties><propertie>...` -> estado `id[k=v,...]`."""
    m = RE_BID.match(val)
    if not m:
        return AIR, {}
    bid = m.group(1)
    props = {}
    # 2026-11-09: the .bp keeps some enum values by their Java name (face=FLOOR, type=TOP); the block
    # state wants the lowercase name, otherwise clean_props drops the property and the block falls back
    # to its default (floor flower boxes became wall ones and broke, leaving their supports bare;
    # curtain halves, sofa rows and double chests lost their shape)
    vp = M.valid_props(bid) if M.exists(bid) else {}
    for k, v in RE_PROP.findall(val):
        if v not in vp.get(k, ()):
            v = v.lower()  # also for ids remapped later by repair(): state values are lowercase
        props[k] = v
    return bid, props


def read_bp(name):
    d = json.load(open(os.path.join(SRC, name + '.bp'), encoding='utf-8'))
    W, H, L = d['lunghezzaX'], d['altezza'], d['lunghezzaZ']
    g = [[[AIR] * W for _ in range(L)] for _ in range(H)]
    tags = {}
    for part in ('BlocksData', 'NotSolidBlocksData'):
        for _key, col in d.get(part, {}).items():
            for pos, val in col.items():
                x, y, z = (int(v) for v in RE_POS.match(pos).groups())
                bid, props = parse_value(val)
                g[y][z][x] = M.fmt(bid, props)
    for _key, col in d.get('BlocksNBT', {}).items():
        for pos, val in col.items():
            x, y, z = (int(v) for v in RE_POS.match(pos).groups())
            tags[(x, y, z)] = val
    return d, g, tags


# ---------------------------------------------------------------- resolucao de blocos
def _first(*cands):
    for c in cands:
        if c and M.exists(c):
            return c
    return None


def _wood(name):
    for w in sorted(WOOD_ALIAS, key=len, reverse=True):
        if w in name:
            return w
    return None


def _vanilla(wood):
    return WOOD_ALIAS.get(wood, wood)


def repair_composite(bid):
    """everycomp/diagonalfences/diagonalwalls -> bloco estatico equivalente."""
    ns, rest = bid.split(':', 1)
    bits = rest.split('/')
    mod = bits[0]
    name = bits[-1]
    if ns in ('diagonalfences', 'diagonalwalls'):
        return _first(f'{mod}:{name}', f'minecraft:{name}')
    if len(bits) < 3:
        return None
    feat = bits[0] if len(bits) > 1 else ''
    mod, name = bits[1], bits[-1]
    w = _wood(name)
    vw = _vanilla(w) if w else None
    if name.endswith('_vertical_planks') or re.search(r'vertical_.*_planks$', name):
        return _first(f'{mod}:{w}_planks', f'minecraft:{vw}_planks')
    if name.endswith('_bookshelf'):
        return _first(f'{mod}:{name}', f'{mod}:{w}_bookshelf', f'minecraft:{vw}_bookshelf', 'minecraft:bookshelf')
    if name.endswith(('_post', '_beam', '_support')):
        return _first(f'{mod}:{name}', f'{mod}:{w}_log', f'decorative_blocks:{vw}_beam',
                      f'minecraft:{vw}_log')
    if name.endswith('_leaf_carpet'):
        return _first(f'{mod}:{name}', 'minecraft:moss_carpet')
    if name.endswith('_seat'):
        return _first(f'{mod}:{name}', f'decorative_blocks:{vw}_seat', 'decorative_blocks:oak_seat')
    if name.endswith('_cabinet'):
        return _first(f'{mod}:{name}', f'farmersdelight:{vw}_cabinet', 'farmersdelight:oak_cabinet')
    if name.endswith('_desk'):
        return _first(f'{mod}:{name}', f'refurbished_furniture:{vw}_desk', 'refurbished_furniture:oak_desk')
    if name.endswith('_table'):
        return _first(f'{mod}:{name}', f'refurbished_furniture:{vw}_table', 'refurbished_furniture:oak_table')
    if name.endswith('_drawer'):
        return _first(f'{mod}:{name}', f'refurbished_furniture:{vw}_drawer', 'refurbished_furniture:oak_drawer')
    if name.endswith('_crate'):
        return _first(f'{mod}:{name}', f'{mod}:{w}_crate', f'refurbished_furniture:{vw}_crate')
    if name.endswith('_chair'):
        return _first(f'{mod}:{name}', f'refurbished_furniture:{vw}_chair', f'{mod}:chair')
    if name.endswith('_trellis'):
        return _first(f'{mod}:{name}', f'beautify:{vw}_trellis', 'beautify:acacia_trellis', 'minecraft:ladder')
    if name.endswith('_window_pane') or name.endswith('_pane'):
        return 'minecraft:glass_pane'
    if name.endswith('_door'):
        return _first(f'{mod}:{name}', f'minecraft:{vw}_door')
    return _first(f'{mod}:{name}', f'{mod}:{w}_planks') if w else None


UNRESOLVED = collections.Counter()


def repair(bid, props, tag):
    """estado final (existe no registry, com propriedades validas)."""
    # 2026-11-10: a substitute keeps the source properties (clean_props drops what it does not have); clearing
    # them turned every swapped trellis, ladder, support, seat and gate to facing=north and every beam to axis=y
    if bid in EXPLICIT:
        bid = EXPLICIT[bid]
    if 'copycat' in bid and bid not in ('minecraft:',):
        mat = RE_MAT.search(tag or '')
        if mat and M.exists(mat.group(1)):
            mp = RE_MATPROPS.search(tag or '')
            p = {}
            if mp and mp.group(1):
                for kv in mp.group(1).split(','):
                    if ':' in kv:
                        k, v = kv.split(':', 1)
                        p[k.strip()] = v.strip().strip('"')
            bid, props = mat.group(1), p
        else:
            be = RE_BEID.search(tag or '')
            if be and M.exists(be.group(1)):
                bid, props = be.group(1), {}
    if not M.exists(bid):
        alt = EXPLICIT.get(bid) or repair_composite(bid)
        if alt:
            bid = alt
        elif bid.startswith('everycomp:') is False and '/' in bid.split(':')[-1]:
            alt = repair_composite(bid)
            if alt:
                bid = alt
    if not M.exists(bid):
        UNRESOLVED[bid] += 1
        if bid.endswith('_wall'):
            bid = 'minecraft:stone_brick_wall'
        elif bid.endswith('_fence'):
            bid = 'minecraft:oak_fence'
        elif bid.endswith('_stairs'):
            bid = 'minecraft:oak_stairs'
        elif bid.endswith('_slab'):
            bid = 'minecraft:oak_slab'
        elif 'glass' in bid or bid.endswith('_pane'):
            bid = 'minecraft:glass_pane'
        else:
            bid = 'minecraft:oak_planks'
    if 'terracotta' in bid:
        # regra do dono: terracota nao existe nas cidades, vira concreto com cor sorteada
        return 'minecraft:%s_concrete' % M.vary('mat:concrete', M.HOUSE_COLORS), {}
    return bid, M.clean_props(bid, props)


# ---------------------------------------------------------------- grade -> partes
def fronts_for(g):
    """lados com porta para fora (o principal primeiro).

    Igual ao schematics.fronts, mas aceitando porta alta do dramaticdoors
    (`third=lower` em vez de `half=lower`), porta curta sem `half` e porteira.
    Sem porta nenhuma (barraca aberta) cai no alcapao/portao do terreo.
    """
    H, L, W = len(g), len(g[0]), len(g[0][0])

    def sky(x, y, z):
        if not (0 <= x < W and 0 <= z < L):
            return True
        return all(VF.is_air(g[yy][z][x]) for yy in range(max(0, y), H))

    def score_doors(allow_trapdoor=False):
        score = collections.Counter()
        for y in range(H):
            for z in range(L):
                for x in range(W):
                    s = g[y][z][x]
                    props = M.parse(s)[1]
                    nm = s.split('[')[0].split(':')[-1]
                    if nm.endswith('_trapdoor'):
                        if not allow_trapdoor:
                            continue
                        # alcapao de porta improvisada: a frente e o lado de onde se abre
                        f = props.get('facing')
                        if f in SC.SIDES:
                            score[SC.OPP_SIDE[f]] += 0.5 / (1 + y * 0.35)
                        continue
                    low = props.get('half') == 'lower' or props.get('third') == 'lower' or \
                        (nm.endswith('_door') and 'third' not in props and 'half' not in props)
                    if not (low or nm.endswith('_fence_gate')):
                        continue
                    f = props.get('facing')
                    if f not in SC.SIDES:
                        continue
                    open_ = {}
                    for side in (f, SC.OPP_SIDE[f]):
                        dx, dz = SC.SIDES[side]
                        n = 0
                        for k in range(1, 7):
                            nx, nz = x + dx * k, z + dz * k
                            if not (0 <= nx < W and 0 <= nz < L):
                                n += 7 - k
                                break
                            n += 1 if sky(nx, y + 2, nz) else 0
                        open_[side] = n
                    if open_[f] == open_[SC.OPP_SIDE[f]]:
                        continue
                    out = max(open_, key=open_.get)
                    score[out] += 1.0 / (1 + y * 0.35)
        return score

    for allow in (False, True):
        score = score_doors(allow)
        if score:
            top = max(score.values())
            return [s for s, v in score.most_common() if v >= 0.6 * top]
    return []


LOOSE_SUPPORTS = collections.Counter()


RE_HANGING = re.compile(r'hanging=true|:chain\b|hanging_pot|hanging_sign')


def drop_loose_supports(g, name=''):
    """2026-11-08 (owner request): a Decorative Blocks support with nothing on top is a bracket stuck on
    the wall holding nothing; in game it reads as a shelf (market basic: rows above the windows).
    2026-11-09 (owner request): the first version only dropped the ones facing open sky, so brackets
    under the eaves stayed (blacksmith basic: three of them on the gable). Now any upright support
    (`up=true`, the beam on top) with air above goes, unless something hangs from it; supports that
    hold a roof, beam, planter or anything else stay. Upside-down ones (`up=false`) are left alone."""
    H = len(g)
    for y in reversed(range(H)):  # top-down: a stack of supports holding nothing goes whole
        for z in range(len(g[0])):
            for x in range(len(g[0][0])):
                s = g[y][z][x]
                if not s.split('[')[0].endswith('_support'):
                    continue
                if M.parse(s)[1].get('up') == 'false':
                    continue
                if y + 1 < H and not VF.is_air(g[y + 1][z][x]):
                    continue
                if y > 0 and RE_HANGING.search(g[y - 1][z][x]):
                    continue
                g[y][z][x] = AIR
                LOOSE_SUPPORTS[name] += 1


# natural ground a blueprint may carry in its first layer (paths, garden beds)
TERRAIN = {'grass_block', 'dirt', 'coarse_dirt', 'rooted_dirt', 'rocky_dirt', 'dirt_path', 'podzol', 'mycelium',
           'moss_block', 'mud', 'gravel', 'sand', 'farmland'}
LIFTED = {}


def is_terrain(s):
    return s.split('[')[0].split(':')[-1].split('/')[-1] in TERRAIN


LOW_PLANT = re.compile(r'(flower|tulip|daisy|poppy|dandelion|orchid|allium|bluet|cornflower|lily|clover|campion|foxglove|'
                       r'bluebells|lupine|mimosa|nightshade|lions_tail|sprouts|(^|_)grass$|fern$|_crop$|crops$|carrots|potatoes|'
                       r'beetroots|wheat|eggplants|cabbages|onions|sapling$)')


def is_low_plant(s):
    return bool(LOW_PLANT.search(s.split('[')[0].split(':')[-1])) and not re.search(r'large_|tall_|pot|box|crate|sack|bag|basket', s)


def lift_onto_ground(g, name=''):
    """2026-11-09 (owner request): the blueprints were saved from the first block ABOVE the ground, so their
    layer 0 holds entry steps, benches, campfires, crates, carpets, flowers and rails. Putting that layer at
    lawn height buried all of it (a ring of snowy stairs half in the grass read as toilets in the street).
    Unless layer 0 is mostly natural ground (witch pineconetown carries its own lawn), the blueprint goes on
    top of a new lawn layer; a loose ground block of the old layer 0 (path, garden bed, nothing on it)
    sinks into the lawn instead of standing one block proud."""
    L, W = len(g[0]), len(g[0][0])
    first = [s for row in g[0] for s in row if not VF.is_air(s)]
    if first and sum(map(is_terrain, first)) * 2 >= len(first):
        return g
    lawn = [[GRASS] * W for _ in range(L)]
    sunk = 0
    for z in range(L):
        for x in range(W):
            s = g[0][z][x]
            if not is_terrain(s):
                continue
            if len(g) < 2 or VF.is_air(g[1][z][x]):
                lawn[z][x] = s
                g[0][z][x] = AIR
                sunk += 1
            elif is_low_plant(g[1][z][x]) and (len(g) < 3 or VF.is_air(g[2][z][x])):
                # 2026-11-10: a bed with a flower or crop on it sinks with its plant (it stood one block proud)
                lawn[z][x] = s
                g[0][z][x] = g[1][z][x]
                g[1][z][x] = AIR
                sunk += 1
    LIFTED[name] = sunk
    return [lawn] + g


def build_grid(bid_name):
    d, g, tags = read_bp(bid_name)
    H, L, W = len(g), len(g[0]), len(g[0][0])
    for y in range(H):
        for z in range(L):
            for x in range(W):
                bid, props = M.parse(g[y][z][x])
                tag = tags.get((x, y, z))
                bid, props = repair(bid, props, tag)
                g[y][z][x] = M.fmt(bid, props)
    g = lift_onto_ground(g, bid_name)
    H = len(g)
    # chao em volta da casa vira gramado (o .bp so tem os blocos construidos)
    for z in range(L):
        for x in range(W):
            if M.parse(g[0][z][x])[0] == AIR:
                g[0][z][x] = GRASS
    # porta que virou porta vanilla sem `half` (blueprint usava dramaticdoors curta):
    # completa a metade de cima para a porta nao ficar so no chao
    for z in range(L):
        for x in range(W):
            for y in range(H - 1):
                s = g[y][z][x]
                bid, props = M.parse(s)
                if not bid.split(':')[-1].endswith('_door') or 'half' in props or 'third' in props:
                    continue
                if not bid.startswith('minecraft:') or not M.exists(bid):
                    continue
                p = dict(props, half='lower')
                g[y][z][x] = M.fmt(bid, M.clean_props(bid, p))
                if VF.is_air(g[y + 1][z][x]):
                    g[y + 1][z][x] = M.fmt(bid, M.clean_props(bid, dict(props, half='upper')))
    drop_loose_supports(g, bid_name)
    return g


def center(g):
    """centraliza a construcao na grade de chunks (16x16 por chunk)."""
    H, L, W = len(g), len(g[0]), len(g[0][0])
    CW = (W + 15) // 16 * 16
    CL = (L + 15) // 16 * 16
    x0, z0 = (CW - W) // 2, (CL - L) // 2
    out = [[[AIR] * CW for _ in range(CL)] for _ in range(H)]
    for y in range(H):
        for z in range(L):
            for x in range(W):
                out[y][z + z0][x + x0] = g[y][z][x]
    for z in range(CL):
        for x in range(CW):
            if M.parse(out[0][z][x])[0] == AIR:
                out[0][z][x] = GRASS
    return out


def entry(state, theme):
    if LOOT_OK.search(state.split('[')[0]):
        return {'block': state, 'loot': f'sunlit:{theme}'}
    return {'block': state}


def write_chunk(key, rot, cx, cz, g, theme):
    H = len(g)
    nparts = max(2, (H + FLOOR_H - 1) // FLOOR_H + (1 if H % FLOOR_H == 0 else 0))
    name = SC.bname(key, rot, cx, cz)
    parts = []

    def emit(tag, ys):
        pal, by = {'G': {'block': SC.FILLER}}, {}
        chars = iter(SC.POOL)
        slices = []
        for y in ys:
            sl = []
            for z in range(16):
                row = []
                for x in range(16):
                    s = g[y][z][x] if 0 <= y < len(g) else (SC.FILLER if y < 0 else AIR)
                    if s in (AIR, ''):
                        row.append(' ')
                        continue
                    e = entry(s, theme)
                    k = json.dumps(e, sort_keys=True)
                    if k not in by:
                        c = next(chars)
                        by[k] = c
                        pal[c] = e
                    row.append(by[k])
                sl.append(''.join(row))
            slices.append(sl)
        prl = f'{name}_{tag}'
        SC.write_json('palettes', prl + '_palette', {'palette': [dict(char=c, **e) for c, e in pal.items()]})
        SC.write_json('parts', prl, {'xsize': 16, 'zsize': 16, 'refpalette': prl + '_palette', 'slices': slices})
        return prl

    for k in range(nparts):
        lo = k * FLOOR_H
        ys = range(lo, min(H, lo + FLOOR_H)) if k < nparts - 1 else range(lo, max(H, lo + 1))
        tag = 'ground' if k == 0 else ('top' if k == nparts - 1 else f'f{k}')
        prl = emit(tag, ys)
        pe = {'top': tag == 'top', 'cellar': False, 'ground': tag == 'ground', 'part': prl}
        if tag.startswith('f'):
            pe['floor'] = k
        parts.append(pe)
    SC.write_json('buildings', name, {'filler': 'G', 'rubber': ' ', 'allowDoors': False, 'allowFillers': True,
                                      'overrideFloors': True, 'minfloors': nparts - 1, 'maxfloors': nparts - 1,
                                      'mincellars': 0, 'maxcellars': 0, 'parts': parts})
    return name


def build(name, write=True):
    npc, s = name.split('_', 1)
    theme = NPCS[npc][0]
    key = 'npc_' + TYPE_CODE[npc] + '_' + SET_CODE[s]
    M.SALT = key  # cor sorteada por casa (terracota -> concreto), igual as casas de schematic
    g = center(build_grid(name))
    H = len(g)
    nparts = max(2, (H + FLOOR_H - 1) // FLOOR_H + (1 if H % FLOOR_H == 0 else 0))
    info = {'key': key, 'name': name, 'theme': theme, 'size': (len(g[0][0]), nparts - 1, len(g[0])),
            'floors': nparts - 1, 'multis': []}
    for rot in SC.ROTS:
        rg, _ = SC.rotate(g, {}, rot // 90)
        W, L = len(rg[0][0]), len(rg[0])
        cw, cl = W // 16, L // 16
        info.setdefault('fronts', {})[str(rot)] = {'dims': [cw, cl], 'fronts': fronts_for(rg)}
        names = [[None] * cl for _ in range(cw)]
        if not write:
            continue
        for cx in range(cw):
            for cz in range(cl):
                sub = [[row[cx * 16:(cx + 1) * 16] for row in sl[cz * 16:(cz + 1) * 16]] for sl in rg]
                names[cx][cz] = write_chunk(key, rot, cx, cz, sub, theme)
        if cw * cl > 1:
            multi = f'sunlit:multi_vila_{key}_r{rot}'
            SC.write_json('multibuildings', multi, {'dimx': cw, 'dimz': cl, 'buildings': names})
            info['multis'].append((multi, cw * cl))
    return info


# ---------------------------------------------------------------- citystyles
def update_styles(buildings, multis):
    for f in sorted(glob.glob(os.path.join(DATA, 'citystyles', '*.json'))):
        cs = json.load(open(f, encoding='utf-8'))
        sel = cs.setdefault('selectors', {})
        for key, entries in (('buildings', buildings), ('multibuildings', multis)):
            lst = [e for e in sel.get(key, []) if not re.search(r'sunlit:(multi_)?vila_npc_', e['value'])]
            lst += entries
            sel[key] = lst
        json.dump(cs, open(f, 'w', encoding='utf-8'))


def main():
    write = '--stats' not in sys.argv
    infos = []
    for npc in NPCS:
        for s in SETS:
            infos.append(build(f'{npc}_{s}', write))
    fronts = {i['key']: i['fronts'] for i in infos}
    singles, multis = [], []
    for i in infos:
        if i['multis']:
            for m, _ in i['multis']:
                multis.append({'factor': WEIGHT_MULTI, 'value': m})
        else:
            for rot in SC.ROTS:
                singles.append({'factor': WEIGHT_BUILDING,
                                'value': f'sunlit:vila_{i["key"]}/r{rot}c00'})
    for i in infos:
        print(f"{i['name']}: {i['size'][0]}x{i['size'][2]} h{i['floors']} andares "
              f"{'multi' if i['multis'] else '1 chunk'} tema {i['theme']} frentes {i['fronts']}")
    if write:
        with open(FRONTS_JS, 'w', encoding='utf-8') as f:
            f.write('// GERADO por sunlit_tools/towns/npc.py (nao editar a mao).\n'
                    '// Blueprints de NPC do Portable Blueprints no Lost Cities: por rotacao, tamanho em chunks\n'
                    '// [x, z] e lados com porta para fora (o principal primeiro).\n')
            f.write('global.sunlitNpcFronts = ' + json.dumps(fronts, sort_keys=True) + ';\n')
        update_styles(singles, multis)
        print(f'predios de NPC gravados: {len(singles)} entradas de 1 chunk, {len(multis)} multibuildings')
    if LIFTED:
        print('casa sobre o gramado (camada 0 era a primeira acima do chao), chao solto afundado: '
              + ', '.join(f'{k} {v}' for k, v in sorted(LIFTED.items())))
    if LOOSE_SUPPORTS:
        print('suporte solto (sem nada em cima) removido: ' + ', '.join(f'{k} {v}' for k, v in sorted(LOOSE_SUPPORTS.items())))
    if UNRESOLVED:
        print('BLOCO SEM EQUIVALENTE (virou madeira de carvalho):')
        for k, v in UNRESOLVED.most_common():
            print(' ', v, k)
    print('npc.py: ok' if write else '(estatisticas)')


if __name__ == '__main__':
    main()
