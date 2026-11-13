"""Restore quest/chapter/task/reward icons lost in the 1.21.1 port.

FTB Quests 1.21.1 reads `icon` as an item stack compound; the plain string icons written by
port.py were dropped when the game re-saved the files. This copies every icon from the 1.20.1
instance (read only) into the matching object (same hex id) of the 1.21.1 files, written inline
as `icon: { count: 1, id: "..." }`. Existing compound icons are left alone; string icons in the
1.21.1 files are turned into compounds. Text is edited line by line to keep the game's formatting.
Usage: python3 -I restore_icons.py [--dry-run]"""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snbt, convert
from snbt import Raw

SRC = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley/config/ftbquests/quests"
DST = convert.ROOT + "/config/ftbquests/quests"
DRY = '--dry-run' in sys.argv
HEX_ID = re.compile(r'^(\t*)id: "([0-9A-F]{16})"$')


def inline(v):
    """Serialize a value on one line, FTB Quests style."""
    if isinstance(v, dict):
        return '{ ' + ', '.join(f'{k if re.fullmatch(r"[A-Za-z0-9_]+", k) else snbt.q(k)}: {inline(v[k])}'
                                for k in sorted(v)) + ' }'
    if isinstance(v, list):
        return '[' + ', '.join(inline(x) for x in v) + ']'
    if isinstance(v, Raw):
        return str(v)
    if isinstance(v, str):
        return snbt.q(v)
    return str(v)


def as_compound(icon):
    new = convert.stack(icon, 'icon')
    if new is None:
        return None
    if isinstance(new, str):
        new = {'id': new, 'count': Raw('1')}
    return new


def collect(node, out, file_icon_key):
    if isinstance(node, dict):
        if 'icon' in node:
            key = str(node['id']) if 'id' in node and re.fullmatch(r'[0-9A-F]{16}', str(node['id'])) else file_icon_key
            if key:
                out[key] = node['icon']
        for v in node.values():
            collect(v, out, None)
    elif isinstance(node, list):
        for v in node:
            collect(v, out, None)


def has_icon(lines, start, indent):
    """True if the object whose id line is at `start` already has an icon key at the same indent."""
    # Scan up to the object's opening brace and down to its closing brace.
    for step in (-1, 1):
        i = start + step
        while 0 <= i < len(lines):
            line = lines[i]
            stripped_indent = len(line) - len(line.lstrip('\t'))
            if stripped_indent < len(indent) and line.strip():
                break
            if line.startswith(indent + 'icon:'):
                return i
            i += step
    return None


total = 0
for src in sorted(glob.glob(SRC + '/**/*.snbt', recursive=True)):
    rel = os.path.relpath(src, SRC)
    dst = os.path.join(DST, rel)
    if '/lang/' in '/' + rel or not os.path.exists(dst):
        continue
    icons = {}
    collect(snbt.loads(open(src).read()), icons, '__file__')
    if not icons:
        continue
    lines = open(dst).read().split('\n')
    changed = 0
    # Top-level (chapter) icon: object id line at one tab.
    for n, line in enumerate(list(lines)):
        m = HEX_ID.match(line)
        if not m:
            continue
        indent, oid = m.group(1), m.group(2)
        icon = icons.get(oid)
        if icon is None and len(indent) == 1:
            icon = icons.get('__file__')
        if icon is None:
            continue
        at = has_icon(lines, n, indent)
        if at is not None and not lines[at].strip().startswith('icon: "'):
            continue  # already a compound icon
        comp = as_compound(icon)
        if comp is None:
            continue
        new_line = f'{indent}icon: {inline(comp)}'
        if at is not None:
            lines[at] = new_line
        else:
            lines[n] = new_line + '\n' + lines[n]
        changed += 1
    if changed:
        total += changed
        print(f'{rel}: {changed}')
        if not DRY:
            open(dst, 'w').write('\n'.join(lines))
print('total', total)
