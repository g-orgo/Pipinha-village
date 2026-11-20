#!/usr/bin/env python3
"""Repair item data lost when "Solito solamente" was converted from 1.20.1 to 1.21.1.

Reads the untouched 1.20.1 save (OLD, read only) and repairs the converted 1.21.1 save (NEW).
Spec: tools/saveport/RESTORE_SPEC.md. Dry-run by default; --apply writes into NEW only.
"""
import argparse
import glob
import gzip
import os
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'pack_tools'))

from convert_save import chunks_of, load_map, lookup  # noqa: E402
from nbtmini import NBTReader  # noqa: E402
from nbtwrite import w_tag  # noqa: E402
from retrofit_hedges import write_region  # noqa: E402

OLD = os.path.normpath(os.path.join(ROOT, '..', 'Society: Sunlit Valley', 'saves', 'Solito solamente'))
NEW = os.path.join(ROOT, 'saves', 'Solito solamente')
BACKUP = os.path.join(ROOT, 'saves', 'Solito solamente backup-antes-restaurar-itens-2026-11-13.zip')
PLAYER = '94835476-d653-44a5-8e00-d4fe3441e950'
REPORT = os.path.join(HERE, 'RESTORE_REPORT.md')
PROBES = {'heater': (-10232, 78, 8341), 'crate': (-10234, 72, 8361)}
QUALITY_NAMES = {1: 'iron', 2: 'gold', 3: 'diamond'}

# Step 2: new BE id -> OLD BE id whose Items are copied when the NEW list is empty.
ITEMS_FILL = {
    'legendarysurvivaloverhaul:heater': 'legendarysurvivaloverhaul:legendarysurvivaloverhaulheater_block_entity',
    'bakery:storage': 'doapi:storage',
}
# Step 2: KubeJS 7 attachment inventories (NEW attachments.inventory, slot byte).
ATTACH_FILL = {'society:feeding_trough', 'shippingbin:basic_shipping_bin'}
# Step 2: bonsaitrees4 pot, OLD key -> NEW inv handler.
BONSAI_KEYS = {'saplingItemStacks': 'sapling', 'soilItemStacks': 'soil', 'outputItemStacks': 'output'}
# Step 3: OLD BE id -> NEW BE id, created where the block exists in NEW and the BE does not.
# doapi:storage -> bakery:storage: the bakery jar registers one STORAGE_ENTITY for every display/tray.
CREATE_MAP = {'doapi:cabinet': 'bakery:cabinet', 'doapi:storage': 'bakery:storage'}
SKIP_REASONS = {
    'supplementaries:jar': 'jar format not verified, skipped',
    'bountiful:board-be': 'skipped by spec',
    'create:clipboard': 'skipped by spec, text listed in report',
}


# ---------- tagged-tree helpers (compound = dict name -> (tid, val); list = (etid, [vals])) ----------

def is_item(d):
    return 'id' in d and d['id'][0] == 8 and any(k in d for k in ('Slot', 'slot', 'Count', 'count'))


def scan_items(node, depth=0, out=None):
    """Collect item compounds under node without descending into items."""
    out = [] if out is None else out
    if isinstance(node, dict):
        if is_item(node):
            out.append(node)
            return out
        if depth > 8:
            return out
        for t, v in node.values():
            if t in (9, 10):
                scan_val(t, v, depth + 1, out)
    return out


def scan_val(t, v, depth, out):
    if t == 10:
        scan_items(v, depth, out)
    elif t == 9 and v[0] in (9, 10):
        for e in v[1]:
            if v[0] == 10:
                scan_items(e, depth, out)
            else:
                scan_val(9, e, depth, out)


def listvals(lst):
    return lst[1] if lst else []


def dig(d, *keys):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k][1]
    return cur


def slot_of(it):
    for k in ('Slot', 'slot'):
        if k in it:
            return it[k][1]
    return None


def count_of(it):
    return it['count'][1] if 'count' in it else it['Count'][1]


def path_of(ident):
    return ident.split(':', 1)[-1]


def summary(be):
    if be is None:
        return 'absent'
    its = scan_items(be)
    parts = []
    for i in its[:12]:
        comps = sorted(i['components'][1]) if 'components' in i else '-'
        parts.append(f"slot {slot_of(i)} {i['id'][1]} x{count_of(i)} comps={comps}")
    return f"{be['id'][1]}: " + ('; '.join(parts) or 'empty') + f" (items={len(its)})"


# ---------- id remap and stack conversion ----------

def remap(t, ident):
    r = lookup(t.items, t, ident)
    return r[0] if r else ident


def convert_stack(old, t, notes):
    """Map a 1.20.1 stack tag onto 1.21.1 components. Returns dict name -> (tid, val) or None."""
    rest = dict(old['tag'][1]) if 'tag' in old else {}
    comps = {}
    d = rest.pop('Damage', None)
    if d and d[1]:
        comps['minecraft:damage'] = (3, d[1])
    disp = rest.pop('display', None)
    if disp:
        dd = disp[1]
        if 'Name' in dd:
            comps['minecraft:custom_name'] = (8, dd['Name'][1])
        if 'Lore' in dd:
            comps['minecraft:lore'] = dd['Lore']
        if 'color' in dd:
            comps['minecraft:dyed_color'] = (10, {'rgb': (3, dd['color'][1])})
    for key, cname in (('Enchantments', 'minecraft:enchantments'),
                       ('StoredEnchantments', 'minecraft:stored_enchantments')):
        e = rest.pop(key, None)
        if e and e[1][1]:
            levels = {x['id'][1]: (3, int(x['lvl'][1])) for x in e[1][1]}
            comps[cname] = (10, {'levels': (10, levels)})
    p = rest.pop('Potion', None)
    if p:
        comps['minecraft:potion_contents'] = (10, {'potion': (8, p[1])})
    rc = rest.pop('RepairCost', None)
    if rc:
        comps['minecraft:repair_cost'] = (3, rc[1])
    qf = rest.get('quality_food')
    if qf and 'quality' in qf[1] and qf[1]['quality'][1] in QUALITY_NAMES:
        n = qf[1]['quality'][1]
        comps['quality_food:quality'] = (10, {'type': (8, 'quality_food:' + QUALITY_NAMES[n]), 'level': (3, n)})
        rest.pop('quality_food')
    for key, cname, tid in (('contentsUuid', 'sophisticatedcore:storage_uuid', 11),
                            ('inventorySlots', 'sophisticatedcore:number_of_inventory_slots', 3),
                            ('upgradeSlots', 'sophisticatedcore:number_of_upgrade_slots', 3)):
        if key in rest and rest[key][0] == tid:
            comps[cname] = rest.pop(key)
    rest.pop('renderInfo', None)
    rest.pop('sortBy', None)
    if 'AccountID' in rest and rest['AccountID'][0] in (3, 11):  # 1.20.1 cards store a UUID int array
        comps['numismatics:card_account_id'] = rest.pop('AccountID')
    if 'UUID' in rest and rest['UUID'][0] == 11 and 'id_card' in old['id'][1]:
        comps['numismatics:id_card_uuid'] = rest.pop('UUID')
    bet = rest.get('BlockEntityTag')
    if bet and dig(bet, 'Items') is not None and not dig(bet, 'Items')[1]:
        rest.pop('BlockEntityTag')
    if rest:
        comps['minecraft:custom_data'] = (10, rest)
    if not comps:
        return None
    return comps


def make_item(o, t, skey, stid, notes, slot=None):
    d = {'id': (8, remap(t, o['id'][1])), 'count': (3, int(o['Count'][1]) if 'Count' in o else int(o['count'][1]))}
    c = convert_stack(o, t, notes)
    if c:
        d['components'] = (10, c)
    d[skey] = (stid, slot_of(o) if slot is None else slot)
    return d


# ---------- chunk / region access ----------

def load_regions(save, sub='region'):
    out = {}
    for p in sorted(glob.glob(os.path.join(save, sub, '*.mca'))):
        raw, items = chunks_of(p)
        roots = {i: root for i, root, err in items if root is not None}
        out[p] = {'raw': raw, 'roots': roots, 'changed': set()}
    return out


def region_path(save, x, z, sub='region'):
    return os.path.join(save, sub, f'r.{x >> 9}.{z >> 9}.mca')


def chunk_index(x, z):
    return ((x >> 4) & 31) + ((z >> 4) & 31) * 32


def block_at(root, x, y, z):
    sy = y >> 4
    for sec in listvals(dig(root, 'sections')):
        if sec['Y'][1] != sy:
            continue
        bs = sec['block_states'][1]
        names = [p['Name'][1] for p in bs['palette'][1][1]]
        if len(names) == 1:
            return names[0]
        bits = max(4, (len(names) - 1).bit_length())
        per = 64 // bits
        i = (y % 16) * 256 + (z % 16) * 16 + (x % 16)
        word = bs['data'][1][i // per] & 0xFFFFFFFFFFFFFFFF
        return names[(word >> ((i % per) * bits)) & ((1 << bits) - 1)]
    return 'minecraft:air'


def index_be(regions):
    out = {}
    for path, reg in regions.items():
        for i, root in reg['roots'].items():
            for be in listvals(dig(root, 'block_entities')):
                pos = (be['x'][1], be['y'][1], be['z'][1])
                out[pos] = (path, i, root, be)
    return out


def load_dat(path):
    with gzip.open(path, 'rb') as f:
        name, tid, val = NBTReader(f.read()).read_tag()
    return {'name': name, 'val': val}


def save_dat(path, dat):
    data = gzip.compress(w_tag(dat['name'], 10, dat['val']))
    with open(path + '.tmp', 'wb') as f:
        f.write(data)
    os.replace(path + '.tmp', path)


# ---------- steps ----------

class Stats:
    def __init__(self):
        self.counts = 0
        self.components = 0
        self.unmatched = 0
        self.filled = {2: [], 3: [], 4: []}
        self.quality = 0
        self.quality_unknown = 0
        self.skipped = []


def step1(nbe, obe, t, st, where):
    olds = {}
    for it in scan_items(obe):
        olds.setdefault((slot_of(it), path_of(remap(t, it['id'][1]))), it)
    for it in scan_items(nbe):
        o = olds.get((slot_of(it), path_of(it['id'][1])))
        if o is None:
            st.unmatched += 1
            continue
        if 'count' in it and it['count'][1] == 1 and 'Count' in o and o['Count'][1] > 1:
            it['count'] = (3, int(o['Count'][1]))
            st.counts += 1
        if 'components' not in it and 'tag' in o:
            c = convert_stack(o, t, [])
            if c:
                it['components'] = (10, c)
                st.components += 1


def old_items(obe):
    out = []
    if 'Items' in obe:
        out += obe['Items'][1][1]
    for att in dig(obe, 'attachments') and obe['attachments'][1][1] or []:
        if 'items' in att:
            out += att['items'][1][1]
    return out


def step2(nbe, obe, t, st, where):
    nid = nbe['id'][1]
    if nid in ITEMS_FILL and obe['id'][1] == ITEMS_FILL[nid] and 'Items' in nbe and not nbe['Items'][1][1]:
        items = [make_item(o, t, 'Slot', 1, []) for o in old_items(obe)]
        if items:
            nbe['Items'] = (9, (10, items))
            st.filled[2].append((where, nid, len(items)))
    if nid in ATTACH_FILL and obe['id'][1] == nid:
        att = nbe.get('attachments')
        if att and att[0] == 10 and 'inventory' in att[1] and not att[1]['inventory'][1][1]:
            items = [make_item(o, t, 'slot', 1, []) for o in old_items(obe)]
            if items:
                att[1]['inventory'] = (9, (10, items))
                st.filled[2].append((where, nid, len(items)))
    if nid == 'bonsaitrees4:bonsaipot' and 'inv' in nbe:
        for okey, hkey in BONSAI_KEYS.items():
            if okey not in obe or hkey not in nbe['inv'][1]:
                continue
            h = nbe['inv'][1][hkey][1]
            if h['Items'][1][1]:
                continue
            items = [make_item(o, t, 'Slot', 3, []) for o in listvals(dig(obe, okey, 'Items'))]
            if items:
                h['Items'] = (9, (10, items))
                st.filled[2].append((where, f'{nid} {hkey}', len(items)))


def step3(obe, t, st, pos, regions, save_root, new_index):
    oid = obe['id'][1]
    if oid in SKIP_REASONS:
        st.skipped.append((pos, oid, SKIP_REASONS[oid]))
        return
    if oid not in CREATE_MAP or pos in new_index:
        return
    x, y, z = pos
    reg = regions.get(region_path(save_root, x, z))
    if reg is None or chunk_index(x, z) not in reg['roots']:
        st.skipped.append((pos, oid, 'chunk missing in NEW, not created'))
        return
    root = reg['roots'][chunk_index(x, z)]
    name = block_at(root, x, y, z)
    want_cabinet = CREATE_MAP[oid] == 'bakery:cabinet'
    if not name.startswith('bakery:') or (want_cabinet and 'cabinet' not in name):
        st.skipped.append((pos, oid, f'NEW block is {name}, not a matching bakery block'))
        return
    items = [make_item(o, t, 'Slot', 1, []) for o in old_items(obe)]
    if not items:
        return  # nothing to restore; the game creates the empty block entity itself
    new = {'id': (8, CREATE_MAP[oid]), 'x': (3, x), 'y': (3, y), 'z': (3, z),
           'keepPacked': (1, 0), 'Items': (9, (10, items))}
    if 'size' in obe:
        new['size'] = obe['size']
    if 'block_entities' not in root:
        root['block_entities'] = (9, (10, []))
    root['block_entities'][1][1].append(new)
    reg['changed'].add(chunk_index(x, z))
    st.filled[3].append((pos, CREATE_MAP[oid], len(items)))


def step4(old_dat, new_dat, t, st):
    old_c = dig(old_dat['val'], 'ForgeCaps', 'curios:inventory', 'Curios')
    new_c = dig(new_dat['val'], 'neoforge:attachments', 'curios:inventory', 'Curios')
    if old_c is None or new_c is None:
        st.skipped.append(('player', 'curios', 'Curios list missing in OLD or NEW'))
        return
    old_by_id = {dig(e, 'Identifier'): e for e in listvals(old_c)}
    for e in listvals(new_c):
        ident = dig(e, 'Identifier')
        oe = old_by_id.get(ident)
        if oe is None:
            continue
        items_path = ('StacksHandler', 'Stacks', 'Items')
        n_items = dig(e, *items_path)
        o_items = dig(oe, *items_path)
        if n_items is None or o_items is None or n_items[1]:
            continue
        items = [make_item(o, t, 'Slot', 3, [], slot=int(slot_of(o))) for o in listvals(o_items)]
        if items:
            dig(e, 'StacksHandler', 'Stacks')['Items'] = (9, (10, items))
            st.filled[4].append(('player', ident, len(items)))


def step5(root, path, regions_changed, st):
    for it in scan_items(root):
        comps = it.get('components')
        if not comps:
            continue
        cd = comps[1].get('minecraft:custom_data')
        if not cd or 'quality_food' not in cd[1]:
            continue
        q = cd[1]['quality_food'][1].get('quality')
        name = QUALITY_NAMES.get(q[1]) if q else None
        if name is None:
            st.quality_unknown += 1
            continue
        comps[1]['quality_food:quality'] = (10, {'type': (8, 'quality_food:' + name), 'level': (3, q[1])})
        del cd[1]['quality_food']
        if not cd[1]:
            del comps[1]['minecraft:custom_data']
        st.quality += 1
        regions_changed.add(path)


def procedure(apply_mode):
    t = load_map()
    st = Stats()
    old_reg = load_regions(OLD)
    new_reg = load_regions(NEW)
    old_index = {}
    for p, reg in old_reg.items():
        for i, root in reg['roots'].items():
            for be in listvals(dig(root, 'block_entities')):
                old_index[(be['x'][1], be['y'][1], be['z'][1])] = be
    new_index = index_be(new_reg)
    before = {k: summary(new_index[v][3] if v in new_index else None) for k, v in PROBES.items()}
    touched_dat = set()

    for pos, obe in old_index.items():
        if pos not in new_index:
            step3(obe, t, st, pos, new_reg, NEW, new_index)
            continue
        ppath, pi, proot, nbe = new_index[pos]
        if nbe['id'][1] == obe['id'][1] or obe['id'][1] in ITEMS_FILL.values() or obe['id'][1] in ATTACH_FILL:
            pass
        before_count = st.counts
        before_comp = st.components
        step1(nbe, obe, t, st, pos)
        if st.counts != before_count or st.components != before_comp:
            new_reg[ppath]['changed'].add(pi)
        n_before = len(st.filled[2])
        step2(nbe, obe, t, st, pos)
        if len(st.filled[2]) != n_before:
            new_reg[ppath]['changed'].add(pi)

    for pos, obe in old_index.items():
        if pos in new_index and obe['id'][1] in CREATE_MAP:
            pass

    old_dat = load_dat(os.path.join(OLD, 'playerdata', PLAYER + '.dat'))
    new_path = os.path.join(NEW, 'playerdata', PLAYER + '.dat')
    new_dat = load_dat(new_path)
    step4(old_dat, new_dat, t, st)

    changed_regions = set()
    for path, reg in new_reg.items():
        pass
    ent_reg = load_regions(NEW, 'entities')
    for path, reg in new_reg.items():
        for i, root in reg['roots'].items():
            step5(root, path, changed_regions, st)
            if i in reg['changed'] or path in changed_regions:
                reg['changed'].add(i)
    for path, reg in ent_reg.items():
        for i, root in reg['roots'].items():
            tmp = set()
            step5(root, path, tmp, st)
            if tmp:
                reg['changed'].add(i)
                ent_reg[path]['changed'].add(i)
    if st.filled[4]:
        touched_dat.add(new_path)  # Curios restored: the player file must be saved
    dat_before = st.quality
    step5(new_dat['val'], new_path, set(), st)
    if st.quality != dat_before:
        touched_dat.add(new_path)

    after = {k: summary(index_be(new_reg)[v][3] if v in index_be(new_reg) else None) for k, v in PROBES.items()}
    head = dig(new_dat['val'], 'neoforge:attachments', 'curios:inventory', 'Curios')
    head_before = head_after = 'absent'
    if head is not None:
        for e in listvals(head):
            if dig(e, 'Identifier') == 'head':
                head_after = ' ; '.join(
                    f"slot {slot_of(i)} {i['id'][1]} x{count_of(i)}" for i in scan_items(e)) or 'empty'
    return {'st': st, 'before': before, 'after': after, 'head_after': head_after,
            'new_reg': new_reg, 'ent_reg': ent_reg, 'new_dat': new_dat, 'new_path': new_path,
            'touched_dat': touched_dat, 'old_index': old_index}


def write_report(res):
    st = res['st']
    lines = ['# RESTORE_REPORT', '', 'Generated by tools/saveport/restore_items.py (dry-run). Spec: RESTORE_SPEC.md.', '',
             '## Totals', '',
             f'- Step 1 counts fixed: {st.counts}',
             f'- Step 1 components fixed: {st.components}',
             f'- Step 1 stacks without OLD match: {st.unmatched}',
             f'- Step 2 BEs filled: {len(st.filled[2])}',
             f'- Step 3 BEs created: {len(st.filled[3])}',
             f'- Step 4 Curios slots filled: {len(st.filled[4])}',
             f'- Step 5 quality converted: {st.quality}',
             f'- Step 5 quality with unknown level: {st.quality_unknown}', '']
    for step, title in ((2, 'Step 2 (emptied BEs)'), (3, 'Step 3 (created BEs)'), (4, 'Step 4 (Curios)')):
        lines += [f'## {title}', '']
        lines += [f'- {w} {i} items={n}' for w, i, n in st.filled[step]] or ['- none']
        lines.append('')
    lines += ['## Skipped', '']
    lines += [f'- {w} {i}: {r}' for w, i, r in st.skipped] or ['- none']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if args.apply:
        out = subprocess.run(['pgrep', '-a', '-x', 'java'], capture_output=True, text=True).stdout
        if any('Pipinha' in line for line in out.splitlines()):
            print('refused: a java process with Pipinha is running')
            return 2
    res = procedure(args.apply)
    st = res['st']
    print(f'step1 counts={st.counts} components={st.components} unmatched={st.unmatched}')
    for s in (2, 3, 4):
        print(f'step{s} entries={len(st.filled[s])}')
        for w, i, n in st.filled[s]:
            print(f'  {w} {i} items={n}')
    print(f'step5 quality={st.quality} unknown={st.quality_unknown}')
    print(f'skipped={len(st.skipped)}')
    for w, i, r in st.skipped:
        print(f'  {w} {i}: {r}')
    for k in PROBES:
        print(f'before {k} {PROBES[k]}: {res["before"][k]}')
        print(f'after  {k} {PROBES[k]}: {res["after"][k]}')
    print(f'after head slot: {res["head_after"]}')
    write_report(res)
    if not args.apply:
        print('dry-run: nothing written to saves/')
        return 0
    if os.path.exists(BACKUP):
        print('backup already exists, not overwriting')
    else:
        with zipfile.ZipFile(BACKUP, 'w', zipfile.ZIP_DEFLATED) as z:
            for dp, _, fns in os.walk(NEW):
                for fn in fns:
                    full = os.path.join(dp, fn)
                    z.write(full, os.path.relpath(full, os.path.dirname(NEW)))
    for reg_map in (res['new_reg'], res['ent_reg']):
        for path, reg in reg_map.items():
            if reg['changed']:
                write_region(path, reg['raw'], {i: reg['roots'][i] for i in reg['changed']})
    if res['touched_dat']:
        save_dat(res['new_path'], res['new_dat'])
    print('applied')
    return 0


if __name__ == '__main__':
    sys.exit(main())
