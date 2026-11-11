"""Builds FTB Chunks map faces (front view of a mob's head) from the real model dumped by
sunlit_tools/headless_client/probe_faces.js (FACE|{json} lines).

Each head cube polygon carries its vertices in model pixels and normalized u/v. The faces turned to
the viewer (normal -Z after the child part poses) are painted far to near on an X/Y grid, one cell
per model pixel, sampling the entity texture from the mod jars / vanilla jar. Output is cropped and
kept at native size, like FTB's own faces (pig 8x8).

Usage (instance root):
  python3 sunlit_tools/gen_mob_faces.py --faces <faces.txt> --out <dir> [--ids pig,cow] [--sheet x.png]
  --out kubejs/assets/ftbchunks/textures/faces writes <ns>/<path>.png (never overwrites).
  --calibrate compares with the FTB Chunks jar faces instead of writing to a faces tree.
"""
import argparse, glob, io, json, math, os, zipfile
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VANILLA_JAR = os.path.normpath(os.path.join(ROOT, '..', '..', 'Install', 'versions', '1.20.1', '1.20.1.jar'))
FTB_JAR = glob.glob(os.path.join(ROOT, 'mods', 'ftb-chunks-forge-*.jar'))[0]
POSE = ('f_104200_', 'f_104201_', 'f_104202_', 'f_104203_', 'f_104204_', 'f_104205_')  # x y z xRot yRot zRot
MIRROR = True  # model +X is the mob's left, which the viewer sees on the right; set by calibration

_index = None


def texture(tex):
    """PIL image for 'ns:path', from kubejs/assets, the mod jars or the vanilla jar."""
    global _index
    ns, path = tex.split(':', 1)
    name = 'assets/%s/%s' % (ns, path)
    local = os.path.join(ROOT, 'kubejs', name)
    if os.path.exists(local):
        return Image.open(local).convert('RGBA')
    if _index is None:
        _index = {}
        for jar in [VANILLA_JAR] + sorted(glob.glob(os.path.join(ROOT, 'mods', '*.jar'))):
            try:
                for n in zipfile.ZipFile(jar).namelist():
                    if n.endswith('.png') and '/textures/' in n:
                        _index.setdefault(n, jar)
            except zipfile.BadZipFile:
                pass
    jar = _index.get(name)
    if not jar:
        return None
    return Image.open(io.BytesIO(zipfile.ZipFile(jar).read(name))).convert('RGBA')


def rot(p, v):
    """Applies a part pose (MC order: translate, then zRot, yRot, xRot) to a point or a normal."""
    x, y, z = v
    a, b, c = p[3], p[4], p[5]
    y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    x, z = x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b)
    x, y = x * math.cos(c) - y * math.sin(c), x * math.sin(c) + y * math.cos(c)
    return x, y, z


def collect(node, chain, out):
    for cube in node['c']:
        for poly in cube['polys']:
            pts = []
            for pos, u, v in poly['v']:
                for p in reversed(chain):
                    q = rot(p, pos)
                    pos = (q[0] + p[0], q[1] + p[1], q[2] + p[2])
                pts.append((pos, u, v))
            n = poly['n']
            for p in reversed(chain):
                n = rot(p, n)
            if n[2] < -0.9:  # facing the viewer
                out.append(pts)
    for ch in node['ch']:
        pose = [ch['p'].get(k, 0.0) for k in POSE]
        collect(ch, chain + [pose], out)


def render(rec):
    img = texture(rec['tex'])
    if img is None:
        raise ValueError('texture not found: ' + rec['tex'])
    W, H = img.size
    quads = []
    collect(rec['head'], [], quads)
    if not quads:
        raise ValueError('no front faces')
    xs = [pt[0][0] for q in quads for pt in q]
    ys = [pt[0][1] for q in quads for pt in q]
    x0, y0 = math.floor(min(xs) + 1e-4), math.floor(min(ys) + 1e-4)
    w, h = math.ceil(max(xs) - 1e-4) - x0, math.ceil(max(ys) - 1e-4) - y0
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    quads.sort(key=lambda q: -min(pt[0][2] for pt in q))  # far (large z) first
    for q in quads:
        a = min(q, key=lambda pt: (pt[0][0], pt[0][1]))
        b = max(q, key=lambda pt: (pt[0][0], pt[0][1]))
        qx0, qy0, qx1, qy1 = a[0][0], a[0][1], b[0][0], b[0][1]
        if qx1 - qx0 < 1e-4 or qy1 - qy0 < 1e-4:
            continue
        for py in range(math.floor(qy0 + 1e-4), math.ceil(qy1 - 1e-4)):
            for px in range(math.floor(qx0 + 1e-4), math.ceil(qx1 - 1e-4)):
                fx, fy = (px + 0.5 - qx0) / (qx1 - qx0), (py + 0.5 - qy0) / (qy1 - qy0)
                u, v = a[1] + fx * (b[1] - a[1]), a[2] + fy * (b[2] - a[2])
                c = img.getpixel((min(W - 1, int(u * W)), min(H - 1, int(v * H))))
                if c[3] > 0:
                    out.putpixel((px - x0, py - y0), c)
    if MIRROR:
        out = out.transpose(Image.FLIP_LEFT_RIGHT)
    box = out.getbbox()
    if not box:
        raise ValueError('all transparent')
    return out.crop(box)


def ftb_face(rid):
    ns, path = rid.split(':', 1)
    try:
        data = zipfile.ZipFile(FTB_JAR).read('assets/ftbchunks/textures/faces/%s/%s.png' % (ns, path))
    except KeyError:
        return None
    return Image.open(io.BytesIO(data)).convert('RGBA')


def match(a, b):
    if b is None or a.size != b.size:
        return None
    pa, pb = list(a.getdata()), list(b.getdata())
    return 100.0 * sum(1 for x, y in zip(pa, pb) if x[:3] == y[:3] or (x[3] == 0 and y[3] == 0)) / len(pa)


def sheet(rows, path, s=8):
    cw = max(r[1].size[0] for r in rows) * s + 8
    ch = max(r[1].size[1] for r in rows) * s + 8
    cols = 12
    im = Image.new('RGBA', (cols * cw * (2 if rows[0][2] is not False else 1), ((len(rows) + cols - 1) // cols) * ch), (60, 60, 60, 255))
    for i, (rid, a, b) in enumerate(rows):
        x, y = (i % cols) * cw * (2 if b is not False else 1), (i // cols) * ch
        im.alpha_composite(a.resize((a.size[0] * s, a.size[1] * s), Image.NEAREST), (x + 4, y + 4))
        if b:
            im.alpha_composite(b.resize((b.size[0] * s, b.size[1] * s), Image.NEAREST), (x + cw + 4, y + 4))
    im.save(path)


def main():
    global MIRROR
    ap = argparse.ArgumentParser()
    ap.add_argument('--faces', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ids', default='')
    ap.add_argument('--sheet', default='')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--no-mirror', action='store_true')
    a = ap.parse_args()
    MIRROR = not a.no_mirror
    want = set(i if ':' in i else 'minecraft:' + i for i in a.ids.split(',') if i)
    rows, skipped = [], []
    for line in open(a.faces, encoding='utf-8'):
        i = line.find('FACE|{')
        if i < 0:
            continue
        rec = json.loads(line[i + 5:])
        rid = rec['id']
        if want and rid not in want:
            continue
        if 'head' not in rec:
            skipped.append((rid, rec.get('unsupported') or rec.get('error')))
            continue
        try:
            img = render(rec)
        except ValueError as e:
            skipped.append((rid, str(e)))
            continue
        if a.calibrate:
            ref = ftb_face(rid)
            m = match(img, ref)
            print('%-24s ours=%s ftb=%s match=%s' % (rid, img.size, ref.size if ref else None,
                                                     'n/a' if m is None else '%.0f%%' % m))
            rows.append((rid, img, ref))
            continue
        ns, path = rid.split(':', 1)
        dst = os.path.join(a.out, ns, path + '.png')
        if os.path.exists(dst):
            skipped.append((rid, 'exists'))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        img.save(dst)
        rows.append((rid, img, False))
    for rid, why in skipped:
        print('SKIP %-24s %s' % (rid, why))
    print('written=%d skipped=%d' % (0 if a.calibrate else len(rows), len(skipped)))
    if a.sheet and rows:
        sheet(rows, a.sheet)


if __name__ == '__main__':
    main()
