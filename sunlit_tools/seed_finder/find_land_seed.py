"""Finds a world seed that puts land (Lithosphere terrain) around a point, without running the game.
Usage: python3 -I find_land_seed.py <blockX> <blockZ> [--count 300] [--check <seed>]
Extracts vanilla + Lithosphere worldgen data from the jars into a temp dir, screens seeds by
continentalness (ocean < -0.19, coast < -0.11) and ranks the land-only ones by terrain height (target y 72).
Validated 2026-11-11 against Solito solamente: 487/487 generated chunks matched ocean/deep/land.
"""
import glob, os, random, sys, tempfile, zipfile
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from litho_continents import Continents

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
DD = os.path.join(tempfile.gettempdir(), 'sunlit_seed_finder', 'data')

def extract():
    jars = [os.path.join(ROOT, '..', '..', 'Install', 'versions', '1.20.1', '1.20.1.jar')] + glob.glob(os.path.join(ROOT, 'mods', 'lithosphere*.jar'))
    for j in jars:
        with zipfile.ZipFile(j) as z:
            for n in z.namelist():
                if '/worldgen/noise/' in n or '/worldgen/density_function/' in n:
                    z.extract(n, os.path.dirname(DD))

def land(args):
    seed, bx, bz = args
    C = Continents(seed, DD)
    for R, step in ((8, 2), (24, 4), (40, 8)):
        for dx in range(-R, R + 1, step):
            for dz in range(-R, R + 1, step):
                if C.at(bx + dx * 16, bz + dz * 16) < -0.11: return None
    return seed

def heights(args):
    seed, bx, bz = args
    D = Continents(seed, DD, 'lithosphere:depth')
    hs = [D.surface(bx + dx * 16 + 8, bz + dz * 16 + 8) for dx in range(-12, 13, 3) for dz in range(-12, 13, 3)]
    return seed, min(hs), max(hs), round(sum(hs) / len(hs), 1)

if __name__ == '__main__':
    bx, bz = int(sys.argv[1]), int(sys.argv[2])
    extract()
    if '--check' in sys.argv:
        s = int(sys.argv[sys.argv.index('--check') + 1])
        print('land' if land((s, bx, bz)) is not None else 'ocean/coast within 40 chunks', heights((s, bx, bz)))
        sys.exit()
    n = int(sys.argv[sys.argv.index('--count') + 1]) if '--count' in sys.argv else 300
    rnd = random.Random(20261111)
    seeds = [rnd.getrandbits(64) - (1 << 63) for _ in range(n)]
    with Pool(6) as p:
        ok = [s for s in p.map(land, [(s, bx, bz) for s in seeds], chunksize=4) if s is not None]
        res = p.map(heights, [(s, bx, bz) for s in ok])
    res.sort(key=lambda r: abs(r[3] - 72) + (r[2] - r[1]) / 4)
    print(len(ok), 'land-only seeds of', n)
    for r in res[:10]: print('seed %d  y %d..%d avg %.1f' % r)
