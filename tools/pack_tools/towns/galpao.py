"""Casca "de galpao" para as construcoes proprias de 16x16 (depositos e oficina Create).

A casca antiga era a caixa de 16x16 inteira com faixa de vidro e telhado sem beiral: parecia um
cubo. Aqui as paredes ficam recuadas 1 bloco (x1..14, z1..14) e a borda do chunk vira quintal:
- base de pedra (rodape), enxaimel com viga no topo da parede e pilares de tora 1 bloco para
  fora da parede (no meio de cada parede e no canto de fora), para dar profundidade;
- janelas em pares com venezianas (alcapao aberto) e floreira embaixo;
- alpendre nas portas N e S: postes de cerca, cobertura de escada/laje e lanterna;
- telhado de duas aguas com beiral (z0/z15) e empena avancada (x0/x15), oitao com tora e
  janelinha, cumeeira de laje; chamine opcional atravessando tudo;
- canteiros, arbustos, banco, lenha e caixotes no quintal.

Grade: slices[y][z][x], x = leste, z = sul. Interior util x2..13, z2..13, y1..3 (y4 = teto).
Janelas (y2-y3) nas paredes N/S em x2-3 e x12-13, nas L/O em z2-3, z7-8 e z12-13: movel alto
fica fora dessas celulas.
Uso: os geradores (vila.py, houses.py) chamam Shell(...).ground()/floor()/roof() e mobiliam com
`furnish()` (interior.Furnish com as celulas livres das portas novas).
"""
import houses as H
import interior as I

X0, X1, Z0, Z1 = 1, 14, 1, 14          # linha das paredes
DOORS = (7, 8)                           # portas duplas no meio das paredes N e S
POSTS_X = (1, 5, 10, 14)
POSTS_Z = (1, 5, 10, 14)
WIN_X = ((2, 3), (12, 13))               # pares de janela nas paredes N/S
WIN_Z = ((2, 3), (7, 8), (12, 13))       # pares nas paredes L/O
FREE = {(7, 2), (8, 2), (7, 13), (8, 13), (12, 13)}  # frente das portas e da escada de mao
LADDER_XZ = (13, 13)

# chars da casca: fora do POOL do interior.Furnish (ele aloca o resto sozinho)
CHARS = ('ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωЀЁЂЃЄЅІЇЈЉЊЋЌЍЎЏБДЖИЙЛПФЦЧШЩЪЫЬЭЮЯбвгджзийлпфцчшщъыьэюя')

STYLES = {
    # infill, rodape, tora do enxaimel, madeira (porta/cerca/alcapao), escada/laje do telhado, piso, janela
    'pedra': dict(infill='minecraft:stone_bricks', plinth='minecraft:mossy_cobblestone', log='minecraft:stripped_dark_oak_log',
                  wood='dark_oak', roof='minecraft:dark_oak', floor='minecraft:spruce_planks', glass='create:dark_oak_window'),
    'andesito': dict(infill='minecraft:polished_andesite', plinth='minecraft:cobblestone', log='minecraft:stripped_spruce_log',
                     wood='spruce', roof='minecraft:spruce', floor='minecraft:oak_planks', glass='create:spruce_window'),
    'ardosia': dict(infill='minecraft:mud_bricks', plinth='minecraft:cobbled_deepslate', log='minecraft:stripped_dark_oak_log',
                    wood='dark_oak', roof='minecraft:deepslate_tile', floor='minecraft:dark_oak_planks', glass='create:dark_oak_window'),
    'tijolo': dict(infill='minecraft:bricks', plinth='minecraft:stone_bricks', log='minecraft:stripped_spruce_log',
                   wood='spruce', roof='minecraft:deepslate_tile', floor='minecraft:spruce_planks', glass='create:spruce_window'),
    'fazenda': dict(infill='minecraft:calcite', plinth='minecraft:cobblestone', log='minecraft:stripped_dark_oak_log',
                    wood='oak', roof='minecraft:spruce', floor='minecraft:oak_planks', glass='create:oak_window'),
    'adega': dict(infill='vinery:dark_cherry_planks', plinth='minecraft:stone_bricks', log='minecraft:stripped_spruce_log',
                  wood='dark_oak', roof='minecraft:deepslate_tile', floor='minecraft:stone_bricks', glass='create:dark_oak_window'),
    'porto': dict(infill='minecraft:oak_planks', plinth='minecraft:cobblestone', log='minecraft:stripped_spruce_log',
                  wood='spruce', roof='minecraft:spruce', floor='minecraft:oak_planks', glass='create:spruce_window'),
    'oficina': dict(infill='minecraft:bricks', plinth='minecraft:andesite', log='minecraft:stripped_spruce_log',
                    wood='spruce', roof='minecraft:waxed_weathered_cut_copper', floor='minecraft:oak_planks', glass='create:framed_glass_pane'),
}


def grid():
    return [[' '] * 16 for _ in range(16)]


def on_ring(x, z):
    return X0 <= x <= X1 and Z0 <= z <= Z1 and (x in (X0, X1) or z in (Z0, Z1))


def inside(x, z):
    return X0 < x < X1 and Z0 < z < Z1


class Shell:
    def __init__(self, parts, style, chimney=None, yard='deposito'):
        """parts: nomes das paletas (todas recebem a mesma casca); chimney: (x, z) dentro de casa ou None"""
        self.parts, self.st, self.chimney, self.yard = parts, STYLES[style], chimney, yard
        self.map = {}
        self.chars = iter(CHARS)
        for p in parts:
            H.pal(p, 'G', 'minecraft:stone_bricks')
        w = self.st['wood']
        self.c_infill = self.c(self.st['infill'])
        # o interior.Furnish so encosta movel em chars de SUPPORT: parede, pilar, rodape e janela
        for b in (self.st['infill'], self.st['plinth'], f'{self.st["log"]}[axis=y]', self.st['glass']):
            I.SUPPORT.add(self.c(b))
        self.wood = w

    def c(self, block):
        if block not in self.map:
            ch = next(self.chars)
            for p in self.parts:
                H.pal(p, ch, block)
            self.map[block] = ch
        return self.map[block]

    # ------------------------------------------------------------ andares
    def walls(self, sl, ground):
        st, w = self.st, self.wood
        log_y = self.c(f'{st["log"]}[axis=y]')
        for y in (1, 2, 3):
            for z in range(16):
                for x in range(16):
                    if not on_ring(x, z):
                        continue
                    # so o canto fica na linha da parede; os pilares do meio saem 1 bloco (outer_posts)
                    if x in (X0, X1) and z in (Z0, Z1):
                        sl[y][z][x] = log_y
                    elif y == 1:
                        sl[y][z][x] = self.c(st['plinth'])
                    else:
                        sl[y][z][x] = self.c_infill
        # janelas em pares (y2 e y3)
        glass = self.c(st['glass'])
        for a, b in WIN_X:
            for z in (Z0, Z1):
                for x in (a, b):
                    sl[2][z][x] = glass
                    sl[3][z][x] = glass
        for a, b in WIN_Z:
            for x in (X0, X1):
                for z in (a, b):
                    sl[2][z][x] = glass
                    sl[3][z][x] = glass
        # viga no topo (y4) e cantos
        for z in range(16):
            for x in range(16):
                if on_ring(x, z):
                    axis = 'x' if z in (Z0, Z1) else 'z'
                    sl[4][z][x] = self.c(f'{st["log"]}[axis={axis}]')
        for x, z in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)):
            sl[4][z][x] = log_y
        # teto (y4) com vigas aparentes e forro (y5)
        for z in range(Z0 + 1, Z1):
            for x in range(X0 + 1, X1):
                sl[4][z][x] = self.c(f'{st["log"]}[axis=x]') if z % 3 == 0 else self.c(st['floor'])
                sl[5][z][x] = self.c(st['floor'])
        for z in range(Z0, Z1 + 1):
            for x in range(X0, X1 + 1):
                if on_ring(x, z):
                    sl[5][z][x] = self.c_infill
        if ground:
            # portas duplas N/S
            # hinge=left fica do lado esquerdo de quem olha para `facing`: a oeste na porta norte,
            # a leste na porta sul (folha trocada = dobradicas no meio)
            for z, f, hinges in ((Z0, 'north', ('left', 'right')), (Z1, 'south', ('right', 'left'))):
                for x, hinge in zip(DOORS, hinges):
                    sl[1][z][x] = self.c(f'minecraft:{w}_door[half=lower,hinge={hinge},facing={f},open=false]')
                    sl[2][z][x] = self.c(f'minecraft:{w}_door[half=upper,hinge={hinge},facing={f},open=false]')
                    sl[3][z][x] = self.c_infill

    def exterior(self, sl, ground):
        """venezianas nas janelas; no terreo tambem quintal, floreiras, alpendre e canteiros"""
        st, w = self.st, self.wood
        shut = lambda f: self.c(f'minecraft:{w}_trapdoor[facing={f},half=bottom,open=true]')
        for a, b in WIN_X:
            for out, f in ((Z0 - 1, 'north'), (Z1 + 1, 'south')):
                for y in (2, 3):
                    sl[y][out][a - 1] = shut(f)
                    sl[y][out][b + 1] = shut(f)
        for a, b in WIN_Z:
            for out, f in ((X0 - 1, 'west'), (X1 + 1, 'east')):
                for y in (2, 3):
                    sl[y][a - 1][out] = shut(f)
                    sl[y][b + 1][out] = shut(f)
        if not ground:
            return
        # chao: quintal de grama, caminho de terra nas portas, fundacao sob as paredes, piso dentro
        grass, path = self.c('minecraft:grass_block[snowy=false]'), self.c('minecraft:dirt_path')
        for z in range(16):
            for x in range(16):
                if on_ring(x, z):
                    sl[0][z][x] = self.c('minecraft:cobblestone')
                elif inside(x, z):
                    sl[0][z][x] = self.c(st['floor'])
                elif DOORS[0] - 1 <= x <= DOORS[1] + 1 and (z < Z0 or z > Z1):
                    sl[0][z][x] = path
                else:
                    sl[0][z][x] = grass
        # floreiras sob as janelas da frente (z0)
        for a, b in WIN_X:
            for x in (a, b):
                sl[1][Z0 - 1][x] = self.c('supplementaries:flower_box[facing=north,face=floor]')
        # alpendre N e S: postes de cerca, cobertura de escada e lanterna pendurada
        fence = self.c(f'minecraft:{w}_fence')
        for zp, f in ((Z0 - 1, 'south'), (Z1 + 1, 'north')):
            for x in (DOORS[0] - 2, DOORS[1] + 2):
                for y in (1, 2, 3):
                    sl[y][zp][x] = fence
            for x in range(DOORS[0] - 2, DOORS[1] + 3):
                sl[4][zp][x] = self.c(f'{st["roof"]}_stairs[facing={f},half=bottom,shape=straight]')
            for x in DOORS:
                sl[3][zp][x] = self.c('minecraft:lantern[hanging=true]')
        # bancos ao lado da porta da frente, canteiros e arbustos nas laterais
        for x in (4, 11):
            sl[1][Z0 - 1][x] = self.c('another_furniture:oak_bench[facing=north]')
        flowers = ['minecraft:poppy', 'minecraft:cornflower', 'minecraft:oxeye_daisy', 'minecraft:allium', 'minecraft:azure_bluet']
        for i, z in enumerate(range(Z0, Z1 + 1)):
            for x in (X0 - 1, X1 + 1):
                if z in POSTS_Z:
                    sl[1][z][x] = self.c('minecraft:azalea_leaves[persistent=true]' if i % 2 else 'minecraft:flowering_azalea_leaves[persistent=true]')
                else:
                    sl[0][z][x] = self.c('minecraft:rooted_dirt')
                    sl[1][z][x] = self.c(flowers[(i + x) % len(flowers)])
        # quintal dos fundos (z15): lenha empilhada e o estoque do tipo do predio
        back = Z1 + 1
        logs = self.c('minecraft:oak_log[axis=x]')
        for x in (1, 2, 3):
            sl[1][back][x] = logs
        sl[2][back][2] = logs
        stock = {
            'deposito': [(12, 1, 'minecraft:barrel[facing=up,open=false]'), (13, 1, f'redeco:{w}_crate[facing=south,propped=false]'),
                         (13, 2, f'redeco:{w}_crate[facing=south,propped=false]'), (14, 1, 'supplementaries:sack')],
            'oficina': [(12, 1, 'minecraft:composter[level=3]'), (13, 1, 'create:andesite_casing'),
                        (13, 2, 'create:brown_toolbox[facing=north,waterlogged=false]'), (14, 1, 'minecraft:barrel[facing=up,open=false]')],
            'casa': [(12, 1, 'minecraft:composter[level=3]'), (13, 1, 'minecraft:hay_block[axis=y]'), (14, 1, 'minecraft:barrel[facing=up,open=false]')],
            'porto': [(12, 1, 'minecraft:barrel[facing=up,open=false]'), (13, 1, 'minecraft:barrel[facing=up,open=false]'),
                      (13, 2, 'minecraft:barrel[facing=up,open=false]'), (14, 1, 'supplementaries:sack')],
        }[self.yard]
        for x, y, b in stock:
            sl[y][back][x] = self.c(b)

    def outer_posts(self, sl, ys, footing=False):
        """pilares de tora 1 bloco para fora da parede (profundidade na fachada): os do meio de cada
        parede e um no canto de fora; roda depois do exterior (o pilar do alpendre vira tora)"""
        log_y = self.c(f'{self.st["log"]}[axis=y]')
        cells = [(x, z) for x in POSTS_X[1:-1] for z in (Z0 - 1, Z1 + 1)]
        cells += [(x, z) for z in POSTS_Z[1:-1] for x in (X0 - 1, X1 + 1)]
        cells += [(x, z) for x in (X0 - 1, X1 + 1) for z in (Z0 - 1, Z1 + 1)]
        for x, z in cells:
            if footing:
                sl[0][z][x] = self.c(self.st['plinth'])
            for y in ys:
                sl[y][z][x] = log_y

    def gable_corbel(self, sl):
        """ultimo andar: misula (escada invertida) e o pe do pendural que sobe pela empena de fora"""
        for x, f in ((X0 - 1, 'east'), (X1 + 1, 'west')):
            for z in (7, 8):
                sl[4][z][x] = self.c(f'minecraft:{self.wood}_stairs[facing={f},half=top,shape=straight]')
                sl[5][z][x] = self.c(f'{self.st["log"]}[axis=y]')

    def chimney_column(self, sl, ys):
        # chamine MACICA de tijolos (sem duto aberto): nao ha buraco nos pisos nem fogueira
        # dentro de casa; a fogueira acesa fica so no topo, em roof()
        if self.chimney:
            x, z = self.chimney
            for y in ys:
                if y < len(sl):
                    sl[y][z][x] = self.c('minecraft:bricks')

    def chimney_rim(self, sl, y):
        # boca de tijolos em volta do duto (andar de cima e telhado): fica apoiada na laje/piso
        if self.chimney:
            x, z = self.chimney
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if sl[y][z + dz][x + dx] == ' ':
                    sl[y][z + dz][x + dx] = self.c('minecraft:bricks')

    def ground(self, ladder=False):
        sl = [grid() for _ in range(6)]
        self.walls(sl, True)
        self.exterior(sl, True)
        self.outer_posts(sl, (1, 2, 3, 4, 5), footing=True)
        if ladder:
            x, z = LADDER_XZ
            for y in (1, 2, 3, 4, 5):
                sl[y][z][x] = self.c('minecraft:ladder[facing=west]')
        self.chimney_column(sl, (2, 3, 4, 5))
        return sl

    def floor(self, ladder=False):
        sl = [grid() for _ in range(6)]
        for z in range(Z0, Z1 + 1):
            for x in range(X0, X1 + 1):
                sl[0][z][x] = self.c(self.st['floor']) if inside(x, z) else self.c_infill
        self.walls(sl, False)
        self.exterior(sl, False)
        self.outer_posts(sl, (0, 1, 2, 3, 4, 5))
        if ladder:
            x, z = LADDER_XZ
            for y in (0, 1, 2):
                sl[y][z][x] = self.c('minecraft:ladder[facing=west]')
        self.chimney_column(sl, (0, 1, 2, 3, 4, 5))
        return sl

    def eave(self, sl):
        """primeira fiada do telhado (beiral, z0/z15) na ultima fatia do ultimo andar"""
        st = self.st
        for x in range(16):
            sl[5][Z0 - 1][x] = self.c(f'{st["roof"]}_stairs[facing=south,half=bottom,shape=straight]')
            sl[5][Z1 + 1][x] = self.c(f'{st["roof"]}_stairs[facing=north,half=bottom,shape=straight]')

    def roof(self):
        """parte top: fiadas 1..7 (z1..7 e z14..8) com empena avancada em x0/x15, cumeeira em y7"""
        st = self.st
        top = 7
        sl = [grid() for _ in range(top + 3)]
        sn = self.c(f'{st["roof"]}_stairs[facing=south,half=bottom,shape=straight]')
        ss = self.c(f'{st["roof"]}_stairs[facing=north,half=bottom,shape=straight]')
        log = st['log']
        for j in range(1, top + 1):
            y = j - 1
            for x in range(16):
                sl[y][Z0 - 1 + j][x] = sn
                sl[y][Z1 + 1 - j][x] = ss
            for z in range(Z0 + j, Z1 + 1 - j):
                for x in (X0, X1):
                    sl[y][z][x] = self.c_infill
        for x in range(16):
            for z in (7, 8):
                sl[top][z][x] = self.c(f'{st["roof"]}_slab[type=bottom]')
        # oitao: linha (collar) de tora em y0, pendural 1 bloco para fora (sob a empena avancada,
        # continua do pe que gable_corbel poe no ultimo andar), janelinhas
        for x, xo in ((X0, X0 - 1), (X1, X1 + 1)):
            for z in range(Z0 + 1, Z1):
                sl[0][z][x] = self.c(f'{log}[axis=z]')
            for y in range(0, top - 1):
                for z in (7, 8):
                    sl[y][z][xo] = self.c(f'{log}[axis=y]')
            for z in (5, 10):
                if sl[2][z][x] == self.c_infill:
                    sl[2][z][x] = self.c('minecraft:glass_pane[north=true,south=true]')
        if self.chimney:
            # chamine maciça: nucleo de tijolos de y0 ate y(top+1) e anel de tijolos ao redor
            # onde ainda ha ar; a fogueira acesa fica por cima do nucleo (y top+2, ao ceu)
            x, z = self.chimney
            for y in range(0, top + 2):
                sl[y][z][x] = self.c('minecraft:bricks')
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if sl[y][z + dz][x + dx] == ' ':
                        sl[y][z + dz][x + dx] = self.c('minecraft:bricks')
            sl[top + 2][z][x] = self.c('minecraft:campfire[facing=north,lit=true]')
        return sl


def furnish(part, slices, ladder=True, ground=True, extra_free=()):
    free = FREE if ladder else FREE - {(LADDER_XZ[0] - 1, LADDER_XZ[1])}
    if not ground:  # andar de cima nao tem porta
        free = {(LADDER_XZ[0] - 1, LADDER_XZ[1])}
    return I.Furnish(H.PALETTES, H.pal, part, slices, free=set(free) | set(extra_free))
