"""Mobilia coerente para os predios 16x16 de houses.py e cozy_expansion.py.

Convencao de facing medida nos predios DC ja gerados no mapa de teste:
- refurbished_furniture: facing = lado das COSTAS (parede). Cadeira/sofa: facing
  aponta para longe da mesa.
- resto (farmersdelight, bakery, vinery, kaleidoscope, another_furniture,
  candlelight, supplementaries, vanilla bau/barril/fornalha): facing = FRENTE.
  Cadeira kaleidoscope/another_furniture: facing aponta para a mesa (encosto
  do modelo fica do lado oposto).
- cama vanilla: facing = direcao da cabeceira (cabeceira encostada na parede).

Grade: x = leste, z = sul, slices[y][z][x]. Interior util x/z 1..14, y 1..3
(y4 = teto). Janelas na faixa y2 (menos cantos e portas): moveis de parede
altos ficam nos cantos; arandelas e lanternas vao em y3.
"""

OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
STEP = {'north': (0, -1), 'south': (0, 1), 'west': (-1, 0), 'east': (1, 0)}
BACK_NS = ('refurbished_furniture:',)
# chars reservados pela casca (base_palette) e pelo filler 'G'
RESERVED = set(' WFfgdDCRHlKG') | {'¡', '¢'}
POOL = [c for c in 'abcehijkmnopqrstuvwxyzABEIJLMNOPQSTUVXYZ0123456789!#$%&*+-=?@^~<>/|;:,.()[]{}_'
        if c not in RESERVED]
# celulas que nunca recebem movel (y1/y2): frente das portas N/S e acesso da escada
FREE_UPPER = {(13, 13), (14, 13)}
FREE_GROUND = FREE_UPPER | {(7, 1), (8, 1), (7, 14), (8, 14)}
SUPPORT = set('WgK')


def facing_for(block, wall=None, toward=None):
    back = block.startswith(BACK_NS)
    if wall:
        return wall if back else OPP[wall]
    if toward:
        return OPP[toward] if back else toward
    raise ValueError('wall ou toward')


class Furnish:
    def __init__(self, palettes, pal, part, slices, free=FREE_GROUND):
        self.P, self.pal, self.part, self.s, self.free = palettes, pal, part, slices, free

    def char(self, block, loot=None):
        used = self.P.setdefault(self.part, {})
        for c, e in used.items():
            if e['block'] == block and e.get('loot') == loot:
                return c
        c = next((ch for ch in POOL if ch not in used), None)
        if c is None:
            raise SystemExit(f'{self.part}: acabaram os chars da paleta')
        self.pal(self.part, c, block, loot)
        return c

    def at(self, x, z, block, y=1, loot=None, wall=None, toward=None):
        if (x, z) in self.free and y in (1, 2):
            raise SystemExit(f'{self.part}: movel bloqueando porta/escada em {(x, z, y)}')
        if '{f}' in block:
            block = block.replace('{f}', facing_for(block, wall, toward))
        if wall:
            dx, dz = STEP[wall]
            behind = self.s[y][z + dz][x + dx]
            if behind not in SUPPORT:
                raise SystemExit(f'{self.part}: {block} em {(x, z, y)} sem parede a {wall} ({behind!r})')
        if self.s[y][z][x] != ' ':
            raise SystemExit(f'{self.part}: celula ocupada {(x, z, y)} por {self.s[y][z][x]!r}')
        self.s[y][z][x] = self.char(block, loot)

    # ---------------------------------------------------------- atalhos
    def run(self, cells, block, wall, y=1, loot=None):
        for x, z in cells:
            self.at(x, z, block, y=y, loot=loot, wall=wall)

    def chair(self, x, z, block, toward, loot=None):
        self.at(x, z, block, toward=toward, loot=loot)

    def bed(self, x, z, color, head, loot=None):
        """(x, z) = cabeceira; o pe fica um bloco para tras."""
        dx, dz = STEP[OPP[head]]
        self.at(x, z, f'minecraft:{color}_bed[part=head,facing={head},occupied=false]', loot=loot)
        self.at(x + dx, z + dz, f'minecraft:{color}_bed[part=foot,facing={head},occupied=false]', loot=loot)

    def lantern(self, x, z):
        self.at(x, z, 'minecraft:lantern[hanging=true]', y=3)

    def sconce(self, x, z, wall):
        self.at(x, z, 'supplementaries:sconce_wall[facing={f},lit=true]', y=3, wall=wall)

    def carpet(self, x0, z0, x1, z1, color):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                if self.s[1][z][x] == ' ':
                    self.at(x, z, f'minecraft:{color}_carpet')

    def wall_x(self, x, z0, z1, gaps=(), char='W'):
        """parede interna norte-sul em x, com vaos (porta sem folha) nos z de gaps."""
        for z in range(z0, z1 + 1):
            for y in (1, 2, 3):
                if z in gaps and y in (1, 2):
                    continue
                self.s[y][z][x] = char

    def wall_z(self, z, x0, x1, gaps=(), char='W'):
        for x in range(x0, x1 + 1):
            for y in (1, 2, 3):
                if x in gaps and y in (1, 2):
                    continue
                self.s[y][z][x] = char
