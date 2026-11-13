"""Leitura de schematics: .schem (Sponge v2/v3, WorldEdit) e .nbt (structure block).

load(path) -> (W, H, L, grid, bes): grid[y][z][x] = estado 'ns:id[k=v,...]' (props em ordem
alfabetica), bes = {(x, y, z): nbt do block entity em dict simples}.
"""
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nbtmini import NBTReader

AIR = 'minecraft:air'


def plain(v):
    t, x = v
    if t == 10:
        return {k: plain(vv) for k, vv in x.items()}
    if t == 9:
        return [plain((x[0], e)) for e in x[1]]
    return x


def varints(b):
    out, i = [], 0
    while i < len(b):
        v = s = 0
        while True:
            c = b[i]
            i += 1
            v |= (c & 0x7F) << s
            if not c & 0x80:
                break
            s += 7
        out.append(v)
    return out


def norm(state):
    """'id[b=1,a=2]' -> 'id[a=2,b=1]' (sem namespace vira minecraft:)"""
    if ':' not in state.split('[')[0]:
        state = 'minecraft:' + state
    if '[' not in state:
        return state
    bid, rest = state.split('[', 1)
    props = sorted(p.split('=', 1) for p in rest.rstrip(']').split(',') if p)
    return bid + '[' + ','.join(f'{k}={v}' for k, v in props) + ']'


def load(path):
    raw = open(path, 'rb').read()
    try:
        raw = gzip.decompress(raw)
    except OSError:
        pass
    _, tid, val = NBTReader(raw).read_tag()
    d = plain((tid, val))
    bes = {}
    if path.endswith('.nbt'):
        W, H, L = d['size']
        pal = []
        for e in d['palette']:
            props = e.get('Properties', {})
            pal.append(norm(e['Name'] + ('[' + ','.join(f'{k}={v}' for k, v in props.items()) + ']' if props else '')))
        g = [[[AIR] * W for _ in range(L)] for _ in range(H)]
        for b in d['blocks']:
            x, y, z = b['pos']
            g[y][z][x] = pal[b['state']]
            if 'nbt' in b:
                bes[(x, y, z)] = b['nbt']
        return W, H, L, g, bes
    if 'Schematic' in d:
        d = d['Schematic']
    W, H, L = d['Width'], d['Height'], d['Length']
    if 'Blocks' in d:  # Sponge v3
        pald, data, bel = d['Blocks']['Palette'], d['Blocks']['Data'], d['Blocks'].get('BlockEntities', [])
    else:
        pald, data, bel = d['Palette'], d['BlockData'], d.get('BlockEntities', [])
    pal = [AIR] * (max(pald.values()) + 1)
    for k, v in pald.items():
        pal[v] = norm(k)
    data = data if isinstance(data, (bytes, bytearray)) else bytes(b & 0xFF for b in data)
    idx = varints(data)
    g = [[[AIR] * W for _ in range(L)] for _ in range(H)]
    for i, v in enumerate(idx[:W * H * L]):
        y, r = divmod(i, W * L)
        z, x = divmod(r, W)
        g[y][z][x] = pal[v]
    for be in bel:
        x, y, z = be['Pos']
        bes[(x, y, z)] = be
    return W, H, L, g, bes
