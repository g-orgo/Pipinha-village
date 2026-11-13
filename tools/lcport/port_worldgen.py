"""Move 1.20.1 Forge biome modifiers to the NeoForge 1.21.1 layout.

Forge read data/<ns>/forge/biome_modifier; NeoForge 1.21.1 only reads
data/<ns>/neoforge/biome_modifier, so every file left under forge/ is silently ignored.
This runs after tools/dataport/port_data.py (which rebuilds kubejs/data and the packs
from the 1.20.1 instance) and is idempotent.

Per file:
  - "forge:conditions": [forge:false] or type forge:none -> {"type": "neoforge:none"}
    (disables the mod's own modifier with the same id);
  - type forge:* -> neoforge:*; biome tags #forge:* -> #c:*;
  - RENAMES: the mod renamed the modifier or its features in 1.21.1 (checked in the jars);
  - namespaces of mods that left the pack are dropped.
Also rewrites #forge:* biome tags in the Lost Cities worldstyles.
"""

import glob
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA_ROOTS = [os.path.join(ROOT, "kubejs", "data")] + sorted(
    glob.glob(os.path.join(ROOT, "moonlight-global-datapacks", "*", "data")))

# 1.20.1 modifier id -> 1.21.1 modifier ids (same content applied to each).
RENAMES = {
    "oreganized:overworld_ores": ["oreganized:add_lead_ores", "oreganized:add_silver_ores"],
}
# 1.20.1 placed feature -> 1.21.1 placed feature.
FEATURES = {"embellishcraft:%s_ore" % s: "embellishcraft:ore_%s" % s
            for s in ("jade", "basalt", "slate", "gneiss", "marble", "larvikite")}
# Mods that are no longer installed: their overrides have nothing to act on.
REMOVED_NS = {"species", "bloomingnature"}


def convert(d):
    conds = d.get("forge:conditions")
    if d.get("type") == "forge:none" or (conds and any(c.get("type") == "forge:false" for c in conds)):
        return {"type": "neoforge:none"}
    raw = json.dumps(d)
    raw = raw.replace('"forge:', '"neoforge:').replace('"#forge:', '"#c:')
    d = json.loads(raw)
    feats = d.get("features")
    if isinstance(feats, list):
        d["features"] = [FEATURES.get(f, f) for f in feats]
    elif isinstance(feats, str):
        d["features"] = FEATURES.get(feats, feats)
    return d


def port_modifiers(stats):
    for data in DATA_ROOTS:
        for src_dir in sorted(glob.glob(os.path.join(data, "*", "forge", "biome_modifier"))):
            file_ns = src_dir.split(os.sep)[-3]
            for path in sorted(glob.glob(os.path.join(src_dir, "*.json"))):
                name = os.path.basename(path)[:-5]
                key = "%s:%s" % (file_ns, name)
                if file_ns in REMOVED_NS:
                    stats["dropped (mod removed) " + key] = 1
                    continue
                with open(path, encoding="utf-8") as fh:
                    new = convert(json.load(fh))
                for target in RENAMES.get(key, [key]):
                    ns, tname = target.split(":")
                    out = os.path.join(data, ns, "neoforge", "biome_modifier", tname + ".json")
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "w", encoding="utf-8") as fh:
                        fh.write(json.dumps(new, indent=2) + "\n")
                    stats["%s -> %s (%s)" % (key, target, new["type"])] = 1
            shutil.rmtree(src_dir)
            if not os.listdir(os.path.dirname(src_dir)):
                os.rmdir(os.path.dirname(src_dir))


def port_worldstyles(stats):
    for path in glob.glob(os.path.join(ROOT, "moonlight-global-datapacks", "*", "data", "*",
                                       "lostcities", "worldstyles", "*.json")):
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        if '"#forge:' in raw:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(raw.replace('"#forge:', '"#c:'))
            stats["worldstyle tags forge->c " + os.path.relpath(path, ROOT)] = 1


def main():
    stats = {}
    port_modifiers(stats)
    port_worldstyles(stats)
    left = glob.glob(os.path.join(ROOT, "kubejs", "data", "*", "forge", "biome_modifier")) + glob.glob(
        os.path.join(ROOT, "moonlight-global-datapacks", "*", "data", "*", "forge", "biome_modifier"))
    for k in sorted(stats):
        print(k)
    print("changes: %d; forge/biome_modifier dirs left: %d" % (len(stats), len(left)))


if __name__ == "__main__":
    main()
