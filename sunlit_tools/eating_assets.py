"""Shared lookups over the active resources, in the order the game resolves them."""
import json
import os
import re
import zipfile

MODELS = "sunlit_tools/eating/models_dump.txt"
FLAT_PARENTS = {"builtin/generated", "minecraft:builtin/generated", "item/generated", "minecraft:item/generated",
                "item/handheld", "minecraft:item/handheld"}


def load_model_dump():
    models = {}
    for line in open(MODELS, encoding="utf-8"):
        item, pack, text = line.rstrip("\n").split("|", 2)
        models[item] = json.loads(text) if text else None
    return models


def has_frames(model):
    if not model:
        return False
    return any("eatinganimation:eating" in o.get("predicate", {}) or "eating" in o.get("predicate", {})
               for o in model.get("overrides", []))


class Sources:
    """kubejs/assets first, then packs from the top of the list, then every mod jar."""

    def __init__(self):
        self.packs = []
        options = open("options.txt", encoding="utf-8").read()
        listed = json.loads(re.search(r"^resourcePacks:(.*)$", options, re.M).group(1))
        for entry in reversed(listed):
            if entry.startswith("file/"):
                path = "resourcepacks/" + entry[5:]
                if os.path.isfile(path):
                    self.packs.append(zipfile.ZipFile(path))
        self.jars = {}
        for name in sorted(os.listdir("mods")):
            if name.endswith(".jar"):
                try:
                    jar = zipfile.ZipFile("mods/" + name)
                except zipfile.BadZipFile:
                    continue
                for entry in jar.namelist():
                    if entry.startswith("assets/"):
                        self.jars.setdefault(entry, jar)

    def read(self, path):
        disk = "kubejs/" + path
        if os.path.isfile(disk):
            with open(disk, "rb") as f:
                return f.read()
        for pack in self.packs:
            try:
                return pack.read(path)
            except KeyError:
                pass
        jar = self.jars.get(path)
        return jar.read(path) if jar else None


def active_sources():
    return Sources()


def split(ref, default_ns="minecraft"):
    return ref.split(":", 1) if ":" in ref else (default_ns, ref)


def is_flat(model, src, item, depth=0):
    """True when the model chain ends in the generated item parent, so frames can be drawn."""
    if not model or depth > 8:
        return False
    if not any(k.startswith("layer") for k in model.get("textures", {})) and depth == 0:
        return False
    parent = model.get("parent")
    if parent is None:
        return False
    if parent in FLAT_PARENTS:
        return "elements" not in model
    ns, path = split(parent)
    if path == "builtin/generated":
        return True
    raw = src.read(f"assets/{ns}/models/{path}.json")
    if raw is None:
        return False
    return "elements" not in model and is_flat(json.loads(raw), src, item, depth + 1)
