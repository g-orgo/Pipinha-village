#!/usr/bin/env python3
"""Bowl and plate dishes for gen_ie_foods_all.py: a rounded vessel, a broth or base and real ingredient pieces.

Ingredients come from the dish recipe (sunlit_tools/eating/dish_ingredients.json, rebuilt with --ingredients)
and from the item name. Each ingredient has its own colors and cut: meat chunks with a seared side,
carrot coins, potato cubes, mushroom caps, noodles... The icon only gives the broth color and the
fallback pieces, never the outline or the vessel colors.
"""
import collections
import json
import math
import random
import re
import sys

sys.path.insert(0, "sunlit_tools")
import gen_ie_foods as base  # noqa: E402

CACHE = "sunlit_tools/eating/dish_ingredients.json"
# word in the dish name or in a recipe ingredient id -> (cut, main color, second color)
INGREDIENTS = [
    (("mutton", "lamb", "goat", "beef", "steak", "venison", "pork", "bacon", "ham", "meat", "flesh", "rabbit", "sausage", "minced"), ("chunk", 0x7A3E26, 0xC9906A)),
    (("chicken", "turkey", "duck", "poultry", "wing"), ("chunk", 0xD9A066, 0xF0D2A4)),
    (("salmon", "tuna", "trout"), ("chunk", 0xE58866, 0xF4C7B0)),
    (("cod", "fish", "fillet", "eel", "squid", "tentacle", "calamari"), ("chunk", 0xEADCC4, 0xC9B08E)),
    (("crab", "shrimp", "prawn", "lobster", "clam", "mussel", "scallop"), ("chunk", 0xE0704A, 0xF5E4D4)),
    (("carrot",), ("coin", 0xE8781E, 0xF5A040)),
    (("potato",), ("cube", 0xE6CC7A, 0xF2E0A6)),
    (("radish", "turnip", "daikon"), ("coin", 0xF2EEE6, 0xD8667E)),
    (("onion", "garlic", "leek", "scallion"), ("slice", 0xEDE3C8, 0x9CBF6A)),
    (("mushroom", "fungus", "truffle", "morel"), ("cap", 0x8A5A3C, 0xDCCCAC)),
    (("tomato",), ("cube", 0xD8382A, 0xF06A4E)),
    (("beetroot", "beet"), ("cube", 0x8E1F3A, 0xB0304E)),
    (("chili", "chilli"), ("slice", 0xC8281E, 0x4E8A2E)),
    (("eggplant", "aubergine"), ("coin", 0x5A2E6A, 0xE8DCC0)),
    (("cheese", "parmesan", "tofu"), ("cube", 0xF2DC8A, 0xFFF0B8)),
    (("pumpkin", "squash"), ("cube", 0xE0902A, 0xF2B45A)),
    (("corn", "maize"), ("grain", 0xF2D04A, 0xE6B832)),
    (("pea", "bean", "cabbage", "lettuce", "kale", "spinach", "herb", "basil", "broccoli", "greens", "seaweed", "kelp", "celery", "pepper"), ("leaf", 0x5E9A3A, 0x86BE52)),
    (("rice",), ("grain", 0xF4F0E4, 0xE6E0CE)),
    (("noodle", "pasta", "ramen", "udon", "spaghetti", "dough"), ("strand", 0xEAC97A, 0xF2DA9A)),
    (("egg",), ("egg", 0xF6F2E6, 0xF2B92B)),
    (("berry", "berries", "cherry", "grape"), ("grain", 0x8A2A4A, 0xB8406A)),
    (("apple", "pear", "peach", "fruit"), ("cube", 0xF0E2B0, 0xD8B85A)),
]
CREAMY = ("cream", "chowder", "milk", "porridge", "oatmeal", "potato_soup", "congee")


def build_cache():
    """dish id -> recipe ingredient ids and tags, read from the jars and kubejs/data."""
    import dish_prices as dp
    recipes, tags = dp.load_data()
    out = collections.defaultdict(set)
    for recipe in recipes:
        result, _ = dp.recipe_result(recipe)
        ingredients = dp.recipe_ingredients(recipe)
        if not result or not ingredients:
            continue
        for ing in ingredients:
            for opt in ing if isinstance(ing, list) else [ing]:
                if isinstance(opt, dict):
                    out[result].add(opt.get("item") or "#" + str(opt.get("tag", "")))
    base.json.dump({k: sorted(v) for k, v in sorted(out.items())}, open(CACHE, "w", encoding="utf-8"), indent=0)
    print(f"{len(out)} recipes written to {CACHE}")


_cache = None


def ingredients(item):
    """Ordered ingredient kinds for a dish: the name first, then the recipe."""
    global _cache
    if _cache is None:
        try:
            _cache = json.load(open(CACHE, encoding="utf-8"))
        except OSError:
            _cache = {}
    words = [item.split(":", 1)[1]] + [w for w in _cache.get(item, []) if "bowl" not in w and "plate" not in w]
    found = []
    for text in words:
        for keys, spec in INGREDIENTS:
            tokens = set(re.split(r"[^a-z]+", text.lower()))
            if any(k in tokens or k + "s" in tokens or k + "es" in tokens for k in keys) and spec not in found:
                found.append(spec)
    return found[:4]


def icon_colors(icon):
    """Broth and fallback piece colors from the top of the icon, without the outline or the vessel."""
    if icon is None:
        return 0xA5835A, []
    px = [(x, y, p) for y in range(16) for x in range(16) for p in [icon.getpixel((x, y))] if p[3] >= 128]
    vessel = collections.Counter((p[0] // 24, p[1] // 24, p[2] // 24) for x, y, p in px if y >= 11)
    skip = {q for q, _ in vessel.most_common(2)}
    food = collections.Counter()
    for x, y, (r, g, b, a) in px:
        q = (r // 24, g // 24, b // 24)
        if y < 11 and max(r, g, b) >= 56 and q not in skip:
            food[q] += 1
    cols = [((q[0] * 24 + 12) << 16) | ((q[1] * 24 + 12) << 8) | (q[2] * 24 + 12) for q, _ in food.most_common(4)]
    return (cols[0] if cols else 0xA5835A), cols[1:]


def shade(color, f):
    return (min(255, int((color >> 16 & 255) * f)) << 16) | (min(255, int((color >> 8 & 255) * f)) << 8) | min(255, int((color & 255) * f))


def rcube(painter, origin, size, color, yaw=0.0, tilt=0.0):
    c = base.cube(painter, [round(v, 2) for v in origin], [round(v, 2) for v in size], color)
    if yaw or tilt:
        c["pivot"] = [round(origin[0] + size[0] / 2, 2), round(origin[1], 2), round(origin[2] + size[2] / 2, 2)]
        c["rotation"] = [round(tilt, 1), round(yaw, 1), 0]
    return c


# Bowl pieces are this much bigger than plate pieces and sink this far (unscaled units) into the broth,
# so a thick stew covers about half of each piece instead of showing it whole.
BOWL_PIECE = 1.3
SINK = {"chunk": 1.75, "coin": 1.1, "cube": 1.3, "slice": 1.1, "cap": 1.35, "leaf": 1.15, "strand": 1.0, "egg": 1.3, "grain": 1.05}
# Cuts that stand out of the broth get a collar of sauce clinging to their sides.
COLLAR = {"chunk": (2.4, 2.2), "cube": (1.8, 1.8), "cap": (2.4, 2.4)}


def piece(painter, rng, spec, x, y, z, s=1.0):
    """One ingredient piece centered at x, z with its bottom at y, scaled by s around that point."""
    cut, main, second = spec
    # In a bowl the pieces lie askew in the stew, so often only a corner or an edge comes out of it.
    yaw, tilt = rng.uniform(-35, 35), rng.uniform(-12, 12) * (1.0 if s == 1.0 else 2.4)

    def rcube(painter, origin, size, color, yaw=0.0, tilt=0.0):
        return _rcube(painter, (x + (origin[0] - x) * s, y + (origin[1] - y) * s, z + (origin[2] - z) * s), [v * s for v in size], color, yaw, tilt)
    if cut == "chunk":
        return [rcube(painter, (x - 1.2, y, z - 1.1), (2.4, 1.9, 2.2), main, yaw, tilt),
                rcube(painter, (x - 1.2, y + 1.9, z - 1.1), (2.4, 0.4, 1.2), second, yaw, tilt)]
    if cut == "coin":
        # Coins in a bowl lie almost flat in the stew; on a plate they lean on the other pieces.
        lean = 25 if s == 1.0 else 12
        return [rcube(painter, (x - 1.1, y + 0.6, z - 1.1), (2.2, 0.7, 2.2), main, yaw, rng.uniform(-lean, lean)),
                rcube(painter, (x - 0.5, y + 1.3, z - 0.5), (1.0, 0.1, 1.0), second, yaw)]
    if cut == "cube":
        return [rcube(painter, (x - 0.9, y, z - 0.9), (1.8, 1.8, 1.8), main, yaw, tilt)]
    if cut == "slice":
        return [rcube(painter, (x - 1.4, y + 0.8, z - 0.4), (2.8, 0.5, 0.8), main, yaw, tilt)]
    if cut == "cap":
        return [rcube(painter, (x - 0.4, y, z - 0.4), (0.8, 1.2, 0.8), second, yaw),
                rcube(painter, (x - 1.2, y + 1.2, z - 1.2), (2.4, 0.8, 2.4), main, yaw, tilt)]
    if cut == "leaf":
        return [rcube(painter, (x - 0.9, y + 0.9, z - 0.6), (1.8, 0.3, 1.2), main, yaw, tilt),
                rcube(painter, (x + 0.2, y + 1.0, z - 0.2), (0.9, 0.3, 0.9), second, yaw + 30)]
    if cut == "strand":
        return [rcube(painter, (x - 2.2, y + 0.7, z - 0.3 + k * 0.7), (4.4, 0.5, 0.5), main if k % 2 == 0 else second, yaw + k * 14) for k in range(3)]
    if cut == "egg":
        return [rcube(painter, (x - 1.3, y + 0.7, z - 1.3), (2.6, 0.6, 2.6), main, yaw),
                rcube(painter, (x - 0.6, y + 1.3, z - 0.6), (1.2, 0.5, 1.2), second, yaw)]
    # grain: a small cluster
    return [rcube(painter, (x + dx - 0.35, y + 0.6 + (k % 2) * 0.3, z + dz - 0.35), (0.7, 0.6, 0.7), main if k % 3 else second)
            for k, (dx, dz) in enumerate(((0, 0), (0.8, 0.3), (-0.6, 0.7), (0.3, -0.8), (-0.7, -0.4)))]


_rcube = rcube


def collar(painter, rng, spec, x, top, z, s, broth):
    """Sauce clinging around a piece where it leaves the broth; its height varies so no two collars share a face."""
    w, d = COLLAR[spec[0]]
    w, d, h = (w + 0.9) * s, (d + 0.9) * s, rng.uniform(0.3, 0.5)
    return [rcube(painter, (x - w / 2, top - 0.3, z - d / 2), (w, 0.3 + h, d), shade(broth, 1.06))]


def octagon(painter, cx, cz, half, y0, h, color, rim=None, t=1.0):
    """A ring with cut corners, so the vessel reads round from above."""
    a, b = half - 1, half
    parts = [rcube(painter, (cx - a, y0, cz - b), (2 * a, h, t), color), rcube(painter, (cx - a, y0, cz + b - t), (2 * a, h, t), color),
             rcube(painter, (cx - b, y0, cz - a), (t, h, 2 * a), color), rcube(painter, (cx + b - t, y0, cz - a), (t, h, 2 * a), color)]
    for sx in (-1, 1):
        for sz in (-1, 1):
            # Diagonal step between the two slabs, just inside the cut corner.
            parts.append(rcube(painter, (cx - a if sx < 0 else cx + a - t, y0, cz - a if sz < 0 else cz + a - t), (t, h, t), color))
    if rim:
        parts += [rcube(painter, (cx - a, y0 + h, cz - b), (2 * a, 0.4, t), rim), rcube(painter, (cx - a, y0 + h, cz + b - t), (2 * a, 0.4, t), rim),
                  rcube(painter, (cx - b, y0 + h, cz - a), (t, 0.4, 2 * a), rim), rcube(painter, (cx + b - t, y0 + h, cz - a), (t, 0.4, 2 * a), rim)]
    return parts


def disc(painter, cx, cz, half, y0, h, color):
    """Filled octagon, no overlapping faces."""
    a = half - 1
    return [rcube(painter, (cx - a, y0, cz - a), (2 * a, h, 2 * a), color),
            rcube(painter, (cx - a, y0, cz - half), (2 * a, h, 1), color), rcube(painter, (cx - a, y0, cz + a), (2 * a, h, 1), color),
            rcube(painter, (cx - half, y0, cz - a), (1, h, 2 * a), color), rcube(painter, (cx + a, y0, cz - a), (1, h, 2 * a), color)]


def dish_bones(item, kind, icon, painter, food):
    """Bones of a bowl or plate dish. food is the gen_ie_foods dict; its bones and utensil are kept."""
    rng = random.Random(item)
    bowl = kind == "bowl"
    broth, extra = icon_colors(icon) if icon is not None or "content" not in food else (food["content"], food["bits"])
    if any(w in item for w in CREAMY):
        broth = 0xE8DCC0
    specs = ingredients(item) or [("chunk", c, shade(c, 1.25)) for c in extra[:3]] or [("cube", shade(broth, 0.8), broth)]
    bones = [base.bone("root", None, (0, -8, 7), rotation=(-7.5, 0, 0)), base.bone("bone", "root", (0, -7, 6)),
             base.arm(painter, "leftArm", 8, (-90, 6, 0)), base.arm(painter, "rightArm", -8, (-90, -6, 0)),
             base.bone("food", "bone", (0, -5, -6), rotation=base.VESSEL_TILT), base.bone("eat", "food", (0, -5, -6))]
    cx, cz = 0.0, -6.0
    if bowl:
        wood, rim = food["vessel"], food["rim"]
        vessel = [rcube(painter, (cx - 3, -8, cz - 3), (6, 1, 6), shade(wood, 0.8))] + disc(painter, cx, cz, 5, -7, 1, wood)
        vessel += octagon(painter, cx, cz, 6, -6.5, 1.8, wood) + octagon(painter, cx, cz, 7, -4.7, 1.9, wood, rim)
        # A full bowl: the stew reaches 0.3 below the wall top (-2.8), not halfway down it.
        top = -3.1
        bones.append(base.bone("vessel", "food", (cx, -5, cz), vessel))
        # Broth fills each wall tier up to its inner face, so no broth face lies on a wall face.
        level = disc(painter, cx, cz, 5, -6.5, 1.8, shade(broth, 0.9)) + disc(painter, cx, cz, 6, -4.7, top + 4.7, broth)
        bones.append(base.bone("level", "eat", (cx, -6.5, cz), level))
    else:
        vessel = [rcube(painter, (cx - 4, -7, cz - 4), (8, 0.6, 8), shade(food["vessel"], 0.85))] + disc(painter, cx, cz, 8, -6.4, 0.6, food["vessel"])
        vessel += octagon(painter, cx, cz, 9, -6.2, 0.6, food["rim"])
        top = -5.8
        bones.append(base.bone("vessel", "food", (cx, -5, cz), vessel))
    # Three bite groups, front to back along the spoon path; every group mixes the ingredients.
    if bowl:
        # A full bowl: pieces spread evenly up to the wall (sunflower pattern with jitter), not a heap in the middle.
        spots = []
        for k in range(16):
            r, a = 4.6 * math.sqrt((k + 0.5) / 16), k * 2.39996
            spots.append((r * math.cos(a) + rng.uniform(-0.4, 0.4), r * math.sin(a) + rng.uniform(-0.4, 0.4)))
    else:
        spots = [(rng.uniform(-4.6, 4.6), rng.uniform(-4.6, 4.6)) for _ in range(60)]
        spots = [s for s in spots if math.hypot(*s) <= 4.8][:18] or [(0, 0)]
    for g in range(3):
        cubes = []
        for k, (dx, dz) in enumerate(spots[g::3]):
            spec = specs[(g + k) % len(specs)]
            if bowl:
                s = BOWL_PIECE * rng.uniform(0.92, 1.08)
                sink = SINK[spec[0]] * s + rng.uniform(-0.15, 0.15)
                cubes += piece(painter, rng, spec, cx + dx, top - sink, cz + dz, s)
                if spec[0] in COLLAR:
                    cubes += collar(painter, rng, spec, cx + dx, top, cz + dz, s, broth)
            else:
                cubes += piece(painter, rng, spec, cx + dx, top, cz + dz)
        bones.append(base.bone(str(g + 1), "eat", (cx, -5, cz), cubes))
    bones.extend(base.utensil_bones(painter, food["utensil"], specs[0][1]))
    bones.append(resting_utensil(painter, food["utensil"], cx, top, cz))
    return bones


def resting_utensil(painter, kind, cx, top, cz):
    """The utensil lying in the dish, handle over the right rim. Immersive Eating hides the hand utensil
    in the still pose before the animation (definition "invisible"); this copy shows there and the
    animation scales it to 0 from the first frame, when the hand picks the utensil up."""
    metal, wood = 0xB8BCC2, 0x8A6238
    hx, hy = cx - 1.5, top + 0.2
    if kind == "spoon":
        cubes = [rcube(painter, (hx - 1.3, hy - 0.4, cz - 1.3), (2.6, 0.8, 2.6), metal), rcube(painter, (hx - 12.3, hy, cz - 0.4), (11, 0.8, 0.8), metal)]
    elif kind == "fork":
        cubes = [rcube(painter, (hx - 11.3, hy, cz - 0.4), (11, 0.6, 0.8), metal)] + [rcube(painter, (hx - 0.3, hy, cz - 1.2 + k * 0.8), (2.4, 0.5, 0.4), metal) for k in range(3)]
    else:
        cubes = [rcube(painter, (hx - 10, hy, cz - 1.2 + k * 1.6), (11, 0.7, 0.7), wood) for k in range(2)]
    # Positive z rotation lifts the handle (it runs toward -x, the right side) over the rim.
    return base.bone("utensil_rest", "food", (hx, hy, cz), cubes, rotation=(0, 0, 22 if kind == "spoon" else 12))


if __name__ == "__main__" and "--ingredients" in sys.argv:
    build_cache()
