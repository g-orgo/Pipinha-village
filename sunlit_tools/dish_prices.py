#!/usr/bin/env python3
"""Prices flat or unpriced dishes from their real recipes (ingredients x1.35, per the rule in
docs/context/conventions.md#preços-e-etapas-de-processamento).

Usage: python3 -I sunlit_tools/dish_prices.py <registry_audit dump.json> <out.json>
Reads recipes and item tags from mods/*.jar and kubejs/data, prints what it could not resolve.
"""
import glob
import json
import re
import sys
import zipfile

POT_SERVINGS = 4
STEP = 1.35
SEASONAL_STEP = 1.46
FLAT_VALUES = (20, 30)
# Stations that make food. Fermenting and aging lines are drinks and artisan goods.
STATIONS = {
    "farmersdelight:cooking", "minecraft:crafting_shaped", "minecraft:crafting_shapeless",
    "kaleidoscope_cookery:pot", "kaleidoscope_cookery:stockpot", "kaleidoscope_cookery:steamer",
    "kaleidoscope_cookery:flex_pot", "kaleidoscope_cookery:flex_stockpot",
    "youkaishomecoming:steaming", "youkaishomecoming:unordered_cooking", "farm_and_charm:pot_cooking",
    "farm_and_charm:crafting_bowl", "farm_and_charm:roaster", "bakery:baking_station",
    "meadow:cooking", "candlelight:stove_cooking", "minecraft:smoking", "minecraft:campfire_cooking",
    "farmersdelight:cutting", "brewinandchewin:fermenting",
}
# Blocks served in portions: the block is priced from its recipe and each serving is a share of it.
SERVINGS = {
    "brewinandchewin:fiery_fondue_pot": ("brewinandchewin:fiery_fondue", 4),
    "culturaldelights:eggplant_parmesan_block": ("culturaldelights:eggplant_parmesan", 4),
    "largemeals:mushroom_pot_pie_block": ("largemeals:mushroom_pot_pie", 4),
    "largemeals:omurice_block": ("largemeals:omurice", 4),
    "largemeals:roasted_mutton_rack_block": ("largemeals:roasted_mutton_rack", 4),
    "miners_delight:stuffed_squid": ("miners_delight:bowl_of_stuffed_squid", 4),
    "miners_delight:glazed_arachnid_limbs": ("miners_delight:plate_of_glazed_arachnid_limbs", 4),
    "oceansdelight:guardian_soup": ("oceansdelight:bowl_of_guardian_soup", 4),
}
# Not food: containers and tools the generated lists filed as dishes.
SKIP = re.compile(r"steamer_|_cup$|water_cup|moss$|pie_crust$")
# Cooked food with no price at all, sold as a whole.
UNPRICED = (
    "vintagedelight:oatmeal", "vintagedelight:nut_milk_bottle",
    "youkaishomecoming:pot_of_borscht", "youkaishomecoming:pot_of_cod_stew",
    "youkaishomecoming:pot_of_han_palace", "youkaishomecoming:pot_of_miso_soup",
    "youkaishomecoming:pot_of_mushroom_soup", "youkaishomecoming:pot_of_potato_soup",
    "youkaishomecoming:pot_of_power_soup", "youkaishomecoming:pot_of_seafood_miso_soup",
    "youkaishomecoming:pot_of_shirayuki", "youkaishomecoming:pot_of_tofu_crab_stew",
)


def load_data():
    recipes, tags = [], {}

    def read_tag(name, raw):
        values = tags.setdefault(name, [])
        data = json.loads(raw)
        if data.get("replace"):
            values.clear()
        for value in data.get("values", []):
            values.append(value if isinstance(value, str) else value.get("id"))

    def read(path, raw):
        match = re.match(r"(?:.*/)?data/([^/]+)/(recipes|tags/items)/(.+)\.json$", path)
        if not match:
            return
        try:
            if match.group(2) == "recipes":
                recipe = json.loads(raw)
                if isinstance(recipe, dict):
                    recipes.append(recipe)
            else:
                read_tag(f"{match.group(1)}:{match.group(3)}", raw)
        except ValueError:
            pass

    for jar in sorted(glob.glob("mods/*.jar")):
        try:
            archive = zipfile.ZipFile(jar)
        except zipfile.BadZipFile:
            continue
        for name in archive.namelist():
            if name.endswith(".json") and "data/" in name:
                read(name, archive.read(name))
    for path in glob.glob("kubejs/data/**/*.json", recursive=True):
        with open(path, "rb") as handle:
            read(path, handle.read())
    return recipes, tags


def tag_members(name, tags, seen=None):
    seen = seen if seen is not None else set()
    if name in seen:
        return []
    seen.add(name)
    out = []
    for value in tags.get(name, []):
        if value and value.startswith("#"):
            out += tag_members(value[1:], tags, seen)
        elif value:
            out.append(value)
    return out


def ingredient_cost(ingredient, trades, tags):
    options = ingredient if isinstance(ingredient, list) else [ingredient]
    best = None
    for option in options:
        if not isinstance(option, dict):
            continue
        if "item" in option:
            ids = [option["item"]]
        elif "tag" in option:
            ids = tag_members(option["tag"], tags)
        else:
            continue
        for item in ids:
            if item in trades:
                value = trades[item]["v"]
                best = value if best is None else min(best, value)
    return best


def recipe_ingredients(recipe):
    if isinstance(recipe.get("ingredients"), list):
        return recipe["ingredients"]
    if isinstance(recipe.get("input"), list):
        return recipe["input"]
    if isinstance(recipe.get("ingredient"), (dict, list)):
        return [recipe["ingredient"]]
    if isinstance(recipe.get("key"), dict) and isinstance(recipe.get("pattern"), list):
        symbols = "".join(recipe["pattern"]).replace(" ", "")
        return [recipe["key"].get(symbol) for symbol in symbols]
    return None


def recipe_result(recipe):
    result = recipe.get("result", recipe.get("output"))
    if isinstance(result, str):
        return result, 1
    if isinstance(result, dict) and result.get("item"):
        return result["item"], result.get("count", 1)
    return None, 1


def main():
    dump = json.load(open(sys.argv[1]))
    trades = dump["trades"]
    canonical = dump.get("canonical") or {}
    removed = open("kubejs/startup_scripts/globalRemovedItems.js").read()
    dishes = {entry["item"]: entry["value"] for entry in dump["lists"]["cooking"]}
    seasonal = set()
    recipes, tags = load_data()
    for season in ("spring", "summer", "autumn", "winter"):
        seasonal |= set(tag_members(f"sereneseasons:{season}_crops", tags))
    seasonal -= set(tag_members("sereneseasons:year_round_crops", tags))

    by_result = {}
    for recipe in recipes:
        if str(recipe.get("type")) not in STATIONS:
            continue
        item, count = recipe_result(recipe)
        if item:
            by_result.setdefault(item, []).append((recipe, count))

    def price(item):
        options = []
        for recipe, count in by_result.get(item, []):
            parts = recipe_ingredients(recipe)
            if not parts:
                continue
            total, usesSeasonal = 0.0, False
            for part in parts:
                cost = ingredient_cost(part, trades, tags) if part is not None else None
                if cost is None:
                    total = None
                    break
                total += cost
                ids = [part["item"]] if isinstance(part, dict) and "item" in part else []
                usesSeasonal = usesSeasonal or any(x in seasonal for x in ids)
            if total:
                options.append(total * (SEASONAL_STEP if usesSeasonal else STEP) / max(count, 1))
        return round(min(options)) if options else None

    out, unresolved = {}, []
    # Blocks first, so a serving falls back to its share of the block.
    for block, (serving, parts) in SERVINGS.items():
        # A price already set on the block wins; with no recipe, the servings set the block.
        value = trades[block]["v"] if block in trades else price(block)
        if value is None and serving in trades:
            value = trades[serving]["v"] * parts
        if value is None:
            unresolved.append(block)
            continue
        if block not in trades:
            out[block] = value
        if dishes.get(serving) in FLAT_VALUES:
            out[serving] = max(1, round(value / parts))
    for item, value in sorted(dishes.items()):
        if value not in FLAT_VALUES or item in out or SKIP.search(item):
            continue
        if f'"{item}"' in removed or item in canonical or item not in by_result:
            continue
        computed = price(item)
        if computed is None:
            unresolved.append(item)
        else:
            out[item] = computed
    for item in UNPRICED:
        if item in trades:
            continue
        # A pot of soup is worth its bowls (serve=1..N in its blockstate), like a whole pie.
        serving = item.replace("pot_of_", "")
        if serving != item and serving in trades:
            computed = trades[serving]["v"] * POT_SERVINGS
        else:
            computed = price(item)
        if computed is None:
            unresolved.append(item)
        else:
            out[item] = computed
    json.dump(out, open(sys.argv[2], "w"), indent=1, sort_keys=True)
    print(f"priced {len(out)}, unresolved {len(unresolved)}")
    print("unresolved:", unresolved)


if __name__ == "__main__":
    main()
