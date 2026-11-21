"""Per-family block state rules for blocks that change mod in the 1.20.1 -> 1.21.1 port.

Shared by convert_save.py, fix_orientation.py and tools/lcport/port_palettes.py, so the
save, the in-place fix and the Lost Cities palettes turn and connect furniture the same way.

state_rules.tsv columns: old_glob, new_glob, rotate, map, note.
- rotate: clockwise quarter turns applied to the facing after the map (0..3).
- map: ';' separated entries, read from the OLD state before the turn:
    src>dst1,dst2[:a=b/c=d]  copy the value of src to each dst, translating the listed
                             values (unlisted values pass through); src is removed.
    @shelf_sides>dst         Re:Deco shelf north/east/south/west booleans -> dst
                             single/left/right/middle relative to the facing.
Rules were measured with orient_check.py (voxelized models of both jars).
"""

import fnmatch
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(HERE, 'state_rules.tsv')
DIRS = ['north', 'east', 'south', 'west']  # clockwise seen from above
FACING_KEYS = ('facing', 'horizontal_facing')
_RULES = None


def _parse_map(text):
    entries = []
    for part in filter(None, (p.strip() for p in text.split(';'))):
        src, _, rest = part.partition('>')
        dsts, _, table = rest.partition(':')
        values = dict(kv.split('=', 1) for kv in table.split('/') if '=' in kv)
        entries.append((src, dsts.split(','), values))
    return entries


def load():
    global _RULES
    if _RULES is None:
        _RULES = []
        with open(RULES_FILE, encoding='utf-8') as f:
            next(f)
            for line in f:
                cols = line.rstrip('\n').split('\t') + ['', '', '']
                if not cols[0] or cols[0].startswith('#'):
                    continue
                _RULES.append((cols[0], cols[1], int(cols[2] or 0) % 4, _parse_map(cols[3])))
    return _RULES


def find(old_id, new_id):
    """First rule whose globs match both ids, or None."""
    for rule in load():
        if fnmatch.fnmatchcase(old_id, rule[0]) and fnmatch.fnmatchcase(new_id, rule[1]):
            return rule
    return None


def turn(direction, quarters):
    if direction not in DIRS:
        return direction
    return DIRS[(DIRS.index(direction) + quarters) % 4]


def _shelf_sides(props):
    facing = props.get('facing', 'north')
    if facing not in DIRS:
        return 'single'
    cw = props.get(turn(facing, 1)) == 'true'
    ccw = props.get(turn(facing, 3)) == 'true'
    return {(True, True): 'middle', (True, False): 'right', (False, True): 'left'}.get((cw, ccw), 'single')


def apply(rule, props):
    """Return a new props dict for the new block, from the old block's props."""
    _old, _new, quarters, entries = rule
    out = dict(props)
    for src, dsts, values in entries:
        if src == '@shelf_sides':
            value = _shelf_sides(props)
            for d in DIRS:
                out.pop(d, None)
        elif src in props:
            value = values.get(props[src], props[src])
            out.pop(src, None)
        else:
            continue
        for dst in dsts:
            out[dst] = value
    if quarters:
        for key in FACING_KEYS:
            if key in out:
                out[key] = turn(out[key], quarters)
    return out


def changed_by(rule):
    """True when the rule turns the block or rewrites its state."""
    return bool(rule[2] or rule[3])
