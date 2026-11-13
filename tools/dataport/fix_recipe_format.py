#!/usr/bin/env python3
"""Convert kubejs/data recipe JSON files from the 1.20.1 layout to the 1.21.1 layout.

Idempotent: running it twice changes nothing the second time.

Modes:
  python3 -I tools/dataport/fix_recipe_format.py           apply fixes, write status file
  python3 -I tools/dataport/fix_recipe_format.py --check   report remaining problems only

Field rules come from real 1.21.1 recipes shipped in the mod jars under mods/
(see the TYPE_NOTES table). Types without any example in the jars are left untouched.
Sewing recipes (sewingkit:sewing) are owned by another operator and are skipped.
"""
import glob
import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DATA = os.path.join(ROOT, "kubejs", "data")
MODS = os.path.join(ROOT, "mods")
WORK = os.path.join(ROOT, "tools", "dataport", "work")
ERRORS = os.path.join(WORK, "recipe_errors.tsv")
STATUS = os.path.join(WORK, "recipe_status.tsv")

SEWING = "sewingkit:sewing"

# Types whose files are rewritten by this script, with the evidence used.
TYPE_NOTES = {
    "farmersdelight:cooking": "FarmersDelight jar: result ItemStack {id,count}; container is ItemStack",
    "farm_and_charm:stove": "letsdo-bakery jar: result {id,count}, requiresLearning",
    "farm_and_charm:roaster": "letsdo-brewery jar: container ItemStack {id}, result {id,count}, requiresLearning",
    "farm_and_charm:drying": "letsdo-brewery jar: result {id,count}",
    "create:mixing": "FarmersDelight/create jars: results list of {id,count}; fluid ingredient {type neoforge:single,amount,fluid}",
    "create:compacting": "create jar: fluid ingredient {type neoforge:single,amount,fluid}",
    "create:filling": "FarmersDelight jar: fluid ingredient {type neoforge:single,amount,fluid}",
    "create:sequenced_assembly": "create jar: ingredient, results {id,chance}, transitionalItem ItemStack",
    "create:mechanical_crafting": "create jar: accept_mirrored, result {id,count}",
    "minecraft:crafting_shaped": "FarmersDelight jar: result {id,count}",
    "minecraft:crafting_shapeless": "FarmersDelight jar: result {id,count}",
    "minecraft:smelting": "FarmersDelight jar: result {id,count}",
    "minecraft:blasting": "FarmersDelight jar: result {id,count}",
    "minecraft:smoking": "FarmersDelight jar: result {id,count}",
    "minecraft:campfire_cooking": "FarmersDelight jar: result {id,count}",
    "minecraft:stonecutting": "BuildersDelight jar: result {id,count}",
    "farmersdelight:cutting": "FarmersDelight jar: result list of {item:{id,count}}, tool list",
    "functionalstorage:custom_compacting": "functionalstorage jar: higher_input/lower_input {id,count}",
    "herbalbrews:kettle_brewing": "letsdo-herbalbrews jar: fluid_amount, heat_amount, result {id}, top-level effect/effect_duration",
    "vintagedelight:fermenting": "vintagedelight jar: output {id,count}, container ingredient {item}",
    "meadow:cheese": "letsdo-meadow jar: result {id,count}, bucket ingredient {item}",
    "refurbished_furniture:workbench_constructing": "cfm_wap jar: materials [{count, ingredient}], result {id,count}",
    "refurbished_furniture:cutting_board_combining": "refurbished_furniture jar: result {id,count}",
    "refurbished_furniture:oven_baking": "refurbished_furniture jar: result {id,count}",
    "refurbished_furniture:frying_pan_cooking": "refurbished_furniture jar: result {id}",
    "refurbished_furniture:toaster_heating": "refurbished_furniture jar: result {id}",
    "vinery:apple_fermenting": "letsdo-vinery jar: output {id,count}",
    "vinery:apple_mashing": "letsdo-vinery jar: output {id,count}",
    "vinery:wine_fermentation": "letsdo-vinery jar: result {id,count}",
}

# Types with no example anywhere in the jars: left untouched.
NO_EVIDENCE = {"sawmill:woodcutting", "create_mechanical_extruder:extruding"}

CREATE_TYPES = {"create:mixing", "create:compacting", "create:filling", "create:sequenced_assembly"}
CONTAINER_STACK = {"farmersdelight:cooking", "farm_and_charm:roaster"}
STACK_KEYS = ("result", "output", "higher_input", "lower_input")


def stack(x, count=None):
    """ItemStack in 1.21 form: {"id": ..., "count": ...}."""
    if isinstance(x, str):
        out = {"id": x}
    elif isinstance(x, dict) and "item" in x and "id" not in x:
        out = {"id": x["item"], **{k: v for k, v in x.items() if k != "item"}}
    else:
        out = x
    if count is not None and isinstance(out, dict) and "count" not in out:
        out["count"] = count
    return out


def fluid_ingredient(x):
    """Fluid ingredient for create processing: {type neoforge:single, amount, fluid}."""
    if isinstance(x, dict) and "fluid" in x and "type" not in x:
        x = {"type": "neoforge:single", **x}
    if isinstance(x, dict) and x.get("nbt") == {}:
        del x["nbt"]
    return x


def ingredient_tree(x):
    if isinstance(x, list):
        return [ingredient_tree(e) for e in x]
    return fluid_ingredient(x)


def create_processing(d):
    """Fix one create processing recipe in place; returns True when changed."""
    before = json.dumps(d, sort_keys=True)
    for k in ("ingredients", "ingredient"):
        if k in d:
            d[k] = ingredient_tree(d[k])
    if isinstance(d.get("results"), list):
        fixed = []
        for e in d["results"]:
            if isinstance(e, dict) and "fluid" in e and "id" not in e:
                e = {"id": e["fluid"], **{k: v for k, v in e.items() if k != "fluid"}}
            elif isinstance(e, dict) and "item" in e and "id" not in e:
                e = {"id": e["item"], **{k: v for k, v in e.items() if k != "item"}}
            fixed.append(e)
        d["results"] = fixed
    if isinstance(d.get("transitionalItem"), dict):
        d["transitionalItem"] = stack(d["transitionalItem"])
    if isinstance(d.get("sequence"), list):
        for step in d["sequence"]:
            if isinstance(step, dict):
                create_processing(step)
    return json.dumps(d, sort_keys=True) != before


def fix_farmersdelight_cutting(d):
    results = d.get("result")
    if isinstance(results, list):
        out = []
        for e in results:
            if isinstance(e, dict) and isinstance(e.get("item"), str):
                count = e.pop("count", None)
                e["item"] = stack(e["item"], count)
            out.append(e)
        d["result"] = out


def fix_herbalbrews(d):
    fluid = d.pop("fluid", None)
    if isinstance(fluid, list) and fluid:
        d["fluid_amount"] = fluid[0].get("amount")
    elif isinstance(fluid, dict):
        d["fluid_amount"] = fluid.get("amount")
    heat = d.pop("heat_needed", None)
    if isinstance(heat, list) and heat:
        d["heat_amount"] = heat[0].get("amount")
    elif isinstance(heat, dict):
        d["heat_amount"] = heat.get("amount")
    res = d.get("result")
    if isinstance(res, dict):
        extra = {k: v for k, v in res.items() if k not in ("id", "item", "count")}
        for k in list(extra):
            res.pop(k)
        if "item" in res:
            res["id"] = res.pop("item")
        for k, v in extra.items():
            key = {"effectduration": "effect_duration"}.get(k, k)
            d.setdefault(key, v)


def conv_condition(c):
    """1.20 forge:* condition types become neoforge:* in 1.21, recursively."""
    if not isinstance(c, dict):
        return c
    out = dict(c)
    if isinstance(out.get("type"), str) and out["type"].startswith("forge:"):
        out["type"] = "neoforge:" + out["type"][len("forge:"):]
    if isinstance(out.get("values"), list):
        out["values"] = [conv_condition(v) for v in out["values"]]
    return out


def unwrap_conditional(d):
    """forge:conditional with one entry -> 1.21 root recipe with neoforge:conditions. None if not possible."""
    entries = d.get("recipes", [])
    if len(entries) != 1 or not isinstance(entries[0], dict) or "recipe" not in entries[0]:
        return None
    e = entries[0]
    conds = e.get("neoforge:conditions", e.get("conditions", []))
    out = {"neoforge:conditions": [conv_condition(c) for c in conds]}
    out.update(e["recipe"])
    return out


def conditional_pass(items, status, counts):
    """Handle forge:conditional files that are not listed in the error file."""
    seen = {row[0] for row in status}
    for path in glob.glob(os.path.join(DATA, "*", "recipe", "**", "*.json"), recursive=True):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict):
            continue
        rel = os.path.relpath(path, os.path.join(DATA))
        ns, rest = rel.split(os.sep, 2)[0], rel.split(os.sep, 2)[2]
        rid = ns + ":" + rest[:-len(".json")].replace(os.sep, "/")
        if rid in seen:
            continue
        if d.get("type") == "forge:conditional":
            out = unwrap_conditional(d)
        elif "neoforge:conditions" in d and d.get("type") in TYPE_NOTES:
            out = d
        else:
            continue
        if out is None:
            status.append((rid, "left", "forge:conditional with several entries"))
            counts["left"] += 1
            continue
        fix_recipe(out)
        result = out.get("result")
        result_id = result.get("id") if isinstance(result, dict) else result
        absent_note = ""
        if isinstance(result_id, str) and not result_id.startswith("minecraft:") and result_id not in items:
            absent_note = "result item not in any jar; kept behind its condition: " + result_id
        left = problems(out)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write("\n")
        notes = sorted(set(left)) + ([absent_note] if absent_note else [])
        if notes:
            status.append((rid, "left", "; ".join(notes)))
            counts["left"] += 1
        else:
            status.append((rid, "fixed", "unwrapped forge:conditional to 1.21 neoforge:conditions"))
            counts["fixed"] += 1


def fix_stove_like(d):
    if "result" not in d and "item" in d:
        d["result"] = {"id": d.pop("item"), "count": d.pop("count", 1)}
    if isinstance(d.get("result"), str):
        d["result"] = stack(d["result"])
    if "requiresLearning" not in d:
        d["requiresLearning"] = False


def fix_recipe(d):
    """Apply the 1.21.1 layout to a parsed recipe. Returns True when changed."""
    before = json.dumps(d, sort_keys=True)
    t = d.get("type")
    if t in CREATE_TYPES:
        create_processing(d)
    elif t == "create:mechanical_crafting":
        if "acceptMirrored" in d:
            d["accept_mirrored"] = d.pop("acceptMirrored")
        create_processing_result = d.get("result")
        if isinstance(create_processing_result, str):
            d["result"] = stack(create_processing_result)
        elif isinstance(create_processing_result, dict):
            d["result"] = stack(create_processing_result)
    elif t == "farmersdelight:cutting":
        fix_farmersdelight_cutting(d)
    elif t == "herbalbrews:kettle_brewing":
        fix_herbalbrews(d)
    elif t in ("farm_and_charm:stove", "farm_and_charm:roaster"):
        fix_stove_like(d)
        if isinstance(d.get("container"), dict):
            d["container"] = stack(d["container"])
    elif t == "farmersdelight:cooking":
        if isinstance(d.get("container"), dict):
            d["container"] = stack(d["container"])
        if isinstance(d.get("result"), (dict, str)):
            d["result"] = stack(d["result"])
    elif t == "functionalstorage:custom_compacting":
        for k in ("higher_input", "lower_input"):
            if isinstance(d.get(k), dict):
                d[k] = stack(d[k])
    elif t == "refurbished_furniture:workbench_constructing":
        mats = []
        for m in d.get("materials", []):
            if isinstance(m, dict) and "ingredient" not in m:
                count = m.pop("count", 1)
                mats.append({"count": count, "ingredient": m})
            else:
                mats.append(m)
        if "materials" in d:
            d["materials"] = mats
        if isinstance(d.get("result"), str):
            d["result"] = stack(d["result"], d.pop("count", None))
    elif t == "refurbished_furniture:cutting_board_combining":
        if isinstance(d.get("result"), str):
            d["result"] = stack(d["result"], d.pop("count", None))
    elif t in ("refurbished_furniture:oven_baking", "refurbished_furniture:frying_pan_cooking",
               "refurbished_furniture:toaster_heating", "minecraft:smelting", "minecraft:blasting",
               "minecraft:smoking", "minecraft:campfire_cooking", "minecraft:stonecutting",
               "minecraft:crafting_shaped", "minecraft:crafting_shapeless", "meadow:cheese",
               "vintagedelight:fermenting", "vinery:apple_fermenting", "vinery:apple_mashing",
               "vinery:wine_fermentation"):
        if isinstance(d.get("result"), str) or (t == "minecraft:stonecutting" and "count" in d):
            d["result"] = stack(d["result"], d.pop("count", None))
        for k in ("result", "output"):
            if k in d and isinstance(d[k], dict):
                d[k] = stack(d[k])
    if t == "meadow:cheese" and isinstance(d.get("result"), str):
        d["result"] = stack(d["result"], 1)
    if t == "vintagedelight:fermenting" and isinstance(d.get("output"), dict):
        d["output"] = stack(d["output"])
    if t in ("vinery:apple_fermenting", "vinery:apple_mashing") and isinstance(d.get("output"), dict):
        d["output"] = stack(d["output"])
    if t == "minecraft:crafting_shaped" or t == "minecraft:crafting_shapeless":
        if isinstance(d.get("result"), dict):
            d["result"] = stack(d["result"])
    return json.dumps(d, sort_keys=True) != before


def problems(d):
    """Remaining 1.21.1 layout problems for a parsed recipe."""
    out = []
    t = d.get("type")
    keys = list(STACK_KEYS)
    if t in CONTAINER_STACK:
        keys.append("container")
    for k in keys:
        v = d.get(k)
        if isinstance(v, str):
            out.append(f"{k} is a bare string")
        elif isinstance(v, dict):
            if "item" in v or "fluid" in v or "id" not in v:
                out.append(f"{k} is not an ItemStack with id")
    if t in CREATE_TYPES or t == "farmersdelight:cutting":
        for e in d.get("results", []) if t in CREATE_TYPES else []:
            if isinstance(e, dict) and ("item" in e or "fluid" in e):
                out.append("result entry uses item/fluid")
            if isinstance(e, str):
                out.append("result entry is a bare string")
    if t in CREATE_TYPES:
        def walk(x):
            if isinstance(x, list):
                for e in x:
                    walk(e)
            elif isinstance(x, dict) and "fluid" in x and "type" not in x:
                out.append("fluid ingredient without type")
        walk(d.get("ingredients", []))
        walk(d.get("ingredient", []))
    if t == "refurbished_furniture:workbench_constructing":
        for m in d.get("materials", []):
            if isinstance(m, dict) and "ingredient" not in m:
                out.append("material without ingredient")
    if t == "farmersdelight:cutting":
        for e in d.get("result", []) if isinstance(d.get("result"), list) else []:
            if isinstance(e, dict) and not isinstance(e.get("item"), dict):
                out.append("cutting result item is not an ItemStack")
    return out


def load_error_map():
    errs = {}
    with open(ERRORS, encoding="utf-8") as f:
        for line in f:
            if "\t" in line:
                rid, err = line.rstrip("\n").split("\t", 1)
                errs[rid] = err
    return errs


def rid_to_path(rid):
    ns, path = rid.split(":", 1)
    return os.path.join(DATA, ns, "recipe", path + ".json")


def jar_item_ids():
    """Item ids that have an item model in some installed jar (proxy for 'item exists')."""
    found = set()
    pat = re.compile(r"^assets/([^/]+)/models/item/(.+)\.json$")
    for jar in glob.glob(os.path.join(MODS, "*.jar")):
        try:
            with zipfile.ZipFile(jar) as z:
                for n in z.namelist():
                    m = pat.match(n)
                    if m:
                        found.add(f"{m.group(1)}:{m.group(2)}")
        except zipfile.BadZipFile:
            continue
    return found


def main():
    check_only = "--check" in sys.argv
    errs = load_error_map()
    status = []
    counts = {"fixed": 0, "removed": 0, "left": 0}
    nonkjs = [rid for rid in errs if ":kjs/" not in rid]
    prev = {}
    if os.path.exists(STATUS):
        with open(STATUS, encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:
                parts = line.split("\t", 2)
                if len(parts) == 3:
                    prev[parts[0]] = (parts[1], parts[2])

    if not check_only:
        items = jar_item_ids()
    else:
        items = set()

    for rid in nonkjs:
        path = rid_to_path(rid)
        err = errs[rid]
        if not os.path.exists(path):
            miss = re.findall(r"Unknown registry key in minecraft:item: '([^']+)'", err)
            miss_absent = [u for u in miss if u not in items and not u.startswith("minecraft:")]
            if prev.get(rid, ("", ""))[0] == "removed" or (miss and len(miss_absent) == len(miss)):
                note = prev[rid][1] if prev.get(rid, ("", ""))[0] == "removed" else "item absent from every installed mod: " + ",".join(miss_absent)
                status.append((rid, "removed", note))
                counts["removed"] += 1
            else:
                status.append((rid, "left", "no file at expected path (stale entry)"))
                counts["left"] += 1
            continue
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        t = d.get("type")
        if t == SEWING:
            status.append((rid, "left", "sewing recipe, out of scope"))
            counts["left"] += 1
            continue
        if t == "forge:conditional":
            continue
        if check_only:
            if t in TYPE_NOTES and problems(d):
                print("PROBLEM", rid, problems(d)[:2])
            continue
        unknown = re.findall(r"Unknown registry key in minecraft:item: '([^']+)'", err)
        absent = [u for u in unknown if u not in items and not u.startswith("minecraft:")]
        if unknown and len(absent) == len(unknown):
            os.remove(path)
            status.append((rid, "removed", "item absent from every installed mod: " + ",".join(absent)))
            counts["removed"] += 1
            continue
        if t in NO_EVIDENCE or t not in TYPE_NOTES:
            status.append((rid, "left", f"no 1.21.1 example for type {t}"))
            counts["left"] += 1
            continue
        changed = fix_recipe(d)
        left = problems(d)
        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
                f.write("\n")
        if left:
            status.append((rid, "left", "; ".join(sorted(set(left)))))
            counts["left"] += 1
        else:
            status.append((rid, "fixed", "changed" if changed else "already in 1.21.1 layout"))
            counts["fixed"] += 1

    if check_only:
        bad = 0
        for path in glob.glob(os.path.join(DATA, "*", "recipe", "**", "*.json"), recursive=True):
            with open(path, encoding="utf-8") as f:
                try:
                    d = json.load(f)
                except ValueError as e:
                    print("PARSE ERROR", path, e)
                    bad += 1
                    continue
            if isinstance(d, dict) and d.get("type") == "forge:conditional":
                bad += 1
                print("PROBLEM", os.path.relpath(path, ROOT), "still forge:conditional")
            elif isinstance(d, dict) and d.get("type") in TYPE_NOTES and problems(d):
                bad += 1
                print("PROBLEM", os.path.relpath(path, ROOT), problems(d)[:2])
        print(f"remaining problems: {bad}")
        return 1 if bad else 0

    conditional_pass(items, status, counts)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("id\tstatus\tnote\n")
        for rid, st, note in status:
            f.write(f"{rid}\t{st}\t{note}\n")
    print(f"fixed={counts['fixed']} removed={counts['removed']} left={counts['left']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
