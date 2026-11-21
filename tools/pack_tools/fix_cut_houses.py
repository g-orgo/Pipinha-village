"""Finds and clears buildings cut in half at the edge of kept chunks (game CLOSED for clear).

Why: a strict regen keeps only the FTB claims (and the 5x5 around the origin). When the new generation
has a different layout (new seed, new town pipeline), Lost Cities still places 2x2 multibuildings around
the kept chunks, and the parts that fall inside a kept chunk never generate: the piece left outside is
a house cut in half. It cannot be completed without overwriting the claim, so the piece becomes an
empty grass lot at street level, like the empty lots of the towns.

Usage (from the instance root):
  python3 -I sunlit_tools/fix_cut_houses.py "saves/<save>" scan [--png out.png]
  python3 -I sunlit_tools/fix_cut_houses.py "saves/<save>" clear <cx,cz> [<cx,cz> ...]
          [--ground 71] [--box x0,z0,x1,z1] [--dry]
scan lists the faces of non-kept chunks touching a kept chunk with construction above street level on
3+ heights (candidates: a whole building just leaning on the border also shows up, so check the PNG).
clear empties everything above --ground inside the chunk (or the local --box, inclusive), keeps short
plants, turns the ground into grass, drops the block entities there and makes the game rebuild the
heightmaps and relight the chunk. Only region/ is written; entities/ and poi/ are not touched.
Every cleared chunk is recorded in lotes_limpos.tsv (save name, chunk): regen_chunks.py keeps those
lots, since they have no claim and the seed would generate the cut house there again.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrofit_hedges import read_region, write_region, decode, encode

NATURAL = ('stone', 'dirt', 'grass_block', 'gravel', 'sand', 'clay', 'podzol', 'water', 'lava', 'snow',
           'deepslate', 'andesite', 'diorite', 'granite', 'tuff', 'calcite', 'bedrock', '_ore', 'leaves',
           'grass', 'fern', 'flower', 'poppy', 'dandelion', 'air')
PLANTS = ('grass', 'tall_grass', 'fern', 'large_fern', 'poppy', 'dandelion', 'snow')


def base(name):
    return name.split(':', 1)[-1]


def natural(name):
    b = base(name)
    return b == 'grass_block' or b == 'coarse_dirt' or any(k in b for k in NATURAL) and 'brick' not in b \
        and 'polished' not in b and 'stairs' not in b and 'slab' not in b and 'wall' not in b


def kept_chunks(save):
    keep = {(x, z) for x in range(-2, 3) for z in range(-2, 3)}
    d = os.path.join(save, 'ftbchunks')
    for f in os.listdir(d) if os.path.isdir(d) else []:
        if f.endswith('.snbt'):
            txt = open(os.path.join(d, f)).read()
            keep |= {(int(a), int(b)) for a, b in re.findall(r'x: (-?\d+), z: (-?\d+), time', txt)}
    return keep


class Save:
    def __init__(self, save):
        self.save, self.regions = save, {}

    def region(self, cx, cz):
        p = os.path.join(self.save, 'region', 'r.%d.%d.mca' % (cx >> 5, cz >> 5))
        if p not in self.regions:
            self.regions[p] = read_region(p) if os.path.exists(p) else (b'', {})
        return p, self.regions[p]

    def root(self, cx, cz):
        return self.region(cx, cz)[1][1].get((cx & 31) + (cz & 31) * 32)

    def block(self, root, x, y, z):
        for s in root['sections'][1][1]:
            if s['Y'][1] == y >> 4 and 'block_states' in s:
                pal, idx = decode(s['block_states'][1])
                return pal[idx[((y & 15) * 16 + (z & 15)) * 16 + (x & 15)]]['Name'][1]
        return 'minecraft:air'


def scan(save, png):
    sv, keep = Save(save), kept_chunks(save)
    found = []
    for a in sorted(keep):
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b = (a[0] + dx, a[1] + dz)
            root = None if b in keep else sv.root(*b)
            if not root:
                continue
            cells = set()
            for t in range(16):
                lx, lz = {(1, 0): (0, t), (-1, 0): (15, t), (0, 1): (t, 0), (0, -1): (t, 15)}[(dx, dz)]
                for y in range(72, 120):
                    if not natural(sv.block(root, lx, y, lz)):
                        cells.add((t, y))
            levels = {y for _, y in cells}
            if len(levels) >= 3:
                found.append((b, a, len(cells), min(levels), max(levels)))
                print('candidate %d,%d (touches kept %d,%d): %d cells, y %d-%d' % (b + a + (len(cells), min(levels), max(levels))))
    if not found:
        print('no candidate')
    if png and found:
        from PIL import Image, ImageDraw
        import hashlib
        S, Y0, Y1 = 4, 64, 100
        PW, PH = 16 * S, (Y1 - Y0 + 1) * S
        img = Image.new('RGB', (len(found) * (2 * PW + 14), PH + 14), (15, 15, 25))
        d = ImageDraw.Draw(img)
        for k, (b, a, *_r) in enumerate(found):
            ox = k * (2 * PW + 14)
            d.text((ox, 1), '%d,%d|%d,%d' % (b + a), fill=(255, 255, 0))
            dx, dz = b[0] - a[0], b[1] - a[1]
            # left: face of the candidate on the border; right: face of the kept chunk on the same border
            for j, (c, edge) in enumerate(((b, 0), (a, 15))):
                root = sv.root(*c)
                for t in range(16):
                    e = edge if (dx, dz) in ((1, 0), (0, 1)) else 15 - edge
                    lx, lz = (e, t) if dx else (t, e)
                    for y in range(Y0, Y1 + 1):
                        n = sv.block(root, lx, y, lz)
                        if base(n) in ('air', 'cave_air'):
                            continue
                        h = hashlib.md5(base(n).encode()).digest()
                        px, py = ox + j * (PW + 4) + t * S, 14 + (Y1 - y) * S
                        d.rectangle([px, py, px + S - 1, py + S - 1], fill=(h[0], h[1], h[2]))
        img.save(png)
        print('png', png)


def clear(save, targets, ground, box, dry):
    if subprocess.run('pgrep -a java | grep -qi singleplayer', shell=True).returncode == 0:
        sys.exit('game is running: close it first')
    sv, changed = Save(save), {}
    x0, z0, x1, z1 = box
    for cx, cz in targets:
        path, (raw, chunks) = sv.region(cx, cz)
        i = (cx & 31) + (cz & 31) * 32
        root = chunks.get(i)
        if not root:
            print('chunk %d,%d not in the save' % (cx, cz))
            continue
        removed, grassed, gone = 0, 0, set()
        for s in root['sections'][1][1]:
            sy = s['Y'][1] * 16
            if 'block_states' not in s or sy + 15 < ground:
                continue
            pal, idx = decode(s['block_states'][1])
            pal, idx = list(pal), list(idx)

            def pid(name):
                for k, e in enumerate(pal):
                    if e['Name'][1] == name and 'Properties' not in e:
                        return k
                pal.append({'Name': (8, name)})
                return len(pal) - 1
            for lx in range(x0, x1 + 1):
                for lz in range(z0, z1 + 1):
                    for y in range(max(sy, ground), sy + 16):
                        p = ((y - sy) * 16 + lz) * 16 + lx
                        n = pal[idx[p]]['Name'][1]
                        if y == ground:
                            if base(n) not in ('grass_block', 'water'):
                                idx[p] = pid('minecraft:grass_block')
                                grassed += 1
                        elif base(n) not in ('air', 'cave_air') + PLANTS:
                            idx[p] = pid('minecraft:air')
                            removed += 1
                            gone.add((cx * 16 + lx, y, cz * 16 + lz))
            used = sorted(set(idx))
            remap = {o: k for k, o in enumerate(used)}
            s['block_states'] = (10, encode([pal[o] for o in used], [remap[v] for v in idx]))
        be = root.get('block_entities')
        if be:
            keep = [e for e in be[1][1] if (e['x'][1], e['y'][1], e['z'][1]) not in gone]
            print('  block entities removed:', len(be[1][1]) - len(keep))
            root['block_entities'] = (9, (10, keep) if keep else (0, []))
        root.pop('Heightmaps', None)  # rebuilt on load
        root['isLightOn'] = (1, 0)  # relit on load (sky light under the old roof)
        print('%s chunk %d,%d: %d blocks cleared above y=%d, %d ground blocks to grass' % (
            '[dry]' if dry else '', cx, cz, removed, ground, grassed))
        changed.setdefault(path, (raw, {}))[1][i] = root
    if not dry:
        for path, (raw, ch) in changed.items():
            write_region(path, raw, ch)
            print('written', os.path.basename(path), len(read_region(path)[1]), 'chunks readable')
        record_lots(save, [c for c in targets if sv.root(*c)])


LOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lotes_limpos.tsv')


def save_name(save):
    return os.path.basename(os.path.normpath(save))


def cleared_lots(save):
    """Chunks already turned into grass lots in this save; the strict regen keeps them, otherwise the
    seed generates the cut house there again (they have no claim)."""
    lots = set()
    if os.path.exists(LOTS):
        for line in open(LOTS, encoding='utf-8'):
            parts = line.rstrip('\n').split('\t')
            if len(parts) >= 2 and parts[0] == save_name(save) and re.fullmatch(r'-?\d+,-?\d+', parts[1]):
                lots.add(tuple(map(int, parts[1].split(','))))
    return lots


def record_lots(save, targets):
    new = [c for c in targets if c not in cleared_lots(save)]
    if new:
        with open(LOTS, 'a', encoding='utf-8') as f:
            for cx, cz in new:
                f.write('%s\t%d,%d\n' % (save_name(save), cx, cz))
        print('recorded in lotes_limpos.tsv:', ' '.join('%d,%d' % c for c in new))


def main():
    save, cmd = sys.argv[1], sys.argv[2]
    arg = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    if cmd == 'scan':
        scan(save, arg('--png', None))
    elif cmd == 'clear':
        targets = [tuple(map(int, a.split(','))) for a in sys.argv[3:] if re.fullmatch(r'-?\d+,-?\d+', a)]
        box = tuple(map(int, arg('--box', '0,0,15,15').split(',')))
        clear(save, targets, int(arg('--ground', '71')), box, '--dry' in sys.argv)
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
