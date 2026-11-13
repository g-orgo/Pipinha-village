"""Remodelacao das construcoes proprias de antes dos schematics (2026-10-03).

Depositos (4), oficina Create, casa de fazenda, padaria, casa da cozinha kaleidoscope, adega e
armazem do porto ganham a casca de galpao.py (paredes recuadas, enxaimel, beiral, alpendre,
quintal) e interior redesenhado para o vao de 12x12 (x2..13, z2..13). Grava as MESMAS partes,
paletas e predios que houses.py / cozy_expansion.py / vila.py gravavam (por cima), entao os
pesos do convert.py continuam valendo.

Uso: python3 remodel.py   (depois de vila.py, antes de schematics.py/finalize.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import houses as H
import galpao as GP
import interior as I

LOOT = {**H.LOOT, 'cellar': 'sunlit:cellar', 'dock': 'sunlit:dock', 'deposito': 'sunlit:deposito'}
WOOD = {'pedra': 'dark_oak', 'andesito': 'spruce', 'ardosia': 'dark_oak', 'tijolo': 'spruce'}


# ---------------------------------------------------------------- montagem
class Build:
    """um predio: casca + partes; floors = ['ground'] ou ['ground', 'floor1']"""

    def __init__(self, name, style, floors, chimney=None, yard='casa', prefix=None):
        self.name = name
        self.P = prefix or f'building_{name}/{name}'
        self.floors = floors
        self.parts = [f'{self.P}_{f}_palette' for f in floors] + [f'{self.P}_top_palette']
        for p in self.parts:
            H.PALETTES.pop(p, None)
        self.shell = GP.Shell(self.parts, style, chimney=chimney, yard=yard)
        self.two = len(floors) > 1
        self.slices = {}
        self.top = self.shell.roof()

    def level(self, f):
        if f == 'ground':
            sl = self.shell.ground(ladder=self.two)
        else:
            sl = self.shell.floor(ladder=True)
        if f == self.floors[-1]:
            self.shell.eave(sl)
            self.shell.gable_corbel(sl)
        self.slices[f] = sl
        # a chamine e maciça de tijolos (galpao.py): a celula dela nao e livre para mobilia
        return GP.furnish(f'{self.P}_{f}_palette', sl, ladder=self.two, ground=f == 'ground')

    def attic(self, free=()):
        """sotao dentro do telhado (parte top): y0 = piso (o forro do ultimo andar), y1 ainda em pe
        em z3..12; z2 e z13 so tem 1 bloco de altura"""
        return I.Furnish(H.PALETTES, H.pal, f'{self.P}_top_palette', self.top, free=set(free))

    def write(self):
        floors = []
        for f in self.floors:
            H.write_part(f'{self.P}_{f}', f'{self.P}_{f}_palette', H.rows(self.slices[f]))
            floors.append(('ground' if f == 'ground' else 'floor', f'{self.P}_{f}'))
        H.write_part(f'{self.P}_top', f'{self.P}_top_palette', H.rows(self.top))
        floors.append(('top', f'{self.P}_top'))
        H.write_building(f'building_{self.name}', floors)


# ---------------------------------------------------------------- pecas
def fridge(fx, x, z, wall, loot=LOOT['fridge']):
    fx.at(x, z, 'refurbished_furniture:light_freezer[facing={f},open=false]', loot=loot, wall=wall)
    fx.at(x, z, 'refurbished_furniture:light_fridge[facing={f},open=false]', y=2, loot=loot, wall=wall)


def kitchen_run(fx, wood, cells, wall, loot=LOOT['kitchen']):
    """cells = [(x, z, tipo)] encostados na parede `wall`; tipo em stove/sink/cab/drawer/fd"""
    kinds = {
        'stove': 'farmersdelight:stove[facing={f},lit=false]',
        'sink': f'refurbished_furniture:{wood}_kitchen_sink[facing={{f}}]',
        'cab': f'refurbished_furniture:{wood}_kitchen_cabinetry[facing={{f}},shape=default]',
        'drawer': f'refurbished_furniture:{wood}_kitchen_drawer[facing={{f}},open=false]',
        'fd': f'farmersdelight:{wood}_cabinet[facing={{f}},open=false]',
    }
    for x, z, k in cells:
        fx.at(x, z, kinds[k], loot=None if k == 'stove' else loot, wall=wall)


def dining(fx, x0, z, n, table, chair, loot=None, ends=True):
    for i in range(n):
        x = x0 + i
        t = f'{table}[east={str(i < n - 1).lower()},north=false,south=false,west={str(i > 0).lower()}]' \
            if table.startswith('refurbished_furniture:') else table
        fx.at(x, z, t, loot=loot)
        fx.chair(x, z - 1, chair, 'south')
        fx.chair(x, z + 1, chair, 'north')
    if ends:
        fx.chair(x0 - 1, z, chair, 'east')
        fx.chair(x0 + n, z, chair, 'west')


def bedroom_west(fx, color, wood, loot=LOOT['bedroom'], double=True):
    """quarto no oeste (x2..5, parede interna em x6): cama na parede norte entre criados-mudos,
    bau no pe, guarda-roupa e estante nas paredes sem janela"""
    fx.bed(3, 2, color, 'north', loot)
    if double:
        fx.bed(4, 2, color, 'north', loot)
    for x in (2, 5 if double else 4):
        fx.at(x, 2, f'refurbished_furniture:{wood}_drawer[facing={{f}},left=false,right=false,open=false]', loot=loot, wall='north')
        fx.at(x, 2, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.at(3, 4, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=loot)
    fx.at(2, 5, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=left,open=false]', loot=loot, wall='west')
    fx.at(2, 6, f'refurbished_furniture:{wood}_storage_cabinet[facing={{f}},hinge=right,open=false]', loot=loot, wall='west')
    fx.run([(2, 10), (2, 11)], 'minecraft:bookshelf', 'west')
    fx.at(4, 13, f'another_furniture:{wood}_shelf[facing={{f}},horizontal=single]', y=2, wall='south')
    fx.at(4, 13, 'minecraft:potted_azalea_bush', y=3)
    fx.at(5, 13, 'minecraft:potted_fern')
    fx.lantern(4, 6)
    fx.lantern(4, 11)


def inner(fx, block='minecraft:spruce_planks'):
    """char de parede interna (movel pode encostar nela)"""
    c = fx.char(block)
    I.SUPPORT.add(c)
    return c


def wall_x6(fx, gap=8):
    """parede interna norte-sul em x6 (vao de passagem em z=gap)"""
    fx.wall_x(6, 2, 13, gaps=(gap,), char=inner(fx))


# ================================================================ depositos
def deposito(name, mat):
    w = WOOD[mat]
    b = Build(name, mat, ['ground'], yard='deposito')
    fx = b.level('ground')
    D = LOOT['deposito']
    loot_cycle = ['minecraft:barrel[facing=up,open=false]', f'refurbished_furniture:{w}_crate[open=false]',
                  'minecraft:chest[facing=south,type=single,waterlogged=false]']
    full = [f'redeco:{w}_crate[facing=south,propped=false]', f'embellishcraft:{w}_wooden_crate', 'create:cardboard_block[axis=x]',
            'hearthandharvest:apple_crate', 'crabbersdelight:cod_barrel', 'create:andesite_casing']
    soft = ['supplementaries:sack', 'farm_and_charm:flour_bag[facing=south]', 'farmersdelight:rice_bag']
    i = 0
    # estantes de caixotes em 2 blocos duplos de cada lado do corredor central (x7-8)
    for z0 in (5, 9):
        for x0, x1 in ((4, 6), (9, 11)):
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
    # escritorio do encarregado (NO): mesa, maquina de escrever, cadeira e armario
    fx.at(4, 2, f'refurbished_furniture:{w}_desk[facing={{f}},left=false,right=false]', loot=D, wall='north')
    fx.at(4, 2, 'candlelight:typewriter_iron[facing=south,full=1]', y=2)
    fx.chair(4, 3, f'refurbished_furniture:{w}_chair[facing={{f}},tucked=false]', 'north')
    fx.at(5, 2, 'cluttered:general_store_cabinet[facing={f},part=1]', wall='north')
    fx.at(2, 2, 'minecraft:barrel[facing=up,open=false]', loot=D)
    # cofre/estoque bom (NE)
    fx.at(10, 2, f'refurbished_furniture:{w}_crate[open=false]', loot=D)
    fx.at(11, 2, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=D)
    fx.at(13, 2, 'create:item_vault[axis=x,large=false]')
    # paredes laterais: barris e caixotes, prateleira de item no alto (a leste so ate z6: dali a escada)
    for z in (4, 5, 6, 9, 10, 11):
        fx.at(2, z, 'minecraft:barrel[facing=up,open=false]' if z % 2 else f'redeco:{w}_crate[facing=south,propped=false]',
              loot=D if z % 2 else None)
    for z in (4, 5, 6):
        fx.at(13, z, f'refurbished_furniture:{w}_crate[open=false]' if z % 2 else 'minecraft:barrel[facing=up,open=false]', loot=D)
    for z in (5, 10):
        fx.at(2, z, 'supplementaries:item_shelf[facing={f}]', y=3, wall='west')
    fx.at(13, 5, 'supplementaries:item_shelf[facing={f}]', y=3, wall='east')
    # fundos: carga e sacos ((13, 13) fica livre: pe da escada)
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=D)
    fx.at(3, 13, 'supplementaries:sack')
    fx.at(12, 13, f'refurbished_furniture:{w}_crate[open=false]', loot=D)
    for x, z in ((7, 4), (8, 8), (7, 11), (4, 8), (11, 8)):
        fx.lantern(x, z)
    attic_stairs(b, fx, w, D)
    b.write()


def attic_stairs(b, fx, w, D):
    """escada de madeira na parede leste (x13) subindo de z12 (y1) a z8 (y5) ate o sotao: teto e
    forro abertos sobre ela, escada invertida por baixo (forro inclinado), estoque no vao de baixo
    e guarda-corpo em volta da abertura no piso do sotao"""
    sl = b.slices['ground']
    X = 13
    step = fx.char(f'minecraft:{w}_stairs[facing=north,half=bottom,shape=straight]')
    under = fx.char(f'minecraft:{w}_stairs[facing=south,half=top,shape=straight]')
    for i, z in enumerate(range(12, 7, -1)):
        y = 1 + i
        sl[y][z][X] = step
        if y > 1:
            sl[y - 1][z][X] = under
        for yy in (y + 1, y + 2):
            if yy <= 5:
                sl[yy][z][X] = ' '
    fx.at(X, 10, 'minecraft:barrel[facing=up,open=false]', loot=D)
    fx.at(X, 9, f'refurbished_furniture:{w}_crate[open=false]', loot=D)
    fx.at(X, 9, 'supplementaries:sack', y=2)
    fx.at(X, 8, 'minecraft:barrel[facing=up,open=false]', loot=D)
    # sotao: abertura em x13 z9..10 (o degrau de cima e z8), saida para z7
    at = b.attic(free={(X, 7), (X, 6)})
    def fence(**c):  # o registro so conhece os lados =true (multipart); o resto fica no padrao false
        return f'minecraft:{w}_fence[' + ','.join(f'{d}=true' for d in sorted(c)) + ']'
    for z in (8, 9, 10):
        at.at(12, z, fence(north=True, south=True), y=0)
    at.at(12, 11, fence(north=True, east=True), y=0)
    at.at(X, 11, fence(west=True), y=0)
    # descanso do encarregado no oitao oeste: catre, bau no pe, estante e tapete
    at.at(2, 8, 'minecraft:brown_bed[part=head,facing=west,occupied=false]', y=0)
    at.at(3, 8, 'minecraft:brown_bed[part=foot,facing=west,occupied=false]', y=0)
    at.at(4, 8, 'minecraft:chest[facing=west,type=single,waterlogged=false]', y=0, loot=D)
    at.at(2, 7, f'refurbished_furniture:{w}_drawer[facing=west,left=false,right=false,open=false]', y=0, loot=D)
    at.at(2, 7, 'minecraft:candle[candles=3,lit=true]', y=1)
    for z in (5, 10):
        at.at(2, z, 'minecraft:bookshelf', y=0)
    for z in range(6, 10):
        for x in range(5, 9):
            at.at(x, z, 'minecraft:brown_carpet', y=0)
    # estoque nas aguas do telhado: caixotes em z3/z12 (2 de altura), sacos em z2/z13 (1 de altura)
    stock = ['minecraft:barrel[facing=up,open=false]', f'refurbished_furniture:{w}_crate[open=false]',
             'minecraft:chest[facing=south,type=single,waterlogged=false]']
    full = [f'redeco:{w}_crate[facing=south,propped=false]', 'create:cardboard_block[axis=x]', 'hearthandharvest:apple_crate']
    for i, x in enumerate(range(3, 12)):
        at.at(x, 3, stock[i % 3], y=0, loot=D)
        if i % 2 == 0 and 'chest' not in stock[i % 3]:
            at.at(x, 3, full[i % 3], y=1)
        if i % 3 != 1:
            at.at(x, 2, ['supplementaries:sack', 'farm_and_charm:flour_bag[facing=south]', 'farmersdelight:rice_bag'][i % 3], y=0)
    for i, x in enumerate(range(2, 11)):
        at.at(x, 12, stock[(i + 1) % 3].replace('south', 'north'), y=0, loot=D)
        if i % 3 == 0:
            at.at(x, 12, full[(i + 1) % 3], y=1)
        if i % 2:
            at.at(x, 13, 'supplementaries:sack', y=0)
    # lanternas penduradas na cumeeira (corrente ate a escada do telhado em y6)
    for x, z in ((4, 7), (9, 8)):
        at.at(x, z, 'minecraft:lantern[hanging=true]', y=2)
        for y in (3, 4, 5):
            at.at(x, z, 'minecraft:chain[axis=y]', y=y)


# ================================================================ oficina Create
def oficina():
    b = Build('oficinacreate', 'oficina', ['ground', 'floor1'], chimney=(2, 12), yard='oficina')
    WS, HM, K, BR = LOOT['workshop'], LOOT['home'], LOOT['kitchen'], LOOT['bedroom']
    fx = b.level('ground')
    # bancada de ferramentas (parede norte, oeste)
    fx.at(2, 2, 'minecraft:smithing_table', loot=WS)
    fx.at(3, 2, 'refurbished_furniture:workbench[facing={f},powered=false]', loot=WS, wall='north')
    fx.at(4, 2, 'minecraft:anvil[facing=east]', loot=WS)
    fx.at(5, 2, 'create:andesite_casing', loot=WS)
    fx.at(5, 2, 'create:brown_toolbox[facing=south,waterlogged=false]', y=2)
    fx.at(6, 2, 'minecraft:grindstone[face=floor,facing=north]', loot=WS)
    fx.at(5, 2, 'create:cuckoo_clock[facing={f}]', y=3, wall='north')
    # estacao de mistura e prensa (parede norte, leste): maquina no teto, vao de 1 bloco
    fx.at(10, 2, 'create:basin[facing=down]', loot=WS)
    fx.at(10, 2, 'create:mechanical_mixer', y=3)
    fx.at(12, 2, 'create:cogwheel[axis=y]', y=3)
    fx.at(11, 2, 'create:depot', loot=WS)
    fx.at(11, 2, 'create:mechanical_press[facing=north]', y=3)
    fx.at(13, 2, 'create:fluid_tank[bottom=true,shape=window,top=false]', loot=WS)
    fx.at(13, 2, 'create:fluid_tank[bottom=false,shape=window,top=true]', y=2)
    # forja: coluna da chamine maciça de tijolos (sem fogueira dentro; a fogueira fica no topo) + alto-forno ao lado
    fx.at(2, 12, 'minecraft:bricks', loot=None)
    fx.at(2, 11, 'minecraft:blast_furnace[facing={f},lit=false]', loot=WS, wall='west')
    # queimadores com blaze ao lado da forja + bancada de deployer/crafter (parede norte)
    fx.at(3, 11, 'create:blaze_burner[blaze=smouldering,facing=east]', loot=None)
    fx.at(3, 12, 'create:blaze_burner[blaze=smouldering,facing=east]', loot=None)
    fx.at(9, 2, 'create:deployer[facing={f}]', loot=WS, wall='north')
    fx.at(6, 13, 'create:mechanical_crafter[facing={f},pointing=up]', loot=WS, wall='south')
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    for z in (4, 5, 6):
        fx.at(2, z, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    fx.at(2, 9, 'create:schematic_table[facing=east]', loot=WS)
    # ilha central de montagem (o meio nao fica mais vazio): crafters, eixo descendo do teto
    # com caixa de engrenagem, mo e deposito; bancada de casing com caixa de ferramentas
    for x, z in ((4, 6), (5, 6), (4, 7), (5, 7)):
        fx.at(x, z, 'create:mechanical_crafter[facing=south,pointing=down]', loot=None)
    fx.at(4, 8, 'create:andesite_casing', loot=WS)
    fx.at(5, 8, 'create:andesite_casing', loot=WS)
    fx.at(4, 8, 'create:clipboard[face=floor,facing=south,waterlogged=false,written=true]', y=2)
    fx.at(5, 8, 'create:brown_toolbox[facing=south,waterlogged=false]', y=2)
    fx.at(10, 7, 'create:gearbox[axis=y]', loot=None)
    fx.at(10, 7, 'create:shaft[axis=y]', y=2)
    fx.at(10, 7, 'create:shaft[axis=y]', y=3)
    fx.at(11, 7, 'create:millstone', loot=None)
    fx.at(10, 6, 'create:cogwheel[axis=y]')
    fx.at(10, 8, 'create:depot', loot=WS)
    fx.at(11, 8, 'create:brass_casing', loot=WS)
    fx.at(11, 8, 'create:large_cogwheel[axis=y]', y=2)
    fx.at(11, 6, 'create:item_vault[axis=z,large=false]')
    # estoque leste e sul
    for z in (4, 5, 6):
        fx.at(13, z, 'minecraft:barrel[facing=up,open=false]' if z != 5 else 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(13, 9, 'create:encased_fan[facing=west]')
    fx.at(13, 10, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(13, 11, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    fx.at(10, 13, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(11, 13, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(4, 13, 'refurbished_furniture:oak_crate[open=false]', loot=WS)
    fx.at(5, 13, 'minecraft:barrel[facing=up,open=false]', loot=WS)
    # 3 lanternas de teto ao longo do meio (a oficina e comprida e cheia de
    # maquinas altas: mais que isso virava lustre)
    for x, z in ((3, 7), (8, 7), (12, 7)):
        fx.lantern(x, z)
    # andar: quarto (O) | copa, escrivaninha e sala (L)
    fx = b.level('floor1')
    wall_x6(fx)
    bedroom_west(fx, 'red', 'spruce', BR, double=False)
    fx.carpet(3, 8, 5, 10, 'gray')
    fridge(fx, 11, 2, 'north')
    kitchen_run(fx, 'spruce', [(8, 2, 'fd'), (9, 2, 'sink'), (10, 2, 'stove'), (12, 2, 'cab'), (7, 2, 'drawer')], 'north')
    dining(fx, 9, 5, 2, 'refurbished_furniture:spruce_table', 'refurbished_furniture:spruce_chair[facing={f},tucked=false]', HM)
    fx.at(13, 9, 'refurbished_furniture:spruce_desk[facing={f},left=false,right=false]', loot=WS, wall='east')
    fx.at(13, 9, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(12, 9, 'refurbished_furniture:spruce_chair[facing={f},tucked=false]', 'east')
    fx.run([(13, 10), (13, 11)], 'minecraft:bookshelf', 'east')
    for x in (9, 10):
        fx.at(x, 13, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=HM, wall='south')
    fx.carpet(8, 10, 11, 12, 'gray')
    fx.lantern(9, 4)
    fx.lantern(10, 10)
    b.write()


# ================================================================ casa de fazenda
def casa_fazenda():
    b = Build('casafazenda', 'fazenda', ['ground', 'floor1'], chimney=(13, 2), yard='casa')
    K, HM, FA, BR = LOOT['kitchen'], LOOT['home'], LOOT['farm'], LOOT['bedroom']
    fx = b.level('ground')
    # cozinha caipira em L (NO) com fogao a lenha sob a chamine fica na sala (NE)
    fridge(fx, 4, 2, 'north')
    kitchen_run(fx, 'spruce', [(2, 2, 'cab'), (3, 2, 'drawer'), (5, 2, 'stove'), (6, 2, 'sink')], 'north')
    kitchen_run(fx, 'spruce', [(2, 3, 'cab'), (2, 4, 'fd'), (2, 5, 'drawer')], 'west')
    fx.at(5, 2, 'farmersdelight:skillet[facing=south,support=true]', y=2)
    fx.at(2, 4, 'kaleidoscope_cookery:fruit_basket[facing=east,waterlogged=false]', y=2)
    fx.at(2, 3, 'farm_and_charm:potato_bag[facing={f}]', y=2, wall='west')
    fx.lantern(4, 4)
    dining(fx, 4, 8, 2, 'refurbished_furniture:oak_table', 'refurbished_furniture:oak_chair[facing={f},tucked=false]', HM)
    fx.lantern(4, 8)
    # despensa (SO)
    fx.at(2, 11, 'refurbished_furniture:oak_storage_jar[facing={f}]', loot=FA, wall='west')
    fx.at(2, 12, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(3, 13, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(4, 13, 'farmersdelight:oak_cabinet[facing={f},open=false]', loot=FA, wall='south')
    # sala (L): canto da chamine maciça de tijolos (sem fogueira dentro; a fogueira fica no topo), sofa, poltronas e estante
    fx.at(13, 2, 'minecraft:bricks')
    fx.at(12, 2, 'minecraft:bricks')
    fx.at(13, 3, 'minecraft:bricks')
    for z in (6, 7):
        fx.at(13, z, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=HM, wall='east')
    fx.at(11, 6, 'refurbished_furniture:oak_table[east=false,north=false,south=true,west=false]')
    fx.at(11, 7, 'refurbished_furniture:oak_table[east=false,north=true,south=false,west=false]')
    for z in (6, 7):
        fx.chair(9, z, 'another_furniture:oak_chair[facing={f},tucked=false,variant=1]', 'east')
    fx.carpet(10, 5, 12, 8, 'brown')
    fx.lantern(11, 6)
    fx.run([(9, 2), (10, 2)], 'minecraft:bookshelf', 'north')
    fx.at(13, 10, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=HM, wall='east')
    fx.at(13, 11, 'refurbished_furniture:oak_drawer[facing={f},left=false,right=false,open=false]', loot=HM, wall='east')
    fx.at(13, 11, 'minecraft:potted_fern', y=2)
    fx.at(10, 13, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(11, 13, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    # andar: quarto (O) | banheiro (NE) | escritorio (SE)
    fx = b.level('floor1')
    wall_x6(fx)
    fx.wall_z(6, 7, 13, gaps=(10,), char=inner(fx))
    bedroom_west(fx, 'brown', 'oak', BR)
    fx.carpet(3, 8, 5, 10, 'white')
    fx.at(9, 2, 'refurbished_furniture:white_toilet[facing={f}]', loot=LOOT['bathroom'], wall='north')
    fx.at(11, 2, 'refurbished_furniture:white_basin[facing={f}]', loot=LOOT['bathroom'], wall='north')
    fx.at(12, 5, 'refurbished_furniture:white_bath[facing=east,type=head]', loot=LOOT['bathroom'])
    fx.at(11, 5, 'refurbished_furniture:white_bath[facing=east,type=bottom]', loot=LOOT['bathroom'])
    fx.at(7, 5, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=LOOT['bathroom'], wall='south')
    fx.lantern(10, 3)
    fx.at(13, 9, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=HM, wall='east')
    fx.at(13, 9, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(12, 9, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'east')
    fx.run([(13, 10), (13, 11)], 'minecraft:bookshelf', 'east')
    for x in (9, 10):
        fx.at(x, 13, 'refurbished_furniture:green_sofa[facing={f},shape=default]', loot=HM, wall='south')
    fx.carpet(8, 10, 11, 12, 'green')
    fx.lantern(10, 9)
    b.write()


# ================================================================ padaria
# NOTE (2026-10-09): sem chamine. O duto aberto atravessava o andar de cima e deixava um
# buraco no piso (em cima do stove do terreo); como aqui nao ha fogueira (so stoves, que nao
# soltam fumaca), o buraco foi fechado com o resto do chao (chimney=None).
def padaria():
    b = Build('padariacomfy', 'tijolo', ['ground', 'floor1'], chimney=None, yard='casa')
    BK, CF, K, HM, BR = LOOT['bakery'], LOOT['cafe'], LOOT['kitchen'], LOOT['home'], LOOT['bedroom']
    fx = b.level('ground')
    # producao (O) atras do balcao em x6: forno de tijolo sob a chamine, fogoes e mesas do padeiro
    fx.at(2, 2, 'bakery:cabinet[facing={f},open=false]', loot=BK, wall='north')
    fx.at(2, 12, 'farmersdelight:stove[facing={f},lit=false]', wall='west')
    fx.at(3, 2, 'farmersdelight:stove[facing={f},lit=false]', wall='north')
    fx.at(3, 2, 'farmersdelight:cooking_pot[facing=south,support=tray]', y=2)
    fx.at(4, 2, 'bakery:baker_station[facing={f}]', loot=BK, wall='north')
    fx.at(5, 2, 'bakery:baker_station[facing={f}]', loot=BK, wall='north')
    for z in (4, 5):
        fx.at(2, z, 'bakery:bread_crate[bites=0,facing={f}]', loot=BK, wall='west')
    fx.at(2, 6, 'bakery:cabinet[facing={f},open=false]', loot=BK, wall='west')
    fx.at(2, 9, 'bakery:drawer[facing={f},open=false]', loot=BK, wall='west')
    fx.at(2, 10, 'bakery:cabinet[facing={f},open=false]', loot=BK, wall='west')
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=BK)
    fx.at(3, 13, 'minecraft:barrel[facing=up,open=false]', loot=BK)
    fx.at(4, 13, 'bakery:breadbox[facing={f}]', loot=BK, wall='south')
    for z in range(4, 11):
        fx.at(6, z, 'bakery:brick_counter[facing=east,type=none]', loot=BK)
    fx.at(6, 5, 'bakery:cake_display[facing=east,type=none]', y=2)
    fx.at(6, 7, 'bakery:cupcake_display[facing=east]', y=2)
    fx.at(6, 9, 'cozycafe:cafe_menu[facing=east,dish=false,dirty=false]', y=2)
    fx.lantern(4, 5)
    fx.lantern(4, 10)
    # cafe (L): tres mesinhas
    for x, z in ((10, 4), (10, 10), (12, 7)):
        fx.at(x, z, 'another_furniture:spruce_table[facing=north,leg_1=true,leg_2=true,leg_3=true,leg_4=true]', loot=CF)
        fx.chair(x, z - 1, 'another_furniture:spruce_chair[facing={f},tucked=false,variant=1]', 'south')
        fx.chair(x, z + 1, 'another_furniture:spruce_chair[facing={f},tucked=false,variant=1]', 'north')
        fx.lantern(x, z)
    fx.at(13, 2, 'minecraft:potted_azalea_bush')
    fx.at(13, 4, 'furniture:wooden_planter[facing={f},type=none]', wall='east')
    fx.at(13, 11, 'furniture:wooden_planter[facing={f},type=none]', wall='east')
    fx.at(10, 13, 'minecraft:potted_fern')
    # andar: quarto (O) | copa + sala (L)
    fx = b.level('floor1')
    wall_x6(fx)
    bedroom_west(fx, 'white', 'birch', BR)
    fx.carpet(3, 8, 5, 10, 'light_blue')
    fridge(fx, 11, 2, 'north')
    kitchen_run(fx, 'birch', [(8, 2, 'cab'), (9, 2, 'sink'), (10, 2, 'stove'), (12, 2, 'drawer'), (13, 2, 'cab')], 'north')
    dining(fx, 9, 6, 2, 'refurbished_furniture:birch_table', 'refurbished_furniture:birch_chair[facing={f},tucked=false]', HM)
    for x in (9, 10):
        fx.at(x, 13, 'refurbished_furniture:white_sofa[facing={f},shape=default]', loot=HM, wall='south')
    fx.at(9, 11, 'refurbished_furniture:birch_table[east=true,north=false,south=false,west=false]')
    fx.at(10, 11, 'refurbished_furniture:birch_table[east=false,north=false,south=false,west=true]')
    fx.carpet(8, 10, 11, 12, 'light_gray')
    fx.lantern(9, 5)
    fx.lantern(10, 10)
    fx.at(13, 9, 'refurbished_furniture:birch_storage_cabinet[facing={f},hinge=left,open=false]', loot=HM, wall='east')
    b.write()


# ================================================================ casa da cozinha kaleidoscope
# NOTE (2026-10-09): idem padaria (stoves sem fogueira): sem duto, piso do andar fechado.
def cozinha_kaleido():
    b = Build('cozinhakaleido', 'pedra', ['ground', 'floor1'], chimney=None, yard='casa')
    K, HM, FA, BR = LOOT['kitchen'], LOOT['home'], LOOT['farm'], LOOT['bedroom']
    fx = b.level('ground')
    # cozinha kaleidoscope (NO): fogoes sob a chamine, panelas, tabua, tacho de oleo e pia
    fx.at(2, 2, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    for x in (4, 5):
        fx.at(x, 2, 'kaleidoscope_cookery:stove[facing={f},lit=false]', loot=K, wall='north')
        fx.at(x, 2, 'kaleidoscope_cookery:kitchenware_racks[facing={f},waterlogged=false]', y=3, wall='north')
    fx.at(4, 2, 'kaleidoscope_cookery:pot[facing=south,has_base=false,has_oil=false,show_oil=false,waterlogged=false]', y=2, loot=K)
    fx.at(5, 2, 'kaleidoscope_cookery:stockpot[facing=south,has_base=false,has_chains=false,has_lid=true,waterlogged=false]', y=2, loot=K)
    fx.at(3, 2, 'refurbished_furniture:dark_oak_kitchen_cabinetry[facing={f},shape=default]', loot=K, wall='north')
    fx.at(3, 2, 'kaleidoscope_cookery:chopping_board[facing=south,waterlogged=false]', y=2)
    fx.at(2, 3, 'refurbished_furniture:dark_oak_kitchen_sink[facing={f}]', loot=K, wall='west')
    fx.at(2, 4, 'refurbished_furniture:dark_oak_kitchen_cabinetry[facing={f},shape=default]', loot=K, wall='west')
    fx.at(2, 4, 'kaleidoscope_cookery:oil_pot[facing=east,has_oil=true,waterlogged=false]', y=2, loot=K)
    fx.at(2, 5, 'kaleidoscope_cookery:enamel_basin[has_lid=false,oil_count=0,waterlogged=false]', loot=K)
    fx.at(2, 6, 'minecraft:barrel[facing=up,open=false]', loot=K)
    fx.at(4, 3, 'kaleidoscope_cookery:chili_ristra[is_head=true,sheared=false]', y=3)
    fx.at(6, 3, 'kaleidoscope_cookery:strung_mushrooms[is_head=true,sheared=false]', y=3)
    # jantar: mesa kaleidoscope com 6 cadeiras
    dining(fx, 4, 9, 2, 'kaleidoscope_cookery:table_oak[axis=x,has_carpet=false,position=0,waterlogged=false]',
           'kaleidoscope_cookery:chair_oak[facing={f},has_carpet=false,waterlogged=false]', HM)
    fx.lantern(4, 9)
    fx.lantern(5, 9)
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(3, 13, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    # despensa (NE) e sala (L)
    fx.at(13, 2, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    fx.at(11, 2, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    fx.at(11, 2, 'kaleidoscope_cookery:fruit_basket[facing=south,waterlogged=false]', y=2)
    fx.at(10, 2, 'farmersdelight:dark_oak_cabinet[facing={f},open=false]', loot=K, wall='north')
    fx.at(10, 2, 'farmersdelight:cutting_board[facing=south]', y=2)
    fx.at(13, 4, 'refurbished_furniture:oak_crate[open=false]', loot=FA)
    fx.at(13, 4, 'farm_and_charm:potato_bag[facing={f}]', y=2, wall='east')
    fx.at(13, 5, 'minecraft:barrel[facing=up,open=false]', loot=FA)
    for z in (9, 10):
        fx.at(13, z, 'refurbished_furniture:red_sofa[facing={f},shape=default]', loot=HM, wall='east')
        fx.chair(9, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'east')
    fx.at(11, 9, 'refurbished_furniture:dark_oak_table[east=false,north=false,south=true,west=false]')
    fx.at(11, 10, 'refurbished_furniture:dark_oak_table[east=false,north=true,south=false,west=false]')
    fx.carpet(10, 8, 12, 11, 'red')
    fx.lantern(11, 9)
    fx.run([(10, 13), (11, 13)], 'minecraft:bookshelf', 'south')
    fx.lantern(11, 4)
    # andar: quarto do casal (O) | quarto das criancas (NE) | escritorio (SE)
    fx = b.level('floor1')
    wall_x6(fx)
    fx.wall_z(6, 7, 13, gaps=(10,), char=inner(fx))
    bedroom_west(fx, 'brown', 'oak', BR)
    fx.carpet(3, 8, 5, 10, 'brown')
    fx.bed(9, 2, 'light_blue', 'north', BR)
    fx.bed(11, 2, 'pink', 'north', BR)
    fx.at(10, 2, 'refurbished_furniture:oak_drawer[facing={f},left=false,right=false,open=false]', loot=BR, wall='north')
    fx.at(10, 2, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.at(13, 4, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=BR)
    fx.at(7, 5, 'minecraft:potted_dandelion')
    fx.carpet(9, 4, 12, 5, 'yellow')
    fx.lantern(10, 4)
    fx.at(13, 9, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=HM, wall='east')
    fx.at(13, 9, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(12, 9, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'east')
    fx.run([(13, 10), (13, 11)], 'minecraft:bookshelf', 'east')
    fx.run([(8, 13), (9, 13)], 'minecraft:bookshelf', 'south')
    fx.lantern(10, 10)
    b.write()


# ================================================================ adega
def adega():
    b = Build('adegavinho', 'adega', ['ground', 'floor1'], yard='casa')
    CL, HM, BR = LOOT['cellar'], LOOT['home'], LOOT['bedroom']
    fx = b.level('ground')
    fx.wall_x(6, 2, 13, gaps=(7, 8), char=inner(fx, 'vinery:dark_cherry_planks'))
    # adega (O): barricas de fermentacao, racks de vinho na parede interna, prensa no meio
    fx.at(2, 2, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for x in (3, 4):
        fx.at(x, 2, 'vinery:fermentation_barrel[facing={f}]', loot=CL, wall='north')
    fx.at(5, 2, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for z in (3, 4, 5, 10, 11, 12):
        fx.at(5, z, 'vinery:dark_cherry_wine_rack_mid[facing={f},open=false]', loot=CL, wall='east')
        fx.at(5, z, 'vinery:dark_cherry_wine_rack_small[facing={f}]', y=2, wall='east')
    for z in (4, 5):
        fx.at(2, z, 'vinery:storage_pot[facing={f},open=false]', loot=CL, wall='west')
    fx.at(3, 8, 'vinery:apple_press[facing=east,half=lower]', loot=CL)
    fx.at(3, 8, 'vinery:apple_press[facing=east,half=upper]', y=2)
    fx.at(2, 10, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='west')
    fx.at(2, 11, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='west')
    for x in (2, 3, 4):
        fx.at(x, 13, 'vinery:wine_box[facing={f},open=false]', loot=CL, wall='south')
    fx.lantern(3, 4)
    fx.lantern(3, 11)
    # degustacao (L): bar na parede norte e tres mesas
    for x in (9, 10, 11, 12):
        fx.at(x, 2, 'vinery:dark_cherry_cabinet[facing={f},open=false]', loot=CL, wall='north')
    for x in (9, 11):
        fx.at(x, 2, 'vinery:noir_wine[fake_model=false]', y=2)
    fx.at(13, 2, 'vinery:dark_cherry_barrel[facing=up,open=false]', loot=CL)
    for x, z in ((10, 6), (10, 11)):
        fx.at(x, z, 'vinery:dark_cherry_table[facing=south,type=none]', loot=HM)
        fx.chair(x - 1, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'east')
        fx.chair(x + 1, z, 'kaleidoscope_cookery:chair_dark_oak[facing={f},has_carpet=false,waterlogged=false]', 'west')
        fx.lantern(x, z)
    fx.at(11, 13, 'minecraft:potted_azalea_bush')
    fx.at(13, 9, 'furniture:wooden_planter[facing={f},type=none]', wall='east')
    # andar: quarto (O) | copa + sala (L)
    fx = b.level('floor1')
    wall_x6(fx)
    bedroom_west(fx, 'brown', 'dark_oak', BR)
    fx.carpet(3, 8, 5, 10, 'red')
    fridge(fx, 11, 2, 'north')
    kitchen_run(fx, 'dark_oak', [(8, 2, 'cab'), (9, 2, 'sink'), (10, 2, 'stove'), (12, 2, 'cab')], 'north')
    dining(fx, 9, 6, 2, 'refurbished_furniture:dark_oak_table', 'refurbished_furniture:dark_oak_chair[facing={f},tucked=false]', HM)
    for x in (9, 10):
        fx.at(x, 13, 'refurbished_furniture:brown_sofa[facing={f},shape=default]', loot=HM, wall='south')
    fx.carpet(8, 10, 11, 12, 'brown')
    fx.lantern(9, 5)
    fx.lantern(10, 10)
    b.write()


# ================================================================ armazem do porto
def armazem_porto():
    b = Build('armazemporto', 'porto', ['ground', 'floor1'], yard='porto')
    DK, HM, BR = LOOT['dock'], LOOT['home'], LOOT['bedroom']
    fx = b.level('ground')
    # escritorio da doca (NO) separado por parede baixa de tabua
    plank = inner(fx)
    fx.wall_x(5, 2, 5, gaps=(4,), char=plank)
    fx.wall_z(6, 2, 4, char=plank)
    fx.at(2, 2, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(3, 2, 'minecraft:cartography_table', loot=DK)
    fx.at(2, 4, 'refurbished_furniture:oak_desk[facing={f},left=false,right=false]', loot=DK, wall='west')
    fx.at(2, 4, 'refurbished_furniture:white_lamp[powered=false]', y=2)
    fx.chair(3, 4, 'refurbished_furniture:oak_chair[facing={f},tucked=false]', 'west')
    fx.at(4, 2, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=DK)
    fx.at(4, 5, 'refurbished_furniture:oak_storage_cabinet[facing={f},hinge=left,open=false]', loot=DK, wall='south')
    fx.lantern(3, 3)
    # carga: parede leste e duas fileiras de paletes no meio
    for z in (4, 5, 6, 9, 10, 11):
        fx.at(13, z, 'refurbished_furniture:oak_crate[open=false]' if z % 2 else 'minecraft:barrel[facing=up,open=false]', loot=DK)
    for z in range(5, 11):
        fx.at(10, z, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
        fx.at(11, z, 'minecraft:barrel[facing=up,open=false]' if z % 2 else 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    for z in (5, 7, 9):
        fx.at(10, z, 'refurbished_furniture:oak_crate[open=false]', y=2, loot=DK)
    # canto de pesca (SO): barris, tina e redes
    fx.at(2, 13, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(3, 13, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(2, 12, 'minecraft:water_cauldron[level=3]')
    fx.at(2, 11, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    fx.at(2, 9, 'refurbished_furniture:oak_crate[open=false]', loot=DK)
    fx.at(5, 13, 'minecraft:smithing_table', loot=DK)
    for x, z in ((8, 4), (10, 3), (12, 8), (4, 9), (10, 12)):
        fx.lantern(x, z)
    # andar: alojamento dos estivadores + mesa comum + fogao
    fx = b.level('floor1')
    for x, chest_x in ((3, 4), (5, None), (10, 11), (12, None)):
        fx.bed(x, 2, 'brown', 'north', BR)
        if chest_x:
            fx.at(chest_x, 2, 'minecraft:chest[facing=south,type=single,waterlogged=false]', loot=HM)
    fx.at(2, 2, 'minecraft:barrel[facing=up,open=false]', loot=HM)
    fx.at(13, 2, 'minecraft:barrel[facing=up,open=false]', loot=HM)
    dining(fx, 7, 8, 2, 'refurbished_furniture:oak_table', 'refurbished_furniture:oak_chair[facing={f},tucked=false]', HM)
    fx.at(2, 13, 'farmersdelight:stove[facing={f},lit=false]', wall='south')
    fx.at(2, 13, 'farmersdelight:cooking_pot[facing=north,support=tray]', y=2)
    fx.at(3, 13, 'farmersdelight:oak_cabinet[facing={f},open=false]', loot=LOOT['kitchen'], wall='south')
    fx.at(4, 13, 'minecraft:barrel[facing=up,open=false]', loot=DK)
    fx.at(13, 9, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=DK)
    fx.at(13, 10, 'minecraft:chest[facing=west,type=single,waterlogged=false]', loot=DK)
    fx.lantern(4, 4)
    fx.lantern(11, 4)
    fx.lantern(7, 8)
    fx.lantern(8, 8)
    b.write()


def main():
    for name, mat in (('deposito_pedra', 'pedra'), ('deposito_andesito', 'andesito'), ('deposito_ardosia', 'ardosia'),
                      ('deposito_tijolo', 'tijolo')):
        deposito(name, mat)
    oficina()
    casa_fazenda()
    padaria()
    cozinha_kaleido()
    adega()
    armazem_porto()
    print('remodel: 10 construcoes proprias regravadas com a casca nova')


if __name__ == '__main__':
    main()
