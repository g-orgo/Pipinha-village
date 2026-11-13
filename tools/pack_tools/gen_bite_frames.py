#!/usr/bin/env python3
"""Generates bite frames for foods that have none, in the format of Eating Animation.

For each active food with a flat icon and no frames, writes under kubejs/assets/<ns>:
  textures/item/sunlit_bite/<path>_<frame>[_l<layer>].png   three frames per texture layer
  models/item/sunlit_bite/<path>_<frame>.json               one generated model per frame
  models/item/<path>.json                                   original model plus the overrides

The original model is kept as is, including its own overrides. Drinks keep their icon, like
vanilla potions under Eating Animation. Run from the instance root; rerunning is safe, since it
only reads models from the dump and textures from the active resources.
Needs Pillow. Usage: gen_bite_frames.py [--dry]
"""
import collections
import io
import json
import os
import random
import re
import sys

from PIL import Image

sys.path.insert(0, "sunlit_tools")
from eating_assets import active_sources, has_frames, is_flat, load_model_dump, split  # noqa: E402

FOODS = "sunlit_tools/eating/foods_dump.txt"
POSES = "sunlit_tools/eating/food_poses.txt"
REMAINING = (0.72, 0.46, 0.2)
USE_POINTS = (0.35, 0.7, 0.9)
VESSEL_POSES = {"bowl", "plate"}


def active_foods():
    removed = set(re.findall(r'["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\']', open("kubejs/startup_scripts/globalRemovedItems.js", encoding="utf-8").read()))
    dupes = set(re.findall(r'^\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"\s*:', open("kubejs/startup_scripts/globalCanonicalItems.js", encoding="utf-8").read(), re.M))
    poses = dict(l.strip().split("|") for l in open(POSES, encoding="utf-8"))
    for line in open(FOODS, encoding="utf-8"):
        f = line.rstrip("\n").split("|")
        if f[1] == "true" and f[2] == "EAT" and f[0] not in removed and f[0] not in dupes:
            yield f[0], poses.get(f[0], "hand"), f[7]


def first_frame(image):
    """Animated textures are vertical strips; a bite frame uses the first one."""
    width, height = image.size
    return image.crop((0, 0, width, width)) if height > width else image


def bite_order(pixels, size, rng):
    """Solid food: bites start at the top right and move along the shape, with a jagged edge."""
    cx, cy = size - 1, 0
    return sorted(pixels, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2 + rng.uniform(-0.1, 0.1) * size * size)


def vessel_order(pixels, size, rng, vessel):
    """Bowl or plate: the content goes first, top to bottom, and the vessel stays."""
    content = [p for p in pixels if p not in vessel]
    return sorted(content, key=lambda p: p[1] + rng.uniform(-1.2, 1.2) * size / 16)


def vessel_pixels(image, pose, remainder, src, opaque):
    """Pixels matching the empty vessel icon. Falls back to the lower half of the shape."""
    size = image.size[0]
    ns, path = split(remainder) if remainder else ("minecraft", "bowl")
    raw = src.read(f"assets/{ns}/textures/item/{path}.png")
    match = set()
    if raw:
        empty = first_frame(Image.open(io.BytesIO(raw)).convert("RGBA"))
        if empty.size == image.size:
            match = {p for p in opaque if empty.getpixel(p) == image.getpixel(p)}
    if len(match) >= 0.25 * len(opaque):
        return match
    top = min(p[1] for p in opaque)
    bottom = max(p[1] for p in opaque)
    cut = top + (bottom - top + 1) * 0.5
    return {p for p in opaque if p[1] >= cut}


def erase_sets(image, item, pose, remainder, src):
    """Returns, per frame, the pixels erased. Empty when the icon has no pixels to work with."""
    size = image.size[0]
    opaque = [(x, y) for y in range(size) for x in range(size) if image.getpixel((x, y))[3] > 0]
    if not opaque:
        return []
    rng = random.Random(item)
    if pose in VESSEL_POSES:
        vessel = vessel_pixels(image, pose, remainder, src, opaque)
        order = vessel_order(opaque, size, rng, vessel)
        total = len(order)
    else:
        order = bite_order(opaque, size, rng)
        total = len(order)
    if total == 0:
        return []
    return [set(order[:round(total * (1 - keep))]) for keep in REMAINING]


def apply(layer, erased):
    out = layer.copy()
    for point in erased:
        out.putpixel(point, (0, 0, 0, 0))
    return out


def main():
    dry = "--dry" in sys.argv
    src = active_sources()
    models = load_model_dump()
    stats = collections.Counter()
    skipped = []
    for item, pose, remainder in active_foods():
        model = models.get(item)
        if has_frames(model):
            stats["already"] += 1
            continue
        if not is_flat(model, src, item):
            stats["3d"] += 1
            skipped.append(item)
            continue
        ns, path = item.split(":", 1)
        layers = sorted((k for k in model.get("textures", {}) if re.fullmatch(r"layer\d+", k)), key=lambda k: int(k[5:]))
        images = {}
        for key in layers:
            tns, tpath = split(model["textures"][key])
            raw = src.read(f"assets/{tns}/textures/{tpath}.png")
            if raw is None:
                break
            images[key] = first_frame(Image.open(io.BytesIO(raw)).convert("RGBA"))
        if len(images) != len(layers) or not layers or images[layers[0]].size[0] != images[layers[0]].size[1] \
                or len({im.size for im in images.values()}) != 1:
            stats["no_texture"] += 1
            skipped.append(item)
            continue
        composite = Image.new("RGBA", images[layers[0]].size)
        for key in layers:
            composite.alpha_composite(images[key])
        sets = erase_sets(composite, item, pose, remainder, src)
        if not sets:
            stats["empty"] += 1
            skipped.append(item)
            continue
        stats["generated"] += 1
        if dry:
            continue
        overrides = list(model.get("overrides", []))
        for frame, erased in enumerate(sets):
            textures = {}
            for number, key in enumerate(layers):
                name = f"{path}_{frame}" if number == 0 else f"{path}_{frame}_l{number}"
                target = f"kubejs/assets/{ns}/textures/item/sunlit_bite/{name}.png"
                os.makedirs(os.path.dirname(target), exist_ok=True)
                apply(images[key], erased).save(target, optimize=True)
                textures[key] = f"{ns}:item/sunlit_bite/{name}"
            target = f"kubejs/assets/{ns}/models/item/sunlit_bite/{path}_{frame}.json"
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as out:
                json.dump({"parent": model.get("parent"), "textures": textures}, out)
            overrides.append({"predicate": {"eatinganimation:eat": USE_POINTS[frame], "eatinganimation:eating": 1.0},
                              "model": f"{ns}:item/sunlit_bite/{path}_{frame}"})
        merged = dict(model)
        merged["overrides"] = overrides
        target = f"kubejs/assets/{ns}/models/item/{path}.json"
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as out:
            json.dump(merged, out)
    print(dict(stats))
    if skipped:
        print("skipped:", " ".join(skipped[:40]), "..." if len(skipped) > 40 else "")


if __name__ == "__main__":
    main()
