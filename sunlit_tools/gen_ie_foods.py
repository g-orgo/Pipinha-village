#!/usr/bin/env python3
"""Writes original full first person animations for Immersive Eating into kubejs/assets/food.

Everything here is authored in this file: shapes, colors and timing. Nothing is derived from the
assets of Immersive Eating (CC BY-NC-ND); only its data format and bone names are followed.
A dish sits on a vessel in front of the player and the right hand brings bites to the mouth with
a utensil. Hand foods are held in the right hand. Duration 4 to 8 s. Run from the instance root.
"""
import json
import os
import random

from PIL import Image

OUT = "kubejs/assets/food"
SIZE = 128
CELL = 16
FACES = ("north", "south", "east", "west", "up", "down")
MOUTH_POS, MOUTH_ROT = (-2.0, 1.0, 3.0), (-24.0, 0.0, 34.0)
# The utensil never turns in the grip: the whole arm carries it. Dip lowers the hand over the right rim
# so the spoon head goes into the stew; scoop drags the hand back toward the player with the head still
# in the stew, like taking a spoonful (poses checked in the headless client); the vessel tilts toward the camera.
# The forearm turns in toward the bowl and the fist stays at its right rim, in view; only arm keyframes move the spoon.
DIP_POS, DIP_ROT = (-12.0, 9.4, -2.5), (-42.2, -65.6, 62.0)
SCOOP_POS, SCOOP_ROT = (-15.4, 9.0, -4.5), (-54.1, -78.5, 70.1)
# A fork on a plate keeps its fist at the right rim and picks the bite there.
FORK_DIP_POS, FORK_DIP_ROT = (-6.0, 3.5, 1.0), (-10.0, 0.0, 35.0)
VESSEL_TILT = (-20.0, 0.0, 0.0)
# At rest the spoon leans up out of the bowl, above the near rim, instead of lying behind it.
REST_POS, REST_ROT = (-3.0, 0.0, 2.5), (-20.0, 0.0, 32.0)

# bite count, duration and palette by food. "shape" picks vessel and content.
FOODS = {
    "farm_and_charm:potato_soup": dict(shape="soup", seconds=6.0, bites=3, utensil="spoon", vessel=0x7A5230, rim=0x94683F, content=0xE3CFA0, bits=[0xC9A869, 0xF0E2BE, 0x7E9A4E], sound="soup"),
    "crabbersdelight:clam_chowder": dict(shape="soup", seconds=6.0, bites=3, utensil="spoon", vessel=0x7A5230, rim=0x94683F, content=0xEFE7D4, bits=[0xD8B48A, 0xC48B5A, 0xA8BC6E], sound="soup"),
    "candlelight:harvest_plate": dict(shape="plate", seconds=6.5, bites=4, utensil="fork", vessel=0xD9D3C6, rim=0xEFEBDF, content=0xB5763F, bits=[0xD29A48, 0x7E9A4E, 0xB5453A, 0xE9C46A], sound="eating"),
    "vintagedelight:pad_thai": dict(shape="noodles", seconds=6.0, bites=3, utensil="chopsticks", vessel=0xC9BFA9, rim=0xE4DCC8, content=0xD9A650, bits=[0xE6BE6E, 0xC47A3A, 0x6E9A4A], sound="eating"),
    "candlelight:salad": dict(shape="plate", seconds=5.0, bites=3, utensil="fork", vessel=0xCDC6B5, rim=0xE8E3D6, content=0x5E9440, bits=[0x7FB255, 0xC8453A, 0xE7D27A], sound="eating"),
    "minecraft:bread": dict(shape="hand", seconds=4.0, bites=3, utensil=None, content=0xC08A3E, bits=[0xD29D52, 0xB57F36, 0xC89148], sound="eating"),
}


class Painter:
    """Fills a texture with noisy color cells and hands out their UVs."""

    def __init__(self, seed):
        self.image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        self.rng = random.Random(seed)
        self.next = 0
        self.cells = {}

    def cell(self, color):
        if color in self.cells:
            return self.cells[color]
        u, v = (self.next % (SIZE // CELL)) * CELL, (self.next // (SIZE // CELL)) * CELL
        self.next += 1
        r, g, b = (color >> 16) & 255, (color >> 8) & 255, color & 255
        for y in range(CELL):
            for x in range(CELL):
                shade = self.rng.choice((0.86, 0.93, 0.97, 1.0, 1.0, 1.05, 1.1))
                self.image.putpixel((u + x, v + y), (min(255, int(r * shade)), min(255, int(g * shade)), min(255, int(b * shade)), 255))
        self.cells[color] = (u, v)
        return u, v


def cube(painter, origin, size, color):
    u, v = painter.cell(color)
    # One texture pixel per model unit, as in a hand painted model.
    w, h, d = (max(1, min(CELL, round(n))) for n in size)
    sizes = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}
    return {"origin": list(origin), "size": list(size), "uv": {face: {"uv": [u, v], "uv_size": list(sizes[face])} for face in FACES}}


def bone(name, parent, pivot, cubes=None, rotation=None):
    out = {"name": name, "pivot": list(pivot)}
    if parent:
        out["parent"] = parent
    if rotation:
        out["rotation"] = list(rotation)
    if cubes:
        out["cubes"] = cubes
    return out


def arm(painter, name, x, rotation):
    # Immersive Eating draws the skin of the player over this cube; only its size and place matter.
    return bone(name, "root", (x, -7, 7), [cube(painter, (x - 2, -19, 5), (4, 12, 4), 0xC8A080)], rotation)


def utensil_bones(painter, kind, morsel):
    wood = 0x8A6238
    metal = 0xB8BCC2
    hand = (-8, -19, 7)
    # A fork or spoon in line with the forearm hides behind the hand; turned 30 degrees it shows at rest, in the bowl and at the mouth.
    bones = [bone("utensil", "rightArm", hand, rotation={"fork": (0, 0, 30), "spoon": (0, 0, 30)}.get(kind))]
    if kind == "spoon":
        # Long handle so the head stays above the rim while it dips into the bowl.
        bones.append(bone("utensil_part", "utensil", hand, [cube(painter, (-8.4, -31, 6.6), (0.8, 13, 0.8), metal), cube(painter, (-9.3, -33, 5.7), (2.6, 2.4, 2.6), metal)]))
    elif kind == "fork":
        bones.append(bone("utensil_part", "utensil", hand, [cube(painter, (-8.4, -31, 6.6), (0.8, 13, 0.8), metal), cube(painter, (-9.2, -33.5, 6.7), (0.6, 2.8, 0.6), metal), cube(painter, (-7.4, -33.5, 6.7), (0.6, 2.8, 0.6), metal)]))
    else:
        bones.append(bone("utensil_part", "utensil", hand, [cube(painter, (-8.9, -29, 6.6), (0.7, 11, 0.7), wood), cube(painter, (-7.4, -29, 6.6), (0.7, 11, 0.7), wood)]))
    bones.append(bone("morsel", "utensil", (-8, -33, 7), [cube(painter, (-9.3, -34.4, 5.7), (2.6, 1.6, 2.6), morsel)]))
    return bones


def geometry(food, painter, path):
    bones = [bone("root", None, (0, -8, 7), rotation=(-7.5, 0, 0)), bone("bone", "root", (0, -7, 6))]
    bones.append(arm(painter, "leftArm", 8, (-90, 6, 0)))
    bones.append(arm(painter, "rightArm", -8, (-90, -6, 0)))
    # Vessel foods tilt toward the camera so the content and the spoon head read in first person.
    tilt = None if food["shape"] == "hand" else VESSEL_TILT
    bones.append(bone("food", "bone", (0, -5, -6), rotation=tilt))
    bones.append(bone("eat", "food", (0, -5, -6)))
    bits = food["bits"]
    rng = random.Random(path)
    if food["shape"] == "hand":
        # Bread loaf in the right hand: one chunk goes per bite.
        hand = (-8, -19, 7)
        bones[-2] = bone("food", "rightArm", hand)
        # One hand food: the left arm rests down out of view, also in the still pose before the animation.
        bones[2] = arm(painter, "leftArm", 8, (0, 6, 0))
        bones[-1] = bone("eat", "food", hand)
        for n in range(food["bites"]):
            y = -26 + n * 3
            bones.append(bone(str(n + 1), "eat", (-8, y + 1, 7), [cube(painter, (-11, y, 4), (6, 3, 7), bits[n % len(bits)]), cube(painter, (-10, y + 0.5, 11), (4, 2, 1), food["content"])]))
        return bones
    if food["shape"] == "soup" or food["shape"] == "noodles":
        bones.append(bone("vessel", "food", (0, -5, -6), [
            cube(painter, (-6, -7, -12), (12, 1, 12), food["vessel"]),
            cube(painter, (-7, -6, -13), (14, 3, 1), food["vessel"]), cube(painter, (-7, -6, 0), (14, 3, 1), food["vessel"]),
            cube(painter, (-7, -6, -12), (1, 3, 12), food["vessel"]), cube(painter, (6, -6, -12), (1, 3, 12), food["vessel"]),
            cube(painter, (-7.5, -3, -13.5), (15, 1, 1), food["rim"]), cube(painter, (-7.5, -3, 0.5), (15, 1, 1), food["rim"])]))
        bones.append(bone("level", "eat", (0, -6, -6), [cube(painter, (-6, -6, -12), (12, 3, 12), food["content"])]))
    else:
        bones.append(bone("vessel", "food", (0, -5, -6), [
            cube(painter, (-8, -6.5, -14), (16, 1, 16), food["vessel"]),
            cube(painter, (-9, -6, -15), (18, 1, 1), food["rim"]), cube(painter, (-9, -6, 2), (18, 1, 1), food["rim"]),
            cube(painter, (-9, -6, -14), (1, 1, 16), food["rim"]), cube(painter, (8, -6, -14), (1, 1, 16), food["rim"])]))
    for n in range(food["bites"]):
        cubes = []
        cx, cz = -3.5 + rng.uniform(-1, 1) + (n % 2) * 7, -9 + (n // 2) * 6 + rng.uniform(-1, 1)
        for k in range(7):
            w, h, d = rng.choice((1, 2, 2, 3)), rng.choice((1, 1, 2)), rng.choice((1, 2, 2, 3))
            cubes.append(cube(painter, (round(cx + rng.uniform(-3, 2), 2), round(-3.6 + rng.uniform(-0.6, 0.4), 2) if food["shape"] != "plate" else round(-5.6 + rng.uniform(0, 1.0), 2), round(cz + rng.uniform(-3, 2), 2)), (w, h, d), bits[(n + k) % len(bits)]))
        bones.append(bone(str(n + 1), "eat", (round(cx, 2), -5, round(cz, 2)), cubes))
    bones.extend(utensil_bones(painter, food["utensil"], bits[0]))
    return bones


def frames(points):
    return {f"{t:.2f}": {"vector": list(v)} for t, v in sorted(points)}


def animation(food):
    total = food["seconds"]
    bites = food["bites"]
    start, end = food.get("start", 0.5), total - 0.7
    step = (end - start) / bites
    arm_pos, arm_rot, shot_scale, sounds, camera = [(0, (0, 0, 0))], [(0, (0, 0, 0))], [(0, (0, 0, 0))], {}, [(0, (0, 0, 0))]
    out = {}
    hand = food["shape"] == "hand"
    for n in range(bites):
        t = start + n * step
        # The spoonful leaves the stew at the end of the scoop; a fork picks its bite at the dip.
        spoon = food.get("utensil") == "spoon" and not hand
        dip, scoop, lift, bite, back = t + step * (0.2 if spoon else 0.22), t + step * 0.34, t + step * 0.5, t + step * 0.62, t + step * 0.95
        take = scoop if spoon else dip
        if hand:
            arm_pos += [(t, (-6, -3, 2)), (lift, (-3, 0, 3)), (bite, (-2, 2, 4)), (back, (-6, -3, 2))]
            arm_rot += [(t, (-8, 0, 24)), (lift, (-16, 0, 32)), (bite, (-20, 0, 36)), (back, (-8, 0, 24))]
        else:
            dips = [(DIP_POS, DIP_ROT), (SCOOP_POS, SCOOP_ROT)] if spoon else [(FORK_DIP_POS, FORK_DIP_ROT)]
            arm_pos += [(t, REST_POS)] + [(k, d[0]) for k, d in zip((dip, scoop), dips)] + [(lift, MOUTH_POS), (bite, MOUTH_POS), (back, REST_POS)]
            arm_rot += [(t, REST_ROT)] + [(k, d[1]) for k, d in zip((dip, scoop), dips)] + [(lift, MOUTH_ROT), (bite, MOUTH_ROT), (back, REST_ROT)]
            shot_scale += [(take - 0.01, (0, 0, 0)), (take, (1, 1, 1)), (bite, (1, 1, 1)), (bite + 0.01, (0, 0, 0))]
        camera += [(bite, (0, 0, 0)), (bite + 0.12, (1.2, 0, 0)), (bite + 0.3, (0, 0, 0))]
        sounds[f"{bite:.2f}"] = {"effect": food["sound"]}
        out[str(n + 1)] = {"scale": frames([(0, (1, 1, 1)), ((take if not hand else bite) - 0.01, (1, 1, 1)), (take if not hand else bite, (0, 0, 0))])}
    arm_pos += [(total - 0.5, (0, 0, 0))]
    arm_rot += [(total - 0.5, (0, 0, 0))]
    out["rightArm"] = {"position": frames(arm_pos), "rotation": frames(arm_rot)}
    out["bone"] = {"position": frames([(0, (0, -12, 0)), (0.35, (0, 0, 0)), (total - 0.5, (0, 0, 0)), (total - 0.1, (0, -12, 0))]),
                   "rotation": frames([(0, (-8, 0, 0)), (0.35, (0, 0, 0)), (total - 0.5, (0, 0, 0)), (total - 0.1, (-8, 0, 0))])}
    if hand:
        # Hand foods are held by the right hand only; the left arm would hang in front of the food.
        out["leftArm"] = {"position": frames([(0, (0, -12, 0)), (total, (0, -12, 0))]), "scale": frames([(0, (0, 0, 0)), (total, (0, 0, 0))])}
    else:
        out["leftArm"] = {"position": frames([(0, (0, -12, 0)), (0.35, (0, 0, 0)), (total - 0.5, (0, 0, 0)), (total - 0.1, (0, -12, 0))])}
    out["camera"] = {"rotation": frames(camera)}
    if not hand:
        out["morsel"] = {"scale": frames(shot_scale)}
        # The utensil resting in the dish only shows in the still pose; the hand takes it from the first frame.
        out["utensil_rest"] = {"scale": frames([(0, (0, 0, 0)), (total, (0, 0, 0))])}
        if food["shape"] in ("soup", "noodles"):
            out["level"] = {"scale": frames([(0, (1, 1, 1)), (end - 0.1, (1, 1, 1)), (end, (1, 0.25, 1))])}
    return {"format_version": "1.8.0", "animations": {"eat": {
        "loop": "hold_on_last_frame", "animation_length": total, "bones": out,
        "sound_effects": sounds, "timeline": {f"{total - 0.25:.2f}": "finished;"}}}}


def main():
    for sub in ("definitions", "geo", "animations", "textures/item"):
        os.makedirs(f"{OUT}/{sub}", exist_ok=True)
    for item, food in FOODS.items():
        path = item.split(":", 1)[1]
        painter = Painter(item)
        if food["shape"] == "hand":
            bones = geometry(food, painter, path)
        else:
            import sys
            sys.path.insert(0, "sunlit_tools")
            import gen_ie_dishes
            bones = gen_ie_dishes.dish_bones(item, "plate" if food["shape"] == "plate" else "bowl", None, painter, food)
        bones.insert(0, bone("camera", None, (0, 0, 0)))
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": f"geometry.{path}", "texture_width": SIZE, "texture_height": SIZE,
                            "visible_bounds_width": 3, "visible_bounds_height": 3, "visible_bounds_offset": [0, 0.5, 0]},
            "bones": bones}]}
        with open(f"{OUT}/geo/{path}.geo.json", "w", encoding="utf-8") as f:
            json.dump(geo, f, indent=1)
        with open(f"{OUT}/animations/{path}.animation.json", "w", encoding="utf-8") as f:
            json.dump(animation(food), f, indent=1)
        painter.image.save(f"{OUT}/textures/item/{path}.png", optimize=True)
        definition = {"item": item, "invisible": ["utensil"] if food["utensil"] else [], "sounds": {"eating": "food:eat", "soup": "food:soup"}}
        with open(f"{OUT}/definitions/{path}.json", "w", encoding="utf-8") as f:
            json.dump(definition, f, indent=1)
    print(f"{len(FOODS)} foods written to {OUT}")


if __name__ == "__main__":
    main()
