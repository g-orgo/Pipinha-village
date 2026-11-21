"""Make farmland converted from the 1.20.1 save work with Sunrise Gardening (overworld only).

In 1.20.1 Dew Drop replaced minecraft:farmland itself; in 1.21.1 the managed farmland is
sunrisegardening:tilled_soil. Sunrise only grows a crop when its soil has an entry in the chunk
attachment sunrisegardening:tilled_block_chunk_data and a pending 10-tick scheduled tick, both
created by onPlace. Blocks written by the save conversion have neither, so their crops never grow
and Jade shows "Cannot grow". This script, with the game closed:
  1. turns minecraft:farmland into sunrisegardening:tilled_soil (same moisture);
  2. adds the missing day data, with total_days_grown = floor(age * growTime / maxAge) of the crop
     above (the formula of Sunrise's DayDataUtils.syncDayData) and day_last_grown = current day;
  3. adds the missing scheduled tick of each Sunrise soil block.

Usage: python3 sunrise_soil.py "<save dir>" [--dry]
"""
import glob, gzip, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
INST = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(INST, 'tools', 'pack_tools'))
from nbtmini import NBTReader  # noqa: E402
from retrofit_hedges import read_region, write_region, decode, encode  # noqa: E402

SG = 'sunrisegardening:'
SOILS = {SG + n for n in ('tilled_soil', 'weak_fertilized_farmland', 'strong_fertilized_farmland',
                          'hyper_fertilized_farmland', 'hydrating_farmland', 'deluxe_hydrating_farmland',
                          'bountiful_fertilized_farmland', 'low_quality_fertilized_farmland',
                          'high_quality_fertilized_farmland', 'pristine_quality_fertilized_farmland',
                          'tilled_sand', 'hyper_fertilized_sand')}
RATE = {SG + 'weak_fertilized_farmland': 0.1, SG + 'strong_fertilized_farmland': 0.25,
        SG + 'hyper_fertilized_farmland': 0.33}          # data_maps/block/growth_fertilizer_rate.json
GROW = {'minecraft:wheat': 15, 'minecraft:beetroots': 7}  # data_maps/block/crop_grow_times.json
KEY = SG + 'tilled_block_chunk_data'
VANILLA = {'minecraft:wheat': 7, 'minecraft:carrots': 7, 'minecraft:potatoes': 7, 'minecraft:beetroots': 3,
           'minecraft:nether_wart': 3, 'minecraft:sweet_berry_bush': 3, 'minecraft:torchflower_crop': 1,
           'minecraft:pitcher_crop': 4, 'minecraft:melon_stem': 7, 'minecraft:pumpkin_stem': 7}  # client jar
_max_age = {}


def max_age(bid):
    """Highest age=N in the block's blockstate file (mod jars, then kubejs/assets)."""
    if bid in VANILLA:
        return VANILLA[bid]
    if bid in _max_age:
        return _max_age[bid]
    ns, path = bid.split(':')
    name = f'assets/{ns}/blockstates/{path}.json'
    text = None
    loose = os.path.join(INST, 'kubejs', name)
    if os.path.exists(loose):
        text = open(loose).read()
    for jar in ([] if text else glob.glob(os.path.join(INST, 'mods', '*.jar'))):
        try:
            with zipfile.ZipFile(jar) as z:
                if name in z.namelist():
                    text = z.read(name).decode('utf-8', 'replace')
                    break
        except zipfile.BadZipFile:
            continue
    ages = [int(a) for a in re.findall(r'age=(\d+)', text or '')]
    ages += [int(a) for a in re.findall(r'"age"\s*:\s*"?(\d+)', text or '')]
    _max_age[bid] = max(ages) if ages else None
    return _max_age[bid]


def state_name(p):
    d = p[1] if isinstance(p, tuple) else p
    props = d.get('Properties', (10, {}))[1]
    return d['Name'][1], {k: v[1] for k, v in props.items()}


def main():
    save = sys.argv[1]
    dry = '--dry' in sys.argv
    lvl = NBTReader(gzip.open(os.path.join(save, 'level.dat')).read()).read_tag()[2]['Data'][1]
    day = lvl['DayTime'][1] // 24000
    stats = {'farmland': 0, 'day_data': 0, 'ticks': 0, 'chunks': 0, 'no_max_age': set()}
    for rp in sorted(glob.glob(os.path.join(save, 'region', '*.mca'))):
        raw, chunks = read_region(rp)
        changed = {}
        for ci, root in chunks.items():
            cx, cz = root['xPos'][1], root['zPos'][1]
            grid, dirty = {}, False
            for s in root['sections'][1][1]:
                if 'block_states' not in s:
                    continue
                raw_pal, idx = decode(s['block_states'][1])
                pal = [state_name(p) for p in raw_pal]
                if any(n == 'minecraft:farmland' for n, _ in pal):
                    keys, new_pal, remap = {}, [], []
                    for n, props in pal:
                        if n == 'minecraft:farmland':
                            n = SG + 'tilled_soil'
                        k = (n, tuple(sorted(props.items())))
                        if k not in keys:
                            keys[k] = len(new_pal)
                            entry = {'Name': (8, n)}
                            if props:
                                entry['Properties'] = (10, {a: (8, b) for a, b in props.items()})
                            new_pal.append(entry)
                        remap.append(keys[k])
                    stats['farmland'] += sum(1 for i in idx if pal[i][0] == 'minecraft:farmland')
                    idx = [remap[i] for i in idx]
                    pal = [state_name(p) for p in new_pal]
                    s['block_states'] = (10, encode(new_pal, idx))
                    dirty = True
                grid[s['Y'][1]] = (pal, idx)

            def at(x, y, z):
                sec = grid.get(y >> 4)
                return sec[0][sec[1][((y & 15) << 8) | ((z & 15) << 4) | (x & 15)]] if sec else (None, {})

            soils = []
            for sy, (pal, idx) in grid.items():
                if not any(n in SOILS for n, _ in pal):
                    continue
                for i, pi in enumerate(idx):
                    if pal[pi][0] in SOILS:
                        soils.append((pal[pi][0], cx * 16 + (i & 15), sy * 16 + (i >> 8), cz * 16 + ((i >> 4) & 15)))
            if not soils:
                if dirty:
                    changed[ci] = root
                continue
            att = root.setdefault('neoforge:attachments', (10, {}))[1]
            entries = att.setdefault(KEY, (9, (10, [])))[1][1]
            have = {tuple(e['pos'][1]) for e in entries}
            bt = root.get('block_ticks')
            ticks = bt[1][1] if bt and bt[1][0] == 10 else []
            ticked = {(t['x'][1], t['y'][1], t['z'][1]) for t in ticks}
            added = 0
            for n, (soil, x, y, z) in enumerate(soils):
                if (x, y, z) not in have:
                    crop, props = at(x, y + 1, z)
                    total = 0
                    if crop and 'age' in props:
                        top = max_age(crop)
                        if top:
                            base = GROW.get(crop, top)
                            g = int(base * (1 - RATE[soil])) if soil in RATE else base
                            total = max(0, int(props['age']) * g // top)
                        else:
                            stats['no_max_age'].add(crop)
                    entries.append({'pos': (11, [x, y, z]), 'day_data': (10, {
                        'total_days_grown': (3, total), 'day_last_grown': (4, day)})})
                    stats['day_data'] += 1
                    added += 1
                if (x, y, z) not in ticked:
                    ticks.append({'i': (8, soil), 'x': (3, x), 'y': (3, y), 'z': (3, z),
                                  't': (3, 10 + n % 20), 'p': (3, 0)})
                    stats['ticks'] += 1
                    added += 1
            if added:
                root['block_ticks'] = (9, (10, ticks))
            if added or dirty:
                changed[ci] = root
        if changed:
            stats['chunks'] += len(changed)
            if not dry:
                write_region(rp, raw, changed)
    print(('DRY ' if dry else '') + f"day {day}: farmland->tilled_soil {stats['farmland']}, "
          f"day data added {stats['day_data']}, ticks added {stats['ticks']}, chunks {stats['chunks']}")
    if stats['no_max_age']:
        print('crops without a readable max age (total_days_grown = 0):', sorted(stats['no_max_age']))


if __name__ == '__main__':
    main()
