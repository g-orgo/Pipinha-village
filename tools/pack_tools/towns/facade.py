"""Retoque das fachadas das construcoes proprias que continuam (as casas da vila agora sao schematics).

Inspirado nas casas dos schematics e nos predios importados: em vez de caixa lisa com faixa
continua de vidro e laje no topo, cada predio de 16x16 ganha
- enxaimel: tora descascada nos 4 cantos e pilares em 5/10 de cada fachada, viga no topo da parede;
- rodape de pedra na primeira fiada;
- janelas em pares (2 de largura, 2 de altura quando o interior deixa) separadas por parede/pilar;
- telhado de duas aguas (9 fatias, cumeeira de laje, chamine de tijolo) no lugar da laje plana;
  metade dos predios com a cumeeira girada (norte-sul).

Roda no datapack final (depois do finalize.py, antes do polish.py), parte a parte via lcparts.
Nunca mexe em porta, nem em celula de parede que tenha movel encostado por dentro na altura mudada.
"""
import re
import sys
import zlib

import lcparts as L
import mapping as M

# 2026-10-03: as 10 construcoes que este script retocava sao refeitas por remodel.py (casca de galpao.py);
# fica sem alvo e fora da pipeline, so como referencia
TARGETS = []
SIDE_POS = range(1, 15)
POSTS = (5, 10)
WINDOWS = (2, 3, 7, 8, 12, 13)


def bid(s):
    return s.split('[', 1)[0]


def is_air(s):
    return s is None or L.block_is_air(s)


def ring_cells():
    """(z, x, lado, posicao ao longo do lado)"""
    for p in SIDE_POS:
        yield 0, p, 'n', p
        yield 15, p, 's', p
        yield p, 0, 'w', p
        yield p, 15, 'e', p


def inner(z, x):
    return (min(14, max(1, z)), min(14, max(1, x)))


def frame_log(wall):
    if re.search(r'dark_oak|dark_cherry|deepslate|blackstone|mud_bricks|bricks$', bid(wall)):
        return 'minecraft:stripped_birch_log' if 'brick' not in wall else 'minecraft:stripped_spruce_log'
    return 'minecraft:stripped_dark_oak_log'


def plinth(wall):
    w = bid(wall)
    if re.search(r'planks|terracotta|wool|dark_cherry', w):
        return 'minecraft:cobblestone'
    if re.search(r'bricks|mud', w):
        return 'minecraft:stone_bricks'
    return 'minecraft:mossy_cobblestone'


def roof_mats(wall):
    w = bid(wall)
    if re.search(r'dark_oak|dark_cherry|bricks$|mud_bricks', w):
        return 'minecraft:deepslate_tile_stairs', 'minecraft:deepslate_tile_slab'
    if re.search(r'spruce', w):
        return 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab'
    if re.search(r'stone|andesite|deepslate|cobble', w):
        return 'minecraft:dark_oak_stairs', 'minecraft:dark_oak_slab'
    return 'minecraft:spruce_stairs', 'minecraft:spruce_slab'


def wall_block(g):
    from collections import Counter
    c = Counter()
    for y in (1, 2, 3):
        if y >= g.H:
            continue
        for z, x, _, _ in ring_cells():
            b = g.b(y, z, x)
            if b and not is_air(b) and not re.search(r'glass|pane|window|door|_log|stairs|slab', b):
                c[b] += 1
    return c.most_common(1)[0][0] if c else None


def near_door(g, y, z, x):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for dx in (-1, 0, 1):
                b = g.b(y + dy, z + dz, x + dx) if g.inside(y + dy, z + dz, x + dx) else None
                if b and re.search(r'_door\b|_door\[|door$', bid(b)):
                    return True
    return False


def clean(state):
    b, p = M.parse(state)
    return M.fmt(b, M.clean_props(b, p))


def retouch_walls(g, stats):
    wall = wall_block(g)
    if not wall:
        return None
    glass = None
    for z, x, _, _ in ring_cells():
        b = g.b(2, z, x)
        if b and re.search(r'glass|pane|window', b):
            glass = b
            break
    log = frame_log(wall)
    base = plinth(wall)
    for z, x, side, p in ring_cells():
        if near_door(g, 2, z, x):
            continue
        iz, ix = (1 if side == 'n' else 14 if side == 's' else z), (1 if side == 'w' else 14 if side == 'e' else x)
        for y in (1, 2, 3):
            cur = g.b(y, z, x)
            if cur is None or is_air(cur):
                continue
            behind_free = is_air(g.b(y, iz, ix))
            if p in POSTS:
                g.put(y, z, x, clean(f'{log}[axis=y]'))
                stats['pilar'] += 1
            elif y == 1:
                if cur == wall:
                    g.put(y, z, x, base)
                    stats['rodape'] += 1
            elif glass and p in WINDOWS and (y == 2 or behind_free):
                if cur != glass:
                    g.put(y, z, x, glass)
                    stats['janela'] += 1
            elif glass and re.search(r'glass|pane|window', cur):
                g.put(y, z, x, wall)
                stats['parede'] += 1
    # cantos
    for z, x in ((0, 0), (0, 15), (15, 0), (15, 15)):
        for y in (1, 2, 3):
            if g.b(y, z, x) and not is_air(g.b(y, z, x)):
                g.put(y, z, x, clean(f'{log}[axis=y]'))
    # viga no topo da parede (fiada 4 = borda do teto)
    if g.H > 4:
        for z, x, side, p in ring_cells():
            b = g.b(4, z, x)
            if b and not is_air(b):
                g.put(4, z, x, clean(f'{log}[axis={"x" if side in "ns" else "z"}]'))
                stats['viga'] += 1
        for z, x in ((0, 0), (0, 15), (15, 0), (15, 15)):
            if g.b(4, z, x) and not is_air(g.b(4, z, x)):
                g.put(4, z, x, clean(f'{log}[axis=y]'))
    return wall


def gable(g, wall, seed, stats):
    """substitui a parte de topo (laje plana) por telhado de duas aguas de 9 fatias"""
    stairs, slab = roof_mats(wall)
    turn = seed % 2 == 1
    H = 9
    while len(g.s) < H:
        g.s.append([[' '] * 16 for _ in range(16)])
    g.H = H
    for y in range(H):
        for z in range(16):
            for x in range(16):
                g.s[y][z][x] = ' '
    g.changed = True

    def put(y, z, x, block):
        if turn:
            z, x = x, z
            block = block.replace('facing=south', 'facing=EAST').replace('facing=north', 'facing=WEST').lower()
        g.put(y, z, x, clean(block))

    log = frame_log(wall)
    for k in range(8):
        for x in range(16):
            put(k, k, x, f'{stairs}[facing=south,half=bottom,shape=straight,waterlogged=false]')
            put(k, 15 - k, x, f'{stairs}[facing=north,half=bottom,shape=straight,waterlogged=false]')
        for z in range(k + 1, 15 - k):
            put(k, z, 0, wall)
            put(k, z, 15, wall)
    for z in (7, 8):
        for x in range(16):
            put(8, z, x, f'{slab}[type=bottom,waterlogged=false]')
    # oitao: tora no meio e janelinha
    for k in range(1, 7):
        for x in (0, 15):
            put(k, 7, x, f'{log}[axis=y]')
    for x in (0, 15):
        put(3, 8, x, 'minecraft:glass_pane[east=false,north=true,south=true,waterlogged=false,west=false]' if not turn else
            'minecraft:glass_pane[east=true,north=false,south=false,waterlogged=false,west=true]')
    # chamine de tijolo com fogueira (fumaça)
    for k in range(3, 8):
        put(k, 12, 12, 'minecraft:bricks')
    put(8, 12, 12, 'minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]')
    stats['telhado'] += 1


def main():
    store = L.Store()
    stats = __import__('collections').Counter()
    for t in TARGETS:
        names = sorted(n for n in store.parts if n.startswith(f'sunlit:{t}/'))
        wall = None
        for n in names:
            if n.endswith('/top'):
                continue
            path, part = store.parts[n]
            g = L.Grid(store, n, part)
            w = retouch_walls(g, stats)
            wall = wall or w
            if g.commit():
                L.json.dump(part, open(path, 'w', encoding='utf-8'))
        top = f'sunlit:{t}/top'
        if top in store.parts and wall:
            path, part = store.parts[top]
            g = L.Grid(store, top, part)
            gable(g, wall, zlib.crc32(t.encode()), stats)
            if g.commit():
                L.json.dump(part, open(path, 'w', encoding='utf-8'))
    n = store.save()
    print(f'facade: {dict(stats)}; {n} paletas regravadas')


if __name__ == '__main__':
    main()
