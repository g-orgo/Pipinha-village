#!/usr/bin/env python3
"""Generates first person Immersive Eating animations for the in-scope foods and drinks.

Scope: rows of docs/animacoes-inventario.md with Tipo comida or bebida, without a full animation,
whose pose is one of the seven FoodPose kinds. Files are written under kubejs/assets/food and
the map goes to sunlit_tools/eating/ie_all_map.json.

Kinds:
  bowl, plate   vessel and content (palette from the item icon), reusing gen_ie_foods.py shapes
  cup, bottle   vessel lifted and tilted to the mouth, the level drops, no utensil
  hand, slice, skewer  the 16x16 icon extruded into voxels, one cube per opaque run, split into
                       3 bite groups that vanish with scale keyframes; the texture is the icon itself

Only the format and bone names of Immersive Eating are followed; nothing is copied from its assets.
Path collisions: the first item (sorted) owns definitions/<path>.json. A second item with the same
kind shares the owner files and gets definitions/<path>__<ns>.json; a second item of another kind
gets its own files named <path>__<ns>.

Usage (from the instance root, python3 -I):
  gen_ie_foods_all.py --sample 200   write a deterministic sample spread over kinds and mods
  gen_ie_foods_all.py                write every in-scope item
  gen_ie_foods_all.py --sample 200 --items a:b,c:d   sample plus the listed in-scope items
  gen_ie_foods_all.py --check        static check of the map, the files and the baseline hashes
  gen_ie_foods_all.py --clean        remove only the files listed in the map, never baseline files
"""
import argparse
import collections
import hashlib
import io
import json
import math
import os
import sys

from PIL import Image

sys.path.insert(0, "sunlit_tools")
import gen_ie_foods as base  # noqa: E402
import gen_ie_dishes as dishes  # noqa: E402
from eating_assets import active_sources, is_flat, load_model_dump, split  # noqa: E402

OUT = base.OUT
INV = "docs/animacoes-inventario.md"
MAP = "sunlit_tools/eating/ie_all_map.json"
BASELINE = "sunlit_tools/eating/ie_baseline.sha256"
SECONDS = {"hand": 3.0, "slice": 3.0, "skewer": 3.0, "bowl": 4.5, "plate": 4.5, "cup": 3.0, "bottle": 3.0, "jar": 6.0}
VOXEL = ("hand", "slice", "skewer")
ICON_FALLBACK = 0xA5835A
PIXEL = 0.75  # model units per icon pixel
# Hand foods stand upright and lean toward the screen center, more when held by a bone or stick.
# MIRROR = -1 flips the icon left to right if the game shows it mirrored; the lean keeps its screen side.
LEAN_HANDLE = 20
LEAN_PLAIN = 15
MIRROR = 1


def inventory():
    # Items this script generated before are marked as full in the inventory; they stay in scope
    # so a change to the generator can regenerate them.
    try:
        ours = set(json.load(open(MAP, encoding="utf-8")))
    except (OSError, ValueError):
        ours = set()
    rows = []
    for line in open(INV, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not cells[0].startswith("`"):
            continue
        item, tipo, pose, full = cells[0].strip("`"), cells[2], cells[3], cells[6]
        if tipo in ("comida", "bebida") and (full == "não" or item in ours) and pose in SECONDS:
            rows.append((item, pose))
    return rows


def baseline_hashes():
    out = {}
    for line in open(BASELINE, encoding="utf-8"):
        digest, path = line.split()
        out[path] = digest
    return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def plan():
    """Returns the in-scope (item, kind) pairs and the skipped items by reason."""
    base_paths = {os.path.basename(p)[:-5] for p in baseline_hashes() if "/definitions/" in p}
    addon = set()
    for ns in os.listdir("kubejs/assets"):
        if ns == "food":
            continue
        d = os.path.join("kubejs/assets", ns, "definitions")
        if os.path.isdir(d):
            addon |= {f[:-5] for f in os.listdir(d) if f.endswith(".json")}
    included, skipped = [], collections.defaultdict(list)
    for item, kind in inventory():
        kind = jar_kind(item, kind)
        path = item.split(":", 1)[1]
        if path in base_paths:
            skipped["baseline"].append(item)
        elif path in addon:
            skipped["addon"].append(item)
        else:
            included.append((item, kind))
    return included, skipped


def sample(included, n):
    if n is None:
        return sorted(included)
    by_kind = collections.defaultdict(list)
    for item, kind in sorted(included, key=lambda r: (r[0].split(":")[0], r[0])):
        by_kind[kind].append((item, kind))
    counts = {k: len(v) for k, v in by_kind.items()}
    total = sum(counts.values())
    quota = {k: max(1, round(n * c / total)) for k, c in counts.items()}
    biggest = max(counts, key=counts.get)
    quota[biggest] += n - sum(quota.values())
    chosen = []
    for kind in sorted(by_kind):
        items, q = by_kind[kind], quota[kind]
        chosen += [items[i * len(items) // q] for i in range(q)]
    return sorted(chosen)


def blob_icon():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    rgb = ((ICON_FALLBACK >> 16) & 255, (ICON_FALLBACK >> 8) & 255, ICON_FALLBACK & 255, 255)
    for y in range(16):
        for x in range(16):
            if (x - 7.5) ** 2 + (y - 7.5) ** 2 <= 56:
                im.putpixel((x, y), rgb)
    return im


def gui_model(model, src):
    """3D items with separate transforms keep a flat model for the inventory; its icon is the item's look."""
    parent = model.get("perspectives", {}).get("gui", {}).get("parent")
    if not parent:
        return None
    ns, path = split(parent)
    raw = src.read(f"assets/{ns}/models/{path}.json")
    try:
        return json.loads(raw) if raw is not None else None
    except ValueError:
        return None


def icon_for(item, models, src):
    model = models.get(item)
    if model and "perspectives" in model:
        model = gui_model(model, src) or model
    textures = model.get("textures", {}) if model else {}
    flat = model and (is_flat(model, src, item) or model.get("parent") in ("minecraft:item/generated", "item/generated"))
    if not flat or "layer0" not in textures:
        return None
    ns, path = split(textures["layer0"])
    raw = src.read(f"assets/{ns}/textures/{path}.png")
    if raw is None:
        return None
    im = Image.open(io.BytesIO(raw)).convert("RGBA")
    im = im.crop((0, 0, im.width, im.width))
    return im if im.width == 16 else im.resize((16, 16), Image.NEAREST)


def palette(im):
    counts = collections.Counter()
    for r, g, b, a in im.getdata():
        if a >= 128:
            counts[(r // 32, g // 32, b // 32)] += 1
    if not counts:
        return [ICON_FALLBACK] * 3
    top = [((q[0] * 32 + 16) << 16) | ((q[1] * 32 + 16) << 8) | (q[2] * 32 + 16) for q, _ in counts.most_common(3)]
    return top + [top[0]] * (3 - len(top))


def voxel(x0, x1, y, color_uv):
    n = x1 - x0
    return {"origin": [round(-14 + x0 * PIXEL, 3), round(-26 + y * PIXEL, 3), 4],
            "size": [round(n * PIXEL, 3), PIXEL, 3],
            "uv": {"north": {"uv": [x0, y], "uv_size": [n, 1]}, "south": {"uv": [x0, y], "uv_size": [n, 1]},
                   "east": {"uv": [x0, y], "uv_size": [1, 1]}, "west": {"uv": [x0, y], "uv_size": [1, 1]},
                   "up": {"uv": [x0, y], "uv_size": [n, 1]}, "down": {"uv": [x0, y], "uv_size": [n, 1]}}}


def is_handle_color(c, kind):
    """Bone-like pale colors; skewers also get wood tones, since their stick is wood."""
    r, g, b = c
    hi, lo = max(c), min(c)
    if hi >= 140 and (hi - lo) / hi <= 0.25:
        return True
    return kind == "skewer" and r > g > b and r - b >= 40 and 90 <= hi <= 200


# Foods whose icon shows a bone to hold. A color test alone also catches cream, rice and plates.
BONE_WORDS = ("chop", "drumstick", "knuckle", "shank", "leg", "rib", "rack", "wing", "ham")


def skewer_grip(opaque):
    """Skewer icons are diagonal with the stick end at the bottom left: hold the stick there, eat from the top right.
    The lowest fifth along the stick stays in the hand as the handle."""
    pts = list(opaque)
    lo = max(pts, key=lambda p: (p[1] - p[0], p[1]))
    hi = min(pts, key=lambda p: (p[1] - p[0], -p[0]))
    ax, ay = hi[0] - lo[0], hi[1] - lo[1]
    norm = math.hypot(ax, ay) or 1.0
    axis = (ax / norm, ay / norm)
    grip = (lo[0] + 0.5 + axis[0] * 1.5, lo[1] + 0.5 + axis[1] * 1.5)
    handle = {p for p in pts if (p[0] + 0.5 - lo[0] - 0.5) * axis[0] + (p[1] + 0.5 - lo[1] - 0.5) * axis[1] < 0.2 * norm}
    return grip, axis, handle


def grip_and_axis(opaque, kind, item=""):
    """Returns (grip, axis, handle pixels) in icon coords. Grip is where the hand holds the food.
    Without a valid handle the grip sits low in the icon and the axis points up."""
    pts = list(opaque)
    if pts:
        x0 = min(p[0] for p in pts)
        x1 = max(p[0] for p in pts) + 1
        y0 = min(p[1] for p in pts)
        y1 = max(p[1] for p in pts) + 1
    else:
        x0, x1, y0, y1 = 0, 1, 0, 1
    bw, bh = x1 - x0, y1 - y0
    if kind == "skewer" and len(pts) >= 4:
        return skewer_grip(opaque)
    bony = any(t in BONE_WORDS or t[:-1] in BONE_WORDS for t in item.split(":", 1)[-1].split("_"))
    cand = {p for p, c in opaque.items() if is_handle_color(c, kind)} if bony else set()
    food = [p for p in pts if p not in cand]
    if 3 <= len(cand) <= 0.4 * len(opaque) and food:
        hc = centroid(cand)
        fc = centroid(food)
        if math.hypot(hc[0] - fc[0], hc[1] - fc[1]) >= 0.3 * max(bw, bh):
            ax, ay = fc[0] - hc[0], fc[1] - hc[1]
            norm = math.hypot(ax, ay)
            return hc, (ax / norm, ay / norm), cand
    return ((x0 + x1) / 2, y1 - 0.25 * bh), (0.0, -1.0), set()


def centroid(points):
    """Pixel centers, so the result lives in the same space as the grip (edge coords shifted by 0.5)."""
    n = len(points)
    return (sum(x + 0.5 for x, _ in points) / n, sum(y + 0.5 for _, y in points) / n)


def mapped_cube(x0, x1, y, hand, grip):
    """One row run [x0, x1) at row y, placed so the grip pixel lands on the hand pivot."""
    hx, hy, hz = hand
    gx, gy = grip
    cube = voxel(x0, x1, y, None)
    xa = hx + MIRROR * (x0 - gx) * PIXEL
    xb = hx + MIRROR * (x1 - gx) * PIXEL
    # Model y grows upward while icon y grows downward, so the run's lower edge is row y + 1.
    cube["origin"] = [round(min(xa, xb), 3), round(hy - (y + 1 - gy) * PIXEL, 3), round(hz - 1.5, 3)]
    return cube


def cells_cubes(cells, hand, grip):
    """One cube per horizontal run of equal color. cells maps (x, y) to a color."""
    cubes = []
    for y in range(16):
        run = None
        for x in range(17):
            c = cells.get((x, y)) if x < 16 else None
            if run and (c is None or c != run[2]):
                cubes.append(mapped_cube(run[0], x, y, hand, grip))
                run = None
            if c is not None and run is None:
                run = (x, x, c)
    return cubes


def voxel_bones(icon, painter, kind="hand", item=""):
    hand = (-8, -19, 7)
    hx, hy, hz = hand
    px = icon.load()
    w, h = icon.size
    opaque = {(x, y): px[x, y][:3] for y in range(h) for x in range(w) if px[x, y][3] >= 128}
    grip, axis, handle = grip_and_axis(opaque, kind, item)
    food = {p: c for p, c in opaque.items() if p not in handle}
    # Bites go from the far end (largest projection on the axis) to the grip, in equal thirds.
    proj = {p: (p[0] + 0.5 - grip[0]) * axis[0] + (p[1] + 0.5 - grip[1]) * axis[1] for p in food}
    tmin, tmax = (min(proj.values()), max(proj.values())) if proj else (0, 0)
    span = tmax - tmin

    def group(p):
        return 0 if span <= 0 else min(2, int((tmax - proj[p]) / span * 3))

    # Lean is mirrored with MIRROR so that flipping MIRROR keeps the food leaning to the same screen side.
    lean = (LEAN_HANDLE if handle else LEAN_PLAIN) * MIRROR
    # Model-space axis (x mirrored, y up); rotate it onto +y, then lean. A positive z rotation in the
    # game turns +y toward +x (clockwise on screen, checked with a diagonal skewer), hence phi - 90.
    phi = math.degrees(math.atan2(-axis[1], MIRROR * axis[0]))
    angle = round((phi - 90 + lean + 180) % 360 - 180, 3)
    bones = core(painter) + [base.bone("food", "rightArm", hand, rotation=(90, 0, 0)),
                             base.bone("orient", "food", hand, rotation=(0, 0, angle)),
                             base.bone("eat", "orient", hand)]
    if handle:
        bones.append(base.bone("handle", "orient", hand, cells_cubes({p: opaque[p] for p in handle}, hand, grip)))
    for g in range(3):
        cells = {p: c for p, c in food.items() if group(p) == g}
        bones.append(base.bone(str(g + 1), "eat", hand, cells_cubes(cells, hand, grip)))
    return bones


def core(painter):
    return [base.bone("root", None, (0, -8, 7), rotation=(-7.5, 0, 0)), base.bone("bone", "root", (0, -7, 6)),
            # One hand foods and drinks: the left arm rests down out of view, also in the still pose
            # Immersive Eating shows before and while blending into the animation.
            base.arm(painter, "leftArm", 8, (0, 6, 0)), base.arm(painter, "rightArm", -8, (-90, -6, 0))]


def walls(painter, color, box, base_only=False):
    x0, x1, y0, y1, z0, z1 = box
    t = 0.6
    parts = [base.cube(painter, (x0, y0, z0), (x1 - x0, t, z1 - z0), color)] if base_only else [
        base.cube(painter, (x0, y0, z0), (t, y1 - y0, z1 - z0), color),
        base.cube(painter, (x1 - t, y0, z0), (t, y1 - y0, z1 - z0), color),
        base.cube(painter, (x0, y0, z0), (x1 - x0, y1 - y0, t), color),
        base.cube(painter, (x0, y0, z1 - t), (x1 - x0, y1 - y0, t), color),
        base.cube(painter, (x0, y1 - t, z0), (x1 - x0, t, z1 - z0), color)]
    return parts


def drink_color(im):
    """Most common saturated color of the icon, so the liquid is not painted with the glass or the outline."""
    counts = collections.Counter()
    for r, g, b, a in im.getdata():
        hi, lo = max(r, g, b), min(r, g, b)
        if a >= 128 and hi >= 48 and (hi - lo) / hi >= 0.25:
            counts[(r // 32, g // 32, b // 32)] += 1
    if not counts:
        return palette(im)[0]
    q = counts.most_common(1)[0][0]
    return ((q[0] * 32 + 16) << 16) | ((q[1] * 32 + 16) << 8) | (q[2] * 32 + 16)


def drink_bones(kind, vessel, liquid, painter):
    """A vessel held upright in the right hand. Three liquid layers vanish from the top, like the bites of a food."""
    hx, hy, hz = hand = (-8, -19, 7)
    bones = core(painter) + [base.bone("food", "rightArm", hand, rotation=(90, 0, 0)), base.bone("eat", "food", hand)]
    if kind == "cup":
        x0, x1, y0, y1, z0, z1 = hx - 4, hx + 4, hy - 4, hy + 3, hz - 4, hz + 4
        cubes = [base.cube(painter, (x0, y0, z0), (x1 - x0, 0.8, z1 - z0), vessel),
                 base.cube(painter, (x0, y0, z0), (0.8, y1 - y0, z1 - z0), vessel),
                 base.cube(painter, (x1 - 0.8, y0, z0), (0.8, y1 - y0, z1 - z0), vessel),
                 base.cube(painter, (x0, y0, z0), (x1 - x0, y1 - y0, 0.8), vessel),
                 base.cube(painter, (x0, y0, z1 - 0.8), (x1 - x0, y1 - y0, 0.8), vessel),
                 base.cube(painter, (x0 - 2, y0 + 2, hz - 0.5), (2, 3, 1), vessel)]
        lx0, lx1, lz0, lz1, ly0, ly1 = x0 + 0.8, x1 - 0.8, z0 + 0.8, z1 - 0.8, y0 + 0.8, y1 - 0.8
    else:
        x0, x1, y0, y1, z0, z1 = hx - 2.5, hx + 2.5, hy - 6, hy + 4, hz - 2.5, hz + 2.5
        cubes = [base.cube(painter, (x0, y0, z0), (x1 - x0, y1 - y0, z1 - z0), vessel),
                 base.cube(painter, (hx - 1.5, y1, hz - 1.5), (3, 2, 3), vessel),
                 base.cube(painter, (hx - 1, y1 + 2, hz - 1), (2, 2, 2), 0x8A6642)]
        lx0, lx1, lz0, lz1, ly0, ly1 = x0 - 0.4, x1 + 0.4, z0 - 0.4, z1 + 0.4, y0 + 0.5, y1 - 1
    bones.append(base.bone("vessel", "food", hand, cubes))
    h = (ly1 - ly0) / 3
    for n in range(3):
        y = ly1 - (n + 1) * h
        bones.append(base.bone(str(n + 1), "eat", (hx, y, hz), [
            base.cube(painter, (lx0, y, lz0), (lx1 - lx0, h, lz1 - lz0), liquid)]))
    return bones


JAR_NOT = ("bread_with_jam", "jam_roll", "music_jam")


def jar_kind(item, kind):
    """Lidded jars (mayonnaise, preserves, jam, jelly) are opened and sipped, never bitten or held as a mug."""
    path = item.split(":", 1)[1]
    if path in JAR_NOT or path.endswith("mayonnaise_bottle"):
        return kind
    if path.endswith("_flask"):
        return "bottle"
    if "mayonnaise" in path or path.endswith(("_preserves", "_jam", "_jelly")):
        return "jar"
    return kind


def common(im, rows, light=False):
    counts = collections.Counter()
    for y in rows:
        for x in range(16):
            r, g, b, a = im.getpixel((x, y))
            if a >= 128 and max(r, g, b) >= (150 if light else 60):
                counts[(r // 24, g // 24, b // 24)] += 1
    if not counts:
        return None
    q = counts.most_common(1)[0][0]
    return ((q[0] * 24 + 12) << 16) | ((q[1] * 24 + 12) << 8) | (q[2] * 24 + 12)


def jar_bones(item, icon, painter):
    """A lidded jar in the right hand. The lid comes off first, then four sips empty it from the top."""
    hx, hy, hz = hand = (-8, -19, 7)
    bones = core(painter) + [base.bone("food", "rightArm", hand, rotation=(90, 0, 0)), base.bone("eat", "food", hand)]
    mayo = "mayonnaise" in item
    label = drink_color(icon) if icon else 0xE8C860
    lid = (common(icon, range(0, 5)) if icon else None) or 0xD8B030
    body = ((common(icon, range(6, 16), light=True) if icon else None) or 0xF2F0EA) if mayo else label
    content = 0xF3E9C6 if mayo else label
    glass = 0xF2F0EA if mayo else 0xBFD8E0
    # The jar sits in front of the fist; centered on the hand, the forearm showed inside the empty jar.
    jz = hz - 4.5
    x0, x1, y0, y1, z0, z1 = hx - 3, hx + 3, hy - 5, hy + 2, jz - 3, jz + 3
    t = 0.7
    cubes = [base.cube(painter, (x0, y0, z0), (6, t, 6), body),
             base.cube(painter, (x0, y0, z0), (t, 7, 6), body), base.cube(painter, (x1 - t, y0, z0), (t, 7, 6), body),
             base.cube(painter, (x0 + t, y0, z0), (6 - 2 * t, 7, t), body), base.cube(painter, (x0 + t, y0, z1 - t), (6 - 2 * t, 7, t), body),
             # neck: a narrower glass ring above the shoulder
             base.cube(painter, (x0 + 0.5, y1, z0 + 0.5), (5, 1, 0.6), glass), base.cube(painter, (x0 + 0.5, y1, z1 - 1.1), (5, 1, 0.6), glass),
             base.cube(painter, (x0 + 0.5, y1, z0 + 1.1), (0.6, 1, 3.8), glass), base.cube(painter, (x1 - 1.1, y1, z0 + 1.1), (0.6, 1, 3.8), glass)]
    if mayo:
        # label band around the middle of the jar
        cubes += [base.cube(painter, (x0 - 0.1, y0 + 2, z0 + 1), (0.1, 2.6, 4), label), base.cube(painter, (x1, y0 + 2, z0 + 1), (0.1, 2.6, 4), label),
                  base.cube(painter, (x0 + 1, y0 + 2, z0 - 0.1), (4, 2.6, 0.1), label), base.cube(painter, (x0 + 1, y0 + 2, z1), (4, 2.6, 0.1), label)]
    bones.append(base.bone("vessel", "food", hand, cubes))
    bones.append(base.bone("lid", "food", (hx, y1 + 1, jz), [
        base.cube(painter, (x0 + 0.2, y1 + 1, z0 + 0.2), (5.6, 1.4, 5.6), lid), base.cube(painter, (x0 + 1, y1 + 2.4, z0 + 1), (4, 0.3, 4), common(icon, range(0, 3)) or lid if icon else lid)]))
    lx0, lz0, w = x0 + t, z0 + t, 6 - 2 * t
    ly0, ly1 = y0 + t, y1 + 0.6
    h = (ly1 - ly0) / 4
    for n in range(4):
        y = ly1 - (n + 1) * h
        bones.append(base.bone(str(n + 1), "eat", (hx, y, jz), [base.cube(painter, (lx0, y, lz0), (w, h, w), content)]))
    return bones


def jar_animation():
    anim = base.animation({"shape": "hand", "seconds": SECONDS["jar"], "bites": 4, "sound": "soup", "start": 1.4})
    bones = anim["animations"]["eat"]["bones"]
    # The lid is lifted off the neck and put aside before the first sip; scale 0 keeps it off in third person too.
    bones["lid"] = {"position": base.frames([(0, (0, 0, 0)), (0.45, (0, 0, 0)), (0.8, (0, 2.5, 0)), (1.15, (5, 3.5, 0))]),
                    "scale": base.frames([(0, (1, 1, 1)), (1.14, (1, 1, 1)), (1.15, (0, 0, 0))])}
    return anim


def build(item, kind, icon, path):
    """Returns (geo, animation, texture image) for one kind of item."""
    painter = base.Painter(item)
    secs = SECONDS[kind]
    if kind in VOXEL:
        im = icon or blob_icon()
        bones = voxel_bones(im, painter, kind, item)
        anim = base.animation({"shape": "hand", "seconds": secs, "bites": 3, "sound": "eating"})
        tex, size = im, 16
    elif kind in ("bowl", "plate"):
        pal = palette(icon) if icon else [ICON_FALLBACK] * 3
        bowl = kind == "bowl"
        food = dict(shape="soup" if bowl else "plate", seconds=secs, bites=3, utensil="spoon" if bowl else "fork",
                    vessel=0x7A5230 if bowl else 0xD9D3C6, rim=0x94683F if bowl else 0xEFEBDF, content=pal[0],
                    bits=pal, sound="soup" if bowl else "eating")
        bones = dishes.dish_bones(item, kind, icon, painter, food)
        anim = base.animation(food)
        tex, size = painter.image, 128
    elif kind == "jar":
        bones = jar_bones(item, icon, painter)
        anim = jar_animation()
        tex, size = painter.image, 128
    else:
        liquid = drink_color(icon) if icon else ICON_FALLBACK
        vessel = 0xBFD8E0 if kind == "bottle" else 0xCBB89A
        bones = drink_bones(kind, vessel, liquid, painter)
        anim = base.animation({"shape": "hand", "seconds": secs, "bites": 3, "sound": "eating"})
        tex, size = painter.image, 128
    bones.insert(0, base.bone("camera", None, (0, 0, 0)))
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{path}", "texture_width": size, "texture_height": size,
                        "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 0.5, 0]},
        "bones": bones}]}
    return geo, anim, tex


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def generate(n, extra=()):
    included, skipped = plan()
    chosen = sample(included, n)
    if extra:
        scope = dict(included)
        for item in extra:
            if item not in scope:
                raise SystemExit(f"not in scope, cannot generate: {item}")
            if (item, scope[item]) not in chosen:
                chosen.append((item, scope[item]))
        chosen = sorted(chosen)
    models, src = load_model_dump(), active_sources()
    owners, out_map, stats, no_icon = {}, {}, collections.defaultdict(lambda: [0, 0]), []
    collisions = 0
    for item, kind in chosen:
        ns, path = item.split(":", 1)
        if path in owners and owners[path][1] == kind:
            name, reuse = path, True
            collisions += 1
        elif path in owners:
            name, reuse = f"{path}__{ns}", False
            collisions += 1
        else:
            owners[path] = (item, kind)
            name, reuse = path, False
        icon = icon_for(item, models, src)
        if icon is None:
            no_icon.append(item)
        written = 0
        if not reuse:
            geo, anim, tex = build(item, kind, icon, name)
            written += dump(f"{OUT}/geo/{name}.geo.json", geo)
            written += dump(f"{OUT}/animations/{name}.animation.json", anim)
            os.makedirs(f"{OUT}/textures/item", exist_ok=True)
            tex.save(f"{OUT}/textures/item/{name}.png", optimize=True)
            written += os.path.getsize(f"{OUT}/textures/item/{name}.png")
        dname = path if item == owners[path][0] else f"{path}__{ns}"
        written += dump(f"{OUT}/definitions/{dname}.json", {
            "item": item, "invisible": ["utensil"] if kind in ("bowl", "plate") else [],
            "sounds": {"eating": "food:eat", "soup": "food:soup"}})
        out_map[item] = {"kind": kind, "seconds": SECONDS[kind], "geo": f"{OUT}/geo/{name}.geo.json",
                         "texture": f"{OUT}/textures/item/{name}.png", "animation": f"{OUT}/animations/{name}.animation.json"}
        stats[kind][0] += 1
        stats[kind][1] += written
    if not n:
        # A baseline model is never rewritten: items sharing its path only get a definition of their own.
        for item in skipped["baseline"]:
            ns, path = item.split(":", 1)
            definition = json.load(open(f"{OUT}/definitions/{path}.json", encoding="utf-8"))
            definition["item"] = item
            dump(f"{OUT}/definitions/{path}__{ns}.json", definition)
            out_map[item] = {"kind": "shared", "seconds": 0, "geo": f"{OUT}/geo/{path}.geo.json",
                             "texture": f"{OUT}/textures/item/{path}.png", "animation": f"{OUT}/animations/{path}.animation.json"}
    dump(MAP, out_map)
    return included, skipped, chosen, stats, no_icon, collisions


def report(included, skipped, chosen, stats, no_icon, collisions):
    print(f"in scope: {len(included)}; sampled: {len(chosen)}; path collisions in sample: {collisions}")
    for reason, items in sorted(skipped.items()):
        print(f"skipped ({reason}): {len(items)}")
    total = 0
    for kind in sorted(stats):
        n, b = stats[kind]
        total += b
        print(f"{kind}: items {n}, bytes {b}, bytes/item {b // max(1, n)}")
    per_item = total / max(1, len(chosen))
    print(f"total bytes {total}, bytes/item {per_item:.0f}, extrapolated to {len(included)} items: {per_item * len(included) / 1e6:.2f} MB")
    print(f"items without flat icon (neutral fallback): {len(no_icon)}")
    for item in no_icon:
        print(f"  no icon: {item}")


def check():
    errors = []
    m = json.load(open(MAP, encoding="utf-8"))
    counts = collections.Counter(v["kind"] for v in m.values())
    for item, v in m.items():
        path = item.split(":", 1)[1]
        ns = item.split(":", 1)[0]
        found = [p for p in (f"{OUT}/definitions/{path}.json", f"{OUT}/definitions/{path}__{ns}.json") if os.path.exists(p)]
        match = [p for p in found if json.load(open(p, encoding="utf-8")).get("item") == item]
        if len(match) != 1:
            errors.append(f"definition {item}")
        for key in ("geo", "animation", "texture"):
            if not os.path.exists(v[key]):
                errors.append(f"{key} missing {item}")
        if not errors or errors[-1] != f"definition {item}":
            geo = json.load(open(v["geo"], encoding="utf-8"))
            anim = json.load(open(v["animation"], encoding="utf-8"))
            bones = {b["name"] for b in geo["minecraft:geometry"][0]["bones"]}
            eat = anim["animations"]["eat"]
            if not set(eat["bones"]) <= bones:
                errors.append(f"missing bones {item}")
            if "finished;" not in eat["timeline"].values():
                errors.append(f"no finished; {item}")
            Image.open(v["texture"]).verify()
    baseline = baseline_hashes()
    for path, digest in baseline.items():
        if not os.path.exists(path) or sha(path) != digest:
            errors.append(f"baseline changed {path}")
    included, skipped = plan()
    print(f"map items: {len(m)}; per kind: {dict(sorted(counts.items()))}")
    for reason, items in sorted(skipped.items()):
        print(f"skipped ({reason}): {len(items)}: {', '.join(items[:30])}{' ...' if len(items) > 30 else ''}")
    print(f"baseline files checked: {len(baseline)}")
    for e in errors:
        print("ERROR", e)
    print("CHECK", "PASS" if not errors else f"FAIL ({len(errors)})")
    return not errors


def clean():
    if not os.path.exists(MAP):
        print("no map, nothing to clean")
        return
    baseline = set(baseline_hashes())
    m = json.load(open(MAP, encoding="utf-8"))
    removed = 0
    for item, v in m.items():
        path, ns = item.split(":", 1)[1], item.split(":", 1)[0]
        for key in ("geo", "animation", "texture"):
            if v[key] not in baseline and os.path.exists(v[key]):
                os.remove(v[key])
                removed += 1
        for p in (f"{OUT}/definitions/{path}.json", f"{OUT}/definitions/{path}__{ns}.json"):
            if p not in baseline and os.path.exists(p) and json.load(open(p, encoding="utf-8")).get("item") == item:
                os.remove(p)
                removed += 1
    os.remove(MAP)
    print(f"removed {removed} generated files and the map")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--items", type=lambda s: [x for x in s.split(",") if x], default=[],
                    help="extra in-scope items to generate on top of the sample, comma separated")
    args = ap.parse_args()
    if args.check:
        sys.exit(0 if check() else 1)
    if args.clean:
        clean()
        return
    report(*generate(args.sample, args.items))


if __name__ == "__main__":
    main()
