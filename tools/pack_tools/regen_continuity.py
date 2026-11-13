"""Keeps buildings whole during a partial regen.

A Lost Cities multibuilding (or any build) can span several chunks. If regen_chunks.py keeps one
of its chunks and deletes the neighbour, the neighbour is regenerated with the current layout and
the old building is left cut in half. This module grows the kept set: whenever built blocks of a
kept chunk touch built blocks of a neighbour across their shared border, on several heights (a
wall, not a flat road), the neighbour is kept too, transitively.
"""
import os, struct, zlib
from nbtmini import NBTReader

BUILT = ('planks', '_stairs', '_slab', 'brick', 'glass', '_pane', 'door', 'terracotta', 'concrete',
         'wool', 'stripped_', 'shingle', 'tile', 'cobblestone', 'polished_', 'smooth_', 'chiseled_',
         'cut_', 'carpet', 'bookshelf', 'beam', 'roof', 'siding', 'timber', 'thatch', 'window',
         'shutter', 'column', 'pillar', 'quartz_block', 'mossy_stone_brick')
NOT_BUILT = ('leaves', 'fence', 'path', '_ore', 'sapling', 'infested')
MIN_PAIRS, MIN_LEVELS = 6, 3


def is_built(name):
    n = name.split(':', 1)[-1]
    if any(k in n for k in NOT_BUILT):
        return False
    if n.endswith('_log') or n.endswith('_wood'):
        return n.startswith('stripped_')
    return any(k in n for k in BUILT)


class Chunks:
    """Lazy reader of region chunks (pre-deletion data) with border-column extraction."""

    def __init__(self, save):
        self.dir = os.path.join(save, 'region')
        self.raw, self.cache = {}, {}

    def _nbt(self, cx, cz):
        name = 'r.%d.%d.mca' % (cx >> 5, cz >> 5)
        if name not in self.raw:
            p = os.path.join(self.dir, name)
            self.raw[name] = open(p, 'rb').read() if os.path.exists(p) and os.path.getsize(p) >= 8192 else b''
        raw = self.raw[name]
        if not raw:
            return None
        i = (cz & 31) * 32 + (cx & 31)
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if not loc:
            return None
        off = (loc >> 8) * 4096
        ln = struct.unpack('>I', raw[off:off + 4])[0]
        if raw[off + 4] != 2:
            return None
        return NBTReader(zlib.decompress(raw[off + 5:off + 4 + ln])).read_tag()[2]

    def borders(self, cx, cz):
        """{side: set((y, t))} of built blocks on each edge column; side in W(x=0) E(x=15) N(z=0) S(z=15),
        t = the coordinate along the edge."""
        key = (cx, cz)
        if key in self.cache:
            return self.cache[key]
        out = {'W': set(), 'E': set(), 'N': set(), 'S': set()}
        d = self._nbt(cx, cz)
        for sec in (d.get('sections', (9, (10, [])))[1][1] if d else []):
            bs = sec.get('block_states', (10, {}))[1]
            pal = bs.get('palette')
            if not pal:
                continue
            pal = [is_built(e['Name'][1]) for e in pal[1][1]]
            if not any(pal):
                continue
            sy = sec['Y'][1] * 16
            if len(pal) == 1:
                for y in range(16):
                    for t in range(16):
                        for s in out:
                            out[s].add((sy + y, t))
                continue
            data = bs['data'][1]
            bits = max(4, (len(pal) - 1).bit_length())
            per = 64 // bits
            mask = (1 << bits) - 1

            def at(x, y, z):
                idx = (y * 16 + z) * 16 + x
                v = data[idx // per] & 0xFFFFFFFFFFFFFFFF
                return pal[(v >> ((idx % per) * bits)) & mask]

            for y in range(16):
                for t in range(16):
                    if at(0, y, t):
                        out['W'].add((sy + y, t))
                    if at(15, y, t):
                        out['E'].add((sy + y, t))
                    if at(t, y, 0):
                        out['N'].add((sy + y, t))
                    if at(t, y, 15):
                        out['S'].add((sy + y, t))
        self.cache[key] = out
        return out

    def joined(self, a, b):
        """True when a building crosses the border between adjacent chunks a and b."""
        dx, dz = b[0] - a[0], b[1] - a[1]
        sa, sb = {(1, 0): ('E', 'W'), (-1, 0): ('W', 'E'), (0, 1): ('S', 'N'), (0, -1): ('N', 'S')}[(dx, dz)]
        pairs = self.borders(*a)[sa] & self.borders(*b)[sb]
        return len(pairs) >= MIN_PAIRS and len({y for y, _ in pairs}) >= MIN_LEVELS


def grow(save, keep, exists):
    """Adds to keep (in place) every chunk joined to a kept one by a building, transitively.
    exists(c) tells whether chunk c is present in the region files. Returns {added chunk: source}."""
    ch, added = Chunks(save), {}
    todo = [c for c in keep if exists(c)]
    while todo:
        a = todo.pop()
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b = (a[0] + d[0], a[1] + d[1])
            if b in keep or not exists(b):
                continue
            if ch.joined(a, b):
                keep.add(b)
                added[b] = a
                todo.append(b)
    return added
