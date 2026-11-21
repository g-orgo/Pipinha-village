"""Safe standing spots for an animal inside a chunk, read straight from region/*.mca (used by move_pets.py).

A spot is a 3x3 patch of columns whose top block (open sky) sits at the same height, is a full solid block
from a known list, and has GAP free blocks above it (air, plants, thin snow). The 3x3 covers the widest
animals (horse 1.4, camel 1.7 wide); GAP covers the tallest (camel 2.4). No water or lava ever counts as
free or as ground, so a spot is never wet. Natural ground (grass, dirt, sand...) ranks above built floors.
"""
import os
from nbtmini import read_region_chunk

GAP = 3
NATURAL = {'grass_block', 'dirt', 'coarse_dirt', 'podzol', 'rooted_dirt', 'mycelium', 'moss_block',
           'dirt_path', 'sand', 'red_sand', 'snow_block', 'clay', 'packed_mud', 'gravel'}
BUILT_SUFFIX = ('planks', 'stone', 'bricks', 'cobblestone', 'concrete', 'terracotta', 'wool', 'tiles',
                'deepslate', 'andesite', 'diorite', 'granite', 'tuff', 'calcite', 'sandstone', 'hay_block')
NOT_FULL = ('slab', 'stairs', 'wall', 'fence', 'button', 'plate', 'pane', 'door', 'sign', 'carpet', 'magma',
            'campfire', 'cactus', 'leaves', 'ice', 'powder_snow', 'farmland', 'soul_sand', 'mud')
FREE_PLANTS = ('short_grass', 'tall_grass', 'fern', 'large_fern', 'dandelion', 'poppy', 'tulip', 'daisy',
               'orchid', 'allium', 'azure_bluet', 'cornflower', 'lily_of_the_valley', 'dead_bush')
MAX_SNOW = 4  # snow layers above this are too thick to stand in


def _local(name):
    return name.split(':', 1)[-1]


def is_free(name, props):
    loc = _local(name)
    if loc in ('air', 'cave_air', 'void_air'):
        return True
    if name == 'minecraft:snow':
        return int(props.get('layers', '1')) <= MAX_SNOW
    return name.startswith('minecraft:') and loc in FREE_PLANTS


def ground_class(name, props):
    """0 natural ground, 1 built full block, None when nothing should stand on it."""
    loc = _local(name)
    if props.get('waterlogged') == 'true' or any(w in loc for w in NOT_FULL):
        return None
    if loc in NATURAL or loc.endswith('grass_block'):
        return 0
    if loc.endswith(BUILT_SUFFIX):
        return 1
    return None


def _unpack(bs):
    """(palette [(name, props)], 4096 palette indices or None when the palette has one entry)."""
    pal = [(e['Name'][1], {k: v[1] for k, v in e.get('Properties', (10, {}))[1].items()})
           for e in bs['palette'][1][1]]
    data = bs.get('data', (12, []))[1]
    if len(pal) == 1 or not data:
        return pal, None
    bits = max(4, (len(pal) - 1).bit_length())
    per, mask, idx = 64 // bits, (1 << bits) - 1, []
    for word in data:
        word &= (1 << 64) - 1
        for j in range(per):
            idx.append((word >> (j * bits)) & mask)
    return pal, idx[:4096]


def column_tops(save, cx, cz):
    """{(lx, lz): (ground_y, class, stand_y)} for the open-sky top of every column of a full chunk."""
    p = os.path.join(save, 'region', 'r.%d.%d.mca' % (cx >> 5, cz >> 5))
    tag = read_region_chunk(p, cx, cz) if os.path.exists(p) else None
    if not tag or tag[2].get('Status', (8, ''))[1] != 'minecraft:full':
        return {}
    secs = sorted(((s['Y'][1], _unpack(s['block_states'][1])) for s in tag[2]['sections'][1][1]
                   if 'block_states' in s), reverse=True)
    out = {}
    for lz in range(16):
        for lx in range(16):
            free, snow = 0, 0.0
            for sy, (pal, idx) in secs:
                done = False
                for ly in range(15, -1, -1):
                    name, props = pal[idx[(ly * 16 + lz) * 16 + lx] if idx else 0]
                    if is_free(name, props):
                        free += 1
                        snow = (int(props.get('layers', '1')) - 1) / 8 if name == 'minecraft:snow' else 0.0
                        continue
                    cls = ground_class(name, props)
                    if cls is not None and free >= GAP:
                        y = sy * 16 + ly
                        out[(lx, lz)] = (y, cls, y + 1 + snow)
                    done = True
                    break
                if done:
                    break
    return out


def chunk_spots(save, cx, cz):
    """[(class, x, stand_y, z)] centres of 3x3 patches with one ground height (block x/z, world coords)."""
    tops, spots = column_tops(save, cx, cz), []
    for (lx, lz), (y, cls, stand) in tops.items():
        if not (0 < lx < 15 and 0 < lz < 15):
            continue
        around = [tops.get((lx + dx, lz + dz)) for dx in (-1, 0, 1) for dz in (-1, 0, 1)]
        if all(a and a[0] == y for a in around):
            spots.append((max(a[1] for a in around), cx * 16 + lx, max(a[2] for a in around), cz * 16 + lz))
    return spots
