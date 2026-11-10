"""Polimento 3D do datapack (roda DEPOIS do finalize.py e ANTES do validate.py).

Olha cada parte montada (paleta da parte + sunlit:common) e corrige o que so aparece em jogo:
- movel de chao em cima de outro movel (pia de pe em cima de armario, bau em cima do fogao):
  ele desce para o piso com o que estava preso acima (espelho) e o armario sobe para o alto
  da parede com uma prateleira de apoio embaixo (padrao das casas importadas), ou some;
- nada apoiado em bau, saco, cesto, panela, assento, vaso, abajur...; numa lista random
  (caixotes e sacos sorteados) a posicao com algo em cima so sorteia blocos cheios;
- geladeira do Refurbished = freezer embaixo + geladeira em cima, costas na parede;
  movel de parede virado para a parede gira 180; coifa encostada no teto; banheira com
  as duas metades na ordem certa;
- coluna de folhas no maximo 4 blocos (parte de andar de cima nao continua a coluna);
- lanterna vanilla longe do teto ganha corrente (ou some se nao tiver apoio);
- vaso, relogio, maquina de costura etc. soltos no chao sobem para um movel vizinho ou
  ganham uma mesinha embaixo;
- cadeiras da mesma mesa ficam iguais (o tipo da maioria) e viradas para a mesa;
- prateleira vazia ganha enfeite em cima;
- cerca de horta na altura da terra sobe um bloco (embaixo vira borda de tora);
- street_lantern vira o poste Illuminant Column (simplylight:lamp_post, 3 blocos);
- loot so em bloco que guarda loot (o resto so gerava "Error setting loot" no log);
- movel de varias partes do Cluttered (armario 2x2, poltrona, manequim) ganha as partes que faltam ou
  vira um movel de 1 bloco;
- mesa das casas ganha comida de bloco em cima (Display Delight, assados, tortas, bolos);
- partes _90/_270 importadas com blocos de eixo sem girar (flywheel saindo da parede, poste deitado) trocam x/z;
- RETOUCH: correcoes a mao por parte (park_12: bancos soltos na borda, postes sem lanterna).

Uso: python3 polish.py   (o build todo esta no README)
"""
import collections, functools, glob, itertools, json, os, re, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcparts as L
import itemcheck as IC
import mapping as M

OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
DIRS = {'north': (-1, 0), 'south': (1, 0), 'west': (0, -1), 'east': (0, 1)}  # (dz, dx)
DIR_OF = {v: k for k, v in DIRS.items()}
STATS = collections.Counter()
DETAIL = collections.Counter()  # (regra, bloco, vizinho) -> n; impresso com --detalhe


def note(rule, *ids):
    DETAIL[(rule,) + tuple(bid(i) if isinstance(i, str) else i for i in ids)] += 1


def rx(p):
    return re.compile(p)


@functools.lru_cache(maxsize=None)  # nomes de bloco se repetem milhoes de vezes
def bid(s):
    return s.split('[')[0] if s else ''


@functools.lru_cache(maxsize=None)
def nm(s):
    """nome sem namespace: as categorias olham so o nome (buildersdelight/farmersdelight tem 'light',
    vinery tem 'vine', candlelight tem 'candle')"""
    return bid(s).split(':', 1)[-1]


def props(s):
    return M.parse(s)[1] if s else {}


def with_props(s, **kw):
    b, p = M.parse(s)
    p = dict(p, **{k: v for k, v in kw.items()})
    return M.fmt(b, p)


# ---------------------------------------------------------------- categorias (no id do bloco)
TABLE = rx(r'(?<!crafting)(?<!smithing)(?<!fletching)(?<!cartography)(?<!enchanting)(?<!schematic)(?<!sewing)(?<!side)'
           r'(?<!_end)(?<!end)_table$|^table_[a-z_]+$')
CHAIR = rx(r'(?<!arm)chair')
SEAT = rx(r'chair|stool|sofa|couch|_bench$|^bench$|armchair|_seat$|pouffe|ottoman')
CABINETLIKE = rx(r'kitchen_cabinetry|kitchen_drawer|kitchen_storage_cabinet|storage_cabinet|_cabinet$|_drawer$|drawers$|counter$|'
                 r'_counter$|dresser$')
SUPPORT = rx(r'_table$|^table_|side_table|end_table|nightstand|bedside|desk$|counter|cabinetry|_drawer$|drawers$|dresser|'
             r'_cabinet$|storage_cabinet|crate$|^barrel$|_barrel$|bookshelf|wine_rack|baker_station|workbench|casing$|depot$')
NO_TOP = rx(r'chest$|sack$|_sack|_bag$|basket|cooking_pot|stockpot|^pot$|skillet|kettle|sink$|basin$|toilet|_bath$|_bed$|'
            r'(?<!rod)lamp$|potted_|flower_pot$|^([a-z_]+_)?candle$|cutting_board|chopping_board|^plate$|clock$|sewing|typewriter|'
            r'toaster|microwave|^(soul_)?lantern$|chair|stool|sofa|couch|_bench$|armchair|_seat$|pouffe|ottoman')
FLOOR_ONLY = rx(r'basin$|kitchen_sink$|toilet|_bath$|_bed$|_stove$|^stove$|chair|stool|sofa|couch|'
                r'_bench$|armchair|desk$|wooden_planter|piano|mannequin|recycle_bin|trash')
# bau em cima de movel de cozinha/banheiro/assento sai (em cima de comoda, mesa ou estante fica)
CHEST = rx(r'(?<!ender_)chest$')
CHEST_BAD_BASE = rx(r'stove|oven|sink|basin|toilet|_bath$|chair|stool|sofa|couch|_bench$|_bed$|lamp$|microwave|toaster|range_hood|'
                    r'fridge|freezer')
SURFACE = rx(r'potted_|^flower_pot$|cuckoo_clock|^oak_clock$|_clock$|sewing_machine|typewriter|book_pile|stack_of_books|row_of_small_books|'
             r'^jar$|_jars$|vase$|kettle|toaster|microwave|radio$|^globe$|cash_register|office_supplies|paper_pile|tea_set|'
             r'desk_bell|coin_stack|gramophone|phonograph|vial_stand|box_of_paints')
# preso na parede/teto (nao "apoiado" em cima do bloco de baixo)
ATTACHED = rx(r'kitchen_storage_cabinet|sconce|_wall_|wall_lamp|mirror|painting|item_shelf|kitchenware_racks|_sign$|banner|lightswitch|doorbell|range_hood|'
              r'curtain|blinds|shutter|ladder|vine|chain$|ceiling|_fan$|hanging|_shelf$|faucet|towel|rack$')
HOOD = rx(r'range_hood$')
# loucas e fogao: em cima de armario, descem para o piso e o armario sobe (o resto so sai)
FIXTURE = rx(r'basin$|sink$|toilet|washing_machine|_stove$|^stove$')
SHELF = rx(r'(?<!book)(?<!item_)shelf$|shelf_[a-z]+$')
LEAVES = rx(r'_leaves$|_hedge$')
FENCE = rx(r'(?<!iron)(?<!nether_brick)_fence$|_fence_gate$|picket_fence(_gate)?$')
FURNITURE = rx('|'.join(p.pattern for p in (TABLE, SEAT, SUPPORT, NO_TOP, FLOOR_ONLY, SURFACE, ATTACHED, HOOD, SHELF)) +
               r'|fridge|freezer|_bed$|television|computer|bookshelf|planter|trash|bin$|stove|oven|grill|cooler')
THIN = rx(r'carpet|pressure_plate|_rug$|snow$|moss_carpet')
OUTDOOR = rx(r'grass|dirt|podzol|mycelium|moss|sand$|gravel|farmland|path|mud$|clay$|snow')
# movel de cima (mesa, cadeira, balcao...): nada de mesinha ou outro movel empilhado em cima dele
FURN_TOP = rx(r'table|chair|bench|stool|sofa|armchair|counter|desk|drawer|cabinet|crate|barrel|chest')
NONSOLID = rx(r'air$|water|lava|door|trapdoor|_stairs|_slab|fence|_wall$|pane|bars|glass|torch|lantern|button|plate|rail|vine|'
              r'carpet|chain|sign|banner|flower|sapling|grass$|fern|bush|_bed$|rod$|candle|scaffold|ladder|leaves|hedge|lattice|'
              r'cobweb|lamp|light|_post$|pole|seat|rope')


def is_air(s):
    return s is not None and L.block_is_air(s)


def furniture(s):
    return bool(s) and s != '?' and bool(FURNITURE.search(nm(s)))


def solid(s):
    """bloco de construcao (parede, piso, teto)"""
    if not s or s == '?':
        return s == '?'
    return not NONSOLID.search(nm(s)) and not furniture(s)


def cat_all(g, y, z, x, pat):
    o = g.opts(y, z, x)
    return bool(o) and all(pat.search(nm(s)) for s in o if s != '?')


def cat_any(g, y, z, x, pat):
    return any(pat.search(nm(s)) for s in g.opts(y, z, x) if s != '?')


def wallish(s):
    """serve de parede para encostar movel: solido, slab vertical, vidro/vidraca"""
    return solid(s) or bool(re.search(r'vertical_slab|glass|_pane$|window', nm(s))) if s else False


def ceiling(s):
    """bloco que serve de teto (solido, laje de cima, escada invertida)"""
    return solid(s) or bool(re.search(r'_slab\[.*type=(double|top)|_stairs\[.*half=top', s or ''))


def floor_below(g, y, z, x):
    """True se o que esta embaixo e piso de verdade (carpete e transparente); fora da parte conta como piso"""
    yy = y - 1
    while yy >= 0 and THIN.search(nm(g.b(yy, z, x)) or '-'):
        yy -= 1
    if yy < 0:
        return True
    b = g.b(yy, z, x)
    return solid(b) or bool(re.search(r'_slab\[.*type=(double|top)|_stairs', b or ''))


def covered(g, y, z, x, up=5):
    """interior: algo solido acima dentro de 'up' blocos"""
    for yy in range(y + 1, min(g.H, y + up + 1)):
        if solid(g.b(yy, z, x)):
            return True
    return False


def back_is_facing(block):
    return bid(block).startswith('refurbished_furniture:')


def wall_dir(block):
    """lado da parede de um movel encostado (convencao de cada mod)"""
    f = props(block).get('facing')
    if f not in OPP:
        return None
    return f if back_is_facing(block) else OPP[f]


def facing_with_wall(block, wall):
    return wall if back_is_facing(block) else OPP[wall]


def pick(seed, seq):
    seq = list(seq)
    return seq[zlib.crc32(seed.encode()) % len(seq)] if seq else None


def wood_of(s, default='oak'):
    for w in ('dark_oak', 'spruce', 'birch', 'jungle', 'acacia', 'mangrove', 'cherry', 'crimson', 'warped', 'oak'):
        if w in bid(s):
            return w
    return default


def ok_state(s):
    b, p = M.parse(s)
    if not M.exists(b):
        return None
    return M.fmt(b, M.clean_props(b, p))


# ---------------------------------------------------------------- loot
LOOT_OK = rx(r'^minecraft:(chest|trapped_chest|barrel|dispenser|dropper|hopper|[a-z_]*shulker_box)$|^lootr:|'
             r'^refurbished_furniture:[a-z_]*(drawer|storage_cabinet|crate|fridge|freezer|cooler|storage_jar|mail_box|post_box|'
             r'recycle_bin|stove|microwave|toaster|workbench|cutting_board|frying_pan|plate)$|'
             r'^cfm:[a-z_]*(cabinet|cooler|crate|freezer|fridge|kitchen_drawer|mail_box)$|^another_furniture:[a-z_]*_drawer$|'
             r'^farmersdelight:([a-z_]*_cabinet|wooden_basket|basket)$|^furniture:[a-z_]*(cabinet|coffer|dresser)$|'
             r'^redeco:[a-z_]*(cabinet|drawers|side_table|trash_bin)$|^supplementaries:(sack|safe)$|^cluttered:cardboard_box[a-z_]*$|'
             r'^(meadow|vinery|beachparty):[a-z_]*cabinet$|^vinery:[a-z_]*basket$|^farm_and_charm:(crafting_bowl|mincer)$|'
             r'^(bakery|brewery):(cabinet|drawer|wall_cabinet)$|^quark:[a-z_]+_(trapped_)?chest$|^vinery:(storage_pot|dark_cherry_barrel)$|'
             r'^cluttered:kitchen_set_[a-z_]+?_(cabinet|cabinet_glass|cabinet_mini|cabinet_inner_corner|cabinet_open|counter|'
             r'counter_outer_corner_left|counter_outer_corner_right)$')


def fix_loot(store):
    for pal in list(store.pals.values()):
        for e in pal.entries:
            if 'loot' not in e:
                continue
            ids = [bid(e['block'])] if 'block' in e else [bid(b['block']) for b in e.get('blocks', [])]
            if ids and not all(LOOT_OK.search(i) for i in ids):
                del e['loot']
                pal.dirty = True
                STATS['loot_removido'] += 1


# ---------------------------------------------------------------- regras por parte
def cells(g):
    return itertools.product(range(g.H), range(g.Z), range(g.X))


def two_part(s):
    return bool(re.search(r'half=upper|half=lower|part=head|part=foot|type=head|type=bottom|_bed$|fridge|freezer|_bath$',
                          s or '')) or bool(re.search(r'_bed$|fridge|freezer|_bath$', bid(s)))


JUNK = rx(r'^minecraft:(daylight_detector|observer|comparator|repeater|redstone_wire|tripwire|target)$')


def rule_junk(g):
    """redstone e sensor de luz soltos (vinham de lampada automatica dos predios importados)"""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) == 1 and JUNK.search(bid(o[0])):
            g.clear(y, z, x)
            STATS['redstone_removido'] += 1


def rule_chests(g):
    """bau em cima de fogao, pia, geladeira, assento... sai (em cima de comoda, mesa ou estante fica)"""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if y == 0 or len(o) != 1 or not CHEST.search(nm(o[0])):
            continue
        under = g.opts(y - 1, z, x)
        if len(under) == 1 and CHEST_BAD_BASE.search(nm(under[0])):
            note('bau_removido', under[0])
            g.clear(y, z, x)
            STATS['bau_em_movel_removido'] += 1


def rule_loot_cap(g, outdoor):
    """no maximo 2 containers com loot por parte/andar (3 se o andar for maior),
    2026-10-09 pedido do dono: bau/barril de verdade primeiro, ordem fixa por
    posicao para nao variar entre rebuilds. Parques e ruas ficam como estao."""
    if outdoor:
        return
    found = []
    for y, z, x in cells(g):
        e = g.entry(y, z, x)
        if not e or 'loot' not in e:
            continue
        o = g.opts(y, z, x)
        if len(o) != 1:
            continue
        i = bid(o[0])
        prio = 0 if re.search(r'chest$|barrel$', i) else (1 if re.search(r'fridge|freezer', i) else 2)
        found.append((prio, y, z, x))
    if len(found) <= 2:
        return
    keep_n = 3 if len(found) > 6 else 2
    for _, y, z, x in sorted(found)[keep_n:]:
        e = dict(g.entry(y, z, x))
        e.pop('loot', None)
        e.pop('char', None)
        note('loot_cortado', g.b(y, z, x))
        g.put_entry(y, z, x, e)
        STATS['loot_cortado'] += 1


def _fridge_want(g, y, z, x, cur):
    """lado da parede para as costas da geladeira (facing = costas): o atual se a
    parede estiver atras e a frente livre; senao um lado com parede atras e frente
    livre (solido primeiro, vidro/vidraca depois); senao o atual."""
    order = [cur] + [d for d in ('north', 'south', 'west', 'east') if d != cur]

    def Sr(d):
        dz, dx = DIRS[d]
        return g.b(y, z + dz, x + dx)

    def front_open(d):
        f = OPP[d]
        dz, dx = DIRS[f]
        s = g.b(y, z + dz, x + dx)
        if s is None:
            return True
        if wallish(s) or furniture(s):
            return False
        s2 = g.b(y + 1, z + dz, x + dx)
        return s2 is None or not (wallish(s2) or furniture(s2))

    for solid_first in (True, False):
        for d in order:
            w = Sr(d)
            if w is None or not wallish(w):
                continue
            if solid_first and not solid(w):
                continue
            if front_open(d):
                return d
    for d in order:
        w = Sr(d)
        if w is not None and wallish(w):
            return d
    return cur


def rule_fridges(g):
    """freezer embaixo + geladeira em cima, mesma cor e mesmo facing, costas na
    parede com a frente livre (2026-10-09: antes so girava 180 quando o outro lado
    era parede; atravessada de lado continuava atravessada)"""
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        m = re.match(r'refurbished_furniture:(light|dark)_(fridge|freezer)$', bid(b))
        if not m or len(g.opts(y, z, x)) != 1:
            continue
        below = g.b(y - 1, z, x) if y > 0 else None
        if below and re.match(r'refurbished_furniture:(light|dark)_(fridge|freezer)$', bid(below)):
            continue  # nao e a base da pilha
        tone = m.group(1)
        run = 0
        while g.inside(y + run, z, x) and re.match(r'refurbished_furniture:(light|dark)_(fridge|freezer)$', bid(g.b(y + run, z, x))):
            run += 1
        f = _fridge_want(g, y, z, x, props(b).get('facing', 'north'))
        if f != props(b).get('facing', 'north'):
            STATS['geladeira_girada'] += 1
        g.put(y, z, x, f'refurbished_furniture:{tone}_freezer[facing={f},open=false]', loot=g.entry(y, z, x).get('loot'))
        if run >= 2:
            g.put(y + 1, z, x, f'refurbished_furniture:{tone}_fridge[facing={f},open=false]', loot=g.entry(y + 1, z, x).get('loot'))
            for k in range(2, run):
                g.clear(y + k, z, x)
        elif g.inside(y + 1, z, x) and is_air(g.b(y + 1, z, x)):
            g.put(y + 1, z, x, f'refurbished_furniture:{tone}_fridge[facing={f},open=false]')
            STATS['geladeira_completa'] += 1


ORIENT_BACK = rx(r'^refurbished_furniture:[a-z_]*(kitchen_sink|basin|toilet|kitchen_cabinetry|kitchen_drawer|kitchen_storage_cabinet|'
                  r'storage_cabinet|stove|range_hood|cooler|drawer)$')
ORIENT_FRONT = rx(r'^farmersdelight:([a-z_]*_cabinet|stove)$|^candlelight:[a-z_]*(counter|stove|drawer)$|^bakery:[a-z_]*(counter|cabinet|'
                  r'drawer|station)$|^another_furniture:[a-z_]*drawer$|^furniture:[a-z_]*(cabinet|dresser)$|^kaleidoscope_cookery:stove$|'
                  r'^minecraft:(furnace|smoker|blast_furnace)$|^create:display_board$|^supplementaries:notice_board$')


def rule_orient(g):
    """movel de parede com a frente na parede e as costas no vazio gira 180"""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1:
            continue
        b = o[0]
        if not (ORIENT_BACK.search(bid(b)) or ORIENT_FRONT.search(bid(b))):
            continue
        w = wall_dir(b)
        if not w:
            continue
        dz, dx = DIRS[w]
        if wallish(g.b(y, z - dz, x - dx)) and not wallish(g.b(y, z + dz, x + dx)) and g.inside(y, z + dz, x + dx):
            _flip_orient(g, y, z, x, b)
        elif wallish(g.b(y, z - dz, x - dx)) and wallish(g.b(y, z + dz, x + dx)):
            # encurralado (parede dos dois lados, ex. quiosque da floricultura): as costas ficam no lado
            # mais fechado em cima (balcao/parede) e a frente no lado mais aberto (sala)
            back_open = _column_open(g, y, z - dz, x - dx)
            front_open = _column_open(g, y, z + dz, x + dx)
            if front_open < back_open:
                _flip_orient(g, y, z, x, b)


def _column_open(g, y, z, x):
    """quao aberto e acima da celula (0 = fechado, quanto maior mais sala): ar/folha conta, solido nao"""
    n = 0
    for yy in range(y + 1, min(g.H, y + 3)):
        s = g.b(yy, z, x)
        if s is None or is_air(s) or LEAVES.search(nm(s) or ''):
            n += 1
    return n


def _flip_orient(g, y, z, x, b):
    f = props(b)['facing']
    e = dict(g.entry(y, z, x))
    e.pop('char', None)
    e['block'] = with_props(b, facing=OPP[f])
    g.put_entry(y, z, x, e)
    note('movel_parede_girado', b)
    STATS['movel_parede_girado'] += 1


DOOR = rx(r'_door$')
TRAPDOOR = rx(r'trapdoor$')


def rule_doors(g):
    """porta dupla com as metades em facing diferente (floricultura DC: uma aberta para um lado e a outra
    fechada para o outro) alinha tudo no facing da metade fechada; a metade de cima acompanha a de baixo"""
    lowers = {}
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or TRAPDOOR.search(nm(o[0])):
            continue
        if not DOOR.search(nm(o[0])) or props(o[0]).get('half', 'lower') != 'lower':
            continue
        lowers[(y, z, x)] = o[0]
    seen = set()
    for (y, z, x), b in lowers.items():
        if (y, z, x) in seen:
            continue
        group = [(y, z, x)]
        for dz, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            if (y, z + dz, x + dx) in lowers:
                group.append((y, z + dz, x + dx))
        if len(group) < 2:
            continue
        seen.update(group)
        faces = [props(lowers[c])['facing'] for c in group]
        if len(set(faces)) == 1:
            _door_wall(group, g)
            continue
        closed = [props(lowers[c])['facing'] for c in group if props(lowers[c]).get('open') == 'false']
        want = max(set(closed), key=closed.count) if closed else max(set(faces), key=faces.count)
        for (yy, zz, xx) in group:
            _set_door_facing(g, yy, zz, xx, want)
        _door_wall(group, g)
    # porta sozinha no meio de parede reta mas com facing paralelo a parede (porta t da floricultura):
    # gira para a perpendicular, para o lado aberto
    for (y, z, x), b in lowers.items():
        if (y, z, x) in seen:
            continue
        f = props(b).get('facing')
        wall_x = wallish(g.b(y, z, x - 1)) and wallish(g.b(y, z, x + 1))
        wall_z = wallish(g.b(y, z - 1, x)) and wallish(g.b(y, z + 1, x))
        if wall_x and not wall_z and f in ('east', 'west'):
            _set_door_facing(g, y, z, x, _open_side(g, y, z, x, ('north', 'south')))
        elif wall_z and not wall_x and f in ('north', 'south'):
            _set_door_facing(g, y, z, x, _open_side(g, y, z, x, ('east', 'west')))


def _open_side(g, y, z, x, sides):
    """dos dois lados, o mais aberto (ar em y + espaco acima); empate fica no primeiro"""
    best, best_n = sides[0], -1
    for s in sides:
        dz, dx = DIRS[s]
        n = 0
        cell = g.b(y, z + dz, x + dx)
        if cell is None or is_air(cell):
            n += 2
        elif not wallish(cell):
            n += 1
        n += _column_open(g, y, z + dz, x + dx)
        if n > best_n:
            best, best_n = s, n
    return best


def _door_wall(group, g):
    """grupo de portas com facing paralelo a parede reta: gira o grupo para a perpendicular"""
    (y, z, x) = group[0]
    f = props(g.b(y, z, x)).get('facing')
    wall_x = all(wallish(g.b(yy, zz, xx - 1)) and wallish(g.b(yy, zz, xx + 1)) for (yy, zz, xx) in group)
    wall_z = all(wallish(g.b(yy, zz - 1, xx)) and wallish(g.b(yy, zz + 1, xx)) for (yy, zz, xx) in group)
    want = None
    if wall_x and not wall_z and f in ('east', 'west'):
        want = _open_side(g, y, z, x, ('north', 'south'))
    elif wall_z and not wall_x and f in ('north', 'south'):
        want = _open_side(g, y, z, x, ('east', 'west'))
    if want and want != f:
        for (yy, zz, xx) in group:
            _set_door_facing(g, yy, zz, xx, want)


def _set_door_facing(g, y, z, x, want):
    for dy in (0, 1):
        if not g.inside(y + dy, z, x):
            continue
        cur = g.b(y + dy, z, x)
        if cur is None or not DOOR.search(nm(cur) or '') or TRAPDOOR.search(nm(cur) or ''):
            continue
        if props(cur).get('facing') == want:
            continue
        e = dict(g.entry(y + dy, z, x))
        e.pop('char', None)
        e['block'] = with_props(cur, facing=want)
        g.put_entry(y + dy, z, x, e)
        STATS['porta_alinhada'] += 1


def rule_door_visible(g):
    """porta de vidro do Create (framed_glass_door) sem a prop visible: o estado fica incompleto e a
    porta some ou aparece pela metade no jogo; ganha visible=true (a mesma prop das portas do blockstate)"""
    for y, z, x in cells(g):
        cur = g.b(y, z, x)
        if not cur or nm(cur) != 'framed_glass_door' or 'visible' in props(cur):
            continue
        e = dict(g.entry(y, z, x))
        e.pop('char', None)
        e['block'] = with_props(cur, visible='true')
        g.put_entry(y, z, x, e)
        STATS['porta_visible'] += 1


def rule_hedge_links(g):
    """hedge do Refurbished sem north/south/east/west (cubo isolado): liga nos vizinhos do mesmo slice
    que sao hedge ou folha; a regra e a mesma do HedgeBlock do Refurbished"""
    def links(b):
        return bool(b) and (re.search(r'_hedge$', nm(b)) is not None or re.search(r'_leaves$', nm(b)) is not None)
    for y, z, x in cells(g):
        cur = g.b(y, z, x)
        if not cur or not re.search(r'_hedge$', nm(cur)):
            continue
        p = props(cur)
        want = {}
        for d, (dz, dx) in DIRS.items():
            ok = g.inside(y, z + dz, x + dx)
            want[d] = 'true' if ok and links(g.b(y, z + dz, x + dx)) else 'false'
        if all(p.get(d) == v for d, v in want.items()):
            continue
        e = dict(g.entry(y, z, x))
        e.pop('char', None)
        e['block'] = with_props(cur, **want)
        g.put_entry(y, z, x, e)
        STATS['hedge_liga'] += 1


def axis_unrotated(store):
    """partes _90/_270 importadas cujos blocos com eixo (postes deitados, eixos, engrenagens, flywheel) vieram sem
    girar: mesma contagem de axis=x/axis=z que a parte base. Num predio girado 90/270 graus x e z trocam."""
    out = set()
    for name, (path, part) in store.parts.items():
        m = re.search(r'_(90|270)$', name)
        if not m or name[:m.start()] not in store.parts:
            continue
        cnt = []
        for n in (name[:m.start()], name):
            g = FastGrid(store, n, store.parts[n][1])
            c = collections.Counter(props(s).get('axis') for y, z, x in cells(g) for s in [g.b(y, z, x)] if s and 'axis=' in s)
            cnt.append((c['x'], c['z']))
        if cnt[0] == cnt[1] and cnt[0] != (0, 0):
            out.add(name)
    return out


def rule_rotated_axis(g):
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not re.search(r'axis=[xz]', o[0]):
            continue
        e = dict(g.entry(y, z, x))
        e.pop('char', None)
        e['block'] = with_props(o[0], axis='z' if props(o[0])['axis'] == 'x' else 'x')
        g.put_entry(y, z, x, e)
        STATS['eixo_girado'] += 1


def retouch_park_12(g):
    """praca de quartzo: as escadas soltas na borda ficavam por cima do muro/vao que o Lost Cities poe em volta do
    parque (bancos brancos flutuando); os postes tinham corrente sem lanterna e alcapao de ferro solto no ar"""
    n = g.Z - 1
    for z in range(g.Z):
        for x in range(g.X):
            if (z in (0, n) or x in (0, n)) and g.H > 1 and bid(g.b(1, z, x)) == 'minecraft:quartz_stairs':
                g.clear(1, z, x)
                STATS['park12_banco_borda'] += 1
            if g.H < 6 or bid(g.b(4, z, x)) != 'cfm:light_gray_picket_fence' or not (z in (0, n) or x in (0, n)):
                continue
            dz, dx = (1 if z == 0 else -1 if z == n else 0), (1 if x == 0 else -1 if x == n else 0)
            if dz and dx:
                continue
            if bid(g.b(5, z + dz, x + dx)) == 'minecraft:stone_slab':
                g.put(4, z + dz, x + dx, ok_state('minecraft:lantern[hanging=true,waterlogged=false]'))
                STATS['park12_lanterna'] += 1
            if g.inside(4, z + 2 * dz, x + 2 * dx) and bid(g.b(4, z + 2 * dz, x + 2 * dx)) == 'minecraft:iron_trapdoor':
                g.clear(4, z + 2 * dz, x + 2 * dx)


RETOUCH = {'sunlit:parks/park_12': retouch_park_12}


def retouch_convenience(g):
    """lojinha do posto: bancada de hortifruti com padrao FIXO (regra do dono; antes cada
    posicao sorteava entre 10 caixotes/sacos e ficava aleatorio). Caixotes deterministicos,
    armarios verdes de vidro com geleias em cima, sem produce empilhado em cima de lampada."""
    fixed = {(8, 4): 'hearthandharvest:apple_crate', (9, 4): 'hearthandharvest:raspberry_crate',
             (10, 4): 'hearthandharvest:blueberry_crate', (11, 4): 'culturaldelights:eggplant_crate',
             (12, 4): 'vintagedelight:cucumber_crate', (8, 6): 'veggiesdelight:broccoli_crate',
             (9, 6): 'farmersdelight:rice_bag', (10, 6): 'farmersrespite:green_tea_leaves_sack',
             (11, 6): 'youkaishomecoming:cucumber_crate', (12, 6): 'vinery:apple_bag[facing=north]',
             (11, 7): 'hearthandharvest:apple_crate'}
    for (x, z), block in fixed.items():
        st = ok_state(block)
        if not st:
            continue
        cur = g.opts(2, z, x)
        if len(cur) >= 1:
            g.put(2, z, x, st)
            STATS['loja_caixote_fixo'] += 1
        # produce empilhado em cima de lampada nao existe: volta a ser ar
        up = g.b(3, z, x)
        if up and up != '?' and nm(up) not in ('air',) and 'industrial_flat' not in up and 'lantern' not in up:
            g.clear(3, z, x)
            STATS['loja_pilha_removida'] += 1
    for z in (5, 6):
        cab = ok_state('cluttered:kitchen_set_light_green_cabinet_glass[facing=east,waterlogged=false]')
        jar = ok_state('cluttered:jam_jars[facing=east,stacked=false]')
        if cab and bid(g.b(1, z, 5)) == 'minecraft:smooth_stone_slab':
            g.put(1, z, 5, cab)
            STATS['loja_armario_verde'] += 1
            if jar and is_air(g.b(2, z, 5)):
                g.put(2, z, 5, jar)
                STATS['loja_geleia'] += 1


RETOUCH['sunlit:convenientstore_1/ground'] = retouch_convenience


def rule_bath(g):
    """banheira do Refurbished: facing aponta da metade bottom para a head (a head e a ponta fechada)"""
    seen = set()
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if not re.match(r'refurbished_furniture:[a-z_]+_bath$', bid(b)) or (y, z, x) in seen:
            continue
        for d, (dz, dx) in DIRS.items():
            n = g.b(y, z + dz, x + dx)
            if n and bid(n) == bid(b) and (y, z + dz, x + dx) not in seen:
                f = props(b).get('facing')
                # mantem a orientacao original se ja estiver no eixo do par
                if f == OPP[d]:
                    head, bottom, face = (y, z, x), (y, z + dz, x + dx), OPP[d]
                else:
                    head, bottom, face = (y, z + dz, x + dx), (y, z, x), d
                want_h = f'{bid(b)}[facing={face},type=head]'
                want_b = f'{bid(b)}[facing={face},type=bottom]'
                if g.b(*head) != want_h or g.b(*bottom) != want_b:
                    g.put(*head, want_h, loot=(g.entry(*head) or {}).get('loot'))
                    g.put(*bottom, want_b, loot=(g.entry(*bottom) or {}).get('loot'))
                    STATS['banheira_corrigida'] += 1
                seen.update({head, bottom})
                break


def rule_hood(g):
    """coifa sobe ate encostar no teto"""
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if not HOOD.search(nm(b)) or len(g.opts(y, z, x)) != 1:
            continue
        top = y
        while g.inside(top + 1, z, x) and is_air(g.b(top + 1, z, x)):
            top += 1
        if top != y and g.inside(top + 1, z, x) and ceiling(g.b(top + 1, z, x)):
            g.copy_cell((y, z, x), (top, z, x))
            g.clear(y, z, x)
            STATS['coifa_no_teto'] += 1


def stack_above(g, y, z, x):
    """celulas de movel/enfeite empilhadas a partir de y (para no ar ou em bloco de construcao)"""
    out = []
    while g.inside(y, z, x):
        b = g.b(y, z, x)
        if is_air(b) or not furniture(b):
            break
        out.append(y)
        y += 1
    return out


def shelf_for(wood, wall):
    s = ok_state(f'another_furniture:{wood}_shelf[facing={OPP[wall]},horizontal=single]')
    return s or ok_state(f'another_furniture:oak_shelf[facing={OPP[wall]},horizontal=single]')


def rule_floor_only(g):
    """movel de chao em cima de outro movel. Armario embaixo de pia/vaso/etc: a pia desce com o
    que estava preso nela (espelho) e o armario vai para o alto da parede com prateleira de apoio."""
    for y, z, x in cells(g):
        if y == 0:
            continue
        o = g.opts(y, z, x)
        if len(o) == 1 and CHEST.search(nm(o[0])):
            continue
        if len(o) != 1 or not FLOOR_ONLY.search(nm(o[0])) or two_part(o[0]):
            continue
        below = g.opts(y - 1, z, x)
        if len(below) != 1 or not furniture(below[0]) or two_part(below[0]) or is_air(below[0]):
            continue
        if SHELF.search(nm(below[0])) and not CABINETLIKE.search(nm(below[0])):
            continue
        S = below[0]
        S_loot = (g.entry(y - 1, z, x) or {}).get('loot')
        if FIXTURE.search(nm(o[0])) and CABINETLIKE.search(nm(S)) and floor_below(g, y - 1, z, x):
            seg = stack_above(g, y, z, x)
            for yy in seg:  # desce a pilha (pia, espelho, ...) um bloco
                g.copy_cell((yy, z, x), (yy - 1, z, x))
            g.clear(seg[-1], z, x)
            # armario no alto: abaixo do primeiro bloco solido acima da pilha, com parede atras
            top = seg[-1]
            while g.inside(top + 1, z, x) and is_air(g.b(top + 1, z, x)):
                top += 1
            w = wall_dir(S)
            placed = False
            if is_air(g.b(top, z, x)) and g.inside(top + 1, z, x) and ceiling(g.b(top + 1, z, x)) and w:
                dz, dx = DIRS[w]
                if wallish(g.b(top, z + dz, x + dx)):
                    g.put(top, z, x, S, loot=S_loot)
                    placed = True
                    if top - 1 > seg[-1] - 1 and is_air(g.b(top - 1, z, x)):
                        sh = shelf_for(wood_of(S), w)
                        if sh:
                            g.put(top - 1, z, x, sh)
            note('movel_de_chao_desceu', o[0], S)
            STATS['movel_de_chao_desceu'] += 1
            STATS['armario_subiu' if placed else 'armario_removido'] += 1
        else:
            note('movel_de_chao_removido', o[0], S)
            g.clear(y, z, x)
            STATS['movel_de_chao_removido'] += 1


def rule_no_top(g):
    """nada apoiado em bau, saco, cesto, panela, assento, vaso, abajur..."""
    for y, z, x in cells(g):
        if not g.inside(y + 1, z, x):
            continue
        o = g.opts(y, z, x)
        if not o or not any(NO_TOP.search(nm(s)) for s in o if s != '?') or ATTACHED.search(nm(o[0])):
            continue
        a = g.b(y + 1, z, x)
        if is_air(a) or not furniture(a) or ATTACHED.search(nm(a)) or 'hanging=true' in (a or ''):
            continue
        if two_part(o[0]) and bid(a).split('_')[-1] == bid(o[0]).split('_')[-1]:
            continue
        e = g.entry(y, z, x)
        if e and e.get('blocks') and not all(NO_TOP.search(nm(s)) for s in o):
            # lista random (caixotes/sacos): nesta posicao so sorteia o que aguenta peso
            keep = [dict(b) for b in e['blocks'] if not NO_TOP.search(nm(b['block']))]
            tot = sum(b.get('random', 0) for b in keep)
            if tot < 128:  # o Lost Cities aborta o chunk se a lista nao somar 128
                k = -(-128 // max(tot, 1))
                for b in keep:
                    b['random'] = max(b.get('random', 0), 1) * k
            ne = {k: v for k, v in e.items() if k not in ('char', 'blocks')}
            ne['blocks'] = keep
            g.put_entry(y, z, x, ne)
            STATS['lista_sem_saco'] += 1
            continue
        for yy in stack_above(g, y + 1, z, x):
            if ATTACHED.search(nm(g.b(yy, z, x))):
                break
            note('removido_de_cima', g.b(yy, z, x), o[0])
            g.clear(yy, z, x)
            STATS['removido_de_cima'] += 1


def rule_leaves(g, upper):
    """colunas de folha/hedge com no maximo 4; em parte de andar de cima, coluna que comeca
    na fatia 0 e continuacao do andar de baixo e sai."""
    for z in range(g.Z):
        for x in range(g.X):
            y = 0
            while y < g.H:
                if not cat_all(g, y, z, x, LEAVES):
                    y += 1
                    continue
                s = y
                while y < g.H and cat_all(g, y, z, x, LEAVES):
                    y += 1
                if s == 0 and upper:
                    for yy in range(s, y):
                        g.clear(yy, z, x)
                    STATS['folha_continuacao'] += y - s
                elif y - s > 4:
                    for yy in range(s + 4, y):
                        g.clear(yy, z, x)
                    STATS['folha_cortada'] += y - s - 4


LANTERN = rx(r'^minecraft:(soul_)?lantern$')


def rule_lanterns(g):
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if not LANTERN.search(bid(b)) or len(g.opts(y, z, x)) != 1:
            continue
        hanging = props(b).get('hanging') == 'true'
        below = g.b(y - 1, z, x) if y > 0 else 'x'
        above = g.b(y + 1, z, x)
        if not hanging and (y == 0 or not is_air(below)):
            continue
        if hanging and (above is None or not is_air(above)):
            continue  # preso no teto ou topo da parte (o andar de cima e o teto)
        c = y + 1
        while c < g.H and is_air(g.b(c, z, x)) and c - y <= 4:
            c += 1
        if c < g.H and c - y <= 4 and not is_air(g.b(c, z, x)):
            for yy in range(y + 1, c):
                g.put(yy, z, x, ok_state('minecraft:chain[axis=y]'))
            g.put(y, z, x, with_props(b, hanging='true'))
            STATS['lanterna_com_corrente'] += 1
        elif y > 0 and not is_air(below):
            g.put(y, z, x, with_props(b, hanging='false'))
        elif c >= g.H:
            continue  # acima da parte: pode ter o teto do proximo andar
        else:
            g.clear(y, z, x)
            STATS['lanterna_solta_removida'] += 1


LIGHT_ANY = rx(r'lantern|torch|candle|glowstone|shroomlight|sea_lantern|froglight|redstone_lamp|chandelier|ceiling_light|_lamp$|lamp_post')


def rule_dark_parts(g, name):
    """parte interna sem nenhuma luz (nem tocha/vela) ganha ate 2 lanternas de
    teto: comodo fechado (piso embaixo, ar no meio, teto solido em cima).
    2026-10-10: oficinas do Create (workshop_*) e torres DC escuras. Telhados,
    parques e infra de rua ficam de fora."""
    if re.match(r'sunlit:(parks|fountains)/', name):
        return
    if re.search(r'/top$|/eave$|roof|bridge|highway|street|plaza|fountain', name):
        return
    n_light = sum(1 for y, z, x in cells(g) if len(g.opts(y, z, x)) == 1 and LIGHT_ANY.search(nm(g.b(y, z, x) or '')))
    if n_light >= 2:
        return
    placed = []
    for z, x in sorted(((z, x) for z in range(g.Z) for x in range(g.X)),
                       key=lambda c: abs(c[1] - g.X // 2) + abs(c[0] - g.Z // 2)):
        if n_light + len(placed) >= 2:
            break
        if any(abs(x - px) + abs(z - pz) < 5 for _, pz, px in placed):
            continue
        for y in range(min(g.H - 2, 4), 2, -1):
            if not g.inside(y + 1, z, x) or y - 3 < 0:
                continue
            o = g.opts(y, z, x)
            if len(o) != 1 or not is_air(o[0]):
                continue
            if not all(len(g.opts(y - k, z, x)) == 1 and is_air(g.b(y - k, z, x)) for k in (1, 2)):
                continue
            if not ceiling(g.b(y + 1, z, x)):
                continue
            if not floor_below(g, y - 2, z, x):
                continue
            g.put(y, z, x, ok_state('minecraft:lantern[hanging=true,waterlogged=false]'))
            placed.append((y, z, x))
            STATS['lanterna_no_escuro'] += 1
            note('lanterna_no_escuro', name)
            break


def side_table(seed, wall):
    w = pick(seed, ['oak', 'spruce', 'dark_oak', 'birch'])
    f = OPP[wall] if wall else 'south'
    return ok_state(f'redeco:{w}_side_table[facing={f},open=false]') or ok_state(f'cluttered:cottage_side_table[facing={f},waterlogged=false]')


def rule_surface(g, name):
    """vaso/relogio/maquina de costura no chao: sobe para um movel vizinho ou ganha mesinha"""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not SURFACE.search(nm(o[0])):
            continue
        if not floor_below(g, y, z, x) or y == 0 and False:
            continue
        fl = g.b(y - 1, z, x) if y > 0 else None
        if fl and OUTDOOR.search(nm(fl)) or not covered(g, y, z, x):
            continue
        if fl and FURN_TOP.search(nm(fl)) and not bid(fl).startswith('minecraft:'):
            continue  # o vaso ja esta sobre um movel: nao cria mesinha em cima do movel
        if fl and re.search(r'_slab\[.*type=top|_stairs\[.*half=top', fl):
            continue  # ja esta em cima de um tampo (mesa de escada/laje de cima): mesinha viraria mesa em cima de mesa
        moved = False
        for d, (dz, dx) in DIRS.items():
            n = g.b(y, z + dz, x + dx)
            if n and len(g.opts(y, z + dz, x + dx)) == 1 and SUPPORT.search(nm(n)) and not NO_TOP.search(nm(n)) \
                    and g.inside(y + 1, z + dz, x + dx) and is_air(g.b(y + 1, z + dz, x + dx)):
                g.copy_cell((y, z, x), (y + 1, z + dz, x + dx))
                g.clear(y, z, x)
                moved = True
                STATS['enfeite_no_movel'] += 1
                break
        if moved or not g.inside(y + 1, z, x) or not is_air(g.b(y + 1, z, x)):
            continue
        wall = next((d for d, (dz, dx) in DIRS.items() if wallish(g.b(y, z + dz, x + dx))), None)
        t = side_table(f'{name}{y}{z}{x}', wall)
        if t:
            g.copy_cell((y, z, x), (y + 1, z, x))
            g.put(y, z, x, t)
            note('enfeite_na_mesinha', g.b(y + 1, z, x))
            STATS['enfeite_na_mesinha'] += 1


def rule_chairs(g):
    """cadeiras em volta da mesma mesa: um tipo so (o da maioria) e viradas para a mesa"""
    seen = set()
    for y, z, x in cells(g):
        if (y, z, x) in seen or not cat_all(g, y, z, x, TABLE):
            continue
        comp, stack = [], [(z, x)]
        seen.add((y, z, x))
        while stack:
            cz, cx = stack.pop()
            comp.append((cz, cx))
            for dz, dx in DIRS.values():
                q = (y, cz + dz, cx + dx)
                if q not in seen and g.inside(*q) and cat_all(g, *q, TABLE):
                    seen.add(q)
                    stack.append(q[1:])
        chairs = {}
        for cz, cx in comp:
            for dz, dx in DIRS.values():
                q = (cz + dz, cx + dx)
                o = g.opts(y, *q)
                if len(o) == 1 and CHAIR.search(nm(o[0])) and not TABLE.search(nm(o[0])) and q not in chairs:
                    chairs[q] = (o[0], (-dz, -dx))  # direcao da cadeira para a mesa
        if not chairs:
            continue
        ids = collections.Counter(bid(s) for s, _ in chairs.values())
        top = max(ids.items(), key=lambda kv: (kv[1], -list(ids).index(kv[0])))[0]
        tpl, tdir = next((s, d) for s, d in chairs.values() if bid(s) == top)
        # convencao do modelo escolhido: aprende com a propria cadeira (facing para a mesa ou o oposto)
        tf = props(tpl).get('facing')
        if tf == DIR_OF[tdir]:
            back = False
        elif tf == OPP.get(DIR_OF[tdir]):
            back = True
        else:
            back = back_is_facing(tpl)
        for (cz, cx), (s, (dz, dx)) in chairs.items():
            toward = DIR_OF[(dz, dx)]
            f = OPP[toward] if back else toward
            want = with_props(tpl, facing=f) if 'facing' in M.valid_props(bid(tpl)) else tpl
            if s != want:
                e = dict(g.entry(y, cz, cx))
                e.pop('char', None)
                e['block'] = want
                g.put_entry(y, cz, cx, e)
                STATS['cadeira_padronizada'] += 1


SHELF_DECOR = ['supplementaries:book_pile', 'cluttered:stack_of_books[facing=F,waterlogged=false]', 'minecraft:potted_fern',
               'minecraft:potted_azalea_bush', 'supplementaries:jar', 'cluttered:two_flower_pots[facing=F,waterlogged=false]',
               'tanukidecor:small_fancy_vase', 'minecraft:potted_red_tulip', 'cluttered:row_of_small_books[facing=F,waterlogged=false]',
               'minecraft:candle[candles=3,lit=false,waterlogged=false]', 'cluttered:small_glass_jars[facing=F,waterlogged=false]']


def full_shelf(s):
    """prateleira com tampo no alto do bloco (another_furniture: px 14-16). A do Candlelight tem a
    tabua embaixo (px 3-5): qualquer coisa em cima dela flutua, entao vira a do another_furniture."""
    if bid(s).startswith('another_furniture:'):
        return s
    f = props(s).get('facing', 'north')
    return shelf_for(wood_of(s), OPP[f]) or s


def shelf_decor(g, y, z, x, name, f):
    for _ in range(3):
        st = ok_state(pick(f'{name}{x}{y}{z}{_}', SHELF_DECOR).replace('=F', '=' + f))
        if st:
            g.put(y, z, x, st)
            STATS['prateleira_enfeitada'] += 1
            return


def rule_shelves(g, name):
    """prateleira baixa so quando sustenta um container (como nas casas importadas) ou serve de
    degrau; o resto vai para o alto da parede e sempre com enfeite em cima."""
    done = set()
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if (y, z, x) in done or len(o) != 1 or not SHELF.search(nm(o[0])) or 'item_shelf' in o[0]:
            continue
        s = o[0]
        f = props(s).get('facing', 'north')
        above = g.b(y + 1, z, x) if g.inside(y + 1, z, x) else None
        support = above and not is_air(above) and not ATTACHED.search(nm(above)) and \
            (furniture(above) or CHEST.search(nm(above)) or re.search(r'barrel|crate|box|vault|casing|sack|bag', nm(above)))
        step = any(g.inside(y + dy, z + dz, x + dx) and SHELF.search(nm(g.b(y + dy, z + dz, x + dx)) or '-')
                   for dy in (-1, 1) for dz, dx in DIRS.values())
        full = full_shelf(s)
        if full != s:
            g.put(y, z, x, full)
            STATS['prateleira_trocada'] += 1
        if support or step:
            continue
        wall = OPP[f]
        dz, dx = DIRS[wall]
        if floor_below(g, y, z, x) and y > 0:
            # no chao: sobe 1 (ou 2) com parede atras e enfeite em cima
            for ty in (y + 1, y + 2):
                if not (g.inside(ty + 1, z, x) and all(is_air(g.b(k, z, x)) for k in range(y + 1, ty + 2))):
                    break
                if not wallish(g.b(ty, z + dz, x + dx)):
                    continue
                g.copy_cell((y, z, x), (ty, z, x))
                g.clear(y, z, x)
                done.add((ty, z, x))
                STATS['prateleira_subiu'] += 1
                shelf_decor(g, ty + 1, z, x, name, f)
                break
            continue
        if above is not None and is_air(above) and covered(g, y + 1, z, x, 4):
            shelf_decor(g, y + 1, z, x, name, f)


SOIL_FARM = rx(r'^farmland$')
SOIL = rx(r'^(farmland|dirt_path|dirt|coarse_dirt|rooted_dirt|mud)$')


def rule_fences(g):
    """cerca de horta encostada na terra arada sobe um bloco; embaixo vira borda de tora"""
    seen = set()
    for y, z, x in cells(g):
        if (y, z, x) in seen or not cat_all(g, y, z, x, FENCE):
            continue
        comp, stack = [], [(z, x)]
        seen.add((y, z, x))
        while stack:
            cz, cx = stack.pop()
            comp.append((cz, cx))
            for dz, dx in DIRS.values():
                q = (y, cz + dz, cx + dx)
                if q not in seen and g.inside(*q) and cat_all(g, *q, FENCE):
                    seen.add(q)
                    stack.append(q[1:])
        # cerca de horta: encosta em terra arada ou no caminho de terra de um canteiro com terra arada
        has_farm = any(cat_any(g, y, zz, xx, SOIL_FARM) for zz in range(g.Z) for xx in range(g.X))
        touches = has_farm and any(cat_any(g, y, cz + dz, cx + dx, SOIL) for cz, cx in comp for dz, dx in DIRS.values())
        if not touches or y + 1 >= g.H:
            continue
        compset = set(comp)
        for cz, cx in comp:
            col = stack_above(g, y + 1, cz, cx)
            col = [y] + col
            top = col[-1] + 1
            if not g.inside(top, cz, cx) or not is_air(g.b(top, cz, cx)):
                if not g.inside(y + 1, cz, cx):
                    continue
                # nao da para subir a pilha: so a cerca sobe se houver ar logo acima
                if not is_air(g.b(y + 1, cz, cx)):
                    border = g.b(y, cz, cx)
                    g.put(y, cz, cx, log_border(border, cz, cx, compset, 'y'))
                    continue
                col = [y]
                top = y + 1
            for yy in reversed(col):
                g.copy_cell((yy, cz, cx), (yy + 1, cz, cx))
            fb = g.b(y, cz, cx)
            ew = (cz, cx - 1) in compset or (cz, cx + 1) in compset
            ns = (cz - 1, cx) in compset or (cz + 1, cx) in compset
            axis = 'x' if ew else ('z' if ns else 'y')
            if re.search(r'fence_gate', bid(fb)):
                g.put(y, cz, cx, 'minecraft:dirt_path')
            else:
                g.put(y, cz, cx, log_border(fb, cz, cx, compset, axis))
        STATS['cerca_de_horta_subiu'] += len(comp)


def log_border(fence, cz, cx, compset, axis):
    w = wood_of(fence, 'spruce')
    return ok_state(f'minecraft:stripped_{w}_log[axis={axis}]') or f'minecraft:stripped_spruce_log[axis={axis}]'


def rule_lamp_posts(g, name, grow):
    """furniture:street_lantern -> Illuminant Column (simplylight:lamp_post bottom/middle/top)"""
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if bid(b) not in ('furniture:street_lantern', 'furniture:plated_street_lantern') or len(g.opts(y, z, x)) != 1:
            continue
        need = [y + 1, y + 2]
        while grow and need[-1] >= g.H:
            g.s.append([[' '] * g.X for _ in range(g.Z)])
            g.H += 1
            g.changed = True
        if all(g.inside(yy, z, x) and is_air(g.b(yy, z, x)) for yy in need):
            g.put(y, z, x, 'simplylight:lamp_post[position=bottom]')
            g.put(y + 1, z, x, 'simplylight:lamp_post[position=middle]')
            g.put(y + 2, z, x, 'simplylight:lamp_post[position=top]')
            STATS['poste_trocado'] += 1


# ---------------------------------------------------------------- uso das partes nos predios
def roof_part_names():
    """sunlit:vila_* parts that hold a building's top (roof) layer"""
    tops = set()
    for p in glob.glob(os.path.join(L.LC, 'buildings', '**', '*.json'), recursive=True):
        d = json.load(open(p, encoding='utf-8'))
        for key in ('parts', 'parts2'):
            for pr in d.get(key, []):
                if pr.get('top'):
                    tops.add(pr['part'])
    return {n for n in tops if n.startswith('sunlit:vila_')}


def ground_ladder_contexts():
    """parte do terreo -> [(maxcellars, parte do porao da mesma casa ou None)], para a regra da escada"""
    ctx = collections.defaultdict(list)
    for p in glob.glob(os.path.join(L.LC, 'buildings', '**', '*.json'), recursive=True):
        d = json.load(open(p, encoding='utf-8'))
        cellars = [pr['part'] for key in ('parts', 'parts2') for pr in d.get(key, []) if pr.get('cellar')]
        cname = cellars[0] if cellars else None
        for key in ('parts', 'parts2'):
            for pr in d.get(key, []):
                if pr.get('ground'):
                    ctx[pr['part']].append((d.get('maxcellars', 0), cname))
    return ctx


def part_roles(store):
    """parte que pode ir num andar acima do terreo (floor>0, top, sem condicao de terreo)"""
    upper, used = set(), set()
    for p in glob.glob(os.path.join(L.LC, 'buildings', '**', '*.json'), recursive=True):
        d = json.load(open(p, encoding='utf-8'))
        for key in ('parts', 'parts2'):
            for pr in d.get(key, []):
                used.add(pr['part'])
                if pr.get('cellar') or pr.get('ground') or pr.get('floor') == 0:
                    continue
                if pr.get('top') or pr.get('floor', 1) > 0 or 'floor' not in pr:
                    upper.add(pr['part'])
    return upper, used


# ---------------------------------------------------------------- moveis de varios blocos (Cluttered)
# O Cluttered monta o movel inteiro no onPlace da parte 1; o Lost Cities grava so o bloco, entao a parte 1
# sozinha ficava "pela metade" e o que estivesse no lugar das outras partes (caixote em cima do armario)
# entrava dentro do modelo. Aqui as partes que faltam sao gravadas (MultiblockPlacer: shape[y][i][0], o passo
# i vai para +x com facing north, -x south, +z east, -z west); sem espaco (ar) ou sem piso embaixo, o movel
# vira a versao de 1 bloco.
MULTIPART = {
    'cluttered:general_store_cabinet': [(1, 0, 2), (0, 1, 3), (1, 1, 4)],
    'cluttered:card_index': [(1, 0, 2), (0, 1, 3), (1, 1, 4)],
    'cluttered:cottage_armchair': [(1, 0, 2)],
    'cluttered:sewing_clutter': [(1, 0, 2)],
    'cluttered:sewing_mannequin': [(0, 1, 2)],
}
MULTIPART_FALLBACK = {
    'cluttered:general_store_cabinet': 'farmersdelight:spruce_cabinet[facing={f},open=false]',
    'cluttered:card_index': 'farmersdelight:spruce_cabinet[facing={f},open=false]',
    'cluttered:cottage_armchair': 'another_furniture:spruce_chair[facing={f},tucked=false,variant=1]',
    'cluttered:sewing_clutter': 'cluttered:scissors_and_thread[facing={f},waterlogged=false]',
}
MP_STEP = {'north': (0, 1), 'south': (0, -1), 'east': (1, 0), 'west': (-1, 0)}  # (dz, dx) por passo i


def is_multipart(s):
    b = bid(s)
    return b in MULTIPART or (b.startswith('cluttered:') and 'part' in (M.REG['blocks'].get(b) or {}))


def mp_fallback(b, f):
    t = MULTIPART_FALLBACK.get(b)
    return ok_state(t.format(f=f)) if t else None


def rule_multiblock(g):
    done = set()
    # partes 1 primeiro: com facing south/west a parte 2 fica antes da 1 na varredura
    order = sorted(cells(g), key=lambda c: props(g.b(*c) or '').get('part', '1') != '1')
    for y, z, x in order:
        if (y, z, x) in done:
            continue
        o = g.opts(y, z, x)
        mp = [s for s in o if s != '?' and is_multipart(s)]
        if not mp:
            continue
        b, p = bid(mp[0]), props(mp[0])
        f = p.get('facing', 'north')
        fb = mp_fallback(b, f)
        if len(o) > 1 or b not in MULTIPART or p.get('part', '1') != '1':
            # sorteio com movel de varias partes, parte solta ou movel sem tabela: vira o de 1 bloco
            g.put(y, z, x, fb) if fb else g.clear(y, z, x)
            STATS['multibloco_trocado'] += 1
            continue
        dz, dx = MP_STEP.get(f, (0, 1))
        cells_ = [(y + dy, z + dz * i, x + dx * i, k) for i, dy, k in MULTIPART[b]]
        base = with_props(mp[0], part='1', facing=f)

        def free(cy, cz, cx, k):
            b2 = g.b(cy, cz, cx)
            return is_air(b2) or (len(g.opts(cy, cz, cx)) == 1 and bid(b2) == b and props(b2).get('part') == str(k)
                                  and props(b2).get('facing') == f)
        ok = all(g.inside(cy, cz, cx) and free(cy, cz, cx, k) for cy, cz, cx, k in cells_)
        ok = ok and all(floor_below(g, cy, cz, cx) for cy, cz, cx, _ in cells_ if cy == y)
        if not ok:
            g.put(y, z, x, fb) if fb else g.clear(y, z, x)
            note('multibloco_sem_espaco', b)
            STATS['multibloco_sem_espaco'] += 1
            continue
        for cy, cz, cx, k in cells_:
            g.put(cy, cz, cx, with_props(base, part=str(k)))
            done.add((cy, cz, cx))
        STATS['multibloco_completo'] += 1


# ---------------------------------------------------------------- comida em cima das mesas das casas
# Display Delight e pratos/bolos/assados de bloco dos mods de comida; sempre o estado "cheio" (servings no
# maximo, bites/cuts 0).
TABLE_FOOD = [
    'displaydelight:plated_hamburger', 'displaydelight:plated_chicken_sandwich', 'displaydelight:plated_egg_sandwich',
    'displaydelight:plated_bacon_sandwich', 'displaydelight:plated_cabbage_rolls',
    'displaydelight:plated_cookie', 'displaydelight:plated_honey_cookie', 'displaydelight:plated_sweet_berry_cookie',
    'displaydelight:plated_dumplings', 'displaydelight:plated_barbecue_stick', 'displaydelight:plated_mutton_wrap',
    'displaydelight:plated_pumpkin_pie', 'displaydelight:plated_salmon_roll', 'displaydelight:plated_cod_roll',
    'displaydelight:plated_stuffed_potato', 'displaydelight:plated_kelp_roll', 'displaydelight:small_plated_apple_pie_slice',
    'displaydelight:small_plated_cake_slice', 'displaydelight:small_plated_chocolate_pie_slice',
    'displaydelight:small_plated_sweet_berry_cheesecake_slice', 'displaydelight:small_plated_cabbage_rolls',
    'farmersdelight:roast_chicken_block', 'farmersdelight:honey_glazed_ham_block', 'farmersdelight:shepherds_pie_block',
    'farmersdelight:stuffed_pumpkin_block', 'farmersdelight:rice_roll_medley_block', 'farmersdelight:apple_pie',
    'farmersdelight:sweet_berry_cheesecake', 'farmersdelight:chocolate_pie', 'farmersdelight:pumpkin_pie',
    'bakery:bread_block', 'bakery:braided_bread_block', 'bakery:baguette_block', 'bakery:strawberry_cake',
    'bakery:chocolate_cake', 'bakery:sweetberry_cake', 'bakery:apple_pie', 'bakery:linzer_tart', 'bakery:chocolate_tart',
    'bakery:strawberry_cupcake_block', 'bakery:waffle_block', 'bakery:toast_block',
    'candlelight:lasagne_block', 'candlelight:beef_wellington_block', 'candlelight:fresh_garden_salad_block',
    'candlelight:tomato_mozzarella_block', 'candlelight:pork_ribs_block',
    'farm_and_charm:farmers_bread_block', 'farm_and_charm:stuffed_chicken_block', 'farm_and_charm:grandmothers_strawberry_cake_block',
    'farm_and_charm:farmers_breakfast_block', 'farm_and_charm:oat_pancake_block', 'farm_and_charm:potato_with_roast_meat_block',
    'hearthandharvest:blueberry_pie', 'hearthandharvest:carrot_cake', 'hearthandharvest:chicken_pot_pie', 'hearthandharvest:raspberry_pie',
    'kaleidoscope_cookery:apple_platter', 'kaleidoscope_cookery:berry_platter', 'kaleidoscope_cookery:watermelon_platter',
    'kaleidoscope_cookery:baozi_plate', 'kaleidoscope_cookery:zongzi_plate', 'kaleidoscope_cookery:stargazy_pie',
    'largemeals:omurice_block', 'largemeals:roasted_mutton_rack_block', 'largemeals:mushroom_pot_pie_block',
    'meadow:cheese_block', 'meadow:cheesecake', 'meadow:cheese_tart', 'meadow:roasted_ham',
    'vintagedelight:meat_pizza', 'brewinandchewin:pizza', 'veggiesdelight:carrot_cake', 'veggiesdelight:sweet_potato_pie',
    'culturaldelights:eggplant_parmesan_block', 'farmersrespite:coffee_cake',
    'youkaishomecoming:red_velvet_cake',
]


def food_state(block, f):
    reg = M.REG['blocks'].get(block)
    if reg is None:
        return None
    p = {}
    for k, vals in reg.items():
        if k == 'facing' and f in vals:
            p[k] = f
        elif k == 'servings':
            p[k] = max(vals, key=int)
        elif k in ('bites', 'cuts', 'age'):
            p[k] = min(vals, key=int)
        elif k in ('stacks', 'stack'):
            p[k] = '2' if '2' in vals else vals[0]
        elif k == 'waterlogged':
            p[k] = 'false'
    return ok_state(M.fmt(block, p))


def rule_table_food(g, name):
    """mesa de casa (de jantar, de centro, de cozinha) com tampo livre ganha comida de bloco em cima"""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not TABLE.search(nm(o[0])) or re.search(r'desk|work|craft|drafting|potion|alchemy', nm(o[0])):
            continue
        if not g.inside(y + 1, z, x) or not is_air(g.b(y + 1, z, x)) or not covered(g, y + 1, z, x):
            continue
        seed = f'{name}|{y}|{z}|{x}'
        if zlib.crc32(('comida' + seed).encode()) % 100 >= 55:
            continue
        st = food_state(pick(seed, TABLE_FOOD), pick(seed + 'f', ('north', 'south', 'east', 'west')))
        if st:
            g.put(y + 1, z, x, st)
            note('comida_na_mesa', st)
            STATS['comida_na_mesa'] += 1


# ---------------------------------------------------------------- convencao das partes de parque
# O Lost Cities poe o gramado do parque na altura da rua e a parte 1 bloco ACIMA. Convencao fixa (validada
# pelo validate.py) para o KubeJS poder baixar tudo 1 bloco sem adivinhar:
# - fatia 0 = CAMADA DO CHAO: so chao (terra, caminho, terra arada, agua, piso cheio, tronco de arvore). Em jogo
#   ela toma o lugar da grama. Laje de baixo/de cima vira laje dupla (meia laje afundava meio bloco no chao).
# - fatia 0 vazia = grama do Lost Cities fica; o que esta acima desce 1 e assenta na grama.
# - objeto na fatia 0 (cerca, banco, flor, poste, feno, caixote, laje decorativa...) sobe 1 com a coluna toda.
PARK_SOIL = rx(r'^(dirt_path|farmland|water|grass_block|dirt|coarse_dirt|rooted_dirt|mud|packed_mud|gravel|moss_block|podzol|'
               r'mycelium|sand|red_sand|clay|snow_block)$')
PARK_NOT_FLOOR = rx(r'hay|bale|crate|sack|bag|pumpkin|melon|lamp|light|barrel|chest|composter|beehive|bee_nest|leaves|hedge|'
                    r'glass|ice$|carpet|target|_log$|_wood$|_stem$|cake|pie|cheese|spawner|bookshelf|jukebox|note_block|tnt|'
                    r'sponge|slime|honey|shroomlight|lantern|furnace|smoker|table|bench|chair|stool|planter|pot$|_box$')
PARK_TREE = rx(r'_log$|_wood$|_stem$')
PARK_CANOPY = rx(r'_log$|_wood$|_stem$|_leaves$|hedge')


def park_cell_kind(g, z, x):
    """'air', 'ground' ou 'object' para a celula da fatia 0"""
    o = [s for s in g.opts(0, z, x) if s != '?']
    if not o or all(is_air(s) for s in o):
        return 'air'
    for s in o:
        n = nm(s)
        if PARK_SOIL.search(n):
            continue
        if PARK_TREE.search(n):
            above = g.b(1, z, x) if g.inside(1, z, x) else None
            if above and PARK_CANOPY.search(nm(above)):
                continue  # tronco de arvore
            return 'object'
        if re.search(r'_slab$', n) and not PARK_NOT_FLOOR.search(n):
            continue
        if solid(s) and not PARK_NOT_FLOOR.search(n):
            continue
        return 'object'
    return 'ground'


def rule_park_ground(g):
    # at most 2 beehives per park; the rest become flowers (a lawn full of hives looked like stray boxes)
    hives = [(y, z, x) for y, z, x in cells(g) if len(g.opts(y, z, x)) == 1 and re.search(r'beehive|bee_nest', nm(g.b(y, z, x)))]
    for i, (y, z, x) in enumerate(sorted(hives)):
        if i >= 2:
            g.put(y, z, x, 'minecraft:poppy')
            STATS['parque_colmeia_virou_flor'] += 1
    for z in range(g.Z):
        for x in range(g.X):
            kind = park_cell_kind(g, z, x)
            if kind == 'ground':
                o = g.opts(0, z, x)
                if len(o) == 1 and re.search(r'_slab\[.*type=(bottom|top)', o[0]):
                    g.put(0, z, x, with_props(o[0], type='double'))
                    STATS['parque_laje_dupla'] += 1
            elif kind == 'object':
                top = g.H - 1
                if not is_air(g.b(top, z, x)):
                    g.s.append([[' '] * g.X for _ in range(g.Z)])
                    g.H += 1
                    g.changed = True
                for y in range(g.H - 1, 0, -1):
                    g.copy_cell((y - 1, z, x), (y, z, x))
                g.clear(0, z, x)
                note('parque_objeto_subiu', g.b(1, z, x))
                STATS['parque_objeto_subiu'] += 1


PARK_HANGING = rx(r'leaves|hedge|lantern|chain|vine|wall_|torch|_sign$|sign$|banner|bars|pane|bell|awning|string|bunting|'
                  r'trapdoor|button|ladder|scaffold|lamp|light|glow|lily_pad|cobweb|rope|flag|pennant')


def park_problems(g):
    """o que fica errado em jogo: objeto na camada do chao ou bloco/grupo solto no ar depois da descida"""
    out = []
    for z in range(g.Z):
        for x in range(g.X):
            if park_cell_kind(g, z, x) == 'object':
                out.append(f'objeto na fatia 0 ({x},{z}): {g.b(0, z, x)}')
    # componentes (6-vizinhanca) de blocos nao pendurados acima da fatia 0; apoiado = toca a fatia 1
    # (assenta na grama ou na camada do chao)
    seen = set()
    for y in range(1, g.H):
        for z in range(g.Z):
            for x in range(g.X):
                if (y, z, x) in seen:
                    continue
                b = g.b(y, z, x)
                if b is None or is_air(b) or b == '?' or PARK_HANGING.search(nm(b)):
                    continue
                comp, stack, ok = [], [(y, z, x)], False
                seen.add((y, z, x))
                while stack:
                    c = stack.pop()
                    comp.append(c)
                    below = g.b(c[0] - 1, c[1], c[2])
                    if c[0] == 1 or (below and not is_air(below) and below != '?' and PARK_HANGING.search(nm(below))):
                        ok = True  # na grama/camada do chao, ou apoiado em folha/poste
                    for dy, dz, dx in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                        n = (c[0] + dy, c[1] + dz, c[2] + dx)
                        if n in seen or n[0] < 1 or not g.inside(*n):
                            continue
                        nb = g.b(*n)
                        if nb is None or is_air(nb) or nb == '?' or PARK_HANGING.search(nm(nb)):
                            continue
                        seen.add(n)
                        stack.append(n)
                if not ok:
                    out.append(f'solto no ar y{comp[0][0]} ({comp[0][2]},{comp[0][1]}): {b} (+{len(comp) - 1})')
    return out


# ---------------------------------------------------------------- portao de cerca alinhado com a cerca
# O portao abre atravessando a linha da cerca: com a cerca correndo em x (vizinhos a leste/oeste) o facing e
# north/south; correndo em z (vizinhos ao norte/sul), east/west. As partes geradas punham facing=north em todos.
GATE = rx(r'fence_gate$')
LINE = rx(r'fence$|fence_gate$|_wall$|hedge$|_post$|bars$|pane$')


def rule_gates(g):
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not GATE.search(nm(o[0])):
            continue
        along_x = sum(1 for dx in (-1, 1) if (b := g.b(y, z, x + dx)) and b != '?' and LINE.search(nm(b)))
        along_z = sum(1 for dz in (-1, 1) if (b := g.b(y, z + dz, x)) and b != '?' and LINE.search(nm(b)))
        if along_x == along_z:
            continue
        f = props(o[0]).get('facing', 'north')
        want = ('north', 'south') if along_x > along_z else ('east', 'west')
        if f not in want:
            g.put(y, z, x, with_props(o[0], facing=want[0]))
            STATS['portao_virado'] += 1


# ---------------------------------------------------------------- chamine de verdade
# Bloco industrial no topo de coluna de alvenaria com ceu aberto = chapeu de chamine do DC:
# vira fogueira acesa (o "dispenser" que parecia entupir a chamine). So com coluna >= 4 embaixo
# para nao pegar bloco industrial decorativo no meio da casa.
CHIMNEY_CAP = rx(r'^industrial')
CHIMNEY_MASONRY = rx(r'bricks|cobblestone|^stone$|terracotta|concrete|basalt|tuff')


def rule_chimney(g):
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not CHIMNEY_CAP.search(nm(o[0])):
            continue
        above = g.b(y + 1, z, x) if g.inside(y + 1, z, x) else None
        if above is not None and not is_air(above):
            continue
        n = 0
        for yy in range(y - 1, max(-1, y - 6), -1):
            b = g.b(yy, z, x)
            if b and solid(b) and CHIMNEY_MASONRY.search(nm(b) or ''):
                n += 1
            else:
                break
        if n < 4:
            continue
        st = ok_state('minecraft:campfire[facing=north,lit=true]')
        if not st:
            continue
        note('chapeu_virou_fogueira', o[0])
        g.put(y, z, x, st)
        STATS['chapeu_virou_fogueira'] += 1


# ---------------------------------------------------------------- nada flutuando
# Vaso/quadro/tapete sem apoio embaixo sai; suporte de ferramenta/armas sem parede atras
# (tool rack no vazio, sword mount solto) gira para a parede oposta ou sai. Escopo estreito
# de proposito: prateleiras e o rule_orient ja cuida (so gira, nunca remove).
FLOAT_NEEDS_BELOW = rx(r'potted_|^flower_pot$|carpet$|moss_carpet$|candle$|paper_pile|_jars$|^jar$|vase$|plate$|'
                       r'cutting_board|chopping_board')
WALL_MOUNT = rx(r'tool_rack|sword_mount')


def rule_stacked_tables(g):
    """mesa com outra mesa logo embaixo: sobra so a de baixo (de cima para baixo, 3 empilhadas ficam so a ultima)"""
    for y in range(g.H - 1, 0, -1):
        for z in range(g.Z):
            for x in range(g.X):
                if 'table' in bid(g.b(y, z, x)) and 'table' in bid(g.b(y - 1, z, x)):
                    note('mesa_empilhada_removida', g.b(y, z, x))
                    g.clear(y, z, x)
                    STATS['mesa_empilhada_removida'] += 1


def ladder_hole(ctxs, cellar_grid, z, x):
    """escada no terreo sem sala de porao embaixo: buraco no chao. ctxs = [(maxcellars, cellar part ou None)]"""
    for mc, cname in ctxs:
        if mc == 0:
            continue
        cg = cellar_grid(cname) if cname else None
        top = cg.b(cg.H - 1, z, x) if cg is not None else None
        if top is not None and (is_air(top) or 'ladder' in nm(top)):
            return False
    return True


def rule_floor_ladder(g, ctxs, cellar_grid):
    """escada na fatia 0 da parte do terreo sem porao debaixo vira piso (o bloco mais comum dos vizinhos)"""
    for z in range(g.Z):
        for x in range(g.X):
            o = g.opts(0, z, x)
            if len(o) != 1 or o[0] == '?' or 'ladder' not in nm(o[0]):
                continue
            if not ladder_hole(ctxs, cellar_grid, z, x):
                continue
            near = collections.Counter()
            for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = g.b(0, z + dz, x + dx)
                if c is None or c == '?' or is_air(c) or 'ladder' in nm(c):
                    continue
                near[bid(c)] += 1
            if not near:
                continue
            note('escada_buraco_trocada', o[0])
            g.put(0, z, x, near.most_common(1)[0][0])
            STATS['escada_buraco_trocada'] += 1


def rule_float(g):
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or o[0] == '?':
            continue
        n = nm(o[0])
        if FLOAT_NEEDS_BELOW.search(n):
            below = g.b(y - 1, z, x) if y > 0 else None
            if below is not None and is_air(below):
                note('flutuante_removido', o[0])
                g.clear(y, z, x)
                STATS['flutuante_removido'] += 1
            continue
        if WALL_MOUNT.search(n):
            w = wall_dir(o[0])
            if not w or w not in DIRS:
                continue
            dz, dx = DIRS[w]
            behind = g.b(y, z + dz, x + dx)
            if wallish(behind):
                continue
            front = g.b(y, z - dz, x - dx)
            if wallish(front):
                _flip_orient(g, y, z, x, o[0])
            else:
                note('parede_sem_apoio', o[0])
                g.clear(y, z, x)
                STATS['parede_sem_apoio'] += 1


# ---------------------------------------------------------------- terra arada sempre plantada
# Horta com buraco na plantacao parecia pela metade: terra arada ao ar livre com ar em cima ganha a colheita
# de um vizinho (a mesma entrada, inclusive lista random) ou batata madura (ano todo; trigo e sazonal e
# mostraria "Cannot grow" fora de estacao). Cebola nunca (so na loja).
BANNED_NAMES = {x.split(':', 1)[-1] for x in IC.BANNED} | set(IC.BANNED)
FARMLAND = rx(r'^farmland$')
CROP = rx(r'^(carrots|potatoes)$|^(cabbages|onions)$|_crop$|^eggplants$|_crops$')  # all-year only (mix.py GROUPS); wheat/beetroots are seasonal, bushes dropped


def rule_windows(g):
    """2026-10-10 (pedido do dono, 3a vez): wall no meio do vidro nunca (montante entre
    dois vidros ou pilar grudado no vidro com ar do outro lado sai); persiana (trapdoor aberta ou
    fechada) de um lado so do vidro e espelhada para o outro lado, mesmo wood/facing/open/half."""
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or not nm(o[0]).endswith('_wall'):
            continue
        for d, (dz, dx) in DIRS.items():
            nb = g.b(y, z + dz, x + dx)
            if nb is None or ('glass' not in (nm(nb) or '') and 'pane' not in (nm(nb) or '')):
                continue
            od = OPP[d]
            odz, odx = DIRS[od]
            other = g.b(y, z + odz, x + odx)
            if other is None:
                continue
            onm = nm(other) or ''
            if 'glass' in onm or 'pane' in onm or is_air(other):
                note('parede_na_janela', o[0])
                g.clear(y, z, x)
                STATS['parede_na_janela'] += 1
                break
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if len(o) != 1 or ('glass' not in (nm(o[0]) or '') and 'pane' not in (nm(o[0]) or '')):
            continue
        for d, opp in (('east', 'west'), ('west', 'east'), ('north', 'south'), ('south', 'north')):
            dz, dx = DIRS[d]
            odz, odx = DIRS[opp]
            a = g.b(y, z + dz, x + dx)
            b = g.b(y, z + odz, x + odx)
            if a is None or b is None:
                continue
            ao = g.opts(y, z + dz, x + dx) if g.inside(y, z + dz, x + dx) else []
            # any shutter trapdoor beside the glass (open or closed) gets its mirror on the other side
            if len(ao) != 1 or not nm(ao[0]).endswith('_trapdoor'):
                continue
            bo = g.opts(y, z + odz, x + odx) if g.inside(y, z + odz, x + odx) else []
            if bo and not all(s == '?' or not nm(s).endswith('_trapdoor') for s in bo):
                continue
            if is_air(b) or 'glass' in (nm(b) or '') or 'pane' in (nm(b) or ''):
                g.put(y, z + odz, x + odx, ao[0])
                STATS['persiana_espelhada'] += 1


def banned(s):
    """crop removido/escondido/quebrado (itemcheck.BANNED): nunca copiado para a horta"""
    return nm(s) in BANNED_NAMES or bid(s) in BANNED_NAMES


def rule_farmland(g):
    for y, z, x in cells(g):
        o = g.opts(y, z, x)
        if not o or not any(FARMLAND.search(nm(s)) for s in o):
            continue
        if not g.inside(y + 1, z, x):
            continue
        above = g.opts(y + 1, z, x)
        if not all(is_air(s) for s in above if s != '?'):
            continue
        if covered(g, y + 1, z, x):
            continue
        src = None
        for r in (1, 2, 3):
            for dz in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if g.inside(y + 1, z + dz, x + dx):
                        n = [s2 for s2 in g.opts(y + 1, z + dz, x + dx) if s2 != '?']
                        if n and all(CROP.search(nm(s2)) and 'onion' not in s2 and not banned(s2) for s2 in n):
                            src = (y + 1, z + dz, x + dx)
                            break
                if src:
                    break
            if src:
                break
        if src:
            g.copy_cell(src, (y + 1, z, x))
        else:
            g.put(y + 1, z, x, 'minecraft:beetroots[age=3]')
        STATS['terra_arada_plantada'] += 1


ROOF_LAYERS = 6


_MISS = object()


class FastGrid(L.Grid):
    """L.Grid com cache por char: uma vez resolvido, o char de paleta sempre aponta para a mesma entrada
    (alloc so cria chars novos), entao b/opts/entry sao iguais aos da classe base, so bem mais rapidos"""

    def __init__(self, store, name, part):
        super().__init__(store, name, part)
        self._bc = {}  # char -> b() resolvido
        self._oc = {}  # char -> opts() resolvido

    def _resolved(self, c):
        e = self.pal.by.get(c) or self.store.common.by.get(c)
        if e is None and c == ' ':
            return {'block': L.AIR}
        return e

    def entry(self, y, z, x):
        if not self.inside(y, z, x):
            return None
        return self._resolved(self.s[y][z][x])

    def opts(self, y, z, x):
        if not (0 <= y < self.H and 0 <= z < self.Z and 0 <= x < self.X):
            return []
        c = self.s[y][z][x]
        o = self._oc.get(c)
        if o is None:
            e = self._resolved(c)
            if e is None:
                return ['?']
            if 'block' in e:
                o = [e['block']]
            elif e.get('blocks'):
                o = [b['block'] for b in e['blocks']]
            else:
                o = ['?']
            self._oc[c] = o
        return list(o)

    def b(self, y, z, x):
        if not (0 <= y < self.H and 0 <= z < self.Z and 0 <= x < self.X):
            return None
        c = self.s[y][z][x]
        r = self._bc.get(c, _MISS)
        if r is _MISS:
            o = self.opts(y, z, x)
            r = o[0] if o else None
            if self._resolved(c) is not None:
                self._bc[c] = r  # '?' de char nao resolvido nao entra no cache
        return r


class RoofGuard(FastGrid):
    """Top part of a vila: refuses edits on exposed roof stairs/slabs in the top layers."""

    def put(self, y, z, x, block, loot=None):
        if y >= self.H - ROOF_LAYERS:
            cur = self.b(y, z, x)
            roof = ('_stairs' in cur or '_slab' in cur) and (y == self.H - 1 or is_air(self.b(y + 1, z, x)))
            if roof and cur != block:
                return
        return super().put(y, z, x, block, loot)


GROUND_RX = re.compile(r'^(grass_block|dirt|coarse_dirt|podzol|rooted_dirt|mud)$')
CONT_RX = re.compile(r'chest|barrel|crate')
PLANT_RX = re.compile(r'potted|flower_pot|fern|grass|dead_bush|tulip|poppy|orchid|allium|dandelion|lily|sapling|'
                      r'sunflower|lilac|peony|rose_bush|cornflower|azure|oxeye|mushroom|bamboo')


def is_clutter(s):
    """container ou planta que nao deve ficar em caminho"""
    if not s or s == '?':
        return False
    n = nm(s)
    if CONT_RX.search(n):
        return True
    return bool(PLANT_RX.search(n)) and not n.endswith('_block') and not re.search(r'stairs|slab|fence|wall', n)


def stair_front_back(b, z, x):
    """(low, tall) cells de uma escada: facing aponta para o lado alto (costas); o degrau baixo fica do lado oposto"""
    m = re.search(r'facing=(\w+)', b or '')
    if not m or m.group(1) not in DIRS:
        return None
    dz, dx = DIRS[m.group(1)]
    return (z - dz, x - dx), (z + dz, x + dx)


def _passable(s):
    return s is not None and s != '?' and (is_air(s) or bool(THIN.search(nm(s))))


def _floor_under(s):
    return s is not None and (solid(s) or bool(re.search(r'_slab\[.*type=(double|top)|_stairs', s)))


def walk_strict(g, y, z, x):
    """andavel sem contar 'fora da parte' como chao (usado para escadas soltas)"""
    b = g.b(y, z, x)
    if b is None:
        return False
    if b == '?' or re.search(r'_stairs|_slab|ladder|_door', nm(b)):
        return True
    return _passable(b) and y > 0 and _floor_under(g.b(y - 1, z, x))


def _floor(g, y, z, x):
    """celula de piso andavel; no terreo o ar conta como chao"""
    if not _passable(g.b(y, z, x)):
        return False
    return y == 0 or _floor_under(g.b(y - 1, z, x))


def walkway_cells(g):
    """caminhos: vizinhos de porta, paisagens de escada, e passagens de 1 bloco de largura"""
    W = set()
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if not b or b == '?':
            continue
        if '_door' in nm(b) and 'trapdoor' not in nm(b):
            for dz, dx in DIRS.values():
                W.add((y, z + dz, x + dx))
        if '_stairs' in nm(b):
            fb = stair_front_back(b, z, x)
            if fb:
                (fz, fx), (bz, bx) = fb
                W.update({(y, fz, fx), (y - 1, fz, fx), (y + 1, bz, bx), (y, bz, bx)})
    for y, z, x in cells(g):
        if not _floor(g, y, z, x):
            continue
        if (wallish(g.b(y, z - 1, x)) and wallish(g.b(y, z + 1, x))) or \
           (wallish(g.b(y, z, x - 1)) and wallish(g.b(y, z, x + 1))):
            W.add((y, z, x))
    return W


def rule_dangling_stairs(g):
    """escada solta (half=bottom, y<=2). Caso A interior: degrau baixo e ar sem chao, lado alto sem andar.
    Caso B borda: y==2 e o degrau baixo cai para fora da parte (rua). Pula fileiras de mesma facing (beirais)"""
    for y, z, x in cells(g):
        if y > 2:
            continue
        b = g.b(y, z, x)
        if not b or b == '?' or '_stairs' not in nm(b) or 'half=bottom' not in b:
            continue
        fb = stair_front_back(b, z, x)
        if not fb:
            continue
        facing = re.search(r'facing=(\w+)', b).group(1)
        if any(re.search(r'facing=(\w+)', g.b(y, zz, xx) or '') and
               re.search(r'facing=(\w+)', g.b(y, zz, xx)).group(1) == facing and '_stairs' in nm(g.b(y, zz, xx))
               for zz, xx in ((z + dz, x + dx) for dz, dx in DIRS.values()) if g.inside(y, zz, xx)):
            continue  # fileira de escadas (beiral/decoracao)
        (lz, lx), (tz, tx) = fb
        case = None
        if y == 2 and not g.inside(y, lz, lx):
            case = 'B'  # degrau baixo fora da parte: queda para a rua
        elif 1 <= y <= 2 and g.inside(y, lz, lx) and g.inside(y - 1, lz, lx):
            low = g.b(y, lz, lx)
            if (not is_air(g.b(y + 1, z, x)) if g.inside(y + 1, z, x) else True):
                continue  # algo em cima: estrutural
            if low is None or low == '?' or not is_air(low):
                continue  # lado baixo nao e ar (folhas, solido): nao mexe
            under = g.b(y - 1, lz, lx)
            if under is None or under == '?' or _floor_under(under):
                continue
            if any(walk_strict(g, yy, tz, tx) for yy in (y, y + 1) if g.inside(yy, tz, tx)):
                continue  # o lado alto leva a um andar, porta ou chao
            case = 'A'
        if not case:
            continue
        note('escada_solta_removida', b)
        g.put(y, z, x, L.AIR)
        STATS['escada_solta_removida'] += 1
        STATS['escada_solta_' + case] += 1


POST_RX = re.compile(r'(log|wood|stem|hyphae)$')


def is_post(s):
    """pilar de madeira (tora, madeira, caule, hifa) que segura as escadas do anel"""
    return bool(s) and s != '?' and bool(POST_RX.search(nm(s)))


def rule_post_stairs(g):
    """escada encostada num pilar, virada para ele: no pe do pilar fica half=bottom e no topo (capitel) half=top,
    para o anel nao sair misturado no jogo. So muda half; facing, shape e waterlogged ficam"""
    for y, z, x in cells(g):
        b = g.b(y, z, x)
        if not b or b == '?' or '_stairs' not in nm(b) or 'half=' not in b:
            continue
        fb = stair_front_back(b, z, x)
        if not fb or not is_post(g.b(y, fb[1][0], fb[1][1])):
            continue
        pz, px = fb[1]
        if not is_post(g.b(y - 1, pz, px)):
            want = 'bottom'  # pe do pilar
        elif not is_post(g.b(y + 1, pz, px)):
            want = 'top'  # topo do pilar
        else:
            continue
        if props(b).get('half') == want or 'block' not in (g.entry(y, z, x) or {}):
            continue  # ja certo, ou celula com variantes sorteadas (nao mexe)
        g.put(y, z, x, with_props(b, half=want))
        STATS['escada_pilar_normalizada'] += 1


def rule_buried_fences(g):
    """cerca com bloco de terra/grama logo acima vira esse bloco (cerca enterrada)"""
    for y in range(g.H - 1):
        for z, x in ((z, x) for z in range(g.Z) for x in range(g.X)):
            b = g.b(y, z, x)
            if not b or b == '?' or not nm(b).endswith('_fence'):
                continue
            up = g.b(y + 1, z, x)
            if up and up != '?' and GROUND_RX.match(nm(up)):
                note('cerca_enterrada', b)
                g.put(y, z, x, up)
                STATS['cerca_enterrada'] += 1


def rule_floor_holes(g):
    """buraco no piso de casa (ar ou grama) com o mesmo piso em 3 lados vira piso"""
    for y in range(g.H):
        for z, x in ((z, x) for z in range(g.Z) for x in range(g.X)):
            b = g.b(y, z, x)
            if not b or b == '?' or not (is_air(b) or re.search(r'short_grass|tall_grass|^grass$', nm(b))):
                continue
            vert = [g.b(yy, z, x) for yy in (y - 1, y + 1)]
            if any(v and v != '?' and re.search(r'ladder|_stairs', nm(v)) for v in vert):
                continue
            if not covered(g, y, z, x, up=4):
                continue
            full, cnt = {}, collections.Counter()
            for dz, dx in DIRS.values():
                c = g.b(y, z + dz, x + dx)
                if c and c != '?' and solid(c):
                    cnt[bid(c)] += 1
                    full.setdefault(bid(c), c)
            if not cnt:
                continue
            key, n = cnt.most_common(1)[0]
            if n < 3:
                continue
            note('buraco_piso_preenchido', full[key])
            g.put(y, z, x, full[key])
            STATS['buraco_piso_preenchido'] += 1


def rule_walkway_clutter(g):
    """container e planta fora de caminho: vai para parede livre da mesma sala (ate 6 blocos) ou some"""
    W = walkway_cells(g)
    for y, z, x in sorted(W):
        if not g.inside(y, z, x):
            continue
        b = g.b(y, z, x)
        if not is_clutter(b):
            continue
        best, best_key = None, None
        for yy, zz, xx in ((y, zz, xx) for zz in range(z - 6, z + 7) for xx in range(x - 6, x + 7)):
            if (yy, zz, xx) in W or not g.inside(yy, zz, xx) or yy != y:
                continue
            if not is_air(g.b(yy, zz, xx)) or not _floor(g, yy, zz, xx):
                continue
            walls = sum(1 for dz, dx in DIRS.values() if wallish(g.b(yy, zz + dz, xx + dx)))
            if walls < 1:
                continue
            key = (-walls, abs(zz - z) + abs(xx - x))
            if best_key is None or key < best_key:
                best, best_key = (yy, zz, xx), key
        if best:
            note('caminho_limpo_movido', b)
            g.copy_cell((y, z, x), best)
            g.clear(y, z, x)
            STATS['caminho_limpo_movido'] += 1
        else:
            note('caminho_limpo_removido', b)
            g.clear(y, z, x)
            STATS['caminho_limpo_removido'] += 1



# decoracao pequena que pode ficar sobre um movel (planta, pote, vela, lampiao, livro...)
DECOR_RX = re.compile(PLANT_RX.pattern + r'|jar|candle|lantern|lamp|book')


def fix_cross_floor_furniture(lc_dir):
    """Remove moveis empilhados entre andares. Se a fatia de cima de uma parte tem movel em (x,z) e a fatia 0
    da parte seguinte do predio tem movel no mesmo (x,z), o movel de cima sai, junto com a decoracao pequena
    da fatia 1 nessa coluna. As decisoes usam os dados originais (snapshot), entao uma parte compartilhada
    entre predios recebe a uniao das remocoes, e cada parte e gravada uma unica vez."""
    def part_file(name):
        return os.path.join(lc_dir, 'parts', name.split(':', 1)[-1] + '.json')

    parts, palettes = {}, {}

    def load_part(name):
        if name not in parts:
            pp = part_file(name)
            parts[name] = json.load(open(pp, encoding='utf-8')) if os.path.exists(pp) else None
        return parts[name]

    def load_palette(name, part):
        # a paleta da parte e a do refpalette; sem refpalette, a de mesmo nome (como o cross.py)
        ref = part.get('refpalette', name).split(':', 1)[-1]
        if ref not in palettes:
            pl = os.path.join(lc_dir, 'palettes', ref + '.json')
            if not os.path.exists(pl):
                palettes[ref] = None
            else:
                blocks, air = {}, ' '
                for e in json.load(open(pl, encoding='utf-8'))['palette']:
                    blk = e.get('block') or (e['blocks'][0]['block'] if e.get('blocks') else '')
                    blocks[e['char']] = blk
                    if blk == 'minecraft:air':
                        air = e['char']
                palettes[ref] = (blocks, air)
        return palettes[ref]

    def ch_at(sl, y, z, x):
        if 0 <= y < len(sl) and z < len(sl[y]) and x < len(sl[y][z]):
            return sl[y][z][x]
        return ' '

    def block_of(blocks, ch):
        return blocks.get(ch, '') if ch != ' ' else ''

    def is_furn(blk):
        return bool(blk) and not blk.startswith('minecraft:') and bool(FURN_TOP.search(nm(blk)))

    # 1) decisao: tudo sobre os dados originais
    remove, decor = collections.defaultdict(set), collections.defaultdict(set)
    for path in glob.glob(os.path.join(lc_dir, 'buildings', '**', '*.json'), recursive=True):
        bld = json.load(open(path, encoding='utf-8'))
        names = [q['part'] for q in bld.get('parts', []) if 'part' in q]
        for lo, hi in zip(names, names[1:]):
            pl, ph = load_part(lo), load_part(hi)
            if not pl or not ph or not pl.get('slices') or not ph.get('slices'):
                continue
            cl, chh = load_palette(lo, pl), load_palette(hi, ph)
            if cl is None or chh is None:
                continue
            sl, sh = pl['slices'], ph['slices']
            top = len(sl) - 1
            for z in range(len(sh[0])):
                for x in range(len(sh[0][z])):
                    if not is_furn(block_of(chh[0], ch_at(sh, 0, z, x))):
                        continue
                    if not is_furn(block_of(cl[0], ch_at(sl, top, z, x))):
                        continue
                    remove[hi].add((0, z, x))
                    dblk = block_of(chh[0], ch_at(sh, 1, z, x))
                    if dblk and DECOR_RX.search(nm(dblk)):
                        decor[hi].add((1, z, x))

    # 2) aplica nas partes de cima e grava cada uma uma vez
    n_furn = n_decor = 0
    changed = []
    for name in sorted(set(remove) | set(decor)):
        part = parts[name]
        blocks, air = load_palette(name, part)
        # cada linha da fatia e uma string de x caracteres: troca o caractere (x) por string
        for y, z, x in remove.get(name, ()):
            row = part['slices'][y][z]
            part['slices'][y][z] = row[:x] + air + row[x + 1:]
            n_furn += 1
        for y, z, x in decor.get(name, ()):
            row = part['slices'][y][z]
            part['slices'][y][z] = row[:x] + air + row[x + 1:]
            n_decor += 1
        changed.append(name)
    for name in changed:
        with open(part_file(name), 'w', encoding='utf-8') as f:
            json.dump(parts[name], f)
    STATS['movel_entre_andares_removido'] += n_furn
    STATS['movel_entre_andares_decor_removido'] += n_decor
    print(f'moveis entre andares: {n_furn} moveis e {n_decor} decoracoes removidos em {len(changed)} partes')
    return n_furn


def main():
    store = L.Store()
    upper, used = part_roles(store)
    roof_parts = roof_part_names()
    ladder_ctx = ground_ladder_contexts()
    cellar_cache = {}

    def cellar_grid(cname):
        if cname not in cellar_cache:
            cellar_cache[cname] = FastGrid(store, cname, store.parts[cname][1]) if cname in store.parts else None
        return cellar_cache[cname]
    fix_loot(store)
    axis_fix = axis_unrotated(store)
    changed = 0
    pending = []
    for name, (path, part) in store.parts.items():
        g = RoofGuard(store, name, part) if name in roof_parts else FastGrid(store, name, part)
        if not g.H:
            continue
        building = name in used
        outdoor = re.match(r'sunlit:(parks|fountains)/', name) is not None
        if name in axis_fix:
            rule_rotated_axis(g)
        rule_junk(g)
        rule_multiblock(g)
        rule_gates(g)
        rule_chests(g)
        rule_fridges(g)
        rule_bath(g)
        rule_orient(g)
        rule_doors(g)
        rule_door_visible(g)
        rule_hedge_links(g)
        rule_hood(g)
        rule_floor_only(g)
        rule_no_top(g)
        schem_house = name.startswith('sunlit:vila_')
        if not schem_house:
            rule_leaves(g, name in upper)
        rule_lanterns(g)
        rule_dark_parts(g, name)
        if building:
            rule_surface(g, name)
            rule_chairs(g)
            rule_shelves(g, name)
            rule_table_food(g, name)
        if not schem_house and not outdoor:
            # parques: o KubeJS afunda caminho/terra arada para a camada do gramado, a cerca fica na altura certa
            rule_fences(g)
        rule_lamp_posts(g, name, grow=outdoor)
        rule_farmland(g)
        rule_windows(g)
        rule_chimney(g)
        rule_float(g)
        rule_stacked_tables(g)
        if building:
            rule_dangling_stairs(g)
            rule_post_stairs(g)
            rule_buried_fences(g)
            rule_floor_holes(g)
            rule_walkway_clutter(g)
        if name in ladder_ctx:
            rule_floor_ladder(g, ladder_ctx[name], cellar_grid)
        rule_loot_cap(g, outdoor)
        if name.startswith('sunlit:parks/'):
            rule_park_ground(g)
        if name in RETOUCH:
            RETOUCH[name](g)  # last: sees the final layers (park ground already normalized)
        if g.commit():
            pending.append((path, part))
            changed += 1
    # every part palette is loaded now (the call at the top only saw sunlit:common): drop loot from blocks that
    # cannot hold it, or Lost Cities logs "Error setting loot" for each one
    fix_loot(store)
    n = store.save()
    # palettes are saved before parts so a crash never leaves parts referencing chars that were not saved
    for path, part in pending:
        json.dump(part, open(path, 'w', encoding='utf-8'))
    print(f'polish: {changed} partes e {n} paletas regravadas')
    for k, v in sorted(STATS.items()):
        print(f'  {k}: {v}')
    if '--detalhe' in sys.argv:
        for k, v in DETAIL.most_common(120):
            print(v, *k)


if __name__ == '__main__':
    main()
