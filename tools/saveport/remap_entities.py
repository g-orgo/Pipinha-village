#!/usr/bin/env python3
"""Rename entity ids inside a save's entities/*.mca (passengers included), keeping every other tag.

Meadow 1.21 dropped meadow:wooly_sheep, so those entities would vanish when the world loads.
Renaming them to minecraft:sheep keeps position, name, owner data and the Society affection
(KubeJSPersistentData), which KubeJS 7 still reads under the same key.

Usage: remap_entities.py <save> [--dry]   (the game must be closed)
"""
import glob
import os
import sys
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pack_tools'))
from nbtmini import NBTReader  # noqa: E402
from regen_chunks import chunks_of, rewrite, _enc_str, _enc_payload, _val  # noqa: E402

ENTITY_MAP = {
    'meadow:wooly_sheep': 'minecraft:sheep',
}


def remap(e, hits):
    """Renames e and its passengers in place; appends 'old@x,y,z' to hits."""
    eid = _val(e.get('id', (8, '')))
    if eid in ENTITY_MAP:
        e['id'] = (8, ENTITY_MAP[eid])
        x, y, z = (round(v) for v in e['Pos'][1][1])
        hits.append('%s@%d,%d,%d' % (eid, x, y, z))
    for p in _val(e.get('Passengers', (9, (10, []))))[1]:
        remap(p, hits)


def main():
    save, dry = sys.argv[1], '--dry' in sys.argv
    total = []
    for path in sorted(glob.glob(os.path.join(save, 'entities', '*.mca'))):
        if os.path.getsize(path) < 8192:
            continue
        raw = open(path, 'rb').read()
        repl = {}
        for i, off, ln in chunks_of(raw):
            if raw[off + 4] != 2:
                continue
            data = zlib.decompress(raw[off + 5:off + 4 + ln])
            if not any(k.encode() in data for k in ENTITY_MAP):
                continue
            name, tid, root = NBTReader(data).read_tag()
            hits = []
            for e in root.get('Entities', (9, (10, [])))[1][1]:
                remap(e, hits)
            if hits:
                comp = zlib.compress(bytes([tid]) + _enc_str(name or '') + _enc_payload(tid, root))
                repl[i] = len(comp + b'x').to_bytes(4, 'big') + bytes([2]) + comp
                total += hits
        if repl and not dry:
            rewrite(path, raw, set(), repl)
    for h in total:
        print(('[dry] ' if dry else '') + 'renomeado ' + h)
    print(('[dry] ' if dry else '') + f'entidades renomeadas: {len(total)}')


if __name__ == '__main__':
    main()
