"""Expansao cozy do preset sunlit (so chunks novos).

Gera 3 predios 16x16 em orientacao unica + 1 parque + 1 multibuilding:
- building_cozinhakaleido (vila): cozinha CAIPIRA COMPLETA de kaleidoscope
  no terreo (stove + pot + stockpot + chopping_board + kitchenware_racks +
  oil_pot + enamel_basin) + sala de jantar; quartos em cima
- building_adegavinho (vila, centro): adega vinery no terreo
  (fermentation_barrel + wine_rack + apple_press + tasting) + moradia em cima
- building_armazemporto (vila, industrial): armazem/trapiche com deck de
  madeira, caixas, barris e escritorio da doca; loot de pesca
- parque vinhedo: fileiras de parreira red/white grape em farmland com
  mouroes de tora (sem vinery:*_lattice, que nasce torta) + mesa de degustacao
- multi_porto (1x1): o armazem empacotado para scattered; aparece FORA das
  cidades em bioma de rio/praia (construcoes portuarias perto do rio)

Tambem cria os temas de loot 'cellar' e 'dock' (conditions + loot_tables,
no mesmo formato que convert.py gera a partir de loot.py).

Uso: python3 sunlit_tools/towns/cozy_expansion.py [--check-only]
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
import loot as L

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit', 'lostcities')
LTAB = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit', 'loot_tables', 'chests')
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
         'allowFillers': False, 'overrideFloors': True,
         'minfloors': n - 1, 'maxfloors': n - 1,
         'mincellars': cellars, 'maxcellars': cellars, 'parts': parts}
    with open(os.path.join(d, name.split('/')[-1] + '.json'), 'w') as f:
        json.dump(b, f)


LOOT = {
    'kitchen': 'sunlit:kitchen', 'bedroom': 'sunlit:bedroom',
    'home': 'sunlit:home', 'farm': 'sunlit:farm',
    'cellar': 'sunlit:cellar', 'dock': 'sunlit:dock', 'fridge': 'sunlit:fridge',
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


# ================================================================ 1. COZINHA KALEIDOSCOPE
def cozinha_kaleido():
    P = 'building_cozinhakaleido/cozinhakaleido'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'minecraft:dark_oak_planks', 'redeco:polished_birch_planks',
                     'createdeco:iron_window')
        PALETTES[p]['K'] = B('minecraft:bricks')
    K, H, FA, BR = LOOT['kitchen'], LOOT['home'], LOOT['farm'], LOOT['bedroom']

    # ---- terreo: cozinha kaleidoscope em L (NO) + mesa de jantar (O) | despensa (NE) + sala (L)
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fx.at(1, 1, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    for x in (2, 3):
        fx.at(x, 1, 'kaleidoscope_cookery:stove[facing={f},lit=false]', loot=K, wall='north')
        fx.at(x, 1, 'kaleidoscope_cookery:kitchenware_racks[facing={f},waterlogged=false]', y=3, wall='north')
    fx.at(2, 1, 'kaleidoscope_cookery:pot[facing=south,has_base=false,has_oil=false,show_oil=false,waterlogged=false]', y=2, loot=K)
    fx.at(3, 1, 'kaleidoscope_cookery:stockpot[facing=south,has_base=false,has_chains=false,has_lid=true,waterlogged=false]', y=2, loot=K)
    for x in (4, 5):
        fx.at(x, 1, 'refurbished_furniture:dark_oak_kitchen_cabinetry[facing={f},shape=default]', loot=K, wall='north')
    fx.at(4, 1, 'kaleidoscope_cookery:chopping_board[facing=south,waterlogged=false]', y=2)
    fx.at(5, 1, 'kaleidoscope_cookery:oil_pot[facing=south,has_oil=true,waterlogged=false]', y=2, loot=K)
    fx.at(6, 1, 'refurbished_furniture:dark_oak_kitchen_sink[facing={f}]', loot=K, wall='north')
    fx.at(1, 2, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='west')
    fx.at(1, 3, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='west')
    fx.at(1, 4, 'kaleidoscope_cookery:enamel_basin[has_lid=false,oil_count=0,waterlogged=false]', loot=K)
    fx.at(1, 5, 'minecraft:barrel[facing=up,open=false]', loot=K)
    # temperos pendurados no teto sobre a bancada
    fx.at(4, 2, 'kaleidoscope_cookery:chili_ristra[is_head=true,sheared=false]', y=3)
    fx.at(6, 2, 'kaleidoscope_cookery:strung_mushrooms[is_head=true,sheared=false]', y=3)
    fx.lantern(3, 3)
    # jantar: mesa de 2 com 6 cadeiras kaleidoscope
    dining(fx, 3, 8, 2, 'kaleidoscope_cookery:table_oak[axis=x,has_carpet=false,position=0,waterlogged=false]',
           'kaleidoscope_cookery:chair_oak[facing={f},has_carpet=false,waterlogged=false]', H)
    fx.lantern(3, 8)
    fx.lantern(4, 8)
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(2, 14, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(5, 14, 'furniture:wooden_planter[facing={f},type=none]', wall='south')
    # despensa NE
    fx.at(14, 1, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(13, 1, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    fx.at(13, 1, 'kaleidoscope_cookery:fruit_basket[facing=south,waterlogged=false]', y=2)
    fx.at(12, 1, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    # mescla: tabua do Farmer's Delight e saco de cebola do Let's Do na despensa kaleidoscope
    fx.at(12, 1, 'farmersdelight:cutting_board[facing=south]', y=2)
    fx.at(14, 2, 'farm_and_charm:potato_bag[facing={f}]', y=2, wall='east')
    fx.at(14, 2, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(14, 3, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.lantern(12, 3)
    # sala: sofa na parede leste, mesa de centro, duas cadeiras de frente
    for z in (7, 8):
        fx.at(14, z, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=H, wall='east')
        fx.chair(10, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'east')
    fx.at(12, 7, 'cfm:dark_oak_coffee_table[east=false,north=false,south=true,tall=false,west=false]')
    fx.at(12, 8, 'cfm:dark_oak_coffee_table[east=false,north=true,south=false,tall=false,west=false]')
    fx.carpet(11, 6, 13, 9, 'red')
    fx.lantern(12, 7)
    fx.run([(10, 14), (11, 14), (12, 14)], 'minecraft:bookshelf', 'south')
    fx.at(14, 14, 'minecraft:potted_fern')
    fx.sconce(1, 10, 'west')
    fx.sconce(14, 11, 'east')
    fx.sconce(4, 14, 'south')
    write_part('building_cozinhakaleido/cozinhakaleido_ground', PG, rows(g))

    # ---- andar: quarto do casal (O) | quarto das criancas (NE) | escritorio (SE)
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    fx.wall_x(6, 1, 14, gaps=(12,))
    fx.wall_z(6, 7, 14, gaps=(10,))
    bedroom_west(fx, 'brown', 'oak', BR)
    fx.carpet(2, 8, 4, 10, 'brown')
    fx.bed(9, 1, 'light_blue', 'north', BR)
    fx.bed(12, 1, 'pink', 'north', BR)
    fx.at(10, 1, 'refurbished_furniture:oak_drawer[facing={f},left=false,right=false,open=false]', loot=BR, wall='north')
    fx.at(10, 1, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.at(14, 1, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=BR)
    fx.at(14, 4, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=BR, wall='east')
    fx.at(7, 5, 'minecraft:potted_dandelion')
    fx.carpet(9, 3, 12, 4, 'yellow')
    fx.lantern(10, 3)
    fx.at(14, 8, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=H, wall='east')
    fx.at(14, 8, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(13, 8, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'east')
    fx.run([(14, 10), (14, 11)], 'minecraft:bookshelf', 'east')
    fx.run([(9, 14), (10, 14)], 'minecraft:bookshelf', 'south')
    fx.lantern(11, 10)
    fx.sconce(7, 9, 'west')
    write_part('building_cozinhakaleido/cozinhakaleido_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_cozinhakaleido/cozinhakaleido_top', PT, rows(r))
    write_building('building_cozinhakaleido',
                   [('ground', 'building_cozinhakaleido/cozinhakaleido_ground'),
                    ('floor', 'building_cozinhakaleido/cozinhakaleido_floor1'),
                    ('top', 'building_cozinhakaleido/cozinhakaleido_top')])


# ================================================================ 2. ADEGA VINERY
def adega_vinho():
    P = 'building_adegavinho/adegavinho'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'vinery:dark_cherry_planks', 'minecraft:stone_bricks',
                     'create:dark_oak_window_pane')
        PALETTES[p]['K'] = B('minecraft:bricks')
    CL, H, BR, K = LOOT['cellar'], LOOT['home'], LOOT['bedroom'], LOOT['kitchen']

    # ---- terreo: adega (O, separada por parede com arco) | salao de degustacao (L)
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fx.wall_x(6, 1, 14, gaps=(7, 8))
    # barricas de fermentacao na parede norte, barris nos cantos
    fx.at(1, 1, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for x in (2, 3, 4):
        fx.at(x, 1, 'vinery:fermentation_barrel[facing={f}]', loot=CL, wall='north')
    fx.at(5, 1, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    # adegas de garrafas na parede interna (sem janelas): rack medio embaixo, pequeno em cima
    for z in (2, 3, 4, 5, 10, 11, 12, 13):
        fx.at(5, z, 'vinery:dark_cherry_wine_rack_mid[facing={f},open=false]', loot=CL, wall='east')
        fx.at(5, z, 'vinery:dark_cherry_wine_rack_small[facing={f}]', y=2, wall='east')
    for z in (3, 4, 5):
        fx.at(1, z, 'vinery:storage_pot[facing={f},open=false]', loot=CL, wall='west')
    # prensa de maca no meio da adega, com bancada ao lado
    fx.at(2, 8, 'vinery:apple_press[facing=east,half=lower]', loot=CL)
    fx.at(2, 8, 'vinery:apple_press[facing=east,half=upper]', y=2)
    fx.at(1, 10, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='west')
    fx.at(1, 11, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='west')
    fx.at(1, 13, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for x in (1, 2, 3):
        fx.at(x, 14, 'vinery:wine_box[facing={f},open=false]', loot=CL, wall='south')
    fx.lantern(3, 4)
    fx.lantern(3, 11)
    # degustacao: bar na parede norte + 3 mesas
    for x in (9, 10, 11, 12, 13):
        fx.at(x, 1, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='north')
    for x in (10, 12):
        fx.at(x, 1, 'vinery:noir_wine[fake_model=false]', y=2)
    fx.at(14, 1, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for x, z in [(10, 5), (10, 10)]:
        fx.at(x, z, 'vinery:dark_cherry_table[facing=south,type=none]', loot=H)
        fx.chair(x - 1, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'east')
        fx.chair(x + 1, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'west')
        fx.lantern(x, z)
    fx.at(13, 8, 'vinery:dark_cherry_table[facing=south,type=none]', loot=H)
    fx.chair(13, 7, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'south')
    fx.chair(13, 9, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'north')
    fx.lantern(13, 8)
    fx.at(14, 14, 'minecraft:potted_azalea_bush')
    fx.at(9, 14, 'minecraft:potted_fern')
    fx.sconce(7, 4, 'west')
    fx.sconce(7, 11, 'west')
    fx.sconce(14, 11, 'east')
    write_part('building_adegavinho/adegavinho_ground', PG, rows(g))

    # ---- andar: quarto (O) | copa + sala (L)
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    fx.wall_x(6, 1, 14, gaps=(12,))
    bedroom_west(fx, 'brown', 'dark_oak', BR)
    fx.carpet(2, 8, 4, 10, 'red')
    fridge(fx, 14, 1, 'north', LOOT['fridge'])
    kitchen_line(fx, 'dark_oak', [(10, 'cab'), (11, 'sink'), (12, 'cab'), (13, 'stove')], K)
    dining(fx, 10, 5, 2, 'refurbished_furniture:dark_oak_table',
           'refurbished_furniture:dark_oak_chair[facing={f},tucked=false]', H)
    fx.lantern(10, 5)
    for x in (10, 11):
        fx.at(x, 14, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=H, wall='south')
    fx.at(10, 12, 'cfm:dark_oak_coffee_table[east=true,north=false,south=false,tall=false,west=false]')
    fx.at(11, 12, 'cfm:dark_oak_coffee_table[east=false,north=false,south=false,tall=false,west=true]')
    fx.carpet(9, 11, 12, 13, 'brown')
    fx.lantern(10, 11)
    fx.sconce(7, 8, 'west')
    write_part('building_adegavinho/adegavinho_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_adegavinho/adegavinho_top', PT, rows(r))
    write_building('building_adegavinho',
                   [('ground', 'building_adegavinho/adegavinho_ground'),
                    ('floor', 'building_adegavinho/adegavinho_floor1'),
                    ('top', 'building_adegavinho/adegavinho_top')])


# ================================================================ 3. ARMAZEM DO PORTO
def armazem_porto():
    P = 'building_armazemporto/armazemporto'
    PG, PF, PT = P + '_ground_palette', P + '_floor1_palette', P + '_top_palette'
    for p in (PG, PF, PT):
        base_palette(p, 'minecraft:oak_planks', 'minecraft:oak_planks',
                     'create:framed_glass_pane')
        PALETTES[p]['K'] = B('minecraft:bricks')
    DK, H, BR = LOOT['dock'], LOOT['home'], LOOT['bedroom']

    # ---- terreo: escritorio da doca fechado (NO) + galpao com estantes de carga em fileira
    g = shell_ground()
    ladder_shaft(g, layers=(1, 2, 3, 4, 5))
    fx = furnish(PG, g)
    fx.wall_x(5, 1, 5, gaps=(3,))
    fx.wall_z(5, 1, 4)
    fx.at(1, 1, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(2, 1, 'minecraft:cartography_table', loot=DK)
    fx.at(1, 3, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=DK, wall='west')
    fx.at(1, 3, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(2, 3, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'west')
    fx.at(4, 1, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=DK)
    fx.at(4, 4, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=DK, wall='south')
    fx.lantern(3, 2)
    # parede leste: carga encostada
    fx.at(14, 1, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    for z in (2, 3, 4, 8, 9, 10):
        fx.at(14, z, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    for z in (5, 6):
        fx.at(14, z, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    # duas fileiras de paletes no meio (corredores x=9 e x=12..13 livres)
    for z in range(4, 11):
        fx.at(10, z, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
        fx.at(11, z, 'minecraft:barrel[facing=up,open=false]' if z % 2 else 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    for z in (4, 6, 8):
        fx.at(10, z, 'refurbished_furniture:oak_crate[open=false]', y=2, loot=DK)
    # canto de pesca (SO): barris de peixe, tina de agua e caixa de redes
    fx.at(1, 14, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(2, 14, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(1, 13, 'minecraft:water_cauldron[level=3]')
    fx.at(1, 12, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    fx.at(4, 14, 'minecraft:smithing_table', loot=DK)
    fx.at(1, 8, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    fx.at(1, 9, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    fx.at(12, 14, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(14, 14, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    for x, z in [(7, 4), (10, 2), (12, 7), (4, 10), (10, 12)]:
        fx.lantern(x, z)
    write_part('building_armazemporto/armazemporto_ground', PG, rows(g))

    # ---- andar: alojamento dos estivadores (4 camas com bau) + mesa comum
    f = shell_floor()
    ladder_shaft(f, layers=(0, 1, 2))
    fx = furnish(PF, f, upper=True)
    for x, chest_x in [(2, 3), (4, None), (11, 12), (13, None)]:
        fx.bed(x, 1, 'brown', 'north', BR)
        if chest_x:
            fx.at(chest_x, 1, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=H)
    fx.at(1, 1, 'minecraft:barrel[facing=up,open=false]', loot=H)
    fx.at(14, 1, 'minecraft:barrel[facing=up,open=false]', loot=H)
    dining(fx, 7, 8, 2, 'refurbished_furniture:oak_table', 'refurbished_furniture:oak_chair[facing={f},tucked=false]', H)
    fx.lantern(7, 8)
    fx.lantern(8, 8)
    fx.at(1, 14, 'farmersdelight:stove[facing={f},lit=false]', loot=LOOT['kitchen'], wall='south')
    fx.at(1, 14, 'farmersdelight:cooking_pot[facing=north,support=none]', y=2)
    fx.at(2, 14, 'farmersdelight:oak_cabinet[facing={f},open=false]', loot=LOOT['kitchen'], wall='south')
    fx.at(3, 14, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(14, 8, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=DK)
    fx.at(14, 9, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=DK)
    fx.lantern(3, 3)
    fx.lantern(12, 3)
    fx.sconce(1, 8, 'west')
    fx.sconce(14, 11, 'east')
    write_part('building_armazemporto/armazemporto_floor1', PF, rows(f))

    r = shell_roof()
    write_part('building_armazemporto/armazemporto_top', PT, rows(r))
    write_building('building_armazemporto',
                   [('ground', 'building_armazemporto/armazemporto_ground'),
                    ('floor', 'building_armazemporto/armazemporto_floor1'),
                    ('top', 'building_armazemporto/armazemporto_top')])


# ================================================================ 4. PARQUE VINHEDO
def parque_vinhedo():
    s0, s1, s2 = grid(), grid(), grid()
    # cercado + caminhos em cruz
    for i in range(16):
        s0[0][i] = s0[15][i] = s0[i][0] = s0[i][15] = 'f'
    s0[7][0] = s0[8][0] = s0[7][15] = s0[8][15] = 'G'
    s0[0][7] = s0[0][8] = s0[15][7] = s0[15][8] = 'G'
    for i in range(1, 15):
        s0[7][i] = s0[8][i] = s0[i][7] = s0[i][8] = 'p'
    # 4 talhoes de parreira (farmland + mudas adultas)
    for (x0, x1, z0, z1, bush) in [(1, 5, 1, 5, 'R'), (10, 14, 1, 5, 'W'),
                                   (1, 5, 10, 14, 'W'), (10, 14, 10, 14, 'R')]:
        rect(s0, x0, z0, x1, z1, 'F')
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                if (x + z) % 2 == 0:
                    s1[z][x] = bush
        # fileira central do talhao: parreira cheia entre dois mouroes (a vinery:*_lattice so tem
        # o estado "" no blockstate e o resto vem do block entity: o Lost Cities a poe torta)
        for x in range(x0, x1 + 1):
            s1[(z0 + z1) // 2][x] = bush
        s1[(z0 + z1) // 2][x0] = s1[(z0 + z1) // 2][x1] = 'T'
        # olho d'agua no centro do talhao 5x5: hidrata toda a terra arada (alcance 4)
        cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
        s0[cz][cx] = 'w'
        s1[cz][cx] = ' '
    # faixa entre talhao e caminho era ar no chao (buraco de 1 bloco): vira grama
    for z in range(1, 15):
        for x in range(1, 15):
            if s0[z][x] == ' ':
                s0[z][x] = 'g'
    # cantina de degustacao no centro (cadeira kaleidoscope: facing aponta para a mesa)
    put(s1, 7, 7, 't')
    put(s1, 6, 7, 'e')
    put(s1, 8, 7, 'h')
    put(s1, 2, 2, 'b')
    put(s1, 13, 13, 'b')
    put(s1, 2, 13, 'b')
    put(s1, 13, 2, 'b')
    for x, z in [(0, 0), (15, 0), (0, 15), (15, 15)]:
        put(s1, x, z, 'o')
        put(s2, x, z, 'l')
    pal = {'f': 'minecraft:dark_oak_fence', 'G': 'minecraft:dark_oak_fence_gate[facing=north]',
           'p': 'minecraft:dirt_path', 'F': 'minecraft:farmland[moisture=7]', 'w': 'minecraft:water',
           'R': 'vinery:red_grape_bush[age=3]', 'W': 'vinery:white_grape_bush[age=3]',
           'T': 'minecraft:stripped_dark_oak_log[axis=y]', 'g': 'minecraft:grass_block[snowy=false]',
           't': 'vinery:dark_cherry_table[facing=south,type=none]',
           'e': 'kaleidoscope_cookery:chair_oak[facing=east,has_carpet=false,waterlogged=false]',
           'h': 'kaleidoscope_cookery:chair_oak[facing=west,has_carpet=false,waterlogged=false]',
           'b': 'vinery:dark_cherry_barrel[facing=up,open=false]',
           'o': 'minecraft:stripped_oak_log[axis=y]', 'l': 'minecraft:lantern'}
    for ch, st in pal.items():
        bid, props = M.parse(st)
        if not M.exists(bid):
            raise SystemExit(f'bloco inexistente em parque: {bid}')
    if CHECK_ONLY:
        return
    name, folder = 'vinhedo', 'parks'
    pj = {'name': name, 'xsize': 16, 'zsize': 16, 'refpalette': f'sunlit:{folder}/{name}_palette',
          'slices': [[''.join(r) for r in s] for s in (s0, s1, s2)]}
    pp = os.path.join(DATA, 'parts', folder, name + '.json')
    os.makedirs(os.path.dirname(pp), exist_ok=True)
    with open(pp, 'w') as f:
        json.dump(pj, f)
    entries = [{'char': ' ', 'block': 'minecraft:air'}]
    for ch, st in pal.items():
        bid, props = M.parse(st)
        entries.append({'char': ch, 'block': M.fmt(bid, M.clean_props(bid, props))})
    pp2 = os.path.join(DATA, 'palettes', folder, name + '_palette.json')
    os.makedirs(os.path.dirname(pp2), exist_ok=True)
    with open(pp2, 'w') as f:
        json.dump({'name': f'{folder}/{name}_palette', 'palette': entries}, f)


# ---------------------------------------------------------------- wiring
def wire():
    if CHECK_ONLY:
        return
    # pesos por bairro ficam todos no convert.py (SUNLIT_* / build_citystyle)
    # multibuilding 1x1 do porto (reusa o predio da cidade)
    mb = {'dimx': 1, 'dimz': 1,
          'buildings': [['sunlit:building_armazemporto/building_armazemporto']]}
    mp = os.path.join(DATA, 'multibuildings', 'multi_porto.json')
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    with open(mp, 'w') as f:
        json.dump(mb, f)
    # referência scattered (validate.py exige o arquivo; y0 do predio = fundacao
    # no nivel do terreno, por isso heightoffset 0 e nao -7 como nos DC)
    sp = os.path.join(DATA, 'scattered', 'multi_porto.json')
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    with open(sp, 'w') as f:
        json.dump({'multibuilding': 'sunlit:multi_porto', 'terrainheight': 'highest',
                   'terrainfix': 'none', 'heightoffset': 0}, f)
    # scattered: porto fora das cidades, so em rio/praia
    ws = os.path.join(DATA, 'worldstyles', 'towns.json')
    w = json.load(open(ws))
    lst = w['scattered']['list']
    entry = {'name': 'sunlit:multi_porto', 'weight': 14, 'maxheightdiff': 3,
             'biomes': {'if_any': ['#minecraft:is_river', '#minecraft:is_beach']}}
    if not any(x['name'] == 'sunlit:multi_porto' for x in lst):
        lst.append(entry)
    with open(ws, 'w') as f:
        json.dump(w, f)
    # loot novo (mesmo formato do convert.py)
    for t in ('cellar', 'dock'):
        with open(os.path.join(DATA, 'conditions', t + '.json'), 'w') as f:
            json.dump({'values': [{'factor': 1, 'value': f'sunlit:chests/{t}'}]}, f)
        with open(os.path.join(LTAB, t + '.json'), 'w') as f:
            json.dump(L.loot_table(t), f)


def main():
    cond = set()
    for f in os.listdir(os.path.join(DATA, 'conditions')):
        if f.endswith('.json'):
            cond.add('sunlit:' + f[:-5])
    for v in list(LOOT.values()) + ['sunlit:cellar', 'sunlit:dock']:
        if v not in cond and v not in ('sunlit:cellar', 'sunlit:dock'):
            raise SystemExit(f'condicao ausente: {v}')
    cozinha_kaleido()
    adega_vinho()
    armazem_porto()
    parque_vinhedo()
    wire()
    print('expansao gerada OK (check-only)' if CHECK_ONLY else 'expansao gravada + citystyles/scattered/loot atualizados')


main()
