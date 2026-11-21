#!/usr/bin/env python3
"""Measure how a block remapped by convert_save.py turns compared to its 1.20.1 block.

Usage:
  orient_check.py [--all] [--out PATH]

For every block row of id_map.tsv whose old block has a horizontal facing property, the
old model (1.20.1 jars) in each facing is voxelized and compared with the new model
(1.21.1 jars) in each facing. The best match gives the rotation the converter must apply
(clockwise quarter turns, 0..3), compared with the rotate column of state_rules.tsv.
Symmetric or low-overlap rows need a manual look (top/side views); the decisions are in
ORIENTATION.md. Without --all only ids listed in solito_oriented.txt (if present) are
checked. Stdlib only, read only.
"""

import glob
import io
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OLD_ROOT = os.path.join(os.path.dirname(ROOT), 'Society: Sunlit Valley')
VERSIONS = os.path.join(os.path.dirname(os.path.dirname(ROOT)), 'Install', 'versions')
sys.path.insert(0, HERE)
import convert_save as cs  # noqa: E402
import state_rules as sr  # noqa: E402

DIRS = ['north', 'east', 'south', 'west']  # clockwise seen from above
FACING_KEYS = ('facing', 'horizontal_facing', 'direction')


class Assets:
    """Asset lookup over a list of jars, first jar wins."""

    def __init__(self, jars):
        self.index = {}
        for jar in jars:
            try:
                z = zipfile.ZipFile(jar)
            except (zipfile.BadZipFile, OSError):
                continue
            self.add(z)
        self.cache = {}

    def add(self, z):
        """Index a jar and the jars bundled inside it (META-INF/jars, META-INF/jarjar)."""
        for name in z.namelist():
            if name.startswith('assets/') and name.endswith('.json'):
                self.index.setdefault(name, z)
            elif name.startswith('META-INF/jar') and name.endswith('.jar'):
                try:
                    self.add(zipfile.ZipFile(io.BytesIO(z.read(name))))
                except zipfile.BadZipFile:
                    continue

    def json(self, path):
        if path not in self.cache:
            z = self.index.get(path)
            try:
                self.cache[path] = json.loads(z.read(path)) if z else None
            except ValueError:
                self.cache[path] = None
        return self.cache[path]

    def blockstate(self, ident):
        ns, _, path = ident.partition(':')
        return self.json(f'assets/{ns}/blockstates/{path}.json')

    def elements(self, model, depth=0):
        if depth > 20:
            return []
        ns, _, path = model.partition(':') if ':' in model else ('minecraft', '', model)
        data = self.json(f'assets/{ns}/models/{path}.json')
        if data is None:
            return []
        if 'elements' in data:
            return data['elements']
        if 'parent' in data:
            return self.elements(data['parent'], depth + 1)
        return []


def jars(mods_dir, version):
    out = sorted(glob.glob(os.path.join(mods_dir, '*.jar')))
    out.append(os.path.join(VERSIONS, version, f'{version}.jar'))
    return out


def match(cond, state):
    if 'OR' in cond:
        return any(match(c, state) for c in cond['OR'])
    if 'AND' in cond:
        return all(match(c, state) for c in cond['AND'])
    for k, v in cond.items():
        if state.get(k) not in str(v).split('|'):
            return False
    return True


def parse_key(key):
    return dict(p.split('=', 1) for p in key.split(',') if '=' in p)


def models_for(bs, state):
    """[(model, y)] for a state; for variants the first key compatible with state."""
    out = []
    if 'variants' in bs:
        for key, apply in bs['variants'].items():
            if all(state.get(k) == v for k, v in parse_key(key).items() if k in state):
                for a in (apply if isinstance(apply, list) else [apply])[:1]:
                    out.append((a['model'], a.get('y', 0), a.get('x', 0)))
                break
    for part in bs.get('multipart', []):
        if 'when' not in part or match(part['when'], state):
            for a in (part['apply'] if isinstance(part['apply'], list) else [part['apply']])[:1]:
                out.append((a['model'], a.get('y', 0), a.get('x', 0)))
    return out


def span(a, b):
    """Voxel range of one element axis; flat planes (from == to) still count as one voxel."""
    lo, hi = sorted((a, b))
    lo_i = min(15, max(0, int(lo if lo < 16 else 15)))
    hi_i = min(16, max(lo_i + 1, int(-(-hi // 1))))
    return range(lo_i, hi_i)


def voxels(assets, bs, state):
    vox = set()
    for model, y, x in models_for(bs, state):
        if x:  # tilted parts (rare in furniture): skip, they do not decide the facing
            continue
        for el in assets.elements(model):
            rx, ry, rz = (span(el['from'][i], el['to'][i]) for i in range(3))
            for vx in rx:
                for vy in ry:
                    for vz in rz:
                        px, pz = vx, vz
                        for _ in range((y // 90) % 4):  # blockstate y: clockwise seen from above
                            px, pz = 15 - pz, px
                        vox.add((px, vy, pz))
    return vox


def states_of(bs):
    keys = {}
    for key in bs.get('variants', {}):
        for k, v in parse_key(key).items():
            keys.setdefault(k, []).append(v)
    for part in bs.get('multipart', []):
        for cond in ([part.get('when', {})] + part.get('when', {}).get('OR', [])):
            for k, v in cond.items():
                if k not in ('OR', 'AND'):
                    keys.setdefault(k, []).extend(str(v).split('|'))
    return {k: list(dict.fromkeys(v)) for k, v in keys.items()}


def base_state(bs, facing_key, facing, prefer):
    st = {facing_key: facing}
    for k, vals in states_of(bs).items():
        if k == facing_key:
            continue
        st[k] = next((p for p in prefer if p in vals), vals[0])
    return st


PREFER = ('single', 'none', 'false', 'bottom', 'lower', 'fabric', 'straight', 'solo', '0', 'left')


def facing_key_of(bs):
    keys = states_of(bs)
    for k in FACING_KEYS:
        if k in keys and set(keys[k]) >= set(DIRS):
            return k
    return None


def iou(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def check(old_id, new_id, old_assets, new_assets):
    obs, nbs = old_assets.blockstate(old_id), new_assets.blockstate(new_id)
    if obs is None or nbs is None:
        return None, 'blockstate ausente'
    ok, nk = facing_key_of(obs), facing_key_of(nbs)
    if not ok:
        return None, 'sem facing na origem'
    if not nk:
        return None, 'sem facing no destino'
    old = voxels(old_assets, obs, base_state(obs, ok, 'north', PREFER))
    if not old:
        return None, 'modelo antigo sem elementos'
    scores = []
    for q, d in enumerate(DIRS):
        new = voxels(new_assets, nbs, base_state(nbs, nk, d, PREFER))
        scores.append(iou(old, new))
    best = max(range(4), key=lambda i: scores[i])
    ranked = sorted(scores, reverse=True)
    if ranked[0] - ranked[1] < 0.02:
        return None, 'simetrico ' + ' '.join(f'{s:.2f}' for s in scores)
    return best, ' '.join(f'{s:.2f}' for s in scores)


def main(argv):
    out_path = argv[argv.index('--out') + 1] if '--out' in argv else None
    t = cs.load_map()
    used = None
    used_file = os.path.join(HERE, 'solito_oriented.txt')
    if '--all' not in argv and os.path.isfile(used_file):
        used = set(open(used_file, encoding='utf-8').read().split())
    old_assets = Assets(jars(os.path.join(OLD_ROOT, 'mods'), '1.20.1'))
    new_assets = Assets(jars(os.path.join(ROOT, 'mods'), '1.21.1'))
    rows = ['| old id | new id | rotate na tabela | medido | IoU N/E/S/W |', '|---|---|---|---|---|']
    bad = 0
    for old_id, (new_id, _ren, _sets) in sorted(t.blocks.items()):
        if used is not None and old_id not in used:
            continue
        if new_id == cs.AIR or new_id.startswith('minecraft:') and old_id.partition(':')[2] == new_id.partition(':')[2]:
            continue
        q, info = check(old_id, new_id, old_assets, new_assets)
        if q is None and info.startswith('sem facing na origem'):
            continue
        srule = sr.find(old_id, new_id)
        have = srule[2] if srule else 0
        flag = '' if q is None or q == have else ' **DIVERGE**'
        bad += bool(flag)
        rows.append(f'| {old_id} | {new_id} | {have} | {"-" if q is None else q}{flag} | {info} |')
    text = '\n'.join(rows) + f'\n\nDivergencias: {bad}\n'
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
    print(text)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
