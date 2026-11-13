"""Reparo pontual de quintais/ruas ja gerados, direto nos .mca (jogo FECHADO).

Cobre, sem regenerar chunks:
1) caminho 1 acima: dirt_path com grass_block embaixo e ar em cima desce 1
   (o parque/lote nasceu 1 bloco acima da grama naquele ponto);
2) reaterro: numa area retangular de chunks com a superficie afundada (ex. fosso
   de porao que nao existe mais), todo ar em [grade-8, grade] vira terra e o ar
   na cota `grade` vira grama. Nunca sobrescreve bloco algum; coluna com agua/lava
   ou com bau/barril/shulker/loot abaixo de grade+1 e preservada (nao enterra loot).

Uso:
  python3 retrofit_yard.py "<save>" --dry
  python3 retrofit_yard.py "<save>" --paths --dry
  python3 retrofit_yard.py "<save>" --grade 71 --rect 20,70,21,71 [--dry]
  python3 retrofit_yard.py "<save>" --sunken 340,1126,341,1127,68,71 [--dry]
  (rect = cx0,cz0,cx1,cz1 em coords de chunk; sunken = x0,z0,x1,z1,piso,rua em
  coords de bloco: abre poco ate o piso e poe escada de stone_bricks descendo
  para o sul; sem --paths/--grade/--sunken so mostra diagnostico)
"""
import sys, os, glob, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retrofit_hedges import read_region, write_region, chunk_origin, decode, encode

LOOT_RX = re.compile(r'chest|barrel|shulker|loot', re.I)
WATER_RX = re.compile(r'water|lava', re.I)


def bid(entry):
    return entry['Name'][1]


def get(sections, x, y, z):
    """entry do bloco em coords absolutas, ou None."""
    for s, pal, idx, oy in sections:
        if oy <= y < oy + 16:
            return pal[idx[(y - oy) * 256 + (z % 16) * 16 + (x % 16)]]
    return None


def load_sections(root):
    out = []
    for s in root.get('sections', (9, (10, [])))[1][1]:
        if 'block_states' not in s:
            continue
        pal, idx = decode(s['block_states'][1])
        out.append((s, pal, idx, s['Y'][1] * 16))
    return out


def main():
    save = sys.argv[1]
    dry = '--dry' in sys.argv
    do_paths = '--paths' in sys.argv
    grade = None
    rect = None
    sunken = None
    for i, a in enumerate(sys.argv):
        if a == '--grade' and i + 1 < len(sys.argv):
            grade = int(sys.argv[i + 1])
        if a == '--rect' and i + 1 < len(sys.argv):
            rect = [int(v) for v in sys.argv[i + 1].split(',')]
        if a == '--sunken' and i + 1 < len(sys.argv):
            sunken = [int(v) for v in sys.argv[i + 1].split(',')]
    stats = collections.Counter()
    files = sorted(glob.glob(os.path.join(save, 'region', '*.mca')))
    for path in files:
        raw, chunks = read_region(path)
        changed = {}
        for i, root in chunks.items():
            ox, oz = chunk_origin(root)
            cx, cz = ox // 16, oz // 16
            in_rect = rect and rect[0] <= cx <= rect[2] and rect[1] <= cz <= rect[3]
            in_sunken = False
            if sunken:
                sx0, sz0, sx1, sz1, _fl, _gr = sunken
            if not do_paths and not in_rect and not sunken:
                continue
            sections = load_sections(root)
            if not sections:
                continue
            touched = False
            # indice mutavel por secao: sy -> [pal_entries, idx, section_tag, oy]
            mods = {}
            for s, pal, idx, oy in sections:
                mods[s['Y'][1]] = [list(pal), list(idx), s, oy]

            def entry_at(x, y, z):
                m = mods.get(y // 16)
                if not m:
                    return None
                _pal, _idx, _s, _oy = m
                return _pal[_idx[(y - _oy) * 256 + (z % 16) * 16 + (x % 16)]]

            def set_block(lx, y, lz, new_entry):
                _sy = y // 16
                if _sy not in mods:
                    return False
                _pal, _idx, _s, _oy = mods[_sy]
                _p = (y - _sy * 16) * 256 + lz * 16 + lx
                _k = (new_entry['Name'][1], tuple(sorted((a, b[1]) for a, b in new_entry.get('Properties', (10, {}))[1].items())))
                for _j, _e in enumerate(_pal):
                    _k2 = (_e['Name'][1], tuple(sorted((a, b[1]) for a, b in _e.get('Properties', (10, {}))[1].items())))
                    if _k2 == _k:
                        _idx[_p] = _j
                        return True
                _pal.append(new_entry)
                _idx[_p] = len(_pal) - 1
                return True

            def is_air(e):
                return e is not None and bid(e).endswith('air')

            if do_paths:
                for lx in range(16):
                    for lz in range(16):
                        x, z = ox + lx, oz + lz
                        for y in range(60, 90):
                            e = entry_at(x, y, z)
                            if e is None or bid(e) != 'minecraft:dirt_path':
                                continue
                            below = entry_at(x, y - 1, z)
                            above = entry_at(x, y + 1, z)
                            if below is not None and bid(below) == 'minecraft:grass_block' and is_air(above):
                                if set_block(lx, y - 1, lz, dict(e)):
                                    set_block(lx, y, lz, {'Name': (8, 'minecraft:air')})
                                    stats['caminho_descido'] += 1
                                    touched = True
            if in_rect:
                for lx in range(16):
                    for lz in range(16):
                        x, z = ox + lx, oz + lz
                        col = [entry_at(x, y, z) for y in range(grade - 8, grade + 1)]
                        if any(e is not None and (WATER_RX.search(bid(e)) or LOOT_RX.search(bid(e))) for e in col):
                            continue
                        for y in range(grade - 8, grade + 1):
                            e = entry_at(x, y, z)
                            if e is None or not is_air(e):
                                continue
                            if y < grade:
                                ok = set_block(lx, y, lz, {'Name': (8, 'minecraft:dirt')})
                                stats['aterro'] += 1
                            else:
                                ok = set_block(lx, y, lz, {'Name': (8, 'minecraft:grass_block'),
                                                          'Properties': (10, {'snowy': (8, 'false')})})
                                stats['grama'] += 1
                            touched = touched or ok
            if sunken:
                sx0, sz0, sx1, sz1, floor_y, grade_y = sunken
                stair = {'Name': (8, 'minecraft:stone_brick_stairs'),
                         'Properties': (10, {'facing': (8, 'north'), 'half': (8, 'bottom'),
                                             'shape': (8, 'straight'), 'waterlogged': (8, 'false')})}
                for lx in range(16):
                    for lz in range(16):
                        x, z = ox + lx, oz + lz
                        if not (sx0 <= x <= sx1 and sz0 <= z <= sz1):
                            continue
                        col = [entry_at(x, y, z) for y in range(floor_y, grade_y + 1)]
                        if any(e is not None and (WATER_RX.search(bid(e)) or LOOT_RX.search(bid(e))) for e in col):
                            continue
                        for y in range(floor_y + 1, grade_y + 1):
                            if y < grade_y:
                                ok = set_block(lx, y, lz, dict(stair))
                                stats['escada_pedra'] += 1
                            else:
                                ok = set_block(lx, y, lz, {'Name': (8, 'minecraft:air')})
                                stats['poco_aberto'] += 1
                            touched = touched or ok
            if touched:
                for _sy, (_pal, _idx, _s, _oy) in mods.items():
                    _s['block_states'] = (10, encode(_pal, _idx))
                changed[i] = root
        if changed:
            stats['chunks'] += len(changed)
            if not dry:
                write_region(path, raw, changed)
    print(('[dry] ' if dry else '') + save, dict(stats))


if __name__ == '__main__':
    main()
