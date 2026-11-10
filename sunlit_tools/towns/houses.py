"""Casas comfy novas para o preset sunlit cozy (so chunks novos).

Gera 3 predios 16x16 em orientacao unica + registra nos citystyles:
- building_casafazenda  (vila): cozinha caipira + quarto + banheiro
- building_padariacomfy (vila, centro): padaria no terreo + moradia em cima
- building_oficinacreate (vila): oficina Create no terreo + deposito/moradia

Tambem liga multis ja vendorizadas e hoje sem uso:
- multi_farmhouse1, multi_cabin2 (vila)

Uso: python3 sunlit_tools/towns/houses.py [--check-only]
Regras: todo bloco passa por mapping.parse/exists/valid_props antes de
escrever qualquer arquivo. No final rode validate.py (tem que dar OK).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapping as M
import interior as I
import mix as MIX

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit', 'lostcities')
CHECK_ONLY = '--check-only' in sys.argv

# ---------------------------------------------------------------- helpers
PALETTES = {}  # part_name -> {char: entry}


def B(block, loot=None):
    """Valida e monta 'id[props]'. So aceita blocos do registry com props validas."""
    bid, props = M.parse(block)
    if not M.exists(bid):
        raise SystemExit(f'bloco inexistente: {block}')
    vp = M.valid_props(bid)
    for k, v in props.items():
        if k not in vp or v not in vp[k]:
            raise SystemExit(f'propriedade invalida: {block}')
    e = {'block': block}
    if loot:
        e['loot'] = loot
    return e


def pal(part, char, block, loot=None):
    if ' ' == char:
        raise SystemExit('char espaco nao pode entrar em paleta')
    PALETTES.setdefault(part, {})[char] = B(block, loot)


def grid():
    return [[' ' for _ in range(16)] for _ in range(16)]


def put(g, x, z, c):
    g[z][x] = c


def rect(g, x0, z0, x1, z1, c):
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            g[z][x] = c


def ring(g, c):
    for i in range(16):
        g[0][i] = c
        g[15][i] = c
        g[i][0] = c
        g[i][15] = c


def mixed_entry(c, e):
    """moveis sem loot (fogao, panela, tabua, cesto, colheita) viram sorteio entre mods"""
    mixed = None if e.get('loot') else MIX.blocks_for(e['block'])
    return {'char': c, 'blocks': mixed} if mixed else {'char': c, **e}


def write_part(name, palette_name, slices):
    used = {c for sl in slices for row in sl for c in row} - {' '}
    pal = PALETTES.get(palette_name, {})
    miss = used - set(pal)
    if miss:
        raise SystemExit(f'{name}: chars sem paleta: {sorted(miss)}')
    if CHECK_ONLY:
        return
    pj = {'name': name, 'refpalette': f'sunlit:{palette_name}',
          'xsize': 16, 'zsize': 16, 'slices': slices}
    pp = os.path.join(DATA, 'parts', name + '.json')
    os.makedirs(os.path.dirname(pp), exist_ok=True)
    with open(pp, 'w') as f:
        json.dump(pj, f)
    pj2 = {'name': palette_name,
           'palette': [mixed_entry(c, pal[c]) for c in sorted(pal)]}
    pp2 = os.path.join(DATA, 'palettes', palette_name + '.json')
    os.makedirs(os.path.dirname(pp2), exist_ok=True)
    with open(pp2, 'w') as f:
        json.dump(pj2, f)


def write_building(name, floors, cellars=0):
    if CHECK_ONLY:
        return
    d = os.path.join(DATA, 'buildings', name)
    os.makedirs(d, exist_ok=True)
    parts, n = [], 0
    for kind, pname in floors:
        parts.append({'top': kind == 'top', 'cellar': False,
                      'ground': kind == 'ground', 'part': f'sunlit:{pname}'})
        n += 1
    b = {'filler': 'G', 'rubber': ' ', 'allowDoors': False,
         'allowFillers': True, 'overrideFloors': True,
         'minfloors': n - 1, 'maxfloors': n - 1,
         'mincellars': cellars, 'maxcellars': cellars, 'parts': parts}
    with open(os.path.join(d, name.split('/')[-1] + '.json'), 'w') as f:
        json.dump(b, f)


LOOT = {
    'kitchen': 'sunlit:kitchen', 'bedroom': 'sunlit:bedroom',
    'home': 'sunlit:home', 'farm': 'sunlit:farm', 'fridge': 'sunlit:fridge',
    'bakery': 'sunlit:bakery', 'workshop': 'sunlit:workshop',
    'cafe': 'sunlit:cafe', 'bathroom': 'sunlit:bathroom',
    'grocery': 'sunlit:grocery',
}

# ---------------------------------------------------------------- base comum
WALL = 'W'       # parede externa
FLOOR = 'F'      # piso
FOUND = 'f'      # fundacao
GLASS = 'g'      # janela
DOOR_L = 'd'     # porta lower (dobradica a oeste)
DOOR_U = 'D'     # porta upper
DOOR_L2 = '¡'  # porta lower (dobradica a leste): as duas folhas formam porta dupla
DOOR_U2 = '¢'
CEIL = 'C'       # teto
ROOF = 'R'       # telhado/parapeito
LADDER = 'H'     # escada de mao (furo no teto/piso acima vai junto)


def base_palette(part, wall, floor, win):
    pal(part, WALL, wall)
    pal(part, FLOOR, floor)
    pal(part, FOUND, 'minecraft:stone_bricks')
    # 'G' e o filler do building JSON (preenche abaixo do predio ate o terreno)
    pal(part, 'G', 'minecraft:stone_bricks')
    pal(part, GLASS, win)
    pal(part, DOOR_L, 'minecraft:dark_oak_door[half=lower,hinge=left,facing=north,open=false]')
    pal(part, DOOR_U, 'minecraft:dark_oak_door[half=upper,hinge=left,facing=north,open=false]')
    pal(part, DOOR_L2, 'minecraft:dark_oak_door[half=lower,hinge=right,facing=north,open=false]')
    pal(part, DOOR_U2, 'minecraft:dark_oak_door[half=upper,hinge=right,facing=north,open=false]')
    pal(part, CEIL, floor)
    pal(part, ROOF, 'minecraft:oak_slab[type=bottom]')
    # escada em x=14 encosta na parede leste (x=15): facing=west
    pal(part, LADDER, 'minecraft:ladder[facing=west]')
    pal(part, 'l', 'minecraft:lantern[hanging=true]')


def shell_ground(wall_door_x=(7, 8)):
    """y0..y5 (6 fatias: o Lost Cities empilha andares de 6 em 6 = FLOORHEIGHT).
    Retorna [y0..y5]. Portas duplas N (z=0) e S (z=15). Teto duplo (y4+y5)."""
    y0, y1, y2, y3, y4, y5 = grid(), grid(), grid(), grid(), grid(), grid()
    rect(y0, 0, 0, 15, 15, FOUND)
    rect(y0, 1, 1, 14, 14, FLOOR)
    for g in (y1, y2, y3):
        ring(g, WALL)
    # janelas no y2 (faixa), menos cantos e portas
    for x in range(2, 14):
        if x not in wall_door_x:
            y2[0][x] = GLASS
            y2[15][x] = GLASS
    for z in range(2, 14):
        y2[z][0] = GLASS
        y2[z][15] = GLASS
    xl, xr = wall_door_x
    for zz in (0, 15):
        y1[zz][xl], y2[zz][xl] = DOOR_L, DOOR_U
        y1[zz][xr], y2[zz][xr] = DOOR_L2, DOOR_U2
    rect(y4, 0, 0, 15, 15, CEIL)
    rect(y5, 0, 0, 15, 15, CEIL)
    return [y0, y1, y2, y3, y4, y5]


def shell_floor():
    """Andar de cima: 6 fatias (FLOORHEIGHT). Teto duplo (y9+yA)."""
    y5, y6, y7, y8, y9 = grid(), grid(), grid(), grid(), grid()
    rect(y5, 0, 0, 15, 15, FLOOR)
    for g in (y6, y7, y8):
        ring(g, WALL)
    for x in range(2, 14):
        y7[0][x] = GLASS
        y7[15][x] = GLASS
    for z in range(2, 14):
        y7[z][0] = GLASS
        y7[z][15] = GLASS
    rect(y9, 0, 0, 15, 15, CEIL)
    yA = grid()
    rect(yA, 0, 0, 15, 15, CEIL)
    return [y5, y6, y7, y8, y9, yA]


def shell_roof():
    y0, y1 = grid(), grid()
    ring(y0, WALL)
    rect(y1, 0, 0, 15, 15, ROOF)
    # chamine
    put(y0, 12, 12, 'K')
    put(y1, 12, 12, 'K')
    return [y0, y1]


def ladder_shaft(slices, x=14, z=13, layers=(1, 2, 3, 4, 5, 6)):
    for y in layers:
        if y < len(slices):
            slices[y][z][x] = LADDER


def furnish(part, slices, upper=False):
    return I.Furnish(PALETTES, pal, part, slices, free=I.FREE_UPPER if upper else I.FREE_GROUND)


def rows(slices):
    return [[''.join(r) for r in sl] for sl in slices]


# moveis recorrentes (facing resolvido por interior.facing_for)
def kitchen_line(fx, wood, cells, loot):
    """bancada na parede norte: cells = [(x, tipo)], tipo em stove/sink/cab/drawer."""
    kinds = {
        'stove': 'refurbished_furniture:light_stove[facing={f},open=false]',
        'sink': f'refurbished_furniture:{wood}_kitchen_sink[facing={{f}}]',
        'cab': f'refurbished_furniture:{wood}_kitchen_cabinetry[facing={{f}},shape=default]',
        'drawer': f'refurbished_furniture:{wood}_kitchen_drawer[facing={{f}},open=false]',
    }
    for x, k in cells:
        fx.at(x, 1, kinds[k], loot=loot, wall='north')


def fridge(fx, x, z, wall, loot):
    fx.at(x, z, 'refurbished_furniture:light_freezer[facing={f},open=false]', loot=loot, wall=wall)
    fx.at(x, z, 'refurbished_furniture:light_fridge[facing={f},open=false]', y=2, loot=loot, wall=wall)


def dining(fx, x0, z, n, table, chair, loot=None):
    """mesa de n lugares no eixo x (x0..x0+n-1, z) com cadeiras dos dois lados e nas pontas."""
    for i in range(n):
        x = x0 + i
        if table.startswith('refurbished_furniture:'):
            t = f'{table}[east={str(i < n - 1).lower()},north=false,south=false,west={str(i > 0).lower()}]'
        else:
            t = table
        fx.at(x, z, t, loot=loot)
        fx.chair(x, z - 1, chair, 'south')
        fx.chair(x, z + 1, chair, 'north')
    fx.chair(x0 - 1, z, chair, 'east')
    fx.chair(x0 + n, z, chair, 'west')


def bedroom_west(fx, color, wood, loot, double=True):
    """quarto no lado oeste (x1..5): cama com cabeceira na parede norte, criados-mudos
    com abajur, guarda-roupa na parede oeste, bau no pe da cama, estante no fundo."""
    fx.bed(2, 1, color, 'north', loot)
    if double:
        fx.bed(3, 1, color, 'north', loot)
    right = 4 if double else 3
    for x in (1, right):
        fx.at(x, 1, f'refurbished_furniture:{wood}_drawer[facing={{f}},left=false,right=false,open=false]',
              loot=loot, wall='north')
        fx.at(x, 1, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.at(1, 5, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=left,open=false]', loot=loot, wall='west')
    fx.at(1, 6, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=right,open=false]', loot=loot, wall='west')
    fx.at(2, 3, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=loot)
    fx.run([(1, 14), (2, 14)], 'minecraft:bookshelf', 'south')
    fx.at(5, 14, 'minecraft:potted_azalea_bush')
    fx.lantern(3, 4)
    fx.sconce(5, 9, 'east')
    fx.sconce(1, 11, 'west')


# ================================================================ 1. FAZENDA
def casa_fazenda():
    P = 'building_casafazenda/casafazenda'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'minecraft:oak_planks', 'redeco:polished_oak_planks',
                     'createdeco:iron_window')
        PALETTES[p]['K'] = B('minecraft:bricks')
    K, H, FA, BR = LOOT['kitchen'], LOOT['home'], LOOT['farm'], LOOT['bedroom']

    # ---- terreo: cozinha em L (NO) + jantar (O) | sala de estar (L) | despensa (SO)
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fridge(fx, 1, 1, 'north', LOOT['fridge'])
    kitchen_line(fx, 'spruce', [(2, 'stove'), (3, 'cab'), (4, 'sink'), (5, 'cab'), (6, 'drawer')], K)
    fx.at(2, 1, 'refurbished_furniture:frying_pan[facing=south,lit=false]', y=2)
    fx.at(5, 1, 'refurbished_furniture:oak_cutting_board[facing={f}]', y=2, wall='north')
    fx.at(1, 2, 'refurbished_furniture:spruce_kitchen_cabinetry[facing={f},shape=default]', loot=K, wall='west')
    fx.at(1, 3, 'refurbished_furniture:spruce_kitchen_drawer[facing={f},open=false]', loot=K, wall='west')
    fx.at(1, 4, 'farmersdelight:spruce_cabinet[facing={f},open=false]', loot=K, wall='west')
    # mescla de mods na bancada: tabua kaleidoscope + cesta de frutas + saco de batata do Let's Do
    fx.at(3, 1, 'kaleidoscope_cookery:chopping_board[facing=south,waterlogged=false]', y=2)
    fx.at(1, 4, 'kaleidoscope_cookery:fruit_basket[facing=east,waterlogged=false]', y=2)
    fx.at(1, 3, 'farm_and_charm:potato_bag[facing={f}]', y=2, wall='west')
    fx.lantern(4, 3)
    dining(fx, 3, 8, 2, 'refurbished_furniture:oak_table', 'refurbished_furniture:oak_chair[facing={f},tucked=false]', H)
    fx.lantern(3, 8)
    # despensa no canto SO
    fx.at(1, 12, 'refurbished_furniture:oak_storage_jar[facing={f}]', loot=FA, wall='west')
    fx.at(1, 13, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(2, 14, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(3, 14, 'farmersdelight:oak_cabinet[facing={f},open=false]', loot=FA, wall='south')
    fx.at(5, 14, 'furniture:wooden_planter[facing={f},type=none]', wall='south')
    # sala: sofa na parede leste olhando a mesa de centro e duas poltronas
    for z in (6, 7):
        fx.at(14, z, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=H, wall='east')
    fx.at(12, 6, 'cfm:oak_coffee_table[east=false,north=false,south=true,tall=false,west=false]')
    fx.at(12, 7, 'cfm:oak_coffee_table[east=false,north=true,south=false,tall=false,west=false]')
    for z in (6, 7):
        fx.chair(10, z, 'another_furniture:oak_chair[facing={f},tucked=false,variant=1]', 'east')
    fx.carpet(11, 5, 13, 8, 'brown')
    fx.lantern(12, 6)
    fx.run([(10, 1), (11, 1), (12, 1)], 'minecraft:bookshelf', 'north')
    fx.at(13, 1, 'refurbished_furniture:oak_drawer[facing={f},left=false,right=false,open=false]', loot=H, wall='north')
    fx.at(13, 1, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.at(14, 1, 'minecraft:potted_fern')
    # entrada sul: armario de casacos + caixas da roca
    fx.at(11, 14, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=H, wall='south')
    fx.at(12, 14, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.sconce(1, 9, 'west')
    fx.sconce(14, 10, 'east')
    fx.sconce(4, 14, 'south')
    fx.sconce(10, 1, 'north')
    write_part('building_casafazenda/casafazenda_ground', PG, rows(g))

    # ---- andar: quarto (O) | banheiro (NE) | escritorio/sala intima (SE)
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    fx.wall_x(6, 1, 14, gaps=(12,))
    fx.wall_z(5, 7, 14, gaps=(11,))
    bedroom_west(fx, 'brown', 'oak', BR)
    fx.carpet(2, 8, 4, 10, 'white')
    # banheiro
    fx.at(8, 1, 'refurbished_furniture:oak_toilet[facing={f}]', loot=LOOT['bathroom'], wall='north')
    fx.at(10, 1, 'refurbished_furniture:oak_basin[facing={f}]', loot=LOOT['bathroom'], wall='north')
    fx.at(14, 4, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=LOOT['bathroom'], wall='south')
    fx.at(7, 4, 'minecraft:potted_fern')
    fx.lantern(10, 3)
    # escritorio
    fx.at(14, 8, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=H, wall='east')
    fx.at(14, 8, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(13, 8, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'east')
    fx.run([(14, 10), (14, 11)], 'minecraft:bookshelf', 'east')
    for x in (10, 11):
        fx.at(x, 14, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=H, wall='south')
    fx.carpet(9, 11, 12, 13, 'green')
    fx.lantern(11, 10)
    fx.sconce(7, 9, 'west')
    write_part('building_casafazenda/casafazenda_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_casafazenda/casafazenda_top', PT, rows(r))
    write_building('building_casafazenda',
                   [('ground', 'building_casafazenda/casafazenda_ground'),
                    ('floor', 'building_casafazenda/casafazenda_floor1'),
                    ('top', 'building_casafazenda/casafazenda_top')])


# ================================================================ 2. PADARIA
def padaria_comfy():
    P = 'building_padariacomfy/padariacomfy'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'minecraft:bricks', 'redeco:polished_spruce_planks',
                     'create:dark_oak_window_pane')
        PALETTES[p]['K'] = B('minecraft:bricks')
    BK, CF, K, H, BR = LOOT['bakery'], LOOT['cafe'], LOOT['kitchen'], LOOT['home'], LOOT['bedroom']

    # ---- terreo: producao (O) atras do balcao de vitrines | cafe (L)
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fx.at(1, 1, 'bakery:cabinet[facing={f},open=false]', loot=BK, wall='north')
    for x in (2, 3):
        fx.at(x, 1, 'farmersdelight:stove[facing={f},lit=false]', loot=K, wall='north')
    fx.at(2, 1, 'farmersdelight:cooking_pot[facing=south,support=none]', y=2)
    fx.at(4, 1, 'bakery:baker_station[facing={f}]', loot=BK, wall='north')
    fx.at(5, 1, 'bakery:baker_station[facing={f}]', loot=BK, wall='north')
    for z in (3, 4, 5):
        fx.at(1, z, 'bakery:bread_crate[bites=0,facing={f}]', loot=BK, wall='west')
    fx.at(1, 7, 'bakery:drawer[facing={f},open=false]', loot=BK, wall='west')
    fx.at(1, 8, 'bakery:cabinet[facing={f},open=false]', loot=BK, wall='west')
    fx.at(1, 13, 'minecraft:barrel[facing=up,open=false]', loot=BK)
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=BK)
    fx.at(2, 14, 'minecraft:barrel[facing=up,open=false]', loot=BK)
    fx.at(3, 14, 'bakery:breadbox[facing={f}]', loot=BK, wall='south')
    # balcao corrido em x=5 virado para os clientes (leste), passagem em z=1..2 e z>=10
    for z in range(3, 10):
        fx.at(5, z, 'bakery:brick_counter[facing=east,type=none]', loot=BK)
    fx.at(5, 4, 'bakery:cake_display[facing=east,type=none]', y=2)
    fx.at(5, 6, 'bakery:cupcake_display[facing=east]', y=2)
    fx.at(5, 8, 'cozycafe:cafe_menu[facing=east,dish=false,dirty=false]', y=2)
    fx.lantern(3, 4)
    fx.lantern(3, 10)
    # cafe: duas mesinhas com duas cadeiras cada
    for z in (4, 10):
        fx.at(11, z, 'another_furniture:spruce_table[facing=north,leg_1=true,leg_2=true,leg_3=true,leg_4=true]', loot=CF)
        fx.chair(10, z, 'another_furniture:spruce_chair[facing={f},tucked=false,variant=1]', 'east')
        fx.chair(12, z, 'another_furniture:spruce_chair[facing={f},tucked=false,variant=1]', 'west')
        fx.lantern(11, z)
    fx.at(14, 1, 'minecraft:potted_azalea_bush')
    fx.at(9, 1, 'minecraft:potted_flowering_azalea_bush')
    fx.at(14, 7, 'furniture:wooden_planter[facing={f},type=none]', wall='east')
    fx.at(14, 14, 'minecraft:potted_fern')
    fx.sconce(1, 11, 'west')
    fx.sconce(14, 10, 'east')
    fx.sconce(11, 14, 'south')
    fx.sconce(11, 1, 'north')
    write_part('building_padariacomfy/padariacomfy_ground', PG, rows(g))

    # ---- andar: quarto (O) | copa + sala (L)
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    fx.wall_x(6, 1, 14, gaps=(12,))
    bedroom_west(fx, 'white', 'birch', BR)
    fx.carpet(2, 8, 4, 10, 'light_blue')
    fridge(fx, 14, 1, 'north', LOOT['fridge'])
    kitchen_line(fx, 'birch', [(9, 'cab'), (10, 'drawer'), (11, 'sink'), (12, 'cab'), (13, 'stove')], K)
    dining(fx, 10, 5, 2, 'refurbished_furniture:birch_table', 'refurbished_furniture:birch_chair[facing={f},tucked=false]', H)
    fx.lantern(10, 5)
    for x in (10, 11):
        fx.at(x, 14, 'refurbished_furniture:white_sofa[facing={f},shape=default]', loot=H, wall='south')
    fx.at(10, 12, 'cfm:birch_coffee_table[east=true,north=false,south=false,tall=false,west=false]')
    fx.at(11, 12, 'cfm:birch_coffee_table[east=false,north=false,south=false,tall=false,west=true]')
    fx.carpet(9, 11, 12, 13, 'light_gray')
    fx.lantern(10, 11)
    fx.at(9, 14, 'minecraft:potted_dandelion')
    fx.sconce(7, 8, 'west')
    write_part('building_padariacomfy/padariacomfy_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_padariacomfy/padariacomfy_top', PT, rows(r))
    write_building('building_padariacomfy',
                   [('ground', 'building_padariacomfy/padariacomfy_ground'),
                    ('floor', 'building_padariacomfy/padariacomfy_floor1'),
                    ('top', 'building_padariacomfy/padariacomfy_top')])


# ================================================================ 3. OFICINA
def oficina_create():
    P = 'building_oficinacreate/oficinacreate'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'minecraft:andesite', 'minecraft:oak_planks',
                     'create:framed_glass_pane')
        PALETTES[p]['K'] = B('minecraft:bricks')
    WS, H, K, BR = LOOT['workshop'], LOOT['home'], LOOT['kitchen'], LOOT['bedroom']

    # ---- terreo: bancada de ferramentas (N oeste), estacao de mistura/prensa (N leste),
    # forja na parede oeste, estoque nos cantos sul
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fx.at(1, 1, 'minecraft:smithing_table', loot=WS)
    fx.at(2, 1, 'refurbished_furniture:workbench[facing={f},powered=false]', loot=WS, wall='north')
    fx.at(3, 1, 'minecraft:anvil[facing=east]', loot=WS)
    fx.at(4, 1, 'create:andesite_casing', loot=WS)
    fx.at(4, 1, 'create:brown_toolbox[facing=south,waterlogged=false]', y=2)
    fx.at(5, 1, 'create:depot', loot=WS)
    fx.at(6, 1, 'minecraft:grindstone[face=floor,facing=north]', loot=WS)
    fx.at(4, 1, 'create:cuckoo_clock[facing={f}]', y=3, wall='north')
    # mistura: bacia + misturador pendurado no teto (vao de 1 bloco entre eles, como no Create)
    fx.at(10, 1, 'create:basin[facing=down]', loot=WS)
    fx.at(10, 1, 'create:mechanical_mixer', y=3)
    fx.at(11, 1, 'create:cogwheel[axis=y]', y=3)
    fx.at(12, 1, 'create:depot', loot=WS)
    fx.at(12, 1, 'create:mechanical_press[facing=north]', y=3)
    fx.at(14, 1, 'create:fluid_tank[bottom=true,shape=window,top=false]', loot=WS)
    fx.at(14, 1, 'create:fluid_tank[bottom=false,shape=window,top=true]', y=2)
    fx.at(14, 2, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    fx.at(14, 3, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    # forja + estoque de minerio na parede oeste
    for z in (3, 4, 5):
        fx.at(1, z, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    fx.at(1, 7, 'minecraft:blast_furnace[facing={f},lit=false]', loot=WS, wall='west')
    fx.at(1, 8, 'minecraft:blast_furnace[facing={f},lit=false]', loot=WS, wall='west')
    fx.at(1, 10, 'create:schematic_table[facing=east]', loot=WS)
    # bancada central de montagem
    for x in (4, 5):
        fx.at(x, 8, 'create:andesite_casing', loot=WS)
    fx.at(5, 8, 'create:brown_toolbox[facing=north,waterlogged=false]', y=2)
    fx.at(4, 9, 'create:andesite_casing', loot=WS)
    fx.at(1, 14, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(2, 14, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(1, 13, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    fx.at(12, 14, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    for x, z in [(4, 4), (11, 4), (7, 8)]:
        fx.lantern(x, z)
    write_part('building_oficinacreate/oficinacreate_ground', PG, rows(g))

    # ---- andar: quarto (O) | prancheta + copa + sala (L)
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    fx.wall_x(6, 1, 14, gaps=(12,))
    bedroom_west(fx, 'red', 'spruce', BR, double=False)
    fx.carpet(2, 8, 4, 10, 'gray')
    fridge(fx, 14, 1, 'north', LOOT['fridge'])
    fx.at(13, 1, 'farmersdelight:stove[facing={f},lit=false]', loot=K, wall='north')
    fx.at(12, 1, 'farmersdelight:spruce_cabinet[facing={f},open=false]', loot=K, wall='north')
    dining(fx, 10, 4, 2, 'refurbished_furniture:spruce_table', 'refurbished_furniture:spruce_chair[facing={f},tucked=false]', H)
    fx.lantern(10, 4)
    fx.at(14, 8, 'refurbished_furniture:spruce_desk[facing={f},left=false,right=false]', loot=WS, wall='east')
    fx.at(14, 8, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(13, 8, 'refurbished_furniture:spruce_chair[facing={f},tucked=false]', 'east')
    fx.run([(14, 10), (14, 11)], 'minecraft:bookshelf', 'east')
    for x in (10, 11):
        fx.at(x, 14, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=H, wall='south')
    fx.carpet(9, 11, 12, 13, 'gray')
    fx.lantern(11, 10)
    fx.sconce(7, 8, 'west')
    write_part('building_oficinacreate/oficinacreate_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_oficinacreate/oficinacreate_top', PT, rows(r))
    write_building('building_oficinacreate',
                   [('ground', 'building_oficinacreate/oficinacreate_ground'),
                    ('floor', 'building_oficinacreate/oficinacreate_floor1'),
                    ('top', 'building_oficinacreate/oficinacreate_top')])


# ---------------------------------------------------------------- wiring
def wire():
    """pesos por bairro ficam todos no convert.py (SUNLIT_* / build_citystyle)"""
    return


def main():
    # confere condicoes de loot usadas
    cond = set()
    for f in os.listdir(os.path.join(DATA, 'conditions')):
        if f.endswith('.json'):
            cond.add('sunlit:' + f[:-5])
    for v in LOOT.values():
        if v not in cond:
            raise SystemExit(f'condicao ausente: {v}')
    # confere multis vendorizadas
    for m in ['multi_farmhouse1', 'multi_cabin2']:
        p = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns',
                         'data', 'sunlit', 'lostcities',
                         'multibuildings', m + '.json')
        if not os.path.exists(p):
            raise SystemExit(f'multi ausente: {p}')
    casa_fazenda()
    padaria_comfy()
    oficina_create()
    wire()
    print('casas geradas OK (check-only)' if CHECK_ONLY else 'casas gravadas + citystyles atualizados')


if __name__ == '__main__':
    main()
