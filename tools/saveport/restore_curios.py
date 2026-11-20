"""Restore the player's Curios slots from the 1.20.1 save into the converted 1.21.1 save.

The 1.20.1 player keeps Curios in ForgeCaps."curios:inventory"; NeoForge 1.21.1 keeps them in
"neoforge:attachments"."curios:inventory". The save conversion did not carry them over, so this
fills every NEW slot list that is still empty with the OLD stacks, converted to 1.21 components by
restore_items.make_item. Both playerdata/<uuid>.dat and level.dat (Data.Player, used by
singleplayer) are patched. Run with the game closed; --apply writes after a zip backup.

Usage: python3 tools/saveport/restore_curios.py [--apply]
"""
import argparse
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from restore_items import OLD, NEW, PLAYER, ROOT, dig, listvals, load_dat, load_map, make_item, save_dat, slot_of  # noqa: E402

BACKUP = os.path.join(ROOT, 'saves', 'Solito solamente backup-antes-curios-1.21.1-2026-11-20.zip')
STACKS = ('StacksHandler', 'Stacks')


def player_root(dat, is_level):
    return dig(dat['val'], 'Data', 'Player') if is_level else dat['val']


def game_running():
    out = subprocess.run(['pgrep', '-af', 'java'], capture_output=True, text=True).stdout
    return any("Pipinha's Village" in line for line in out.splitlines())


def world_open():
    """True while a world is loaded: the game runs and latest.log shows no save-on-exit after the last start."""
    if not game_running():
        return False
    try:
        with open(os.path.join(ROOT, 'logs', 'latest.log'), errors='replace') as f:
            log = f.read()
    except OSError:
        return True
    return log.rfind('Starting integrated minecraft server') > log.rfind('All dimensions are saved')


def restore(old_player, new_player, t, label, report):
    old_c = dig(old_player, 'ForgeCaps', 'curios:inventory', 'Curios')
    new_c = dig(new_player, 'neoforge:attachments', 'curios:inventory', 'Curios')
    if old_c is None or new_c is None:
        report.append(f'{label}: Curios list missing in OLD or NEW, skipped')
        return 0
    new_by_id = {dig(e, 'Identifier'): e for e in listvals(new_c)}
    filled = 0
    for oe in listvals(old_c):
        ident = dig(oe, 'Identifier')
        o_items = listvals(dig(oe, *STACKS, 'Items'))
        if not o_items:
            continue
        ne = new_by_id.get(ident)
        if ne is None:
            report.append(f'{label}: slot type "{ident}" does not exist in 1.21.1, items NOT restored: '
                          + ', '.join(o['id'][1] for o in o_items))
            continue
        stacks = dig(ne, *STACKS)
        if listvals(dig(stacks, 'Items')):
            report.append(f'{label}: "{ident}" already has items in 1.21.1, left as is')
            continue
        size = stacks['Size'][1]
        notes = []
        items = []
        for o in o_items:
            slot = int(slot_of(o))
            if slot >= size:
                notes.append(f'{o["id"][1]} (slot {slot} >= size {size})')
                continue
            items.append(make_item(o, t, 'Slot', 3, notes, slot=slot))
        if notes:
            report.append(f'{label}: "{ident}" notes: ' + '; '.join(map(str, notes)))
        if items:
            stacks['Items'] = (9, (10, items))
            filled += len(items)
            report.append(f'{label}: "{ident}" <- ' + ', '.join(
                f'{i["id"][1]} x{i["count"][1]}' + (f' {sorted(i["components"][1])}' if 'components' in i else '')
                for i in items))
    return filled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    t = load_map()
    targets = [(os.path.join('playerdata', PLAYER + '.dat'), False), ('level.dat', True)]
    report = []
    touched = []
    for rel, is_level in targets:
        old_dat = load_dat(os.path.join(OLD, rel))
        new_path = os.path.join(NEW, rel)
        new_dat = load_dat(new_path)
        n = restore(player_root(old_dat, is_level), player_root(new_dat, is_level), t, rel, report)
        if n:
            touched.append((new_path, new_dat))
    print('\n'.join(report))
    if not args.apply:
        print(f'dry-run: {len(touched)} file(s) would be written')
        return
    if world_open():
        sys.exit('world is open: leave the world or close Minecraft first, nothing written')
    with zipfile.ZipFile(BACKUP, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel, _ in targets:
            z.write(os.path.join(NEW, rel), rel)
    for path, dat in touched:
        save_dat(path, dat)
    print(f'applied: {len(touched)} file(s) written, backup {BACKUP}')


if __name__ == '__main__':
    main()
