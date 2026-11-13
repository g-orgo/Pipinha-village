import sys, struct, zlib, glob, os, random, math, shutil
sys.path.insert(0, '/tmp')
from nbtmini import NBTReader
from nbtwrite import w_tag

NON_SOLID = {
 'minecraft:air','minecraft:cave_air','minecraft:void_air','minecraft:water','minecraft:lava',
 'minecraft:cobweb','minecraft:torch','minecraft:wall_torch','minecraft:redstone_torch','minecraft:redstone_wall_torch',
 'minecraft:soul_torch','minecraft:soul_wall_torch','minecraft:ladder','minecraft:vine','minecraft:glow_lichen',
 'minecraft:oak_fence','minecraft:spruce_fence','minecraft:birch_fence','minecraft:jungle_fence','minecraft:acacia_fence',
 'minecraft:dark_oak_fence','minecraft:mangrove_fence','minecraft:cherry_fence','minecraft:bamboo_fence','minecraft:crimson_fence',
 'minecraft:warped_fence','minecraft:cobblestone_wall','minecraft:oak_fence_gate','minecraft:glass','minecraft:white_stained_glass',
 'minecraft:gray_stained_glass','minecraft:light_blue_stained_glass','minecraft:blue_stained_glass','minecraft:glass_pane',
 'minecraft:oak_leaves','minecraft:spruce_leaves','minecraft:birch_leaves','minecraft:jungle_leaves','minecraft:acacia_leaves',
 'minecraft:dark_oak_leaves','minecraft:azalea_leaves','minecraft:flowering_azalea_leaves','minecraft:mangrove_leaves',
 'minecraft:grass','minecraft:tall_grass','minecraft:fern','minecraft:large_fern','minecraft:poppy','minecraft:dandelion',
 'minecraft:oak_sapling','minecraft:spruce_sapling','minecraft:birch_sapling','minecraft:acacia_sapling',
 'minecraft:oak_pressure_plate','minecraft:stone_pressure_plate','minecraft:oak_button','minecraft:snow','minecraft:carpet',
 'minecraft:white_carpet','minecraft:rail','minecraft:iron_bars','minecraft:chain','minecraft:lantern','minecraft:soul_lantern',
 'minecraft:potted_cactus','minecraft:potted_poppy','minecraft:potted_dandelion','minecraft:potted_oak_sapling',
 'minecraft:cauldron','minecraft:brewing_stand','minecraft:anvil','minecraft:bookshelf','minecraft:crafting_table',
}
# blocks that can float mid-air (dust) -> always air; others below only checked vs NON_SOLID
FURNITURE = [
 (50, {'Name': (8, 'minecraft:air')}),
 (9,  {'Name': (8, 'refurbished_furniture:oak_table')}),
 (7,  {'Name': (8, 'refurbished_furniture:oak_chair')}),
 (8,  {'Name': (8, 'minecraft:bookshelf')}),
 (6,  {'Name': (8, 'minecraft:crafting_table')}),
 (6,  {'Name': (8, 'minecraft:furnace')}),
 (5,  {'Name': (8, 'farmersdelight:oak_cabinet')}),
 (4,  {'Name': (8, 'furniture:oak_cabinet')}),
 (5,  {'Name': (8, 'minecraft:lantern')}),
]
FW = [w for w,_ in FURNITURE]; FTOT = sum(FW)

def pick(rng):
    r = rng.random()*FTOT; acc = 0
    for w, e in FURNITURE:
        acc += w
        if r < acc: return e
    return FURNITURE[0][1]

def pal_name(entry):
    return entry.get('Name', (0, ''))[1]

def decode_section(bs):
    pal = bs['palette'][1][1]
    n = len(pal)
    bpe = max(4, math.ceil(math.log2(n)) if n > 1 else 4)
    per = 64 // bpe
    mask = (1 << bpe) - 1
    if 'data' in bs:
        longs = [(v & 0xFFFFFFFFFFFFFFFF) for v in bs['data'][1]]
    else:
        longs = [0]*((4096 + per - 1)//per)
    idx = [0]*4096
    for pos in range(4096):
        li, off = divmod(pos, per)
        idx[pos] = (longs[li] >> (off*bpe)) & mask if li < len(longs) else 0
    return pal, idx

def encode_section(pal, idx):
    n = len(pal)
    if n == 1:
        return {'palette': (9, (10, pal))}
    bpe = max(4, math.ceil(math.log2(n)))
    per = 64 // bpe
    nlongs = (4096 + per - 1)//per
    longs = [0]*nlongs
    for pos, v in enumerate(idx):
        li, off = divmod(pos, per)
        longs[li] |= (v & ((1<<bpe)-1)) << (off*bpe)
    return {'palette': (9, (10, pal)), 'data': (12, longs)}

def process_chunk(root, rng):
    secs = root['sections'][1][1]
    # build y->section map
    smap = {}
    for s in secs:
        smap[s['Y'][1]] = s
    changed = 0
    conv_furn = 0
    def get(yi, x, y, z):
        s = smap.get(yi)
        if s is None or 'block_states' not in dict(s): return 'minecraft:air'
        pal, idx = decode_section(s['block_states'][1])
        return pal_name(pal[idx[(y*16+z)*16+x]])
    for s in secs:
        if 'block_states' not in dict(s): continue
        bs = s['block_states'][1]
        pal, idx = decode_section(bs)
        names = [pal_name(e) for e in pal]
        if 'minecraft:cobweb' not in names: continue
        new_idx = list(idx)
        # state cache: name->entry (rebuild palette at end)
        for pos, vi in enumerate(idx):
            if names[vi] != 'minecraft:cobweb': continue
            x = pos % 16; z = (pos // 16) % 16; y = pos // 256
            abs_y = s['Y'][1]*16 + y
            below = get(s['Y'][1]-1 if y == 0 else s['Y'][1], x, (y-1) % 16, z)
            if below not in NON_SOLID:
                entry = pick(rng)
                if entry['Name'][1] != 'minecraft:air': conv_furn += 1
            else:
                entry = {'Name': (8, 'minecraft:air')}
            new_idx[pos] = entry['Name'][1]  # temp store name
            changed += 1
        # rebuild palette preserving order + new entries
        order = []
        seen = {}
        final_idx = [0]*4096
        # map old palette entries (name,propstuple) keep dicts
        old_entries = pal
        key_of = lambda e: (pal_name(e), tuple(sorted((k, v[1]) for k, v in e.get('Properties', (10, {}))[1].items())) if 'Properties' in e else ())
        for e in old_entries:
            k = key_of(e)
            if k not in seen: seen[k] = len(order); order.append(e)
        for pos in range(4096):
            if isinstance(new_idx[pos], str):
                nm = new_idx[pos]
                # find entry with this name (new furniture has no props)
                k = (nm, ())
                if k not in seen:
                    # locate template
                    for w, e in FURNITURE:
                        if e['Name'][1] == nm:
                            seen[k] = len(order); order.append(e); break
                final_idx[pos] = seen[k]
            else:
                final_idx[pos] = seen[key_of(old_entries[new_idx[pos]])]
        # prune unused palette entries
        used = sorted(set(final_idx))
        remap = {old_i: new_i for new_i, old_i in enumerate(used)}
        order = [order[o] for o in used]
        final_idx = [remap[v] for v in final_idx]
        s['block_states'] = (10, encode_section(order, final_idx))
    if changed and 'Heightmaps' in root:
        del root['Heightmaps']
    return changed, conv_furn

def process_file(path, rng, dry=False):
    with open(path, 'rb') as f:
        raw_all = f.read()
    hdr = raw_all[:8192]
    chunks = {}
    for i in range(1024):
        (loc,) = struct.unpack('>I', hdr[4*i:4*i+4])
        if loc == 0: continue
        off, cnt = (loc >> 8)*4096, (loc & 255)*4096
        ln = struct.unpack('>I', raw_all[off:off+4])[0]
        comp = raw_all[off+4]
        payload = raw_all[off+5:off+4+ln]
        data = zlib.decompress(payload) if comp == 2 else payload
        root = NBTReader(data).read_tag()[2]
        chunks[i] = (off, cnt, comp, root)
    tch = tcf = 0
    out_payloads = {}
    for i, (off, cnt, comp, root) in chunks.items():
        ch, cf = process_chunk(root, rng)
        tch += ch; tcf += cf
        if ch:
            out_payloads[i] = zlib.compress(w_tag('', 10, root), 6)
    if dry or not out_payloads:
        return len(chunks), tch, tcf, False
    # rebuild file
    new_file = bytearray(8192)
    new_file[:8192] = hdr[:8192]
    # timestamps preserved (second 4k already copied)
    cur = 2  # next free sector
    # first pass: keep unmodified in place? simplest: rewrite all sequentially
    blobs = {}
    for i in range(1024):
        (loc,) = struct.unpack('>I', hdr[4*i:4*i+4])
        if loc == 0: continue
        off, cnt = (loc >> 8)*4096, (loc & 255)*4096
        if i in out_payloads:
            comp = 2; payload = out_payloads[i]
        else:
            comp = chunks[i][2]
            ln0 = struct.unpack('>I', raw_all[off:off+4])[0]
            payload = raw_all[off+5:off+4+ln0]
            # keep original compression byte
            comp = raw_all[off+4]
        blob = struct.pack('>I', len(payload)+1) + bytes([comp]) + payload
        nsec = (len(blob) + 4095)//4096
        blob += b'\x00'*(nsec*4096 - len(blob))
        blobs[i] = (cur, nsec, blob)
        cur += nsec
    for i, (sec, nsec, blob) in blobs.items():
        struct.pack_into('>I', new_file, 4*i, (sec << 8) | nsec)
    body = bytearray()
    # ensure order by sector
    for i, (sec, nsec, blob) in sorted(blobs.items(), key=lambda kv: kv[1][0]):
        body += blob
    with open(path, 'wb') as f:
        f.write(bytes(new_file) + bytes(body))
    return len(chunks), tch, tcf, True

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    target = [a for a in sys.argv[1:] if not a.startswith('--')]
    rng = random.Random(20261002)
    TCH = TCF = TCHN = 0
    for pat in target:
        for path in sorted(glob.glob(pat)):
            if os.path.getsize(path) == 0: continue
            try:
                n, ch, cf, wrote = process_file(path, rng, dry)
            except Exception as e:
                print('ERROR', path, repr(e)); continue
            TCHN += n; TCH += ch; TCF += cf
            print(f'{"[dry] " if dry else ""}{path}: chunks={n} cobwebs={ch} ->mobilia={cf} {"rewritten" if wrote else "skipped"}')
    print(f'TOTAL chunks={TCHN} cobwebs={TCH} mobilia={TCF}')
