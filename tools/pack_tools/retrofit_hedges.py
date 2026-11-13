"""Religa as cercas-vivas (hedges) de um save ja gerado, direto nos arquivos .mca.

Por que: o Lost Cities colocava as hedges com os 4 lados como vinham da paleta e nunca
recalculava; em borda de chunk o vizinho ainda nao existia e a hedge ficava "cubo isolado".
Alem disso hedge do cfm so conecta com hedge do cfm e a do Refurbished so com a do
Refurbished (qualquer madeira), entao fileiras mistas nunca se ligavam.

O que faz (2 passadas, o jogo PRECISA estar fechado):
1) acha todas as hedges do save (cfm/refurbished) e agrupa as encostadas (6 vizinhos);
2) grupo misto cfm + refurbished: as do cfm viram refurbished da mesma madeira;
3) lado north/south/east/west = true quando o vizinho e hedge; contra outros blocos
   mantem o valor que ja estava (o jogo ja calculou parede/folha).
Hedges de grupos so-cfm ou so-refurbished nao trocam de tipo (as que voce colocou ficam iguais).

Uso: python3 retrofit_hedges.py "../saves/Nosso mapa" [--dry]
"""
import sys, os, glob, struct, zlib, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from nbtwrite import w_tag

DIRS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0)}


def is_hedge(name):
    return name.endswith('_hedge') and name.split(':')[0] in ('cfm', 'refurbished_furniture')


def wood(name):
    w = name.split(':')[1][:-len('_hedge')]
    return 'azalea' if w == 'flowering_azalea' else w


def decode(bs):
    pal = bs['palette'][1][1]
    n = len(pal)
    if n == 1 or 'data' not in bs:
        return pal, [0] * 4096
    bpe = max(4, math.ceil(math.log2(n)))
    per = 64 // bpe
    mask = (1 << bpe) - 1
    longs = [v & 0xFFFFFFFFFFFFFFFF for v in bs['data'][1]]
    return pal, [(longs[p // per] >> ((p % per) * bpe)) & mask for p in range(4096)]


def encode(pal, idx):
    n = len(pal)
    if n == 1:
        return {'palette': (9, (10, pal))}
    bpe = max(4, math.ceil(math.log2(n)))
    per = 64 // bpe
    longs = [0] * ((4096 + per - 1) // per)
    for p, v in enumerate(idx):
        longs[p // per] |= v << ((p % per) * bpe)
    return {'palette': (9, (10, pal)), 'data': (12, longs)}


def read_region(path):
    raw = open(path, 'rb').read()
    out = {}
    if len(raw) < 8192:
        return raw, out
    for i in range(1024):
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if not loc:
            continue
        off = (loc >> 8) * 4096
        ln = struct.unpack('>I', raw[off:off + 4])[0]
        comp = raw[off + 4]
        if comp not in (1, 2, 3):
            continue  # chunk externo (.mcc) ou desconhecido: nao mexe
        payload = raw[off + 5:off + 4 + ln]
        data = zlib.decompress(payload) if comp in (1, 2) else payload
        out[i] = NBTReader(data).read_tag()[2]
    return raw, out


def write_region(path, raw, changed):
    """regrava o arquivo inteiro: chunks alterados recomprimidos, o resto copiado byte a byte."""
    header = bytearray(raw[:8192])
    body = bytearray()
    cur = 2
    for i in range(1024):
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if not loc:
            continue
        off = (loc >> 8) * 4096
        if i in changed:
            payload = zlib.compress(w_tag('', 10, changed[i]), 6)
            blob = struct.pack('>I', len(payload) + 1) + b'\x02' + payload
        else:
            ln = struct.unpack('>I', raw[off:off + 4])[0]
            blob = raw[off:off + 4 + ln]
        nsec = (len(blob) + 4095) // 4096
        blob += b'\x00' * (nsec * 4096 - len(blob))
        struct.pack_into('>I', header, 4 * i, (cur << 8) | nsec)
        body += blob
        cur += nsec
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(bytes(header) + bytes(body))
    os.replace(tmp, path)


def sections_with_hedges(root):
    secs = root.get('sections', (9, (10, [])))[1][1]
    for s in secs:
        if 'block_states' not in s:
            continue
        bs = s['block_states'][1]
        if any(is_hedge(e['Name'][1]) for e in bs['palette'][1][1]):
            yield s, bs


def chunk_origin(root):
    return root['xPos'][1] * 16, root['zPos'][1] * 16


def main():
    save = sys.argv[1]
    dry = '--dry' in sys.argv
    files = sorted(glob.glob(os.path.join(save, 'region', '*.mca')))
    # passada 1: posicoes de todas as hedges
    hedges = {}
    for path in files:
        _, chunks = read_region(path)
        for root in chunks.values():
            ox, oz = chunk_origin(root)
            for s, bs in sections_with_hedges(root):
                pal, idx = decode(bs)
                oy = s['Y'][1] * 16
                for p, v in enumerate(idx):
                    nm = pal[v]['Name'][1]
                    if is_hedge(nm):
                        hedges[(ox + p % 16, oy + p // 256, oz + (p // 16) % 16)] = nm
    # grupos encostados (union-find em 6 vizinhos)
    parent = {p: p for p in hedges}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for (x, y, z) in hedges:
        for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            q = (x + d[0], y + d[1], z + d[2])
            if q in hedges:
                ra, rb = find((x, y, z)), find(q)
                if ra != rb:
                    parent[ra] = rb
    mods = collections.defaultdict(set)
    for p, nm in hedges.items():
        mods[find(p)].add(nm.split(':')[0])
    mixed = {r for r, m in mods.items() if len(m) > 1}

    stats = collections.Counter(total=len(hedges), grupos_mistos=len(mixed))
    # passada 2: regrava estados
    for path in files:
        raw, chunks = read_region(path)
        changed = {}
        for i, root in chunks.items():
            ox, oz = chunk_origin(root)
            touched = False
            for s, bs in sections_with_hedges(root):
                pal, idx = decode(bs)
                oy = s['Y'][1] * 16
                keys, entries, new_idx = {}, [], [0] * 4096
                for p, v in enumerate(idx):
                    e = pal[v]
                    nm = e['Name'][1]
                    if is_hedge(nm):
                        pos = (ox + p % 16, oy + p // 256, oz + (p // 16) % 16)
                        old = {k: t[1] for k, t in e.get('Properties', (10, {}))[1].items()}
                        new_nm = nm
                        if nm.startswith('cfm:') and find(pos) in mixed:
                            new_nm = f'refurbished_furniture:{wood(nm)}_hedge'
                            stats['cfm_para_refurbished'] += 1
                        props = {}
                        for side, (dx, dy, dz) in DIRS.items():
                            nb = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
                            props[side] = 'true' if nb in hedges else old.get(side, 'false')
                        if new_nm.startswith('cfm:'):
                            props['waterlogged'] = old.get('waterlogged', 'false')
                        if new_nm != nm or any(props[k] != old.get(k) for k in props):
                            stats['religadas'] += 1
                            touched = True
                        e = {'Name': (8, new_nm), 'Properties': (10, {k: (8, v) for k, v in props.items()})}
                    k = (e['Name'][1], tuple(sorted((a, b[1]) for a, b in e.get('Properties', (10, {}))[1].items())))
                    if k not in keys:
                        keys[k] = len(entries)
                        entries.append(e)
                    new_idx[p] = keys[k]
                s['block_states'] = (10, encode(entries, new_idx))
            if touched:
                changed[i] = root
        if changed:
            stats['chunks'] += len(changed)
            if not dry:
                write_region(path, raw, changed)
    print(('[dry] ' if dry else '') + save, dict(stats))


if __name__ == '__main__':
    main()
