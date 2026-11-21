"""Moves every tamed animal (living entity with an owner) that stands outside its owner's FTB Chunks claims
into one of them, on a safe spot (pet_spot.py). The game MUST be closed, with a backup made before.

Called by regen_chunks.py before deleting anything (2026-11-18, owner's request): the strict regen used to
leave the animal where it was and the new terrain was born on top of it (the mare Epona suffocated).
Target: the owner's claimed chunks, nearest to the owner's herd already inside them (same species first).
The Horseman wander anchor and any other home/anchor position near the old spot follow the animal.
Owner without claims, or no safe spot: the animal stays and the report says so. A player animal with no
owner at all (Society affection, name tag, lead) outside every claim goes to the nearest claim of any team.

Usage: python3 -I move_pets.py "Solito solamente" [--dry]
"""
import sys, os, re, glob, zlib, struct, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from nbtwrite import w_tag
from pet_spot import chunk_spots

SAVES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'saves')
OWNER_KEYS = ('Owner', 'OwnerUUID', 'Owner_UUID', 'RedomesticateOwner')
SKIP_KEYS = {'Pos', 'Motion', 'Rotation', 'UUID', 'Passengers', 'Attributes', 'attributes', 'Items',
             'Inventory', 'ArmorItems', 'HandItems', 'body_armor_item', 'SaddleItem', 'DecorItem'}
NEAR = 128  # a stored position this close to the old spot is the animal's home/anchor
ALWAYS = {'HorsemanWanderAnchor'}  # Horseman tie anchor: always follows the animal, wherever it pointed


def _uuid(t, v):
    if t == 11 and len(v) == 4:
        h = ''.join('%08x' % (x & 0xffffffff) for x in v)
        return '%s-%s-%s-%s-%s' % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])
    return v.lower() if t == 8 and re.fullmatch(r'[0-9a-fA-F-]{36}', v) else None


def owner_of(e):
    if 'Health' not in e or e['id'][1].startswith('easy_npc:'):  # xp catalysts and town NPCs have an Owner too
        return None
    for k in OWNER_KEYS:
        if k in e and _uuid(*e[k]):
            return _uuid(*e[k])
    return None


def team_claims(save):
    """{player uuid: set of overworld chunks claimed by every team the player belongs to}, {uuid: name}."""
    members, names, claims = {}, {}, {}
    for f in glob.glob(os.path.join(save, 'ftbteams', '*', '*.snbt')):
        txt = open(f, encoding='utf-8').read()
        tid = re.search(r'\bid:\s*"([0-9a-f-]{36})"', txt)
        ranks = re.search(r'ranks:\s*\{(.*?)\}', txt, re.S)
        if tid and ranks:
            for u, r in re.findall(r'([0-9a-f-]{36})"?\s*:\s*"(\w+)"', ranks.group(1)):
                if r in ('owner', 'officer', 'member'):
                    members.setdefault(tid.group(1), set()).add(u)
        name = re.search(r'player_name:\s*"([^"]*)"', txt)
        if tid and name:
            names[tid.group(1)] = name.group(1)
    for f in glob.glob(os.path.join(save, 'ftbchunks', '*.snbt')):
        tid = os.path.basename(f)[:-5]
        m = re.search(r'"?minecraft:overworld"?\s*:\s*\[(.*?)\]', open(f, encoding='utf-8').read(), re.S)
        cs = {(int(a), int(b)) for a, b in re.findall(r'\bx:\s*(-?\d+)\b[^{}]*?\bz:\s*(-?\d+)\b', m.group(1))} if m else set()
        for u in members.get(tid, {tid}):
            claims.setdefault(u, set()).update(cs)
    return claims, names


def players(save):
    """UUIDs of real players: playerdata/<uuid>.dat plus FTB Teams player teams."""
    files = glob.glob(os.path.join(save, 'playerdata', '*.dat')) + glob.glob(os.path.join(save, 'ftbteams', 'player', '*.snbt'))
    return {m.group(0) for f in files for m in [re.fullmatch(r'[0-9a-f-]{36}', os.path.basename(f).rsplit('.', 1)[0])] if m}


def _chunks(raw):
    for i in range(1024):
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if loc:
            off = (loc >> 8) * 4096
            yield i, raw[off:off + 4 + struct.unpack('>I', raw[off:off + 4])[0]]


def _decode(blob):
    return NBTReader(zlib.decompress(blob[5:])).read_tag() if blob[4] == 2 else None


def _encode(tag):
    comp = zlib.compress(w_tag(*tag))
    return struct.pack('>I', len(comp) + 1) + b'\x02' + comp


def _write_region(path, raw, blobs, touched):
    """Rewrites a .mca with blobs {index: full blob}; untouched chunks are copied byte for byte."""
    stamps = bytearray(raw[4096:8192]) if raw else bytearray(4096)
    for i in touched:
        struct.pack_into('>I', stamps, 4 * i, int(time.time()))
    header, body, cur = bytearray(8192), bytearray(), 2
    for i in sorted(blobs):
        blob = blobs[i] + b'\x00' * (-len(blobs[i]) % 4096)
        struct.pack_into('>I', header, 4 * i, (cur << 8) | (len(blob) // 4096))
        body += blob
        cur += len(blob) // 4096
    header[4096:] = stamps
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(bytes(header) + bytes(body))
    os.replace(tmp, path)


def _retarget(node, old, new, path=''):
    """Moves home/anchor positions stored near the old spot to the new one. Returns the keys changed."""
    changed = []
    for k, (t, v) in list(node.items()):
        if k in SKIP_KEYS:
            continue
        if k.endswith('X') and t in (3, 5, 6) and k[:-1] + 'Z' in node and k[:-1] + 'Y' in node:
            ky, kz = k[:-1] + 'Y', k[:-1] + 'Z'
            if k[:-1] in ALWAYS or (abs(v - old[0]) <= NEAR and abs(node[kz][1] - old[2]) <= NEAR):
                for key, val in ((k, new[0]), (ky, new[1]), (kz, new[2])):
                    tt = node[key][0]
                    node[key] = (tt, float(val) if tt in (5, 6) else int(val // 1))
                changed.append(path + k[:-1])
        elif t == 11 and len(v) == 3 and re.search(r'pos|home|anchor', k, re.I):
            if abs(v[0] - old[0]) <= NEAR and abs(v[2] - old[2]) <= NEAR:
                node[k] = (11, [int(new[0] // 1), int(new[1] // 1), int(new[2] // 1)])
                changed.append(path + k)
        elif t == 10:
            changed += _retarget(v, old, new, path + k + '.')
    return changed


def _shift(e, d):
    x, y, z = e['Pos'][1][1]
    e['Pos'] = (9, (6, [x + d[0], y + d[1], z + d[2]]))
    e['Motion'] = (9, (6, [0.0, 0.0, 0.0]))
    e['FallDistance'] = (5, 0.0)
    for p in e.get('Passengers', (9, (10, [])))[1][1]:
        _shift(p, d)


def _label(e, own, names):
    x, y, z = e['Pos'][1][1]
    nm = re.search(r'"text":"([^"]*)"', e.get('CustomName', (8, ''))[1])
    return '%s%s @%d,%d,%d dono=%s' % (e['id'][1], " '%s'" % nm.group(1) if nm else '', x // 1, y // 1, z // 1,
                                      names.get(own, own))


def move_pets(save, dry=False):
    """Returns the UUIDs (int arrays as tuples) of the animals moved (or that would be, with dry)."""
    base = save if os.path.isdir(save) else os.path.join(SAVES, save)
    tag = '[dry] ' if dry else ''
    claims, names = team_claims(base)
    known = players(base)
    regions, roots = {}, []
    for p in sorted(glob.glob(os.path.join(base, 'entities', '*.mca'))):
        raw = open(p, 'rb').read()
        if len(raw) < 8192:
            continue
        reg = regions[p] = {'raw': raw, 'blobs': dict(_chunks(raw)), 'tags': {}, 'dirty': set()}
        for i, blob in reg['blobs'].items():
            t = _decode(blob)
            if t:
                reg['tags'][i] = t
                roots += [(p, i, e) for e in t[2].get('Entities', (9, (10, [])))[1][1]]
    from regen_chunks import player_animal  # lazy: regen_chunks imports this module
    # Player animal with no owner at all (Society affection, name tag, lead): '' = any team's claim, nearest
    claims[''], names[''] = set().union(*claims.values()), 'sem dono'
    herd, movers, inside = {}, [], 0
    for p, i, e in roots:
        own = owner_of(e)
        living = 'Health' in e and not e['id'][1].startswith('easy_npc:')
        if own is None and living and not any(k in e for k in OWNER_KEYS) and player_animal(e):
            own = ''
        elif own not in known:  # not an animal, or owned by a mob/NPC instead of a player
            continue
        x, _, z = e['Pos'][1][1]
        c = (int(x // 16), int(z // 16))
        if c in claims['']:
            herd.setdefault('', []).append((e['id'][1], x, z))
        if c in claims.get(own, ()):
            herd.setdefault(own, []).append((e['id'][1], x, z))
            inside += 1
        else:
            movers.append((p, i, e, own))
    spots, used, moved, stuck = {}, [], set(), {'sem_claim': 0, 'sem_lugar': 0}
    for p, i, e, own in movers:
        label = _label(e, own, names)
        if not claims.get(own):
            stuck['sem_claim'] += 1
            print(f'{tag}animal_sem_claim_do_dono (fica onde esta): {label}')
            continue
        x, y, z = e['Pos'][1][1]
        near = [h for h in herd.get(own, []) if h[0] == e['id'][1]] or herd.get(own, [])
        rx, rz = min(((hx, hz) for _, hx, hz in near), key=lambda h: (h[0] - x) ** 2 + (h[1] - z) ** 2,
                     default=(x, z))
        cands = []
        for c in claims[own]:
            if c not in spots:
                spots[c] = chunk_spots(base, *c)
            cands += [s for s in spots[c] if all(max(abs(s[1] - u[0]), abs(s[3] - u[1])) > 1 for u in used)]
        if not cands:
            stuck['sem_lugar'] += 1
            print(f'{tag}animal_sem_lugar_seguro (fica onde esta): {label}')
            continue
        cls, sx, sy, sz = min(cands, key=lambda s: (s[0], (s[1] - rx) ** 2 + (s[3] - rz) ** 2))
        used.append((sx, sz))
        new = (sx + 0.5, sy, sz + 0.5)
        changed = _retarget(e, (x, y, z), new)
        _shift(e, (new[0] - x, new[1] - y, new[2] - z))
        if 'leash' in e:  # tied to a knot that is about to be deleted
            del e['leash']
            changed.append('guia_solta')
        src = regions[p]['tags'][i][2]
        src['Entities'] = (9, (10, [q for q in src['Entities'][1][1] if q is not e]))
        regions[p]['dirty'].add(i)
        cx, cz = sx >> 4, sz >> 4
        tp = os.path.join(base, 'entities', 'r.%d.%d.mca' % (cx >> 5, cz >> 5))
        reg = regions.setdefault(tp, {'raw': None, 'blobs': {}, 'tags': {}, 'dirty': set()})
        ti = (cx & 31) + (cz & 31) * 32
        dst = reg['tags'].setdefault(ti, ('', 10, {'DataVersion': src['DataVersion'], 'Position': (11, [cx, cz]),
                                                    'Entities': (9, (10, []))}))[2]
        dst['Entities'] = (9, (10, dst['Entities'][1][1] + [e]))
        reg['dirty'].add(ti)
        moved.add(tuple(e['UUID'][1]) if 'UUID' in e else id(e))
        print(f'{tag}animal_movido: {label} -> {new[0]:.1f},{new[1]:.2f},{new[2]:.1f} chunk ({cx},{cz})'
              f'{" chao construido" if cls else ""}{" ajustado=" + ",".join(changed) if changed else ""}')
    if not dry:
        dirty = {p: reg for p, reg in regions.items() if reg['dirty']}
        for reg in dirty.values():
            for i in reg['dirty']:
                reg['blobs'][i] = _encode(reg['tags'][i])
                if len(reg['blobs'][i]) > 255 * 4096:  # would need a .mcc file: write nothing at all
                    sys.exit('move_pets: chunk de entidades grande demais, nada foi gravado')
        for p, reg in dirty.items():
            _write_region(p, reg['raw'], reg['blobs'], reg['dirty'])
    print(f'{tag}animais do jogador: movidos={len(moved)} ja_em_claim={inside} '
          f'sem_claim_do_dono={stuck["sem_claim"]} sem_lugar_seguro={stuck["sem_lugar"]}')
    return moved


if __name__ == '__main__':
    move_pets(sys.argv[1], '--dry' in sys.argv)
