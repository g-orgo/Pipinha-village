"""Themed multi-chunk lots built from the buildings and parks we already have (runs AFTER polish.py,
before validate.py; everything is already in the sunlit namespace).

- lot gardens: every park part becomes a 1-chunk building (sunlit:lote/<park>). Park parts follow the
  ground-layer convention (polish.rule_park_ground): slice 0 is the ground itself, so as a building ground
  part it sits exactly at street level; empty cells of slice 0 become grass (under a building there is no
  grass from Lost Cities).
- complexes of 3 chunks (3x1 and 1x3) and 4 chunks (2x2): house/workshop + annexes + yards, some of them
  enlarged versions of a house (house + annex + yard).
- big farm of 6x6 chunks (~1 hectare): farmhouse, barns, corrals, vegetable plots, orchards, vineyard.
  Goes into the rural citystyle (when it fits) and into the scattered list (countryside).
Schematic houses inside a lot are written in rotation r0; sunlitTownsLostCities.js turns each one to the
street on its own. Every building of a lot is copied with the same floor count (Lost Cities gives all chunks of a
multibuilding the floors of the top-left chunk).

Usage: python3 complexes.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lcparts as L

LC = L.LC
FLOOR_H = 6

# token -> building: H:<house key> (1-chunk schematic house), B:<building name>, P:<park>
COMPLEXES = {
    # 3 chunks (written as 3x1 and 1x3)
    'sitio': ['B:casafazenda/main', 'P:horta_mista', 'P:curral'],
    'vinicola': ['B:adegavinho/main', 'P:vinhedo', 'P:vinhedo'],
    'oficina_create': ['B:oficinacreate/main', 'H:vermelhacre', 'B:deposito_pedra/main'],
    'atelie': ['H:vermelhaart', 'P:jardim', 'H:fadaart'],
    'estudo_magico': ['H:vermelhaenc', 'P:pomar_frutas', 'H:vermelhaalq'],
    'padaria_quintal': ['B:padariacomfy/main', 'P:horta_graos', 'P:feira'],
    'vermelha_ampliada': ['H:vermelha', 'B:deposito_tijolo/main', 'P:jardim'],
    'fada_fazendinha': ['H:fadafaz', 'P:horta', 'P:pomar'],
    # 4 chunks (2x2): [[x0z0, x0z1], [x1z0, x1z1]]
    'ferraria': [['H:vermelhafer', 'P:curral'], ['B:deposito_ardosia/main', 'P:horta']],
    'mercado': [['B:padariacomfy/main', 'P:feira'], ['B:cozinhakaleido/main', 'P:praca']],
    'fazendinha': [['B:casafazenda/main', 'P:celeiro'], ['P:horta_sobrevivencia', 'P:pomar']],
    'vila_magica': [['H:vermelhaenc', 'P:jardim'], ['H:fadabib', 'H:vermelhaalq']],
    'fada_ampliada': [['H:fada', 'P:horta'], ['H:fadacre', 'P:jardim']],
    'oficina_ampliada': [['B:oficinacreate/main', 'B:deposito_andesito/main'], ['H:vermelhacre', 'P:praca']],
}
COMPLEX_WEIGHT = 0.12
# 6x6 farm: rows along z, columns along x
FARM = [
    ['P:pomar', 'P:pomar_frutas', 'P:horta', 'P:horta_mista', 'P:horta_graos', 'P:vinhedo'],
    ['P:pomar_frutas', 'P:curral', 'P:curral', 'P:horta_graos', 'P:horta_sobrevivencia', 'P:vinhedo'],
    ['P:horta', 'P:curral', 'B:casafazenda/main', 'P:celeiro', 'P:horta', 'P:horta_mista'],
    ['P:horta_mista', 'P:jardim', 'P:celeiro', 'B:adegavinho/main', 'P:horta_graos', 'P:horta'],
    ['P:horta_graos', 'P:horta_sobrevivencia', 'P:horta', 'P:curral', 'P:pomar', 'P:pomar_frutas'],
    ['P:vinhedo', 'P:horta', 'P:horta_mista', 'P:curral', 'P:pomar_frutas', 'P:pomar'],
]


def path(kind, rl):
    return os.path.join(LC, kind, *rl.split(':', 1)[1].split('/')) + '.json'


def write(kind, rl, obj):
    p = path(kind, rl)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f)


def garden_building(store, park):
    """park part -> 1-chunk building sunlit:lote/<park> (ground part + floors of 6 slices + top)"""
    name = f'sunlit:lote/{park}'
    if os.path.exists(path('buildings', name)):
        return name
    src = store.parts[f'sunlit:parks/{park}'][1]
    g = L.Grid(store, f'sunlit:parks/{park}', json.loads(json.dumps(src)))
    grass = g.pal.alloc({'block': 'minecraft:grass_block[snowy=false]'}, store.common_chars)
    dirt = g.pal.alloc({'block': 'minecraft:dirt'}, store.common_chars)
    slices = [[list(r) for r in sl] for sl in src['slices']]
    for z in range(16):
        for x in range(16):
            if slices[0][z][x] == ' ':
                slices[0][z][x] = grass
    slices = [[''.join(r) for r in sl] for sl in slices]
    # cellar: 5 solid dirt slices + the park's slice 0 on top, so the park lands at y71 (street level)
    cellar_prl = f'sunlit:lote/{park}_cellar'
    write('parts', cellar_prl, {'xsize': 16, 'zsize': 16, 'refpalette': g.pal.rl,
                                'slices': [[dirt * 16] * 16 for _ in range(5)] + [slices[0]]})
    slices = slices[1:]
    while len(slices) < FLOOR_H + 1:
        slices.append([' ' * 16] * 16)
    parts = [{'top': False, 'cellar': True, 'ground': False, 'part': cellar_prl, 'floor': -1}]
    chunks = [slices[i:i + FLOOR_H] for i in range(0, len(slices), FLOOR_H)]
    if len(chunks[-1]) == FLOOR_H:
        chunks.append([[' ' * 16] * 16])
    for k, sl in enumerate(chunks):
        tag = 'ground' if k == 0 else ('top' if k == len(chunks) - 1 else f'f{k}')
        prl = f'sunlit:lote/{park}_{tag}'
        write('parts', prl, {'xsize': 16, 'zsize': 16, 'refpalette': g.pal.rl, 'slices': sl})
        pe = {'top': tag == 'top', 'cellar': False, 'ground': tag == 'ground', 'part': prl}
        if tag.startswith('f'):
            pe['floor'] = k
        parts.append(pe)
    floors = len(chunks) - 1
    # filler must be a char of the city style palette (Lost Cities fills under the building with it): 'G' = grass
    write('buildings', name, {'filler': 'G', 'rubber': ' ', 'allowDoors': False, 'allowFillers': False,
                              'overrideFloors': True, 'minfloors': floors, 'maxfloors': floors,
                              'mincellars': 1, 'maxcellars': 1, 'parts': parts})
    return name


AIR_PART = 'sunlit:lote/ar'


def air_part():
    write('parts', AIR_PART, {'xsize': 16, 'zsize': 16, 'slices': [[' ' * 16] * 16]})
    return AIR_PART


SOLID_CELLAR = 'sunlit:lote/cellar_solid'


def solid_cellar():
    """shared cellar of the lot buildings that are not gardens: 6 slices, all dirt"""
    pal = SOLID_CELLAR + '_palette'
    write('palettes', pal, {'palette': [{'char': 'D', 'block': 'minecraft:dirt'}]})
    write('parts', SOLID_CELLAR, {'xsize': 16, 'zsize': 16, 'refpalette': pal, 'slices': [['D' * 16] * 16] * FLOOR_H})
    return SOLID_CELLAR


def levels(bname):
    """building -> (floors F, {level: [part entries]}, filler, [garden cellar parts]) where level 0 = ground and level F = top"""
    d = json.load(open(path('buildings', bname), encoding='utf-8'))
    f = d['maxfloors']
    lv = {}
    generic = []
    cellars = []
    for pe in d['parts']:
        if pe.get('cellar'):
            # only the cellar of a garden (park-derived) is kept; the others are replaced in uniform()
            if pe['part'].startswith('sunlit:lote/') and pe['part'].endswith('_cellar'):
                cellars.append(pe['part'])
            continue
        if pe.get('ground'):
            lv.setdefault(0, []).append(pe['part'])
        elif pe.get('top'):
            lv.setdefault(f, []).append(pe['part'])
        elif 'floor' in pe:
            lv.setdefault(pe['floor'], []).append(pe['part'])
        else:
            generic.append(pe['part'])
    for k in range(1, f):
        lv.setdefault(k, list(generic))
    return f, lv, d['filler'], cellars


def uniform(cx_name, idx, bname, target, sep='_'):
    """copy of a building with exactly `target` floors: Lost Cities gives every chunk of a multibuilding the
    floor count of its top-left chunk, so all buildings of a lot must share it (shorter ones keep the roof at
    their own height and get empty floors above). Every lot building gets exactly 1 cellar, shared by the
    multibuilding: the garden's own cellar, or the solid dirt one."""
    f, lv, filler, cellars = levels(bname)
    if f > target:
        raise SystemExit(f'complexes: {bname} has {f} floors > {target}')
    cel = cellars[0] if cellars else solid_cellar()
    parts = [{'top': False, 'cellar': True, 'ground': False, 'part': cel, 'floor': -1}]
    parts += [{'top': False, 'cellar': False, 'ground': True, 'part': p} for p in lv[0]]
    for k in range(1, target + 1):
        src = lv.get(k) if k <= f else None
        lst = src if src else [air_part()]
        for p in lst:
            if k == target:
                parts.append({'top': True, 'cellar': False, 'ground': False, 'part': p})
            else:
                parts.append({'top': False, 'cellar': False, 'ground': False, 'part': p, 'floor': k})
    name = f'sunlit:cx/{cx_name}{sep}{idx}'
    write('buildings', name, {'filler': filler, 'rubber': ' ', 'allowDoors': False, 'allowFillers': False,
                              'overrideFloors': True, 'minfloors': target, 'maxfloors': target,
                              'mincellars': 1, 'maxcellars': 1, 'parts': parts})
    return name


def normalize(cx_name, grid):
    """grid[x][z] of building names -> grid of uniform copies. Schematic houses (sunlit:vila_<key>/r0c00) are
    copied in the 4 rotations as sunlit:cx/<lot>_<i>_vila_<key>/r<rot>c00 so the KubeJS can still turn them
    to the street by swapping the rotation in the name"""
    target = max(levels(b)[0] for col in grid for b in col)
    out, cache = [], {}
    for col in grid:
        row = []
        for b in col:
            if b not in cache:
                i = len(cache)
                house = b.split(':', 1)[1].split('/')[0] if b.startswith('sunlit:vila_') else None
                if house:
                    for rot in (0, 90, 180, 270):
                        uniform(f'{cx_name}_{i}_{house}', f'r{rot}c00', f'sunlit:{house}/r{rot}c00', target, sep='/')
                    cache[b] = f'sunlit:cx/{cx_name}_{i}_{house}/r0c00'
                else:
                    cache[b] = uniform(cx_name, i, b, target)
            row.append(cache[b])
        out.append(row)
    return out


def resolve(store, token):
    kind, val = token.split(':', 1)
    if kind == 'P':
        return garden_building(store, val)
    if kind == 'H':
        name = f'sunlit:vila_{val}/r0c00'
    else:
        name = f'sunlit:{val}'
    if not os.path.exists(path('buildings', name)):
        raise SystemExit(f'complexes: building {name} does not exist ({token})')
    return name


import schematics as SCH

PARK_ROTS = (90, 180, 270)


def park_rotations(store):
    """rotated copies of every park (Lost Cities never rotates parks): sunlit:parks/<name>_r<rot>.
    The ground-layer convention survives a rotation (only x/z move)."""
    made = []
    for name in sorted(n for n in store.parts if n.startswith('sunlit:parks/') and '_r' not in n.rsplit('/', 1)[1][-5:]):
        path_, src = store.parts[name]
        g = L.Grid(store, name, src)
        for rot in PARK_ROTS:
            k = rot // 90
            rl = f'{name}_r{rot}'
            new = {'xsize': 16, 'zsize': 16, 'refpalette': g.pal.rl,
                   'slices': [[' ' * 16 for _ in range(16)] for _ in range(g.H)]}
            ng = L.Grid(store, rl, new)
            for y in range(g.H):
                for z in range(16):
                    for x in range(16):
                        nx, nz = x, z
                        for _ in range(k):
                            nx, nz = 15 - nz, nx
                        e = g.entry(y, z, x)
                        if e is None or (set(e) == {'block'} and L.block_is_air(e['block'])):
                            continue
                        e2 = {kk: vv for kk, vv in e.items() if kk != 'char'}
                        if 'block' in e2:
                            e2['block'] = SCH.rot_state(e2['block'], k)
                        if 'blocks' in e2:
                            e2['blocks'] = [dict(b, block=SCH.rot_state(b['block'], k)) for b in e2['blocks']]
                        ng.put_entry(y, nz, nx, e2)
            ng.commit()
            write('parts', rl, new)
            made.append(rl)
    return made


LOTE_JS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       'kubejs', 'startup_scripts', 'sunlitTownsLotes.js')


def ground_has_farmland(part_rl):
    """the ground-floor part of a building has farmland in its slices (a lot garden on the ground floor)"""
    pd = json.load(open(path('parts', part_rl), encoding='utf-8'))
    pal = json.load(open(path('palettes', pd.get('refpalette', 'sunlit:common')), encoding='utf-8'))
    blocks = {e['char']: e.get('block', '') for e in pal['palette']}
    chars = {c for sl in pd['slices'] for r in sl for c in r if c != ' '}
    return any('farmland' in blocks.get(c, '') for c in chars)


def write_lote_js():
    """predios de lote (jardim): alguma parte sunlit:lote/* ou terreo com farmland. Predios com casa schematic
    (sunlit:vila_*) no terreo ficam de fora, porque rebaixar o terreo enterraria a casa."""
    names = set()
    for p in glob.glob(os.path.join(LC, 'buildings', '**', '*.json'), recursive=True):
        d = json.load(open(p, encoding='utf-8'))
        parts = [pr['part'] for key in ('parts', 'parts2') for pr in d.get(key, [])]
        grounds = [pr['part'] for key in ('parts', 'parts2') for pr in d.get(key, []) if pr.get('ground')]
        if any(pt.startswith('sunlit:vila_') for pt in grounds):
            continue
        if any(pt.startswith('sunlit:lote/') for pt in parts) or any(ground_has_farmland(pt) for pt in grounds):
            rel = os.path.relpath(p, os.path.join(LC, 'buildings'))[:-len('.json')].replace(os.sep, '/')
            if rel.split('/')[0].startswith('vila_'):
                continue
            names.add(f'sunlit:{rel}')
            names.add(rel)
    with open(LOTE_JS, 'w', encoding='utf-8') as f:
        f.write('// GERADO por sunlit_tools/towns/complexes.py (nao editar a mao).\n'
                '// Predios que sao so jardim de lote: o sunlitTownsLife.js rebaixa o terreo deles como parque.\n')
        f.write('global.sunlitLoteBuildings = ' + json.dumps({n: True for n in sorted(names)}, sort_keys=True) + ';\n')
    return len(names) // 2


def main():
    store = L.Store()
    rotated = park_rotations(store)
    multis = {}
    for key, layout in COMPLEXES.items():
        if isinstance(layout[0], list):
            grid = [[resolve(store, t) for t in col] for col in layout]
            multis[f'sunlit:multi_cx_{key}'] = grid
        else:
            row = [resolve(store, t) for t in layout]
            multis[f'sunlit:multi_cx_{key}_x'] = [[b] for b in row]   # 3 along x
            multis[f'sunlit:multi_cx_{key}_z'] = [row]                # 3 along z
    farm = [[resolve(store, FARM[z][x]) for z in range(6)] for x in range(6)]
    multis['sunlit:multi_cx_fazenda_grande'] = farm
    for n, (rl, grid) in enumerate(multis.items()):
        # short lot code in the copy names: Windows Explorer cannot extract paths > 260 (validate caps 120)
        tail = rl.rsplit('_', 1)[1] if rl.endswith(('_x', '_z')) else ''
        grid = normalize(f'c{n}{tail}', grid)
        write('multibuildings', rl, {'dimx': len(grid), 'dimz': len(grid[0]), 'buildings': grid})
    n = store.save()

    # parks: equal weight for every park type (no single plaza dominating) split over its 4 rotations
    for f in sorted(os.listdir(os.path.join(LC, 'citystyles'))):
        p = os.path.join(LC, 'citystyles', f)
        d = json.load(open(p, encoding='utf-8'))
        parks = [e for e in d['selectors'].get('parks', []) if not e['value'].rsplit('_', 1)[-1].startswith('r')
                 or not e['value'].rsplit('_', 1)[-1][1:].isdigit()]
        if not parks:
            continue
        out = []
        # 2026-10-16: na vila pracas e feiras (pavimentadas) pesam pouco; lotes vazios viram verde
        pf = (lambda v: 0.08 if v.rsplit('/', 1)[-1].startswith(('praca', 'feira')) else 0.25) if f == 'vila.json' else (lambda v: 0.25)
        for e in parks:
            out.append({'factor': pf(e['value']), 'value': e['value']})
            for rot in PARK_ROTS:
                if os.path.exists(path('parts', f"{e['value']}_r{rot}")):
                    out.append({'factor': pf(e['value']), 'value': f"{e['value']}_r{rot}"})
        d['selectors']['parks'] = out
        json.dump(d, open(p, 'w', encoding='utf-8'))

    # citystyles: complexes in the village-like styles, the big farm only in rural
    small = [rl for rl in multis if not rl.endswith('fazenda_grande')]
    for cs, factor in (('vila', COMPLEX_WEIGHT), ('rural', COMPLEX_WEIGHT * 1.5), ('centro', COMPLEX_WEIGHT * 0.5)):
        p = path('citystyles', f'sunlit:{cs}')
        d = json.load(open(p, encoding='utf-8'))
        lst = [e for e in d['selectors'].get('multibuildings', []) if not e['value'].startswith('sunlit:multi_cx_')]
        lst += [{'factor': factor, 'value': rl} for rl in small]
        if cs == 'rural':
            lst.append({'factor': 0.35, 'value': 'sunlit:multi_cx_fazenda_grande'})
        d['selectors']['multibuildings'] = lst
        json.dump(d, open(p, 'w', encoding='utf-8'))

    # countryside: the big farm also as scattered structure
    write('scattered', 'sunlit:fazenda_grande', {'multibuilding': 'sunlit:multi_cx_fazenda_grande', 'terrainheight': 'average',
                                                'terrainfix': 'none', 'heightoffset': 0})
    wp = path('worldstyles', 'sunlit:towns')
    w = json.load(open(wp, encoding='utf-8'))
    sc = w['scattered']['list']
    sc[:] = [e for e in sc if e['name'] != 'sunlit:fazenda_grande']
    sc.append({'name': 'sunlit:fazenda_grande', 'weight': 25, 'maxheightdiff': 4,
               'biomes': {'if_any': ['#minecraft:is_savanna', '#forge:is_plains', 'minecraft:plains',
                                     'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:flower_forest']}})
    w['scattered']['areasize'] = max(w['scattered'].get('areasize', 7), 7)
    json.dump(w, open(wp, 'w', encoding='utf-8'))
    print(f'lotes-jardim no KubeJS: {write_lote_js()}')
    print(f'parques girados: {len(rotated)}')
    # moveis empilhados entre andares (depois de escrever predios e partes)
    from polish import fix_cross_floor_furniture
    fix_cross_floor_furniture(LC)
    print(f'complexos: {len(multis)} multibuildings ({len(small)} lotes + fazenda 6x6), '
          f'{len([1 for f in os.listdir(os.path.join(LC, "buildings", "lote"))])} jardins de lote, {n} paletas')


if __name__ == '__main__':
    main()
