"""Apaga do overworld de um save todos os chunks SEM presenca de jogador, para o Minecraft
gerar de novo com a worldgen atual (datapack sunlit_towns, perfil sunlit_cozy) quando
alguem passar por la. O jogo PRECISA estar fechado.

Fica preservado:
- raio de RADIUS chunks em volta da posicao atual e do ponto de spawn (cama) de cada jogador
  que esteja no overworld;
- todo chunk com claim do FTB Chunks no overworld (ftbchunks/*.snbt), sem raio — incluindo
  os com forceload ativo (force_loaded_time > 0 na entrada do chunk; forceload exige claim,
  entao e um subconjunto, mas o script conta os dois separados no log);
- qualquer chunk com InhabitedTime >= MIN_INHABITED (jogador passou bastante tempo perto: base);
- SEMPRE (qualquer modo, inclusive --politica-solo e --apenas-forceload): chunk com animal do
  jogador em entities/ (carinho do Society em KubeJSPersistentData, dono/domado, golem ou
  stoneling feito pelo jogador, na guia, nome dado com name tag, ou passageiro de um desses).
  NPCs de cidade (easy_npc) e nomes gerados (so translate) nao contam.
- SEMPRE (qualquer modo): lote de grama feito por fix_cut_houses.py (lotes_limpos.tsv), senao a seed
  gera a meia casa de novo nele.
- SEMPRE: predio inteiro. Todo chunk mantido leva a area inteira do Lost Cities (8x8 da cidade,
  7x7 das construcoes avulsas) e regen_continuity.py mantem o vizinho quando um predio cruza a
  borda; areas 8x8 tocadas ficam inteiras, ate estabilizar (motivos area_lc / predio_cruza).

- ANTES de tudo (qualquer modo, 2026-11-18): move_pets.py leva cada animal domado (vivo, com dono jogador)
  que esteja fora dos claims do dono para um ponto seguro dentro deles, com a ancora do Horseman junto.
  Animal do jogador sem dono nenhum (carinho, name tag, guia) fora de todo claim vai para o claim mais
  proximo. Dono sem claim ou sem lugar seguro: o animal fica e o relatorio diz.

Para cada chunk apagado tambem some a entrada em entities/ e poi/ (senao villagers/itens
antigos e pontos de trabalho fantasmas ficariam no chunk novo). Arquivo .mca que fica sem
chunk nenhum e removido.

Uso: python3 regen_chunks.py "Solito solamente" --so-claims-estrito [--dry]
     (outros modos: [--radius N] [--so-jogadores] [--baus] [--fazendas] [--so-forceload]
                    [--politica-solo] [--apenas-forceload] [--so-predio])
  --radius N       raio em chunks em volta de cada jogador/cama (padrao 5; 0 = so o chunk)
  --so-jogadores   ignora o InhabitedTime (mantem apenas os chunks dos jogadores/camas)
  --baus           mantem chunk com container do jogador: InhabitedTime >= MIN_INH_BAUS, algum BE com
                   inventario nao vazio e sem LootTable, fora de DECOR_IDS e lootr:*
  --so-forceload   so mantem claims FTB com forceload ativo (claim sem forceload e apagado)
  --politica-solo  preset = --radius 0 --so-jogadores --baus --so-forceload: keep only the player's
                   current chunk, force loaded chunks and chunks with player storage
  --apenas-forceload  mantem somente os chunks com forceload FTB (nem jogador, nem baus)
  --so-claims-estrito  PADRAO do modo claims desde 2026-11-11 (pedido do dono): mantem SOMENTE os
                   chunks com claim FTB (forceload incluso). Nada mais segura terreno: nem predio que
                   cruza a borda (regen_continuity), nem area_lc, nem jogador/cama, nem animal. Os
                   animais do jogador de chunk apagado nao seguram o terreno: region e poi somem, mas o
                   entities/ do chunk e reescrito so com os animais (o resto das entidades some).
  --so-claims      Mantem somente chunks com claim FTB
                   (forceload incluso, pois exige claim) + as regras SEMPRE (animal do jogador, predio
                   que cruza a borda). Nem jogador, nem cama, nem bau, nem InhabitedTime: abrir um bau
                   de loot (que perde o LootTable e passa a parecer bau do jogador) nao segura mais o
                   chunk. Implica --so-predio. Os claims nascem sozinhos ao colocar bau, cama, maquina
                   etc. (kubejs/server_scripts/blockEvents/autoClaimChunk.js)
  --fazendas       mantem chunk com terra arada onde o jogador ficou >= 1 min (InhabitedTime)
  --so-predio      sem a area inteira do Lost Cities (8x8/7x7) em volta de cada chunk mantido: so o
                   predio que cruza a borda segue junto (regen_continuity). 2026-11-10, pedido do dono:
                   a area em cascata segurava cidades inteiras velhas (21 chunks base -> 2624 mantidos)
"""
import sys, os, glob, gzip, json, re, struct, zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from regen_continuity import grow
from send_to_bed import send_to_bed
from move_pets import move_pets
from fix_cut_houses import cleared_lots

RADIUS = 5
MIN_INHABITED = 12000  # ticks = 10 min
FARM_INHABITED = 1200  # ticks = 1 min
MIN_INH_BAUS = 1200  # ticks = 1 min; container de jogador precisa de presenca minima
DECOR_IDS = {"another_furniture:shelf", "minecraft:dispenser", "minecraft:dropper"}


def _val(x):
    return x[1] if isinstance(x, tuple) else x


def stored_items(node, depth=0):
    """True se algum item nao-ar (entrada com id + Count/count) aparece em qualquer nivel do no.
    Cobre Items de topo, Inventory/Compartments (Create toolbox), storageWrapper (Sophisticated)."""
    if depth > 6 or not isinstance(node, dict):
        return False
    for t in node.values():
        if not isinstance(t, tuple):
            continue
        if t[0] == 9 and isinstance(t[1], tuple) and t[1][0] == 10:
            for e in t[1][1]:
                if 'id' in e and ('Count' in e or 'count' in e):
                    if _val(e['id']) != 'minecraft:air':
                        return True
                elif stored_items(e, depth + 1):
                    return True
        elif t[0] == 10 and stored_items(t[1], depth + 1):
            return True
    return False


def player_chest(d):
    """(id, x, y, z) do primeiro BE de armazenamento do jogador no chunk, ou None."""
    for be in d.get('block_entities', (9, (10, [])))[1][1]:
        bid = _val(be.get('id', (8, '')))
        if 'LootTable' in be or bid in DECOR_IDS or bid.startswith('lootr:'):
            continue
        if stored_items(be):
            return bid, _val(be['x']), _val(be['y']), _val(be['z'])
    return None


def _areasizes():
    """(multi, scattered) area sizes of the sunlit worldstyle; Lost Cities defaults if unreadable."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'moonlight-global-datapacks',
                     'sunlit_towns', 'data', 'sunlit', 'lostcities', 'worldstyles', 'towns.json')
    try:
        ws = json.load(open(p, encoding='utf-8'))
        return ws['multisettings']['areasize'], ws['scattered']['areasize']
    except (OSError, KeyError, ValueError):
        return 8, 7


MULTI_AREA, SCATTERED_AREA = _areasizes()


def lc_areas(c):
    """Chunk sets of the Lost Cities areas holding chunk c: the city multibuilding area
    (MultiChunk.getMultiCoord: floorDiv) and the scattered building area (Scattered: (c + 2000000) / size).
    A multibuilding never leaves its area, so keeping the whole area keeps it whole."""
    out = []
    m = MULTI_AREA
    mx, mz = c[0] // m * m, c[1] // m * m
    out.append([(mx + i, mz + j) for i in range(m) for j in range(m)])
    s, off = SCATTERED_AREA, 2000000
    sx, sz = (c[0] + off) // s * s - off, (c[1] + off) // s * s - off
    out.append([(sx + i, sz + j) for i in range(s) for j in range(s)])
    return out


def _flag(e, *keys):
    return any(_val(e.get(k, (1, 0))) for k in keys)


def player_animal(e):
    """Why this entity belongs to the player, or None. Town NPCs (easy_npc) and generated names
    (translate-only CustomName) do not count."""
    eid = _val(e.get('id', (8, '')))
    if eid.startswith('easy_npc:'):
        return None
    for tag in ('NeoForgeData', 'KubeJSPersistentData'):
        kjs = _val(e.get(tag, (10, {})))
        if isinstance(kjs, dict) and ('affection' in kjs or 'ageLastPet' in kjs):
            return 'carinho'
    if any(k in e for k in ('Owner', 'OwnerUUID', 'Owner_UUID')) or _flag(e, 'Tame', 'Tamed', 'tamed', 'Trusting', 'RedomesticateTamed'):
        return 'domado'
    if _flag(e, 'PlayerCreated', 'playerMade'):
        return 'criado'
    if 'Leash' in e:
        return 'guia'
    if '"text"' in str(_val(e.get('CustomName', (8, '')))):
        return 'nomeado'
    for p in _val(e.get('Passengers', (9, (10, []))))[1]:
        if player_animal(p):
            return 'passageiro'
    return None


def pet_chunks(save, name, skip=()):
    """{chunk index: 'motivo:id@x,y,z'} of the entities/<name> chunks holding a player animal."""
    p = os.path.join(save, 'entities', name)
    if not os.path.exists(p) or os.path.getsize(p) < 8192:
        return {}
    raw, out = open(p, 'rb').read(), {}
    for i, off, ln in chunks_of(raw):
        if raw[off + 4] != 2:
            continue
        d = NBTReader(zlib.decompress(raw[off + 5:off + 4 + ln])).read_tag()[2]
        for e in d.get('Entities', (9, (10, [])))[1][1]:
            why = player_animal(e)
            if why and tuple(_val(e.get('UUID', (11, [])))) not in skip:
                x, y, z = (round(v) for v in e['Pos'][1][1])
                out[i] = '%s:%s@%d,%d,%d' % (why, _val(e['id']), x, y, z)
                break
    return out


def has_farmland(d):
    for sec in d.get('sections', (9, (10, [])))[1][1]:
        pal = sec.get('block_states', (10, {}))[1].get('palette')
        if pal and any(e['Name'][1] == 'minecraft:farmland' for e in pal[1][1]):
            return True
    return False


def keep_set(save):
    keep, centers = set(), []
    for f in glob.glob(os.path.join(save, 'playerdata', '*.dat')):
        d = NBTReader(gzip.decompress(open(f, 'rb').read())).read_tag()[2]
        if d.get('Dimension', (8, ''))[1] == 'minecraft:overworld':
            x, _, z = d['Pos'][1][1]
            centers.append((int(x) >> 4, int(z) >> 4))
        if 'SpawnX' in d and d.get('SpawnDimension', (8, 'minecraft:overworld'))[1] == 'minecraft:overworld':
            centers.append((d['SpawnX'][1] >> 4, d['SpawnZ'][1] >> 4))
    for cx, cz in centers:
        for dx in range(-RADIUS, RADIUS + 1):
            for dz in range(-RADIUS, RADIUS + 1):
                keep.add((cx + dx, cz + dz))
    return keep, centers


def claimed(save):
    """(claims, forceloaded) do FTB Chunks no overworld: chunks: { "minecraft:overworld": [ {x, z, ...}, ... ] }.
    Entrada com force_loaded_time > 0 (ou force_loaded: true/1b) tem forceload ativo e cai nos dois
    conjuntos; claim sem forceload cai so em claims. Os dois sao preservados."""
    claims, loaded = set(), set()
    for f in glob.glob(os.path.join(save, 'ftbchunks', '*.snbt')):
        txt = open(f, encoding='utf-8').read()
        m = re.search(r'"?minecraft:overworld"?\s*:\s*\[(.*?)\]', txt, re.S)
        if not m:
            continue
        for entry in re.findall(r'\{([^{}]*)\}', m.group(1), re.S):
            xz = re.search(r'\bx:\s*(-?\d+)\b.*?\bz:\s*(-?\d+)\b', entry, re.S)
            if not xz:
                continue
            c = (int(xz.group(1)), int(xz.group(2)))
            claims.add(c)
            if re.search(r'force_loaded(?:_time)?\s*:\s*(?:[1-9]|true|1b)', entry):
                loaded.add(c)
    return claims, loaded


def chunks_of(raw):
    for i in range(1024):
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if loc:
            off = (loc >> 8) * 4096
            yield i, off, struct.unpack('>I', raw[off:off + 4])[0]


def _enc_str(s):
    b = s.encode('utf-8')
    return struct.pack('>H', len(b)) + b


def _enc_payload(tid, v):
    """Inverse of NBTReader.read_payload for the values it returns."""
    if tid == 1: return struct.pack('>b', v)
    if tid == 2: return struct.pack('>h', v)
    if tid == 3: return struct.pack('>i', v)
    if tid == 4: return struct.pack('>q', v)
    if tid == 5: return struct.pack('>f', v)
    if tid == 6: return struct.pack('>d', v)
    if tid == 7: return struct.pack('>i', len(v)) + bytes(v)
    if tid == 8: return _enc_str(v)
    if tid == 9:
        et, items = v
        return bytes([et]) + struct.pack('>i', len(items)) + b''.join(_enc_payload(et, x) for x in items)
    if tid == 10:
        return b''.join(bytes([t]) + _enc_str(k) + _enc_payload(t, val) for k, (t, val) in v.items()) + b'\x00'
    if tid == 11: return struct.pack('>i', len(v)) + b''.join(struct.pack('>i', x) for x in v)
    if tid == 12: return struct.pack('>i', len(v)) + b''.join(struct.pack('>q', x) for x in v)
    raise ValueError(f'bad tag {tid}')


def animal_only(raw, off, ln, skip=()):
    """entities/ chunk re-encoded with only the player animals (Passengers included), or None.
    Returns (blob, ['id@x,y,z', ...]). Everything else in the chunk (NPCs, items, ...) is dropped.
    skip: UUIDs move_pets.py moved away (only still here in a dry run)."""
    if raw[off + 4] != 2:
        return None
    name, tid, root = NBTReader(zlib.decompress(raw[off + 5:off + 4 + ln])).read_tag()
    keep, labels = [], []
    for e in root.get('Entities', (9, (10, [])))[1][1]:
        if player_animal(e) and tuple(_val(e.get('UUID', (11, [])))) not in skip:
            keep.append(e)
            x, y, z = (round(v) for v in e['Pos'][1][1])
            labels.append('%s@%d,%d,%d' % (_val(e.get('id', (8, '?'))), x, y, z))
    if not keep:
        return None
    root['Entities'] = (9, (10, keep))
    comp = zlib.compress(bytes([tid]) + _enc_str(name or '') + _enc_payload(tid, root))
    return struct.pack('>I', len(comp) + 1) + bytes([2]) + comp, labels


def rewrite(path, raw, drop, repl=None):
    """regrava o .mca sem os indices de drop (copia byte a byte o resto). repl: {indice: blob
    completo (length+compression+data)} substitui o chunk daquele indice."""
    repl = repl or {}
    header = bytearray(8192)
    header[4096:8192] = raw[4096:8192]
    body, cur, kept = bytearray(), 2, 0
    for i, off, ln in chunks_of(raw):
        if i in drop:
            struct.pack_into('>I', header, 4096 + 4 * i, 0)
            continue
        blob = repl.get(i, raw[off:off + 4 + ln])
        nsec = (len(blob) + 4095) // 4096
        blob += b'\x00' * (nsec * 4096 - len(blob))
        struct.pack_into('>I', header, 4 * i, (cur << 8) | nsec)
        body += blob
        cur += nsec
        kept += 1
    if not kept:
        os.remove(path)
        return
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(bytes(header) + bytes(body))
    os.replace(tmp, path)


def main():
    global RADIUS, MIN_INHABITED
    save = sys.argv[1]
    dry = '--dry' in sys.argv
    baus, fazendas, so_forceload = '--baus' in sys.argv, '--fazendas' in sys.argv, '--so-forceload' in sys.argv
    if '--politica-solo' in sys.argv:
        RADIUS, MIN_INHABITED, baus, so_forceload = 0, float('inf'), True, True
    # --apenas-forceload: keep only FTB forceloaded chunks; no player/bed, storage or InhabitedTime keeps
    apenas_forceload = '--apenas-forceload' in sys.argv
    if apenas_forceload:
        baus, fazendas, so_forceload, MIN_INHABITED = False, False, True, float('inf')
    # --so-claims: keep only FTB claims (forceload included); casual interaction never keeps a chunk
    # --so-claims-estrito (2026-11-11): claims only; no cascade, no animal keeps terrain
    strict = '--so-claims-estrito' in sys.argv
    so_claims = '--so-claims' in sys.argv or strict
    if so_claims:
        baus, fazendas, so_forceload, MIN_INHABITED = False, False, False, float('inf')
    if '--radius' in sys.argv:
        RADIUS = int(sys.argv[sys.argv.index('--radius') + 1])
    if '--so-jogadores' in sys.argv:
        MIN_INHABITED = float('inf')
    # Every mode (2026-11-18, owner's request): tamed animals outside their owner's claims go into them first,
    # so new terrain is never born on top of them (the mare Epona suffocated after the strict regen)
    moved_pets = move_pets(save, dry)
    keep, centers = (set(), []) if apenas_forceload or so_claims else keep_set(save)
    claims, loaded = claimed(save)
    reason = {c: 'player' for c in keep}
    if so_forceload:
        claims = loaded
    for c in claims:
        reason.setdefault(c, 'forceload' if c in loaded else 'claim')
    keep |= claims
    # Grass lots made by fix_cut_houses.py have no claim; deleting them brings the cut house back
    for c in cleared_lots(save):
        keep.add(c)
        reason.setdefault(c, 'lote_limpo')
    # The origin chunks always stay (2026-11-11): at server start the ALI mod builds one of every entity and the
    # Brewery rope knot reads the block at 0,0,0, so a missing origin chunk is generated synchronously before
    # the first tick. With Lithosphere that took minutes and the world load sat at 0%.
    # A full chunk needs its neighbours up to light, so the whole 5x5 around the origin stays.
    for ox in range(-2, 3):
        for oz in range(-2, 3):
            keep.add((ox, oz))
            reason.setdefault((ox, oz), 'origem_ali')
    preserved = {}
    present = {}  # region path -> {chunk index: (cx, cz)}
    for path in sorted(glob.glob(os.path.join(save, 'region', '*.mca'))):
        raw = open(path, 'rb').read()
        if len(raw) < 8192:
            continue
        rx, rz = map(int, os.path.basename(path).split('.')[1:3])
        present[path] = {}
        pets = {} if strict else pet_chunks(save, os.path.basename(path), moved_pets)
        for i, off, ln in chunks_of(raw):
            cx, cz = rx * 32 + (i % 32), rz * 32 + (i // 32)
            present[path][i] = (cx, cz)
            if (cx, cz) in keep:
                preserved[(cx, cz)] = reason.get((cx, cz), 'player')
                continue
            if strict:
                continue
            if i in pets:
                keep.add((cx, cz))
                preserved[(cx, cz)] = 'animal:' + pets[i]
                continue
            if raw[off + 4] != 2:
                continue
            d = NBTReader(zlib.decompress(raw[off + 5:off + 4 + ln])).read_tag()[2]
            inh = d.get('InhabitedTime', (4, 0))[1]
            pc = player_chest(d) if baus and inh >= MIN_INH_BAUS else None
            why = ('bau:%s@%d,%d,%d' % pc if pc else 'inhabited' if inh >= MIN_INHABITED else
                   'fazenda' if fazendas and inh >= FARM_INHABITED and has_farmland(d) else None)
            if why:
                keep.add((cx, cz))
                preserved[(cx, cz)] = why
    # Never leave a building cut in half: keep the whole Lost Cities area of every kept chunk, then
    # any neighbour a building still crosses into (see regen_continuity.py).
    exists = {c for m in present.values() for c in m.values()}
    base = {c for c in keep if c in exists}
    so_predio = '--so-predio' in sys.argv or so_claims
    for c in ([] if so_predio else sorted(base)):
        for area in lc_areas(c):
            for a in area:
                if a in exists and a not in keep:
                    keep.add(a)
                    preserved[a] = 'area_lc:%d,%d' % c
    # A city multibuilding never leaves its 8x8 area, so an area is kept whole or not at all; the
    # building-crossing check can touch new areas, so both run until nothing changes.
    while not strict:
        m = MULTI_AREA
        for c in ([] if so_predio else sorted(keep & exists)):
            mx, mz = c[0] // m * m, c[1] // m * m
            for a in ((mx + i, mz + j) for i in range(m) for j in range(m)):
                if a in exists and a not in keep:
                    keep.add(a)
                    preserved[a] = 'area_lc:%d,%d' % c
        added = grow(save, keep, exists.__contains__)
        for c, src in added.items():
            preserved[c] = 'predio_cruza:%d,%d' % src
        if not added:
            break
    kept = dropped = animals = 0
    for path, chunks in present.items():
        drop = {i for i, c in chunks.items() if c not in keep}
        kept += len(chunks) - len(drop)
        dropped += len(drop)
        name = os.path.basename(path)
        ent_path = os.path.join(save, 'entities', name)
        # strict: player animals of a deleted chunk survive in entities/ (region and poi do not)
        animal_repl = {}
        if strict and drop and os.path.exists(ent_path) and os.path.getsize(ent_path) >= 8192:
            raw_e = open(ent_path, 'rb').read()
            for i, off, ln in chunks_of(raw_e):
                if i in drop:
                    found = animal_only(raw_e, off, ln, moved_pets)
                    if found:
                        animal_repl[i] = found[0]
                        for label in found[1]:
                            animals += 1
                            if dry:
                                print(f'[dry] animal_mantido:{label}')
        if drop and not dry:
            for sub in ('region', 'entities', 'poi'):
                p = os.path.join(save, sub, name)
                if os.path.exists(p) and os.path.getsize(p) >= 8192:
                    raw_p = open(p, 'rb').read()
                    if sub == 'entities':
                        rewrite(p, raw_p, drop - set(animal_repl), animal_repl)
                    else:
                        rewrite(p, raw_p, drop)
    if dry:
        for (cx, cz), why in sorted(preserved.items()):
            print(f'[dry] preserva chunk ({cx},{cz}) motivo={why}')
    print(('[dry] ' if dry else '') + save, f'centros(chunk)={centers}', f'claims={len(claims)}',
          f'forceloaded={len(loaded)}', f'base={len(base)}', f'preservados={kept}', f'apagados={dropped}')
    if strict:
        print(('[dry] ' if dry else '') + f'claims={len(claims)} apagados={dropped} animais_mantidos={animals}')
        # The new layout puts 2x2 multibuildings against the claims and their inner part never generates
        print('depois que o dono jogar perto da base: python3 -I tools/pack_tools/fix_cut_houses.py '
              '"saves/<save>" scan --png <arquivo>.png (casas cortadas na borda dos claims)')
    # Every mode (2026-11-11, owner's request): players wake up in their bed, inside kept terrain
    send_to_bed(save, dry)


if __name__ == '__main__':
    main()
