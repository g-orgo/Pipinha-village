"""Read-only helpers to inspect placed blocks in a save (game closed or not: only reads region files).

Usage:
  python3 inspect_save.py "<save>" layers <chunkX> <chunkZ> <y> [<y> ...]   # letter map per layer + legend
  python3 inspect_save.py "<save>" column <x> <z> <y0> <y1>                 # blocks of one column
As a module: get(save, x, y, z) -> 'ns:block[props]' or None.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrofit_hedges import read_region, decode

_cache = {}


def chunk(save, cx, cz):
    key = (save, cx, cz)
    if key in _cache:
        return _cache[key]
    path = os.path.join(save, 'region', f'r.{cx >> 5}.{cz >> 5}.mca')
    secs = {}
    if os.path.exists(path):
        _, out = read_region(path)
        root = out.get((cx & 31) + (cz & 31) * 32)
        for s in (root['sections'][1][1] if root else []):
            if 'block_states' not in s:
                continue
            pal, idx = decode(s['block_states'][1])
            names = []
            for p in pal:
                d = p[1] if isinstance(p, tuple) else p
                n = d['Name'][1]
                if 'Properties' in d:
                    n += '[' + ','.join(f'{k}={v[1]}' for k, v in sorted(d['Properties'][1].items())) + ']'
                names.append(n)
            secs[s['Y'][1]] = (names, idx)
    _cache[key] = secs
    return secs


def get(save, x, y, z):
    s = chunk(save, x >> 4, z >> 4).get(y >> 4)
    if not s:
        return None
    names, idx = s
    return names[idx[((y & 15) * 16 + (z & 15)) * 16 + (x & 15)]]


def layers(save, cx, cz, ys):
    legend = {}
    for y in ys:
        print('y', y)
        for z in range(16):
            row = ''
            for x in range(16):
                n = get(save, cx * 16 + x, y, cz * 16 + z) or '?'
                b = re.sub(r'\[.*', '', n).split(':')[-1]
                if b == 'air':
                    row += ' .'
                    continue
                if b not in legend:
                    legend[b] = chr(65 + len(legend)) if len(legend) < 26 else chr(97 + len(legend) - 26)
                row += ' ' + legend[b]
            print(row)
    print({v: k for k, v in legend.items()})


if __name__ == '__main__':
    save, cmd = sys.argv[1], sys.argv[2]
    a = [int(v) for v in sys.argv[3:]]
    if cmd == 'layers':
        layers(save, a[0], a[1], a[2:])
    elif cmd == 'column':
        for y in range(a[3], a[2] - 1, -1):
            print(y, get(save, a[0], y, a[1]))
