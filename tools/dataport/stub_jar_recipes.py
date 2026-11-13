#!/usr/bin/env python3
"""Neutralize or repair mod jar recipes that fail to parse on NeoForge 1.21.1.

For every id listed in IDS the script:

1. finds the jar that ships ``data/<ns>/recipe/<path>.json`` (zip member scan);
2. reads the failing reasons from ``logs/latest.log`` (unknown registry key,
   codec mismatch) -- the same ground-truth approach as fix_jar_loot.py;
3. decides:
   - *fixed*: the installed mod renamed an id (RENAMES) or the recipe uses a
     pre-1.21 ItemStack/Ingredient shape (``{"item": ...}`` as a result,
     ``{"id": ...}`` as an ingredient). A corrected copy is written to
     ``kubejs/data/<ns>/recipe/<path>.json``;
   - *stub*: the namespace mod is absent, a referenced id is not registered and
     has no known replacement, the recipe only exists at runtime, or the
     installed serializer expects a different result type (kettle/FluidStack).
     The pack stub ``{"neoforge:conditions":[{"type":"neoforge:false"}]}`` is
     written;
   - *skipped*: the fix is not needed because an equivalent, correctly shaped
     recipe is already shipped by a jar (minecraft:red_dye).

Usage (from the instance root): python3 tools/dataport/stub_jar_recipes.py .
"""
import json
import re
import sys
import zipfile
from pathlib import Path

IDS = [
    # youkaishomecoming ships these under the farmersdelight namespace
    "farmersdelight:cooking/white_tea",
    "farmersdelight:cooking/tea_mocha",
    "farmersdelight:cooking/sakura_honey_tea",
    "farmersdelight:cooking/saidi_tea",
    "farmersdelight:cooking/oolong_tea",
    "farmersdelight:cooking/green_water",
    "farmersdelight:cooking/green_tea",
    "farmersdelight:cooking/genmai_tea",
    "farmersdelight:cooking/cornflower_tea",
    "farmersdelight:cooking/black_tea",
    "snuffles:snuffle_fluff_from_frosty_fluff",
    "snuffles:snuffle_fluff_carpet_from_snuffle_fluff",
    "snuffles:snuffle_fluff_carpet_from_frosty_fluff_carpet",
    "snuffles:frosty_fluff_from_snuffle_fluff",
    "snuffles:frosty_fluff_carpet_from_snuffle_fluff_carpet",
    "snuffles:frosty_fluff_carpet_from_frosty_fluff",
    "minecraft:red_dye",
    "dramaticdoors:tall_meadow_pine_barn_door",
    "dramaticdoors:tall_arid_glass_door",
    "dramaticdoors:short_meadow_pine_barn_door",
    "dramaticdoors:short_arid_glass_door",
    "brewinandchewin:pizza_from_dough",
    "createdeco:placard",
    "create_factory_logistics:factory_chemical_gauge",
    "create_factory_logistics:barrel_packager",
    "hearthandharvest:goat_milk_crate",
]

# Ids renamed by an installed mod. Verified by inspecting the jars:
# - FarmersDelight 1.21 renamed dough -> wheat_dough.
# - create_factory_logistics 1.6.1 replaced barrel_packager with jar_packager
#   (its jar recipe is byte-for-byte the barrel_packager recipe, new result).
RENAMES = {
    "farmersdelight:dough": "farmersdelight:wheat_dough",
    "create_factory_logistics:barrel_packager": "create_factory_logistics:jar_packager",
}

# Recipe serializers whose result is a FluidStack in the installed version, so
# the jar's stale ItemStack result cannot be converted without inventing data.
FLUID_RESULT_TYPES = {"youkaishomecoming:kettle"}

# Stale duplicates: the same conversion already ships correctly under another id.
EQUIVALENTS = {
    "minecraft:red_dye": ("farmersrespite", "data/farmersrespite/recipe/red_dye_from_coffee_berries.json"),
}

STUB_TEXT = '{"neoforge:conditions":[{"type":"neoforge:false"}]}'

UNKNOWN_ITEM_RE = re.compile(r"Unknown registry key in minecraft:item: '([^']+)'")
RECIPE_ID_RE = re.compile(
    r"(?:Error parsing recipe |Parsing error loading recipe '|Failed to parse recipe ')"
    r"([a-z0-9_.-]+:[a-z0-9_./-]+)"
)


def index_jars(mods_dir):
    """Return (jars, item_index, namespaces). item_index is (ns, path) of item
    models and blockstates, used as a cheap registry proxy when the log has no
    explicit 'unknown item' line."""
    jars = {}
    item_index = set()
    namespaces = set()
    for jar in sorted(mods_dir.glob("*.jar")):
        with zipfile.ZipFile(jar) as zf:
            names = set(zf.namelist())
        jars[jar] = names
        for name in names:
            parts = name.split("/")
            if name.startswith("assets/") and len(parts) >= 3:
                namespaces.add(parts[1])
                if len(parts) >= 5 and parts[2] == "models" and parts[3] == "item":
                    item_index.add((parts[1], "/".join(parts[4:])[:-5]))
                elif len(parts) >= 4 and parts[2] == "blockstates":
                    item_index.add((parts[1], "/".join(parts[3:])[:-5]))
            elif name.startswith("data/") and len(parts) >= 3:
                namespaces.add(parts[1])
    return jars, item_index, namespaces


def read_log_hints(log_path):
    """Map recipe id -> concatenated log lines that mention it."""
    hints = {}
    if not log_path.is_file():
        return hints
    text = log_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        match = RECIPE_ID_RE.search(line)
        if not match:
            continue
        ident = match.group(1)
        if ident in IDS:
            hints.setdefault(ident, []).append(line)
    return hints


def find_source(jars, ns, path):
    member = f"data/{ns}/recipe/{path}.json"
    for jar, names in jars.items():
        if member in names:
            return jar, member
    return None, None


def load_member(jar, member):
    with zipfile.ZipFile(jar) as zf:
        raw = zf.read(member)
    return json.loads(raw.decode("utf-8-sig"))


def rename_ids(node, renames):
    changed = False
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, str) and value in renames:
                node[key] = renames[value]
                changed = True
            elif rename_ids(value, renames):
                changed = True
    elif isinstance(node, list):
        for value in node:
            if rename_ids(value, renames):
                changed = True
    return changed


def _fix_ingredient(node):
    """Ingredient codec in 1.21 uses 'item'/'tag'; the jar may use 'id'."""
    if isinstance(node, dict) and "id" in node and "item" not in node and "tag" not in node:
        node["item"] = node.pop("id")
        return True
    return False


def fix_recipe(recipe):
    """Convert pre-1.21 result/ingredient shapes in place. Returns True if changed."""
    changed = False
    result = recipe.get("result")
    if isinstance(result, str):
        recipe["result"] = {"id": result, "count": 1}
        changed = True
    elif isinstance(result, dict) and "item" in result and "id" not in result:
        result["id"] = result.pop("item")
        changed = True

    for ingredient in recipe.get("ingredients") or []:
        if _fix_ingredient(ingredient):
            changed = True
    key = recipe.get("key")
    if isinstance(key, dict):
        for ingredient in key.values():
            if isinstance(ingredient, list):
                for sub in ingredient:
                    if _fix_ingredient(sub):
                        changed = True
            elif _fix_ingredient(ingredient):
                changed = True

    if rename_ids(recipe, RENAMES):
        changed = True
    return changed


def referenced_ids(node):
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("item", "id") and isinstance(value, str) and ":" in value:
                found.add(value)
            else:
                found |= referenced_ids(value)
    elif isinstance(node, list):
        for value in node:
            found |= referenced_ids(value)
    return found


def id_present(item_id, item_index):
    ns, _, path = item_id.partition(":")
    if ns == "minecraft":
        return True
    return (ns, path) in item_index


def has_amount_result(recipe):
    result = recipe.get("result")
    return isinstance(result, dict) and "amount" in result


def equivalent_ok(jars, ident):
    """True when the configured equivalent recipe exists and is shaped for 1.21."""
    entry = EQUIVALENTS.get(ident)
    if not entry:
        return False
    ns, member = entry
    for jar, names in jars.items():
        if member in names:
            recipe = load_member(jar, member)
            if isinstance(recipe.get("result"), dict) and "id" in recipe["result"]:
                if recipe.get("type") == "minecraft:crafting_shapeless":
                    return True
    return False


def main(argv):
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    mods_dir = root / "mods"
    if not mods_dir.is_dir():
        print(f"error: {mods_dir} not found", file=sys.stderr)
        return 2

    jars, item_index, namespaces = index_jars(mods_dir)
    hints = read_log_hints(root / "logs" / "latest.log")
    out_root = root / "kubejs" / "data"

    fixed = stubbed = skipped = 0
    for ident in IDS:
        ns, _, path = ident.partition(":")
        lines = hints.get(ident, [])
        joined = "\n".join(lines)
        unknown = set(UNKNOWN_ITEM_RE.findall(joined))
        unresolved = {item for item in unknown if item not in RENAMES}
        fluid_mismatch = "No key amount" in joined

        if ident in EQUIVALENTS and equivalent_ok(jars, ident):
            skipped += 1
            print(f"skipped {ident} - equivalent 1.21 recipe already shipped; no override needed")
            continue

        jar, member = find_source(jars, ns, path)
        if jar is None:
            stubbed += 1
            if ns not in namespaces:
                reason = f"namespace mod '{ns}' is not installed"
            elif unresolved:
                reason = "no jar recipe; runtime-generated recipe references unregistered " + ", ".join(sorted(unresolved))
            else:
                reason = "no data/<ns>/recipe json in any installed jar"
            out = out_root / ns / "recipe" / f"{path}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(STUB_TEXT, encoding="utf-8")
            print(f"stub {ident} - {reason}")
            continue

        recipe = load_member(jar, member)

        if fluid_mismatch or (recipe.get("type") in FLUID_RESULT_TYPES and not has_amount_result(recipe)):
            stubbed += 1
            out = out_root / ns / "recipe" / f"{path}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(STUB_TEXT, encoding="utf-8")
            print(
                f"stub {ident} - installed serializer expects a FluidStack result "
                f"({recipe.get('type')}); jar ships a stale item result"
            )
            continue

        changed = fix_recipe(recipe)
        # The log is authoritative about unregistered ids: a jar may still ship
        # assets (model/blockstate) for an item the mod no longer registers.
        unresolved_after = set(unresolved)
        absent = {
            item for item in referenced_ids(recipe)
            if item not in RENAMES and item not in unknown
            and not id_present(item, item_index)
        }
        unresolved_after |= absent

        if unresolved_after:
            stubbed += 1
            out = out_root / ns / "recipe" / f"{path}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(STUB_TEXT, encoding="utf-8")
            print(
                f"stub {ident} - references unregistered "
                + ", ".join(sorted(unresolved_after))
            )
            continue

        if not changed:
            skipped += 1
            print(f"skipped {ident} - no fix identified")
            continue

        fixed += 1
        out = out_root / ns / "recipe" / f"{path}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(recipe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        renames_used = sorted({src for src, dst in RENAMES.items() if src in joined})
        if renames_used:
            reason = "renamed " + ", ".join(f"{a} -> {RENAMES[a]}" for a in renames_used)
        else:
            reason = "converted stale 1.20 item_stack/ingredient shape to 1.21"
        print(f"fixed {ident} - {reason} (source {jar.name})")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
