#!/usr/bin/env python3
"""Port a Minecraft 1.20.1 world save to the 1.21.1 ids used by this pack.

Usage:
  convert_save.py scan <save> [--out PATH]         read-only report (default: REPORT.md)
  convert_save.py run <src_save> <dst_save> [--lost PATH]
                                                   copy src to dst (dst must not exist),
                                                   then remap dst in place. src is never written.
                                                   --lost writes the dropped-items list.

Stdlib only. Mappings come from id_map.tsv in this folder, plus namespace renames from
tools/modcheck/namespace_renames.tsv (fallback list below when the file is missing).
Notes:
- Lookup order: exact id row, then namespace rule (path unchanged), then unmapped.
- Ids listed in id_map.tsv with kind 'ignore' are never reported (false positives).
- Block entities: renamed when mapped and kept; dropped when mapped to air, or when their
  namespace is unknown. Dropped block entities that hold items are listed as lost items.
- DataVersion is never touched, so the game's DataFixer upgrades the world on load.
- Furniture that changes mod is turned and reconnected by state_rules.tsv (state_rules.py);
  check the table with orient_check.py and fix an already converted save with fix_orientation.py.
- Villager affinity (player KubeJSPersistentData.npcData) is checked against src after the
  copy and restored per NPC when missing or lower (affinity.py; also runs on its own).
"""

import glob
import gzip
import os
import re
import shutil
import struct
import sys
import zipfile
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MODS = os.path.join(ROOT, 'mods')
NS_FILE = os.path.join(ROOT, 'tools', 'modcheck', 'namespace_renames.tsv')
for sub in ('pack_tools', 'lcport'):
    sys.path.insert(0, os.path.join(ROOT, 'tools', sub))

from nbtmini import NBTReader  # noqa: E402
from nbtwrite import w_tag  # noqa: E402
from retrofit_hedges import write_region  # noqa: E402
import lc_ids  # noqa: E402
from affinity import merge_affinity  # noqa: E402
import state_rules  # noqa: E402

MAP_FILE = os.path.join(HERE, 'id_map.tsv')
DEFAULT_REPORT = os.path.join(HERE, 'REPORT.md')
AIR = 'minecraft:air'
KITCHEN_SINK_OLD = 'cfm:kitchen_sink'
KITCHEN_SINK_NEW = 'refurbished_furniture:kitchen_sink'
BE_KEEP_KEYS = ('id', 'x', 'y', 'z', 'keepPacked')  # kept on the kitchen sink block entity
BE_DROP = {'redeco:side_table_block_entity', 'redeco:sword_mount_block_entity'}
CREATE_RE = re.compile(r'\.create\(\s*"([a-z0-9_.-]+:[a-z0-9_./-]+)"')
KINDS = ('block', 'be', 'item', 'entity')
FALLBACK_NS = {
    'miners_delight': 'minersdelight',
    'numismatics_utils': 'numismaticsutils',
    'largemeals': 'large_meals',
    'bonsaitrees3': 'bonsaitrees4',
    'domesticationinnovation': 'redomesticate',
}


def parse_pairs(text, sep):
    out = {}
    for part in filter(None, text.split(';')):
        k, _, v = part.partition(sep)
        out[k] = v
    return out


def load_ns_rules():
    if not os.path.isfile(NS_FILE):
        return dict(FALLBACK_NS), 'fallback list'
    rules = {}
    with open(NS_FILE, encoding='utf-8') as f:
        for line in f:
            cols = line.rstrip('\n').split('\t')
            if len(cols) < 2 or cols[0] in ('', 'old_ns') or cols[0].startswith('#'):
                continue
            rules[cols[0]] = cols[1]
    return rules, NS_FILE


class Table:
    def __init__(self):
        self.blocks, self.items, self.bes, self.entities = {}, {}, {}, {}
        self.ignore = set()
        self.ns_rules, self.ns_source = load_ns_rules()
        self.prefixes = []

    def add_row(self, old, new, kind, ren, sets):
        if kind == 'ignore':
            self.ignore.add(old)
            return
        base, _, brk = new.partition('[')
        sets_all = parse_pairs(brk.rstrip(']').replace(',', ';'), '=')
        sets_all.update(parse_pairs(sets, '='))
        entry = (base, parse_pairs(ren, '>'), sets_all)
        if kind in ('block', 'any'):
            self.blocks[old] = entry
        if kind in ('item', 'any'):
            self.items[old] = (base, {}, {})
        if kind == 'be':
            self.bes[old] = entry
        if kind == 'entity':
            self.entities[old] = (base, {}, {})


def load_map():
    t = Table()
    with open(MAP_FILE, encoding='utf-8') as f:
        next(f)
        for line in f:
            if not line.strip():
                continue
            cols = line.rstrip('\n').split('\t') + ['', '', '']
            old, new, kind, ren, sets = cols[:5]
            if old.endswith(':*'):
                t.prefixes.append((old[:-2], new[:-2]))
                continue
            t.add_row(old, new, kind, ren, sets)
    return t


def ns_of(ident):
    return ident.partition(':')[0]


_ASSETS = None


def asset_exists(ns, path):
    """True when a mod jar ships blockstate, block or item model json for ns:path."""
    global _ASSETS
    if _ASSETS is None:
        _ASSETS = set()
        for jar in glob.glob(os.path.join(MODS, '*.jar')):
            try:
                with zipfile.ZipFile(jar) as z:
                    for name in z.namelist():
                        parts = name.split('/')
                        if len(parts) >= 4 and parts[0] == 'assets' and name.endswith('.json'):
                            _ASSETS.add((parts[1], '/'.join(parts[2:])[:-5]))
            except zipfile.BadZipFile:
                continue
    return any((ns, rel) in _ASSETS for rel in
               (f'blockstates/{path}', f'models/block/{path}', f'models/item/{path}'))


def lookup(table_dict, t, ident):
    """Exact row first, then namespace rule. Returns (base, renames, sets) or None."""
    if ident in t.ignore or ':' not in ident:
        return None
    if ident in table_dict:
        return table_dict[ident]
    ns, _, path = ident.partition(':')
    for old_ns, new_ns in t.prefixes:
        if ns == old_ns:
            return (f'{new_ns}:{path}', {}, {})
    if ns == 'toms_storage' and path.startswith('ts.') and asset_exists(ns, path[3:]):
        return (f'{ns}:{path[3:]}', {}, {})  # Tom's Storage dropped the ts. prefix in 1.21
    if ns in t.ns_rules:
        return (f'{t.ns_rules[ns]}:{path}', {}, {})
    return None


def mod_ids():
    ids = {'minecraft'}
    for jar in glob.glob(os.path.join(MODS, '*.jar')):
        try:
            with zipfile.ZipFile(jar) as z:
                for name in ('META-INF/neoforge.mods.toml', 'META-INF/mods.toml'):
                    if name in z.namelist():
                        ids.update(re.findall(r'modId\s*=\s*"([^"]+)"', z.read(name).decode('utf-8', 'replace')))
        except zipfile.BadZipFile:
            continue
    return ids


def kubejs_known():
    """KubeJS registrations: lc_ids scan plus explicit namespaced .create("ns:path") calls."""
    items, blocks = lc_ids._scan_kubejs_registrations()
    items, blocks = set(items), set(blocks)
    pattern = os.path.join(ROOT, 'kubejs', 'startup_scripts', '**', '*.js')
    for path in glob.glob(pattern, recursive=True):
        with open(path, encoding='utf-8', errors='replace') as f:
            found = set(CREATE_RE.findall(f.read()))
        items |= found
        blocks |= found
    return items, blocks


def known_namespaces(kube_items, kube_blocks):
    ns = mod_ids()
    for ident in list(kube_items) + list(kube_blocks):
        ns.add(ns_of(ident))
    return ns


def profile_exists(name):
    suffix = f'/{name}.json'
    for jar in glob.glob(os.path.join(MODS, '*.jar')):
        try:
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    if n.endswith(suffix) and 'profile' in n.lower():
                        return True
        except zipfile.BadZipFile:
            continue
    return False


def chunks_of(path):
    """Return (raw file bytes, [(index, root_or_None, error_or_None)]) for one .mca file."""
    raw = open(path, 'rb').read()
    out = []
    if len(raw) < 8192:  # empty or truncated region: no chunk table to read
        return raw, out
    for i in range(1024):
        loc = struct.unpack('>I', raw[4 * i:4 * i + 4])[0]
        if not loc:
            continue
        off = (loc >> 8) * 4096
        try:
            ln = struct.unpack('>I', raw[off:off + 4])[0]
            comp = raw[off + 4]
            payload = raw[off + 5:off + 4 + ln]
            if comp == 1:
                data = gzip.decompress(payload)
            elif comp == 2:
                data = zlib.decompress(payload)
            elif comp == 3:
                data = payload
            else:
                raise ValueError(f'compression type {comp} not handled')
            out.append((i, NBTReader(data).read_tag()[2], None))
        except Exception as exc:  # report and keep going
            out.append((i, None, f'{type(exc).__name__}: {exc}'))
    return raw, out


def read_dat(path):
    with gzip.open(path, 'rb') as f:
        return NBTReader(f.read()).read_tag()


def convert_props(name, rule, props, accepted):
    """New block props for an old block state: state_rules.tsv (turn and connection
    values between mods), then prop renames, forced values and the accepted-state filter."""
    new, ren, sets = rule
    srule = state_rules.find(name, new)
    if srule:
        props = state_rules.apply(srule, props)
    if new.startswith('redecorate:'):
        ren = dict(ren, upholstery='fabric')
    props = {ren.get(k, k): v for k, v in props.items()}
    props.update(sets)
    acc = None if new.startswith('minecraft:') else accepted(new)
    if acc is not None:
        props = {k: v for k, v in props.items() if k in acc and (acc[k] is None or v in acc[k])}
    return props


def val(d, key, default=None):
    return d[key][1] if key in d else default


class Job:
    def __init__(self, mode, t, namespaces, known_blocks, known_items, save):
        self.mode = mode
        self.t = t
        self.namespaces = namespaces
        self.known = {'block': known_blocks, 'item': known_items}
        self.save = save
        self.seen = {k: Counter() for k in KINDS}
        self.lost = []  # (where, be_id, x, y, z, item_id, count)
        self.changed = False
        self.acc_cache = {}
        self.where = ''
        self.applied = Counter()  # run mode: remapped occurrences per kind

    def accepted(self, block):
        if block not in self.acc_cache:
            self.acc_cache[block] = lc_ids.accepted_states(block)
        return self.acc_cache[block]

    def block_entry(self, d):
        name = val(d, 'Name')
        self.seen['block'][name] += 1
        rule = lookup(self.t.blocks, self.t, name)
        if rule is None or self.mode != 'run':
            return
        self.applied['block'] += 1
        new, ren, sets = rule
        if new == AIR:
            d['Name'] = (8, AIR)
            d.pop('Properties', None)
            self.changed = True
            return
        props = {k: v[1] for k, v in d['Properties'][1].items()} if 'Properties' in d else {}
        props = convert_props(name, rule, props, self.accepted)
        d['Name'] = (8, new)
        if props:
            d['Properties'] = (10, {k: (8, v) for k, v in sorted(props.items())})
        else:
            d.pop('Properties', None)
        self.changed = True

    def item_entry(self, d):
        ident = val(d, 'id')
        self.seen['item'][ident] += 1
        rule = lookup(self.t.items, self.t, ident)
        if rule is None or self.mode != 'run':
            return
        if rule[0] != ident:
            d['id'] = (8, rule[0])
            self.changed = True
            self.applied['item'] += 1

    def entity_entry(self, d):
        ident = val(d, 'id')
        self.seen['entity'][ident] += 1
        rule = lookup(self.t.entities, self.t, ident)
        if rule is None or self.mode != 'run':
            return
        if rule[0] != ident:
            d['id'] = (8, rule[0])
            self.changed = True
            self.applied['entity'] += 1

    def visit(self, d, key):
        if key == 'palette' and 'Name' in d:
            self.block_entry(d)
        elif key in ('Entities', 'Passengers') and 'id' in d:
            self.entity_entry(d)
        elif 'id' in d and 'Count' in d and d['id'][0] == 8:
            self.item_entry(d)

    def walk(self, tid, v, key):
        if tid == 10:
            self.visit(v, key)
            for k, (t, sub) in list(v.items()):
                self.walk(t, sub, k)
        elif tid == 9 and v[0] == 10:
            for d in v[1]:
                self.visit(d, key)
                for k, (t, sub) in list(d.items()):
                    self.walk(t, sub, k)

    def block_entities(self, root):
        lst = root.get('block_entities')
        if not lst or lst[0] != 9:
            return
        et, items = lst[1]
        keep = []
        for be in items:
            bid = val(be, 'id', '')
            self.seen['be'][bid] += 1
            if bid in BE_DROP:
                self.drop_be(be, bid)
                continue
            if bid == KITCHEN_SINK_OLD and 'refurbished_furniture' in self.namespaces:
                self.shrink_kitchen_sink(be, bid)
                keep.append(be)
                continue
            rule = lookup(self.t.bes, self.t, bid)
            target = bid if rule is None else rule[0]
            # Only installed namespaces are known: a BE whose namespace has no mod jar is dropped.
            if target == AIR or ':' not in target or ns_of(target) not in self.namespaces:
                self.drop_be(be, bid)
                continue
            if rule is not None and self.mode == 'run':
                be['id'] = (8, target)
                self.changed = True
                self.applied['be'] += 1
            keep.append(be)
        if len(keep) != len(items):
            root['block_entities'] = (9, (et, keep))
            self.changed = True

    def drop_be(self, be, bid):
        if self.mode == 'run':
            self.changed = True
            self.applied['be_dropped'] += 1
        self.record_items(be, bid)

    def record_items(self, be, bid):
        items = val(be, 'Items')
        if not items or items[0] != 9:
            return
        pos = [val(be, c, 0) for c in ('x', 'y', 'z')]
        for it in items[1][1]:
            self.lost.append((self.where, bid, *pos, val(it, 'id', '?'), val(it, 'Count', 0)))

    def shrink_kitchen_sink(self, be, bid):
        """cfm kitchen sink BE becomes refurbished_furniture:kitchen_sink; only BE_KEEP_KEYS stay.
        The BE does not carry its block, so every cfm kitchen sink BE is treated the same way."""
        for k in [k for k in be if k not in BE_KEEP_KEYS]:
            if k == 'Items':
                self.record_items(be, bid)
            if self.mode == 'run':
                del be[k]
        if self.mode == 'run':
            be['id'] = (8, KITCHEN_SINK_NEW)
            self.changed = True
            self.applied['be'] += 1

    def chunk(self, root):
        self.walk(10, root, '')
        self.block_entities(root)


def region_files(save):
    return sorted(glob.glob(os.path.join(save, '**', '*.mca'), recursive=True))


def dat_files(save):
    out = [os.path.join(save, 'level.dat')]
    out += sorted(glob.glob(os.path.join(save, 'playerdata', '*.dat')))
    return [p for p in out if os.path.isfile(p)]


def is_known(job, kind, ident):
    if ':' not in ident or ident in job.t.ignore:
        return True  # not an id (e.g. DUMMY) or a known false positive
    if kind == 'block':
        return ident in job.known['block']
    if kind == 'item':
        return ident in job.known['item']
    return ns_of(ident) in job.namespaces  # be, entity: namespace level only


def strings_under(node, out, path=''):
    if isinstance(node, tuple) and len(node) == 2 and isinstance(node[0], int):
        tid, v = node
        if tid == 8:
            out.append((path, v))
        elif tid == 10:
            for k, sub in v.items():
                strings_under(sub, out, f'{path}.{k}')
        elif tid == 9:
            for i, item in enumerate(v[1]):
                strings_under((v[0], item), out, f'{path}[{i}]')


def level_info(save, namespaces):
    lines = []
    _, _, root = read_dat(os.path.join(save, 'level.dat'))
    data = root['Data'][1]
    gen_root = data.get('WorldGenSettings', (10, {}))[1]
    dims = gen_root.get('dimensions', (10, {}))[1]
    lines += ['| dimension | dimension type | generator | namespace known |', '|---|---|---|---|']
    profiles = []
    for dim_id, (_, dim) in dims.items():
        dtype = val(dim, 'type', '')
        gen = dim.get('generator', (10, {}))[1]
        gtype = val(gen, 'type', '')
        ns = ns_of(dim_id)
        lines.append(f'| {dim_id} | {dtype} | {gtype} | {"yes" if ns in namespaces else "no"} |')
        strs = []
        strings_under((10, gen), strs)
        profiles += [(p, v) for p, v in strs if 'profile' in p.lower()]
    lines += ['', 'Generator profile values (path, value, exists as json in a mod jar):', '']
    if not profiles:
        lines.append('- none found')
    for path, v in profiles:
        lines.append(f'- `{path}` = `{v}`: {"yes" if profile_exists(v) else "no"}')
    return lines


def fmt_table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return out


def process_save(save, job):
    chunks, errors, regions = 0, [], 0
    for path in region_files(save):
        regions += 1
        rel = os.path.relpath(path, save)
        _, items = chunks_of(path)
        for idx, root, err in items:
            if err:
                errors.append((rel, idx, err))
                continue
            chunks += 1
            job.where = f'{rel} chunk {idx}'
            job.chunk(root)
    for path in dat_files(save):
        _, tid, root = read_dat(path)
        job.where = os.path.relpath(path, save)
        job.walk(tid, root, '')
    return regions, chunks, errors


def scan_block_be_counts(job):
    return {k: Counter({i: c for i, c in job.seen[k].items() if i}) for k in KINDS}


def run_scan(save, t, out_path):
    kitems, kblocks = kubejs_known()
    kb, ki = lc_ids.scan_known_ids()
    kb, ki = set(kb) | kblocks, set(ki) | kitems
    namespaces = known_namespaces(kitems, kblocks)
    job = Job('scan', t, namespaces, kb, ki, save)
    regions, chunks, errors = process_save(save, job)
    lines = ['# Save port report', '', f'Source: `{save}` (read only, scan mode).', '']
    lines += ['## Totals', '']
    lines += [f'- region files: {regions}, chunks decoded: {chunks}, decode errors: {len(errors)}']
    lines += [f'- error: `{e[0]}` chunk {e[1]}: {e[2]}' for e in errors[:20]]
    lines += [f'- namespace rules from: `{t.ns_source}`', '']
    lines.append('Counts are palette entries, block entities, item stacks and entities seen (not block positions).')
    lines.append('')
    lines += ['| kind | occurrences | distinct ids | mapped distinct | unmapped distinct |', '|---|---|---|---|---|']
    unmapped = {}
    for kind in KINDS:
        seen = job.seen[kind]
        table = {'block': t.blocks, 'be': t.bes, 'item': t.items, 'entity': t.entities}[kind]
        mapped = [i for i in seen if lookup(table, t, i) is not None]
        um = Counter({i: c for i, c in seen.items() if i not in mapped and not is_known(job, kind, i)})
        unmapped[kind] = um
        lines.append(f'| {kind} | {sum(seen.values())} | {len(seen)} | {len(mapped)} | {len(um)} |')
    lines.append('')
    for kind, label in (('block', 'Blocks'), ('be', 'Block entities'), ('item', 'Items'), ('entity', 'Entities')):
        table = {'block': t.blocks, 'be': t.bes, 'item': t.items, 'entity': t.entities}[kind]
        rows = []
        for i, c in job.seen[kind].most_common():
            r = lookup(table, t, i)
            if r is not None:
                rows.append((i, r[0], c))
        lines += [f'## Mapped {label.lower()}', '']
        lines += fmt_table(['old id', 'new id', 'occurrences'], rows) if rows else ['- none']
        lines.append('')
    for kind, label in (('block', 'blocks'), ('be', 'block entities'), ('item', 'items'), ('entity', 'entities')):
        um = unmapped[kind]
        ns = Counter()
        for i, c in um.items():
            ns[ns_of(i) if ':' in i else i] += c
        lines += [f'## Unmapped {label}: by namespace', '']
        lines += fmt_table(['namespace', 'occurrences'], ns.most_common()) if ns else ['- none']
        lines += ['', f'Top 40 unmapped {label}:', '']
        top = um.most_common(40)
        lines += fmt_table(['id', 'occurrences'], top) if top else ['- none']
        if len(um) > 40:
            lines.append(f'- {len(um) - 40} more distinct ids not listed')
        lines.append('')
    lines += [f'## Itens perdidos ({len(job.lost)} stacks)', '']
    lines += [f'- {w}: {b} at {x},{y},{z}: {i} x{c}' for w, b, x, y, z, i, c in job.lost] or ['- none']
    lines.append('')
    lines += ['## level.dat', '']
    lines += level_info(save, namespaces)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'chunks={chunks} regions={regions} decode_errors={len(errors)} lost_stacks={len(job.lost)} report={out_path}')
    for kind in KINDS:
        top = unmapped[kind].most_common(15)
        print(f'top unmapped {kind}: ' + ', '.join(f'{i} x{c}' for i, c in top))
    return len(errors)


def run_convert(src, dst, t, lost_path):
    if os.path.exists(dst):
        sys.exit(f'refusing: destination exists: {dst}')
    shutil.copytree(src, dst)
    lock = os.path.join(dst, 'session.lock')
    if os.path.exists(lock):
        os.remove(lock)  # copy only; the game recreates it on open
    kitems, kblocks = kubejs_known()
    kb, ki = lc_ids.scan_known_ids()
    kb, ki = set(kb) | kblocks, set(ki) | kitems
    job = Job('run', t, known_namespaces(kitems, kblocks), kb, ki, dst)
    errors = 0
    for path in region_files(dst):
        raw, items = chunks_of(path)
        changed = {}
        job.where = os.path.relpath(path, dst)
        for idx, root, err in items:
            if err:
                errors += 1
                continue
            job.changed = False
            job.where = f'{os.path.relpath(path, dst)} chunk {idx}'
            job.chunk(root)
            if job.changed:
                changed[idx] = root
        if changed:
            write_region(path, raw, changed)
    for path in dat_files(dst):
        name, tid, root = read_dat(path)
        job.changed = False
        job.where = os.path.relpath(path, dst)
        job.walk(tid, root, '')
        if job.changed:
            with gzip.open(path, 'wb') as f:
                f.write(w_tag(name or '', tid, root))
    # Society villager affinity (player KubeJSPersistentData.npcData): checked against the
    # source and restored per NPC when missing or lower, see affinity.py.
    for line in merge_affinity(src, dst, True):
        print(f'affinity: {line}')
    if lost_path:
        with open(lost_path, 'w', encoding='utf-8') as f:
            for w, b, x, y, z, i, c in job.lost:
                f.write(f'{w}\t{b}\t{x},{y},{z}\t{i}\t{c}\n')
    print(f'run done: dst={dst} decode_errors={errors} lost_stacks={len(job.lost)} applied={dict(job.applied)}')


def main(argv):
    if len(argv) >= 2 and argv[0] == 'scan':
        out = DEFAULT_REPORT
        if '--out' in argv:
            out = argv[argv.index('--out') + 1]
        return 1 if run_scan(argv[1], load_map(), out) else 0
    if len(argv) >= 3 and argv[0] == 'run':
        lost = argv[argv.index('--lost') + 1] if '--lost' in argv else None
        run_convert(argv[1], argv[2], load_map(), lost)
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
