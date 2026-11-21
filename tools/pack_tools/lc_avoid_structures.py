"""Writes Lost Cities' `avoidStructures` with every surface structure of the installed mods.

Why: other mods' structures take their height from the natural terrain and Lost Cities flattens the town
afterwards, so a structure inside a town floats 2 to 5 blocks above the street. With the structure in
`avoidStructures` (and `avoidFlattening = true`), Lost Cities leaves its footprint out of the town and
blends the terrain around it. Only affects chunks generated after the change; chunks that already exist
are fixed by fix_floating_structures.py.

Usage (from the instance root, rerun after adding or removing a structure mod):
  python3 -I tools/pack_tools/lc_avoid_structures.py [--dry] ["saves/<save>" ...]
Writes config/ and defaultconfigs/ lostcities-server.toml, plus serverconfig/ of each save given.
"""
import glob, io, json, os, re, sys, zipfile

KEEP = ['minecraft:mansion', 'minecraft:jungle_pyramid', 'minecraft:desert_pyramid', 'minecraft:igloo',
        'minecraft:swamp_huts', 'minecraft:pillager_outpost']  # Lost Cities defaults, kept first
SURFACE_TYPES = {'hearthandharvest:corn_maze', 'supplementaries:road_sign', 'paraglider:tarrey_town_goddess_statue',
                 'youkaishomecoming:flat_check'}  # custom types without project_start_to_heightmap


def loose_json(text):
    text = re.sub(r'(?m)^\s*//.*$', '', text)
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', text))


def structures(inst):
    out = {}
    def scan(zf):
        for n in zf.namelist():
            m = re.match(r'data/([^/]+)/worldgen/structure/(.+)\.json$', n)
            if m:
                try:
                    out['%s:%s' % m.groups()] = loose_json(zf.read(n).decode('utf-8', 'replace'))
                except ValueError:
                    print('unreadable', n, file=sys.stderr)
            elif n.startswith('META-INF/jarjar/') and n.endswith('.jar'):
                scan(zipfile.ZipFile(io.BytesIO(zf.read(n))))
    for jar in sorted(glob.glob(os.path.join(inst, 'mods', '*.jar'))):
        scan(zipfile.ZipFile(jar))
    for f in glob.glob(os.path.join(inst, 'kubejs', 'data', '*', 'worldgen', 'structure', '**', '*.json'), recursive=True):
        m = re.search(r'kubejs/data/([^/]+)/worldgen/structure/(.+)\.json$', f)
        out['%s:%s' % m.groups()] = loose_json(open(f, encoding='utf-8').read())
    return out


def surface(d):
    biomes = json.dumps(d.get('biomes', ''))
    if 'nether' in biomes or re.search(r'is_end\b|the_end', biomes) or 'nether' in d.get('type', ''):
        return False
    if any(v < -16 for v in map(int, re.findall(r'"absolute": (-?\d+)', json.dumps(d.get('start_height', {}))))):
        return False  # projected to the surface but started deep underground (mineshafts)
    return d.get('project_start_to_heightmap') == 'WORLD_SURFACE_WG' or d.get('type') in SURFACE_TYPES


def main():
    inst = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
    ids = KEEP + sorted(k for k, d in structures(inst).items() if surface(d) and k not in KEEP)
    line = '\tavoidStructures = [%s]' % ', '.join('"%s"' % i for i in ids)
    saves = [a for a in sys.argv[1:] if not a.startswith('--')]
    files = [os.path.join(inst, 'config', 'lostcities-server.toml'), os.path.join(inst, 'defaultconfigs', 'lostcities-server.toml')]
    files += [os.path.join(s, 'serverconfig', 'lostcities-server.toml') for s in saves]
    print('%d structures in avoidStructures' % len(ids))
    for f in files:
        text = open(f, encoding='utf-8').read()
        new, n = re.subn(r'(?m)^\s*avoidStructures = \[.*\]$', lambda _: line, text)
        assert n == 1 and re.search(r'(?m)^\s*avoidFlattening = true$', new), f
        if '--dry' not in sys.argv and new != text:
            open(f, 'w', encoding='utf-8').write(new)
        print(('[dry] ' if '--dry' in sys.argv else '') + ('updated ' if new != text else 'unchanged ') + f)


if __name__ == '__main__':
    main()
