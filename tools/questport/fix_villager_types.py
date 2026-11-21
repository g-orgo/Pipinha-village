"""Put back the villager type on society:villager icons and society:invitation task items.

The first 1.21.1 port turned these stacks into ftbquests:missing_item (the KubeJS items did not
exist yet) and the later repair restored only the id, so every villager icon showed the default
face and every invitation task accepted any invitation. This reads the type of each stack from the
1.20.1 chapters (read only), converts it with convert.stack (custom_data type plus the face
custom_model_data, same as the shop icons) and rewrites the matching 1.21.1 icon or item, found by
the id of the object that owns it. Idempotent; the game must be closed.

Usage: python3 -I fix_villager_types.py [--dry-run]"""
import glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snbt, convert
from snbt import Raw

SRC = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley/config/ftbquests/quests/chapters"
DST = convert.ROOT + "/config/ftbquests/quests/chapters"
DRY = '--dry-run' in sys.argv
IDS = ('society:villager', 'society:invitation')
KEY = re.compile(r'[A-Za-z0-9_]+')


def key(k): return k if KEY.fullmatch(k) else snbt.q(k)


def inline(v):
    if isinstance(v, Raw): return str(v)
    if isinstance(v, str): return snbt.q(v)
    return '{ ' + ', '.join(f'{key(k)}: {inline(v[k])}' for k in sorted(v)) + ' }'


def block(v, ind):
    """Multi-line compound in the layout FTB Quests writes for icons."""
    out = ['{']
    for k in sorted(v):
        x = v[k]
        out.append(ind + '\t' + key(k) + ': ' + (block(x, ind + '\t') if isinstance(x, dict) else inline(x)))
    return '\n'.join(out) + '\n' + ind + '}'


def collect(node, owner, out):
    """(owner id, key) -> converted stack, for every villager/invitation stack with a type."""
    if isinstance(node, dict):
        oid = str(node['id']) if re.fullmatch(r'[0-9A-F]{16}', str(node.get('id', ''))) else owner
        for k, v in node.items():
            if isinstance(v, dict) and str(v.get('id')) in IDS and 'type' in v.get('tag', {}):
                new = convert.stack(v, 'icon' if k == 'icon' else 'task', match=True)
                if k == 'icon': new.pop('count', None)  # the game writes icons without count
                out[(oid, k)] = new
            collect(v, oid, out)
    elif isinstance(node, list):
        for v in node: collect(v, owner, out)


def value_range(lines, n, indent, k):
    """Line range [a, b] of key k of the object whose id line is n, or None."""
    for step in (-1, 1):
        i = n + step
        while 0 <= i < len(lines):
            line = lines[i]
            if line.strip() and len(line) - len(line.lstrip('\t')) < len(indent): break
            if line.startswith(indent + k + ':'):
                if line.rstrip().endswith('{'):
                    j = i + 1
                    while not lines[j].startswith(indent + '}'): j += 1
                    return i, j
                return i, i
            i += step
    return None


total = 0
for src in sorted(glob.glob(SRC + '/*.snbt')):
    dst = os.path.join(DST, os.path.basename(src))
    stacks = {}
    collect(snbt.loads(open(src).read()), None, stacks)
    if not stacks or not os.path.exists(dst): continue
    lines = open(dst).read().split('\n')
    changed, missing = 0, set(stacks)
    for n in range(len(lines) - 1, -1, -1):  # bottom-up so replaced ranges do not shift pending ids
        m = re.match(r'^(\t*)id: "([0-9A-F]{16})"$', lines[n])
        if not m: continue
        indent, oid = m.groups()
        for k in ('icon', 'item'):
            new = stacks.get((oid, k))
            if new is None: continue
            missing.discard((oid, k))
            at = value_range(lines, n, indent, k)
            if at is None:
                print(f'  {oid} {k}: not found in 1.21.1'); continue
            text = indent + k + ': ' + (block(new, indent) if k == 'icon' else inline(new))
            if '\n'.join(lines[at[0]:at[1] + 1]) != text:
                lines[at[0]:at[1] + 1] = text.split('\n'); changed += 1
    for oid, k in sorted(missing): print(f'  {oid} {k}: owner id not in 1.21.1')
    print(f'{os.path.basename(dst)}: {len(stacks)} stacks, {changed} rewritten')
    total += changed
    if changed and not DRY: open(dst, 'w').write('\n'.join(lines))
print('total rewritten', total, '(dry run)' if DRY else '')
