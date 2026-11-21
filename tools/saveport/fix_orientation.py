#!/usr/bin/env python3
"""Fix, in place, furniture turned or disconnected by an older convert_save.py run.

Usage:
  fix_orientation.py save <src_1.20.1_save> <converted_save> [--apply]
  fix_orientation.py palettes [--apply]

Dry run unless --apply (back the save up first; close the game). Only positions where the
1.20.1 source had a block covered by state_rules.tsv and the converted save still has the
mapped block in the old, unturned state are changed, so blocks the player placed or turned
in 1.21.1 are left alone. Only the facing and the keys written by the rule are touched.
'palettes' does the same for the Lost Cities palettes in moonlight-global-datapacks,
pairing each file and entry with the 1.20.1 instance. Stdlib only.
"""

import glob
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import convert_save as cs  # noqa: E402
import state_rules as sr  # noqa: E402

ROOT = cs.ROOT
OLD_ROOT = os.path.join(os.path.dirname(ROOT), 'Society: Sunlit Valley')


def rule_keys(srule):
    keys = set(sr.FACING_KEYS)
    for _src, dsts, _vals in srule[3]:
        keys.update(dsts)
    return keys


def needs_fix(old_props, cur, fixed, srule):
    """cur still holds the unturned/unmapped state of old_props, and differs from fixed."""
    keys = rule_keys(srule)
    if all(cur.get(k) == fixed.get(k) for k in keys if k in fixed):
        return False, 'ja certo'
    fk = next((k for k in sr.FACING_KEYS if k in cur), None)
    if srule[2] and fk and cur.get(fk) != old_props.get(fk):
        return False, 'mexido no 1.21.1'
    return True, 'corrigir'


def merged(cur, fixed, srule):
    out = dict(cur)
    out.update({k: v for k, v in fixed.items() if k in rule_keys(srule)})
    return out


def unpack(bs):
    pal = bs['palette'][1][1]
    if 'data' not in bs:
        return pal, [0] * 4096
    bits = max(4, (len(pal) - 1).bit_length())
    per, mask, out = 64 // bits, (1 << bits) - 1, []
    for word in bs['data'][1]:
        word &= (1 << 64) - 1
        out.extend((word >> (bits * j)) & mask for j in range(per))
    return pal, out[:4096]


def pack(bs, pal, idx):
    bs['palette'] = (9, (10, pal))
    if len(pal) == 1:
        bs.pop('data', None)
        return
    bits = max(4, (len(pal) - 1).bit_length())
    per, words = 64 // bits, []
    for i in range(0, 4096, per):
        w = 0
        for j, v in enumerate(idx[i:i + per]):
            w |= v << (bits * j)
        words.append(w - (1 << 64) if w >= 1 << 63 else w)
    bs['data'] = (12, words)


def props_of(entry):
    return {k: v[1] for k, v in entry['Properties'][1].items()} if 'Properties' in entry else {}


def fix_chunk(t, src_root, dst_root, accepted, stats):
    dst_secs = {s['Y'][1]: s for s in dst_root.get('sections', (9, (10, [])))[1][1] if 'block_states' in s}
    changed = False
    for s in src_root.get('sections', (9, (10, [])))[1][1]:
        if 'block_states' not in s or s['Y'][1] not in dst_secs:
            continue
        spal, sidx = unpack(s['block_states'][1])
        todo = {}
        for i, e in enumerate(spal):
            rule = cs.lookup(t.blocks, t, e['Name'][1])
            srule = rule and sr.find(e['Name'][1], rule[0])
            if srule and sr.changed_by(srule):
                old = props_of(e)
                todo[i] = (rule[0], old, cs.convert_props(e['Name'][1], rule, old, accepted), srule)
        if not todo:
            continue
        dbs = dst_secs[s['Y'][1]]['block_states'][1]
        dpal, didx = unpack(dbs)
        sec_changed = False
        for pos, si in enumerate(sidx):
            if si not in todo:
                continue
            new, old, fixed, srule = todo[si]
            entry = dpal[didx[pos]]
            if entry['Name'][1] != new:
                stats['outro bloco'] += 1
                continue
            cur = props_of(entry)
            ok, why = needs_fix(old, cur, fixed, srule)
            stats[why] += 1
            if not ok:
                continue
            want = merged(cur, fixed, srule)
            hit = next((k for k, p in enumerate(dpal) if p['Name'][1] == new and props_of(p) == want), None)
            if hit is None:
                dpal.append({'Name': (8, new), 'Properties': (10, {k: (8, v) for k, v in sorted(want.items())})})
                hit = len(dpal) - 1
            didx[pos] = hit
            stats[f'{srule[0]} -> {srule[1]}'] += 1
            sec_changed = True
        if sec_changed:
            pack(dbs, dpal, didx)
            changed = True
    return changed


def run_save(src, dst, apply):
    t = cs.load_map()
    cache = {}

    def accepted(block):
        if block not in cache:
            cache[block] = cs.lc_ids.accepted_states(block)
        return cache[block]
    stats, regions = Counter(), 0
    for spath in cs.region_files(src):
        dpath = os.path.join(dst, os.path.relpath(spath, src))
        if not os.path.isfile(dpath) or '/region/' not in spath.replace(os.sep, '/'):
            continue
        _, sitems = cs.chunks_of(spath)
        draw, ditems = cs.chunks_of(dpath)
        droots = {i: r for i, r, err in ditems if r is not None}
        changed = {}
        for i, sroot, err in sitems:
            if sroot is not None and i in droots and fix_chunk(t, sroot, droots[i], accepted, stats):
                changed[i] = droots[i]
        if changed:
            regions += 1
            stats['chunks alterados'] += len(changed)
            if apply:
                cs.write_region(dpath, draw, changed)
    return stats, regions


def pair_blocks(old, new, out):
    if isinstance(old, dict) and isinstance(new, dict):
        for k in new:
            if k == 'block' and isinstance(new[k], str) and isinstance(old.get(k), str):
                out.append((old[k], new, k))
            elif k in old:
                pair_blocks(old[k], new[k], out)
    elif isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for a, b in zip(old, new):
            pair_blocks(a, b, out)


def run_palettes(apply):
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'lcport'))
    import port_palettes as pp
    mapping, stats = pp.load_map(), Counter()
    pattern = os.path.join(ROOT, 'moonlight-global-datapacks', '*', 'data', '*', 'lostcities', '**', '*.json')
    for path in sorted(glob.glob(pattern, recursive=True)):
        opath = os.path.join(OLD_ROOT, os.path.relpath(path, ROOT))
        if not os.path.isfile(opath):
            continue
        raw = open(path, encoding='utf-8').read()
        new_data, pairs = json.loads(raw), []
        pair_blocks(json.load(open(opath, encoding='utf-8')), new_data, pairs)
        hits = 0
        for oldv, node, key in pairs:
            obase, nbase = oldv.split('[')[0], node[key].split('[')[0]
            srule = obase in mapping and sr.find(obase, nbase)
            if not srule or not sr.changed_by(srule) or mapping[obase][0] != nbase:
                continue
            fixed = dict(pp.parse_props(pp.transform(oldv, mapping)[0]))
            cur = dict(pp.parse_props(node[key]))
            ok, why = needs_fix(dict(pp.parse_props(oldv)), cur, fixed, srule)
            stats[why] += 1
            if ok:
                node[key] = pp.render(nbase, list(merged(cur, fixed, srule).items()))
                stats[f'{srule[0]} -> {srule[1]}'] += 1
                hits += 1
        if hits:
            stats['arquivos alterados'] += 1
            if apply:
                compact = '\n' not in raw.strip()
                out = json.dumps(new_data, ensure_ascii=True, separators=(',', ':')) if compact else \
                    json.dumps(new_data, indent='\t' if raw.startswith(('{\n\t', '[\n\t')) else 2, ensure_ascii=True)
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(out + ('\n' if raw.endswith('\n') else ''))
    return stats


def main(argv):
    apply = '--apply' in argv
    args = [a for a in argv if a != '--apply']
    if len(args) == 3 and args[0] == 'save':
        stats, regions = run_save(args[1], args[2], apply)
        print(f'regioes alteradas: {regions}')
    elif args == ['palettes']:
        stats = run_palettes(apply)
    else:
        sys.exit(__doc__)
    for k, v in sorted(stats.items()):
        print(f'{v:7d}  {k}')
    print('APLICADO' if apply else 'dry run (nada escrito; use --apply)')


if __name__ == '__main__':
    main(sys.argv[1:])
