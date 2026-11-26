#!/usr/bin/env python3
"""Price audit for the Pipinha's Village modpack (read-only for the pack).

Lists existing items that should have a shipping bin sell price and do not,
with a suggested price each. Writes REPORT.md (pt-BR) and missing.json next to
this script. Regex based on purpose: a planning aid, not a parser.

Run with: python3 -I tools/priceaudit/price_audit.py
"""
import collections
import difflib
import importlib.util
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KJS = ROOT / "kubejs"
OLD_KJS = ROOT.parent / "Society: Sunlit Valley" / "kubejs"
CHECK_IDS = ROOT / "tools" / "kjsport" / "check_ids.py"

ID_RE = re.compile(r'["\']([a-z][a-z0-9_.-]*):([a-z0-9_./-]+)["\']')
SIMPLE_ID_RE = re.compile(r"^[a-z0-9_.-]+:[a-z0-9_/.-]+$")
LOOT_NAME_RE = re.compile(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"')
TPL_RE = re.compile(r'`([a-z][a-z0-9_.-]*):([a-z0-9_/.-]*)\$\{([^}]+)\}([a-z0-9_/.-]*)`')
MACHINE_RE = re.compile(r'\[\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"\s*,\s*\{\s*output:\s*\[([^\]]*)\]')
OUT_RE = re.compile(r'"(?:(\d+)x\s+)?([a-z0-9_.-]+:[a-z0-9_/.-]+)"')
DATA_RE = re.compile(r'^data/([a-z0-9_.-]+)/(tags/item|recipe|loot_table)/(.+)\.json$')
FOOD_TAG_RE = re.compile(r"^c:(foods|drinks)(/.*)?$")

IGNORE_NS = {"shippingbin", "c", "forge", "fabric", "neoforge", "global", "tag"}
RESULT_KEYS = {"result", "results", "output", "outputs"}
SKIP_KEYS = RESULT_KEYS | {"type", "conditions", "neoforge:conditions", "fabric:load_conditions", "forge:conditions"}
ING_KEYS = {"ingredient", "ingredients", "input", "inputs", "base", "addition", "template", "key"}
STATION_EXPLICIT = {"minecraft:smoking", "minecraft:campfire_cooking"}
STATION_NS = {"farmersdelight", "brewinandchewin", "meadow", "vinery", "nethervinery", "herbalbrews",
              "bakery", "candlelight", "farm_and_charm", "kaleidoscope_cookery"}
STATION_HINTS = ("cooking", "fermenting", "brewing", "distill", "mixing", "stove", "drying",
                 "caking", "baking", "pot", "station", "keg", "smoking", "campfire")
MACHINE_FACTOR = 1.35
CLASS_ORDER = ("machine", "animal", "food")


def is_item_like(iid):
    return iid.split(":", 1)[0] not in IGNORE_NS and "multiplier" not in iid


def num(s):
    f = float(s)
    return int(f) if f.is_integer() else f


def line_at(text, start, end):
    a = text.rfind("\n", 0, start) + 1
    b = text.find("\n", end)
    return text[a: b if b != -1 else len(text)]


def bracket_body(text, start):
    """Return the text between the '[' at start and its matching ']'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
    return text[start + 1:]


def load_check_ids():
    spec = importlib.util.spec_from_file_location("check_ids", CHECK_IDS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TEMPLATE_LISTS = ("geodeList", "frozenGeodeList", "magmaGeodeList", "gems", "artifacts", "relics")
# Same food, different mod, found while auditing; both sides must be priced (checked at lookup).
PRICE_ALIASES = {
    "hearthandharvest:corn": "farm_and_charm:corn",
    "hearthandharvest:hops": "brewery:hops",
    "wildernature:cooked_turkey_meat": "autumnity:cooked_turkey",
}


def canonical_pairs():
    text = (KJS / "startup_scripts" / "globalCanonicalItems.js").read_text("utf-8", "ignore")
    decl = re.search(r"global\.canonicalItems\s*=\s*\{", text)
    if not decl:
        return {}
    body = bracket_body(text, decl.end() - 1)
    return {a: b for a, b in re.findall(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', body)}


def load_existing(ci, jars):
    """Ids that exist: jars + client assets/loot (check_ids.collect) + kubejs .create/.crop registrations."""
    known, *_ = ci.collect(jars)
    existing = set(known)
    for f in sorted((KJS / "startup_scripts").rglob("*.js")):
        text = f.read_text("utf-8", "ignore")
        existing.update(m.group(1) for m in ci.CREATE_RE.finditer(text))
        existing.update(m.group(1) for m in ci.CROP_RE.finditer(text))
        for m in ci.TEMPLATE_CREATE_RE.finditer(text):
            end = text.rfind("].forEach", 0, m.start())
            begin = text.rfind("[", 0, end) if end != -1 else -1
            if begin != -1:
                existing.update(f"{m.group(1)}:{n}" for n in re.findall(r'["\']([a-z0-9_]+)["\']', text[begin:end]))
    # Fluids registered in registerFluids.js are not items: drop them unless a jar defines them.
    fluid_file = KJS / "startup_scripts" / "registration" / "registerFluids.js"
    if fluid_file.exists():
        fluids = {m.group(1) for m in ci.CREATE_RE.finditer(fluid_file.read_text("utf-8", "ignore"))}
        existing -= fluids - set(known)
    # Template registrations (e.create(`society:${x.item.path}`)): take the item ids of the lists they iterate.
    gr = KJS / "startup_scripts" / "globalRegistry.js"
    if gr.exists():
        text = gr.read_text("utf-8", "ignore")
        for name in TEMPLATE_LISTS:
            decl = re.search(r"global\." + name + r"\s*=\s*\[", text)
            if decl:
                body = bracket_body(text, decl.end() - 1)
                existing.update(i for i in re.findall(r'item:\s*"(society:[a-z0-9_./-]+)"', body))
    return {i for i in existing if is_item_like(i)}


def load_data(jars):
    """Return (origin, ns, kind, path, text) for every tag, recipe and loot table in jars and kubejs/data."""
    entries = []
    for jp in jars:
        try:
            z = zipfile.ZipFile(jp)
        except (OSError, zipfile.BadZipFile):
            continue
        for n in z.namelist():
            m = DATA_RE.match(n)
            if m:
                entries.append(("jar", m.group(1), m.group(2), m.group(3), z.read(n).decode("utf-8", "ignore")))
    for f in sorted((KJS / "data").rglob("*.json")):
        m = DATA_RE.match("data/" + f.relative_to(KJS / "data").as_posix())
        if m:
            entries.append(("kubejs", m.group(1), m.group(2), m.group(3), f.read_text("utf-8", "ignore")))
    return entries


def walk_ings(node, key, items, tags):
    if isinstance(node, list):
        for x in node:
            walk_ings(x, key, items, tags)
    elif isinstance(node, dict):
        if isinstance(node.get("item"), str):
            items.add(node["item"])
        if isinstance(node.get("tag"), str):
            tags.add(node["tag"])
        if key in ING_KEYS and isinstance(node.get("id"), str):
            items.add(node["id"])
        for k, v in node.items():
            if k not in ("item", "tag"):
                walk_ings(v, k, items, tags)
    elif isinstance(node, str) and key in ING_KEYS:
        if node.startswith("#"):
            tags.add(node[1:])
        elif SIMPLE_ID_RE.match(node):
            items.add(node)


def parse_stack(v):
    if isinstance(v, str):
        return (v, 1)
    if isinstance(v, dict):
        iid = v.get("id", v.get("item"))
        if isinstance(iid, str):
            return (iid, max(1, int(v.get("count", 1) or 1)))
    return None


def parse_data(entries):
    tags, recipes, loot = collections.defaultdict(list), [], []
    for origin, ns, kind, path, text in entries:
        if kind == "loot_table":
            loot.append((origin, ns, path, text))
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            continue
        if kind == "tags/item":
            for v in data.get("values", []):
                tags[f"{ns}:{path}"].append(v if isinstance(v, str) else str(v.get("id", "")))
        elif kind == "recipe" and isinstance(data, dict):
            outs = []
            for k in RESULT_KEYS:
                if k in data:
                    vals = data[k] if isinstance(data[k], list) else [data[k]]
                    outs += [p for p in (parse_stack(v) for v in vals) if p]
            items, rtags = set(), set()
            for k, v in data.items():
                if k not in SKIP_KEYS:
                    walk_ings(v, k, items, rtags)
            recipes.append({"type": str(data.get("type", "")), "origin": origin, "outputs": outs,
                            "items": items, "tags": rtags})
    return tags, recipes, loot


def is_station(rtype):
    if rtype in STATION_EXPLICIT:
        return True
    ns, _, path = rtype.partition(":")
    return ns in STATION_NS and any(h in path for h in STATION_HINTS)


def station_mult(rtype):
    """Return (multiplier, known). Multipliers follow globalRegistryAddonFoods.js; others use x2."""
    path = rtype.split(":", 1)[-1]
    if any(h in path for h in ("fermenting", "brewing", "mixing", "stove")):
        return 3.0, True
    if "crafting" in path:
        return 1.4, True
    if any(h in path for h in ("smoking", "campfire", "drying")):
        return 1.5, True
    if "cooking" in path or "pot" in path:
        return 2.0, True
    return 2.0, False


def bracket_expand_template(text, m):
    ns, prefix, expr, suffix = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
    root = expr.split(".")[0]
    if expr not in (root, root + ".item.path", root + ".path"):
        return None, "unsupported expression"
    headers = list(re.finditer(r'([A-Za-z_][\w.]*)\.forEach\(\s*\(?\s*%s\s*\)?\s*=>' % re.escape(root),
                               text[:m.start()]))
    if not headers:
        return None, f"no forEach over {root} before it"
    src = headers[-1].group(1)
    decl = re.search(r'(?<![\w.])%s\s*=\s*\[' % re.escape(src.split(".")[-1]), text)
    if not decl:
        return None, f"list {src} not defined in this file"
    body = bracket_body(text, decl.end() - 1)
    if expr == root:
        elems = re.findall(r'"([a-z0-9_/.-]+)"', body)
    else:
        elems = [i.split(":", 1)[1] for i in re.findall(r'item:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"', body)]
    if not elems:
        return None, f"list {src} has no usable entries"
    return [f"{ns}:{prefix}{e}{suffix}" for e in elems], ""


def extract_prices(files):
    """Return ({id: {value, attr, files}}, expanded_count, unexpanded Counter of (pattern, reason))."""
    out, expanded, unexpanded = {}, 0, collections.Counter()
    for f in files:
        text = f.read_text("utf-8", "ignore")
        for m in ID_RE.finditer(text):
            iid = f"{m.group(1)}:{m.group(2)}"
            if not is_item_like(iid):
                continue
            rec = out.setdefault(iid, {"value": None, "attr": None, "files": set()})
            rec["files"].add(f.name)
            if rec["value"] is None or rec["attr"] is None:
                line = line_at(text, m.start(), m.end())
                lit = re.escape(iid)
                if rec["value"] is None:
                    vm = (re.search(r'"%s"[^\n]*?\bvalue:\s*(?:global\.getConfiguredValue\(\s*)?(\d+(?:\.\d+)?)' % lit, line)
                          or re.search(r'"%s"\s*,\s*(\d+(?:\.\d+)?)\s*\]' % lit, line)
                          or re.search(r'"%s"[^\n]*?getConfiguredValue\(\s*(\d+(?:\.\d+)?)' % lit, line))
                    if vm:
                        rec["value"] = num(vm.group(1))
                if rec["attr"] is None:
                    am = re.search(r'"%s"[^\n]*?getConfiguredValue\(\s*[\d.]+\s*,\s*["\'](\w+)["\']' % lit, line)
                    if am:
                        rec["attr"] = am.group(1)
        for m in TPL_RE.finditer(text):
            ids, reason = bracket_expand_template(text, m)
            if ids is None:
                unexpanded[(m.group(0), reason)] += 1
                continue
            for iid in ids:
                if is_item_like(iid):
                    rec = out.setdefault(iid, {"value": None, "attr": None, "files": set()})
                    rec["files"].add(f.name)
                    expanded += 1
    return out, expanded, unexpanded


def ids_in(path):
    if not path.exists():
        return set()
    return {f"{a}:{b}" for a, b in ID_RE.findall(path.read_text("utf-8", "ignore")) if is_item_like(f"{a}:{b}")}


def md_cell(s):
    return str(s if s is not None else "").replace("|", "/").replace("\n", " ")


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows]
    return lines


GEN_PATH = KJS / "startup_scripts" / "globalRegistryMissingPrices.js"
DEAD_LOG = HERE / "dead_fixes.json"
EXCLUDE_RULES = [
    (re.compile(r"_spawn_egg$"), "spawn egg"),
    (re.compile(r"sapling$"), "sapling"),
    (re.compile(r"totem"), "totem"),
    (re.compile(r"rubber_ring"), "toy or decor"),
    (re.compile(r"fertilized_soil|fertilizer"), "soil or fertilizer"),
    (re.compile(r"_stool$|_banner$"), "toy or decor"),
    (re.compile(r"loot_bag$|_food_bag$"), "loot container"),
    # Seeds follow the Seed Maker rule (conventions.md), never the recipe rule.
    (re.compile(r"_seeds?$|seedling$"), "seed"),
]
FEAST_RE = re.compile(r"(_salad)?_block$")
SERVING_RE = re.compile(r"slice|serving|portion|piece|wedge")
FALLBACK_PATH_RE = re.compile(r"(^|_)(water_bottle|milk_bottle|sugar|ice|bowl|glass_bottle|sticks?)$")
FALLBACK_COINS = 2.0
ANIMAL_FALLBACK = 5
WRAP = {"wood": "shippingbin:wood_sell_multiplier", "meat": "shippingbin:meat_sell_multiplier",
        "gem": "shippingbin:gem_sell_multiplier"}


def crop_factor(iid):
    """Factor globalPriceBalance.js applies to a raw crop: EASY_CROPS 1/3, NORMAL_CROPS 1/1.5, else 1."""
    text = (KJS / "startup_scripts" / "globalPriceBalance.js").read_text("utf-8", "ignore")
    for name, factor in (("EASY_CROPS", 1 / 3), ("NORMAL_CROPS", 1 / 1.5)):
        m = re.search(name + r"\s*=\s*\[(.*?)\];", text, re.S)
        if m and f'"{iid}"' in m.group(1):
            return factor
    return 1


def price_files(unsell_unused=None):
    files = sorted((KJS / "startup_scripts").glob("globalRegistry*.js"))
    files += [KJS / "startup_scripts" / n for n in ("globalPriceBalance.js", "globalCanonicalItems.js")]
    return [f for f in files if f.exists() and f != GEN_PATH]


def load_priced(unsell):
    files = price_files()
    priced, expanded, unexpanded = extract_prices(files)
    return {k: v for k, v in priced.items() if k not in unsell}, expanded, unexpanded


def exclusion_reason(iid, priced):
    ns, path = iid.split(":", 1)
    for rx, why in EXCLUDE_RULES:
        if rx.search(path):
            return why
    if FEAST_RE.search(path):
        stem = FEAST_RE.sub("", path)
        for pid in priced:
            pns, ppath = pid.split(":", 1)
            if pns == ns and stem and stem in ppath and SERVING_RE.search(ppath):
                return "placeable feast block, serving priced"
    return None


def is_fallback_item(iid):
    ns, path = iid.split(":", 1)
    return ns == "minecraft" or FALLBACK_PATH_RE.search(path) is not None


def compute_dead(existing, priced):
    existing_by_path = collections.defaultdict(list)
    pool_by_ns = collections.defaultdict(list)
    for e in sorted(existing):
        ns, path = e.split(":", 1)
        existing_by_path[path].append(e)
        pool_by_ns[ns].append(path)
    dead = []
    for pid in sorted(i for i in priced if i not in existing):
        ns, path = pid.split(":", 1)
        others = [e for e in existing_by_path.get(path, []) if e != pid]
        if others:
            conf = "high" if len(others) == 1 else "low"
            dead.append((pid, sorted(others)[0], conf, "same path under another namespace"))
            continue
        close = difflib.get_close_matches(path, pool_by_ns.get(ns, []), n=1, cutoff=0.6)
        if close:
            ratio = difflib.SequenceMatcher(None, path, close[0]).ratio()
            conf = "high" if ratio >= 0.9 else "low"
            dead.append((pid, f"{ns}:{close[0]}", conf, f"fuzzy name match ({ratio:.2f})"))
        else:
            dead.append((pid, None, "none", "no candidate"))
    return dead


def apply_dead_fixes(dead, priced):
    """Rename high-confidence dead ids in the price files (ids only, never values)."""
    log = json.loads(DEAD_LOG.read_text("utf-8")) if DEAD_LOG.exists() else []
    applied = []
    for pid, sugg, conf, _ in dead:
        if conf != "high" or sugg is None or sugg in priced:
            continue
        needle = f'"{pid}"'
        for f in price_files():
            text = f.read_text("utf-8", "ignore")
            if needle in text:
                f.write_text(text.replace(needle, f'"{sugg}"'), "utf-8")
                applied.append({"dead": pid, "sugg": sugg, "file": f.name})
                break
    if applied:
        log.extend(applied)
        DEAD_LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return log


def write_generated(rows):
    lines = ["// priority: -22",
             "// Generated by tools/priceaudit/price_audit.py. Do not edit by hand: rerun the tool.",
             "// Each entry: [global list name, item id, shipping bin value, attribute].",
             "const missingPriceEntries = ["]
    for r in rows:
        if r["suggested"] is not None:
            lines.append(f'  ["{r["list"]}", "{r["id"]}", {r["suggested"]}, "{r["attribute"]}"],')
    lines += [
        "];",
        "",
        "// Rhino 2101: no const/let inside functions; declare with let at the top.",
        "const missingPriceHelper = (entry) => {",
        "  let list;",
        "  let multiplier;",
        "  if (global.trades.has(entry[1])) return;",
        "  list = global[entry[0]];",
        "  if (list) list.push({ item: entry[1], value: entry[2] });",
        "  multiplier = entry[3] === \"wood\" ? \"shippingbin:wood_sell_multiplier\"",
        "    : entry[3] === \"meat\" ? \"shippingbin:meat_sell_multiplier\"",
        "    : entry[3] === \"gem\" ? \"shippingbin:gem_sell_multiplier\"",
        "    : \"shippingbin:crop_sell_multiplier\";",
        "  global.trades.set(entry[1], {",
        "    value: global.getConfiguredValue(entry[2], entry[3]),",
        "    multiplier: multiplier,",
        "  });",
        "};",
        "",
        "missingPriceEntries.forEach((entry) => { missingPriceHelper(entry); });",
        "",
    ]
    GEN_PATH.write_text("\n".join(lines), "utf-8")


def main():
    ci = load_check_ids()
    jars = sorted((ROOT / "mods").glob("*.jar")) + [ci.CLIENT_JAR]
    existing = load_existing(ci, jars)
    tags, recipes, loot = parse_data(load_data(jars))
    unsell = ids_in(KJS / "startup_scripts" / "globalUnsellableItems.js")

    priced, expanded, unexpanded = load_priced(unsell)
    dead = compute_dead(existing, priced)
    # Renaming dead ids is opt-in: the id scan misses template registrations (society geodes)
    # and counts fluids as items, so every suggestion needs a manual check first.
    if "--apply-dead" in sys.argv and apply_dead_fixes(dead, priced):
        priced, expanded, unexpanded = load_priced(unsell)
        dead = compute_dead(existing, priced)
    fixes_log = json.loads(DEAD_LOG.read_text("utf-8")) if DEAD_LOG.exists() else []

    ref_files = sorted((OLD_KJS / "startup_scripts").glob("globalRegistry*.js"))
    ref_files += [OLD_KJS / "startup_scripts" / n for n in ("globalPriceBalance.js", "globalCanonicalItems.js")]
    ref, _, _ = extract_prices([f for f in ref_files if f.exists()])
    if not ref:
        print("warn: no 1.20.1 price files found", file=sys.stderr)

    cands = collections.defaultdict(lambda: {"classes": set(), "sources": set()})
    entries = collections.defaultdict(list)

    def add_cand(iid, cls, src):
        if iid in existing and iid not in unsell:
            cands[iid]["classes"].add(cls)
            cands[iid]["sources"].add(src)
            return True
        return False

    # a. machine outputs
    machine_files = sorted((KJS / "startup_scripts" / "customMachines").glob("*.js"))
    machine_files += sorted((KJS / "startup_scripts" / "powerfulMachines").glob("*.js"))
    machine_files.append(KJS / "startup_scripts" / "fishPondDefinitions.js")
    machine_counts = collections.Counter()
    for f in machine_files:
        if not f.exists():
            continue
        for m in MACHINE_RE.finditer(f.read_text("utf-8", "ignore")):
            for om in OUT_RE.finditer(m.group(2)):
                oid = om.group(2)
                if add_cand(oid, "machine", f"machine {f.name}"):
                    entries[oid].append({"kind": "machine", "input": m.group(1),
                                         "count": max(1, int(om.group(1) or 1)),
                                         "label": f"machine {f.name}"})
                    machine_counts[f.name] += 1
    for oid in sorted(existing):
        if re.match(r"^society:(double_)?aged_", oid):
            add_cand(oid, "machine", "aged name pattern (society:aged_*)")

    # b. animal products
    husbandry = KJS / "startup_scripts" / "husbandryDefinitions.js"
    animal_entities = set()
    for line in husbandry.read_text("utf-8", "ignore").splitlines() if husbandry.exists() else []:
        if re.search(r"\banimal\s*:", line):
            animal_entities.update(f"{a}:{b}" for a, b in ID_RE.findall(line))
            continue
        for m in ID_RE.finditer(line):
            add_cand(f"{m.group(1)}:{m.group(2)}", "animal", "husbandryDefinitions.js")
    registry = KJS / "startup_scripts" / "globalRegistry.js"
    if registry.exists():
        text = registry.read_text("utf-8", "ignore")
        decl = re.search(r"global\.animalProducts\s*=\s*\[", text)
        if decl:
            for a, b in ID_RE.findall(bracket_body(text, decl.end() - 1)):
                add_cand(f"{a}:{b}", "animal", "globalRegistry.js animalProducts")
    for origin, ns, path, text in loot:
        if origin == "kubejs" and re.search(r"shears|husbandry|animal", path):
            for name in LOOT_NAME_RE.findall(text):
                add_cand(name, "animal", f"loot {ns}:{path}")
    for ent in sorted(animal_entities):
        ens, _, epath = ent.partition(":")
        for origin, ns, path, text in loot:
            if ns == ens and path == f"entities/{epath}":
                for name in LOOT_NAME_RE.findall(text):
                    add_cand(name, "animal", f"entity loot {ens}:{path}")

    # c. food: recipe outputs in c:foods / c:drinks or from station recipe types
    food_keys = [k for k in tags if FOOD_TAG_RE.match(k)]
    tag_cache = {}

    def resolve_tag(key, seen=()):
        if key in tag_cache:
            return tag_cache[key]
        if key in seen:
            return set()
        out = set()
        for v in tags.get(key, []):
            if v.startswith("#"):
                out |= resolve_tag(v[1:], seen + (key,))
            elif v:
                out.add(v)
        tag_cache[key] = out
        return out

    food_set = set()
    for k in food_keys:
        food_set |= resolve_tag(k)
    recipe_types = collections.Counter()
    other_mult_types = set()
    for r in recipes:
        station = is_station(r["type"])
        mult, known = station_mult(r["type"])
        for oid, cnt in r["outputs"]:
            if oid not in existing or oid in unsell:
                continue
            if oid not in food_set and not station:
                continue
            add_cand(oid, "food", f"recipe {r['type']}")
            if not known:
                other_mult_types.add(r["type"])
            recipe_types[r["type"]] += 1
            entries[oid].append({"kind": "recipe", "items": sorted(r["items"]), "tags": sorted(r["tags"]),
                                 "count": cnt, "mult": mult, "label": f"recipe {r['type']}"})

    # Exclude non-products from candidates
    excluded = {}
    for iid in sorted(cands):
        reason = exclusion_reason(iid, priced)
        if reason:
            excluded[iid] = reason
            del cands[iid]

    missing_ids = sorted(i for i in cands if i not in priced and i not in unsell)

    memo = {}
    alias_used = {}
    canon = canonical_pairs()
    by_path = collections.defaultdict(list)
    for pid, pv in priced.items():
        if pv["value"] is not None:
            by_path[pid.split(":", 1)[1]].append(pid)

    def alias_target(iid):
        """Priced equivalent of an unpriced id: explicit table, canonical pair, or same path in one other namespace."""
        def ok(t):
            return t is not None and t != iid and t in priced and priced[t]["value"] is not None
        t = PRICE_ALIASES.get(iid)
        if ok(t):
            return t
        if iid in canon and ok(canon[iid]):
            return canon[iid]
        inv = {v: k for k, v in canon.items()}
        if iid in inv and ok(inv[iid]):
            return inv[iid]
        same = [x for x in by_path.get(iid.split(":", 1)[1], []) if x != iid]
        if len(same) == 1:
            return same[0]
        return None

    def ingredient_blockers(iid):
        out = set()
        for ent in entries.get(iid, []):
            if ent["kind"] == "machine":
                if price_of(ent["input"])[0] is None:
                    out.add(ent["input"])
                continue
            for it in ent["items"]:
                if price_of(it)[0] is None:
                    out.add(it)
            for tg in ent["tags"]:
                if not any(price_of(m)[0] is not None for m in resolve_tag(tg)):
                    out.add("#" + tg)
        return sorted(out)

    def clamp(v):
        return int(round(min(1000, max(5, v))))

    def price_of(iid, stack=()):
        p = priced.get(iid)
        if p and p["value"] is not None:
            return p["value"], "priced", False
        if iid in memo:
            return memo[iid]
        if iid in stack:
            return None, "", False
        res = (None, "", False)
        for ent in entries.get(iid, []):
            r = eval_entry(ent, stack + (iid,))
            if r is not None and r[0] is not None:
                res = (clamp(r[0]), ent["label"], r[1])
                break
        if res[0] is None:
            tgt = alias_target(iid)
            if tgt is not None:
                alias_used[iid] = tgt
                res = (priced[tgt]["value"], f"alias {tgt}", False)
        if res[0] is None and iid in ref and ref[iid]["value"] is not None:
            res = (ref[iid]["value"], "1.20.1 value", False)
        memo[iid] = res
        return res

    def eval_entry(ent, stack):
        """Return (raw_value, used_fallback) or None."""
        if ent["kind"] == "machine":
            v, _, _ = price_of(ent["input"], stack)
            if v is None:
                return None
            return v * MACHINE_FACTOR / ent["count"], False
        total = 0.0
        fb_any = False
        for it in ent["items"]:
            v, _, fb = price_of(it, stack)
            if v is None:
                v, fb = FALLBACK_COINS, True
            total += v
            fb_any = fb_any or fb
        for tg in ent["tags"]:
            opts = [price_of(m, stack) for m in sorted(resolve_tag(tg))]
            opts = [(v, fb) for v, _, fb in opts if v is not None]
            if opts:
                best = min(opts, key=lambda o: o[0])
                total += best[0]
                fb_any = fb_any or best[1]
            else:
                total += FALLBACK_COINS
                fb_any = True
        return total / ent["count"] * ent["mult"], fb_any

    rows = []
    for iid in missing_ids:
        classes = [c for c in CLASS_ORDER if c in cands[iid]["classes"]]
        value, label, fb = price_of(iid)
        src = label
        # A priced equivalent (same item from another mod) beats a recipe built on fallbacks.
        alias = alias_target(iid) if (value is None or fb or iid in PRICE_ALIASES) else None
        if alias:
            value, fb, src = priced[alias]["value"], False, "alias of " + alias
            # globalPriceBalance.js scales raw crops of its lists after this file runs; the
            # equivalent of a listed crop gets the same scaled value here.
            factor = crop_factor(alias)
            if factor != 1:
                value = max(1, round(value * factor))
                src += f" x{factor:.3f} (globalPriceBalance list)"
        if value is None:
            value, fb = ANIMAL_FALLBACK, True
            src = "no usable recipe or 1.20.1 price"
        if fb:
            src = "fallback: " + src
        attr = (ref.get(iid) or {}).get("attr") or "crop"
        if "food" in classes or "machine" in classes:
            lst = "cooking"
        elif "animal" in classes:
            lst = "animalProducts"
        else:
            lst = "cooking"
        rows.append({"id": iid, "class": classes[0], "classes": classes, "source": src,
                     "suggested": value, "attribute": attr, "list": lst, "fallback": bool(fb and value is not None)})

    dead_counts = collections.Counter(d[2] for d in dead)
    with_sugg = [r for r in rows if r["suggested"] is not None]
    unresolved = [r for r in rows if r["suggested"] is None]
    fallback_rows = [r for r in with_sugg if r["fallback"]]
    alias_rows = [r for r in with_sugg if r["source"].startswith("alias ")]
    no_recipe_rows = [r for r in rows if r["source"].startswith("fallback: no usable")]
    ing_fallback = sorted({it for ents in entries.values() for ent in ents
                           for it in ent.get("items", [])
                           if price_of(it)[0] is None and it not in alias_used})
    missing_ns = collections.Counter(r["id"].split(":", 1)[0] for r in rows)
    top5 = missing_ns.most_common(5)
    gen_by_class = collections.Counter(r["class"] for r in with_sugg)

    write_generated(with_sugg)

    md = ["# Auditoria de preços: Pipinha's Village", "",
          "Gerado por `tools/priceaudit/price_audit.py` (só lê o pack e a 1.20.1). Rodar de novo recria este arquivo; "
          "a saída é determinística. O arquivo gerado `kubejs/startup_scripts/globalRegistryMissingPrices.js` "
          "é escrito pelo mesmo script e não entra na leitura de PRICED, para a saída ser estável.", "",
          "## Resumo", ""]
    md += md_table(["Métrica", "Valor"], [
        ["Ids existentes (jars, cliente, kubejs)", len(existing)],
        ["PRICED (ids com preço no kubejs)", len(priced)],
        ["PRICED com valor literal", sum(1 for v in priced.values() if v["value"] is not None)],
        ["DEAD_PRICED restante", len(dead)],
        ["  DEAD_PRICED alta confiança (não corrigidos)", dead_counts["high"]],
        ["  DEAD_PRICED baixa confiança", dead_counts["low"]],
        ["  DEAD_PRICED sem sugestão", dead_counts["none"]],
        ["Correções de id aplicadas (dead_fixes.json)", len(fixes_log)],
        ["Candidatos existentes (sem excluídos)", len(cands)],
        ["Excluídos (não são produto)", len(excluded)],
        ["MISSING (ids únicos)", len(rows)],
        ["MISSING com sugestão (gerados)", len(with_sugg)],
        ["  gerados com fallback", len(fallback_rows)],
        ["  gerados por alias de preço", len(alias_rows)],
        ["  gerados por classe food/machine/animal",
         f"{gen_by_class['food']}/{gen_by_class['machine']}/{gen_by_class['animal']}"],
        ["UNRESOLVED (ficam sem preço)", len(unresolved)],
        ["MISSING após aplicar (UNRESOLVED + excluídos)", len(unresolved) + len(excluded)],
        ["Excluídos (globalUnsellableItems.js)", len(unsell)],
    ])
    md += ["", "## Candidatos e faltantes por classe", ""]
    class_rows = []
    for c in CLASS_ORDER:
        cand_c = [i for i in cands if c in cands[i]["classes"]]
        miss_c = [r for r in rows if c in r["classes"]]
        class_rows.append([c, len(cand_c), len(miss_c),
                           sum(1 for r in miss_c if r["suggested"] is not None),
                           sum(1 for r in miss_c if r["suggested"] is None)])
    md += md_table(["Classe", "Candidatos", "MISSING", "Com sugestão", "UNRESOLVED"], class_rows)
    md += ["", "Um id com mais de uma classe aparece em cada uma delas nesta tabela; "
           "no missing.json ele sai uma vez, com a primeira classe em ordem machine, animal, food.", ""]
    md += ["Maiores namespaces em MISSING: " + ", ".join(f"{ns} ({n})" for ns, n in top5) + ".", ""]
    md += ["## Excluídos (não são produto)", ""]
    md += md_table(["id", "motivo"], [[i, excluded[i]] for i in sorted(excluded)]) if excluded else ["Nenhum."]
    md += ["", "## Correções de id aplicadas (DEAD_PRICED alta confiança)", ""]
    md += md_table(["id antigo", "id novo", "arquivo"],
                   [[f_["dead"], f_["sugg"], f_["file"]] for f_ in fixes_log]) if fixes_log else ["Nenhuma."]
    md += ["", "## MISSING por namespace", ""]
    by_ns = collections.defaultdict(list)
    for r in rows:
        by_ns[r["id"].split(":", 1)[0]].append(r)
    for ns in sorted(by_ns, key=lambda n: (-len(by_ns[n]), n)):
        md += [f"### {ns} ({len(by_ns[ns])})", ""]
        md += md_table(["id", "classe", "fonte", "sugestão", "atributo", "lista"],
                       [[r["id"], ",".join(r["classes"]), r["source"],
                         "" if r["suggested"] is None else r["suggested"], r["attribute"], r["list"]]
                        for r in by_ns[ns]])
        md.append("")
    md += ["## PRICED (ids com preço no kubejs)", ""]
    md += md_table(["id", "valor", "existe", "arquivos"],
                   [[pid, "" if p["value"] is None else p["value"], "sim" if pid in existing else "não",
                     ", ".join(sorted(p["files"]))] for pid, p in sorted(priced.items())])
    md += ["", "## DEAD_PRICED (preço para id que não existe)", ""]
    md += md_table(["id", "sugestão", "confiança", "evidência"], [list(d) for d in dead])
    md += ["", "## UNRESOLVED", ""]
    md += ["Nenhum: todo MISSING tem preço (alias, receita ou fallback)." if not unresolved
           else "Itens sem preço: " + ", ".join(f"`{r['id']}`" for r in unresolved) + "."]
    md += ["", "## Fallback de 5 moedas (sem receita útil nem preço 1.20.1)", ""]
    md += md_table(["id", "classe", "bloqueio (insumo sem preço)"],
                   [[r["id"], ",".join(r["classes"]), ", ".join(ingredient_blockers(r["id"])) or "nenhum"]
                    for r in no_recipe_rows]) if no_recipe_rows else ["Nenhum."]
    md += ["", "## Aliases de preço aplicados", ""]
    md += md_table(["id sem preço", "alias para (já priced)"], [[k, v] for k, v in sorted(alias_used.items())]) \
        if alias_used else ["Nenhum."]
    md += ["", "## Insumos sem preço próprio (fallback de 2 moedas por unidade)", ""]
    md += [", ".join(f"`{x}`" for x in ing_fallback) or "Nenhum."]
    md += ["", "## Tipos de receita contados (candidatos de food)", ""]
    md += md_table(["tipo", "receitas que geraram candidato", "multiplicador"],
                   [[t, n, f"x{station_mult(t)[0]:g}" + ("" if station_mult(t)[1] else " (padrão, sem regra)")]
                    for t, n in sorted(recipe_types.items())])
    md += ["", "Tipos de estação sem regra própria de multiplicador usam x2: "
           + (", ".join(f"`{t}`" for t in sorted(other_mult_types)) or "nenhum") + ".", ""]
    md += ["## Padrões de template", "", f"Ids expandidos a partir de listas no mesmo arquivo: {expanded}.", ""]
    md += md_table(["padrão", "motivo", "ocorrências"],
                   [[p, reason, n] for (p, reason), n in sorted(unexpanded.items())]) \
        if unexpanded else ["Nenhum padrão sem expansão."]
    md += ["", "## Método", "",
           "- PRICED: ids literais em `globalRegistry*.js`, `globalPriceBalance.js` e `globalCanonicalItems.js`. "
           "Valor só quando aparece como `{ item, value }`, `[id, N]` ou `getConfiguredValue(N, ...)` na mesma linha.",
           "- Exclusão: spawn eggs, saplings, totens, brinquedos/decoração e solo/fertilizante. Blocos `*_block` "
           "(e `*_salad_block`) só são excluídos quando existe fatia/porção priced com o mesmo radical.",
           "- Receitas: saída de receitas em `c:foods`/`c:drinks` ou de tipos de estação (lista acima). "
           "Preço = soma dos insumos / quantidade de saída x multiplicador da estação, limitado a [5, 1000]. "
           "Tag de insumo usa o membro mais barato com preço.",
           f"- Fallback de insumo sem preço e sem receita: {FALLBACK_COINS:g} moedas por unidade para `minecraft:*`, "
           "tags `c:*` e garrafas, leite, açúcar, gelo, tigelas e varas. Marcado como `fallback`.",
           f"- Máquinas: preço da entrada x {MACHINE_FACTOR} / quantidade de saída, quando a entrada tem preço.",
           f"- Animal sem receita e sem preço 1.20.1: {ANIMAL_FALLBACK} moedas (mínimo), marcado como `fallback`.",
           "- Ordem do preço: receita; depois alias de preço: primeiro a tabela `PRICE_ALIASES` "
           "(hearthandharvest:corn, hearthandharvest:hops, wildernature:cooked_turkey_meat), depois o par de "
           "`global.canonicalItems` (nos dois sentidos), depois o mesmo caminho em um único outro namespace. O alvo tem que ser PRICED.",
           "- Sem preço até aqui: valor de 1.20.1 do mesmo id, se existir; senão fallback de 5 moedas, marcado como `fallback`.",
           "- Ids de fluido criados em `registerFluids.js` não contam como itens; os templates de geode/gema/artefato/relíquia entram pelas listas de `globalRegistry.js`.",
           "- Atributo: o da entrada 1.20.1 quando existe, senão `crop`. Lista: `cooking` para food e máquina, "
           "`animalProducts` para animal.",
           f"- Saídas de máquina contadas por arquivo: "
           + (", ".join(f"{k} ({v})" for k, v in machine_counts.most_common()) or "nenhuma") + ".",
           f"- Gerado: `kubejs/startup_scripts/globalRegistryMissingPrices.js` com {len(with_sugg)} entradas.",
           ""]
    (HERE / "REPORT.md").write_text("\n".join(md) + "\n", "utf-8")

    keys = ("id", "class", "classes", "source", "suggested", "attribute", "list", "fallback")
    payload = [{k: r[k] for k in keys} for r in rows]
    (HERE / "missing.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", "utf-8")

    print(f"existing={len(existing)} priced={len(priced)} dead={len(dead)} "
          f"(high={dead_counts['high']} low={dead_counts['low']} none={dead_counts['none']}) "
          f"excluded={len(excluded)} missing={len(rows)} generated={len(with_sugg)} "
          f"fallback={len(fallback_rows)} unresolved={len(unresolved)}")
    print("top namespaces: " + ", ".join(f"{ns}={n}" for ns, n in top5))


if __name__ == "__main__":
    main()
