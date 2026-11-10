"""Gera o datapack moonlight-global-datapacks/sunlit_towns a partir do DCTweaks original.

Uso: python3 convert.py [caminho/DCTweaks.jar]
Rode build_registry.py antes se mods foram adicionados/removidos.
"""
import json, os, re, sys, shutil, zipfile, copy, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapping as M
import loot as L
import parks as P
import enrich as E
import mix as MIX
import vila as V
import schematics as SCH

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
JAR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(ROOT), 'DeceasedCraft - Urban Zombie Apocalypse', 'mods', 'DCTweaks_5.10.14.jar')
OUT = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns')
DC = 'data/deceasedcraft/lostcities/'

# conteudo apocaliptico ou sem sentido numa vila viva
EXCLUDE = re.compile(r'broken|damaged|deadzone|planecrash|hideout|gunstore|residentialsurvivor|abyss|wasteland|'
                     r'highway_bridge_crash|highway_open_car|ambulance|roadblock|fountain_highrise_office_trash|'
                     r'residential_body|_bus$|dummy')

z = zipfile.ZipFile(JAR)
NAMES = set(z.namelist())


# fewer parks overall (2026-10-04: too many repeated plazas); scales every citystyle parkchance
PARK_SCALE = 0.6

def dc_json(kind, name):
    """kind=parts|palettes|buildings..., name sem namespace"""
    p = f'{DC}{kind}/{name}.json'
    return json.loads(z.read(p)) if p in NAMES else None


def strip(rl):
    return rl.split(':', 1)[1] if ':' in rl else rl


def write(path, obj):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        json.dump(obj, f, separators=(',', ':'))


stats = {'air': {}, 'fallback': {}, 'mapped': {}}
counts = collections.Counter()

LOOTABLE = re.compile(r'^(minecraft:(chest|trapped_chest|barrel)|lootr:lootr_(chest|barrel|trapped_chest)|'
                      r'refurbished_furniture:.*(drawer|cabinet|crate|fridge|freezer|cooler|storage_jar|kitchen_storage_cabinet)|'
                      r'farmersdelight:.*_cabinet)$')
# containers do DC que perderam a funcao de bau ganham um equivalente que guarda loot
LOOT_FALLBACK = [(r'fridge|freezer|cooler|ice', 'refurbished_furniture:light_fridge'),
                 (r'safe|locker|medical|cabinet', 'refurbished_furniture:oak_storage_cabinet'),
                 (r'kitchen', 'refurbished_furniture:oak_kitchen_drawer'),
                 (r'drawer', 'refurbished_furniture:oak_drawer'),
                 (r'', 'refurbished_furniture:oak_crate')]
used_themes = set()
COMMON = {}


def sanitize_tag(block_id, tag):
    if not isinstance(tag, dict):
        return None
    t = copy.deepcopy(tag)
    if 'Command' in t or 'posInMB' in t:
        return None
    if 'Items' in t and isinstance(t['Items'], list):
        t['Items'] = [it for it in t['Items'] if isinstance(it, dict) and M.item_ok(it.get('id', ''))]
    return t


# blocos que precisam de apoio: sem ele flutuam no ar (ex. abajur de mesa no lugar de
# luz de parede, arandela sem parede). So remove quando o apoio existe na mesma parte
# e e ar/agua: slice 0 se apoia no terreno ou na parte de baixo, borda se apoia na
# parte vizinha -> nesses casos mantem.
NEEDS_BELOW = re.compile(r'_lamp\[|lamp_[a-z_]+\[|flower_pot|potted_|_carpet\[|minecraft:torch\[|_candle\[|_sign\['
                         r'|poppy|dandelion|cornflower|allium|daisy|tulip|bluet|_sapling|dead_bush|grass\[|fern\[|'
                         r'lily_pad|_crop\[|wheat\[|carrots\[|potatoes\[|beetroots\[|pitcher|cactus\[|sugar_cane')
NEEDS_ABOVE = re.compile(r'ceiling_light|ceiling_fan|hanging=true|minecraft:chain\[|chandelier|pendant')
NEEDS_WALL = re.compile(r'wall_torch|sconce_wall|lamp_wall|minecraft:ladder\[|_wall_sign|_wall_banner|wall_hanging|'
                        r'faucet|shower|mirror|sconce\[')


SIMPLY_FACING = re.compile(r'simplylight:[a-z_]+\[(?:.*,)?facing=(north|south|east|west|up|down)')
SUPPORT_OFFSET = {'down': (1, 0, 0), 'up': (-1, 0, 0), 'north': (0, 1, 0), 'south': (0, -1, 0),
                  'west': (0, 0, 1), 'east': (0, 0, -1)}  # (dy, dz, dx) ate o bloco de apoio


def has_support(b):
    return b is not None and not b.startswith('minecraft:air') and 'water' not in b


def defloat(part, ps, common):
    sl = [[list(r) for r in s] for s in part['slices']]
    H, Z, X = len(sl), part['zsize'], part['xsize']
    B = lambda y, z, x: E.block_of(ps, common, sl[y][z][x]) if 0 <= y < H and 0 <= z < Z and 0 <= x < X else None
    removed = 0
    for y in range(H):
        for z in range(Z):
            for x in range(X):
                b = B(y, z, x)
                if not b or b.startswith('minecraft:air'):
                    continue
                if 'redstone_lamp' in b or 'glowstone' in b or 'sea_lantern' in b:
                    continue  # cubos solidos de luz: nunca flutuam
                m = SIMPLY_FACING.match(b)
                if m:
                    # simplylight: facing aponta para longe do apoio (facing=down = preso no teto)
                    dy, dz, dx = SUPPORT_OFFSET[m.group(1)]
                    n = B(y + dy, z + dz, x + dx)
                    if n is not None and not has_support(n):
                        sl[y][z][x] = ' '
                        removed += 1
                    continue
                if NEEDS_WALL.search(b):
                    near = [B(y, z + dz, x + dx) for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0))
                            if 0 <= x + dx < X and 0 <= z + dz < Z]
                    if near and not any(has_support(n) for n in near):
                        sl[y][z][x] = ' '
                        removed += 1
                elif NEEDS_ABOVE.search(b):
                    if y + 1 < H and not has_support(B(y + 1, z, x)):
                        sl[y][z][x] = ' '
                        removed += 1
                elif NEEDS_BELOW.search(b):
                    if y > 0 and not has_support(B(y - 1, z, x)):
                        sl[y][z][x] = ' '
                        removed += 1
    if removed:
        part['slices'] = [[''.join(r) for r in s] for s in sl]
    return removed


def convert_palette(name, bname):
    M.SALT = bname
    src = dc_json('palettes', name)
    if src is None:
        return False
    out = []
    for e in src.get('palette', []):
        ne = {'char': e['char']}
        orig = e.get('block')
        if 'mob' in e:
            ne['block'] = 'minecraft:air'
            out.append(ne); continue
        if 'block' in e:
            st = M.convert_state(e['block'], stats)
            st = M.swap_material(st)  # cor/madeira do predio (2026-10-06: casas iguais demais)
            ne['block'] = st or 'minecraft:air'
        elif 'blocks' in e:
            bl = []
            for b in e['blocks']:
                st = M.convert_state(b['block'], stats)
                bl.append({'random': b.get('random', 1), 'block': M.swap_material(st) or 'minecraft:air'})
            ne['blocks'] = bl
        else:
            # variant / frompalette: mantem a referencia
            for k in ('variant', 'frompalette'):
                if k in e: ne[k] = e[k]
        if 'torch' in e:
            ne['torch'] = e['torch']
        new_id = ne.get('block', '').split('[')[0]
        # bloco inalterado: preserva NBT (camas, quadros, displays) sem itens invalidos
        if 'tag' in e and orig and orig.split('[')[0] == new_id:
            t = sanitize_tag(new_id, e['tag'])
            if t: ne['tag'] = t
        # loot: todo container ganha tema pelo contexto (predio + tipo de movel)
        had_loot = 'loot' in e
        if new_id == 'minecraft:air':
            had_loot = False
        if new_id and new_id != 'minecraft:air' and (had_loot or LOOTABLE.match(new_id)):
            if not LOOTABLE.match(new_id):
                src_name = (orig or '').split('[')[0]
                for rx, fb in LOOT_FALLBACK:
                    if re.search(rx, src_name):
                        props = M.parse(ne['block'])[1]
                        ne['block'] = M.fmt(fb, M.clean_props(fb, props)); new_id = fb; ne.pop('tag', None)
                        break
            theme = L.theme_for(bname, new_id, name)
            used_themes.add(theme)
            ne['loot'] = f'sunlit:{theme}'
            counts['loot'] += 1
        # mescla de mods bloco a bloco (fogao, panela, tabua, caixotes, cestos, colheitas)
        if 'block' in ne and 'loot' not in ne and 'tag' not in ne:
            mixed = MIX.blocks_for(ne['block'])
            if mixed:
                del ne['block']
                ne['blocks'] = mixed
                counts['mix'] += 1
        out.append(ne)
    PALS[name] = E.PaletteState(out)
    counts['palettes'] += 1
    return True


HEDGE_LIGHT = re.compile(r'lamp|light|bulb|lantern|sconce|torch|end_rod|candle')
HEDGE_POST = re.compile(r'_wall\b|_wall\[|fence|chain|_post\b|_post\[|end_rod')
MAX_HEDGE = 4  # cerca-viva nunca passa de 4 blocos de altura


def hedge_wood(bid):
    """madeira da hedge ('dark_oak', 'azalea'...); cfm:flowering_azalea vira azalea."""
    w = bid.split(':')[1][:-len('_hedge')]
    return 'azalea' if w == 'flowering_azalea' else w


def tidy_hedges(part, ps, common, name):
    """Cercas-vivas do DC usadas como parede verde/poste viravam colunas sem fim
    (cada andar de 6 fatias emenda na hedge do andar de baixo), copas soltas no ar
    e postes com corpo de hedge. Por coluna (z, x):
    - hedge que comeca na fatia 0 de um andar superior e continuacao do andar de
      baixo: vira ar (ou musgo, se for o piso);
    - hedge sem nada embaixo (copa de arvore DC) vira folha persistente da mesma madeira;
    - qualquer hedge com mais de MAX_HEDGE de altura e cortada no topo;
    - luminaria/poste em cima da hedge: luz e pecas de poste viram ar; pilar
      (muro/cerca) que sobe ate o teto substitui a hedge por ele mesmo."""
    sl = [[list(r) for r in s] for s in part['slices']]
    H, Z, X = len(sl), part['zsize'], part['xsize']
    if not H:
        return collections.Counter()
    B = lambda y, z, x: E.block_of(ps, common, sl[y][z][x]) if 0 <= y < H and 0 <= z < Z and 0 <= x < X else None
    is_h = lambda b: bool(b) and '_hedge' in b
    part_name = name.split('/')[-1]
    upper = 'floor' in part_name or part_name.endswith(('_top', '_top_90', '_top_180', '_top_270'))
    c = collections.Counter()

    def put(y, z, x, state):
        ch = ' ' if state is None else ps.char_for(state, None)
        if ch:
            sl[y][z][x] = ch
            return True
        return False

    for z in range(Z):
        for x in range(X):
            y = 0
            while y < H:
                if not is_h(B(y, z, x)):
                    y += 1
                    continue
                s = y
                while y < H and is_h(B(y, z, x)):
                    y += 1
                e = y - 1  # run s..e
                bid = B(s, z, x).split('[')[0]
                if s == 0 and upper:
                    floor = sum(1 for dx, dz in ((0, -1), (0, 1), (-1, 0), (1, 0))
                                if E.solid(B(0, z + dz, x + dx)) and not is_h(B(0, z + dz, x + dx)))
                    for yy in range(s, e + 1):
                        put(yy, z, x, 'minecraft:moss_block' if yy == 0 and floor >= 2 else None)
                    c['hedge_cut'] += e - s + 1
                    continue
                if s > 0 and E.is_air(B(s - 1, z, x)):
                    lid = f'minecraft:{hedge_wood(bid)}_leaves'
                    if M.exists(lid):
                        for yy in range(s, e + 1):
                            put(yy, z, x, M.fmt(lid, M.clean_props(lid, {'persistent': 'true', 'distance': '7', 'waterlogged': 'false'})))
                        c['hedge_leaf'] += e - s + 1
                        continue
                if e - s + 1 > MAX_HEDGE:
                    for yy in range(s + MAX_HEDGE, e + 1):
                        put(yy, z, x, None)
                    c['hedge_cap'] += e - s + 1 - MAX_HEDGE
                    e = s + MAX_HEDGE - 1
                above = B(e + 1, z, x)
                if above and not E.is_air(above):
                    a_id = above.split('[')[0].split(':')[1]
                    if HEDGE_LIGHT.search(a_id):
                        yy = e + 1
                        while yy < H:
                            b2 = B(yy, z, x)
                            if not b2 or E.is_air(b2):
                                break
                            i2 = b2.split('[')[0].split(':')[1]
                            if not (HEDGE_LIGHT.search(i2) or HEDGE_POST.search(i2)):
                                break
                            put(yy, z, x, None)
                            yy += 1
                        c['hedge_post'] += 1
                    elif HEDGE_POST.search(a_id) and B(e + 2, z, x) and B(e + 2, z, x).split('[')[0] == above.split('[')[0]:
                        for yy in range(s, e + 1):
                            put(yy, z, x, above)
                        c['hedge_pillar'] += 1
    part['slices'] = [[''.join(r) for r in s] for s in sl]
    return c


def fix_hedges(part, ps, common):
    """Religa as hedges: o DC vinha com os 4 lados false e a cerca-viva nascia em
    cubos isolados. Toda hedge vira Refurbished (a do cfm so conecta com cfm e a do
    Refurbished so com Refurbished, independente da madeira). Lado true quando o
    vizinho no mesmo slice e hedge ou folha (mesma regra do HedgeBlock do Refurbished)."""
    sl = [[list(r) for r in s] for s in part['slices']]
    H, Z, X = len(sl), part['zsize'], part['xsize']
    def B(y, z, x):
        if not (0 <= y < H and 0 <= z < Z and 0 <= x < X):
            return None
        return E.block_of(ps, common, sl[y][z][x])
    def links(nb):
        return bool(nb) and ('_hedge' in nb or '_leaves' in nb.split('[')[0])
    fixed = 0
    for y in range(H):
        for z in range(Z):
            for x in range(X):
                b = B(y, z, x)
                if not b or '_hedge' not in b:
                    continue
                bid = 'refurbished_furniture:' + hedge_wood(b.split('[')[0]) + '_hedge'
                if not M.exists(bid):
                    bid = 'refurbished_furniture:oak_hedge'
                want = {'north': 'true' if links(B(y, z - 1, x)) else 'false',
                        'south': 'true' if links(B(y, z + 1, x)) else 'false',
                        'west': 'true' if links(B(y, z, x - 1)) else 'false',
                        'east': 'true' if links(B(y, z, x + 1)) else 'false'}
                state = M.fmt(bid, M.clean_props(bid, want))
                if state == b:
                    continue
                entry = ps.by_char.get(sl[y][z][x]) or {}
                if 'blocks' in entry:
                    continue  # lista random: nao da p/ fatiar por posicao, mantem
                ch = ps.char_for(state, entry.get('loot'))
                if ch:
                    sl[y][z][x] = ch
                    fixed += 1
    if fixed:
        part['slices'] = [[''.join(r) for r in s] for s in sl]
    return fixed


PALS = {}


done_parts, done_pal, done_build = set(), set(), set()


def do_part(rl, bname):
    name = strip(rl)
    if name in done_parts:
        return
    done_parts.add(name)
    p = dc_json('parts', name)
    if p is None:
        if not rl.startswith('deceasedcraft:'):
            return  # parte do proprio Lost Cities
        print('  parte ausente', rl); return
    if p.get('refpalette'):
        pn = strip(p['refpalette'])
        if pn not in done_pal:
            done_pal.add(pn)
            convert_palette(pn, bname)
        # interiores de predios ganham decoracao nos cantos (ruas, parques e telhados nao)
        if pn in PALS and re.match(r'(building|multi|scattered)_', bname) and not name.endswith(('_top', '_top_90', '_top_180', '_top_270')):
            theme = L.building_theme(bname) or 'home'
            counts['decor'] += E.enrich(p, PALS[pn], COMMON, theme, name, LOOTABLE)
        if pn in PALS:
            # apoio faltando vira ar em vez de flutuar (abajur sem mesa, arandela sem parede...)
            counts['defloat'] += defloat(p, PALS[pn], COMMON)
            # colunas/copas/postes de hedge, depois religa os lados (cubos isolados)
            counts.update(tidy_hedges(p, PALS[pn], COMMON, name))
            counts['hedges'] += fix_hedges(p, PALS[pn], COMMON)
    write(f'data/deceasedcraft/lostcities/parts/{name}.json', p)
    counts['parts'] += 1


def do_building(rl):
    name = strip(rl)
    if name in done_build:
        return
    done_build.add(name)
    b = dc_json('buildings', name)
    if b is None:
        print('  predio ausente', rl); return
    bname = name.split('/')[0]
    for pr in b.get('parts', []):
        do_part(pr['part'], bname)
    for pr in b.get('parts2', []):
        do_part(pr['part'], bname)
    # Cabanas DC (multi_cabin*, scattered_cabin_*, campsite, foodtruck, farmhouse)
    # declaram partes so para floor 0..2 mas forcam min/maxfloors=3: o slot 3 nao
    # casa com nada e o chunk quebra ("Misconfiguration! No part condition matches").
    # Trava no maior floor declarado quando todas as partes usam floor explicito.
    # Alem disso essas cabanas nao tem nenhuma parte top:true (a peca *_top vem
    # com top:false): sem ela o andar de cima nunca casa (floor==floors exige
    # top:true). Marca a peca *_top do maior andar como telhado.
    parts = b.get('parts', [])
    if parts and all('floor' in p for p in parts) and b.get('mincellars', 0) == 0:
        cap = max(p['floor'] for p in parts)
        if b.get('maxfloors', 0) > cap:
            b['maxfloors'] = cap
        if b.get('minfloors', 0) > cap:
            b['minfloors'] = cap
        if not any(p.get('top') for p in parts):
            cands = [p for p in parts if p['floor'] == cap]
            roofs = [p for p in cands if 'top' in p['part'].split('/')[-1] or 'roof' in p['part'].split('/')[-1]]
            for p in roofs or cands:
                p['top'] = True
            counts['retop'] += len(roofs or cands)
    write(f'data/deceasedcraft/lostcities/buildings/{name}.json', b)
    counts['buildings'] += 1


def do_multi(rl):
    if rl.startswith('sunlit:'):
        return  # conteudo proprio (schematics.py) e gravado depois
    name = strip(rl)
    mb = dc_json('multibuildings', name)
    for row in mb['buildings']:
        for b in row:
            do_building(b)
    write(f'data/deceasedcraft/lostcities/multibuildings/{name}.json', mb)
    counts['multibuildings'] += 1


def do_scattered(rl):
    name = strip(rl)
    s = dc_json('scattered', name)
    if 'multibuilding' in s:
        do_multi(s['multibuilding'])
    for b in s.get('buildings', []):
        do_building(b)
    write(f'data/deceasedcraft/lostcities/scattered/{name}.json', s)


def keep(sel):
    return [x for x in sel if not EXCLUDE.search(x['value'])]


def build_citystyle(src_name, new_name, buildings=None, multis=None, extra_buildings=(), extra_multis=(),
                    parkchance=None, buildingchance=None, park_weights=None, fountains=None, maxfloors=None):
    cs = json.loads(z.read(f'{DC}citystyles/{src_name}.json'))
    sel = cs['selectors']
    sel['buildings'] = keep(sel.get('buildings', [])) if buildings is None else buildings
    sel['buildings'] += list(extra_buildings)
    sel['multibuildings'] = keep(sel.get('multibuildings', [])) if multis is None else multis
    sel['multibuildings'] += list(extra_multis)
    sel['fronts'] = keep(sel.get('fronts', [])) or [{'factor': 1.0, 'value': 'deceasedcraft:fronts/front_suburb_residential_1'}]
    sel['stairs'] = keep(sel.get('stairs', []))
    # pracas, hortas, pomares e cercados ganham peso alto; parques DC continuam
    dc_parks = [p for p in keep(sel.get('parks', []))]
    sel['parks'] = dc_parks + [{'factor': w, 'value': f'sunlit:parks/{n}'} for n, w in (park_weights or P.PARK_WEIGHTS).items()]
    sel['fountains'] = [{'factor': w, 'value': f'sunlit:fountains/{n}'} for n, w in (fountains or P.FOUNTAIN_WEIGHTS).items()]
    if parkchance is not None:
        # 2026-10-04: fewer parks overall (the user saw too many repeated plazas)
        cs.setdefault('parkblocks', {})['parkchance'] = round(parkchance * PARK_SCALE, 3)
    if buildingchance is not None or maxfloors is not None:
        bs = cs.setdefault('buildingsettings', {})
        if buildingchance is not None: bs['buildingchance'] = buildingchance
        if maxfloors is not None: bs['maxfloors'] = maxfloors
    sb = cs.setdefault('streetblocks', {})
    sb['fountainchance'] = 0.35
    # o LC 7.5.5 usa largeparts (vias principais) e tertiaryparts; sem isso cai nas ruas padrao do LC,
    # cuja paleta nao existe nos estilos DC ("Could not find entry 'b'")
    sp = sb.get('parts', {})
    for k in ('connector', 'stair'):
        sp.setdefault(k, sp['straight'])
    sb['largeparts'] = dict(sp)
    sb['tertiaryparts'] = dict(sp)
    for b in sel['buildings']:
        do_building(b['value'])
    for m in sel['multibuildings']:
        do_multi(m['value'])
    for k in ('fronts', 'stairs', 'bridges', 'largebridges', 'raildungeons'):
        for x in sel.get(k, []):
            do_part(x['value'], 'street')
    for k, v in cs.get('streetblocks', {}).get('parts', {}).items():
        for x in v:
            do_part(x, 'street')
    for x in dc_parks:
        do_part(x['value'], 'park')
    write(f'data/sunlit/lostcities/citystyles/{new_name}.json', cs)
    return cs


def B(name, f):
    """predio com as 4 rotacoes (o DC gera _90/_180/_270)"""
    out = []
    for suf in ('', '_90', '_180', '_270'):
        rl = f'deceasedcraft:{name}/{name}{suf}'
        if f'{DC}buildings/{name}/{name}{suf}.json' in NAMES:
            out.append({'factor': f, 'value': rl})
    return out


def MB(name, f):
    return [{'factor': f, 'value': f'deceasedcraft:{name}'}]


# Conteudo cozy proprio (gerado por houses.py / cozy_expansion.py DEPOIS do
# convert.py, pois o convert apaga e recria o OUT inteiro). Declarado aqui
# para que os citystyles/scattered regenerados ja incluam as referencias.
def SB(name, f):
    return [{'factor': f, 'value': f'sunlit:{name}'}]


# fatia do conteudo proprio (schematics + construcoes proprias) frente as casas importadas: com peso
# cheio elas ocupavam 75-95% dos bairros e as casas importadas quase sumiam (2026-10-03 v7)
OWN_SHARE = 0.3


# 2026-10-16 variedade: vermelha/fada dominavam as casas de 1 chunk; cada familia tem um multiplicador
# sobre o peso base de schematics.py (sem editar schematics.py). Familias sem entrada valem 1.0.
VARIETY = {'vermelha': 0.5, 'fada': 0.5, 'robella': 1.0, 'cerejeira': 1.0, 'serrana': 1.0,
           'medieval': 3.0, 'moderna': 2.0, 'solar': 2.5}


def variety(name):
    key = name.split('vila_', 1)[-1]
    for fam, mult in VARIETY.items():
        if key.startswith(fam):
            return mult
    return 1.0


def mixed_pool(scale, deposito=0.3):
    """conteudo proprio que entra em TODOS os bairros (casas variadas, depositos, casas comfy);
    scale ajusta o peso relativo ao conteudo de cada bairro. O porto fica so nas docas."""
    scale *= OWN_SHARE
    deposito *= OWN_SHARE
    pool = [{'factor': round(SCH.WEIGHT[n] * scale * variety(n), 3), 'value': n} for n in SCH.NAMES]
    pool += [{'factor': deposito, 'value': n} for n in V.NAMES_DEPOSITO]
    # houses.py: casafazenda, padariacomfy e oficinacreate com o mesmo peso base
    pool += SB('building_casafazenda/building_casafazenda', round(1.0 * scale, 3)) + \
        SB('building_padariacomfy/building_padariacomfy', round(1.0 * scale, 3)) + \
        SB('building_oficinacreate/building_oficinacreate', round(1.0 * scale, 3)) + \
        SB('building_cozinhakaleido/building_cozinhakaleido', round(0.3 * scale, 3)) + \
        SB('building_adegavinho/building_adegavinho', round(0.2 * scale, 3))
    return pool


def mixed_multis(scale):
    """casas de schematic com mais de 1 chunk (multibuildings) em todos os bairros"""
    return [{'factor': round(SCH.WEIGHT[m] * scale * OWN_SHARE * variety(m), 3), 'value': m} for m in SCH.MULTIS]


PORTO = SB('building_armazemporto/building_armazemporto', 0.7)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    json.dump({'pack': {'pack_format': 15, 'description': 'Sunlit Towns: vilas vivas do Sunlit Valley com casas variadas, depositos, '
               'bairros residenciais vivos, hortas, pracas e loot tematico'}},
              open(os.path.join(OUT, 'pack.mcmeta'), 'w'), indent=2)

    # estilos e paleta comum do DC (ruas, calcadas, gramado)
    for s in ['suburb_residential_style', 'retail_district_style', 'highrise_residential_style',
              'highrise_office_style', 'highrise_hotel_style']:
        write(f'data/deceasedcraft/lostcities/styles/{s}.json', json.loads(z.read(f'{DC}styles/{s}.json')))
    convert_palette('common', 'street')
    COMMON.update(PALS['common'].by_char)

    houses = B('building_residentiala', 0.07) + B('building_residentialb', 0.07) + B('building_residentialc', 0.07) + \
        B('building_residentiald', 0.07)
    shops = B('building_flowershop', 0.08) + B('building_fastfood', 0.06) + B('building_restaurantsushi', 0.04) + \
        B('building_clothstore', 0.05) + B('building_hardwarestoreie', 0.05) + B('building_hardwarestorece', 0.04)
    apart = B('building_apartmentsmalla', 0.06) + B('building_apartmentsmallb', 0.06) + B('building_apartmentsmallc', 0.06) + \
        B('building_apartmentsmalld', 0.06)

    # 1) vila residencial: o grosso das cidades (casas + comercio de bairro + pracas/hortas)
    build_citystyle('suburb_residential', 'vila', buildings=houses + shops + B('building_gasstation', 0.01),
                    multis=MB('multi_residentiale', 0.5) + MB('multi_residentialf', 0.5) + MB('multi_cafe', 0.25) +
                    MB('multi_convenientstore', 0.25) + MB('multi_communitycenter', 0.12) + MB('multi_polyclinic', 0.08) +
                    MB('multi_policestation', 0.06),
                     extra_multis=mixed_multis(1.0) + SB('multi_farmhouse1', 0.3) + SB('multi_cabin2', 0.3),
                     extra_buildings=mixed_pool(1.0),
                     # 2026-10-16: menos casas por bairro (buildingchance 0.22 -> 0.12); lotes vazios viram verde
                     parkchance=0.55, buildingchance=0.12,
                    park_weights={**P.PARK_WEIGHTS, 'vinhedo': 1.8, 'praca': 0.4, 'praca_waystone': 0.5, 'feira': 0.5})
    # 2) centro comercial: lojas, restaurantes, mercado
    build_citystyle('retail_district', 'centro', buildings=shops + houses[:8] + B('building_gasstation', 0.03),
                    multis=MB('multi_cafe', 0.4) + MB('multi_convenientstore', 0.4) + MB('multi_terraceplaza', 0.25) +
                    MB('multi_gasstation', 0.15) + MB('multi_hospital', 0.1) + MB('multi_residentiale', 0.2),
                     extra_multis=mixed_multis(0.8), extra_buildings=mixed_pool(0.8),
                     parkchance=0.45, buildingchance=0.26,
                    park_weights={**P.PARK_WEIGHTS, 'praca': 3.0, 'feira': 3.0, 'jardim': 1.5})
    # 3) bairro de apartamentos com escola
    build_citystyle('highrise_residential', 'apartamentos', buildings=apart + houses[:4] + shops[:4],
                    multis=MB('multi_flatapartment', 0.4) + MB('multi_flatmedium', 0.35) + MB('multi_flatlarge', 0.2) +
                    MB('multi_taigaresidence', 0.3) + MB('multi_oasiscondo', 0.15) + MB('multi_verticalschool', 0.15) +
                    MB('multi_policeapartment', 0.1),
                    extra_multis=mixed_multis(0.6), extra_buildings=mixed_pool(0.6), parkchance=0.5)
    # 4) centro de negocios (escritorios, banco)
    build_citystyle('highrise_office', 'negocios', multis=MB('multi_workshop', 0.4) + MB('multi_timbertower', 0.2) +
                    MB('multi_officethefirst', 0.25) + MB('multi_courtyardofficetower', 0.15),
                    extra_multis=mixed_multis(0.5), extra_buildings=shops[:6] + mixed_pool(0.5), parkchance=0.5)
    # 5) distrito industrial pequeno (oficinas, ferragens, estudios)
    build_citystyle('highrise_office', 'industrial',
                    buildings=B('building_hardwarestoreie', 0.3) + B('building_hardwarestorece', 0.3) + B('building_gasstation', 0.15) +
                    B('building_office4', 0.1) + B('building_office5', 0.1) + houses[:4],
                    multis=MB('multi_workshop', 0.8) + MB('multi_gasstation', 0.3),
                    extra_multis=mixed_multis(0.5), extra_buildings=mixed_pool(0.5, deposito=0.6),
                    parkchance=0.4)
    # 6) hoteis / lazer (raro)
    build_citystyle('highrise_hotel', 'hoteis', multis=MB('multi_gallery', 0.3) + MB('multi_timbertower', 0.2) +
                    MB('multi_sunkenclub', 0.2) + MB('multi_sunkenmonumentpark', 0.3) + MB('multi_casino', 0.1) +
                    MB('multi_thering', 0.1) + MB('multi_gasstation', 0.2),
                    extra_multis=mixed_multis(0.5), extra_buildings=mixed_pool(0.5), parkchance=0.5)

    # 7) zona de fazenda: poucas casas, muitas hortas/pomares/celeiros/currais (mescla de mods)
    build_citystyle('suburb_residential', 'rural', buildings=[dict(b, factor=0.06) for b in houses[:8]],
                    multis=MB('multi_farmhouse1', 0.6) + MB('multi_cabin2', 0.3),
                     extra_multis=mixed_multis(0.8), extra_buildings=mixed_pool(0.8, deposito=0.15) + SB('building_casafazenda/building_casafazenda', 0.4),
                     parkchance=0.8, buildingchance=0.18, maxfloors=3,
                    park_weights={**P.RURAL_PARK_WEIGHTS, 'vinhedo': 2.0})
    # 8) docas: bairro de pescadores perto de rio/praia (armazem do porto, cais, feira de peixe)
    build_citystyle('suburb_residential', 'docas', buildings=[dict(b, factor=0.04) for b in houses],
                    multis=MB('multi_cafe', 0.2) + MB('multi_convenientstore', 0.15),
                     extra_multis=mixed_multis(0.6), extra_buildings=PORTO + mixed_pool(0.6, deposito=0.2),
                     parkchance=0.6, buildingchance=0.22, maxfloors=3,
                    park_weights=P.DOCAS_PARK_WEIGHTS)

    # zona rural: fazendas, cabanas, acampamentos, food trucks
    scattered = [('multi_farmhouse1', 40), ('multi_cabin1', 20), ('multi_cabin2', 20), ('multi_cabin3', 20),
                 ('scattered_cabin_1', 12), ('scattered_cabin_2', 12), ('scattered_cabin_3', 12), ('multi_campsite1', 10),
                 ('scattered_treehouse_1', 8), ('scattered_foodtruck_1', 10), ('villager_1', 12)]
    for n, _ in scattered:
        do_scattered(f'deceasedcraft:{n}')

    # rodovias DC (sem carros batidos)
    ws_dc = json.loads(z.read(f'{DC}worldstyles/modern.json'))
    hw = ws_dc['parts']['highways']
    for k in hw:
        hw[k] = [x for x in hw[k] if not EXCLUDE.search(x)]
        for x in set(hw[k]):
            do_part(x, 'street')

    P.write_all(write)
    # funcoes manuais (/function sunlit:villagers_here etc.), sem o piloto automatico por tick
    fdir = os.path.join(OUT, 'data', 'sunlit', 'functions')
    os.makedirs(fdir, exist_ok=True)
    for fn in os.listdir(os.path.join(HERE, 'functions')):
        shutil.copy(os.path.join(HERE, 'functions', fn), fdir)

    land = ['#minecraft:is_ocean', '#minecraft:is_river', '#minecraft:is_beach']
    world = {
        'outsidestyle': 'outside',
        'settings': {'railwayavoidance': 'ignore', 'railpartheight6': 2},
        # casas da vila de schematic sao 2x2/3x2: mais multibuildings por area de 8x8 chunks
        # 2026-10-09: menos casas por bairro (maximum 6->4) para bairros mais arejados
        # 2026-10-16: maximum 4->2 (multibuildings menos densas, bairros com mais espaco entre casas)
        'multisettings': {'areasize': 8, 'minimum': 1, 'maximum': 2, 'correctstylefactor': 0.6, 'attempts': 30},
        'scattered': {'areasize': 7, 'chance': 0.7, 'weightnone': 25, 'list': [
            {'name': f'deceasedcraft:{n}', 'weight': w, 'maxheightdiff': 3, 'biomes': {'excluding': land}} for n, w in scattered] + [
            # porto cozy fora das cidades, so em rio/praia (if_any em vez de excluding)
            {'name': 'sunlit:multi_porto', 'weight': 14, 'maxheightdiff': 3,
             'biomes': {'if_any': ['#minecraft:is_river', '#minecraft:is_beach']}}]},
        'citybiomemultipliers': [{'multiplier': 0.1, 'biomes': {'if_any': ['#minecraft:is_ocean']}},
                                 {'multiplier': 0.3, 'biomes': {'if_any': ['#minecraft:is_river']}}],
        'citystyles': [{'factor': 7.0, 'citystyle': 'sunlit:vila'}, {'factor': 2.5, 'citystyle': 'sunlit:centro'},
                       {'factor': 1.2, 'citystyle': 'sunlit:apartamentos'}, {'factor': 0.7, 'citystyle': 'sunlit:industrial'},
                       {'factor': 0.5, 'citystyle': 'sunlit:negocios'}, {'factor': 0.3, 'citystyle': 'sunlit:hoteis'},
                       {'factor': 2.5, 'citystyle': 'sunlit:rural'},
                       {'factor': 6.0, 'citystyle': 'sunlit:rural',
                        'biomes': {'if_any': ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow',
                                              'minecraft:savanna', 'minecraft:flower_forest']}},
                       {'factor': 9.0, 'citystyle': 'sunlit:docas', 'biomes': {'if_any': ['#minecraft:is_beach', '#minecraft:is_river']}}],
        'parts': {'highways': hw},
    }
    write('data/sunlit/lostcities/worldstyles/towns.json', world)

    # condicoes de loot (palette "loot" aponta para condicao) + loot tables tematicas
    for t in sorted(used_themes | set(L.THEMES)):
        write(f'data/sunlit/lostcities/conditions/{t}.json', {'values': [{'factor': 1, 'value': f'sunlit:chests/{t}'}]})
        write(f'data/sunlit/loot_tables/chests/{t}.json', L.loot_table(t))
    L.write_extra_js()

    for pn, ps in PALS.items():
        write(f'data/deceasedcraft/lostcities/palettes/{pn}.json', {'palette': ps.entries})

    print(dict(counts))
    print('fallback (viraram ar):', stats['fallback'])
    with open(os.path.join(HERE, 'ultimo_mapeamento.json'), 'w') as f:
        json.dump({'substituidos': stats['mapped'], 'removidos_ar': stats['air']}, f, indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
