"""Moveis "de vanilla" dos schematics -> moveis dos mods do pack, e cômodos vazios mobiliados.

Os schematics de casas trazem moveis montados com blocos vanilla: fornalha/defumador como
fogao, caldeirao com gancho de armadilha como pia, bloco de ferro/concreto branco com botao
como geladeira, escada com alcapao do lado como cadeira/sofa, cerca com placa de pressao como
mesa, funil como privada. Aqui cada padrao vira o movel de mod equivalente, com o facing pela
convencao de cada mod (interior.facing_for: refurbished = costas, resto = frente).

Comodos que ficam vazios (muitas casas so tem a casca) ganham mobilia pelo tema do comodo
(sala, cozinha, quarto, banheiro, sotao), sempre encostada em parede, longe de portas e escadas.

Grade: Vox.g[y][z][x], x = leste, z = sul. Tudo aqui roda ANTES da rotacao das variantes.
"""
import collections
import re
import zlib

import interior as I
from loot import LANG
import mapping as M

AIR = 'minecraft:air'
DIRS = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}
OPP = I.OPP
WOODS = ['dark_oak', 'oak', 'spruce', 'birch', 'jungle', 'acacia', 'mangrove', 'cherry']


def bid(s):
    return s.split('[', 1)[0]


def nm(s):
    return bid(s).split(':', 1)[-1]


def props(s):
    return M.parse(s)[1]


def rx(p):
    return re.compile(p)


# ---------------------------------------------------------------- classes de bloco (pelo nome sem namespace)
PASSABLE = rx(r'^(air|cave_air|void_air|light|\w*carpet|\w+_pressure_plate|grass|short_grass|tall_grass|fern|large_fern|'
              r'dandelion|poppy|\w+_tulip|allium|azure_bluet|oxeye_daisy|cornflower|lily_of_the_valley|blue_orchid|'
              r'wither_rose|pink_petals|snow|rail|powered_rail|detector_rail|activator_rail|redstone_wire|tripwire|'
              r'\w+_button|torch|wall_torch|soul_torch|soul_wall_torch|redstone_torch|redstone_wall_torch|lever|vine|'
              r'glow_lichen|dead_bush|\w+_sapling|sweet_berry_bush|seagrass)$')
LEAFY = rx(r'leaves$|^vine$|^azalea$|^flowering_azalea$')
NOT_FLOOR = rx(r'(_fence|_fence_gate|_wall|_pane|^iron_bars|_trapdoor|_door|leaves|lantern|chain|_sign|_banner|'
               r'flower_pot|^potted_|campfire|ladder|scaffolding|_bed$|^bell$|candle)')
FURNACE = rx(r'^(furnace|smoker|blast_furnace)$')
WORKSHOP = rx(r'^(anvil|chipped_anvil|damaged_anvil|smithing_table|grindstone|stonecutter|fletching_table|cartography_table|loom)$')
CAULDRON = rx(r'^(cauldron|water_cauldron)$')
FRIDGE_MAT = rx(r'^(iron_block|white_concrete|light_gray_concrete|quartz_block|smooth_quartz|snow_block|white_glazed_terracotta|'
                r'light_gray_glazed_terracotta|calcite|polished_diorite)$')
HANDLE = rx(r'(_button|^lever|^tripwire_hook|^iron_trapdoor)$')
COUNTER_MAT = rx(r'(_concrete$|^polished_|^smooth_(stone|quartz|sandstone|basalt)$|^quartz_(block|bricks)$|^calcite$|'
                 r'^stripped_\w+_wood$|^chiseled_bookshelf$|^barrel$|^(deepslate|stone|polished_blackstone)_bricks$|'
                 r'^\w+_planks$|_glazed_terracotta$|^dark_prismarine$|^mud_bricks$|^bricks$)')
TABLE_LEG = rx(r'(_fence$|_wall$|^iron_bars$|^chain$|^end_rod$|^lightning_rod$)')
TABLE_TOP = rx(r'(_pressure_plate$|carpet$|_slab$|_trapdoor$)')
SEAT_SIDE = rx(r'(_trapdoor$|_wall_sign$|_sign$|_fence_gate$|_button$)')
LIGHT = rx(r'(lantern|torch|glowstone|sea_lantern|froglight|shroomlight|campfire|candle|lamp|_light$|end_rod|sconce|beacon|'
           r'jack_o_lantern|redstone_lamp|chandelier|lantern)')
FURN = rx(r'^(?!minecraft:).+|^minecraft:(chest|trapped_chest|barrel|bookshelf|chiseled_bookshelf|crafting_table|furnace|smoker|'
          r'blast_furnace|anvil|loom|lectern|\w+_bed|brewing_stand|cauldron|water_cauldron|composter|smithing_table|'
          r'cartography_table|fletching_table|grindstone|stonecutter|jukebox|enchanting_table|note_block|\w+_banner|'
          r'decorated_pot|flower_pot|potted_\w+|\w+_shulker_box|ender_chest)$')
CONTAINER = rx(r'^minecraft:(chest|trapped_chest|barrel)$|cabinet|drawer|crate|fridge|freezer|storage|kitchen_cabinetry|'
               r'_sink$|basin|toilet|desk$|wardrobe|dresser|bookcase')
KITCHEN_BASE = rx(r'^refurbished_furniture:\w+_kitchen_(cabinetry|drawer|sink)$|^farmersdelight:stove$')
COUNTER_DECOR = ['displaydelight:plated_cookie[facing={f},stacks=2]', 'displaydelight:small_plated_cake_slice[facing={f}]',
                 'displaydelight:small_plated_apple_pie_slice[facing={f}]', 'displaydelight:plated_dumplings[facing={f},stacks=1]',
                 'cluttered:jam_jars[facing={f},stacked=false]', 'cluttered:small_spice_jars[facing={f}]',
                 'cluttered:sliced_bread[facing={f},waterlogged=false]', 'cluttered:pastry_plate[facing={f},waterlogged=false]',
                 'cluttered:assorted_glass_jars[facing={f},waterlogged=false]', 'farmersdelight:cutting_board[facing={f}]',
                 'refurbished_furniture:{w}_cutting_board[facing={f}]', 'refurbished_furniture:light_toaster[facing={f},powered=false]',
                 'kaleidoscope_cookery:apple_platter[facing={f},servings=4]', 'cluttered:basket_of_produce[facing={f},waterlogged=false]',
                 'supplementaries:jar', 'farmersdelight:apple_pie[bites=0,facing={f}]']
TABLE_DECOR = rx(r'flower_pot|^potted_|candle|lantern|book|jar|plate|cake|pie')
WHITE_SEAT = rx(r'^(quartz|smooth_quartz|polished_diorite|diorite|calcite|white_concrete|white_terracotta|snow)_')
FENCEISH = rx(r'(_fence$|_fence_gate$|_wall$|^iron_bars$|^chain$|^bamboo$|leaves$)')
REMOVE = rx(r'^(redstone_wire|repeater|comparator|observer|piston|sticky_piston|piston_head|moving_piston|tripwire|'
            r'detector_rail|activator_rail|powered_rail|daylight_detector|target|tnt|command_block|structure_block|'
            r'structure_void|barrier|light|jigsaw|spawner|cobweb|\w+_skull|\w+_wall_skull|\w+_head|\w+_wall_head)$')


def is_air(s):
    return s is None or bid(s) in ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air')


def passable(s):
    return is_air(s) or bool(PASSABLE.match(nm(s)))


MOD_FURN = rx(r'^(refurbished_furniture|another_furniture|farmersdelight|kaleidoscope_cookery|candlelight|supplementaries|'
              r'displaydelight|cluttered|redeco|furniture|bakery|vinery):')


def floorlike(s):
    if passable(s) or MOD_FURN.match(bid(s)):  # tampo de mesa/bancada convertida nao e piso de comodo
        return False
    p = props(s)
    n = nm(s)
    if n.endswith('_slab') and p.get('type') == 'bottom':
        return False
    if n.endswith('_stairs') and p.get('half') == 'bottom':
        return False
    return not NOT_FLOOR.search(n)


def wallish(s):
    return not passable(s)


def wood_of(state, default='oak'):
    n = nm(state)
    for w in WOODS:
        if n.startswith(w + '_') or n.startswith('stripped_' + w + '_') or ('_' + w + '_') in n:
            return w
    return default


COLOR_OF = [(r'red_nether|crimson|red_', 'red'), (r'^nether_brick|blackstone|black_|deepslate', 'black'),
            (r'quartz|white_|diorite|calcite|birch', 'white'), (r'acacia|orange_', 'orange'), (r'warped|cyan_', 'cyan'),
            (r'prismarine|blue_', 'blue'), (r'pink|cherry', 'pink'), (r'^stone|cobble|andesite|gray_|tuff', 'gray'),
            (r'green_|moss', 'green'), (r'purpur|purple_', 'purple'), (r'yellow_|sandstone|bamboo', 'yellow')]


def color_of(state, default='brown'):
    n = nm(state)
    for p, c in COLOR_OF:
        if re.search(p, n):
            return c
    return default


class Vox:
    def __init__(self, g):
        self.g = g
        self.H, self.L, self.W = len(g), len(g[0]), len(g[0][0])
        self.loot = {}
        self.stats = collections.Counter()

    def inside(self, x, y, z):
        return 0 <= y < self.H and 0 <= z < self.L and 0 <= x < self.W

    def get(self, x, y, z):
        return self.g[y][z][x] if self.inside(x, y, z) else AIR

    def set(self, x, y, z, state, loot=None):
        if not self.inside(x, y, z):
            return
        if state != AIR:
            b, p = M.parse(state)
            state = M.fmt(b, M.clean_props(b, p))
        self.g[y][z][x] = state
        self.loot.pop((x, y, z), None)
        if loot:
            self.loot[(x, y, z)] = loot

    def nb(self, x, y, z, d):
        dx, dz = DIRS[d]
        return self.get(x + dx, y, z + dz)

    def covered(self, x, y, z, up=12):
        for yy in range(y + 1, min(self.H, y + up + 1)):
            s = self.g[yy][z][x]
            if not is_air(s) and not LEAFY.search(nm(s)) and not passable(s):
                return True
        return False

    def cells(self):
        for y in range(self.H):
            for z in range(self.L):
                for x in range(self.W):
                    yield x, y, z

    def on_floor(self, x, y, z):
        return floorlike(self.get(x, y - 1, z))


def back_dir(v, x, y, z, skip=()):
    """lado das costas de um movel em (x,y,z): parede atras e livre na frente; None se ambiguo."""
    good = []
    for d in DIRS:
        b = v.nb(x, y, z, d)
        f = v.nb(x, y, z, OPP[d])
        dx, dz = DIRS[d]
        if (x + dx, z + dz) in skip:
            continue
        if wallish(b) and passable(f):
            good.append(d)
    if len(good) == 1:
        return good[0]
    if good:
        # parede "de verdade" (bloco cheio que sobe) ganha de movel baixo
        tall = [d for d in good if wallish(v.get(x + DIRS[d][0], y + 1, z + DIRS[d][1]))]
        if len(tall) == 1:
            return tall[0]
    return None


def front_from_handle(v, x, y, z, levels=(0, 1)):
    for dy in levels:
        for d in DIRS:
            s = v.nb(x, y + dy, z, d)
            if HANDLE.search(nm(s)):
                p = props(s)
                if p.get('face', 'wall') == 'wall' and p.get('facing') == d:
                    return d
    return None


def place(block, wall):
    """facing pela convencao do mod com a parede no lado 'wall'"""
    return block.replace('{f}', I.facing_for(block, wall=wall))


# ================================================================ conversao dos moveis vanilla
class House:
    def __init__(self, v, key, wood='oak', seed=0, variant=0, theme=None):
        self.v, self.key, self.seed, self.variant, self.theme = v, key, seed, variant, theme
        self.ground = 0  # y of the ground slice (schematics sets it); porch detection only applies near it
        self.wood = wood if M.exists(f'refurbished_furniture:{wood}_kitchen_cabinetry') else 'oak'
        self.room_kind = {}

    def pick(self, salt, seq):
        return seq[zlib.crc32(f'{self.key}{salt}'.encode()) % len(seq)]

    # ------------------------------------------------ limpeza
    def cleanup(self):
        v = self.v
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            n = nm(s)
            if is_air(s):
                continue
            if REMOVE.match(n):
                v.set(x, y, z, AIR)
                v.stats['removido'] += 1
            elif n == 'redstone_lamp':
                v.set(x, y, z, 'minecraft:glowstone')
            elif n == 'redstone_block':
                v.set(x, y, z, 'minecraft:red_concrete')
            elif n in ('rail',) and v.covered(x, y, z):
                v.set(x, y, z, AIR)

    def outdoor_furnaces(self):
        """fornalha/defumador/alto-forno fora de casa (varanda, fachada: no schematic faziam papel de
        ar-condicionado ou churrasqueira) saem; os de dentro viram fogao em kitchen()"""
        v = self.v
        f = lambda x, y, z: bool(FURNACE.match(nm(v.get(x, y, z))))
        drop = []
        for x, y, z in v.cells():
            if not f(x, y, z):
                continue
            outside = not v.covered(x, y, z, up=6) and not self.near_room(x, y, z)
            # bloco 2x2 de fornalhas = aparelho de ar-condicionado/caixa de fachada, nunca fogao
            square = any(f(x + dx, y, z) and f(x, y, z + dz) and f(x + dx, y, z + dz) for dx in (-1, 1) for dz in (-1, 1))
            if outside or square:
                drop.append((x, y, z))
        for q in drop:
            v.set(*q, AIR)
            v.stats['fornalha_externa_removida'] += 1

    def floating_thin(self):
        """placa de pressao, tapete, vaso ou vela sem nada embaixo (sobrou de tampo de mesa convertido):
        desce ate o primeiro apoio a ate 2 blocos ou sai"""
        v = self.v
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if is_air(s) or not re.search(r'pressure_plate$|carpet$|flower_pot$|^potted_|candle$', nm(s)) or y == 0:
                continue
            if not is_air(v.get(x, y - 1, z)):
                continue
            to = None
            for k in (1, 2):
                b = v.get(x, y - k - 1, z)
                if not is_air(b):
                    to = y - k if not passable(b) else None
                    break
            v.set(x, y, z, AIR)
            if to is not None and is_air(v.get(x, to, z)) and not re.search(r'pressure_plate$|carpet$', nm(s)):
                v.set(x, to, z, s)
                v.stats['enfeite_desceu'] += 1
            else:
                v.stats['solto_removido'] += 1

    # ------------------------------------------------ fogao / pia / geladeira / bancada
    def kitchen(self):
        v, w = self.v, self.wood
        anchors = []
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            n = nm(s)
            if FURNACE.match(n) and self.near_room(x, y, z) and passable(v.nb(x, y, z, props(s).get('facing', 'north'))):
                near_ws = any(WORKSHOP.match(nm(v.get(x + dx, y + dy, z + dz)))
                              for dx in range(-3, 4) for dz in range(-3, 4) for dy in (-1, 0, 1))
                if near_ws:
                    continue
                front = props(s).get('facing', 'north')
                v.set(x, y, z, f'farmersdelight:stove[facing={front},lit=false]')
                v.stats['fogao'] += 1
                anchors.append((x, y, z))
                top = v.get(x, y + 1, z)
                if re.search(r'rail|pressure_plate|carpet', nm(top)):
                    v.set(x, y + 1, z, AIR)
            elif CAULDRON.match(n) and self.near_room(x, y, z) and v.on_floor(x, y, z):
                anchors.append((x, y, z))
        # geladeiras: 2 blocos empilhados de material branco/ferro, com puxador ou perto de bancada
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if not FRIDGE_MAT.match(nm(s)) or not self.near_room(x, y, z) or not v.on_floor(x, y, z):
                continue
            up = v.get(x, y + 1, z)
            # 2 de altura; se o mesmo material continua para cima e parede, nao geladeira
            if not FRIDGE_MAT.match(nm(up)) or FRIDGE_MAT.match(nm(v.get(x, y + 2, z))) or FRIDGE_MAT.match(nm(v.get(x, y - 1, z))):
                continue
            front = front_from_handle(v, x, y, z)
            near_k = any(abs(ax - x) + abs(az - z) <= 4 and abs(ay - y) <= 1 for ax, ay, az in anchors)
            if not front and not (near_k and nm(s) == 'iron_block'):
                continue
            if not front:
                bd = back_dir(v, x, y, z)
                if not bd:
                    continue
                front = OPP[bd]
            back = OPP[front]
            # 2026-10-09: a geladeira so vale com as costas numa parede de verdade e a
            # frente livre (sem parede nem outro movel de cozinha colado nela, senao a
            # porta abre para dentro do fogao/pia e o facing sai errado). Sem isso ela
            # nascia atravessada no meio da cozinha.
            def _fridge_ok(bk):
                fr = OPP[bk]
                dxb, dzb = DIRS[bk]
                dxf, dzf = DIRS[fr]
                if not wallish(v.nb(x, y, z, bk)) or not wallish(v.get(x + dxb, y + 1, z + dzb)):
                    return False
                if any(ax == x + dxf and az == z + dzf and abs(ay - y) <= 1 for ax, ay, az in anchors):
                    return False
                return True
            if not _fridge_ok(back):
                alt = next((d for d in DIRS if d != back and _fridge_ok(d)), None)
                if alt is None:
                    alt = next((d for d in DIRS if d != back and wallish(v.nb(x, y, z, d))), None)
                if alt is None:
                    continue
                back, front = alt, OPP[alt]
            v.set(x, y, z, f'refurbished_furniture:light_freezer[facing={back},open=false]', loot='fridge')
            v.set(x, y + 1, z, f'refurbished_furniture:light_fridge[facing={back},open=false]', loot='fridge')
            for dy in (0, 1):
                hs = v.nb(x, y + dy, z, front)
                if HANDLE.search(nm(hs)):
                    dx, dz = DIRS[front]
                    v.set(x + dx, y + dy, z + dz, AIR)
            v.stats['geladeira'] += 1
            anchors.append((x, y, z))
        # porta de ferro dentro de casa encostada em bloco = geladeira
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if nm(s) != 'iron_door' or props(s).get('half') != 'lower' or not self.near_room(x, y, z):
                continue
            f = props(s).get('facing', 'north')
            behind = v.nb(x, y, z, f)
            infront = v.nb(x, y, z, OPP[f])
            if wallish(behind) and passable(infront):
                v.set(x, y, z, f'refurbished_furniture:light_freezer[facing={f},open=false]', loot='fridge')
                v.set(x, y + 1, z, f'refurbished_furniture:light_fridge[facing={f},open=false]', loot='fridge')
                v.stats['geladeira'] += 1
                anchors.append((x, y, z))
        # bancada: tudo que encosta (mesmo y) num fogao/pia/geladeira e tem cara de bancada
        run = set()
        stack = list(anchors)
        seen = set(anchors)
        while stack:
            x, y, z = stack.pop()
            for d in DIRS:
                dx, dz = DIRS[d]
                q = (x + dx, y, z + dz)
                if q in seen:
                    continue
                s = v.get(*q)
                if self.counter_like(*q, chained=True):
                    seen.add(q)
                    run.add(q)
                    stack.append(q)
        anchor_set = set(anchors)
        for (x, y, z) in sorted(run):
            s = v.get(x, y, z)
            bd = back_dir(v, x, y, z, skip={(a[0], a[2]) for a in run | anchor_set if a[1] == y})
            if not bd:
                bd = back_dir(v, x, y, z)
            if not bd:
                # canto da bancada em L: costas na parede cujo lado oposto continua a bancada
                same = run | anchor_set
                bd = next((d for d in DIRS if wallish(v.nb(x, y, z, d)) and
                           (x + DIRS[d][0], y, z + DIRS[d][1]) not in same and
                           (x - DIRS[d][0], y, z - DIRS[d][1]) in same), None)
            if not bd:
                continue
            if nm(s) == 'barrel':
                v.loot[(x, y, z)] = 'kitchen'
                continue
            front = OPP[bd]
            handle = HANDLE.search(nm(v.nb(x, y, z, front)))
            if handle:
                dx, dz = DIRS[front]
                v.set(x + dx, y, z + dz, AIR)
                v.set(x, y, z, f'refurbished_furniture:{self.wood}_kitchen_drawer[facing={bd},open=false]', loot='kitchen')
            else:
                v.set(x, y, z, f'refurbished_furniture:{self.wood}_kitchen_cabinetry[facing={bd},shape=default]', loot='kitchen')
            v.stats['bancada'] += 1
            top = v.get(x, y + 1, z)
            if re.search(r'rail|pressure_plate|_carpet', nm(top)):
                v.set(x, y + 1, z, AIR)
        # pias: caldeirao na bancada = pia de cozinha; sozinho = lavatorio
        for x, y, z in anchors:
            s = v.get(x, y, z)
            if not CAULDRON.match(nm(s)):
                continue
            kitchen = any((x + dx, y, z + dz) in run or (x + dx, y, z + dz) in anchor_set and (x + dx, y, z + dz) != (x, y, z)
                          for dx, dz in DIRS.values())
            bd = back_dir(v, x, y, z, skip={(a[0], a[2]) for a in run | anchor_set if a[1] == y}) or back_dir(v, x, y, z)
            if not bd:
                fh = front_from_handle(v, x, y, z, levels=(1,))
                bd = OPP[fh] if fh else 'north'
            for dy in (1, 2):
                if re.search(r'tripwire_hook|lever|_button', nm(v.get(x, y + dy, z))):
                    v.set(x, y + dy, z, AIR)
                for d in DIRS:
                    hs = v.nb(x, y + dy, z, d)
                    if nm(hs) == 'tripwire_hook':
                        dx, dz = DIRS[d]
                        v.set(x + dx, y + dy, z + dz, AIR)
            if kitchen:
                v.set(x, y, z, f'refurbished_furniture:{self.wood}_kitchen_sink[facing={bd}]', loot='kitchen')
                v.stats['pia'] += 1
            else:
                v.set(x, y, z, f'refurbished_furniture:white_basin[facing={bd}]', loot='bathroom')
                v.stats['lavatorio'] += 1

    def kitchen_tops(self):
        """em cima da bancada o schematic poe alcapao/placa como "tampo": vira comida (Display Delight,
        Cluttered, Kaleidoscope) ou utensilio; panela/frigideira no fogao; nada na pia. Alcapao/escada
        de cima 2-3 blocos acima da bancada, encostado na parede, vira armario de parede (coifa em
        cima do fogao)."""
        v, w = self.v, self.wood
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            b = bid(s)
            m = KITCHEN_BASE.search(b)
            if not m:
                continue
            f = props(s).get('facing', 'north')
            wall = f if b.startswith('refurbished_furniture:') else OPP[f]
            front = OPP[wall]
            a = v.get(x, y + 1, z)
            junk = re.search(r'_trapdoor$|pressure_plate$|carpet$', nm(a)) and not (nm(a).endswith('_trapdoor') and props(a).get('open') == 'true')
            seed = zlib.crc32(f'{self.key}{x}{y}{z}'.encode())
            if junk or is_air(a) and seed % 4 == 0:
                if 'stove' in b:
                    top = ['farmersdelight:cooking_pot[facing={f},support=tray]', 'farmersdelight:skillet[facing={f},support=true]',
                           'refurbished_furniture:frying_pan[facing={f},lit=false]'][seed % 3]
                elif 'sink' in b:
                    top = None
                else:
                    top = COUNTER_DECOR[seed % len(COUNTER_DECOR)] if seed % 7 else None
                if top and M.exists(bid(top).replace('{w}', w)):
                    # props the block does not have (stacks in displaydelight:plated_*) are dropped before writing
                    tb, tp = M.parse(top.replace('{w}', w).replace('{f}', front))
                    v.set(x, y + 1, z, M.fmt(tb, M.clean_props(tb, tp)))
                    v.stats['tampo_enfeitado'] += 1
                elif junk:
                    v.set(x, y + 1, z, AIR)
            # armario de parede / coifa
            for dy in (2, 3):
                u = v.get(x, y + dy, z)
                un, up = nm(u), props(u)
                upper = (un.endswith('_trapdoor') and up.get('half') == 'top' and up.get('open') == 'false') or \
                    (un.endswith('_stairs') and up.get('half') == 'top') or (un.endswith('_slab') and up.get('type') == 'top')
                if not upper:
                    continue
                if dy == 3 and not passable(v.get(x, y + 2, z)):
                    break
                dx, dz = DIRS[wall]
                if not wallish(v.get(x + dx, y + dy, z + dz)):
                    break
                if 'stove' in b:
                    v.set(x, y + dy, z, f'refurbished_furniture:light_range_hood[facing={wall},powered=false]')
                    v.stats['coifa'] += 1
                else:
                    hinge = 'left' if (x + z) % 2 else 'right'
                    v.set(x, y + dy, z, f'refurbished_furniture:{w}_kitchen_storage_cabinet[facing={wall},hinge={hinge},open=false]',
                          loot='kitchen')
                    v.stats['armario_de_parede'] += 1
                break

    def counter_like(self, x, y, z, chained=False):
        v = self.v
        s = v.get(x, y, z)
        if is_air(s) or not (chained or self.near_room(x, y, z)) or not v.on_floor(x, y, z):
            return False
        n, p = nm(s), props(s)
        ok = (n.endswith('_stairs') and p.get('half') == 'top') or (n.endswith('_slab') and p.get('type') in ('top', 'double')) \
            or bool(COUNTER_MAT.search(n))
        if not ok:
            return False
        above = v.get(x, y + 1, z)
        # parede continua para cima (ou janela em cima): nao e bancada
        return passable(above) or re.search(r'lantern|flower_pot|potted_|candle|_hook|chain|cooking_pot|cutting_board|'
                                            r'brewing_stand|_pressure_plate|_trapdoor|rail', nm(above)) is not None

    # ------------------------------------------------ banheiro
    def bathroom(self):
        """funil com gancho/alavanca/botao em cima (torneira) = lavatorio; funil sozinho = privada;
        escada/laje de material branco com alcapao de tampa em cima, ou perto da pia, = privada"""
        v = self.v
        fixtures = []
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if nm(s) != 'hopper' or not self.near_room(x, y, z) or not v.on_floor(x, y, z) or not v.covered(x, y, z):
                continue
            above = v.get(x, y + 1, z)
            tap = HANDLE.search(nm(above)) or nm(above) == 'tripwire_hook'
            if wallish(above) and not tap and not SEAT_SIDE.search(nm(above)):
                continue
            bd = back_dir(v, x, y, z)
            if not bd:
                # 2026-10-11: funil dentro de casa e sempre louca (lavatorio ou
                # privada); sem parede clara usa o norte em vez de nascer vanilla.
                bd = 'north'
                v.stats['privada_sem_parede'] += 1
            if tap:
                v.set(x, y + 1, z, AIR)
                v.set(x, y, z, f'refurbished_furniture:white_basin[facing={bd}]', loot='bathroom')
                v.stats['lavatorio'] += 1
            else:
                v.set(x, y, z, f'refurbished_furniture:white_toilet[facing={bd}]', loot='bathroom')
                if SEAT_SIDE.search(nm(above)):
                    v.set(x, y + 1, z, AIR)
                v.stats['privada'] += 1
            fixtures.append((x, y, z))
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            n = nm(s)
            if not (WHITE_SEAT.search(n) and re.search(r'_(stairs|slab)$', n)) or props(s).get('type') == 'double':
                continue
            # encostada num comodo de verdade (friso de janela do lado de fora nao conta)
            if not self.near_room(x, y, z) or not v.on_floor(x, y, z) or not v.covered(x, y, z):
                continue
            above = v.get(x, y + 1, z)
            lid = nm(above).endswith('_trapdoor') or HANDLE.search(nm(above))
            near_fix = any(abs(fx - x) + abs(fz - z) <= 3 and fy == y for fx, fy, fz in fixtures)
            if not (lid or near_fix) or wallish(above) and not lid:
                continue
            bd = back_dir(v, x, y, z)
            if not bd:
                continue
            if lid:
                v.set(x, y + 1, z, AIR)
            v.set(x, y, z, f'refurbished_furniture:white_toilet[facing={bd}]', loot='bathroom')
            v.stats['privada'] += 1

    def wall_side(self, x, y, z):
        """unico lado com parede cheia (ou o primeiro, se houver mais de um)"""
        sides = [d for d in DIRS if wallish(self.v.nb(x, y, z, d)) and not passable(self.v.nb(x, y, z, d))]
        return sides[0] if sides else None

    # ------------------------------------------------ camas falsas
    def beds(self):
        """cabeceira = laje dupla/bloco do mesmo material encostada numa escada de baixo (colchao)"""
        v = self.v
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            n, p = nm(s), props(s)
            if not ((n.endswith('_slab') and p.get('type') == 'double') or re.search(r'_wool$|_concrete$|_terracotta$', n)):
                continue
            if not self.near_room(x, y, z, r=2) or not v.on_floor(x, y, z):
                continue
            mat = re.sub(r'_(slab|wool|concrete|terracotta)$', '', n)
            feet = []
            for d in DIRS:
                t = v.nb(x, y, z, d)
                tn, tp = nm(t), props(t)
                if tn == mat + '_stairs' and tp.get('half') == 'bottom':
                    feet.append(d)
            if len(feet) != 1:
                continue
            d = feet[0]
            dx, dz = DIRS[d]
            # a flight of steps, not a bed: only skip when the headboard spot itself is
            # stairs/slabs going up (it turned the steps down under the pink house into a bed).
            # Do not skip real beds just because the floor behind is open.
            bx, bz = x - dx, z - dz
            stepish = all(re.search(r'_stairs$|_slab$', nm(v.get(bx, y + k, bz))) for k in (0, 1))
            if stepish:
                continue
            head = OPP[d]  # facing da cama = direcao da cabeceira, vista do pe
            color = color_of(s, 'red')
            if not M.exists(f'minecraft:{color}_bed'):
                color = 'red'
            v.set(x, y, z, f'minecraft:{color}_bed[facing={head},occupied=false,part=head]')
            v.set(x + dx, y, z + dz, f'minecraft:{color}_bed[facing={head},occupied=false,part=foot]')
            if nm(v.get(x, y + 1, z)).endswith('_slab'):
                v.set(x, y + 1, z, AIR)
            v.stats['cama'] += 1

    def wool_beds(self):
        """bloco de la de 1-2 de largura e 2-4 de comprimento no chao (as vezes com glowstone de
        abajur embutido) = cama(s) de verdade; a cabeceira fica no lado encostado na parede.
        O que estava em cima (tapete, cerca, laje) sai."""
        v = self.v
        seen = set()
        for x, y, z in v.cells():
            if (x, y, z) in seen or not nm(v.g[y][z][x]).endswith('_wool'):
                continue
            comp, stack = [], [(x, z)]
            seen.add((x, y, z))
            while stack:
                cx, cz = stack.pop()
                comp.append((cx, cz))
                for dx, dz in DIRS.values():
                    q = (cx + dx, y, cz + dz)
                    if q in seen:
                        continue
                    qs = v.get(*q)
                    if nm(qs).endswith('_wool') or nm(qs) == 'glowstone' and \
                            sum(nm(v.get(q[0] + ex, y, q[2] + ez)).endswith('_wool') for ex, ez in DIRS.values()) >= 2:
                        seen.add(q)
                        stack.append((q[0], q[2]))
            # so dentro de casa: la no quintal (almofada, toldo, canteiro) nao vira cama
            if not all(v.covered(cx, y, cz) for cx, cz in comp):
                continue
            xs = sorted({c[0] for c in comp})
            zs = sorted({c[1] for c in comp})
            wx, lz = len(xs), len(zs)
            if len(comp) != wx * lz or len(comp) < 2 or min(wx, lz) > 2 or max(wx, lz) > 4:
                continue
            if not all(v.on_floor(cx, y, cz) for cx, cz in comp) or not any(self.near_room(cx, y, cz, r=2) for cx, cz in comp):
                continue
            # la que continua para cima e parede/divisoria, nao cama
            if any(wallish(v.get(cx, y + 1, cz)) and not re.search(r'carpet|fence|_slab|_table|pressure_plate|trapdoor', nm(v.get(cx, y + 1, cz)))
                   for cx, cz in comp):
                continue
            along_x = wx > lz or wx == lz and any(wallish(v.get(xs[0] - 1, y, cz)) or wallish(v.get(xs[-1] + 1, y, cz)) for cz in zs)
            if along_x:
                head_side = 'west' if all(wallish(v.get(xs[0] - 1, y, cz)) for cz in zs) else 'east'
                rows = [[(cx, cz) for cx in (xs if head_side == 'west' else xs[::-1])] for cz in zs]
            else:
                head_side = 'north' if all(wallish(v.get(cx, y, zs[0] - 1)) for cx in xs) else 'south'
                rows = [[(cx, cz) for cz in (zs if head_side == 'north' else zs[::-1])] for cx in xs]
            color = re.sub(r'_wool$', '', nm(v.get(*((rows[0][0][0], y, rows[0][0][1])))) or 'white')
            if not M.exists(f'minecraft:{color}_bed'):
                color = 'white'
            for cx, cz in comp:
                for dy in (1, 2):
                    a = v.get(cx, y + dy, cz)
                    if not is_air(a) and re.search(r'carpet|fence|_slab|_table|pressure_plate|trapdoor|_wall$|^snow$', nm(a)):
                        v.set(cx, y + dy, cz, AIR)
                v.set(cx, y, cz, AIR)
            for row in rows:
                (hx, hz), (fx, fz) = row[0], row[1]
                v.set(hx, y, hz, f'minecraft:{color}_bed[facing={head_side},occupied=false,part=head]')
                v.set(fx, y, fz, f'minecraft:{color}_bed[facing={head_side},occupied=false,part=foot]')
                v.stats['cama_de_la'] += 1
            # pe da cama: bau so na primeira fileira se sobrou espaco
            if len(rows[0]) >= 3:
                ex, ez = rows[0][2]
                v.set(ex, y, ez, f'minecraft:chest[facing={OPP[head_side]},type=single,waterlogged=false]', loot='bedroom')

    # ------------------------------------------------ mesas, cadeiras e sofas
    def stair_seat(self, x, y, z):
        v = self.v
        s = v.get(x, y, z)
        n, p = nm(s), props(s)
        if not n.endswith('_stairs') or p.get('half') != 'bottom' or not self.near_room(x, y, z) or not v.on_floor(x, y, z):
            return False
        if wallish(v.get(x, y + 1, z)):
            return False
        f = p.get('facing', 'north')
        dx, dz = DIRS[f]
        # degrau de escada: o proximo degrau sobe na direcao do facing
        nxt = v.get(x + dx, y + 1, z + dz)
        if nm(nxt).endswith(('_stairs', '_slab')) or floorlike(nxt):
            return False
        prev = v.get(x - dx, y - 1, z - dz)
        if nm(prev).endswith('_stairs') and props(prev).get('facing') == f:
            return False
        # frente livre (dentro do comodo) e pelo menos um lado livre, braco ou outro assento: escada embutida
        # na parede (peitoril, friso) tem paredes dos dois lados
        if (x - dx, y, z - dz) not in self.inroom:
            return False
        lat = ('east', 'west') if f in ('north', 'south') else ('north', 'south')
        embedded = all(wallish(v.nb(x, y, z, d)) and wallish(v.nb(x, y + 1, z, d)) and
                       not SEAT_SIDE.search(nm(v.nb(x, y, z, d))) for d in lat)
        return not embedded

    def seats(self):
        v, w = self.v, self.wood
        tables = set()
        # mesas: perna (cerca/muro) com tampo, ou perna solta com cadeira-escada encostada.
        # 2026-10-11: movel testa indoors() (teto + piso + encosto no comodo); o
        # inroom estrito do 10-10 testava a celula do movel e nunca convertia nada.
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            n = nm(s)
            if not self.indoors(x, y, z):
                continue
            leg = TABLE_LEG.search(n) and not n.endswith('_fence_gate')
            if leg:
                top = v.get(x, y + 1, z)
                tn, tp = nm(top), props(top)
                capped = TABLE_TOP.search(tn) and (not tn.endswith('_slab') or tp.get('type') == 'bottom') and \
                    (not tn.endswith('_trapdoor') or tp.get('half') == 'bottom' and tp.get('open') == 'false')
                chair_near = any(self.stair_seat(x + dx, y, z + dz) for dx, dz in DIRS.values())
                # perna solta so e mesa se nao fizer parte de cerca/muro (vizinhos da mesma familia = cercado)
                fence_run = sum(1 for d in DIRS if TABLE_LEG.search(nm(v.nb(x, y, z, d)))) >= 2
                if (capped or chair_near) and not fence_run:
                    if capped:
                        v.set(x, y + 1, z, AIR)
                    tables.add((x, y, z))
            elif (n.endswith('_slab') and props(s).get('type') == 'top') or (n.endswith('_stairs') and props(s).get('half') == 'top') \
                    or n == 'scaffolding':
                if passable(v.get(x, y + 1, z)) and any(self.stair_seat(x + dx, y, z + dz) for dx, dz in DIRS.values()):
                    tables.add((x, y, z))
        # mesa "suspensa": tampo de laje de cima com ar embaixo e piso logo abaixo, pernas de alcapao aberto
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if not (nm(s).endswith('_slab') and props(s).get('type') == 'top') or y < 2:
                continue
            if not is_air(v.get(x, y - 1, z)) or not floorlike(v.get(x, y - 2, z)) or (x, y - 1, z) not in self.inroom:
                continue
            deco = v.get(x, y + 1, z)
            on_top = not passable(deco) and TABLE_DECOR.search(nm(deco))
            if not passable(deco) and not on_top:
                continue
            # tampo de mesa tem vizinho tampo/alcapao/ar; laje de teto/beiral tem bloco cheio do lado
            if any(floorlike(v.nb(x, y, z, d)) and not nm(v.nb(x, y, z, d)).endswith('_slab') for d in DIRS):
                continue
            v.set(x, y, z, AIR)
            tables.add((x, y - 1, z))
            if on_top:  # vaso/vela do centro de mesa desce para cima do tampo novo
                v.set(x, y, z, deco)
                v.set(x, y + 1, z, AIR)
            for d in DIRS:
                dx, dz = DIRS[d]
                for dy in (-1, 0):  # saia de alcapao aberto em volta do tampo
                    leg = v.get(x + dx, y + dy, z + dz)
                    if nm(leg).endswith('_trapdoor') and props(leg).get('open') == 'true':
                        v.set(x + dx, y + dy, z + dz, AIR)
        # tampo de escada de cima (half=top) no nivel do piso, dentro de casa, com ar
        # em cima e encostado num conjunto de jantar (mesa ja achada, andaime ou
        # assento de escada): vira tampo de mesa de mod. Fora desse contexto
        # continua prateleira/balcao/pouso de escada (nao mexer).
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if not (nm(s).endswith('_stairs') and props(s).get('half') == 'top'):
                continue
            if not self.indoors(x, y, z) or not passable(v.get(x, y + 1, z)):
                continue
            if not any((x + dx, y, z + dz) in tables or
                       (nm(v.get(x + dx, y, z + dz)) == 'scaffolding' and self.indoors(x + dx, y, z + dz)) or
                       self.stair_seat(x + dx, y, z + dz) for dx, dz in DIRS.values()):
                continue
            tables.add((x, y, z))
            v.stats['tampo_escada'] += 1
        for (x, y, z) in tables:
            v.set(x, y, z, f'refurbished_furniture:{w}_table[east=false,north=false,south=false,west=false]')
            v.stats['mesa'] += 1
        # cadeira de laje: laje de baixo (madeira) com alcapao aberto de encosto e mesa/tampo do lado oposto
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if not (nm(s).endswith('_slab') and props(s).get('type') == 'bottom') or not self.indoors(x, y, z):
                continue
            if not wood_of(s, None):
                continue
            back = next((d for d in DIRS if nm(v.nb(x, y, z, d)).endswith('_trapdoor') and props(v.nb(x, y, z, d)).get('open') == 'true'), None)
            if not back:
                continue
            dx, dz = DIRS[OPP[back]]
            t = (x + dx, y, z + dz)
            ts = v.get(*t)
            desk = t in tables or (nm(ts).endswith('_stairs') and props(ts).get('half') == 'top') or \
                (nm(ts).endswith('_slab') and props(ts).get('type') == 'top')
            if not desk:
                continue
            bx, bz = DIRS[back]
            v.set(x + bx, y, z + bz, AIR)
            for q in ((x, y + 1, z), (x + bx, y + 1, z + bz)):
                if nm(v.get(*q)).endswith('_trapdoor'):
                    v.set(*q, AIR)
            # tampo de escadas/lajes de cima emendado: vira mesa inteira (escrivaninha em L)
            todo = [t] if t not in tables else []
            while todo:
                q = todo.pop()
                qs = v.get(*q)
                top_ok = passable(v.get(q[0], y + 1, q[2])) or TABLE_DECOR.search(nm(v.get(q[0], y + 1, q[2])))
                if q in tables or not top_ok or not ((nm(qs).endswith('_stairs') and props(qs).get('half') == 'top') or
                                                     (nm(qs).endswith('_slab') and props(qs).get('type') == 'top')):
                    continue
                tables.add(q)
                v.set(*q, f'refurbished_furniture:{w}_table[east=false,north=false,south=false,west=false]')
                v.stats['mesa'] += 1
                for ex, ez in DIRS.values():
                    todo.append((q[0] + ex, y, q[2] + ez))
            model = f'another_furniture:{w}_chair[facing={{f}},tucked=false,variant=1]'
            if not M.exists(bid(model)):
                model = 'another_furniture:oak_chair[facing={f},tucked=false,variant=1]'
            v.set(x, y, z, model.replace('{f}', I.facing_for(model, toward=OPP[back])))
            v.stats['cadeira'] += 1
        # cadeira de andaime: encosto = alcapao aberto ao lado (no mesmo nivel ou um acima)
        for x, y, z in v.cells():
            if nm(v.g[y][z][x]) != 'scaffolding' or not self.indoors(x, y, z):
                continue
            back = None
            for d in DIRS:
                for dy in (0, 1):
                    t = v.nb(x, y + dy, z, d)
                    if nm(t).endswith('_trapdoor') and props(t).get('open') == 'true':
                        back = back or d
                        dx, dz = DIRS[d]
                        v.set(x + dx, y + dy, z + dz, AIR)
            for dy in (1,):
                if nm(v.get(x, y + dy, z)).endswith('_trapdoor'):
                    v.set(x, y + dy, z, AIR)
            if back is None:
                tdir = next((d for d in DIRS if (x + DIRS[d][0], y, z + DIRS[d][1]) in tables), None)
                back = OPP[tdir] if tdir else (back_dir(v, x, y, z) or 'north')
            model = f'another_furniture:{w}_chair[facing={{f}},tucked=false,variant=1]'
            if not M.exists(bid(model)):
                model = 'another_furniture:oak_chair[facing={f},tucked=false,variant=1]'
            v.set(x, y, z, model.replace('{f}', I.facing_for(model, toward=OPP[back])))
            v.stats['cadeira'] += 1
        # assentos: escadas de baixo dentro de casa que nao sao degrau
        seen = set()
        chair_models = [f'kaleidoscope_cookery:chair_{w}[facing={{f}},has_carpet=false,waterlogged=false]',
                        f'another_furniture:{w}_chair[facing={{f}},tucked=false,variant=2]',
                        f'candlelight:{w}_chair[facing={{f}}]',
                        f'refurbished_furniture:{w}_chair[facing={{f}},tucked=false]']
        chair_models = [c for c in chair_models if M.exists(bid(c))] or [f'refurbished_furniture:oak_chair[facing={{f}},tucked=false]']
        for x, y, z in v.cells():
            if (x, y, z) in seen or not self.stair_seat(x, y, z):
                continue
            s = v.get(x, y, z)
            f = props(s).get('facing', 'north')
            lat = ('east', 'west') if f in ('north', 'south') else ('north', 'south')
            run = [(x, y, z)]
            seen.add((x, y, z))
            for d in lat:
                cx, cz = x, z
                while True:
                    dx, dz = DIRS[d]
                    cx, cz = cx + dx, cz + dz
                    q = (cx, y, cz)
                    qs = v.get(*q)
                    if q in seen or not self.stair_seat(*q) or props(qs).get('facing') != f:
                        break
                    seen.add(q)
                    run.append(q)
            front = OPP[f]  # quem senta olha para longe do encosto
            near_table = any((qx + DIRS[front][0], y, qz + DIRS[front][1]) in tables for qx, _, qz in run)
            armrest = any(SEAT_SIDE.search(nm(v.get(qx + dx, y, qz + dz))) for qx, _, qz in run for dx, dz in DIRS.values())
            soft = re.search(r'nether|quartz|wool|terracotta|concrete|prismarine|purpur|blackstone|deepslate', nm(s))
            # 2026-10-10: sofa no meio do nada nao existe: fileira so vira sofa com as costas
            # numa parede de verdade (senao vira cadeira, que bloqueia menos a passagem).
            back_dx, back_dz = DIRS[f]
            backed = all(wallish(v.get(qx + back_dx, y, qz + back_dz)) and
                         wallish(v.get(qx + back_dx, y + 1, qz + back_dz)) for qx, _, qz in run)
            if len(run) >= 2 and backed and (soft or armrest or not near_table):
                color = color_of(s)
                if not M.exists(f'another_furniture:{color}_sofa'):
                    color = 'brown'
                for q in run:
                    v.set(*q, f'another_furniture:{color}_sofa[facing={front},type=single]')
                v.stats['sofa'] += len(run)
            else:
                for q in run:
                    model = chair_models[(zlib.crc32(f'{self.key}{q[0] // 8}{q[2] // 8}'.encode())) % len(chair_models)]
                    v.set(*q, model.replace('{f}', I.facing_for(model, toward=front)))
                v.stats['cadeira'] += len(run)
            # bracos de alcapao/placa dos lados viram ar (o movel ja tem braco)
            for qx, _, qz in run:
                for d in lat:
                    dx, dz = DIRS[d]
                    side = v.get(qx + dx, y, qz + dz)
                    if SEAT_SIDE.search(nm(side)) and not nm(side).endswith('_button'):
                        v.set(qx + dx, y, qz + dz, AIR)
        self.trim_tables(tables)

    def trim_tables(self, tables):
        """conjuntos de jantar convertidos: no maximo 2 tampos (2x1 solitario) e
        1 cadeira. (2026-10-11, pedido do dono: a mesa do print nascia grande
        demais, com andaimes/escadas/caixotes em volta parecendo extensao.)"""
        v = self.v
        seen = set()
        for t in sorted(tables):
            if t in seen:
                continue
            comp, stack = [t], [t]
            seen.add(t)
            while stack:
                cx, cy, cz = stack.pop()
                for dx, dz in DIRS.values():
                    q = (cx + dx, cy, cz + dz)
                    if q in tables and q not in seen:
                        seen.add(q)
                        comp.append(q)
                        stack.append(q)
            for q in sorted(comp)[2:]:
                v.set(*q, AIR)
                v.stats['mesa_cortada'] += 1
            keep = set(sorted(comp)[:2])
            chairs = []
            for qx, qy, qz in keep:
                for dx, dz in DIRS.values():
                    cs = v.get(qx + dx, qy, qz + dz)
                    if bid(cs).startswith('minecraft:') or not re.search(r'chair|stool', nm(cs)):
                        continue
                    if re.search(r'sofa|couch', nm(cs)):
                        continue
                    chairs.append((qx + dx, qy, qz + dz))
            for c in sorted(set(chairs))[1:]:
                v.set(*c, AIR)
                v.stats['cadeira_cortada'] += 1

    # ------------------------------------------------ luzes
    def lights(self):
        v = self.v
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if nm(s) == 'beacon' and self.near_room(x, y, z) or nm(s) == 'beacon' and self.near_room(x, y - 1, z):
                above = v.get(x, y + 1, z)
                if wallish(above) and is_air(v.get(x, y - 1, z)):
                    v.set(x, y, z, 'refurbished_furniture:light_ceiling_light[face=ceiling,facing=north,powered=false]')
                else:
                    v.set(x, y, z, 'refurbished_furniture:white_lamp[powered=false]')
                v.stats['luminaria'] += 1

    # ------------------------------------------------ comodos
    def rooms(self):
        """regioes de ar cobertas com piso, por nivel; cada uma = lista de (x, z) no nivel y."""
        v = self.v
        seen = set()
        out = []
        for x, y, z in v.cells():
            if (x, y, z) in seen:
                continue
            if not self.room_cell(x, y, z):
                continue
            comp, stack = [], [(x, z)]
            seen.add((x, y, z))
            leak = 0
            while stack:
                cx, cz = stack.pop()
                comp.append((cx, cz))
                for dx, dz in DIRS.values():
                    q = (cx + dx, y, cz + dz)
                    if not v.inside(*q):
                        leak += 1
                        continue
                    if q in seen:
                        continue
                    if self.room_cell(*q):
                        seen.add(q)
                        stack.append((q[0], q[2]))
                    elif passable(v.get(*q)) and not v.covered(*q):
                        leak += 1
                    elif y <= self.ground + 3 and v.inside(q[0], y + 1, q[2]) and passable(v.get(q[0], y + 1, q[2])) and \
                            not v.covered(q[0], y + 1, q[2]) and not FENCEISH.search(nm(v.get(*q))):
                        # mureta/parapeito com ar livre em cima: alpendre/varanda, nao comodo
                        leak += 1
                    elif FENCEISH.search(nm(v.get(*q))):
                        # cerca/muro so abre o comodo se do outro lado for rua (ar descoberto ou fora da grade)
                        q2 = (q[0] + dx, y, q[2] + dz)
                        if not v.inside(*q2) or passable(v.get(*q2)) and not v.covered(*q2):
                            leak += 1
            if 4 <= len(comp) <= 400 and leak <= max(3, len(comp) // 15):
                out.append((y, comp))
        return out

    def map_rooms(self):
        self.inroom = {(x, y, z) for y, comp in self.rooms() for x, z in comp}

    def near_room(self, x, y, z, r=1):
        if (x, y, z) in self.inroom:
            return True
        if r == 1:
            return any((x + dx, y, z + dz) in self.inroom for dx, dz in DIRS.values())
        # r > 1: movel no canto cercado de outros moveis (cama de casal encostada em comoda etc.)
        return any((x + dx, y, z + dz) in self.inroom for dx in range(-r, r + 1) for dz in range(-r, r + 1))

    def indoors(self, x, y, z):
        """movel dentro de casa: com teto, no piso e encostado num comodo.
        (2026-10-11: o inroom estrito do 10-10 testava a celula DO MOVEL, que
        nunca e ar passavel e por isso nunca esta no inroom: travou TODAS as
        conversoes e andaimes/escadas voltaram a nascer como vanilla.)"""
        return self.v.covered(x, y, z) and self.near_room(x, y, z) and self.v.on_floor(x, y, z)

    def room_cell(self, x, y, z):
        v = self.v
        s = v.get(x, y, z)
        return passable(s) and v.on_floor(x, y, z) and v.covered(x, y, z)

    def headroom(self, x, y, z):
        h = 0
        while h < 6 and passable(self.v.get(x, y + h, z)):
            h += 1
        return h

    def furnish_empty(self):
        v = self.v
        rooms = self.rooms()
        if not rooms:
            return
        info = []
        for y, comp in rooms:
            cs = set(comp)
            lit = False
            # moveis = blocos de movel encostados no comodo (no nivel do piso e 1 acima)
            fpos = set()
            for cx, cz in comp:
                for dy in (0, 1):
                    for dx, dz in [(0, 0)] + list(DIRS.values()):
                        q = (cx + dx, y + dy, cz + dz)
                        if dy == 0 and (q[0], q[2]) in cs:
                            continue
                        s = v.get(*q)
                        if not is_air(s) and FURN.match(bid(s)):
                            fpos.add(q)
            furn = len(fpos)
            for cx, cz in comp:
                for yy in range(y, y + 6):
                    s = v.get(cx, yy, cz)
                    if LIGHT.search(nm(s)):
                        lit = True
                        break
                for dx, dz in DIRS.values():
                    for yy in (y, y + 1, y + 2):
                        if LIGHT.search(nm(v.get(cx + dx, yy, cz + dz))):
                            lit = True
            info.append({'y': y, 'cells': comp, 'furn': furn, 'lit': lit})
        # temas: por andar (y), maior comodo do andar mais baixo = sala
        for r in info:
            r['hr'] = max(self.headroom(cx, r['y'], cz) for cx, cz in r['cells'])
        levels = sorted({r['y'] for r in info})
        tall = sorted({r['y'] for r in info if r['hr'] >= 3})
        base = tall[0] if tall else levels[0]
        for lvl in levels:
            rs = sorted([r for r in info if r['y'] == lvl], key=lambda r: -len(r['cells']))
            for i, r in enumerate(rs):
                n = len(r['cells'])
                hr = r['hr']
                if hr <= 2:
                    r['kind'] = 'sotao'
                elif lvl == base:
                    r['kind'] = ['sala', 'cozinha', 'banheiro', 'quarto'][min(i, 3)] if n > 10 or i == 0 else 'banheiro'
                    if len(rs) == 1:
                        r['kind'] = 'sala_cozinha'
                else:
                    r['kind'] = 'banheiro' if n <= 10 and i > 0 and not any(x.get('kind') == 'banheiro' and x['y'] == lvl for x in rs[:i]) \
                        else 'quarto'
        self.alt_themes(info)
        for r in info:
            self.room_kind.update({(cx, r['y'], cz): r['kind'] for cx, cz in r['cells']})
            empty = r['furn'] < max(2, len(r['cells']) // 10)
            if empty:
                self.furnish_room(r)
            if not r['lit'] or empty:
                self.light_room(r)

    # temas alternativos: casa nao e so cozinha + quarto. O primeiro quarto da casa continua quarto; os outros
    # (e o sotao) viram biblioteca, ateliê, costura, escritorio, musica, estufa, quarto de crianca ou oficina.
    # Variante 0: metade deles; variante 1 (a mesma casa com outro interior): todos, com outro sorteio.
    ALT = ('biblioteca', 'atelie', 'costura', 'escritorio', 'musica', 'estufa', 'quarto_crianca', 'oficina')

    def alt_themes(self, info):
        if self.theme:
            # themed house: every room except kitchen, bathroom and the main bedroom takes the theme
            # (clutter.py fills it from the theme catalog)
            quartos = sorted([r for r in info if r['kind'] == 'quarto'], key=lambda r: (r['y'], -len(r['cells'])))
            keep = {id(quartos[0])} if quartos else set()
            for r in info:
                if r['kind'] in ('cozinha', 'banheiro') or id(r) in keep or r['kind'] == 'sotao' and r['y'] <= self.ground + 2:
                    continue
                if r['kind'] == 'sala_cozinha' and len(info) > 1:
                    continue
                r['kind'] = self.theme
            return
        quartos = sorted([r for r in info if r['kind'] == 'quarto'], key=lambda r: (r['y'], -len(r['cells'])))
        # low rooms at ground level (crawl space under a house on stilts) stay storage: only attics get a theme
        cands = quartos[1:] + [r for r in info if r['kind'] == 'sotao' and len(r['cells']) >= 9 and r['y'] > self.ground + 2]
        if self.variant and not cands and quartos:
            cands = quartos  # casa de um quarto so: a variante troca o quarto
        for i, r in enumerate(cands):
            salt = f'alt{self.variant}|{r["y"]}|{len(r["cells"])}|{i}'
            if self.variant == 0 and zlib.crc32((self.key + salt).encode()) % 2:
                continue
            kinds = list(self.ALT)
            if r['kind'] == 'sotao':
                kinds = ['atelie', 'estufa', 'oficina', 'biblioteca', 'costura']
            r['kind'] = self.pick(salt, kinds)

    @staticmethod
    def one_block(block):
        """bloco existe de verdade (registry + nome no en_us do mod) e e de 1 bloco so"""
        b = bid(block)
        if not M.exists(b) or not (b.startswith('minecraft:') or b in LANG):
            return False
        reg = M.REG['blocks'].get(b) or {}
        return set(reg) <= {'facing', 'waterlogged', 'powered', 'open', 'lit', 'horizontal', 'left', 'right', 'hinge',
                            'has_record', 'attached', 'type', 'shape', 'level', 'occupied', 'part', 'base', 'variant', 'tucked'}

    # itens por tema: (bloco com {f}, loot, alto?) colocados encostados na parede
    def theme_items(self, kind):
        alt = self.alt_items(kind)
        if alt is not None:
            return alt
        return self.base_items(kind)

    def alt_items(self, kind):
        if kind == self.theme:
            return []  # themed rooms are furnished by clutter.py
        w = self.wood
        c = self.pick(kind + 'cor', ['red', 'blue', 'green', 'brown', 'gray', 'light_blue', 'yellow', 'white', 'pink', 'cyan'])
        desk = f'refurbished_furniture:{w}_desk[facing={{f}},left=false,right=false]'
        drawer = f'refurbished_furniture:{w}_drawer[facing={{f}},left=false,right=false,open=false]'
        cabinet = f'refurbished_furniture:{w}_storage_cabinet[facing={{f}},hinge=left,open=false]'
        shelf = f'another_furniture:{w}_shelf[facing={{f}},horizontal=single]'
        sofa = f'another_furniture:{c}_sofa[facing={{f}},type=single]'
        chest = 'minecraft:chest[facing={f},type=single,waterlogged=false]'
        themes = {
            'biblioteca': [('minecraft:bookshelf', None), ('minecraft:bookshelf', None), (desk, 'office'),
                           ('minecraft:lectern[facing={f},has_book=false,powered=false]', None), (sofa, None),
                           ('minecraft:bookshelf', None), ('supplementaries:globe[facing={f}]', None), (cabinet, 'office')],
            'atelie': [('zetter:artist_table[facing={f}]', None), (shelf, None), (drawer, 'home'),
                       ('cluttered:box_of_paints[facing={f},waterlogged=false]', None), ('minecraft:potted_fern', None),
                       (chest, 'home'), ('cluttered:paint_water_jar[facing={f},waterlogged=false]', None)],
            'costura': [('minecraft:loom[facing={f}]', None), ('cluttered:sewing_mannequin[facing={f},part=1]', None),
                        (drawer, 'clothing'), (cabinet, 'clothing'), ('cluttered:sewing_machine_antique[facing={f},waterlogged=false]', None),
                        (chest, 'clothing'), ('cluttered:sewing_clutter[facing={f},part=1]', None)],
            'escritorio': [(desk, 'office'), ('minecraft:bookshelf', None), (cabinet, 'office'), (drawer, 'office'),
                           ('cluttered:traditional_radio[facing={f},has_record=false,waterlogged=false]', None),
                           ('supplementaries:globe_sepia[facing={f}]', None), ('minecraft:cartography_table', None)],
            'musica': [('minecraft:jukebox[has_record=false]', None), ('minecraft:note_block', None), (sofa, None),
                       ('minecraft:note_block', None), ('minecraft:bookshelf', None), (sofa, None),
                       ('tanukidecor:antique_radio[facing={f}]', None)],
            'estufa': [('minecraft:potted_fern', None), (f'another_furniture:{w}_flower_box[facing={{f}},attached=false,horizontal=single]', None),
                       ('minecraft:potted_flowering_azalea_bush', None), ('minecraft:composter[level=0]', None),
                       ('minecraft:potted_bamboo', None), ('minecraft:barrel[facing=up,open=false]', 'farm'),
                       ('cluttered:basket_of_flowers[facing={f},waterlogged=false]', None), ('minecraft:potted_azalea_bush', None)],
            'quarto_crianca': [('bed', 'bedroom'), ('tanukidecor:wooden_block_toys[facing={f}]', None), (chest, 'bedroom'),
                               ('whimsy_deco:red_toy_plane[facing={f},flying=false]', None), (drawer, 'bedroom'),
                               ('minecraft:bookshelf', None), ('tanukidecor:newtons_cradle[facing={f}]', None)],
            'oficina': [('minecraft:crafting_table', None), ('minecraft:smithing_table', None), ('minecraft:barrel[facing=up,open=false]', 'workshop'),
                        ('minecraft:anvil[facing={f}]', None), (chest, 'workshop'), ('create:depot', None), ('minecraft:grindstone[face=floor,facing={f}]', None)],
        }
        if kind not in themes:
            return None
        return [(b, l) for b, l in themes[kind] if b in ('bed', 'bath', 'fridge') or self.one_block(b)]

    def base_items(self, kind):
        w = self.wood
        c = self.pick(kind + 'cor', ['red', 'blue', 'green', 'brown', 'gray', 'light_blue', 'yellow', 'white', 'pink', 'cyan'])
        drawer = f'refurbished_furniture:{w}_drawer[facing={{f}},left=false,right=false,open=false]'
        cabinet = f'refurbished_furniture:{w}_storage_cabinet[facing={{f}},hinge=left,open=false]'
        shelf = f'another_furniture:{w}_shelf[facing={{f}},horizontal=single]'
        if kind in ('cozinha', 'sala_cozinha'):
            base = [('fridge', 'fridge'), (f'farmersdelight:stove[facing={{f}},lit=false]', None),
                    (f'refurbished_furniture:{w}_kitchen_sink[facing={{f}}]', 'kitchen'),
                    (f'refurbished_furniture:{w}_kitchen_cabinetry[facing={{f}},shape=default]', 'kitchen'),
                    (f'refurbished_furniture:{w}_kitchen_drawer[facing={{f}},open=false]', 'kitchen'),
                    (f'farmersdelight:{w if M.exists(f"farmersdelight:{w}_cabinet") else "oak"}_cabinet[facing={{f}},open=false]', 'kitchen'),
                    ('minecraft:barrel[facing=up,open=false]', 'kitchen')]
            if kind == 'sala_cozinha':
                base += [(f'another_furniture:{c}_sofa[facing={{f}},type=single]', None)] * 2 + [('minecraft:bookshelf', None)]
            return base
        if kind == 'sala':
            return [(f'another_furniture:{c}_sofa[facing={{f}},type=single]', None)] * 3 + \
                [('minecraft:bookshelf', None), (drawer, 'home'), ('minecraft:bookshelf', None), (shelf, None),
                 ('minecraft:potted_fern', None), (cabinet, 'home')]
        if kind == 'quarto':
            return [('bed', 'bedroom'), (drawer, 'bedroom'), (cabinet, 'bedroom'), ('minecraft:chest[facing={f},type=single,waterlogged=false]', 'bedroom'),
                    ('minecraft:bookshelf', None), (f'refurbished_furniture:{w}_desk[facing={{f}},left=false,right=false]', 'home'),
                    ('minecraft:potted_azalea_bush', None)]
        if kind == 'banheiro':
            return [('refurbished_furniture:white_toilet[facing={f}]', 'bathroom'), ('refurbished_furniture:white_basin[facing={f}]', 'bathroom'),
                    ('bath', 'bathroom'), (cabinet, 'bathroom')]
        return [('minecraft:barrel[facing=up,open=false]', 'home'), (f'refurbished_furniture:{w}_crate[open=false]', 'home'),
                ('minecraft:chest[facing={f},type=single,waterlogged=false]', 'home'), ('supplementaries:sack', None)]

    def furnish_room(self, r):
        v, y = self.v, r['y']
        cells = set(r['cells'])
        # celulas proibidas: na frente de porta/escada/alcapao e buracos
        banned = set()
        for cx, cz in cells:
            for dx, dz in DIRS.values():
                for dy in (0, 1):
                    s = v.get(cx + dx, y + dy, cz + dz)
                    n = nm(s)
                    # escada so bloqueia se for degrau de verdade (de baixo, com espaco livre em cima);
                    # parede feita de escada (cabana) nao conta
                    step = n.endswith('_stairs') and props(s).get('half') != 'top' and passable(v.get(cx + dx, y + dy + 1, cz + dz))
                    if n.endswith('_door') or n == 'ladder' or step or n.endswith('_fence_gate') or \
                            (n.endswith('_trapdoor') and props(s).get('open') == 'true'):
                        banned.add((cx, cz))
                        banned.add((cx - dx, cz - dz))
            if passable(v.get(cx, y - 1, cz)):
                banned.add((cx, cz))
        walls = []
        for cx, cz in sorted(cells):
            if (cx, cz) in banned:
                continue
            for d, (dx, dz) in DIRS.items():
                b = v.get(cx + dx, y, cz + dz)
                # 2026-10-09: movel (cadeira/mesa ja convertida) nao e parede: a
                # geladeira encostada em cadeira nascia com o facing errado
                if (cx + dx, cz + dz) not in cells and wallish(b) and not nm(b).endswith(('_door', 'ladder')) \
                        and not MOD_FURN.match(bid(b)) and not re.search(r'chair|sofa|_table$|^table_|_bed$', nm(b)):
                    walls.append((cx, cz, d))
                    break
        if not walls:
            return
        used = set()
        budget = max(1, int(len(walls) * 0.45))
        items = self.theme_items(r['kind'])
        if not items:
            return
        i = 0
        # rotaciona o inicio pela casa para nao ficar tudo igual
        start = zlib.crc32(f'{self.key}{y}{len(cells)}'.encode()) % len(walls)
        order = walls[start:] + walls[:start]
        for cx, cz, d in order:
            if len(used) >= budget or i >= len(items) * 2:
                break
            if (cx, cz) in used or not passable(v.get(cx, y, cz)):
                continue
            # deixa um vizinho livre ao longo da parede de vez em quando (circulacao)
            block, loot = items[i % len(items)]
            front = OPP[d]
            fx, fz = cx + DIRS[front][0], cz + DIRS[front][1]
            if block == 'fridge':
                if self.headroom(cx, y, cz) < 3:
                    i += 1
                    continue
                # 2026-10-09: geladeira so com as costas em parede de verdade (nao
                # escada) e a frente livre dentro do comodo (nao abre para dentro
                # do fogao/pia): senao tenta a proxima parede em vez de nascer torta
                back_s = v.get(cx + DIRS[d][0], y, cz + DIRS[d][1])
                if re.search(r'_stairs$|_slab$', nm(back_s)):
                    continue
                fx, fz = cx + DIRS[OPP[d]][0], cz + DIRS[OPP[d]][1]
                if (fx, fz) not in cells or (fx, fz) in used or (fx, fz) in banned or not passable(v.get(fx, y, fz)):
                    continue
                v.set(cx, y, cz, f'refurbished_furniture:light_freezer[facing={d},open=false]', loot='fridge')
                v.set(cx, y + 1, cz, f'refurbished_furniture:light_fridge[facing={d},open=false]', loot='fridge')
            elif block in ('bed', 'bath'):
                if (fx, fz) not in cells or (fx, fz) in used or (fx, fz) in banned or not passable(v.get(fx, y, fz)):
                    i += 1
                    continue
                if block == 'bed':
                    color = self.pick(f'cama{cx}{cz}', ['red', 'blue', 'white', 'light_gray', 'green', 'brown', 'cyan', 'yellow'])
                    v.set(cx, y, cz, f'minecraft:{color}_bed[facing={d},occupied=false,part=head]')
                    v.set(fx, y, fz, f'minecraft:{color}_bed[facing={d},occupied=false,part=foot]')
                else:
                    v.set(cx, y, cz, f'refurbished_furniture:white_bath[facing={front},type=head]')
                    v.set(fx, y, fz, f'refurbished_furniture:white_bath[facing={front},type=bottom]')
                used.add((fx, fz))
            else:
                v.set(cx, y, cz, place(block, d), loot=loot)
            used.add((cx, cz))
            v.stats['auto_' + r['kind']] += 1
            i += 1
        # sala: mesa de centro / jantar no meio se couber
        if r['kind'] in ('sala', 'sala_cozinha', 'cozinha') and len(cells) >= 20:
            xs = sorted(c[0] for c in cells)
            zs = sorted(c[1] for c in cells)
            mx, mz = xs[len(xs) // 2], zs[len(zs) // 2]
            ring = [(mx + dx, mz + dz) for dx, dz in DIRS.values()]
            # folga: nada num raio de 2 da mesa (cadeira nao nasce grudada em geladeira/bancada/parede)
            clear = [(mx + dx, mz + dz) for dx in range(-2, 3) for dz in range(-2, 3)]
            if (mx, mz) in cells and (mx, mz) not in used and all(p in cells and p not in used and p not in banned for p in ring) and \
                    all(p in cells and p not in used and passable(v.get(p[0], y, p[1])) and passable(v.get(p[0], y + 1, p[1])) for p in clear):
                v.set(mx, y, mz, f'refurbished_furniture:{self.wood}_table[east=false,north=false,south=false,west=false]')
                model = f'refurbished_furniture:{self.wood}_chair[facing={{f}},tucked=false]'
                for d, (dx, dz) in DIRS.items():
                    toward = OPP[d]
                    v.set(mx + dx, y, mz + dz, model.replace('{f}', I.facing_for(model, toward=toward)))
                v.stats['auto_mesa'] += 1

    def light_room(self, r):
        v, y = self.v, r['y']
        cells = r['cells']
        xs = sorted(c[0] for c in cells)
        zs = sorted(c[1] for c in cells)
        best = None
        for cx, cz in sorted(cells, key=lambda c: abs(c[0] - xs[len(xs) // 2]) + abs(c[1] - zs[len(zs) // 2])):
            h = self.headroom(cx, y, cz)
            if h >= 3 and wallish(v.get(cx, y + h, cz)) and passable(v.get(cx, y + h - 1, cz)):
                best = (cx, y + h - 1, cz)
                break
        if best:
            v.set(*best, 'minecraft:lantern[hanging=true,waterlogged=false]')
            v.stats['lanterna'] += 1

    # ------------------------------------------------ loot de containers que ficaram sem
    def containers(self):
        v = self.v
        for x, y, z in v.cells():
            s = v.g[y][z][x]
            if is_air(s) or (x, y, z) in v.loot or not CONTAINER.search(bid(s)):
                continue
            kind = self.room_kind.get((x, y, z))
            if kind is None:
                for dx, dz in DIRS.values():
                    kind = self.room_kind.get((x + dx, y, z + dz))
                    if kind:
                        break
            theme = {'cozinha': 'kitchen', 'sala_cozinha': 'kitchen', 'quarto': 'bedroom', 'banheiro': 'bathroom',
                     'sotao': 'home', 'sala': 'home', 'biblioteca': 'office', 'escritorio': 'office', 'atelie': 'home',
                     'costura': 'clothing', 'musica': 'home', 'estufa': 'farm', 'quarto_crianca': 'bedroom',
                     'oficina': 'workshop', 'encantamento': 'luxury', 'alquimia': 'clinic', 'create': 'workshop',
                     'ferreiro': 'workshop', 'artesao': 'clothing', 'fazendeiro': 'farm'}.get(kind)
            if theme is None:
                theme = 'home' if v.covered(x, y, z) else 'farm'
            if any(WORKSHOP.match(nm(v.get(x + dx, y + dy, z + dz))) for dx in range(-2, 3) for dz in range(-2, 3) for dy in (-1, 0, 1)):
                theme = 'workshop'
            v.loot[(x, y, z)] = theme

    def run(self):
        self.cleanup()
        self.map_rooms()
        self.outdoor_furnaces()
        self.kitchen()
        self.kitchen_tops()
        self.bathroom()
        self.beds()
        self.wool_beds()
        self.seats()
        self.lights()
        self.furnish_empty()
        self.floating_thin()
        self.containers()
        return self.v.stats
