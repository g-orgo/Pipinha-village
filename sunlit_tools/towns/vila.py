"""Casas variadas da vila (mescla de mods em todos os comodos).

Gera VARIANTS predios 16x16 combinando material de fachada, telhado (plano ou
duas aguas), numero de andares e um tema para o terreo e outro para o andar:
cozinha mista, casa de cha, taverninha, queijaria, casa do pescador,
alfaiataria e herbanario; quartos com moveis do Refurbished, Another Furniture,
Kaleidoscope e Candlelight misturados. Fogao, panela, tabua, cesto e caixote
saem sorteados entre mods em cada bloco (mix.py, via houses.mixed_entry).

Os nomes ficam em NAMES: o convert.py os coloca em todos os bairros.
Uso: python3 vila.py  (depois de convert.py/houses.py/cozy_expansion.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import houses as H

LOOT = {**H.LOOT, 'cellar': 'sunlit:cellar', 'dock': 'sunlit:dock', 'deposito': 'sunlit:deposito'}

# (chave, parede, piso, janela, escada do telhado, laje do telhado)
MATERIALS = {
    'carvalho': ('minecraft:oak_planks', 'minecraft:spruce_planks', 'create:oak_window', 'minecraft:spruce_stairs', 'minecraft:spruce_slab'),
    'pinho': ('minecraft:spruce_planks', 'redeco:polished_oak_planks', 'create:spruce_window', 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab'),
    'betula': ('minecraft:birch_planks', 'minecraft:dark_oak_planks', 'create:birch_window', 'minecraft:brick_stairs', 'minecraft:brick_slab'),
    'tijolo': ('minecraft:bricks', 'minecraft:spruce_planks', 'create:framed_glass', 'minecraft:deepslate_tile_stairs', 'minecraft:deepslate_tile_slab'),
    'barro': ('minecraft:mud_bricks', 'minecraft:oak_planks', 'create:oak_window', 'minecraft:spruce_stairs', 'minecraft:spruce_slab'),
    'pedra': ('minecraft:stone_bricks', 'minecraft:dark_oak_planks', 'create:framed_glass', 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab'),
    'cerejeira': ('minecraft:cherry_planks', 'minecraft:birch_planks', 'create:cherry_window', 'minecraft:mud_brick_stairs', 'minecraft:mud_brick_slab'),
    'escuro': ('minecraft:dark_oak_planks', 'minecraft:oak_planks', 'create:dark_oak_window', 'minecraft:deepslate_tile_stairs', 'minecraft:deepslate_tile_slab'),
    'caiada': ('minecraft:white_terracotta', 'minecraft:spruce_planks', 'create:spruce_window', 'minecraft:brick_stairs', 'minecraft:brick_slab'),
    'musgo': ('minecraft:mossy_cobblestone', 'minecraft:spruce_planks', 'create:spruce_window', 'minecraft:spruce_stairs', 'minecraft:spruce_slab'),
    'andesito': ('create:cut_andesite_bricks', 'minecraft:smooth_stone', 'create:industrial_iron_window', 'minecraft:deepslate_tile_stairs', 'minecraft:deepslate_tile_slab'),
    'ardosia': ('minecraft:polished_deepslate', 'minecraft:spruce_planks', 'create:framed_glass', 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab'),
}
WOOD = {'carvalho': 'oak', 'pinho': 'spruce', 'betula': 'birch', 'tijolo': 'spruce', 'barro': 'oak', 'pedra': 'dark_oak',
        'cerejeira': 'cherry', 'escuro': 'dark_oak', 'caiada': 'spruce', 'musgo': 'spruce', 'andesito': 'spruce', 'ardosia': 'dark_oak'}

# (nome, material, tema terreo, tema andar ou None = chale terreo, telhado)
VARIANTS = [
    ('cozinhamista', 'carvalho', 'cozinha', 'quartos_rf', 'duas_aguas'),
    ('casadecha', 'cerejeira', 'cha', 'quartos_af', 'duas_aguas'),
    ('taverninha', 'escuro', 'taverna', 'quartos_rf', 'plano'),
    ('queijaria', 'caiada', 'queijo', 'quartos_af', 'duas_aguas'),
    ('pescador', 'pinho', 'pescador', None, 'duas_aguas'),
    ('alfaiate', 'tijolo', 'alfaiate', 'quartos_crianca', 'plano'),
    ('herbanario', 'musgo', 'herbanario', None, 'duas_aguas'),
    ('chalecozinha', 'barro', 'cozinha', None, 'duas_aguas'),
    ('sobradocha', 'pedra', 'cha', 'quartos_crianca', 'plano'),
    ('sobradopescador', 'betula', 'pescador', 'quartos_rf', 'duas_aguas'),
    ('chaletaverna', 'cerejeira', 'taverna', None, 'duas_aguas'),
    ('sobradoqueijo', 'escuro', 'queijo', 'quartos_crianca', 'duas_aguas'),
    ('casaalfaiate', 'carvalho', 'alfaiate', 'quartos_af', 'duas_aguas'),
    ('sobradoerva', 'tijolo', 'herbanario', 'quartos_af', 'plano'),
]
# 2026-10-03: as casas da vila agora vem de schematics (schematics.py); VARIANTS/build ficam so como
# referencia de temas de comodo e nao sao mais gravadas
NAMES = []
# depositos: galpao de estantes e caixotes com loot bom (sunlit:deposito)
DEPOSITOS = [('deposito_pedra', 'pedra'), ('deposito_andesito', 'andesito'), ('deposito_ardosia', 'ardosia'), ('deposito_tijolo', 'tijolo')]
NAMES_DEPOSITO = [f'sunlit:building_{n}/building_{n}' for n, _ in DEPOSITOS]


# ---------------------------------------------------------------- casca
def roof_gable(stairs, slab):
    """telhado de duas aguas completo (9 fatias): escadas subindo de N e S ate se encontrarem
    na cumeeira (z7/z8), empenas de parede nas pontas leste/oeste e laje no topo. Com so 6
    fatias a cumeeira virava uma laje larga e o telhado parecia cortado."""
    sl = [H.grid() for _ in range(9)]
    for k in range(8):
        for x in range(16):
            sl[k][k][x] = 'n'
            sl[k][15 - k][x] = 's'
        for z in range(k + 1, 15 - k):
            sl[k][z][0] = H.WALL
            sl[k][z][15] = H.WALL
    for z in (7, 8):
        for x in range(16):
            sl[8][z][x] = 'r'
    for k in range(3, 7):
        sl[k][12][12] = 'K'
    return sl


def palettes_for(P, mat):
    wall, floor, win, stairs, slab = MATERIALS[mat]
    for p in (P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'):
        H.base_palette(p, wall, floor, win)
        H.PALETTES[p]['K'] = H.B('minecraft:bricks')
        H.PALETTES[p]['n'] = H.B(f'{stairs}[facing=south,half=bottom,shape=straight]')
        H.PALETTES[p]['s'] = H.B(f'{stairs}[facing=north,half=bottom,shape=straight]')
        H.PALETTES[p]['r'] = H.B(f'{slab}[type=bottom]')


# ---------------------------------------------------------------- pecas de mobilia
def mixed_dining(fx, x0, z, n, table, chairs, loot):
    """mesa de n lugares; todas as cadeiras da mesa sao do mesmo modelo (cada mesa da casa
    sorteia um modelo diferente de chairs pelo nome da mesa)."""
    chair = chairs[sum(map(ord, table + str(x0) + str(z))) % len(chairs)]
    for i in range(n):
        x = x0 + i
        if table.endswith('_table') and table.split(':')[0] in ('refurbished_furniture', 'redeco', 'cfm'):
            t = f'{table}[east={str(i < n - 1).lower()},north=false,south=false,west={str(i > 0).lower()}]'
        else:
            t = table
        fx.at(x, z, t, loot=loot if i == 0 else None)
        fx.chair(x, z - 1, chair, 'south')
        fx.chair(x, z + 1, chair, 'north')
    fx.chair(x0 - 1, z, chair, 'east')
    fx.chair(x0 + n, z, chair, 'west')


def chairs_for(wood):
    return [f'kaleidoscope_cookery:chair_{wood}[facing={{f}},has_carpet=false,waterlogged=false]',
            f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=2]',
            f'refurbished_furniture:{wood}_chair[facing={{f}},tucked=false]',
            f'candlelight:{wood}_chair[facing={{f}}]']


def small_kitchen(fx, wood):
    """bancada noroeste x1..6: geladeira + fogoes/bancadas de mods diferentes (o fogao e sorteado
    por bloco) e panela/tabua por cima."""
    K = LOOT['kitchen']
    H.fridge(fx, 1, 1, 'north', LOOT['fridge'])
    line = [(2, 'farmersdelight:stove[facing={f},lit=false]'),
            (3, f'refurbished_furniture:{wood}_kitchen_cabinetry[facing={{f}},shape=default]'),
            (4, f'refurbished_furniture:{wood}_kitchen_sink[facing={{f}}]'),
            (5, 'candlelight:stone_bricks_counter[facing={f},type=none]'),
            (6, 'kaleidoscope_cookery:stove[facing={f},lit=false]')]
    for x, b in line:
        fx.at(x, 1, b, loot=K if 'cabinetry' in b or 'counter' in b else None, wall='north')
    fx.at(2, 1, 'farmersdelight:cooking_pot[facing=south,support=none]', y=2)
    fx.at(3, 1, 'kaleidoscope_cookery:chopping_board[facing=south,waterlogged=false]', y=2)
    fx.at(5, 1, 'farmersdelight:wooden_basket[facing=up]', y=2)
    fx.at(6, 1, 'kaleidoscope_cookery:stockpot[facing=south,has_base=false,has_chains=false,has_lid=true,waterlogged=false]', y=2)
    fx.at(1, 2, f'farmersdelight:{wood}_cabinet[facing={{f}},open=false]', loot=K, wall='west')
    fx.at(1, 3, 'bakery:brick_counter[facing={f},type=none]', loot=K, wall='west')
    fx.at(1, 3, 'farm_and_charm:potato_bag[facing=east]', y=2)
    fx.at(4, 1, 'kaleidoscope_cookery:kitchenware_racks[facing={f},waterlogged=false]', y=3, wall='north')
    fx.lantern(4, 3)


def storage_south(fx, wood, theme_loot):
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=theme_loot)
    fx.at(2, 14, f'refurbished_furniture:{wood}_crate[open=false]', loot=theme_loot)
    fx.at(3, 14, f'farmersdelight:{wood}_cabinet[facing={{f}},open=false]', loot=theme_loot, wall='south')
    fx.at(5, 14, 'minecraft:potted_azalea_bush')


def living_east(fx, wood, sofa):
    """sala no leste: sofa na parede leste, mesinha, poltronas e estante no norte."""
    Hm = LOOT['home']
    for i, z in enumerate((6, 7)):
        if sofa == 'rf':
            fx.at(14, z, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=Hm if i == 0 else None, wall='east')
        elif sofa == 'af':
            fx.at(14, z, 'another_furniture:white_sofa[facing={f},type=single]', wall='east')
        else:
            fx.at(14, z, 'kaleidoscope_tavern:green_sofa[facing={f},connection=single,waterlogged=false]', wall='east')
    fx.at(12, 6, f'cfm:{wood if wood != "cherry" else "oak"}_coffee_table[east=false,north=false,south=true,tall=false,west=false]')
    fx.at(12, 7, f'cfm:{wood if wood != "cherry" else "oak"}_coffee_table[east=false,north=true,south=false,tall=false,west=false]')
    fx.chair(10, 6, f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=5]', 'east')
    fx.chair(10, 7, f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=5]', 'east')
    fx.carpet(11, 5, 13, 8, 'brown' if sofa == 'rf' else 'green')
    fx.run([(10, 1), (11, 1)], 'minecraft:bookshelf', 'north')
    fx.at(12, 1, f'another_furniture:{wood}_drawer[facing={{f}},open=false]', loot=Hm, wall='north')
    fx.at(12, 1, 'candlelight:lamp[hanging=false]', y=2)
    fx.at(13, 1, f'refurbished_furniture:{wood}_drawer[facing={{f}},left=false,right=false,open=false]', loot=Hm, wall='north')
    fx.at(13, 1, 'cluttered:stack_of_books[facing=south,waterlogged=false]', y=2)
    fx.at(14, 1, 'minecraft:potted_fern')
    fx.lantern(12, 6)


# ---------------------------------------------------------------- temas do terreo
def g_cozinha(fx, wood):
    small_kitchen(fx, wood)
    mixed_dining(fx, 3, 8, 3, f'refurbished_furniture:{wood}_table', chairs_for(wood), LOOT['home'])
    fx.lantern(4, 8)
    living_east(fx, wood, 'rf')
    storage_south(fx, wood, LOOT['farm'])
    fx.at(11, 14, 'culturaldelights:eggplant_crate', loot=None)
    fx.at(12, 14, 'hearthandharvest:apple_crate')
    fx.at(14, 14, 'farm_and_charm:potato_bag[facing=north]')


def g_cha(fx, wood):
    """casa de cha: chaleiras do Farmer's Respite no balcao, mesinhas Candlelight e sacas de cha."""
    small_kitchen(fx, wood)
    for x, z in ((3, 8), (3, 11)):
        fx.at(x, z, f'candlelight:{wood}_table[facing=north,type=none]')
        fx.at(x, z, 'farmersrespite:kettle[facing=south,support=none,lid=true]', y=2)
        fx.chair(x - 1, z, f'candlelight:{wood}_chair[facing={{f}}]', 'east')
        fx.chair(x + 1, z, f'candlelight:{wood}_chair[facing={{f}}]', 'west')
    fx.lantern(3, 9)
    living_east(fx, wood, 'af')
    storage_south(fx, wood, LOOT['cafe'])
    fx.at(11, 14, 'farmersrespite:green_tea_leaves_sack')
    fx.at(12, 14, 'farmersrespite:black_tea_leaves_sack')
    fx.at(14, 14, 'supplementaries:flower_box[facing=north,face=floor]')
    fx.at(14, 10, 'supplementaries:flower_box[facing=west,face=floor]')


def g_taverna(fx, wood):
    """taverninha: balcao do Kaleidoscope Tavern, banquetas, barris e adega de vinho de dois mods."""
    small_kitchen(fx, wood)
    for x in range(10, 14):
        conn = 'left' if x == 10 else 'right' if x == 13 else 'middle'
        fx.at(x, 4, f'kaleidoscope_tavern:bar_counter[connection={conn},facing=south]', loot=LOOT['cafe'] if x == 11 else None)
        fx.chair(x, 5, 'kaleidoscope_tavern:brown_bar_stool[facing={f},waterlogged=false]', 'north')
    fx.run([(10, 1), (11, 1)], f'hearthandharvest:{wood if wood != "cherry" else "oak"}_wine_rack[facing={{f}}]', 'north')
    fx.run([(12, 1), (13, 1)], f'vinery:{wood}_wine_rack_mid[facing={{f}},open=false]', 'north')
    fx.at(14, 1, 'kaleidoscope_tavern:barrel')
    fx.at(14, 2, 'kaleidoscope_tavern:barrel')
    fx.at(14, 3, 'brewinandchewin:keg[facing=west,vertical=false]')
    mixed_dining(fx, 3, 9, 2, f'redeco:{wood}_table', chairs_for(wood), LOOT['home'])
    for x, z in ((11, 9), (12, 11)):
        fx.at(x, z, f'another_furniture:{wood}_table[facing=north]')
        fx.chair(x - 1, z, f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=3]', 'east')
        fx.chair(x + 1, z, f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=3]', 'west')
    fx.lantern(11, 5)
    fx.lantern(11, 10)
    storage_south(fx, wood, LOOT['cellar'] if 'cellar' in LOOT else LOOT['home'])
    fx.at(11, 14, 'kaleidoscope_tavern:barrel')
    fx.at(12, 14, 'minecraft:barrel[facing=up,open=false]', loot=LOOT['home'])


def g_queijo(fx, wood):
    """queijaria: prateleiras de queijo do Meadow, caixotes de leite e ovos do Hearth & Harvest."""
    small_kitchen(fx, wood)
    mixed_dining(fx, 3, 9, 2, f'cfm:{wood if wood != "cherry" else "oak"}_table', chairs_for(wood), LOOT['home'])
    for z in (3, 4, 5, 9, 10, 11):
        fx.at(14, z, 'meadow:cheese_rack[facing={f}]', wall='east')
    fx.run([(10, 1), (11, 1), (12, 1)], 'meadow:cheese_rack[facing={f}]', 'north')
    fx.at(13, 1, 'hearthandharvest:milk_crate[type=bottom]')
    fx.at(14, 1, 'hearthandharvest:egg_crate[type=bottom]')
    fx.at(11, 7, f'refurbished_furniture:{wood}_table[east=true,north=false,south=false,west=false]')
    fx.at(12, 7, f'refurbished_furniture:{wood}_table[east=false,north=false,south=false,west=true]')
    fx.at(11, 7, 'farmersdelight:cutting_board[facing=south]', y=2)
    fx.lantern(11, 7)
    storage_south(fx, wood, LOOT['farm'])
    fx.at(11, 14, 'hearthandharvest:milk_crate[type=bottom]')
    fx.at(12, 14, 'hearthandharvest:goat_milk_crate[type=bottom]')
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=LOOT['farm'])


def g_pescador(fx, wood):
    """casa do pescador: barris de peixe e armadilhas do Crabber's Delight, varal de peixe seco do Youkai."""
    small_kitchen(fx, wood)
    mixed_dining(fx, 3, 9, 2, f'refurbished_furniture:{wood}_table', chairs_for(wood), LOOT['home'])
    for i, z in enumerate((3, 4, 5, 6)):
        fx.at(14, z, ['crabbersdelight:cod_barrel', 'crabbersdelight:salmon_barrel',
                      'crabbersdelight:crab_barrel', 'crabbersdelight:shrimp_barrel'][i])
    fx.run([(10, 1), (12, 1)], 'youkaishomecoming:drying_rack[facing={f}]', 'north')
    fx.at(11, 1, 'youkaishomecoming:dried_fish[facing={f}]', wall='north')
    fx.at(13, 1, 'youkaishomecoming:drying_rack[facing={f}]', wall='north')
    fx.at(11, 8, 'crabbersdelight:crab_trap[facing=north,hanging=false,waterlogged=false]')
    fx.at(12, 8, 'crabbersdelight:crab_trap[facing=north,hanging=false,waterlogged=false]')
    fx.at(11, 10, f'another_furniture:{wood}_table[facing=north]')
    fx.at(11, 10, 'farmersdelight:cutting_board[facing=south]', y=2)
    fx.chair(10, 10, f'another_furniture:{wood}_chair[facing={{f}},tucked=false,variant=4]', 'east')
    fx.lantern(11, 6)
    storage_south(fx, wood, LOOT['dock'] if 'dock' in LOOT else LOOT['home'])
    fx.at(11, 14, 'crabbersdelight:clam_barrel')
    fx.at(12, 14, 'supplementaries:sack')
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=LOOT['home'])


def g_alfaiate(fx, wood):
    """alfaiataria: mesa de costura do Legendary Survival, teares e fardos de algodao."""
    small_kitchen(fx, wood)
    mixed_dining(fx, 3, 9, 2, f'refurbished_furniture:{wood}_table', chairs_for(wood), LOOT['home'])
    fx.at(14, 3, 'legendarysurvivaloverhaul:sewing_table[facing={f}]', wall='east')
    fx.at(14, 4, 'minecraft:loom[facing={f}]', wall='east')
    fx.at(14, 5, 'legendarysurvivaloverhaul:sewing_table[facing={f}]', wall='east')
    fx.chair(13, 3, f'refurbished_furniture:{wood}_chair[facing={{f}},tucked=false]', 'east')
    fx.run([(10, 1), (11, 1)], 'hearthandharvest:cotton_bale[axis=y]', 'north')
    for x, c in ((12, 'red'), (13, 'white'), (14, 'blue')):
        fx.at(x, 1, f'minecraft:{c}_wool')
    fx.carpet(10, 7, 13, 10, 'purple')
    fx.lantern(12, 4)
    fx.lantern(11, 9)
    storage_south(fx, wood, LOOT['home'])
    fx.at(11, 14, 'hearthandharvest:cotton_bale[axis=y]')
    fx.at(12, 14, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=left,open=false]', loot=LOOT['bedroom'], wall='south')
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=LOOT['home'])


def g_herbanario(fx, wood):
    """herbanario: bancada de botanico do Beautify, potes, vasos pendurados, alambique e flores."""
    small_kitchen(fx, wood)
    mixed_dining(fx, 3, 9, 2, f'redeco:{wood}_table', chairs_for(wood), LOOT['home'])
    fx.at(14, 3, 'beautify:botanist_workbench[facing={f}]', wall='east')
    fx.at(14, 4, 'minecraft:brewing_stand[has_bottle_0=true,has_bottle_1=false,has_bottle_2=true]')
    fx.at(14, 5, 'beautify:botanist_workbench[facing={f}]', wall='east')
    fx.run([(10, 1), (11, 1), (12, 1)], 'supplementaries:item_shelf[facing={f}]', 'north', y=2)
    fx.at(10, 1, 'supplementaries:jar')
    fx.at(11, 1, 'farmersrespite:green_tea_leaves_sack')
    fx.at(12, 1, 'supplementaries:jar')
    fx.at(13, 1, 'meadow:wooden_flower_pot_big')
    fx.at(14, 1, 'minecraft:potted_red_tulip')
    for x in (10, 12):
        fx.at(x, 7, 'beautify:hanging_pot[grown=true,hanging=true,potflower=3]', y=3)
    fx.at(11, 8, 'furniture:wooden_planter[facing=north,type=left]')
    fx.at(12, 8, 'furniture:wooden_planter[facing=north,type=right]')
    fx.lantern(11, 5)
    storage_south(fx, wood, LOOT['home'])
    fx.at(11, 14, 'supplementaries:flower_box[facing=north,face=floor]')
    fx.at(12, 14, 'minecraft:potted_azalea_bush')
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=LOOT['farm'])


GROUND = {'cozinha': g_cozinha, 'cha': g_cha, 'taverna': g_taverna, 'queijo': g_queijo,
          'pescador': g_pescador, 'alfaiate': g_alfaiate, 'herbanario': g_herbanario}


# ---------------------------------------------------------------- temas do andar
def bedroom_af(fx, color, wood, loot):
    """quarto oeste com Another Furniture + Candlelight (mesma planta do bedroom_west)."""
    fx.bed(2, 1, color, 'north', loot)
    fx.bed(3, 1, color, 'north', loot)
    for x in (1, 4):
        fx.at(x, 1, f'another_furniture:{wood}_drawer[facing={{f}},open=false]', loot=loot, wall='north')
        fx.at(x, 1, 'candlelight:lamp[hanging=false]', y=2)
    fx.at(1, 5, f'cfm:{wood if wood != "cherry" else "oak"}_bedside_cabinet[facing=east,open=false]', loot=loot)
    fx.at(1, 6, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=right,open=false]', loot=loot, wall='west')
    fx.at(2, 3, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=loot)
    fx.run([(1, 14), (2, 14)], f'another_furniture:{wood}_shelf[facing={{f}},horizontal=single]', 'south')
    fx.at(5, 14, 'minecraft:potted_fern')
    fx.lantern(3, 4)
    fx.sconce(5, 9, 'east')
    fx.sconce(1, 11, 'west')


def bedroom_kids(fx, wood, loot):
    """quarto de criancas: duas camas de solteiro de cores diferentes."""
    fx.bed(2, 1, 'light_blue', 'north', loot)
    fx.bed(4, 1, 'pink', 'north', loot)
    fx.at(3, 1, f'refurbished_furniture:{wood}_drawer[facing={{f}},left=false,right=false,open=false]', loot=loot, wall='north')
    fx.at(3, 1, 'beautify:lamp_jar[hanging=false]', y=2)
    fx.at(1, 5, f'farmersdelight:{wood}_cabinet[facing={{f}},open=false]', loot=loot, wall='west')
    fx.at(2, 5, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=loot)
    fx.carpet(2, 7, 4, 10, 'yellow')
    fx.run([(1, 14), (2, 14)], 'minecraft:bookshelf', 'south')
    fx.at(5, 14, 'minecraft:potted_red_tulip')
    fx.lantern(3, 4)
    fx.sconce(5, 9, 'east')
    fx.sconce(1, 11, 'west')


def upper_east(fx, wood):
    """banheiro (NE) + escritorio/sala intima (SE) com moveis de mods diferentes."""
    B = LOOT['bathroom']
    fx.at(8, 1, 'refurbished_furniture:white_toilet[facing={f}]', loot=B, wall='north')
    fx.at(10, 1, f'refurbished_furniture:{wood}_basin[facing={{f}}]', loot=B, wall='north')
    fx.at(12, 1, 'refurbished_furniture:white_bath[facing=west,type=head]')
    fx.at(13, 1, 'refurbished_furniture:white_bath[facing=west,type=bottom]')
    fx.at(14, 4, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=left,open=false]', loot=B, wall='south')
    fx.at(7, 4, 'minecraft:potted_fern')
    fx.lantern(10, 3)
    fx.at(14, 8, f'refurbished_furniture:{wood}_desk[facing={{f}},left=false,right=false]', loot=LOOT['home'], wall='east')
    fx.at(14, 8, 'candlelight:typewriter_iron[facing=west,full=1]', y=2)
    fx.chair(13, 8, f'kaleidoscope_cookery:chair_{wood}[facing={{f}},has_carpet=false,waterlogged=false]', 'east')
    fx.run([(14, 10), (14, 11)], 'minecraft:bookshelf', 'east')
    fx.at(10, 14, 'kaleidoscope_tavern:brown_sofa[facing={f},connection=left,waterlogged=false]', wall='south')
    fx.at(11, 14, 'kaleidoscope_tavern:brown_sofa[facing={f},connection=right,waterlogged=false]', wall='south')
    fx.at(12, 14, 'tanukidecor:antique_radio[facing=north]')
    fx.carpet(9, 11, 12, 13, 'green')
    fx.lantern(11, 10)
    fx.sconce(7, 9, 'west')


def upper(fx, theme, wood):
    fx.wall_x(6, 1, 14, gaps=(12,))
    fx.wall_z(5, 7, 14, gaps=(11,))
    if theme == 'quartos_rf':
        H.bedroom_west(fx, 'brown', wood, LOOT['bedroom'])
    elif theme == 'quartos_af':
        bedroom_af(fx, 'white', wood, LOOT['bedroom'])
    else:
        bedroom_kids(fx, wood, LOOT['bedroom'])
    upper_east(fx, wood)


# ---------------------------------------------------------------- deposito
def deposito(fx, wood):
    """estantes duplas de caixotes nos dois lados do corredor central (x7-8); metade dos
    containers tem loot sunlit:deposito, o resto e estoque decorativo de varios mods."""
    D = LOOT['deposito']
    loot_cycle = ['minecraft:barrel[facing=up,open=false]', f'refurbished_furniture:{wood}_crate[open=false]',
                  'minecraft:chest[facing=south,type=single,waterlogged=false]']
    # so bloco cheio (caixote/barril) aguenta outro em cima: bau e saco ficam sem nada por cima
    full = [f'redeco:{wood}_crate[facing=south,propped=false]', f'embellishcraft:{wood}_wooden_crate', 'create:cardboard_block[axis=x]',
            'hearthandharvest:apple_crate', 'crabbersdelight:cod_barrel', 'create:andesite_casing']
    soft = ['supplementaries:sack', 'farm_and_charm:flour_bag[facing=south]', 'farmersdelight:rice_bag']
    i = 0
    for z0 in (3, 7, 11):
        for x0, x1 in ((2, 5), (10, 13)):
            for z in (z0, z0 + 1):
                for x in range(x0, x1 + 1):
                    if (x + z) % 2 == 0:
                        base = loot_cycle[i % len(loot_cycle)]
                        fx.at(x, z, base, loot=D)
                    elif i % 4 == 3:
                        base = soft[i % len(soft)]
                        fx.at(x, z, base)
                    else:
                        base = full[i % len(full)]
                        fx.at(x, z, base)
                    if 'chest' not in base and base not in soft and i % 3:
                        fx.at(x, z, full[(i + 2) % len(full)], y=2)
                    i += 1
    # estantes de parede nos corredores, lanternas sobre os corredores
    for z in (5, 9):
        fx.at(1, z, f'candlelight:{wood}_shelf[facing={{f}}]', wall='west')
        fx.at(14, z, f'candlelight:{wood}_shelf[facing={{f}}]', wall='east')
        fx.at(1, z + 1, 'supplementaries:item_shelf[facing={f}]', y=2, wall='west')
        fx.at(14, z + 1, 'supplementaries:item_shelf[facing={f}]', y=2, wall='east')
    for x, z in ((4, 6), (11, 6), (4, 10), (11, 10), (7, 4), (8, 12)):
        fx.lantern(x, z)
    # escritorio do encarregado no canto NO e NE
    fx.at(1, 1, f'refurbished_furniture:{wood}_desk[facing={{f}},left=false,right=false]', loot=D, wall='north')
    fx.at(1, 1, 'candlelight:typewriter_iron[facing=south,full=1]', y=2)
    fx.at(2, 1, 'cluttered:general_store_cabinet[facing={f},part=1]', wall='north')
    fx.at(13, 1, 'create:item_vault[axis=x,large=false]')
    fx.at(14, 1, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=D)
    fx.at(12, 1, f'refurbished_furniture:{wood}_crate[open=false]', loot=D)
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=D)
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=D)


def build_deposito(name, mat):
    wood = WOOD[mat]
    P = f'building_{name}/{name}'
    palettes_for(P, mat)
    PG, PT = P + '_ground_palette', P + '_top_palette'
    g = H.shell_ground()
    fx = H.furnish(PG, g)
    deposito(fx, wood)
    fx.sconce(1, 12, 'west')
    fx.sconce(14, 12, 'east')
    H.write_part(f'building_{name}/{name}_ground', PG, H.rows(g))
    H.write_part(f'building_{name}/{name}_top', PT, H.rows(H.shell_roof()))
    H.write_building(f'building_{name}', [('ground', f'building_{name}/{name}_ground'), ('top', f'building_{name}/{name}_top')])


# ---------------------------------------------------------------- montagem
def build(name, mat, ground, top_theme, roof):
    wood = WOOD[mat]
    P = f'building_vila_{name}/vila_{name}'
    palettes_for(P, mat)
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    g = H.shell_ground()
    if top_theme:
        H.ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = H.furnish(PG, g)
    GROUND[ground](fx, wood)
    fx.sconce(1, 9, 'west')
    fx.sconce(14, 11, 'east')
    H.write_part(f'building_vila_{name}/vila_{name}_ground', PG, H.rows(g))
    floors = [('ground', f'building_vila_{name}/vila_{name}_ground')]
    if top_theme:
        f = H.shell_floor()
        H.ladder_shaft(f, layers=(0, 1, 2))
        fx = H.furnish(PF, f, upper=True)
        upper(fx, top_theme, wood)
        H.write_part(f'building_vila_{name}/vila_{name}_floor1', PF, H.rows(f))
        floors.append(('floor', f'building_vila_{name}/vila_{name}_floor1'))
    r = roof_gable(None, None) if roof == 'duas_aguas' else H.shell_roof()
    H.write_part(f'building_vila_{name}/vila_{name}_top', PT, H.rows(r))
    floors.append(('top', f'building_vila_{name}/vila_{name}_top'))
    H.write_building(f'building_vila_{name}', floors)


def main():
    for n, m in DEPOSITOS:
        build_deposito(n, m)
    print(f'vila: {len(DEPOSITOS)} depositos gravados (casas: schematics.py)' + (' (check-only)' if H.CHECK_ONLY else ''))


if __name__ == '__main__':
    main()
