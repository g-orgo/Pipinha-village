#!/usr/bin/env python3
"""Carry the Society villager affinity from a 1.20.1 save into its converted 1.21.1 copy.

Affinity lives on the player, not in the world: KubeJSPersistentData.npcData.<npcId> with
friendship (0..500, -1 before the first chat; 100 points = one heart), dayLastChatted,
dayLastGifted, dayLastPlaced, dayLastMercantil and maxGifted. It is read by
kubejs/server_scripts/npcs/npcInteraction.js and faceNote.js under the same key in KubeJS 7.
Singleplayer keeps the player in level.dat (Data.Player) and in playerdata/<uuid>.dat; both
are handled, matched by file name.

Merge rule per NPC: the destination entry is replaced by the source entry only when the
destination has no entry or a lower friendship, so affinity earned after the conversion is
never lowered. Chunk regeneration (regen_chunks.py, fix_cut_houses.py) never writes player
data, so it keeps the affinity as is.

Usage: affinity.py <src_save> <dst_save> [--apply]   (default is a dry run; game closed)
Also called by convert_save.py run, after the copy.
"""

import gzip
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'pack_tools'))

from nbtmini import NBTReader  # noqa: E402
from nbtwrite import w_tag  # noqa: E402

TAG_COMPOUND = 10
KJS_KEY = 'KubeJSPersistentData'
NPC_KEY = 'npcData'


def _read(path):
    with gzip.open(path, 'rb') as f:
        return NBTReader(f.read()).read_tag()


def _player(root, is_level):
    """Returns the player compound dict, or None (level.dat without a player)."""
    if not is_level:
        return root
    data = root.get('Data', (TAG_COMPOUND, {}))[1]
    return data['Player'][1] if 'Player' in data else None


def _friendship(entry):
    v = entry[1].get('friendship')
    return float(v[1]) if v else -1.0


def _pairs(src, dst):
    out = [('level.dat', True)]
    pd = os.path.join(src, 'playerdata')
    if os.path.isdir(pd):
        out += [(os.path.join('playerdata', n), False) for n in sorted(os.listdir(pd)) if n.endswith('.dat')]
    return [(rel, lvl) for rel, lvl in out
            if os.path.isfile(os.path.join(src, rel)) and os.path.isfile(os.path.join(dst, rel))]


def merge_affinity(src, dst, apply):
    """Returns a list of report lines; writes dst only when apply is true and something changed."""
    lines = []
    for rel, is_level in _pairs(src, dst):
        s_root = _read(os.path.join(src, rel))[2]
        d_name, d_tid, d_root = _read(os.path.join(dst, rel))
        s_player, d_player = _player(s_root, is_level), _player(d_root, is_level)
        if s_player is None or d_player is None:
            continue
        s_npc = s_player.get(KJS_KEY, (TAG_COMPOUND, {}))[1].get(NPC_KEY, (TAG_COMPOUND, {}))[1]
        if not s_npc:
            lines.append(f'{rel}: source has no npcData')
            continue
        d_kjs = d_player.setdefault(KJS_KEY, (TAG_COMPOUND, {}))[1]
        d_npc = d_kjs.setdefault(NPC_KEY, (TAG_COMPOUND, {}))[1]
        changed = []
        for npc_id, entry in sorted(s_npc.items()):
            cur = d_npc.get(npc_id)
            if cur is None or _friendship(cur) < _friendship(entry):
                old = 'none' if cur is None else f'{_friendship(cur):g}'
                d_npc[npc_id] = entry
                changed.append(f'{npc_id} {old}->{_friendship(entry):g}')
        kept = len(s_npc) - len(changed)
        lines.append(f'{rel}: {len(s_npc)} npcs in source, {kept} already ok, '
                     f'{len(changed)} restored' + (f' ({", ".join(changed)})' if changed else ''))
        if changed and apply:
            with gzip.open(os.path.join(dst, rel), 'wb') as f:
                f.write(w_tag(d_name or '', d_tid, d_root))
    if not lines:
        lines.append('no player files found in both saves')
    return lines


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    apply = '--apply' in argv
    for line in merge_affinity(argv[0], argv[1], apply):
        print(('' if apply else '[dry] ') + line)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
