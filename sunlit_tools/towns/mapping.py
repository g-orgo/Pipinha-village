"""Mapeia estados de bloco do DeceasedCraft para blocos que existem no Sunlit Valley.

Regra de ouro: todo estado devolvido tem que existir no registry.json e so carrega
propriedades conhecidas, senao o Lost Cities aborta o chunk inteiro.
"""
import json, os, re, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, 'registry.json')))
BLOCKS = REG['blocks']
ITEMS = set(REG['items'])

COLORS = ['light_blue', 'light_gray', 'white', 'orange', 'magenta', 'yellow', 'lime', 'pink', 'gray',
          'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black']
VWOODS = ['dark_oak', 'oak', 'spruce', 'birch', 'jungle', 'acacia', 'mangrove', 'cherry', 'crimson', 'warped', 'bamboo']
# madeiras de outros mods -> madeira vanilla equivalente
WOOD_ALIAS = {'fir': 'spruce', 'pine': 'spruce', 'redwood': 'spruce', 'maple': 'birch', 'palm': 'jungle',
              'willow': 'mangrove', 'dead': 'dark_oak', 'hellbark': 'crimson', 'jacaranda': 'cherry',
              'magic': 'birch', 'empyreal': 'birch', 'umbran': 'warped', 'snowblossom': 'cherry',
              'roble': 'oak', 'robleosc': 'dark_oak', 'jungla': 'jungle', 'ebano': 'dark_oak', 'kelp': 'jungle',
              'chip_wood': 'oak', 'treated_wood': 'spruce', 'treated': 'spruce'}
COLOR_ALIAS = {'grey': 'gray', 'kelp': 'green', 'beige': 'white', 'skyblue': 'light_blue', 'rainbow': 'lime',
               'blanca': 'white', 'blanco': 'white', 'negra': 'black', 'negro': 'black', 'roja': 'red', 'rojo': 'red',
               'azul': 'blue', 'azulclara': 'light_blue', 'verde': 'green', 'gris': 'gray', 'grisclara': 'light_gray',
               'grisclaro': 'light_gray', 'cafe': 'brown', 'amarilla': 'yellow', 'naranja': 'orange',
               'morada': 'purple', 'rosa': 'pink', 'magenta': 'magenta', 'cian': 'cyan'}

# Blocos que existem aqui mas sao "apocalipticos" ou perigosos dentro de uma vila viva
BANNED_EXISTING = {
    'minecraft:cobweb': None, 'minecraft:spawner': None, 'minecraft:command_block': None,
    'minecraft:chain_command_block': None, 'minecraft:repeating_command_block': None,
    'minecraft:fire': None, 'minecraft:soul_fire': None, 'minecraft:tnt': None,
    'minecraft:skeleton_skull': None, 'minecraft:skeleton_wall_skull': None,
    'minecraft:zombie_head': None, 'minecraft:zombie_wall_head': None,
    'minecraft:wither_skeleton_skull': None, 'minecraft:wither_skeleton_wall_skull': None,
    'minecraft:creeper_head': None, 'minecraft:creeper_wall_head': None,
    'minecraft:player_head': None, 'minecraft:player_wall_head': None,
    'minecraft:lava': None, 'minecraft:magma_block': 'minecraft:stone_bricks',
    'minecraft:infested_stone': 'minecraft:stone', 'minecraft:infested_stone_bricks': 'minecraft:stone_bricks',
    'minecraft:infested_cracked_stone_bricks': 'minecraft:cracked_stone_bricks',
    'minecraft:sculk': 'minecraft:moss_block', 'minecraft:sculk_vein': None,
    'minecraft:redstone_wire': None,
}

# propriedades de blocos com render de entidade (blockstate JSON nao lista nada)
def be_props(bid):
    # create:blaze_burner: o blockstate JSON nao tem variantes (o blaze e renderizado pela
    # block entity); props reais pelo codigo do Create (BlazeBurnerBlock.HEAT_LEVEL + FACING):
    # blaze=none e o queimador VAZIO, smouldering+ ja tem blaze dentro (estavel sem combustivel)
    if bid == 'create:blaze_burner':
        return {'blaze': ['none', 'smouldering', 'fading', 'kindled', 'seething'], 'facing': 'nsew'}
    ns, n = bid.split(':')
    if ns not in ('minecraft', 'lootr'):
        return None
    if n.endswith('_bed'): return {'facing': 'nsew', 'part': ['head', 'foot'], 'occupied': ['false']}
    if n in ('chest', 'trapped_chest', 'lootr_chest', 'lootr_trapped_chest'):
        return {'facing': 'nsew', 'type': ['single', 'left', 'right'], 'waterlogged': ['false', 'true']}
    if n == 'ender_chest': return {'facing': 'nsew', 'waterlogged': ['false', 'true']}
    if n.endswith('_wall_hanging_sign') or n.endswith('_wall_sign'): return {'facing': 'nsew', 'waterlogged': ['false', 'true']}
    if n.endswith('_hanging_sign'): return {'rotation': [str(i) for i in range(16)], 'attached': ['false', 'true'], 'waterlogged': ['false', 'true']}
    if n.endswith('_sign'): return {'rotation': [str(i) for i in range(16)], 'waterlogged': ['false', 'true']}
    if n.endswith('_wall_banner'): return {'facing': 'nsew'}
    if n.endswith('_banner'): return {'rotation': [str(i) for i in range(16)]}
    if n.endswith('shulker_box') or n == 'lootr_shulker': return {'facing': ['north', 'south', 'east', 'west', 'up', 'down']}
    if n == 'decorated_pot': return {'facing': 'nsew', 'waterlogged': ['false', 'true']}
    return None


# blockstate existe no jar mas o bloco NUNCA registra no jogo: o Lost Cities
# derruba o chunk com "Unknown block type". Vistos no latest.log:
# displaydelight:bowl (DisplayDelight 1.7.0 registra o item, nao o bloco),
# beachparty:coconut_hanging (nao registrado).
GHOSTS = {'displaydelight:bowl', 'beachparty:coconut_hanging'}
# aquaculture:*_fish_mount e entidade (como moldura): o blockstate existe so para o modelo
GHOST_RX = re.compile(r'^aquaculture:[a-z_]+_fish_mount$')


def exists(bid):
    return bid in BLOCKS and bid not in GHOSTS and not GHOST_RX.match(bid)


IMPLICIT = {  # propriedades reais que o JSON de blockstate vanilla nao lista
    '_leaves': {'persistent': ['true', 'false'], 'distance': [str(i) for i in range(1, 8)], 'waterlogged': ['false', 'true']},
    '_sapling': {'stage': ['0', '1']},
}


def valid_props(bid):
    p = BLOCKS.get(bid) or {}
    if bid.startswith('minecraft:'):
        for suf, extra in IMPLICIT.items():
            if bid.endswith(suf):
                return {**extra, **p}
    if not p:
        bp = be_props(bid)
        if bp:
            return {k: (['north', 'south', 'east', 'west'] if v == 'nsew' else v) for k, v in bp.items()}
    return p


def parse(state):
    if '[' in state:
        bid, rest = state.split('[', 1)
        props = {}
        for kv in rest.rstrip(']').split(','):
            if '=' in kv:
                k, v = kv.split('=', 1)
                props[k.strip()] = v.strip()
        return bid.strip(), props
    return state.strip(), {}


def fmt(bid, props):
    if not props:
        return bid
    return bid + '[' + ','.join(f'{k}={v}' for k, v in props.items()) + ']'


def clean_props(bid, props):
    vp = valid_props(bid)
    return {k: v for k, v in props.items() if k in vp and v in vp[k]}


def tokens(name):
    """extrai cor e madeira do nome do bloco de origem"""
    n = name.split(':')[-1]
    n = n.split('/')[-1]
    color = wood = None
    for c in COLORS:
        if re.search(rf'(^|_){c}(_|$)', n):
            color = c; break
    if not color:
        for a, c in COLOR_ALIAS.items():
            if re.search(rf'(^|_){a}(_|$)', n) or n.endswith(a):
                color = c; break
    for w in VWOODS:
        if re.search(rf'(^|_){w}(_|$)', n):
            wood = w; break
    if not wood:
        for a, w in WOOD_ALIAS.items():
            if re.search(rf'(^|_){a}(_|$)', n) or n.startswith(a):
                wood = w; break
    return color, wood


SALT = ''  # convert.py troca por predio: o mesmo bloco DC vira mods diferentes em cada predio


def pick(key, cands):
    """escolhe deterministicamente um candidato existente (variedade entre mods e entre predios)"""
    ok = [c for c in cands if exists(c[0] if isinstance(c, tuple) else c)]
    if not ok:
        return None
    return ok[zlib.crc32((key + '|' + SALT).encode()) % len(ok)]


def vary(key, cands):
    """como pick, mas para nomes simples (cor, madeira) que nao sao ids de bloco"""
    return cands[zlib.crc32((key + '|' + SALT).encode()) % len(cands)]


# ---------------------------------------------------------------- familias de material
def fam(full, stairs=None, slab=None, wall=None, vslab=None, fence=None, gate=None, plate=None, button=None,
        door=None, trapdoor=None, pane=None, pillar=None):
    return dict(full=full, stairs=stairs, slab=slab, wall=wall, vslab=vslab, fence=fence, gate=gate, plate=plate,
                button=button, door=door, trapdoor=trapdoor, pane=pane, pillar=pillar)

STONE_PLATE, STONE_BUTTON = 'minecraft:stone_pressure_plate', 'minecraft:stone_button'
BS_PLATE, BS_BUTTON = 'minecraft:polished_blackstone_pressure_plate', 'minecraft:polished_blackstone_button'

def create_stone(s, kind='polished_cut'):
    base = f'create:{kind}_{s}' if kind else f'create:{s}'
    vs = f'quark:{s}_vertical_slab' if f'quark:{s}_vertical_slab' in BLOCKS else 'quark:stone_vertical_slab'
    return fam(base, base + '_stairs', base + '_slab', base + '_wall', vs, None, None,
               STONE_PLATE, STONE_BUTTON, pillar=f'create:{s}_pillar')

FAMILIES = {
    'calcite': fam('create:polished_cut_calcite', 'create:polished_cut_calcite_stairs', 'create:polished_cut_calcite_slab',
                   'create:polished_cut_calcite_wall', 'quark:smooth_quartz_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON,
                   pillar='create:calcite_pillar'),
    'calcite_bricks': fam('create:cut_calcite_bricks', 'create:cut_calcite_brick_stairs', 'create:cut_calcite_brick_slab',
                          'create:cut_calcite_brick_wall', 'quark:smooth_quartz_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'quartz': fam('minecraft:smooth_quartz', 'minecraft:smooth_quartz_stairs', 'minecraft:smooth_quartz_slab',
                  'create:polished_cut_diorite_wall', 'quark:smooth_quartz_vertical_slab', None, None,
                  'minecraft:light_weighted_pressure_plate', 'minecraft:birch_button', pillar='minecraft:quartz_pillar'),
    'andesite': create_stone('andesite'),
    'andesite_bricks': fam('create:cut_andesite_bricks', 'create:cut_andesite_brick_stairs', 'create:cut_andesite_brick_slab',
                           'create:cut_andesite_brick_wall', 'quark:polished_andesite_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'small_andesite': fam('create:small_andesite_bricks', 'create:small_andesite_brick_stairs', 'create:small_andesite_brick_slab',
                          'create:small_andesite_brick_wall', 'quark:polished_andesite_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'diorite': create_stone('diorite'),
    'tuff': create_stone('tuff'),
    'deepslate': fam('minecraft:polished_deepslate', 'minecraft:polished_deepslate_stairs', 'minecraft:polished_deepslate_slab',
                     'minecraft:polished_deepslate_wall', 'quark:polished_deepslate_vertical_slab', None, None, BS_PLATE, BS_BUTTON,
                     pillar='create:deepslate_pillar'),
    'deepslate_bricks': fam('minecraft:deepslate_bricks', 'minecraft:deepslate_brick_stairs', 'minecraft:deepslate_brick_slab',
                            'minecraft:deepslate_brick_wall', 'quark:deepslate_brick_vertical_slab', None, None, BS_PLATE, BS_BUTTON),
    'deepslate_tiles': fam('minecraft:deepslate_tiles', 'minecraft:deepslate_tile_stairs', 'minecraft:deepslate_tile_slab',
                           'minecraft:deepslate_tile_wall', 'quark:deepslate_tile_vertical_slab', None, None, BS_PLATE, BS_BUTTON),
    'slate': create_stone('deepslate'),
    'sandstone': fam('minecraft:smooth_sandstone', 'minecraft:smooth_sandstone_stairs', 'minecraft:smooth_sandstone_slab',
                     'minecraft:sandstone_wall', 'quark:cut_sandstone_vertical_slab', None, None, STONE_PLATE, 'minecraft:birch_button'),
    'red_sandstone': fam('minecraft:smooth_red_sandstone', 'minecraft:smooth_red_sandstone_stairs', 'minecraft:smooth_red_sandstone_slab',
                         'minecraft:red_sandstone_wall', 'quark:cut_red_sandstone_vertical_slab', None, None, STONE_PLATE, 'minecraft:acacia_button'),
    'blackstone': fam('minecraft:polished_blackstone', 'minecraft:polished_blackstone_stairs', 'minecraft:polished_blackstone_slab',
                      'minecraft:polished_blackstone_wall', 'quark:polished_blackstone_vertical_slab', None, None, BS_PLATE, BS_BUTTON),
    'stone_bricks': fam('minecraft:stone_bricks', 'minecraft:stone_brick_stairs', 'minecraft:stone_brick_slab',
                        'minecraft:stone_brick_wall', 'quark:stone_brick_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'smooth_stone': fam('minecraft:smooth_stone', 'twigs:smooth_stone_brick_stairs', 'minecraft:smooth_stone_slab',
                        'twigs:smooth_stone_brick_wall', 'quark:smooth_stone_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'concrete': fam('minecraft:light_gray_concrete', 'create:cut_andesite_stairs', 'create:cut_andesite_slab',
                    'create:cut_andesite_wall', 'quark:andesite_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON,
                    pillar='create:andesite_pillar'),
    'dark_concrete': fam('minecraft:gray_concrete', 'create:cut_deepslate_stairs', 'create:cut_deepslate_slab',
                         'create:cut_deepslate_wall', 'quark:polished_deepslate_vertical_slab', None, None, BS_PLATE, BS_BUTTON),
    'white_concrete': fam('minecraft:white_concrete', 'minecraft:smooth_quartz_stairs', 'minecraft:smooth_quartz_slab',
                          'create:polished_cut_diorite_wall', 'quark:smooth_quartz_vertical_slab', None, None,
                          'minecraft:light_weighted_pressure_plate', 'minecraft:birch_button', pillar='minecraft:quartz_pillar'),
    'bricks': fam('minecraft:bricks', 'minecraft:brick_stairs', 'minecraft:brick_slab', 'minecraft:brick_wall',
                  'quark:brick_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'mud_bricks': fam('minecraft:mud_bricks', 'minecraft:mud_brick_stairs', 'minecraft:mud_brick_slab', 'minecraft:mud_brick_wall',
                      'quark:mud_brick_vertical_slab', None, None, STONE_PLATE, 'minecraft:spruce_button'),
    'prismarine': fam('minecraft:prismarine_bricks', 'minecraft:prismarine_brick_stairs', 'minecraft:prismarine_brick_slab',
                      'minecraft:prismarine_wall', 'quark:prismarine_brick_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'veridium': create_stone('veridium', 'cut'),
    'ochrum': create_stone('ochrum'),
    'scorchia': create_stone('scorchia'),
    'limestone': create_stone('limestone'),
    'cobblestone': fam('minecraft:cobblestone', 'minecraft:cobblestone_stairs', 'minecraft:cobblestone_slab', 'minecraft:cobblestone_wall',
                       'quark:cobblestone_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'metal': fam('quark:iron_plate', 'quark:iron_plate_stairs', 'quark:iron_plate_slab', 'minecraft:iron_bars',
                 'quark:iron_plate_vertical_slab', 'minecraft:iron_bars', 'supplementaries:iron_gate',
                 'minecraft:heavy_weighted_pressure_plate', STONE_BUTTON, 'create:andesite_door', 'minecraft:iron_trapdoor',
                 'minecraft:iron_bars'),
    'copper': fam('minecraft:waxed_cut_copper', 'minecraft:waxed_cut_copper_stairs', 'minecraft:waxed_cut_copper_slab',
                  'create:copper_bars', 'quark:cut_copper_vertical_slab', 'create:copper_bars', None,
                  'minecraft:light_weighted_pressure_plate', STONE_BUTTON, 'create:copper_door', 'minecraft:iron_trapdoor',
                  'create:copper_bars'),
    'terracotta': fam('minecraft:terracotta', 'minecraft:mud_brick_stairs', 'minecraft:mud_brick_slab', 'minecraft:mud_brick_wall',
                      'quark:mud_brick_vertical_slab', None, None, STONE_PLATE, STONE_BUTTON),
    'dirt': fam('minecraft:coarse_dirt', None, None, None, 'quark:dirt_bricks_vertical_slab'),
}

def wood_family(w):
    p = f'minecraft:{w}'
    planks = 'minecraft:bamboo_planks' if w == 'bamboo' else p + '_planks'
    return fam(planks, p + '_stairs', p + '_slab', p + '_fence', f'quark:{w}_vertical_slab', p + '_fence', p + '_fence_gate',
               p + '_pressure_plate', p + '_button', p + '_door', p + '_trapdoor', f'create:{w}_window_pane')

# material da origem -> familia (ordem importa: mais especifico primeiro)
MATERIALS = [
    ('marble_large_brick', 'calcite_bricks'), ('marble_brick', 'calcite_bricks'), ('marble', 'calcite'), ('calcite', 'calcite'),
    ('pearl_brick', 'calcite_bricks'), ('white_sandstone', 'quartz'), ('chiseled_white_sandstone', 'quartz'),
    ('black_sandstone', 'blackstone'), ('red_sandstone', 'red_sandstone'), ('sandstone', 'sandstone'),
    ('gneiss_large_brick', 'andesite_bricks'), ('gneiss_brick', 'andesite_bricks'), ('gneiss_paving', 'small_andesite'),
    ('gneiss_tiles', 'small_andesite'), ('gneiss', 'andesite'), ('andesite_paving', 'small_andesite'), ('andesite', 'andesite'),
    ('basalt_large_brick', 'deepslate_bricks'), ('basalt_tiles', 'deepslate_tiles'), ('basalt', 'deepslate'),
    ('slate', 'slate'), ('deepslate', 'deepslate'), ('diorite', 'diorite'), ('tuff', 'tuff'),
    ('dark_concrete', 'dark_concrete'), ('white_concrete', 'white_concrete'), ('hempcrete', 'white_concrete'),
    ('concrete_brick', 'andesite_bricks'), ('concrete_tile', 'small_andesite'), ('concrete', 'concrete'),
    ('paving', 'stone_bricks'), ('stone_brick', 'stone_bricks'), ('cobblestone', 'cobblestone'),
    ('umber', 'mud_bricks'), ('dean_brick', 'bricks'), ('red_brick', 'bricks'), ('blue_brick', 'prismarine'),
    ('verdant', 'veridium'), ('blastbrick', 'bricks'), ('cokebrick', 'bricks'), ('coke', 'blackstone'), ('clinker', 'bricks'),
    ('jasper', 'red_sandstone'), ('ochrum', 'ochrum'), ('scorchia', 'scorchia'), ('limestone', 'limestone'),
    ('corrugated_metal', 'metal'), ('sheetmetal_copper', 'copper'), ('sheetmetal', 'metal'), ('storage_', 'metal'),
    ('steel', 'metal'), ('iron', 'metal'), ('zinc', 'metal'), ('brass', 'copper'), ('copper', 'copper'),
    ('terracotta', 'terracotta'), ('dirt', 'dirt'), ('tiles', 'quartz'), ('wallpaper', 'quartz'), ('alu', 'metal'),
]

SHAPES = [('_vertical_slab', 'vslab'), ('_fence_gate', 'gate'), ('_pressure_plate', 'plate'), ('_trapdoor', 'trapdoor'),
          ('_stairs', 'stairs'), ('_slab', 'slab'), ('_wall', 'wall'), ('_gate', 'gate'), ('_fence', 'fence'),
          ('_button', 'button'), ('_door', 'door'), ('_glass_pane', 'pane'), ('_pane', 'pane'), ('_pillar', 'pillar')]


def shape_of(n):
    # IE usa prefixo: slab_concrete, stairs_hempcrete
    for pre, sh in (('slab_', 'slab'), ('stairs_', 'stairs')):
        if n.startswith(pre):
            return sh, n[len(pre):]
    for suf, sh in SHAPES:
        if n.endswith(suf):
            return sh, n[:-len(suf)]
    return 'full', n


def material_family(core):
    for key, f in MATERIALS:
        if key in core:
            return FAMILIES[f]
    return None


# ---------------------------------------------------------------- regras de mobilia
# (regex no nome sem namespace, lista de candidatos). {w}=madeira, {c}=cor, {sw}=madeira com stripped
FURN = [
    # prioridade: nomes compostos que contem palavras de outras regras
    (r'table_lamp|manual_table_lamp', ['refurbished_furniture:{c:white}_lamp', 'furniture:lamp_{c:white}']),
    (r'kitchen_counter', ['refurbished_furniture:{cw:oak}_kitchen_cabinetry', 'candlelight:stone_bricks_counter',
                          'bakery:brick_counter']),
    (r'kitchen_drawer', ['refurbished_furniture:{cw:oak}_kitchen_drawer']),
    (r'kitchen_sink|basic_sink', ['refurbished_furniture:{cw:white}_kitchen_sink']),
    (r'market_shelves|large_shelves|metal_?shel', ['farmersdelight:{w:spruce}_cabinet', 'candlelight:{w:spruce}_shelf']),
    (r'(iron|zinc|andesite|brass|copper|industrial).*(window_pane|glass_pane)', ['create:industrial_iron_window_pane', 'create:ornate_iron_window_pane']),
    (r'(iron|zinc|andesite|brass|copper|industrial).*_window$', ['create:industrial_iron_window', 'create:ornate_iron_window']),
    (r'(oak|spruce|birch|jungle|acacia|mangrove|cherry|crimson|warped).*(window_pane|glass_pane)', ['create:{w:oak}_window_pane']),
    (r'(oak|spruce|birch|jungle|acacia|mangrove|cherry|crimson|warped).*(_window|_glass)$', ['create:{w:oak}_window']),
    (r'window_pane|glass_pane', ['create:framed_glass_pane']),
    (r'_window$|_glass$|^glass$', ['create:framed_glass']),
    (r'^(grit_sand|white_sand)$', ['minecraft:sand']),
    (r'^industrial$', ['create:industrial_iron_block']),
    # quarto
    (r'fancy_bed', ['minecraft:{c:red}_bed']),
    (r'camah|hospital_bed', ['refurbished_furniture:{c:white}_sofa']),
    (r'sleeping_bag', ['minecraft:{c:red}_bed']),
    (r'pillow|cushion|pet_bed|fluffy_carpet|c_t[a-z]+$', ['minecraft:{c:white}_carpet']),
    (r'ottoman', ['furniture:pouffe_{c:white}']),
    (r'night_?stand|bedside_cabinet', ['refurbished_furniture:{w:oak}_drawer', 'furniture:{w:oak}_dresser']),
    (r'desk_cabinet', ['refurbished_furniture:{w:oak}_drawer', 'furniture:{w:oak}_cabinet']),
    (r'drawers?$', ['refurbished_furniture:{w:oak}_drawer', 'furniture:{w:oak}_dresser', 'candlelight:{w:oak}_drawer']),
    # sala
    (r'sofa|couch|chaise|love_seat', ['refurbished_furniture:{c:light_gray}_sofa']),
    (r'floor_chair|_seat$|kelp_seat', ['create:{c:red}_seat']),
    (r'armchair', ['cluttered:cottage_armchair', 'refurbished_furniture:{c:light_gray}_sofa']),
    (r'silladedirector|terrace_chair|lounge_chair', ['candlelight:{w:oak}_chair', 'refurbished_furniture:{w:oak}_chair']),
    (r'tall_stool|bar_stool', ['kaleidoscope_tavern:{c:brown}_bar_stool', 'refurbished_furniture:{c:light_gray}_stool']),
    (r'log_stool', ['tanukidecor:log_stool']),
    (r'stool', ['refurbished_furniture:{c:light_gray}_stool', 'kaleidoscope_cookery:cook_stool_{w:oak}']),
    (r'wooden_chair|chair', ['refurbished_furniture:{w:oak}_chair', 'candlelight:{w:oak}_chair', 'furniture:{w:oak}_desk_chair']),
    (r'park_bench|garden_bench|_bench$', ['furniture:{w:oak}_bench']),
    (r'coffee_table|terrace_table|wall_mounted_table|trader_table|iron_table', ['twigs:{w:oak}_table', 'refurbished_furniture:{w:oak}_table']),
    (r'fancy_table', ['candlelight:{w:oak}_table', 'refurbished_furniture:{w:oak}_table']),
    (r'^desk|_desk$', ['refurbished_furniture:{w:oak}_desk', 'furniture:{w:oak}_desk']),
    (r'table', ['refurbished_furniture:{w:oak}_table', 'candlelight:{w:oak}_table', 'twigs:{w:oak}_table']),
    (r'tube_tv|_tv$|plasma_tv|television', ['refurbished_furniture:television']),
    (r'computer|monitor', ['refurbished_furniture:computer']),
    (r'radio', ['tanukidecor:antique_radio', 'cluttered:traditional_radio']),
    (r'fonografo|tocadiscos|maquinadediscos|turntable|record', ['furniture:gramophone', 'tanukidecor:phonograph']),
    (r'pianodecola|piano|tecladomusical', ['tanukidecor:piano']),
    (r'curtain', ['furniture:curtain_{c:white}']),
    (r'blinds', ['beautify:{w:oak}_blinds']),
    (r'shutter', ['furniture:{w:oak}_shutter']),
    (r'^p(lamonalisa|monalisa)|caballeteconlamonalisa', ['kaleidoscope_tavern:mona_lisa_painting']),
    (r'nocheestrellada', ['kaleidoscope_tavern:starry_night_painting']),
    (r'jovendelaperla', ['kaleidoscope_tavern:girl_with_pearl_earring_painting']),
    (r'grito|gotico|serenata|lienzo|caballete', ['kaleidoscope_tavern:great_wave_painting', 'kaleidoscope_tavern:mondrian_painting',
                                                'kaleidoscope_tavern:son_of_man_painting', 'kaleidoscope_tavern:van_gogh_self_portrait_painting']),
    (r'escultura|statue', ['supplementaries:statue']),
    (r'clock', ['furniture:{w:oak}_clock']),
    (r'flower_box|planter', ['supplementaries:flower_box', 'furniture:wooden_planter']),
    (r'terrarium', ['furniture:terrarium', 'cluttered:mini_hanging_terrariums']),
    (r'pedestal', ['supplementaries:pedestal']),
    (r'display_case', ['tanukidecor:display_case']),
    (r'shelves|shelf', ['candlelight:{w:oak}_shelf']),
    (r'bookcase|bookshelf', ['minecraft:bookshelf']),
    # cozinha
    (r'kitchen_counter', ['refurbished_furniture:{cw:oak}_kitchen_cabinetry', 'candlelight:stone_bricks_counter',
                          'bakery:brick_counter']),
    (r'kitchen_drawer', ['refurbished_furniture:{cw:oak}_kitchen_drawer']),
    (r'kitchen_sink|basic_sink', ['refurbished_furniture:{cw:white}_kitchen_sink']),
    (r'marketfridge|fridge', ['refurbished_furniture:light_fridge']),
    (r'freezer', ['refurbished_furniture:light_freezer']),
    (r'microwave', ['refurbished_furniture:light_microwave']),
    (r'kitchen_stove|_stove$|oven', ['refurbished_furniture:light_stove', 'farmersdelight:stove', 'candlelight:stone_bricks_stove',
                                     'kaleidoscope_cookery:stove', 'farm_and_charm:stove']),
    (r'cooler', ['refurbished_furniture:{c:white}_cooler']),
    (r'grill', ['refurbished_furniture:{c:black}_grill']),
    (r'^plate$', ['refurbished_furniture:plate']),
    (r'crafting_bowl', ['farmersdelight:cooking_pot', 'farm_and_charm:crafting_bowl', 'kaleidoscope_cookery:chopping_board']),
    (r'cabinet|locker|medical_storage', ['refurbished_furniture:{w:oak}_storage_cabinet', 'furniture:{w:oak}_cabinet',
                                        'farmersdelight:{w:oak}_cabinet', 'candlelight:cabinet']),
    (r'wooden_crate|ironcrate|_crate$', ['refurbished_furniture:{w:oak}_crate', 'redeco:{w:oak}_crate',
                                         'embellishcraft:{w:oak}_wooden_crate']),
    
    (r'canned_(food|soup|pork|rabbit|fish|melon|strawberry|beetroot|carrots)|oat_crate|strawberry_crate', ['culturaldelights:eggplant_crate', 'hearthandharvest:raspberry_crate', 'vintagedelight:cucumber_crate', 'vintagedelight:peanut_crate', 'hearthandharvest:apple_crate',
     'hearthandharvest:blueberry_crate', 'hearthandharvest:raspberry_crate', 'culturaldelights:eggplant_crate',
     'culturaldelights:avocado_crate', 'youkaishomecoming:cucumber_crate', 'farm_and_charm:potato_bag',
     'vinery:apple_bag', 'farmersrespite:green_tea_leaves_sack', 'farmersdelight:rice_bag']),
    (r'milk_boxes|pack_of', ['minecraft:barrel', 'hearthandharvest:milk_crate', 'hearthandharvest:egg_crate',
                             'crabbersdelight:cod_barrel', 'crabbersdelight:salmon_barrel', 'kaleidoscope_tavern:barrel']),
    (r'oat_block', ['minecraft:hay_block']),
    (r'(chocolate|honey)_cake', ['minecraft:cake']),
    # banheiro / lavanderia
    (r'inodoro|mingitorio|toilet', ['refurbished_furniture:white_toilet']),
    (r'banera|bath$|bathtub', ['refurbished_furniture:white_bath']),
    (r'regadera$|shower', ['whimsy_deco:shower']),
    (r'labetosc|ljungla|lroble|lavabo|basin', ['refurbished_furniture:{w:white}_basin', 'refurbished_furniture:white_basin']),
    (r'llavesde', ['supplementaries:faucet']),
    (r'esp_|mirror', ['furniture:{w:oak}_mirror']),
    (r'lavadora|washing_machine', ['whimsy_deco:washing_machine']),
    (r'letreropisomojado', ['whimsy_deco:caution_floor_sign']),
    (r'^trap$|escoba|broom', ['whimsy_deco:broom']),
    (r'tendedero|^bata', ['cluttered:hanging_cloth']),
    # escritorio / escola / ciencia
    (r'libroabierto', ['cluttered:book_open']),
    (r'libro|books?$|librosapilados', ['supplementaries:book_pile', 'cluttered:stack_of_books', 'cluttered:row_of_small_books']),
    (r'documento|portapapeles|pergamino|magazine|clipboard', ['cluttered:paper_pile', 'cluttered:scattered_papers', 'cluttered:newspaper_pile_short']),
    (r'mapadeltesoro', ['cluttered:antique_map']),
    (r'globo|brujula|globe', ['supplementaries:globe']),
    (r'telescop|spyglass_stand', ['furniture:telescope']),
    (r'microscopio|lupa|bascula|calculadora|tintero', ['cluttered:office_supplies_a', 'cluttered:office_supplies_b']),
    (r'pizarra', ['supplementaries:blackboard']),
    (r'biombo', ['tanukidecor:cabana_screen']),
    (r'frasco|tubo|matraz|suero|laboratory|_jar$', ['cluttered:small_glass_jars', 'cluttered:vial_stand', 'supplementaries:jar']),
    (r'maquinadecoser|sewing', ['cluttered:sewing_machine_antique']),
    (r'maniqui', ['cluttered:sewing_mannequin']),
    (r'^hilo', ['cluttered:spool_of_thread_{c:white}']),
    (r'tijeras', ['cluttered:scissors_and_thread']),
    (r'acuarela|pinceles|paleta', ['cluttered:box_of_paints', 'cluttered:paint_water_jar']),
    (r'schematic_table', ['create:schematic_table']),
    (r'toalla.*colg', ['cluttered:hanging_cloth']),
    (r'toalla', ['minecraft:{c:white}_carpet']),
    (r'^hilo', ['cluttered:sewing_clutter']),
    (r'^pintura', ['cluttered:box_of_paints']),
    (r'medicine_boxes', ['cluttered:small_glass_jars']),
    (r'^jar$', ['supplementaries:jar']),
    # loja
    (r'cash_register', ['furniture:cash_register', 'whimsy_deco:cash_register', 'tanukidecor:cash_register']),
    (r'vending_machine', ['tanukidecor:gumball_machine', 'whimsy_deco:gatcha_machine']),
    (r'market_shelves|large_shelves|metal_?shel', ['farmersdelight:{w:spruce}_cabinet', 'candlelight:{w:spruce}_shelf']),
    (r'service_bell', ['create:desk_bell']),
    (r'mail_?box', ['refurbished_furniture:{w:oak}_mail_box']),
    (r'trash|bin$|trashcan', ['refurbished_furniture:recycle_bin', 'furniture:bin']),
    (r'safe$', ['supplementaries:safe']),
    (r'tool_?box|tool_chest', ['create:{c:red}_toolbox', 'furniture:tool_box']),
    (r'cardboard_box', ['cluttered:cardboard_box_open', 'create:cardboard_block']),
    (r'coinstack', ['fantasyfurniture:decorations/coin_stack_gold']),
    (r'traffic_cone', ['whimsy_deco:traffic_cone']),
    
    (r'watering_can|regadera_', ['cluttered:watering_can']),
    (r'tea_set', ['fantasyfurniture:decorations/venthyr_tea_set']),
    (r'basket', ['farmersdelight:wooden_basket', 'kaleidoscope_cookery:fruit_basket', 'youkaishomecoming:short_basket']),
    # iluminacao
    (r'rodlamp', ['minecraft:end_rod']),
    (r'lamp_post', ['simplylight:lamp_post']),
    (r'wall_lamp|motion_activated_light', ['supplementaries:sconce_wall', 'furniture:lamp_wall_white']),
    (r'edge_light|illuminant_panel|illuminant_slab|industrial_flat_7', ['refurbished_furniture:light_ceiling_light']),
    (r'illuminant_(orange|yellow|red|brown)', ['minecraft:glowstone']),
    (r'illuminant', ['minecraft:sea_lantern']),
    (r'light_bulb|lightbulb', ['beautify:lamp_light_bulb']),
    (r'paper_lantern', ['whimsy_deco:red_paper_lantern', 'twigs:paper_lantern']),
    (r'table_lamp|^lamp$|_lamp$', ['refurbished_furniture:{c:white}_lamp', 'furniture:lamp_{c:white}']),
    (r'floodlight|reflector', ['minecraft:sea_lantern']),
    (r'lantern', ['minecraft:lantern']),
    (r'ceiling_fan', ['refurbished_furniture:{w:oak}_light_ceiling_fan']),
    # exterior / jardim
    (r'hedge', ['refurbished_furniture:{w:oak}_hedge']),
    (r'picket_gate', ['cluttered:wooden_picket_fence_gate']),
    (r'picket_fence', ['cluttered:wooden_picket_fence']),
    (r'upgraded_fence', ['minecraft:{w:oak}_fence']),
    (r'upgraded_gate', ['minecraft:{w:oak}_fence_gate']),
    (r'stepping_stones|rock_path', ['refurbished_furniture:stone_stepping_stones']),
    (r'^(rock|granite_rock|gravel_rock|netherrack_rock|end_stone_rock|soul_soil_rock)$', ['twigs:pebble']),
    (r'oak_stick|^stick$', ['twigs:twig']),
    (r'seashell', ['twigs:opaline_seashell']),
    # oficina / industria (vira Create)
    (r'wire_fence|mesh_fence|metal_fence|steel_fence|concrete_fence|bars$|bars_overlay|radiator', ['minecraft:iron_bars']),
    (r'catwalk_stairs', ['quark:iron_plate_stairs']),
    (r'catwalk|vent|air_duct|ventcover|industrial_flat|grate', ['minecraft:iron_trapdoor']),
    (r'_support$|steel_slope|alu_slope', ['create:metal_girder']),
    (r'scaffolding', ['create:andesite_scaffolding']),
    (r'_hull$|facade|industrial_\d|heavy_engineering|light_engineering|rs_engineering|logic_unit|capacitor|coil_|generator|alternator|electric_motor|accumulator|rolling_mill|diesel_engine|metal_press|charging_station|breaker',
     ['create:andesite_casing', 'create:brass_casing', 'create:copper_casing']),
    (r'^tank$|gas_station', ['create:fluid_tank']),
    (r'conveyor', ['create:depot']),
    (r'barrel', ['minecraft:barrel']),
    (r'craftingtable', ['minecraft:crafting_table']),
    (r'chain_\d|^chain$', ['minecraft:chain']),
    (r'ladder|rungs', ['minecraft:ladder']),
    (r'frame_\d', ['decorative_blocks:{w:oak}_beam']),
    (r'warning_stripes', ['minecraft:yellow_terracotta']),
    (r'pallet_slab|pallet', ['minecraft:spruce_slab']),
    (r'rain_collector', ['minecraft:cauldron']),
    (r'slag_glass', ['minecraft:gray_stained_glass']),
    (r'^coke$', ['minecraft:coal_block']),
(r'orange_sand', ['minecraft:red_sand']),
    (r'dried_salt', ['minecraft:white_concrete']),
    (r'^ice$', ['minecraft:packed_ice']),
    # plantas (folhas sempre persistentes)
    (r'flowering_oak_leaves', ['minecraft:flowering_azalea_leaves']),
    (r'(jacaranda|snowblossom)_leaves', ['minecraft:cherry_leaves']),
    (r'fir_leaves', ['minecraft:spruce_leaves']),
    (r'_leaves$', ['minecraft:oak_leaves']),
    (r'dead_sapling', ['minecraft:dead_bush']),
    (r'potted_', ['minecraft:potted_oak_sapling']),
    (r'_sapling$', ['minecraft:oak_sapling']),
    (r'dead_grass|barley', ['minecraft:grass']),
    (r'waterlily|lily_pad', ['minecraft:lily_pad']),
]

# tudo que lembra apocalipse, violencia ou lixo vira ar
APOC = re.compile(r'blood|body|corpse|remains|severed|trapped_leg|impaled|chained_entity|bear_trap|land_mine|razor|barbed|'
                  r'spike|sandbag|barricade|cobweb|flesh|pus_bubble|tendon|^hair$|gravestone|^cross$|coffin|decal_|gas_canister|'
                  r'barril|veneno|jeringa|ammo|cannon|mortar|herobrine|steve_head|security_camera|alarm|keycard|key_panel|'
                  r'panic_button|portable_radar|projector|^bus$|empty_cans|decomposing|birdsnest|trashbag|trash_bag|'
                  r'pile_of_tires|concrete_barrier|^wire$|chalk|acid|geyser|creosote|gasoline|biodiesel|plantoil|fluid_block|'
                  r'^disabled$|money|sword_mount|lectordesignos|papelhigienico|rollos|jabon|esponja|cubetadeagua|destapador|'
                  r'secadormanos|planch|vasocepillos|barradebano|l_bdiscapacitados|camaradecine|claqueta|rollodepelicula|'
                  r'premio|gafas|aerosol|martillo|guitarra|violin|bateria|tambor|amplificador|microfono|mezcladordj|'
                  r'garden_(bag|hoe|pitchfork|rake|shovel|spade|tools|bucket)|flamingo|starfish|diving_board|'
                  r'connector_|lightning_rod|fluid_placer|redstone_breaker|coinstack_x|statue_x|^post$|parking$|'
                  r'thermoelectric|tacz|plushie_|teddy_bear|catwalk_railing|support_wedge|^documentos?$|^bata|tendedero|toalla.*colg|hanging_cobweb|military|^esco$|banyo|jade_button')

# pinturas de estrada do refueled viram carpete branco (faixas), o resto do namespace vira ar
REFUELED_PAINT = re.compile(r'stripes|side|corner|middle|edge|end|center|zebra|parking|waffle|start')


def fill(t, color, wood):
    def rep(m):
        kind, default = m.group(1), m.group(2)
        if kind == 'c':
            return color or default
        if kind == 'w':
            return wood or default
        if kind == 'cw':
            return color or wood or default
        return default
    return re.sub(r'\{(cw|c|w):([a-z_]+)\}', rep, t)


def map_missing(bid, props):
    """devolve (novo_id, props_sugeridas) ou None para ar"""
    ns, name = bid.split(':', 1)
    leaf = name.split('/')[-1]
    color, wood = tokens(bid)

    if ns in ('horror_element_mod', 'spore', 'undead_revamp2', 'createbigcannons', 'securitycraft', 'tacz', 'chalk'):
        if 'traffic_cone' in leaf: return 'whimsy_deco:traffic_cone', {}
        if 'reinforced_door' in leaf: return 'create:andesite_door', props
        if 'motion_activated_light' in leaf: return 'minecraft:lantern', {}
        return None
    if ns == 'displaydelight':
        if re.search(r'juice|cider|cocoa|broth', leaf):
            return pick(bid, ['kaleidoscope_tavern:empty_bottle', 'kaleidoscope_tavern:water_bottle', 'displaydelight:bowl']), props
        return pick(bid, ['displaydelight:plated_hamburger', 'displaydelight:plated_dumplings', 'displaydelight:plated_cabbage_rolls',
                          'displaydelight:plated_stuffed_potato', 'displaydelight:plated_chicken_sandwich',
                          'displaydelight:plated_barbecue_stick', 'displaydelight:plated_mutton_wrap']), props
    if ns == 'refinedstorage':
        return pick(bid, ['create:andesite_casing', 'create:brass_casing']), {}
    if leaf == 'small_cooking_pot':
        return 'farmersdelight:cooking_pot', {}
    if ns == 'refueled':
        return ('minecraft:white_carpet', {}) if REFUELED_PAINT.search(leaf) else (('create:fluid_tank', {}) if leaf == 'gas_station' else None)
    if APOC.search(leaf):
        return None

    # luminarias: o suporte (chao/parede/teto) vem da orientacao de origem. Abajur de mesa
    # so se facing=up (ou sem facing); parede/teto viram arandela/luz de teto, nunca abajur
    # (abajur no lugar de luz de parede/teto flutuava no ar, ex. em cima do vaso sanitario).
    if 'lamp' in leaf and 'lamp_post' not in leaf and 'rodlamp' not in leaf:
        facing = props.get('facing', '')
        face = props.get('face', '')
        if face == 'ceiling' or facing == 'down':
            got = pick(bid, ['refurbished_furniture:light_ceiling_light', 'refurbished_furniture:dark_ceiling_light'])
            if got:
                return got, props
        if face == 'wall' or facing in ('north', 'south', 'east', 'west'):
            got = pick(bid, ['supplementaries:sconce_wall', 'furniture:lamp_wall_white'])
            if got:
                return got, props
        if facing in ('up', '') or props.get('base') == 'true':
            got = pick(bid, [fill(c, color, 'oak') for c in
                             ('refurbished_furniture:{c:white}_lamp', 'furniture:lamp_{c:white}')])
            if got:
                return got, props
        return 'minecraft:sea_lantern', {}
    # paineis/fitas do simplylight (so cai aqui se o mod sair do pack): facing aponta para
    # longe do apoio. Sem isso a luz de teto do refurbished ficava no estado padrao
    # face=floor e flutuava a 1 bloco do teto.
    if ns == 'simplylight' and re.search(r'edge_light|illuminant_panel|illuminant_slab', leaf):
        f = props.get('facing', 'down')
        if f == 'up':
            face = {'face': 'floor', 'facing': 'north'}
        elif f in OPPOSITE:
            face = {'face': 'wall', 'facing': f}
        else:
            face = {'face': 'ceiling', 'facing': 'north'}
        return 'refurbished_furniture:light_ceiling_light', face
    if leaf in ('wall_lamp', 'motion_activated_light'):
        if props.get('facing') in ('down', 'up'):
            return pick(bid, ['refurbished_furniture:light_ceiling_light',
                              'refurbished_furniture:dark_ceiling_light']), props
        got = pick(bid, ['supplementaries:sconce_wall', 'furniture:lamp_wall_white'])
        if got:
            return got, props
        return 'minecraft:sea_lantern', {}

    # v_slab_compat:<ns>/<bloco>_vertical_slab
    if ns == 'v_slab_compat':
        core = leaf[:-len('_vertical_slab')] if leaf.endswith('_vertical_slab') else leaf
        f = material_family(core)
        if wood and not f:
            f = wood_family(wood)
        target = (f or FAMILIES['stone_bricks'])['vslab']
        if not exists(target):
            target = 'quark:stone_brick_vertical_slab'
        return target, props

    # portas
    if leaf.endswith('_door'):
        if re.search(r'steel|reinforced|zinc|industrial|andesite', leaf):
            return ('minecraft:birch_door' if 'white' in leaf else 'create:andesite_door'), props
        if 'brass' in leaf: return 'create:brass_door', props
        if 'glass' in leaf: return 'create:framed_glass_door', props
        return f'minecraft:{wood or "oak"}_door', props
    if leaf.endswith('_trapdoor'):
        if wood: return f'minecraft:{wood}_trapdoor', props
        return 'minecraft:iron_trapdoor', props

    fleaf = re.sub(r'_\d+$', '', leaf)
    for rx, cands in FURN:
        if re.search(rx, fleaf):
            # madeira/cor da origem primeiro; se nao existir, cai para oak/white
            got = pick(bid, [fill(c, color, wood) for c in cands]) or pick(bid, [fill(c, 'white', 'oak') for c in cands])
            if got:
                p = dict(props)
                if got.endswith('_leaves'):
                    p = {'persistent': 'true'}
                return got, p

    shape, core = shape_of(re.sub(r'_\d+$', '', leaf))
    core = re.sub(r'_\d+$', '', core)
    # madeiras: planks_N, stairs, slabs, logs
    f = material_family(core)
    if wood and (not f or re.search(r'planks|wood|log|polished_(oak|spruce|birch|dark_oak|jungle)', core)):
        if core.endswith('_log') or core.endswith('log'):
            stripped = 'stripped_' if 'stripped' in core else ''
            return pick(bid, [f'minecraft:{stripped}{wood}_log', f'minecraft:{stripped}{wood}_stem',
                              f'minecraft:{stripped}{wood}_block']) or 'minecraft:oak_log', props
        f = wood_family(wood)
    if f:
        target = f.get(shape) or f['full']
        if shape == 'pillar' and not f.get('pillar'):
            target = f['full']
        if exists(target):
            return target, props
        if exists(f['full']):
            return f['full'], {}
    return 'FALLBACK', {}


OPPOSITE = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}

# cadeiras/sofas do refurbished apontam para a PAREDE (costas); o resto aponta
# para a FRENTE (cadeira olha para a mesa). A origem DC seguia a convencao de
# FRENTE, entao ao converter assento para refurbished gira 180 graus, senao a
# cadeira nasce de costas para a mesa (o "aleatorio" que se via nos parques:
# parte virava refurbished, parte candlelight, cada uma para um lado).
BACK_SEAT = re.compile(r'chair|sofa|couch|armchair|_seat$|stool|_bench$|desk_chair')
FRONT_SEAT_SRC = re.compile(r'chair|sofa|couch|armchair|seat|stool|bench|lounge|director|terrace')


def convert_state(state, stats=None):
    """estado DC -> estado valido aqui, ou None (ar)"""
    bid, props = parse(state)
    # cebola so se compra na loja (regra do modpack): nada de cebola plantada, em saco ou caixote
    if 'onion' in bid:
        if re.search(r'bag|sack', bid):
            return 'farm_and_charm:potato_bag[facing=north]'
        if 'crate' in bid:
            return 'culturaldelights:eggplant_crate'
        if re.search(r'onions$|onion_crop|wild_onion', bid):
            return 'farmersdelight:cabbages[age=7]'
        return None
    if bid in BANNED_EXISTING:
        t = BANNED_EXISTING[bid]
        return t
    # vinery:*_lattice: o blockstate so tem "" e a forma real vem do block entity; colocada pelo
    # Lost Cities ela nasce torta. Vira cerca da mesma madeira
    m = re.match(r'^vinery:(\w+)_lattice$', bid)
    if m:
        w = m.group(1) if exists(f'minecraft:{m.group(1)}_fence') else 'dark_oak'
        return f'minecraft:{w}_fence'
    if exists(bid):
        new, p = bid, props
    else:
        r = map_missing(bid, props)
        if r is None:
            if stats is not None: stats['air'][bid] = stats['air'].get(bid, 0) + 1
            return None
        new, p = r
        if new == 'FALLBACK':
            if stats is not None: stats['fallback'][bid] = stats['fallback'].get(bid, 0) + 1
            return None
        if stats is not None: stats['mapped'][bid] = new
        # assento DC (frente p/ mesa) -> refurbished (costas p/ parede): gira 180
        if (new.startswith('refurbished_furniture:') and BACK_SEAT.search(new)
                and FRONT_SEAT_SRC.search(bid) and p.get('facing') in OPPOSITE):
            p = dict(p, facing=OPPOSITE[p['facing']])
        # escadas "suspensas" do Embellishcraft e de passarela do CreateDeco sobem para o lado
        # oposto ao facing (medido nas partes DC); a escada vanilla sobe para o facing
        if re.search(r'suspended_stairs|catwalk_stairs', bid) and p.get('facing') in OPPOSITE:
            p = dict(p, facing=OPPOSITE[p['facing']])
    # slab vertical do quark usa type=north/south/east/west; do DC vinha facing as vezes
    if new.endswith('_vertical_slab') and 'type' not in p and 'facing' in p:
        p = dict(p, type=p['facing'])
    p = clean_props(new, p)
    return fmt(new, p)


# ---------------------------------------------------------------- variacao de material por predio (2026-10-06)
# Casas iguais demais (tudo branco/vermelho): cada familia de material sorteia UMA variante por
# predio (SALT do convert) e todas as ocorrencias da familia naquele predio usam ela. Madeira
# troca o tipo, tijolo troca entre bricks e stone_bricks, concreto e terracota trocam a cor;
# o resto (pedra lisa, vidro, detalhes) fica intacto. Chamado pelo convert.py (so predios DC).
HOUSE_WOODS = ['oak', 'spruce', 'birch', 'jungle', 'acacia', 'dark_oak', 'mangrove', 'cherry']
HOUSE_BRICKS = ['bricks', 'stone_bricks']
HOUSE_COLORS = ['white', 'light_gray', 'gray', 'black', 'brown', 'red', 'orange', 'yellow', 'lime',
                'green', 'cyan', 'light_blue', 'blue', 'purple', 'magenta', 'pink']
HOUSE_CONCRETE_GRAYS = ['white', 'light_gray', 'gray']
WOOD_FORMS = {'log', 'wood', 'stripped_log', 'stripped_wood', 'planks', 'stairs', 'slab', 'fence',
              'fence_gate', 'door', 'trapdoor', 'button', 'pressure_plate', 'sign', 'hanging_sign'}


def swap_material(state):
    """troca a variante dentro da familia (madeira/tijolo/concreto/terracota), consistente por predio"""
    if not state:
        return state
    b, props = parse(state)
    n = b.split(':')[1] if ':' in b else b
    # concrete powder never generates: it collapses like sand, use the set block instead
    m = re.match(r'^([a-z_]+)_concrete_powder$', n)
    if m and m.group(1) in HOUSE_COLORS:
        return f'minecraft:{m.group(1)}_concrete'
    if b in ('minecraft:terracotta',):
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    # quartz / calcite walls become set concrete with color variation (never powder).
    # Concrete has no stairs/slab/wall/pillar in vanilla, so only full blocks swap;
    # shaped pieces keep the original block to preserve the facade.
    if b in ('minecraft:smooth_quartz', 'minecraft:quartz_block', 'minecraft:quartz_bricks',
             'minecraft:calcite', 'create:polished_cut_calcite', 'create:calcite_pillar'):
        quartz = 'quartz' in n
        cands = HOUSE_CONCRETE_GRAYS if quartz else HOUSE_COLORS
        return f'minecraft:{vary("mat:concrete", cands)}_concrete'
    # calcite brick family alternates with stone bricks like regular bricks do
    if b in ('create:cut_calcite_bricks', 'create:cut_calcite_brick_stairs', 'create:cut_calcite_brick_slab',
             'create:cut_calcite_brick_wall'):
        base = vary('mat:brick', HOUSE_BRICKS)
        root = 'stone_brick' if base == 'stone_bricks' else 'brick'
        suf = '_stairs' if n.endswith('_stairs') else ('_slab' if n.endswith('_slab') else ('_wall' if n.endswith('_wall') else 's'))
        return fmt(f'minecraft:{root}{suf}', props)
    if b == 'embellishcraft:terracotta_wall':
        # no concrete walls in vanilla: closest solid relative
        return fmt('minecraft:brick_wall', props)
    if not b.startswith('minecraft:'):
        return state
    n = b.split(':')[1]
    m = re.match(r'^(stripped_)?(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry)_(.+)$', n)
    if m and m.group(3) in WOOD_FORMS:
        w = vary('mat:wood', HOUSE_WOODS)
        return fmt(f'minecraft:{m.group(1) or ""}{w}_{m.group(3)}', props)
    m = re.match(r'^(stone_)?brick(s|_stairs|_slab|_wall)$', n)
    if m:
        base = vary('mat:brick', HOUSE_BRICKS)
        root = 'stone_brick' if base == 'stone_bricks' else 'brick'
        return fmt(f'minecraft:{root}{m.group(2)}', props)
    m = re.match(r'^([a-z_]+)_(concrete|terracotta)$', n)
    if m and m.group(1) in HOUSE_COLORS:
        # NO terracotta in the towns (2026-10-09, owner): every terracotta (plain,
        # colored, glazed) becomes SET concrete with a rolled color (never powder)
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    m = re.match(r'^(?:([a-z_]+)_)?glazed_terracotta$', n)
    if m:
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    if b == 'embellishcraft:terracotta_wall':
        # no concrete walls in vanilla: closest solid relative
        return fmt('minecraft:brick_wall', props)
    return state


def recolor(state):
    """segunda passada de cor (colorways): troca a cor dentro da familia casca
    (madeira/tijolo/concreto) sob o SALT atual. Idempotente quando o SALT e o mesmo
    do swap (c0). Moveis de mod (outros namespaces) nunca sao tocados."""
    if not state:
        return state
    if state == 'minecraft:terracotta':
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    b, props = parse(state)
    n = b.split(':')[1] if ':' in b else b
    m = re.match(r'^([a-z_]+)_concrete_powder$', n)
    if m and m.group(1) in HOUSE_COLORS:
        return f'minecraft:{m.group(1)}_concrete'
    if b in ('minecraft:smooth_quartz', 'minecraft:quartz_block', 'minecraft:quartz_bricks',
             'minecraft:calcite', 'create:polished_cut_calcite', 'create:calcite_pillar'):
        cands = HOUSE_CONCRETE_GRAYS if 'quartz' in n else HOUSE_COLORS
        return f'minecraft:{vary("mat:concrete", cands)}_concrete'
    if b in ('create:cut_calcite_bricks', 'create:cut_calcite_brick_stairs', 'create:cut_calcite_brick_slab',
             'create:cut_calcite_brick_wall'):
        base = vary('mat:brick', HOUSE_BRICKS)
        root = 'stone_brick' if base == 'stone_bricks' else 'brick'
        suf = '_stairs' if n.endswith('_stairs') else ('_slab' if n.endswith('_slab') else ('_wall' if n.endswith('_wall') else 's'))
        return fmt(f'minecraft:{root}{suf}', props)
    if b == 'embellishcraft:terracotta_wall':
        return fmt('minecraft:brick_wall', props)
    if not b.startswith('minecraft:'):
        return state
    n = b.split(':')[1]
    m = re.match(r'^(stripped_)?(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry)_(.+)$', n)
    if m and m.group(3) in WOOD_FORMS:
        return fmt(f'minecraft:{m.group(1) or ""}{vary("mat:wood", HOUSE_WOODS)}_{m.group(3)}', props)
    m = re.match(r'^(stone_)?brick(s|_stairs|_slab|_wall)$', n)
    if m:
        base = vary('mat:brick', HOUSE_BRICKS)
        root = 'stone_brick' if base == 'stone_bricks' else 'brick'
        return fmt(f'minecraft:{root}{m.group(2)}', props)
    m = re.match(r'^([a-z_]+)_concrete$', n)
    if m and m.group(1) in HOUSE_COLORS:
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    m = re.match(r'^(?:([a-z_]+)_)?(terracotta|glazed_terracotta)$', n)
    if m:
        return f'minecraft:{vary("mat:concrete", HOUSE_COLORS)}_concrete'
    if b == 'embellishcraft:terracotta_wall':
        return fmt('minecraft:brick_wall', props)
    return state


def item_ok(iid):
    return iid in ITEMS
