"""Show or change the Lost Cities street layout persisted in a save (data/LostCityWorldGenData.dat).

Why: Lost Cities 8.4 keeps the street mode a world was created with ("Existing worlds keep their persisted
mode"), so changing streetGenerationMode in the profile only reaches new worlds. The pack uses LEGACY (the
1.20.1 layout: a street around every building), which the Sunlit Towns scripts were made for; the
HIERARCHICAL_GRID_V1 default of 8.4 leaves open lots one block above the street, blocks without a road and
houses facing nothing.

Only chunks generated after the change follow the new mode. Chunks that already exist keep the old layout, so
the switch goes together with a regen (regen_chunks.py) of the city chunks, never alone in a played save.
The game MUST be closed. A copy of the .dat is kept next to it (LostCityWorldGenData.dat.bak-<mode>).

Usage: python3 lc_street_mode.py "<save dir>" [LEGACY|HIERARCHICAL_GRID_V1] [--dim minecraft:overworld]
       (without a mode it only prints what is stored)
"""
import gzip
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from nbtwrite import w_tag

MODES = ('LEGACY', 'HIERARCHICAL_GRID_V1')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dim = sys.argv[sys.argv.index('--dim') + 1] if '--dim' in sys.argv else 'minecraft:overworld'
    if '--dim' in sys.argv:
        args.remove(dim)
    if not args:
        print(__doc__)
        return 1
    path = os.path.join(args[0], 'data', 'LostCityWorldGenData.dat')
    if not os.path.exists(path):
        print(f'nao achei {path}')
        return 1
    name, tid, root = NBTReader(gzip.open(path).read()).read_tag()
    data = root['data'][1]
    modes = data.setdefault('streetModes', (10, {}))[1]
    cur = modes.get(dim, (8, None))[1]
    print(f'{dim}: modo de ruas gravado = {cur}')
    if len(args) < 2:
        return 0
    new = args[1]
    if new not in MODES:
        print(f'modo invalido: {new} (use {", ".join(MODES)})')
        return 1
    if cur == new:
        print('nada a fazer')
        return 0
    lock = os.path.join(args[0], 'session.lock')
    if os.path.exists(lock):
        import fcntl
        # Minecraft holds a FileChannel lock (POSIX record lock on Linux) on session.lock while the world is open
        with open(lock, 'rb+') as f:
            try:
                fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.lockf(f, fcntl.LOCK_UN)
            except OSError:
                print('o save esta aberto: feche o jogo antes')
                return 1
    bak = f'{path}.bak-{cur}'
    shutil.copy2(path, bak)
    modes[dim] = (8, new)
    with gzip.open(path, 'wb') as f:
        f.write(w_tag(name, tid, root))
    check = NBTReader(gzip.open(path).read()).read_tag()[2]['data'][1]['streetModes'][1][dim][1]
    print(f'{dim}: {cur} -> {check} (copia em {os.path.basename(bak)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
