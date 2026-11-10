#!/usr/bin/env python3
"""Mercantil discount trades for the society_trading shops.

For each trade listed in GROUPS, adds one discounted copy per Haggle tier
right after the original (trade_id "<original>_mercantil_<tier>"). The
original trade is never changed, so the Auto Trader keeps offering it.
Visibility (see kubejs/startup_scripts/professions/mercantilGlobals.js):
  stage_required mercantil_<group>_<tier>, stage_removed mercantil_<group>_<tier+1>;
  originals with stage_override <s> get stage_override mercantil_<group>_<tier>_<s>.

Idempotent: old copies are dropped and rebuilt. Run from the instance root:
  python3 sunlit_tools/mercantil_discounts.py [--check]
"""
import json
import re
import sys
from pathlib import Path

SHOPS = Path("kubejs/data/society_trading/shops")
# Keep in sync with global.MERCANTIL_DISCOUNTS and MERCANTIL_OVERRIDE_STAGES.
DISCOUNTS = [0.10, 0.15, 0.25]
OVERRIDE_STAGES = {"universal_methods_of_farming"}
# Trades cheaper than this would round to the same price.
MIN_COST = 10
VARIANT_RE = re.compile(r"_mercantil_\d+$")

GROUPS = {
    "farming": {
        "market": [
            "market_flax_seeds", "market_bellpepper_seeds", "market_cranberry_seed",
            "market_lychee_sapling", "market_banana_sapling", "market_peach_sapling",
            "market_dark_cherry_sapling", "market_palm_sapling", "market_apple_tree_sapling",
            "market_rice", "market_cactus", "market_sugar_cane", "market_glass_cactus",
            "minecraft:farmer_hydrating_fertilizer_for_sprocket",
            "minecraft:farmer_low_quality_fertilizer_for_cog",
            "minecraft:farmer_weak_fertilizer_for_cog",
            "minecraft:farmer_pitchfork_for_sun", "farmer_dehydrator_for_sun",
        ],
    },
    "husbandry": {
        "shepherd": [
            "minecraft:shepherd_animal_feed_for_sprocket", "shepherd_feeding_trough_for_bevel",
            "shepherd_milk_pail_for_cog", "shepherd_magic_shears_for_crown",
            "shepherd_mood_scanner", "shepherd_chicken_spawn_egg_for_crown",
            "shepherd_cow_spawn_egg_for_crown", "shepherd_sheep_spawn_egg_for_crown",
            "shepherd_duck_sack_for_crown", "shepherd_rabbit_spawn_egg_for_sun",
            "shepherd_pig_spawn_egg_for_sun", "shepherd_goat_spawn_egg_for_sun",
        ],
    },
    "breeding": {
        "shepherd": ["shepherd_miracle_potion_for_cog"],
    },
    "fishing": {
        "fisher": [
            "fisherman_worm_for_sprocket", "fisherman_fishing_rod_for_crown",
            "fisherman_lava_fishing_rod_rod_for_sun", "fisherman_fish_radar_for_crown",
            "fisherman_fish_pond_for_sun", "fisherman_fish_smoker_for_neptunium_coin",
            "fisherman_light_hook_for_cog_and_sprocket", "fisherman_heavy_hook_for_cog_and_sprocket",
            "fisherman_redstone_hook_for_cog_and_sprocket", "fisherman_gold_hook_for_crown",
            "fisherman_iron_hook_for_cog", "fisherman_diamond_hook_for_crown",
            "fisherman_trap_bobber_for_crown", "fisherman_cork_bobber_for_crown",
            "fisherman_sonar_bobber_for_crown", "fisherman_treasure_bobber_for_sun",
            "fisherman_quality_bobber_for_sun", "fisherman_double_hook_for_crown",
            "fisherman_tackle_box_for_sun", "fisherman_worm_farm_for_crown",
        ],
    },
    "wine": {
        "wandering_winemaker": [
            "wandering_winemaker_red_grape_seeds", "wandering_winemaker_white_grape_seeds",
            "wandering_winemaker_taiga_grape_seeds_red", "wandering_winemaker_taiga_grape_seeds_white",
            "wandering_winemaker_savanna_grape_seeds_red", "wandering_winemaker_savanna_grape_seeds_white",
            "wandering_winemaker_jungle_grape_seeds_red", "wandering_winemaker_jungle_grape_seeds_white",
            "wandering_winemaker_crimson_grape_seeds", "wandering_winemaker_warped_grape_seeds",
        ],
    },
    "kitchen": {
        "market": [
            "minecraft:farmer_sugar_for_sprocket", "minecraft:farmer_glass_bottle_for_sprocket",
            "meadow:farmer_alpine_salt_for_cog", "farmer_cooking_guide_for_sun",
        ],
        "barkeeper": [
            "barkeeper_lunchbag_for_cog", "barkeeper_lunchbox_for_sun",
            "barkeeper_golden_lunchbox_for_sun",
        ],
    },
}
BLOCKING_KEYS = ("stage_required", "stage_removed", "limit")


def variants(trade, group):
    out = []
    cost = trade["numismatics_cost"]
    override = trade.get("stage_override")
    for index, discount in enumerate(DISCOUNTS):
        tier = index + 1
        v = json.loads(json.dumps(trade))
        v["numismatics_cost"] = max(1, int(cost * (1 - discount) + 0.5))
        v["trade_id"] = f"{trade['trade_id']}_mercantil_{tier}"
        v["stage_required"] = f"mercantil_{group}_{tier}"
        if tier < len(DISCOUNTS):
            v["stage_removed"] = f"mercantil_{group}_{tier + 1}"
        if override:
            v["stage_override"] = f"mercantil_{group}_{tier}_{override}"
        v["unlock_description"] = f"jei.society_trading.mercantil_discount_{tier}"
        out.append(v)
    return out


def render(obj, indent, compact):
    if not compact:
        return json.dumps(obj, indent=2, ensure_ascii=False).replace("\n", "\n" + indent)
    inner = indent + "  "
    lines = []
    for key, value in obj.items():
        if isinstance(value, dict):
            body = ", ".join(f"{json.dumps(k)}: {json.dumps(x, ensure_ascii=False)}" for k, x in value.items())
            text = "{ " + body + " }"
        else:
            text = json.dumps(value, ensure_ascii=False)
        lines.append(f"{inner}{json.dumps(key)}: {text}")
    return "{\n" + ",\n".join(lines) + "\n" + indent + "}"


def process(shop, targets):
    path = SHOPS / f"{shop}.json"
    text = path.read_text(encoding="utf-8")
    start = text.index('"trades"')
    pos = text.index("[", start) + 1
    decoder = json.JSONDecoder()
    elements = []
    while True:
        while text[pos] in " \t\r\n,":
            pos += 1
        if text[pos] == "]":
            break
        obj, end = decoder.raw_decode(text, pos)
        elements.append((text[pos:end], obj))
        pos = end
    array_end = pos
    first = text.index("{", text.index("[", start))
    indent = text[text.rindex("\n", 0, first) + 1:first]
    found = set()
    pieces = []
    added = 0
    for raw, obj in elements:
        trade_id = obj.get("trade_id", "")
        if VARIANT_RE.search(trade_id):
            continue
        pieces.append(raw)
        if trade_id in targets:
            group = targets[trade_id]
            found.add(trade_id)
            bad = [k for k in BLOCKING_KEYS if k in obj]
            if bad or not obj.get("numismatics_cost") or obj["numismatics_cost"] < MIN_COST:
                raise SystemExit(f"{shop}/{trade_id}: cannot be discounted ({bad or 'cost'})")
            if obj.get("stage_override") and obj["stage_override"] not in OVERRIDE_STAGES:
                raise SystemExit(f"{shop}/{trade_id}: unknown stage_override {obj['stage_override']}")
            compact = '"offer": {\n' not in raw
            for v in variants(obj, group):
                pieces.append(render(v, indent, compact))
                added += 1
    missing = set(targets) - found
    if missing:
        raise SystemExit(f"{shop}: trade ids not found: {sorted(missing)}")
    head = text[: text.index("[", start) + 1]
    tail_ws = text[text.rindex("}", 0, array_end) + 1:array_end]
    new = head + "\n" + indent + (",\n" + indent).join(pieces) + tail_ws + text[array_end:]
    json.loads(new)
    return path, text, new, added


def main():
    check = "--check" in sys.argv
    per_shop = {}
    for group, shops in GROUPS.items():
        for shop, ids in shops.items():
            for trade_id in ids:
                per_shop.setdefault(shop, {})[trade_id] = group
    changed = []
    for shop, targets in sorted(per_shop.items()):
        path, old, new, added = process(shop, targets)
        print(f"{shop}: {len(targets)} trades, {added} discounted copies")
        if new != old:
            changed.append(path)
            if not check:
                path.write_text(new, encoding="utf-8")
    if check and changed:
        raise SystemExit(f"out of date: {[str(p) for p in changed]}")


if __name__ == "__main__":
    main()
