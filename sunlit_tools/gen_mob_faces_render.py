"""Map faces from front renders (fallback of gen_mob_faces.py for mobs whose head model can't be read:
GeckoLib, no layer definition, no head part).

Input: RENDER|{json} lines from sunlit_tools/headless_client/run_render_probe.sh (render.txt): each one has
the PNG (base64, magenta background) of the mob rendered facing the viewer as the player sees it, plus
feet position, scale (px per block) and eye height. The head is the silhouette run at eye height; its top
is where the run narrows (ears and horns are thin), and the face is the square below that, downsampled
to model pixels (scale / 16 px each) like FTB Chunks' own faces.

Usage: python3 sunlit_tools/gen_mob_faces_render.py --render render.txt --out kubejs/assets/ftbchunks/textures/faces
       [--ids a:b,c:d] [--sheet sheet.png]   (never overwrites an existing face)
"""
import argparse, base64, io, json, os
from PIL import Image


def is_bg(c):
    return c[0] > 200 and c[1] < 60 and c[2] > 200


def run_at(px, w, y, x0):
    """[left, right) of the silhouette run on row y through column x0 (or the nearest solid column)."""
    xs = [x for x in range(w) if not is_bg(px[x, y])]
    if not xs:
        return None
    x0 = min(xs, key=lambda x: abs(x - x0))
    l = r = x0
    while l > 0 and not is_bg(px[l - 1, y]):
        l -= 1
    while r < w - 1 and not is_bg(px[r + 1, y]):
        r += 1
    return l, r + 1


def face(rec):
    im = Image.open(io.BytesIO(base64.b64decode(rec['png']))).convert('RGB')
    w, h = im.size
    px = im.load()
    unit = rec['scale'] / 16.0  # screen px per model pixel
    eye = int(rec['feet'] - rec['eye'] * rec['scale'])
    eye = max(0, min(h - 1, eye))
    run = None
    for dy in range(0, int(unit * 3)):  # the eye row may fall on a gap; look a little lower
        run = run_at(px, w, min(h - 1, eye + dy), int(rec['cx']))
        if run:
            eye += dy
            break
    if not run:
        raise ValueError('no silhouette at eye height')
    l, r = run
    width = r - l
    top = eye
    cx = (l + r) // 2
    while top > 0:
        nr = run_at(px, w, top - 1, cx)
        if not nr or (nr[1] - nr[0]) < width * 0.6:
            break
        top -= 1
    side = max(width, int(unit * 3))
    box = (l, top, l + side, min(h, top + side))
    n = max(1, round(side / unit))
    out = Image.new('RGBA', (n, max(1, round((box[3] - box[1]) / unit))), (0, 0, 0, 0))
    for j in range(out.size[1]):
        for i in range(out.size[0]):
            x = int(box[0] + (i + 0.5) * unit)
            y = int(box[1] + (j + 0.5) * unit)
            if 0 <= x < w and 0 <= y < h and not is_bg(px[x, y]):
                out.putpixel((i, j), px[x, y] + (255,))
    if not out.getbbox():
        raise ValueError('empty crop')
    return out.crop(out.getbbox())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--render', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ids', default='')
    ap.add_argument('--sheet', default='')
    ap.add_argument('--force', action='store_true', help='write even if a face exists (calibration dirs only)')
    a = ap.parse_args()
    want = set(i for i in a.ids.split(',') if i)
    rows, skipped = [], []
    for line in open(a.render, encoding='utf-8'):
        k = line.find('RENDER|{')
        if k < 0:
            continue
        rec = json.loads(line[k + 7:])
        rid = rec['id']
        if want and rid not in want:
            continue
        if 'png' not in rec:
            skipped.append((rid, rec.get('error', 'no render')))
            continue
        ns, path = rid.split(':', 1)
        dst = os.path.join(a.out, ns, path + '.png')
        if os.path.exists(dst) and not a.force:
            skipped.append((rid, 'exists'))
            continue
        try:
            img = face(rec)
        except ValueError as e:
            skipped.append((rid, str(e)))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        img.save(dst)
        rows.append((rid, img))
    for rid, why in skipped:
        print('SKIP %-34s %s' % (rid, why))
    print('written=%d skipped=%d' % (len(rows), len(skipped)))
    if a.sheet and rows:
        from PIL import ImageDraw
        cell, cols = 112, 10
        sheet = Image.new('RGBA', (cols * cell, ((len(rows) + cols - 1) // cols) * (cell + 12)), (70, 70, 70, 255))
        d = ImageDraw.Draw(sheet)
        for i, (rid, img) in enumerate(rows):
            s = max(1, min(96 // img.size[0], 96 // img.size[1]))
            x, y = (i % cols) * cell, (i // cols) * (cell + 12)
            sheet.alpha_composite(img.resize((img.size[0] * s, img.size[1] * s), Image.NEAREST), (x + 8, y + 4))
            d.text((x + 2, y + cell - 6), rid.split(':')[1][:17], fill=(255, 255, 255, 255))
        sheet.save(a.sheet)


if __name__ == '__main__':
    main()
