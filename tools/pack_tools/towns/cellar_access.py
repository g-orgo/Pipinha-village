"""Acesso ao porao: cada regiao de ar do porao precisa de escada ate o terreo.

Regiao: componente conexo de celulas de ar (y, z, x) da grade cellar de todos os predios do grupo
(predio solto ou multipredio), atravessando as bordas dos chunks (16x16) quando as duas celulas
vizinhas sao ar. Regiao com >= 30 celulas de ar e porao real; abaixo disso e ignorada.
Acesso da regiao: alguma celula de ar do topo do porao com ar/escada/stairs na fatia 0 do terreo
da mesma coluna, ou alguma escada/stairs/scaffolding encostada na regiao.

Idempotente: so escava regioes sem acesso, uma escada por regiao. Partes compartilhadas por mais de
um predio sao clonadas com sufixo _acc antes de receber a escada, e so o predio escavado aponta
para o clone. Validado pelo validate.py (analyze), que usa as mesmas regras.
"""
import collections, copy, glob, json, os
import lcparts as L

LC = L.LC
DIRS = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}
OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
MIN_REGION = 30
# grupos sem escavacao possivel; analyze() os ignora (validate e step). Motivo em cada linha.
EXCEPTIONS = {
    # stock LC city building: region at the building edge (x/z 0-1/14-15)
    'sunlit:multibuildings/multi_casino',
    'sunlit:multibuildings/multi_filmworkstower',
    'sunlit:multibuildings/multi_thering',
    # region floats over air (no solid floor in the column) and region at the building edge
    'sunlit:multibuildings/multi_terraceplaza',
    # functional blocks (air ducts/iron doors) in every column
    'sunlit:multibuildings/multi_communitycenter',
    'sunlit:multibuildings/multi_sunkenmonumentpark',
    'sunlit:multibuildings/multi_taigaresidence',
    'sunlit:hardwarestoreie/main',
    'sunlit:hardwarestoreie/90',
    'sunlit:hardwarestoreie/180',
    'sunlit:hardwarestoreie/270',
}
# blocos que nao fazem parede cheia (nao servem de apoio para a escada)
NOT_WALL = ('ladder', 'stairs', 'slab', 'carpet', 'torch', 'lantern', 'door', 'trapdoor', 'button',
            'sign', 'pressure', 'scaffold', 'pot', 'flower', 'rail', 'fence', 'chain', 'glass', 'pane')


def _name(s):
    return (s or '').split('[')[0]


def _air(s):
    return s is not None and L.block_is_air(s)


def _solid(s):
    return s is not None and not _air(s) and not any(k in _name(s) for k in NOT_WALL)


def _climb(s):
    return any(k in _name(s) for k in ('ladder', 'stairs', 'scaffold'))


def _grid(store, name):
    p = L.rl_path('parts', name)
    if not os.path.exists(p):
        return None
    return L.Grid(store, name, json.load(open(p, encoding='utf-8')))


def _record(store, rl):
    """dados do predio com porao (cellar + ground); None se nao tiver porao"""
    p = L.rl_path('buildings', rl)
    if not os.path.exists(p):
        return None
    d = json.load(open(p, encoding='utf-8'))
    parts = [pe for k in ('parts', 'parts2') for pe in d.get(k, [])]
    cel = [pe['part'] for pe in parts if pe.get('cellar')]
    gr = [pe['part'] for pe in parts if pe.get('ground')]
    if not d.get('maxcellars', 0) or not cel or not gr:
        return None
    cg = _grid(store, cel[0])
    gs = [_grid(store, n) for n in gr]
    if cg is None or any(g is None for g in gs):
        return None
    return {'rl': rl, 'path': p, 'd': d, 'cel': cel[0], 'gr': gr, 'cg': cg, 'gs': gs}


def _cells(recs):
    """celulas de ar de todas as grades cellar: chaves (r, c, y, z, x); r,c = posicao no grupo"""
    air = set()
    for (r, c), rec in recs.items():
        cg = rec['cg']
        for y in range(cg.H):
            for z in range(min(cg.Z, 16)):
                for x in range(min(cg.X, 16)):
                    if _air(cg.b(y, z, x)):
                        air.add((r, c, y, z, x))
    return air


def _nbrs(key):
    """vizinhos 6-direcoes; cruza a borda do chunk (16x16) para o chunk vizinho"""
    r, c, y, z, x = key
    yield (r, c, y - 1, z, x)
    yield (r, c, y + 1, z, x)
    for dz, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc, nz, nx = r, c, z + dz, x + dx
        if nz < 0:
            nr, nz = r - 1, 15
        elif nz > 15:
            nr, nz = r + 1, 0
        if nx < 0:
            nc, nx = c - 1, 15
        elif nx > 15:
            nc, nx = c + 1, 0
        yield (nr, nc, y, nz, nx)


def _regions(recs):
    """componentes de ar com >= MIN_REGION celulas"""
    air = _cells(recs)
    seen, regs = set(), []
    for k in sorted(air):
        if k in seen:
            continue
        comp, stack = set(), [k]
        seen.add(k)
        while stack:
            cur = stack.pop()
            comp.add(cur)
            for n in _nbrs(cur):
                if n in air and n not in seen:
                    seen.add(n)
                    stack.append(n)
        if len(comp) >= MIN_REGION:
            regs.append(comp)
    return regs


def _has_access(comp, recs):
    for key in comp:
        r, c, y, z, x = key
        rec = recs[(r, c)]
        if y == rec['cg'].H - 1 and any(_air(g.b(0, z, x)) or _climb(g.b(0, z, x)) for g in rec['gs']):
            return True
        for n in _nbrs(key):
            nb = recs.get(n[:2])
            if nb is not None and _climb(nb['cg'].b(n[2], n[3], n[4])):
                return True
    return False


def _bad(recs):
    """regioes de porao real sem acesso"""
    return [comp for comp in _regions(recs) if not _has_access(comp, recs)]


def analyze(store):
    """grupos (predio solto ou multipredio) com porao real: [{label, ok, recs, bad}]"""
    multi, groups = set(), []
    for mf in sorted(glob.glob(os.path.join(LC, 'multibuildings', '*.json'))):
        rows = json.load(open(mf, encoding='utf-8'))['buildings']
        multi |= {b for row in rows for b in row if b}
        groups.append(('sunlit:multibuildings/' + os.path.basename(mf)[:-5], rows))
    for bf in sorted(glob.glob(os.path.join(LC, 'buildings', '**', '*.json'), recursive=True)):
        rl = 'sunlit:' + os.path.relpath(bf, os.path.join(LC, 'buildings'))[:-5].replace(os.sep, '/')
        if rl not in multi:
            groups.append((rl, [[rl]]))
    out = []
    for label, rows in groups:
        if label in EXCEPTIONS:
            continue
        recs = {}
        for r, row in enumerate(rows):
            for c, rl in enumerate(row):
                rec = _record(store, rl) if rl else None
                if rec is not None:
                    recs[(r, c)] = rec
        if not recs:
            continue
        bad = _bad(recs)
        out.append({'label': label, 'ok': not bad, 'recs': recs, 'bad': bad})
    return out


FUNC = ('chest', 'furnace', 'door', 'bed', 'lever', 'spawner', 'barrel', 'hopper', 'dispenser',
        'dropper', 'shulker', 'anvil', 'crafting', 'enchanting', 'brewing', 'smoker', 'jukebox',
        'lectern', 'cauldron', 'composter', 'beacon', 'bell', 'note_block')


def _func(s):
    """bloco funcional: a escada nao pode substitui-lo"""
    return s is not None and any(k in _name(s) for k in FUNC)


def _pick(comp, recs):
    """melhor coluna para a escada: (score, key, z, x, y_low, dir, gi) ou None.
    A coluna vai da fatia 0 do terreo ate o topo do porao, descendo pelo ar ate o primeiro solido
    sob a regiao. Pode cortar solidos (teto/laje). Menos solidos cortados = melhor."""
    best = None
    for key in sorted(comp):
        r, c, y0, z, x = key
        if not (2 <= z <= 13 and 2 <= x <= 13) or y0 < 1:
            continue
        rec = recs[(r, c)]
        cg = rec['cg']
        top = cg.H - 1
        f = y0 - 1
        while f >= 0 and not _solid(cg.b(f, z, x)):
            f -= 1
        if f < 0:
            continue
        y_low = f + 1
        shaft = range(y_low, top + 1)
        if any(_func(cg.b(y, z, x)) for y in shaft):
            continue
        for gi, g in enumerate(rec['gs']):
            if g.H < 2 or any(_func(g.b(y, z, x)) for y in range(0, min(3, g.H))):
                continue
            # solidos no terreo (fatias 1..2) sao cortados, mas so se a coluna tiver entrada de sala
            gcut = [y for y in range(1, min(3, g.H)) if _solid(g.b(y, z, x))]
            if gcut and not any(
                    0 <= z + dz < g.Z and 0 <= x + dx < g.X
                    and all(_air(g.b(y, z + dz, x + dx)) for y in range(1, min(3, g.H)))
                    and _solid(g.b(0, z + dz, x + dx))
                    for dx, dz in DIRS.values()):
                continue
            dirs = [d for d, (dx, dz) in DIRS.items()
                    if all(_solid(cg.b(y, z + dz, x + dx)) for y in shaft) and _solid(g.b(0, z + dz, x + dx))]
            if not dirs:
                continue
            cut = sum(_solid(cg.b(y, z, x)) for y in shaft) + (1 if _solid(g.b(0, z, x)) else 0) + len(gcut)
            cand = (-cut, key, z, x, y_low, dirs[0], gi)
            if best is None or cand[0] > best[0]:
                best = cand
    return best


def _own(store, name, grid, refs):
    """devolve (nome final, grade final): clona a parte se outro predio tambem a usa"""
    if refs[name] <= 1:
        return name, grid
    new = name + '_acc'
    part = copy.deepcopy(grid.part)
    # parte sem paleta propria so usa chars do common: o clone herda a mesma paleta
    if 'refpalette' not in part and not grid.pal.new:
        part['refpalette'] = grid.pal.rl
    return new, L.Grid(store, new, part)


def _carve(store, recs, comp, refs, stats):
    pick = _pick(comp, recs)
    if pick is None:
        return False
    _, key, z, x, y0, d, gi = pick
    rec = recs[key[:2]]
    cg0, gs0 = rec['cg'], rec['gs'][gi]
    cel_new, cg = _own(store, rec['cel'], cg0, refs)
    gr_name = rec['gr'][gi]
    gr_new, g = _own(store, gr_name, gs0, refs)
    top = cg.H - 1
    ladder = 'minecraft:ladder[facing=%s]' % OPP[d]
    for y in range(y0, top + 1):
        cg.put(y, z, x, ladder)
    g.put(0, z, x, ladder)
    # corta o solido do terreo (fatias 1..2) para o jogador entrar pela sala ao lado
    for y in range(1, min(3, g.H)):
        if _solid(g.b(y, z, x)):
            g.put(y, z, x, 'minecraft:air')
    for name, grid, new in ((rec['cel'], cg, cel_new), (gr_name, g, gr_new)):
        if grid.commit() or new != name:
            json.dump(grid.part, open(L.rl_path('parts', new), 'w', encoding='utf-8'))
        if new != name:
            stats['cloned'] += 1
    d_json = rec['d']
    for k in ('parts', 'parts2'):
        for pe in d_json.get(k, []):
            if pe['part'] == rec['cel'] and cel_new != rec['cel']:
                pe['part'] = cel_new
            if pe['part'] == gr_name and gr_new != gr_name:
                pe['part'] = gr_new
    if cel_new != rec['cel'] or gr_new != gr_name:
        json.dump(d_json, open(rec['path'], 'w', encoding='utf-8'), indent=2)
        for old, new in ((rec['cel'], cel_new), (gr_name, gr_new)):
            if new != old:
                refs[old] -= 1
                refs[new] += 1
    rec['cel'], rec['cg'] = cel_new, cg
    rec['gr'][gi], rec['gs'][gi] = gr_new, g
    return True


def main():
    store = L.Store()
    refs = collections.Counter()
    for bf in glob.glob(os.path.join(LC, 'buildings', '**', '*.json'), recursive=True):
        d = json.load(open(bf, encoding='utf-8'))
        for k in ('parts', 'parts2'):
            for pe in d.get(k, []):
                refs[pe['part']] += 1
    stats = collections.Counter()
    fixed, carves, fails = 0, 0, []
    for grp in analyze(store):
        if grp['ok']:
            continue
        recs = grp['recs']
        bad = grp['bad']
        done_here = 0
        while bad:
            progress = False
            for comp in bad:
                if _carve(store, recs, comp, refs, stats):
                    progress = True
                    done_here += 1
                    break
            if not progress:
                break
            bad = _bad(recs)
        carves += done_here
        if bad:
            fails.append(grp['label'])
        elif done_here:
            fixed += 1
    store.save()
    print(f'cellar_access: {carves} regioes escavadas em {fixed} predios, {stats["cloned"]} partes clonadas, '
          f'{len(fails)} sem escavacao possivel')
    for f in fails[:20]:
        print('SEM ESCAVACAO', f)


if __name__ == '__main__':
    main()
