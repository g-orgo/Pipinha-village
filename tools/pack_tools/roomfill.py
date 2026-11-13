import sys, struct, zlib, glob, os, random, math
sys.path.insert(0, '/tmp')
from nbtmini import NBTReader
from nbtwrite import w_tag
from retrofit import decode_section, pal_name, encode_section

AIRY = {'minecraft:air','minecraft:cave_air','minecraft:void_air','minecraft:water',
 'minecraft:grass','minecraft:tall_grass','minecraft:fern','minecraft:large_fern',
 'minecraft:poppy','minecraft:dandelion','minecraft:torch','minecraft:wall_torch',
 'minecraft:redstone_torch','minecraft:redstone_wall_torch','minecraft:soul_torch','minecraft:soul_wall_torch',
 'minecraft:ladder','minecraft:vine','minecraft:glow_lichen','minecraft:snow',
 'minecraft:oak_pressure_plate','minecraft:stone_pressure_plate','minecraft:oak_button','minecraft:rail',
 'minecraft:lantern','minecraft:soul_lantern','minecraft:chain','minecraft:flower_pot',
 'minecraft:potted_cactus','minecraft:potted_poppy','minecraft:potted_dandelion','minecraft:potted_oak_sapling',
 'minecraft:cobweb','minecraft:scaffolding'}
NOT_STURDY_SUB = ('fence','wall','glass','leaves','_slab','_stairs','carpet','_bed','_door','trapdoor',
 'pane','bars','lantern','_pot','button','plate','rail','torch','ladder','vine','snow','chain')

def sturdy(name):
    if name in AIRY: return False
    n = name.split(':')[-1]
    return not any(s in n for s in NOT_STURDY_SUB)

ANCHORS = {'minecraft:furnace','minecraft:crafting_table','minecraft:bookshelf','minecraft:chest',
 'minecraft:enchanting_table','minecraft:brewing_stand','minecraft:anvil','minecraft:cauldron',
 'minecraft:lantern','minecraft:torch','minecraft:wall_torch','minecraft:ladder',
 'minecraft:oak_fence','minecraft:oak_pressure_plate','minecraft:potted_cactus','minecraft:potted_poppy',
 'minecraft:potted_dandelion','minecraft:potted_oak_sapling',
 'refurbished_furniture:oak_table','refurbished_furniture:oak_chair','farmersdelight:stove',
 'farmersdelight:cooking_pot','farmersdelight:oak_cabinet','farmersdelight:cutting_board',
 'furniture:oak_cabinet','furniture:oak_dresser','furniture:oak_desk','furniture:oak_desk_chair',
 'create:basin','create:depot','create:andesite_casing','refurbished_furniture:oak_kitchen_sink',
 'refurbished_furniture:oak_kitchen_cabinetry','refurbished_furniture:light_stove','refurbished_furniture:white_lamp',
 'furniture:lamp_white','farmersdelight:carrot_crate','farmersdelight:potato_crate'}

def E(name, props=None):
    e = {'Name': (8, name)}
    if props: e['Properties'] = (10, {k: (8, v) for k, v in props.items()})
    return e

KITCHEN = ['farmersdelight:stove','farmersdelight:cooking_pot','farmersdelight:oak_cabinet','furniture:oak_cabinet',
 'farmersdelight:cutting_board','farmersdelight:carrot_crate','farmersdelight:potato_crate','farmersdelight:beetroot_crate',
 'minecraft:furnace','minecraft:cauldron','refurbished_furniture:oak_kitchen_sink','refurbished_furniture:oak_kitchen_cabinetry']
BEDROOM = ['farmersdelight:oak_cabinet','furniture:oak_cabinet','furniture:oak_dresser','minecraft:bookshelf',
 'refurbished_furniture:white_lamp','furniture:lamp_white','minecraft:potted_poppy','minecraft:potted_dandelion']
BEDS = ['minecraft:white_bed','minecraft:light_gray_bed','minecraft:gray_bed']
LIVING = ['refurbished_furniture:oak_table','refurbished_furniture:oak_chair','minecraft:bookshelf','furniture:oak_desk',
 'furniture:oak_desk_chair','furniture:oak_dresser','refurbished_furniture:white_lamp','furniture:lamp_white',
 'minecraft:potted_poppy','minecraft:potted_dandelion','minecraft:lantern','farmersdelight:oak_cabinet']
WORKSHOP = ['minecraft:crafting_table','minecraft:furnace','create:andesite_casing','create:basin','create:depot',
 'minecraft:anvil','minecraft:smithing_table','minecraft:stonecutter','minecraft:grindstone',
 'minecraft:lantern','create:brass_casing']
STORAGE = ['farmersdelight:carrot_crate','farmersdelight:potato_crate','farmersdelight:beetroot_crate','farmersdelight:onion_crate',
 'farmersdelight:oak_cabinet','furniture:oak_cabinet','minecraft:chest','minecraft:crafting_table','minecraft:lantern']
THEMES = [('kitchen',KITCHEN,0.32),('bedroom',BEDROOM,0.30),('living',LIVING,0.30),('workshop',WORKSHOP,0.26),('storage',STORAGE,0.32)]
CARPETS = ['minecraft:white_carpet','minecraft:light_gray_carpet','minecraft:gray_carpet','minecraft:red_carpet','minecraft:blue_carpet','minecraft:green_carpet']

class Chunk:
    def __init__(self, root):
        self.root = root
        self.blocks = {}
        self.ladders = set()
        for s in root['sections'][1][1]:
            if 'block_states' not in dict(s): continue
            pal, idx = decode_section(s['block_states'][1])
            base = s['Y'][1]*16
            for pos, vi in enumerate(idx):
                nm = pal_name(pal[vi])
                if nm == 'minecraft:air': continue
                x = pos % 16; z = (pos//16) % 16; y = base + pos//256
                self.blocks[(x,y,z)] = nm
                if nm == 'minecraft:ladder': self.ladders.add((x,y,z))
    def get(self, x, y, z):
        if not (0 <= x < 16 and 0 <= z < 16): return 'minecraft:stone'
        return self.blocks.get((x,y,z), 'minecraft:air')
    def ceiling_within(self, x, y, z, dist=6):
        for dy in range(1, dist+1):
            if self.get(x, y+dy, z) not in AIRY: return True
        return False

def find_rooms(ch):
    anchors = [(x,y,z) for (x,y,z), nm in ch.blocks.items() if nm in ANCHORS]
    claimed = set()
    rooms = []
    for ax, ay, az in anchors:
        seeds = []
        for dx, dy, dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            c = (ax+dx, ay+dy, az+dz)
            if 0 <= c[0] < 16 and 0 <= c[2] < 16 and ch.blocks.get(c) is None and c not in claimed:
                if ch.ceiling_within(*c): seeds.append(c)
        if not seeds: continue
        room = set()
        stack = seeds[:6]
        while stack and len(room) < 600:
            c = stack.pop()
            if c in claimed or c in room: continue
            if ch.blocks.get(c) is not None: continue
            if not ch.ceiling_within(*c): continue
            room.add(c)
            x, y, z = c
            for dx, dy, dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                n = (x+dx, y+dy, z+dz)
                if 0 <= n[0] < 16 and 0 <= n[2] < 16 and n not in claimed and n not in room and ch.blocks.get(n) is None:
                    stack.append(n)
        if len(room) >= 8:
            claimed |= room
            rooms.append(room)
    return rooms

def free_floor(ch, room, out):
    res = []
    for c in room:
        if c in out or ch.blocks.get(c) is not None: continue
        if ch.blocks.get((c[0], c[1]+1, c[2])) is not None: continue
        if not sturdy(ch.get(c[0], c[1]-1, c[2])): continue
        if any((c[0]+dx, c[1], c[2]+dz) in ch.ladders or (c[0]+dx, c[1]+1, c[2]+dz) in ch.ladders
               for dx, dz in ((1,0),(-1,0),(0,1),(0,-1),(0,0))): continue
        res.append(c)
    return res

def furnish_room(ch, room, rng, out, stats):
    theme, items, dens = rng.choice(THEMES)
    floor = free_floor(ch, room, out)
    if len(floor) < 10: return
    fset = set(floor)
    rng.shuffle(floor)
    take = max(3, int(len(floor)*dens))
    # beds first (bedroom/living)
    if theme in ('bedroom','living'):
        nbeds = 1 if len(floor) < 22 else 2
        for _ in range(nbeds):
            done = False
            for c in rng.sample(floor, min(len(floor), 12)):
                h = (c[0], c[1], c[2]+1)
                if h in fset and h not in out and c not in out and ch.blocks.get(h) is None \
                   and sturdy(ch.get(h[0], h[1]-1, h[2])):
                    bn = rng.choice(BEDS)
                    out[(c[0], c[1], c[2]+1)] = E(bn, {'facing':'north','occupied':'false','part':'foot'})
                    out[c] = E(bn, {'facing':'north','occupied':'false','part':'head'})
                    stats['bed'] = stats.get('bed', 0)+1
                    done = True
                    break
            if not done: break
    for c in floor[:take]:
        if c in out or ch.blocks.get(c) is not None: continue
        nm = rng.choice(items)
        out[c] = E(nm)
        stats[theme] = stats.get(theme, 0)+1
        if nm.endswith('_table') and rng.random() < 0.45:
            for dx, dz in rng.sample([(1,0),(-1,0),(0,1),(0,-1)], 4):
                n2 = (c[0]+dx, c[1], c[2]+dz)
                if n2 in fset and n2 not in out and ch.blocks.get(n2) is None:
                    out[n2] = E('refurbished_furniture:oak_chair')
                    stats['chair_pair'] = stats.get('chair_pair', 0)+1
                    break
    if theme in ('living','bedroom') and len(floor) > 14 and rng.random() < 0.7:
        c0 = rng.choice(floor)
        cp = rng.choice(CARPETS)
        for dx in (0,1):
            for dz in (0,1):
                cc = (c0[0]+dx, c0[1], c0[2]+dz)
                if cc in fset and cc not in out and ch.blocks.get(cc) is None:
                    out[cc] = E(cp)
    if len(floor) > 20:
        c0 = rng.choice(floor)
        if c0 not in out and ch.blocks.get(c0) is None:
            out[c0] = E(rng.choice(['minecraft:lantern','refurbished_furniture:white_lamp','furniture:lamp_white']))

def process_chunk(root, rng, stats):
    ch = Chunk(root)
    rooms = find_rooms(ch)
    if not rooms:
        stats['chunks_empty'] = stats.get('chunks_empty', 0)+1
        return 0
    stats['rooms'] = stats.get('rooms', 0)+len(rooms)
    out = {}
    for r in rooms:
        furnish_room(ch, r, rng, out, stats)
    if not out: return 0
    if len(out) > 500:
        for k in rng.sample(sorted(out.keys()), len(out)-500):
            del out[k]
    secs = root['sections'][1][1]
    smap = {s['Y'][1]: s for s in secs}
    bysec = {}
    for (x, y, z), e in out.items():
        bysec.setdefault(math.floor(y/16), []).append((x, y, z, e))
    n = 0
    def key_of(e):
        return (pal_name(e), tuple(sorted((k, v[1]) for k, v in e.get('Properties', (10, {}))[1].items())) if 'Properties' in e else ())
    for sy, lst in bysec.items():
        s = smap.get(sy)
        if s is None or 'block_states' not in dict(s): continue
        pal, idx = decode_section(s['block_states'][1])
        seen = {}
        order = []
        for e in pal:
            k = key_of(e)
            if k not in seen: seen[k] = len(order); order.append(e)
        idx = list(idx)
        for x, y, z, e in lst:
            pos = ((y - sy*16)*16 + z)*16 + x
            if not (0 <= pos < 4096): continue
            if pal_name(pal[idx[pos]]) != 'minecraft:air': continue
            k = key_of(e)
            if k not in seen: seen[k] = len(order); order.append(e)
            idx[pos] = seen[k]
            n += 1
        used = sorted(set(idx))
        remap = {o: i for i, o in enumerate(used)}
        s['block_states'] = (10, encode_section([order[o] for o in used], [remap[v] for v in idx]))
    if n and 'Heightmaps' in root:
        del root['Heightmaps']
    stats['placed'] = stats.get('placed', 0)+n
    return n

def process_file(path, rng, stats, dry=False):
    with open(path, 'rb') as f:
        raw_all = f.read()
    hdr = raw_all[:8192]
    chunks = {}
    for i in range(1024):
        (loc,) = struct.unpack('>I', hdr[4*i:4*i+4])
        if loc == 0: continue
        off = (loc >> 8)*4096
        ln = struct.unpack('>I', raw_all[off:off+4])[0]
        comp = raw_all[off+4]
        payload = raw_all[off+5:off+4+ln]
        data = zlib.decompress(payload) if comp == 2 else payload
        root = NBTReader(data).read_tag()[2]
        chunks[i] = (comp, root)
    out_payloads = {}
    for i, (comp, root) in chunks.items():
        if process_chunk(root, rng, stats):
            out_payloads[i] = zlib.compress(w_tag('', 10, root), 6)
    if dry or not out_payloads:
        return len(chunks), False
    new_file = bytearray(8192)
    new_file[:8192] = hdr[:8192]
    cur = 2
    blobs = {}
    for i in range(1024):
        (loc,) = struct.unpack('>I', hdr[4*i:4*i+4])
        if loc == 0: continue
        if i in out_payloads:
            comp = 2; payload = out_payloads[i]
        else:
            off = (loc >> 8)*4096
            ln0 = struct.unpack('>I', raw_all[off:off+4])[0]
            comp = raw_all[off+4]
            payload = raw_all[off+5:off+4+ln0]
        blob = struct.pack('>I', len(payload)+1) + bytes([comp]) + payload
        nsec = (len(blob) + 4095)//4096
        blob += b'\x00'*(nsec*4096 - len(blob))
        blobs[i] = (cur, nsec, blob)
        cur += nsec
    for i, (sec, nsec, blob) in blobs.items():
        struct.pack_into('>I', new_file, 4*i, (sec << 8) | nsec)
    body = bytearray()
    for i, (sec, nsec, blob) in sorted(blobs.items(), key=lambda kv: kv[1][0]):
        body += blob
    with open(path, 'wb') as f:
        f.write(bytes(new_file) + bytes(body))
    return len(chunks), True

if __name__ == '__main__':
    import collections
    dry = '--dry' in sys.argv
    target = [a for a in sys.argv[1:] if not a.startswith('--')]
    rng = random.Random(20261003)
    stats = collections.Counter()
    for pat in target:
        for path in sorted(glob.glob(pat)):
            if os.path.getsize(path) == 0: continue
            try:
                n, wrote = process_file(path, rng, stats, dry)
            except Exception as e:
                import traceback; traceback.print_exc()
                print('ERROR', path, repr(e)); continue
            print(f'{"[dry] " if dry else ""}{path}: chunks={n} {"rewritten" if wrote else "skipped"}')
    print('STATS:', dict(stats))
