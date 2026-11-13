"""Dense interior furnishing ("conscious block vomit") for the schematic village houses.

Runs after vanilla_furni (rooms already detected and the basic furniture placed) and the per-house RETOUCH.
For every room:
- a walking path is reserved: shortest paths between doors, stairs, ladders, openings and the access cell of
  every existing interactive block (bed, container, stove...). Some path cells get a rug;
- every other free floor cell is filled from the room catalog: wall pieces against walls, free-standing pieces
  elsewhere, facing the path. Rooms of a themed house use the theme catalog;
- every surface (tables, crates, barrels, counters, desks) gets something on top: decor or placeable food;
- walls get sporadic banners and high shelves with decor;
- armor stands are written as MARKER blocks; sunlitTownsLife.js replaces them by an equipped armor stand
  (Lost Cities cannot place entities).
Blocks are only used when they really exist (registry + lang key, or vanilla) and are single-block.
"""
import re
import zlib

import mapping as M
import vanilla_furni as VF
from loot import LANG

DIRS = VF.DIRS  # side -> (dx, dz)
OPP = VF.OPP
bid, nm, props, is_air, passable, wallish = VF.bid, VF.nm, VF.props, VF.is_air, VF.passable, VF.wallish
place = VF.place
MARKER = 'minecraft:structure_void'
COLORS = ['red', 'blue', 'green', 'brown', 'gray', 'light_blue', 'yellow', 'white', 'pink', 'cyan', 'orange', 'lime', 'purple']
MULTI_PROPS = {'part', 'half', 'width', 'height', 'type_part', 'segment'}

INTERACTIVE = re.compile(r'_bed$|chest$|barrel$|cabinet|drawer|crate$|fridge|freezer|stove|oven|furnace|smoker|sink|basin|'
                         r'toilet|_bath$|crafting_table|smithing|anvil|grindstone|loom|lectern|enchanting|brewing|cauldron|'
                         r'cutting_board|workbench|desk$|bookshelf|cartography|stonecutter|composter|jukebox|press$|depot$')
SUPPORT = re.compile(r'_table$|^table_|desk$|counter|cabinetry|_drawer$|drawers$|dresser|_cabinet$|'
                     r'side_table|nightstand|workbench|artist_table|cartography_table|crafting_table|smithing_table|fletching_table')
SEATING = re.compile(r'_table$|^table_|desk$|chair|stool|sofa|couch|_bench$|^bench$|armchair|_seat$')
# storage blocks whose front must face open floor (a drawer facing a wall is unusable)
FRONT_FACING = re.compile(r'drawer|cabinet')
# ordinary furniture is not capped per room (chests, crates, shelves, plants; tables ARE capped at 2)
GENERIC = re.compile(r'side_table|_crate$|crate$|^barrel$|^chest$|_drawer$|storage_cabinet|bookshelf$|^potted_|_bag$|'
                     r'^sack$|_cabinet$|plant_pot')
NOT_SUPPORT = re.compile(r'storage_cabinet|kitchen_storage_cabinet|chest$|sink|basin|stove|oven|fridge|freezer|wall_')


def real(state):
    """state exists in game (registry + lang, or vanilla) and is a single block"""
    b = bid(state)
    if not M.exists(b) or not (b.startswith('minecraft:') or b in LANG):
        return False
    reg = M.REG['blocks'].get(b) or {}
    return not (set(reg) & MULTI_PROPS)


# ---------------------------------------------------------------- catalogs
# wall: needs a wall behind (facing from the wall); floor: free standing (faces the path);
# top: goes on any support; unique: once per room, placed first; armor: chance per free cell of an armor stand
def _cat(wall=(), floor=(), top=(), unique=(), armor=0.0, loot='home'):
    return {'wall': list(wall), 'floor': list(floor), 'top': list(top), 'unique': list(unique), 'armor': armor, 'loot': loot}


TOP_HOME = ['cluttered:stack_of_books[facing={f},waterlogged=false]', 'cluttered:row_of_small_books[facing={f},waterlogged=false]',
            'minecraft:candle[candles=3,lit=false,waterlogged=false]', 'minecraft:potted_fern', 'minecraft:potted_azalea_bush',
            'cluttered:two_flower_pots[facing={f},waterlogged=false]', 'cluttered:paper_pile[facing={f},waterlogged=false]',
            'supplementaries:jar', 'cluttered:small_glass_jars[facing={f},waterlogged=false]', 'minecraft:flower_pot',
            'cluttered:basket_of_flowers[facing={f},waterlogged=false]', 'cluttered:traditional_radio[facing={f},has_record=false,waterlogged=false]',
            'tanukidecor:classic_vase[facing={f}]', 'tanukidecor:alarm_clock[facing={f}]', 'cluttered:book_open[facing={f},waterlogged=false]']
TOP_FOOD = ['displaydelight:plated_hamburger[facing={f}]', 'displaydelight:plated_cookie[facing={f}]',
            'displaydelight:small_plated_apple_pie_slice[facing={f}]', 'displaydelight:plated_dumplings[facing={f}]',
            'farmersdelight:apple_pie[bites=0,facing={f}]', 'bakery:bread_block[facing={f},stack=3]', 'bakery:strawberry_cake[cuts=0,facing={f}]',
            'meadow:cheese_block[cuts=0,facing={f}]', 'kaleidoscope_cookery:apple_platter[facing={f},servings=4]',
            'cluttered:jam_jars[facing={f},stacked=false]', 'cluttered:sliced_bread[facing={f},waterlogged=false]',
            'cluttered:pastry_plate[facing={f},waterlogged=false]', 'farmersdelight:cutting_board[facing={f}]',
            'cluttered:small_spice_jars[facing={f}]', 'farm_and_charm:farmers_bread_block[bites=0,facing={f}]',
            'farmersdelight:roast_chicken_block[facing={f},servings=4]', 'vintagedelight:meat_pizza[bites=0,facing={f}]']
CRATES = ['culturaldelights:eggplant_crate', 'hearthandharvest:apple_crate', 'hearthandharvest:blueberry_crate', 'hearthandharvest:raspberry_crate',
          'hearthandharvest:raspberry_crate', 'farmersdelight:rice_bag', 'farm_and_charm:potato_bag[facing={f}]',
          'hearthandharvest:apple_crate', 'vintagedelight:cucumber_crate', 'supplementaries:sack[open=false]']


def catalogs(w, c):
    drawer = f'refurbished_furniture:{w}_drawer[facing={{f}},left=false,right=false,open=false]'
    cabinet = f'refurbished_furniture:{w}_storage_cabinet[facing={{f}},hinge=left,open=false]'
    table = f'refurbished_furniture:{w}_table[east=false,north=false,south=false,west=false]'
    desk = f'refurbished_furniture:{w}_desk[facing={{f}},left=false,right=false]'
    crate = f'refurbished_furniture:{w}_crate[open=false]'
    sofa = f'another_furniture:{c}_sofa[facing={{f}},type=single]'
    side = f'redeco:{w}_side_table[facing={{f}},open=false]'
    chest = 'minecraft:chest[facing={f},type=single,waterlogged=false]'
    barrel = 'minecraft:barrel[facing=up,open=false]'
    pots = ['minecraft:potted_fern', 'minecraft:potted_flowering_azalea_bush', 'minecraft:potted_bamboo', 'minecraft:potted_cactus',
            'cluttered:cat_plant_pot_orange[facing={f},waterlogged=false]']
    fd_cab = f'farmersdelight:{w}_cabinet[facing={{f}},open=false]'
    generic_floor = [table, side, crate, barrel] + pots[:3]
    generic_wall = [drawer, cabinet, chest, barrel]
    cats = {
        'sala': _cat(wall=['minecraft:bookshelf', drawer, sofa, cabinet, side, 'minecraft:bookshelf', barrel],
                     floor=[table, sofa, side] + pots[:3] + [crate], top=TOP_HOME + TOP_FOOD[:6], armor=0.04),
        'cozinha': _cat(wall=[f'refurbished_furniture:{w}_kitchen_drawer[facing={{f}},open=false]', fd_cab, barrel,
                              f'refurbished_furniture:{w}_kitchen_cabinetry[facing={{f}},shape=default]'] + CRATES[:4],
                        floor=[table, barrel, 'farmersdelight:wooden_basket[facing=up]'] + pots[:1], top=TOP_FOOD, loot='kitchen'),
        'quarto': _cat(wall=[drawer, cabinet, 'minecraft:bookshelf', chest, side, f'another_furniture:{w}_shelf[facing={{f}},horizontal=single]'],
                       floor=[side, crate, chest] + pots[:2], top=TOP_HOME, armor=0.08, loot='bedroom'),
        'banheiro': _cat(wall=[cabinet, side], floor=pots[:2], top=['minecraft:candle[candles=2,lit=false,waterlogged=false]',
                                                                   'supplementaries:jar', 'minecraft:potted_fern'], loot='bathroom'),
        'sotao': _cat(wall=[barrel, crate, chest, 'supplementaries:sack[open=false]'] + CRATES[:3],
                      floor=[crate, barrel, 'supplementaries:sack[open=false]'] + CRATES,
                      top=TOP_HOME[:8], armor=0.05),
        'encantamento': _cat(wall=['minecraft:bookshelf', 'minecraft:bookshelf', 'minecraft:lectern[facing={f},has_book=false,powered=false]',
                                   'minecraft:chiseled_bookshelf[facing={f},slot_0_occupied=true,slot_1_occupied=true,slot_2_occupied=false,'
                                   'slot_3_occupied=true,slot_4_occupied=false,slot_5_occupied=true]', cabinet],
                             floor=['minecraft:amethyst_block', 'minecraft:bookshelf', side, desk, 'supplementaries:globe[facing={f}]',
                                    'minecraft:calcite'],
                             top=['minecraft:amethyst_cluster[facing=up,waterlogged=false]', 'minecraft:candle[candles=4,lit=false,waterlogged=false]',
                                  'minecraft:purple_candle[candles=3,lit=false,waterlogged=false]', 'cluttered:book_open[facing={f},waterlogged=false]',
                                  'cluttered:stack_of_books[facing={f},waterlogged=false]', 'cluttered:vial_stand[facing={f},waterlogged=false]',
                                  'minecraft:end_rod[facing=up]', 'minecraft:small_amethyst_bud[facing=up,waterlogged=false]'],
                             unique=['minecraft:enchanting_table'], armor=0.06, loot='luxury'),
        'alquimia': _cat(wall=[cabinet, 'minecraft:bookshelf', barrel, f'another_furniture:{w}_shelf[facing={{f}},horizontal=single]',
                               'minecraft:cauldron'],
                         floor=['minecraft:water_cauldron[level=3]', table, side, 'botania:apothecary_default', barrel] + pots[:2],
                         top=['cluttered:vial_stand[facing={f},waterlogged=false]', 'cluttered:small_glass_jars[facing={f},waterlogged=false]',
                              'supplementaries:jar', 'minecraft:brewing_stand[has_bottle_0=true,has_bottle_1=false,has_bottle_2=true]',
                              'minecraft:candle[candles=2,lit=false,waterlogged=false]', 'cluttered:small_spice_jars[facing={f}]',
                              'minecraft:potted_crimson_fungus', 'minecraft:potted_brown_mushroom', 'minecraft:potted_red_mushroom'],
                         unique=['minecraft:brewing_stand[has_bottle_0=false,has_bottle_1=false,has_bottle_2=false]'], loot='clinic'),
        'create': _cat(wall=['create:mechanical_crafter[facing={f},pointing=up]', 'create:deployer[facing={f}]',
                              'create:gearbox[axis=y]', 'create:item_drain[facing={f}]',
                              barrel, 'create:brown_toolbox[facing={f},waterlogged=false]', chest, 'create:millstone'],
                        floor=['create:depot', 'create:basin[facing=down]', 'create:mechanical_mixer', 'create:millstone',
                               'create:mechanical_press[facing={f}]', 'create:blaze_burner[blaze=smouldering,facing={f}]',
                               'create:deployer[facing={f}]', 'create:mechanical_crafter[facing={f},pointing=up]',
                               'create:copper_backtank[facing={f},waterlogged=false]', 'create_enchantment_industry:printer[facing={f}]',
                               'create_central_kitchen:blaze_stove[facing={f}]', 'create:spout'],
                       top=['create:clipboard[face=floor,facing={f},waterlogged=false,writing=false]',
                            'create:brown_toolbox[facing={f},waterlogged=false]', 'cluttered:paper_pile[facing={f},waterlogged=false]',
                            'minecraft:lantern[hanging=false,waterlogged=false]'],
                       unique=['create:mechanical_arm[ceiling=false]'], armor=0.03, loot='workshop'),
        'ferreiro': _cat(wall=[f'redeco:{w}_sword_mount[facing={{f}}]', 'farm_and_charm:tool_rack[facing={f}]', barrel, chest,
                               'minecraft:blast_furnace[facing={f},lit=false]', 'minecraft:grindstone[face=floor,facing={f}]'],
                         floor=['minecraft:anvil[facing={f}]', 'minecraft:chipped_anvil[facing={f}]', 'minecraft:smithing_table',
                                'minecraft:grindstone[face=floor,facing={f}]', barrel, 'minecraft:target[power=0]', crate],
                         top=['minecraft:lantern[hanging=false,waterlogged=false]', 'minecraft:chain[axis=y,waterlogged=false]',
                              'cluttered:paper_pile[facing={f},waterlogged=false]', 'minecraft:candle[candles=2,lit=false,waterlogged=false]'],
                         unique=['minecraft:smithing_table'], armor=0.25, loot='workshop'),
        'artesao': _cat(wall=['minecraft:loom[facing={f}]', drawer, cabinet, f'another_furniture:{w}_shelf[facing={{f}},horizontal=single]',
                              'minecraft:jukebox[has_record=false]', 'minecraft:note_block'],
                        floor=['zetter:artist_table[facing={f}]', table, side, 'minecraft:note_block', sofa] + pots[:2],
                        top=['cluttered:box_of_paints[facing={f},waterlogged=false]', 'cluttered:paint_water_jar[facing={f},waterlogged=false]',
                             'cluttered:sewing_machine_antique[facing={f},waterlogged=false]', 'cluttered:scissors_and_thread[facing={f},waterlogged=false]',
                             'cluttered:basket_of_flowers[facing={f},waterlogged=false]', 'tanukidecor:antique_radio[facing={f}]'],
                        unique=['minecraft:loom[facing={f}]'], armor=0.06, loot='clothing'),
        'biblioteca': _cat(wall=['minecraft:bookshelf', 'minecraft:bookshelf', 'minecraft:bookshelf', cabinet,
                                 'minecraft:lectern[facing={f},has_book=false,powered=false]'],
                           floor=['minecraft:bookshelf', desk, table, sofa, side, 'supplementaries:globe[facing={f}]'],
                           top=TOP_HOME[:2] + ['cluttered:book_open[facing={f},waterlogged=false]', 'minecraft:candle[candles=3,lit=false,waterlogged=false]',
                                               'supplementaries:globe_sepia[facing={f}]', 'cluttered:paper_pile[facing={f},waterlogged=false]'],
                           loot='office'),
        'fazendeiro': _cat(wall=[barrel, fd_cab, chest, 'farm_and_charm:tool_rack[facing={f}]'] + CRATES[:5],
                           floor=CRATES + [barrel, 'minecraft:composter[level=4]', table],
                           top=TOP_FOOD[:8] + ['farmersdelight:wooden_basket[facing=up]', 'supplementaries:jar'], armor=0.04, loot='farm'),
        'floricultura': _cat(wall=['minecraft:potted_poppy', 'minecraft:potted_dandelion', 'minecraft:potted_cornflower', 'minecraft:potted_flowering_azalea_bush'],
                             floor=['cluttered:basket_of_flowers[facing={f},waterlogged=false]', 'minecraft:composter[level=0]',
                                    'dew_drop_farmland_growth:iron_sprinkler', 'minecraft:potted_azalea_bush'],
                             top=['minecraft:potted_poppy', 'minecraft:potted_dandelion', 'minecraft:flower_pot',
                                  'cluttered:two_flower_pots[facing={f},waterlogged=false]'], armor=0.0, loot='floricultura'),
        'adega': _cat(wall=['society:aging_cask', 'society:ancient_cask', barrel],
                      floor=['society:aging_cask', 'society:ancient_cask', barrel, crate],
                      top=['vinery:wine_bottle', 'vinery:apple_juice', 'vinery:red_grapejuice'], armor=0.0, loot='adega'),
        'torre_raio': _cat(wall=['minecraft:copper_block', 'minecraft:cut_copper', 'minecraft:lightning_rod'],
                           floor=['minecraft:copper_block', 'minecraft:cut_copper', 'minecraft:lightning_rod'],
                           top=['minecraft:lightning_rod', 'minecraft:copper_block'], armor=0.0, loot='torre_raio'),
        'laticinio': _cat(wall=['society:cheese_press[facing={f}]', 'society:mayonnaise_machine[facing={f}]', 'minecraft:barrel[facing={f}]'],
                          floor=['society:cheese_press[facing={f}]', 'society:mayonnaise_machine[facing={f}]', 'minecraft:barrel[facing=up,open=false]'],
                          top=['society:cheese_press[facing={f}]', 'society:mayonnaise_machine[facing={f}]'], armor=0.0, loot='laticinio'),
        'vinicola': _cat(wall=['society:wine_keg[facing={f}]', 'society:preserves_jar[facing={f}]', 'minecraft:barrel[facing={f}]'],
                         floor=['society:wine_keg[facing={f}]', 'minecraft:barrel[facing=up,open=false]'],
                         top=['vinery:wine_bottle', 'vinery:red_grapejuice', 'society:preserves_jar[facing={f}]'], armor=0.0, loot='vinicola'),
        'celeiro_neve': _cat(wall=['minecraft:packed_ice', 'minecraft:blue_ice'],
                             floor=['society:feeding_trough[facing={f}]', 'minecraft:packed_ice', 'minecraft:blue_ice'],
                             top=['minecraft:blue_ice', 'minecraft:packed_ice'], armor=0.0, loot='celeiro_neve'),
        'cabana_pescador': _cat(wall=['society:fish_pond_basket', 'crabbersdelight:crab_trap[facing={f}]'],
                                floor=['society:fish_pond[facing={f}]', 'crabbersdelight:crab_trap[facing={f}]', 'society:fish_pond_basket'],
                                top=['crabbersdelight:crab_trap[facing={f}]'], armor=0.0, loot='cabana_pescador'),
        'alfaiataria': _cat(wall=['legendarysurvivaloverhaul:sewing_table[facing={f}]', 'minecraft:white_wool', 'minecraft:gray_wool'],
                            floor=['legendarysurvivaloverhaul:sewing_table[facing={f}]', 'minecraft:white_wool', 'minecraft:gray_wool'],
                            top=['minecraft:white_wool', 'minecraft:gray_wool'], armor=0.0, loot='alfaiataria'),
        'seringueiro': _cat(wall=['society:tapper[facing={f}]', 'minecraft:barrel[facing={f}]'],
                            floor=['minecraft:barrel[facing=up,open=false]', 'society:tapper[facing={f}]'],
                            top=['pamhc2trees:apple_sapling', 'pamhc2trees:orange_sapling'], armor=0.0, loot='seringueiro'),
    }
    for t in THEMES + SPECIAL_THEMES:
        # a themed room is still a room of a house: theme pieces mixed with ordinary furniture
        cats[t]['floor'] += generic_floor
        cats[t]['wall'] += generic_wall
    return cats


# room kinds of vanilla_furni -> catalog
KIND_CAT = {'sala': 'sala', 'sala_cozinha': 'cozinha', 'cozinha': 'cozinha', 'quarto': 'quarto', 'quarto_crianca': 'quarto',
            'banheiro': 'banheiro', 'sotao': 'sotao', 'biblioteca': 'biblioteca', 'escritorio': 'biblioteca', 'atelie': 'artesao',
            'costura': 'artesao', 'musica': 'artesao', 'estufa': 'fazendeiro', 'oficina': 'ferreiro'}
THEMES = ('encantamento', 'alquimia', 'create', 'ferreiro', 'artesao', 'biblioteca', 'fazendeiro')
# one building each, outside the rotation (schematics.py CASAS); loot keys in loot.THEMES
SPECIAL_THEMES = ('floricultura', 'adega', 'torre_raio', 'laticinio', 'vinicola', 'celeiro_neve', 'cabana_pescador',
                  'alfaiataria', 'seringueiro')


class Clutter:
    def __init__(self, house, theme=None):
        self.h, self.v, self.theme = house, house.v, theme
        self.key = house.key
        w = house.wood
        self.cats = {k: {s: [b for b in lst if real(b)] if s in ('wall', 'floor', 'top', 'unique') else lst
                         for s, lst in cat.items()}
                     for k, cat in catalogs(w, self.pick('cor', COLORS)).items()}

    def pick(self, salt, seq):
        seq = list(seq)
        return seq[zlib.crc32(f'{self.key}|{salt}'.encode()) % len(seq)] if seq else None

    def chance(self, salt, p):
        return zlib.crc32(f'{self.key}|{salt}'.encode()) % 1000 < p * 1000

    # ------------------------------------------------ helpers
    def free(self, x, y, z):
        v = self.v
        # the cell above a trapdoor or ladder is the cellar hatch mouth: never place furniture or rugs there
        below = str(v.get(x, y - 1, z) or '')
        if 'trapdoor' in below or 'ladder' in below:
            return False
        return passable(v.get(x, y, z)) and passable(v.get(x, y + 1, z))

    def wall_side(self, x, y, z, cells):
        for d, (dx, dz) in DIRS.items():
            if (x + dx, z + dz) in cells:
                continue
            b = self.v.get(x + dx, y, z + dz)
            if wallish(b) and not re.search(r'_door$|ladder|_stairs$|trapdoor|glass|_pane$|window', nm(b)) and not VF.FURN.match(bid(b)):
                return d
        return None

    def open_front_wall(self, x, y, z, cells, pref):
        """side to back a front-facing piece against: the preferred one if its front cell is open,
        otherwise another wall side whose front cell is air; None when no side works"""
        v = self.v
        order = [pref] + [d for d in DIRS if d != pref]
        for d in order:
            dx, dz = DIRS[d]
            if (x + dx, z + dz) in cells:
                continue
            b = v.get(x + dx, y, z + dz)
            if not wallish(b) or re.search(r'_door$|ladder|_stairs$|trapdoor|glass|_pane$|window', nm(b)) or VF.FURN.match(bid(b)):
                continue
            fx, fz = x - dx, z - dz  # the facing points away from the wall
            if is_air(v.get(fx, y, fz)) and passable(v.get(fx, y + 1, fz)):
                return d
        return None

    def anchors(self, y, cells):
        v, out = self.v, []
        for cx, cz in sorted(cells):
            if passable(v.get(cx, y - 1, cz)):
                out.append((cx, cz))  # stair hole from below
                continue
            for d, (dx, dz) in DIRS.items():
                q = (cx + dx, cz + dz)
                for dy in (0, 1):
                    b = v.get(q[0], y + dy, q[1])
                    n = nm(b)
                    if n.endswith('_door') or n == 'ladder' or n.endswith('_fence_gate') or \
                            n.endswith('_stairs') and dy == 0 and passable(v.get(q[0], y + 1, q[1])) or \
                            n.endswith('_trapdoor') and props(b).get('open') == 'true':
                        out.append((cx, cz))
                if q not in cells and passable(v.get(q[0], y, q[1])) and passable(v.get(q[0], y + 1, q[1])):
                    out.append((cx, cz))  # opening to another room / outside
        # one free access cell per interactive block touching the room: the one closest to the entrances
        base = [a for a in out if self.free(a[0], y, a[1])]
        blocks = {}
        for cx, cz in sorted(cells):
            if not self.free(cx, y, cz):
                continue
            for dx, dz in DIRS.values():
                q = (cx + dx, cz + dz)
                b = v.get(q[0], y, q[1])
                if q not in cells and not is_air(b) and INTERACTIVE.search(nm(b)) or \
                        q in cells and not is_air(b) and INTERACTIVE.search(nm(b)):
                    blocks.setdefault(q, []).append((cx, cz))
        for q, opts in sorted(blocks.items()):
            if base:
                opts.sort(key=lambda c: min(abs(c[0] - a[0]) + abs(c[1] - a[1]) for a in base))
            out.append(opts[0])
        seen, res = set(), []
        for a in out:
            if a not in seen and self.free(a[0], y, a[1]):
                seen.add(a)
                res.append(a)
        return res

    def path(self, y, cells, anchors):
        free = {c for c in cells if self.free(c[0], y, c[1])}
        if not anchors:
            xs, zs = sorted(c[0] for c in free), sorted(c[1] for c in free)
            mid = min(free, key=lambda c: abs(c[0] - xs[len(xs) // 2]) + abs(c[1] - zs[len(zs) // 2]), default=None)
            return {mid} if mid else set()
        root = anchors[0]
        prev, queue = {root: None}, [root]
        for cur in queue:
            for dx, dz in DIRS.values():
                q = (cur[0] + dx, cur[1] + dz)
                if q in free and q not in prev:
                    prev[q] = cur
                    queue.append(q)
        keep = set()
        for a in anchors:
            while a is not None and a in prev and a not in keep:
                keep.add(a)
                a = prev[a]
        return keep

    def reach(self, y, cells, path, dist=3):
        """the whole room stays walkable: a free cell farther than `dist` from the walkway gets a branch of the
        walkway up to it (shortest route through free cells)"""
        free = {c for c in cells if self.free(c[0], y, c[1])}
        path = set(path) & free or set(list(free)[:1])
        for _ in range(len(free)):
            far = [c for c in sorted(free) if min(abs(c[0] - p[0]) + abs(c[1] - p[1]) for p in path) > dist]
            if not far:
                break
            target = far[0]
            prev, queue = {p: None for p in path}, list(path)
            for cur in queue:
                if cur == target:
                    break
                for dx, dz in DIRS.values():
                    q = (cur[0] + dx, cur[1] + dz)
                    if q in free and q not in prev:
                        prev[q] = cur
                        queue.append(q)
            if target not in prev:
                free.discard(target)  # not reachable at all: leave it to the filler
                continue
            node = target
            while node is not None and node not in path:
                path.add(node)
                node = prev[node]
        return path

    def spine(self, y, cells):
        """fallback walkway when the entrances were not found: a corridor along the longest axis through the
        middle of the room plus the cells next to any opening"""
        free = {c for c in cells if self.free(c[0], y, c[1])}
        if not free:
            return set()
        xs, zs = sorted(c[0] for c in free), sorted(c[1] for c in free)
        mx, mz = xs[len(xs) // 2], zs[len(zs) // 2]
        if xs[-1] - xs[0] >= zs[-1] - zs[0]:
            out = {c for c in free if c[1] == mz}
        else:
            out = {c for c in free if c[0] == mx}
        return out

    def toward_path(self, x, z, path, cells):
        for d, (dx, dz) in DIRS.items():
            if (x + dx, z + dz) in path:
                return d
        xs, zs = sorted(c[0] for c in cells), sorted(c[1] for c in cells)
        mx, mz = xs[len(xs) // 2], zs[len(zs) // 2]
        if abs(mx - x) >= abs(mz - z):
            return 'east' if mx > x else 'west'
        return 'south' if mz > z else 'north'

    # ------------------------------------------------ main
    def run(self):
        h, v = self.h, self.v
        # roof guard: stairs and slabs of the top 6 layers of a vila are restored after the pass
        roof_from = len(v.g) - 6
        roof = {(x, y, z): v.get(x, y, z) for x, y, z in v.cells()
                if y >= roof_from and nm(v.get(x, y, z)).endswith(('_stairs', '_slab'))} if self.key.startswith('vila') else {}
        for y, comp in h.rooms():
            cells = set(comp)
            kinds = [h.room_kind.get((cx, y, cz)) for cx, cz in comp]
            kind = max(set(kinds), key=kinds.count) if any(kinds) else 'sala'
            cat = self.cats.get(kind) or self.cats.get(KIND_CAT.get(kind, 'sala'), self.cats['sala'])
            self.room(y, cells, cat, kind)
        for (x, y, z), s0 in roof.items():
            if v.get(x, y, z) != s0:
                v.set(x, y, z, s0)
                v.stats['telhado_mantido'] = v.stats.get('telhado_mantido', 0) + 1
        return v.stats

    def room(self, y, cells, cat, kind):
        v = self.v
        if len(cells) < 4:
            return
        anchors = self.anchors(y, cells)
        path = self.path(y, cells, anchors)
        if len(anchors) < 2:
            path |= self.spine(y, cells)
        path = self.reach(y, cells, path)
        cap = max(1, len(cells) // 22)
        used = {}
        tables = 0
        armor_left = 2
        uniques = list(cat['unique'])
        order = sorted(cells, key=lambda c: zlib.crc32(f'{self.key}{y}{c}'.encode()))
        supports = []
        for cx, cz in order:
            if (cx, cz) in path or not self.free(cx, y, cz) or not v.on_floor(cx, y, cz) or not v.covered(cx, y, cz):
                continue
            salt = f'{kind}{y}{cx}{cz}'
            wall = self.wall_side(cx, y, cz, cells)
            # 2026-10-09: cozinhas saem do jeito que o vanilla_furni/RETOUCH
            # desenhou (so peca de parede): movel solto no meio da cozinha
            # (mesa grudada em bancada, cadeira na frente da geladeira) nao faz
            # sentido. Nos outros comodos o solto preenche ~45% das celulas
            # (25% em comodo pequeno) para o piso continuar legivel.
            if not wall and kind in ('cozinha', 'sala_cozinha'):
                continue
            fill = 0.45 if len(cells) >= 20 else 0.25
            if not wall and not self.chance(salt + 'fill', fill):
                continue
            # free-standing pieces never touch a table or a seat: that is room to sit and to pass (a table piece
            # dropped between two chairs looked like a lost extension of the dining table)
            if not wall and any(SEATING.search(nm(v.get(cx + dx, y, cz + dz))) for dx, dz in DIRS.values()):
                continue
            if cat['armor'] and armor_left and not wall and len(cells) >= 16 and self.chance(salt + 'armor', cat['armor']) and self.free(cx, y + 1, cz):
                v.set(cx, y, cz, MARKER)
                armor_left -= 1
                v.stats['clutter_armor_stand'] += 1
                continue
            if uniques:
                block = uniques.pop(0)
                face = wall and OPP[wall] or self.toward_path(cx, cz, path, cells)
                st = block.replace('{f}', face)
            else:
                lst = cat['wall'] if wall and cat['wall'] else cat['floor']
                lst = [b for b in lst if used.get(bid(b), 0) < cap or GENERIC.search(nm(b))]
                if not lst:
                    continue
                b = self.pick(salt, lst)
                # free-standing TABLES are capped (2 per room) and never glued to support/seating:
                # no table next to a counter, cabinet, chair or another table (cozy_cabin ficava
                # com mesa colada em bancada e mesa do lado de mesa)
                if not wall and re.search(r'_table$', nm(b)) and 'side_table' not in nm(b):
                    if tables >= 2 or any(SEATING.search(nm(v.get(cx + dx, y, cz + dz))) or
                                          SUPPORT.search(nm(v.get(cx + dx, y, cz + dz))) for dx, dz in DIRS.values()):
                        continue
                    tables += 1
                if wall and cat['wall']:
                    if FRONT_FACING.search(nm(b)):
                        wall = self.open_front_wall(cx, y, cz, cells, wall)
                        if wall is None:
                            continue
                    st = place(b, wall)
                else:
                    toward = self.toward_path(cx, cz, path, cells)
                    st = b.replace('{f}', VF.I.facing_for(b, toward=toward)) if '{f}' in b else b
                used[bid(b)] = used.get(bid(b), 0) + 1
            v.set(cx, y, cz, st, loot=cat['loot'] if VF.CONTAINER.search(bid(st)) else None)
            v.stats['clutter_movel'] += 1
            if not wall and re.search(r'_table$', nm(st)) and 'side_table' not in nm(st):
                self.chairs(y, cx, cz, cells, path)
            if SUPPORT.search(nm(st)) and not NOT_SUPPORT.search(nm(st)):
                supports.append((cx, cz, wall))
        # existing supports of the room too (tables and counters placed by vanilla_furni)
        for cx, cz in cells:
            b = v.get(cx, y, cz)
            if not is_air(b) and SUPPORT.search(nm(b)) and not NOT_SUPPORT.search(nm(b)) and (cx, cz, None) not in supports:
                supports.append((cx, cz, self.wall_side(cx, y, cz, cells)))
        for cx, cz, wall in supports:
            if not passable(v.get(cx, y + 1, cz)) or not is_air(v.get(cx, y + 1, cz)) or not v.covered(cx, y + 1, cz):
                continue
            salt = f'top{kind}{y}{cx}{cz}'
            if not cat['top'] or not self.chance(salt, 0.6):
                continue
            b = self.pick(salt, cat['top'])
            f = OPP[wall] if wall else self.pick(salt + 'f', list(DIRS))
            v.set(cx, y + 1, cz, b.replace('{f}', VF.I.facing_for(b, toward=f) if '{f}' in b else f))
            v.stats['clutter_em_cima'] += 1
        self.rug(y, cells, path, kind)
        self.wall_decor(y, cells, kind)

    def chairs(self, y, tx, tz, cells, path, most=2):
        """a free-standing table gets chairs on free cells around it (off the walkway), facing it"""
        v = self.v
        model = f'refurbished_furniture:{self.h.wood}_chair[facing={{f}},tucked=false]'
        if not real(model):
            return
        n = 0
        for d, (dx, dz) in DIRS.items():
            q = (tx + dx, tz + dz)
            if n >= most or q not in cells or q in path or not self.free(q[0], y, q[1]) or not v.on_floor(q[0], y, q[1]):
                continue
            v.set(q[0], y, q[1], model.replace('{f}', VF.I.facing_for(model, toward=OPP[d])))
            v.stats['clutter_cadeira'] += 1
            n += 1

    def rug(self, y, cells, path, kind):
        """rug on the path cells in the middle of the room. 2026-10-10: movel que caiu no meio
        da passagem vira tapete (pedido do dono) em vez de bloquear o caminho."""
        v = self.v
        if len(path) < 4 or kind in ('banheiro', 'cozinha', 'sala_cozinha'):
            return
        xs, zs = sorted(c[0] for c in cells), sorted(c[1] for c in cells)
        mx, mz = xs[len(xs) // 2], zs[len(zs) // 2]
        color = self.pick(f'rugcor{y}', COLORS)
        for cx, cz in path:
            if abs(cx - mx) > 2 or abs(cz - mz) > 2 or not v.on_floor(cx, y, cz):
                continue
            s = v.get(cx, y, cz)
            if is_air(s):
                if not self.chance(f'rug{y}{len(cells)}', 0.7):
                    continue
                v.set(cx, y, cz, f'minecraft:{color}_carpet')
                v.stats['clutter_tapete'] += 1
            elif re.search(r'sofa|chair|stool|_table$|side_table|crate|_pot$|lantern', nm(s)):
                v.set(cx, y, cz, f'minecraft:{color}_carpet')
                v.stats['movel_no_caminho_virou_tapete'] += 1

    def wall_decor(self, y, cells, kind):
        """sporadic banners and high shelves with decor on the walls (y+2)"""
        v = self.v
        tops = self.cats['sala']['top']
        for cx, cz in sorted(cells):
            wall = self.wall_side(cx, y + 2, cz, cells) if v.inside(cx, y + 2, cz) else None
            if not wall or not is_air(v.get(cx, y + 2, cz)) or not v.covered(cx, y + 2, cz):
                continue
            salt = f'parede{kind}{y}{cx}{cz}'
            if not self.chance(salt, 0.08):
                continue
            face = OPP[wall]
            if is_air(v.get(cx, y + 3, cz)) and v.covered(cx, y + 3, cz) and self.chance(salt + 'p', 0.6):
                shelf = f'another_furniture:{self.h.wood}_shelf[facing={face},horizontal=single]'
                if real(shelf):
                    v.set(cx, y + 2, cz, shelf)
                    b = self.pick(salt + 'd', tops)
                    v.set(cx, y + 3, cz, b.replace('{f}', face))
                    v.stats['clutter_prateleira_alta'] += 1
                    continue
            banner = f'minecraft:{self.pick(salt + "b", COLORS)}_wall_banner[facing={face}]'
            v.set(cx, y + 2, cz, banner)
            v.stats['clutter_estandarte'] += 1
