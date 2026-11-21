"""Finds and lowers structures that generated floating above the ground (game CLOSED for fix).

Why: jigsaw structures from other mods (Moog's Voyager, Better Archeology, Society...) pick their height
from the natural terrain, but Lost Cities flattens the town to its own street level afterwards. Inside a
town the structure stays 2 to 5 blocks above the ground. New chunks are covered by `avoidStructures` in
lostcities-server.toml; this tool fixes chunks that already exist.

Usage (from the instance root):
  python3 -I tools/pack_tools/fix_floating_structures.py "saves/<save>" scan
  python3 -I tools/pack_tools/fix_floating_structures.py "saves/<save>" fix [--dry] [--near x,z,radius]
A structure is floating when most columns of its footprint have air under the lowest block. fix moves
every template cell of its pieces down by the gap that 80% of its base columns have (0 when it leans
on the hillside at the town edge), fills what is still open under it
with dirt, moves block entities and entities with it, shifts the stored start (so chunks generated later
place the rest at the new height), drops heightmaps, relights and marks POI sections for a rescan.
"""
import glob, gzip, io, os, re, subprocess, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from retrofit_hedges import read_region, write_region, decode, encode

PLACED = ('minecraft:features', 'minecraft:initialize_light', 'minecraft:light', 'minecraft:spawn', 'minecraft:full')
SOFT = ('air', 'cave_air', 'void_air', 'short_grass', 'tall_grass', 'fern', 'large_fern', 'snow', 'dandelion', 'poppy',
        'cornflower', 'azure_bluet', 'oxeye_daisy', 'allium', 'blue_orchid', 'dead_bush', 'sweet_berry_bush')
MEANT_TO_FLOAT = {'mvs:floating_islands', 'botania:exploration_island'}
DIRT = {'Name': (8, 'minecraft:dirt')}
AIR = {'Name': (8, 'minecraft:air')}


class World:
    def __init__(self, save):
        self.save, self.files, self.secs, self.dirty = save, {}, {}, set()

    def chunk(self, kind, cx, cz):
        p = os.path.join(self.save, kind, 'r.%d.%d.mca' % (cx >> 5, cz >> 5))
        if p not in self.files:
            self.files[p] = read_region(p) if os.path.exists(p) else (b'', {})
        return p, (cx & 31) + (cz & 31) * 32, self.files[p][1].get((cx & 31) + (cz & 31) * 32)

    def placed(self, cx, cz):
        root = self.chunk('region', cx, cz)[2]
        return bool(root) and root.get('Status', (8, ''))[1] in PLACED

    def sec(self, x, y, z):
        key = (x >> 4, y >> 4, z >> 4)
        if key not in self.secs:
            root, hit = self.chunk('region', x >> 4, z >> 4)[2], None
            for s in root['sections'][1][1]:
                if s['Y'][1] == y >> 4 and 'block_states' in s:
                    pal, idx = decode(s['block_states'][1])
                    hit = [s, list(pal), list(idx)]
            self.secs[key] = hit
        return self.secs[key]

    def get(self, x, y, z):
        s = self.sec(x, y, z)
        return s[1][s[2][((y & 15) * 16 + (z & 15)) * 16 + (x & 15)]] if s else AIR

    def set(self, x, y, z, entry):
        s = self.sec(x, y, z)
        if s is None:
            return
        if entry not in s[1]:
            s[1].append(entry)
        s[2][((y & 15) * 16 + (z & 15)) * 16 + (x & 15)] = s[1].index(entry)
        self.dirty.add(self.chunk('region', x >> 4, z >> 4)[:2])
        self.secs[(x >> 4, y >> 4, z >> 4)] = s

    def flush(self):
        for (cx, sy, cz), s in self.secs.items():
            p, i, root = self.chunk('region', cx, cz)
            if s and (p, i) in self.dirty:
                used = sorted(set(s[2]))
                remap = {o: k for k, o in enumerate(used)}
                s[0]['block_states'] = (10, encode([s[1][o] for o in used], [remap[v] for v in s[2]]))
                root.pop('Heightmaps', None)
                root['isLightOn'] = (1, 0)
        by_file = {}
        for p, i in self.dirty:
            by_file.setdefault(p, {})[i] = self.files[p][1][i]
        for p, ch in by_file.items():
            write_region(p, self.files[p][0], ch)
        return len(self.dirty)


def solid(name):
    """Template block that stays as itself (air and jigsaw blocks become something else)."""
    return name.split(':')[-1] not in ('air', 'jigsaw', 'structure_void')


def soft(entry):
    return entry['Name'][1].split(':')[-1] in SOFT


def starts(w):
    for p in sorted(glob.glob(os.path.join(w.save, 'region', 'r.*.mca'))):
        rx, rz = map(int, re.findall(r'-?\d+', os.path.basename(p))[:2])
        w.chunk('region', rx * 32, rz * 32)
        for i, root in list(w.files[p][1].items()):
            for sid, (_, st) in root.get('structures', (10, {}))[1].get('starts', (10, {}))[1].items():
                if st.get('id', (8, 'INVALID'))[1] != 'INVALID' and st.get('Children', (9, (0, [])))[1][1]:
                    yield p, i, sid, st


_index = None


def template(loc):
    """Blocks of a structure template ({(x,y,z): name}) looked up in the mod jars and kubejs/data."""
    global _index
    if _index is None:
        _index = {}
        inst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
        def add(zf, src):
            for n in zf.namelist():
                m = re.match(r'data/([^/]+)/structures?/(.+)\.nbt$', n)
                if m:
                    _index['%s:%s' % m.groups()] = (src, n)
                elif n.startswith('META-INF/jarjar/') and n.endswith('.jar'):
                    add(zipfile.ZipFile(io.BytesIO(zf.read(n))), (src, n))
        for jar in glob.glob(os.path.join(inst, 'mods', '*.jar')):
            add(zipfile.ZipFile(jar), jar)
        for f in glob.glob(os.path.join(inst, 'kubejs', 'data', '*', 'structure*', '**', '*.nbt'), recursive=True):
            m = re.search(r'kubejs/data/([^/]+)/structures?/(.+)\.nbt$', f)
            _index['%s:%s' % m.groups()] = (None, f)
    if loc not in _index:
        return None
    src, name = _index[loc]
    def open_src(s):
        return zipfile.ZipFile(s) if isinstance(s, str) else zipfile.ZipFile(io.BytesIO(open_src(s[0]).read(s[1])))
    raw = open(name, 'rb').read() if src is None else open_src(src).read(name)
    t = NBTReader(gzip.decompress(raw)).read_tag()[2]
    names = [p['Name'][1] for p in t['palette'][1][1]] if 'palette' in t else []
    return {tuple(b['pos'][1][1]): names[b['state'][1]] for b in t['blocks'][1][1]} if names else {}


ROT = {'NONE': lambda x, z: (x, z), 'CLOCKWISE_90': lambda x, z: (-z, x),
       'CLOCKWISE_180': lambda x, z: (-x, -z), 'COUNTERCLOCKWISE_90': lambda x, z: (z, -x)}


def piece_cells(w, pc):
    """World cells of a jigsaw piece from its template: the candidate (versioned elements list one per
    game version) whose rotated size fits the BB and whose blocks best match the save."""
    pe = pc.get('pool_element', (10, {}))[1]
    if 'PosY' in pc and 'location' not in pe:
        return {}  # feature or empty element: nothing of its own to move
    if 'PosY' not in pc:
        return None
    locs = [pe['location'][1]] + [v[1] for v in pe.get('locations', (10, {}))[1].values()]
    best, rot = (0, None), ROT[pc['rotation'][1]]
    x0, y0, z0, x1, y1, z1 = pc['BB'][1]
    for loc in dict.fromkeys(locs):
        blocks = template(loc)
        if blocks == {}:
            return {}  # entity-only piece (mob markers): the entities move with the house cells
        if not blocks:
            continue
        cells = {}
        for (tx, ty, tz), n in blocks.items():
            dx, dz = rot(tx, tz)
            cells[(pc['PosX'][1] + dx, pc['PosY'][1] + ty, pc['PosZ'][1] + dz)] = n
        xs, ys, zs = zip(*cells)
        if (min(xs), min(ys), min(zs)) < (x0, y0, z0) or max(xs) > x1 or max(ys) > y1 or max(zs) > z1:
            continue
        seen = [(c, n) for c, n in cells.items() if solid(n) and w.placed(c[0] >> 4, c[2] >> 4)]
        score = sum(w.get(*c)['Name'][1] == n for c, n in seen) / len(seen) if seen else 0.5
        if score > best[0]:
            best = (score, cells)
    return best[1] if best[0] >= 0.5 else None


def measure(w, st):
    """Gap of air under the lowest template block of each column. cells = every template cell of the
    start (air included, since the template placed that air); None when a piece has no template."""
    gaps, cells = [], {}
    for pc in st['Children'][1][1]:
        pcells = piece_cells(w, pc)
        if pcells is None:
            return [], None
        cells.update(pcells)
        bottoms = {}
        for (x, y, z), n in pcells.items():
            if solid(n) and w.placed(x >> 4, z >> 4) and y < bottoms.get((x, z), 1 << 20):
                bottoms[(x, z)] = y
        floor = min(bottoms.values(), default=0) + 1
        for (x, z), bottom in bottoms.items():
            if bottom > floor:
                continue  # eaves, balconies, roofs: not the base, never filled under
            g = 0
            while g < 40 and soft(w.get(x, bottom - g - 1, z)):
                g += 1
            gaps.append((x, z, bottom, g))
    return gaps, set(cells)


def lower(w, st, gaps, cells, d):
    if d:
        snap = {c: w.get(*c) for c in cells if w.placed(c[0] >> 4, c[2] >> 4)}
        dst = {(x, y - d, z) for x, y, z in snap}
        for (x, y, z), e in sorted(snap.items(), key=lambda t: t[0][1]):
            w.set(x, y - d, z, e)
        for c in snap:
            if c not in dst:
                w.set(*c, AIR)
        moved = {(x >> 4, z >> 4) for x, _, z in snap}
        for cx, cz in moved:
            root = w.chunk('region', cx, cz)[2]
            be = root.get('block_entities', (9, (0, [])))[1][1]
            keep = [e for e in be if (e['x'][1], e['y'][1], e['z'][1]) not in dst - set(snap)]
            for e in keep:
                if (e['x'][1], e['y'][1], e['z'][1]) in snap:
                    e['y'] = (3, e['y'][1] - d)
            root['block_entities'] = (9, (10, keep) if keep else (0, []))
            shift_entities(w, cx, cz, cells, d)
            poi_rescan(w, cx, cz)
        for pc in st['Children'][1][1]:
            pc['BB'] = (11, [v - d if k in (1, 4) else v for k, v in enumerate(pc['BB'][1])])
            for key in ('PosY', 'TPY'):
                if key in pc:
                    pc[key] = (3, pc[key][1] - d)
    for x, z, bottom, g in gaps:
        for y in range(bottom - g, bottom - d):  # what is still open under the base after the move
            w.set(x, y, z, DIRT)


def shift_entities(w, cx, cz, cells, d):
    p, i, root = w.chunk('entities', cx, cz)
    if not root:
        return
    for e in root.get('Entities', (9, (0, [])))[1][1]:
        x, y, z = e['Pos'][1][1]
        if (int(x // 1), int(y // 1), int(z // 1)) in cells:
            e['Pos'] = (9, (6, [x, y - d, z]))
            if 'TileY' in e:
                e['TileY'] = (3, e['TileY'][1] - d)
            w.dirty.add((p, i))


def poi_rescan(w, cx, cz):
    p, i, root = w.chunk('poi', cx, cz)
    if root and 'Sections' in root:
        for sec in root['Sections'][1].values():
            sec[1]['Valid'] = (1, 0)
        w.dirty.add((p, i))


def main():
    save, cmd = sys.argv[1], sys.argv[2]
    near = [int(v) for v in sys.argv[sys.argv.index('--near') + 1].split(',')] if '--near' in sys.argv else None
    dry = cmd == 'scan' or '--dry' in sys.argv
    if not dry and subprocess.run(['pgrep', '-x', 'java'], capture_output=True).returncode == 0:
        sys.exit('game is running: close it first')
    w, todo, untemplated = World(save), [], set()
    for p, i, sid, st in list(starts(w)):
        bb = st['Children'][1][1][0]['BB'][1]
        if near and max(abs(bb[0] - near[0]), abs(bb[2] - near[1])) > near[2]:
            continue
        if sid in MEANT_TO_FLOAT:
            continue
        gaps, cells = measure(w, st)
        if cells is None:
            untemplated.add(sid)
            continue
        hanging = sorted(g for _, _, _, g in gaps)
        if len(hanging) < 4 or sum(g > 0 for g in hanging) < len(hanging) / 2:
            continue
        d = hanging[len(hanging) // 5]  # gap shared by 80% of the base: all over the town -> moved down
        todo.append((p, i, st, gaps, cells, d))
        print('%-45s at %d,%d,%d  columns %d  gap min/med/max %d/%d/%d  -> down %d, fill %d' % (
            sid, bb[0], bb[1], bb[2], len(hanging), hanging[0], hanging[len(hanging) // 2], hanging[-1],
            d, sum(max(0, g - d) for g in hanging)))
    print('%d floating structures; not measured (no template piece): %s' % (len(todo), ' '.join(sorted(untemplated))))
    if dry:
        return
    for p, i, st, gaps, cells, d in todo:
        lower(w, st, gaps, cells, d)
        w.dirty.add((p, i))
    print('chunks written:', w.flush())


if __name__ == '__main__':
    main()
