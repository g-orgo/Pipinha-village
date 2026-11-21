"""Moves every player of a save to their bed (respawn point). The game MUST be closed.

Used by regen_chunks.py after a regen (2026-11-11, owner's request): the player logs in inside a
kept chunk instead of in the middle of freshly deleted terrain, so the first login does not stall
generating everything around the old position.

Writes both copies of the host player: level.dat Data.Player (singleplayer) and
playerdata/<uuid>.dat. Players without a bed, or riding something, are left where they are.

Usage: python3 send_to_bed.py "Solito solamente" [--dry]
"""
import re
import sys, os, glob, gzip, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtmini import NBTReader
from nbtwrite import w_tag

SAVES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'saves')


def _move(player):
    """Moves one player compound in place. Returns a description, or None when unchanged."""
    if 'SpawnX' not in player or 'RootVehicle' in player:
        return None
    x, y, z = (player[k][1] for k in ('SpawnX', 'SpawnY', 'SpawnZ'))
    dim = player.get('SpawnDimension', (8, 'minecraft:overworld'))[1]
    # Bed block position: stand on top of it, centered, like the vanilla respawn
    player['Pos'] = (9, (6, [x + 0.5, y + 0.6, z + 0.5]))
    player['Motion'] = (9, (6, [0.0, 0.0, 0.0]))
    player['Dimension'] = (8, dim)
    player['FallDistance'] = (5, 0.0)
    return f'{dim} {x} {y} {z}'


def _rewrite(path, edit, dry):
    name, tid, root = NBTReader(gzip.open(path).read()).read_tag()
    result = edit(root)
    if result and not dry:
        shutil.copy2(path, path + '_bedbak')
        with gzip.open(path, 'wb') as f:
            f.write(w_tag(name, tid, root))
    return result


def send_to_bed(save, dry=False):
    base = save if os.path.isdir(save) else os.path.join(SAVES, save)
    tag = '[dry] ' if dry else ''
    level = os.path.join(base, 'level.dat')
    res = _rewrite(level, lambda r: _move(r['Data'][1]['Player'][1]) if 'Player' in r['Data'][1] else None, dry)
    print(f'{tag}cama level.dat: {res or "sem cama, posicao mantida"}')
    # Only <uuid>.dat: the game leaves temp files named <uuid>-<number>.dat behind, which it never reads
    for f in sorted(glob.glob(os.path.join(base, 'playerdata', '*.dat'))):
        if not re.fullmatch(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\.dat', os.path.basename(f)):
            continue
        res = _rewrite(f, _move, dry)
        print(f'{tag}cama {os.path.basename(f)}: {res or "sem cama, posicao mantida"}')


if __name__ == '__main__':
    send_to_bed(sys.argv[1], '--dry' in sys.argv)
