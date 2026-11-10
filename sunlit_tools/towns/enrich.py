"""Enche cantos internos dos comodos com decoracao tematica (muito Create), sem bloquear passagens.

Celula elegivel: piso andavel interno (grama/terra/laje = lado de fora), canto de comodo com
duas paredes adjacentes e area livre 2x2 para dentro, e a colocacao nao pode separar o piso
da camada em mais ilhas (nunca fecha corredor ou passagem). Nada perto de portas,
escadas, escadas de mao, camas ou alcapoes, e nunca no meio de corredor de 1 bloco.
"""
import random, re
import mapping as M

OUTDOOR = re.compile(r'grass|dirt|path|sand|gravel|farmland|water|leaves|snow|moss|podzol|mud$|clay$|hedge|carpet|_slab\[type=bottom|_slab$')
NOT_WALL = re.compile(r'air|door|trapdoor|stairs|ladder|fence|gate|pane|bars|glass|torch|lantern|button|plate|rail|vine|carpet|'
                      r'slab|chain|sign|banner|flower|sapling|grass|bed|rod|candle|scaffold')
AVOID = re.compile(r'door|stairs|ladder|trapdoor|_bed|scaffold|fence_gate|vertical_slab|chest|toilet|bidet|bath|shower|sink|basin')

FLOOR_NS = {'minecraft', 'create', 'quark', 'twigs'}
FURNITURE = re.compile(r'depot|basin|casing|tank|vault|toolbox|table|counter|cabinet|drawer|desk|shelf|barrel|chest|crate|'
                       r'anvil|furnace|smoker|composter|bookshelf|lectern|jukebox|note_block|seat|pot|millstone|gearbox|press|'
                       r'toilet|bidet|bath|shower|sink|washing_machine|urinal')
COLORS = ['red', 'blue', 'green', 'yellow', 'white', 'light_gray', 'brown', 'cyan']
DECOR = {
    'home': ['minecraft:potted_fern', 'minecraft:potted_azalea_bush', 'minecraft:potted_flowering_azalea_bush',
             'minecraft:potted_red_tulip', 'minecraft:potted_cornflower', 'create:cuckoo_clock[facing=F]', 'minecraft:barrel[facing=up]',
             'cluttered:stack_of_books[facing=F]', 'cluttered:basket_of_flowers[facing=F]', 'cluttered:two_flower_pots[facing=F]',
             'tanukidecor:classic_vase', 'tanukidecor:small_fancy_vase', 'refurbished_furniture:oak_storage_jar[facing=F]',
             'create:C_seat', 'create:C_toolbox[facing=F]', 'minecraft:lantern', 'furniture:wooden_planter',
             'minecraft:bookshelf', 'supplementaries:book_pile', 'farmersdelight:wooden_basket[facing=up]'],
    'workshop': ['create:depot', 'create:basin', 'create:fluid_tank', 'create:andesite_casing', 'create:brass_casing',
                 'create:C_toolbox[facing=F]', 'create:gearbox', 'create:millstone', 'create:item_drain', 'create:cogwheel[axis=y]',
                 'create:encased_fan[facing=up]', 'create:schematic_table[facing=F]', 'minecraft:barrel[facing=up]',
                 'minecraft:smithing_table', 'minecraft:anvil[facing=F]', 'create:cuckoo_clock[facing=F]', 'create:copper_casing'],
    'shop': ['minecraft:barrel[facing=up]', 'culturaldelights:eggplant_crate', 'hearthandharvest:raspberry_crate', 'vintagedelight:cucumber_crate',
             'vintagedelight:peanut_crate', 'minecraft:melon', 'minecraft:pumpkin', 'minecraft:potted_fern', 'refurbished_furniture:recycle_bin',
             'create:depot', 'farmersdelight:wooden_basket[facing=up]', 'minecraft:potted_azalea_bush', 'create:cuckoo_clock[facing=F]'],
    'office': ['minecraft:potted_fern', 'minecraft:potted_azalea_bush', 'cluttered:paper_pile[facing=F]', 'supplementaries:book_pile',
               'minecraft:bookshelf', 'refurbished_furniture:recycle_bin', 'supplementaries:globe[facing=F]', 'create:cuckoo_clock[facing=F]',
               'cluttered:office_supplies_a[facing=F]', 'create:depot', 'minecraft:lantern'],
    'farm': ['minecraft:barrel[facing=up]', 'minecraft:hay_block[axis=y]', 'minecraft:composter', 'farmersdelight:wooden_basket[facing=up]',
             'culturaldelights:eggplant_crate', 'minecraft:pumpkin', 'create:C_toolbox[facing=F]', 'minecraft:potted_fern'],
}
THEME_GROUP = {'workshop': 'workshop', 'garage': 'workshop', 'grocery': 'shop', 'cafe': 'shop', 'restaurant': 'shop', 'sushi': 'shop',
               'bakery': 'shop', 'flowers': 'shop', 'clothing': 'shop', 'office': 'office', 'bank': 'office', 'school': 'office',
               'clinic': 'office', 'farm': 'farm', 'camp': 'farm'}
FACE_AWAY = {(0, -1): 'south', (0, 1): 'north', (-1, 0): 'east', (1, 0): 'west'}  # parede ao norte -> virado ao sul
CHAR_POOL = [c for c in '¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ']


class PaletteState:
    def __init__(self, entries):
        self.entries = entries
        self.by_char = {e['char']: e for e in entries}
        self.decor = {}

    def char_for(self, state, loot):
        if state in self.decor:
            return self.decor[state]
        free = [c for c in CHAR_POOL if c not in self.by_char]
        if not free:
            return None
        c = free[0]
        e = {'char': c, 'block': state}
        if loot:
            e['loot'] = loot
        self.entries.append(e); self.by_char[c] = e; self.decor[state] = c
        return c


def block_of(ps, common, ch):
    e = ps.by_char.get(ch) or common.get(ch)
    if not e:
        return None
    if 'block' in e:
        return e['block']
    if e.get('blocks'):
        return e['blocks'][0]['block']
    return None


def is_air(b):
    return b is None or b.startswith('minecraft:air')


def solid(b):
    return b is not None and not NOT_WALL.search(b.split(':')[1])


def resolve(tpl, facing, rnd):
    s = tpl.replace('C_', rnd.choice(COLORS) + '_').replace('=F', '=' + facing)
    bid, props = M.parse(s)
    if not M.exists(bid):
        return None
    return M.fmt(bid, M.clean_props(bid, props))


def components(walk):
    """numero de ilhas de piso andavel (vizinhanca 4)"""
    seen, n = set(), 0
    for start in walk:
        if start in seen:
            continue
        n += 1
        stack = [start]; seen.add(start)
        while stack:
            x, z = stack.pop()
            for dx, dz in FACE_AWAY:
                q = (x + dx, z + dz)
                if q in walk and q not in seen:
                    seen.add(q); stack.append(q)
    return n


def enrich(part, ps, common, theme, seed, lootable):
    group = THEME_GROUP.get(theme, 'home')
    rnd = random.Random(seed)
    sl = [[list(r) for r in s] for s in part['slices']]
    H, Z, X = len(sl), part['zsize'], part['xsize']
    B = lambda y, z, x: block_of(ps, common, sl[y][z][x]) if 0 <= y < H and 0 <= z < Z and 0 <= x < X else None
    placed = 0
    for y in range(1, H - 1):
        # piso andavel desta camada: ar nos pes e na cabeca, algo firme embaixo
        walk = set()
        for z in range(Z):
            for x in range(X):
                f = B(y - 1, z, x)
                if is_air(B(y, z, x)) and is_air(B(y + 1, z, x)) and f and not is_air(f) and 'water' not in f:
                    walk.add((x, z))
        base = components(walk)
        for (x, z) in sorted(walk):
            if (x, z) not in walk or not (1 <= x < X - 1 and 1 <= z < Z - 1):
                continue
            floor = B(y - 1, z, x)
            if OUTDOOR.search(floor.split(':')[1]) or not solid(floor):
                continue
            if floor.split(':')[0] not in FLOOR_NS or sl[y - 1][z][x] in ps.decor.values() or FURNITURE.search(floor):
                continue  # so piso de construcao; nada empilhado em movel ou decoracao
            near = [B(y + dy, z + dz, x + dx) for dy in (0, 1) for dz in range(-2, 3) for dx in range(-2, 3)]
            if any(b and AVOID.search(b) for b in near):
                continue  # longe de portas, escadas, camas
            walls = [d for d in FACE_AWAY if solid(B(y, z + d[1], x + d[0]))]
            blocked = [d for d in FACE_AWAY if (x + d[0], z + d[1]) not in walk]
            # so canto de comodo: duas paredes adjacentes e area livre 2x2 do lado de dentro
            if len(blocked) != 2 or not walls or blocked[0][0] == -blocked[1][0] and blocked[0][1] == -blocked[1][1]:
                continue
            ox, oz = -(blocked[0][0] + blocked[1][0]), -(blocked[0][1] + blocked[1][1])
            if not {(x + ox, z), (x, z + oz), (x + ox, z + oz)} <= walk:
                continue
            if rnd.random() > 0.15:
                continue
            walk.discard((x, z))
            if components(walk) != base:
                walk.add((x, z)); continue  # fecharia uma passagem
            state = resolve(rnd.choice(DECOR[group]), FACE_AWAY[walls[0]], rnd)
            if not state:
                walk.add((x, z)); continue
            bid = state.split('[')[0]
            ch = ps.char_for(state, f'sunlit:{theme}' if lootable.match(bid) else None)
            if not ch:
                walk.add((x, z)); break
            sl[y][z][x] = ch
            placed += 1
    part['slices'] = [[''.join(r) for r in s] for s in sl]
    return placed
