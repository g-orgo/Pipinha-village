#!/usr/bin/env python3
"""Port the Society: Sunlit Valley 1.20.1 data packs into Pipinha's Village (1.21.1, NeoForge).

Run from anywhere with: python3 -I tools/dataport/port_data.py
The old instance is read only. Output goes to kubejs/data and the three
moonlight-global-datapacks folders of the new instance. Writes REPORT.md.
"""
import io
import json
import os
import re
import shutil
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent            # <NEW>/tools/dataport
NEW = HERE.parent.parent                          # <NEW>
OLD = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley")
PACKS = ["deceasedcraft_houses", "sunlit_towns", "zzz_sunlit_harmony"]
MANIFEST = HERE / "manifest.json"
UNK_JSON = HERE / "unknown_namespaces.json"
REPORT = HERE / "REPORT.md"
MODIDS = NEW / "tools" / "modcheck" / "modids.txt"

# Files whose id collides at runtime. Meadow 1.21.1 rewrites every ResourceLocation
# meadow:fire_log -> meadow:firewood (DataFixerMixin), so a recipe file named fire_log
# gets the same id as Meadow's own firewood recipe and crashes the data load.
FILE_RENAMES = {
    ("meadow", "recipe/fire_log.json"): "recipe/firewood_from_raw_logs.json",
    ("meadow", "recipe/fire_log_unpack.json"): "recipe/firewood_unpack.json",
}
DIR_MAP = {"recipes": "recipe", "loot_tables": "loot_table", "advancements": "advancement",
           "functions": "function", "structures": "structure", "predicates": "predicate",
           "item_modifiers": "item_modifier"}
TAG_MAP = {"items": "item", "blocks": "block", "entity_types": "entity_type",
           "fluids": "fluid", "game_events": "game_event", "functions": "function"}
REMOVED_NS = {"botania", "botania_seeds", "botaniaseeds", "splendid_slimes", "create_slime"}
FORGE_COND = {"forge:mod_loaded", "forge:not", "forge:and", "forge:or", "forge:tag_empty"}
TEXT_EXT = {".json", ".mcmeta", ".mcfunction"}
REF_RE = re.compile(r'(?<=")#?([a-z0-9_\-]+):(?!//)[a-z0-9_./\-]+(?=")')  # no dotted keys, no URLs
FORGE_TAG_RE = re.compile(r'#forge:([a-z0-9_.\-]+(?:/[a-z0-9_.\-]+)*)')
FORGE_STR_RE = re.compile(r'^(#?)forge:([a-z0-9_.\-]+(?:/[a-z0-9_.\-]+)*)$')
# JSON keys that tell the registry type of the tag references below them (recipe ingredients use "tag").
KEY_TYPES = {"blocks": "block", "block": "block", "items": "item", "item": "item",
             "tag": "item", "fluid": "fluid", "fluids": "fluid", "entity_type": "entity_type"}
LARGE_RE = re.compile(r'(?<![A-Za-z0-9_])largemeals:')
DESC_REPL = [("Society: Sunlit Valley", "Pipinha's Village"),
             ("Sunlit Valley", "Pipinha's Village"),
             ("Sunlit", "Pipinha's Village")]

stats = Counter()
lists = {"nbt_dropped": [], "set_nbt": [], "parse_fail_old": [], "collision": [],
         "output_parse_fail": []}
written = set()
bad_jars = []


def iter_files(root):
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for f in sorted(fns):
            p = Path(dp) / f
            yield p, p.relative_to(root).parts


def map_inner(parts):
    """Apply the singular registry folder renames to the directories below the namespace."""
    out = []
    i, n = 0, len(parts)
    while i < n:
        seg = parts[i]
        if seg == "tags" and i + 1 < n - 1 and parts[i + 1] in TAG_MAP:
            out += ["tags", TAG_MAP[parts[i + 1]]]
            i += 2
            continue
        if i < n - 1 and seg in DIR_MAP:
            out.append(DIR_MAP[seg])
        else:
            out.append(seg)
        i += 1
    return out


def plan(kind, rel, R):
    """Return (new_rel, original_namespace, moved_forge_to_c) for a source relative path."""
    if kind == "kubejs":
        if len(rel) < 2:
            return rel, None, False
        prefix, k = (), 0
    else:
        if len(rel) < 3 or rel[0] != "data":
            return rel, None, False
        prefix, k = ("data",), 1
    ns = rel[k]
    inner = map_inner(list(rel[k + 1:]))
    moved = False
    new_ns = ns
    if ns == "forge" and len(inner) >= 3 and inner[0] == "tags":
        name = "/".join(inner[2:])
        if name.endswith(".json") and (inner[1], name[:-5]) in R:
            new_ns = "c"
            moved = True
    key = (new_ns, "/".join(inner))
    if key in FILE_RENAMES:
        inner = FILE_RENAMES[key].split("/")
    return prefix + (new_ns,) + tuple(inner), ns, moved


def scan_c_tags():
    """Collect every c:<X> tag path found in the jars of NEW mods/ (nested jars included)."""
    found = set()

    def scan_zip(zf, depth):
        for name in zf.namelist():
            if name.startswith("data/c/tags/") and name.endswith(".json"):
                parts = name[len("data/c/tags/"):].split("/", 1)
                if len(parts) == 2:
                    found.add((TAG_MAP.get(parts[0], parts[0]), parts[1][:-5]))
            elif name.endswith(".jar") and depth < 3:
                with zf.open(name) as f:
                    scan_zip(zipfile.ZipFile(io.BytesIO(f.read())), depth + 1)

    jars = sorted((NEW / "mods").glob("*.jar"))
    for jar in jars:
        try:
            with zipfile.ZipFile(jar) as zf:
                scan_zip(zf, 0)
        except (zipfile.BadZipFile, OSError):
            bad_jars.append(jar.name)
    return found, len(jars)


def convert_result(d):
    nd = {"id": d["item"]}
    if "count" in d:
        nd["count"] = d["count"]
    for k, v in d.items():
        if k not in ("item", "count", "nbt"):
            nd[k] = v
    return nd, "nbt" in d


def convert_recipe(obj):
    """Turn result {item,count,nbt} objects into {id,count}. Return True if any was converted."""
    if not isinstance(obj, dict):
        return False, False
    changed, had_nbt = False, False
    res = obj.get("result")
    if isinstance(res, dict) and "item" in res:
        obj["result"], nbt = convert_result(res)
        changed, had_nbt = True, had_nbt or nbt
        stats["result_converted"] += 1
    if isinstance(obj.get("results"), list):
        for i, r in enumerate(obj["results"]):
            if isinstance(r, dict) and "item" in r:
                obj["results"][i], nbt = convert_result(r)
                changed, had_nbt = True, had_nbt or nbt
                stats["result_converted"] += 1
    return changed, had_nbt


def has_forge_type(v):
    return any(isinstance(c, dict) and str(c.get("type", "")).startswith("forge:") for c in v)


def fix_conditions(node):
    if isinstance(node, list):
        for i, v in enumerate(node):
            node[i] = fix_conditions(v)
        return node
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "conditions" and isinstance(v, list) and has_forge_type(v):
                k = "neoforge:conditions"
                stats["conditions_key_renamed"] += 1
            out[k] = fix_conditions(v)
        t = out.get("type")
        if isinstance(t, str) and t in FORGE_COND:
            out["type"] = "neoforge:" + t[len("forge:"):]
            stats["condition_type_renamed"] += 1
        return out
    return node


def has_set_nbt(node):
    if isinstance(node, dict):
        if node.get("function") == "minecraft:set_nbt":
            return True
        return any(has_set_nbt(v) for v in node.values())
    if isinstance(node, list):
        return any(has_set_nbt(v) for v in node)
    return False


def replace_strings(v):
    if isinstance(v, str):
        for a, b in DESC_REPL:
            v = v.replace(a, b)
        return v
    if isinstance(v, dict):
        return {k: replace_strings(x) for k, x in v.items()}
    if isinstance(v, list):
        return [replace_strings(x) for x in v]
    return v


def fix_mcmeta(text):
    obj = json.loads(text)
    obj["pack"]["pack_format"] = 48
    if "description" in obj["pack"]:
        obj["pack"]["description"] = replace_strings(obj["pack"]["description"])
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def emit(dst, payload, rel, is_tag):
    if dst in written:
        if is_tag and dst.suffix == ".json":
            prev = json.loads(dst.read_text(encoding="utf-8"))
            new = json.loads(payload)
            vals = prev.get("values", [])
            for v in new.get("values", []):
                if v not in vals:
                    vals.append(v)
            prev["values"] = vals
            dst.write_text(json.dumps(prev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            stats["tag_merged"] += 1
            return
        stats["collision"] += 1
        lists["collision"].append(f"{dst.relative_to(NEW)} <- {'/'.join(rel)}")
        return
    written.add(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(payload, encoding="utf-8", newline="")


def emit_bytes(dst, data, rel):
    if dst in written:
        stats["collision"] += 1
        lists["collision"].append(f"{dst.relative_to(NEW)} <- {'/'.join(rel)}")
        return
    written.add(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)


def tag_default(kind, rel):
    # Registry type of a tag file (its folder under tags/), None for anything else.
    k = 0 if kind == "kubejs" else 1
    if kind != "kubejs" and (len(rel) < 3 or rel[0] != "data"):
        return None
    inner = map_inner(list(rel[k + 1:]))
    return inner[1] if len(inner) >= 3 and inner[0] == "tags" else None


def rewrite_forge(node, typ, fn):
    # Walk parsed JSON; fn(typ, name, original) returns the replacement for each forge tag string.
    # typ is the registry type from the closest known key or tag folder, None when unknown.
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "type":
                out[k] = v  # condition and predicate type ids, never tag references
            else:
                out[k] = rewrite_forge(v, KEY_TYPES.get(k, typ), fn)
        return out
    if isinstance(node, list):
        return [rewrite_forge(v, typ, fn) for v in node]
    if isinstance(node, str):
        m = FORGE_STR_RE.match(node)
        if m and (m.group(1) == "#" or typ is not None):
            return fn(typ, m.group(2), node)
    return node


# forge names whose standard 1.21 c: tag has a different name (the same-name c: tag exists only in a few mods).
C_ALIASES = {"tools/knives": "tools/knife"}


def forge_ref_handler(R):
    def on_ref(typ, name, original):
        if name in C_ALIASES:
            stats["forge_refs_rewritten"] += 1
            return ("#" if original.startswith("#") else "") + "c:" + C_ALIASES[name]
        if typ is None:
            stats["forge_refs_untyped"] += 1
            return original
        if (typ, name) in R:
            stats["forge_refs_rewritten"] += 1
            return ("#" if original.startswith("#") else "") + "c:" + name
        stats["forge_refs_kept"] += 1
        return original
    return on_ref


def collect_refs(kind, p, rel, refs):
    if p.suffix.lower() not in TEXT_EXT:
        return
    try:
        t = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    obj = None
    if p.suffix.lower() == ".json":
        try:
            obj = json.loads(t)
        except ValueError:
            obj = None
    if obj is None:
        for m in FORGE_TAG_RE.finditer(t):
            refs[(None, m.group(1))] += 1
        return

    def on_ref(typ, name, original):
        refs[(typ, name)] += 1
        return original
    rewrite_forge(obj, tag_default(kind, rel), on_ref)


def process(kind, src, rel, dst_root, R):
    stats["files"] += 1
    if kind == "pack" and rel == ("pack.mcmeta",):
        stats["mcmeta"] += 1
        emit(dst_root / "pack.mcmeta", fix_mcmeta(src.read_text(encoding="utf-8")), rel, False)
        return
    new_rel, ns, moved = plan(kind, rel, R)
    if ns in REMOVED_NS:
        stats["deleted"] += 1
        return
    if new_rel != rel:
        stats["path_changed"] += 1
    if moved:
        stats["forge_to_c"] += 1
    dst = dst_root.joinpath(*new_rel)
    raw = src.read_bytes()
    if src.suffix.lower() not in TEXT_EXT:
        stats["copied_raw"] += 1
        emit_bytes(dst, raw, rel)
        return
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        stats["copied_raw"] += 1
        emit_bytes(dst, raw, rel)
        return
    text, n_large = LARGE_RE.subn("large_meals:", text)
    stats["largemeals_replaced"] += n_large
    stats["copied_text"] += 1
    if src.suffix.lower() != ".json":
        # mcfunction and mcmeta carry no registry type, so their forge refs stay as they are.
        stats["forge_refs_untyped"] += len(FORGE_TAG_RE.findall(text))
        emit(dst, text, rel, False)
        return
    base = 0 if kind == "kubejs" else 1
    inner = new_rel[base + 1:] if ns is not None else ()
    is_tag = bool(inner) and inner[0] == "tags"
    try:
        obj = json.loads(text)
    except ValueError:
        lists["parse_fail_old"].append("/".join(rel))
        stats["old_parse_fail"] += 1
        stats["forge_refs_untyped"] += len(FORGE_TAG_RE.findall(text))
        emit(dst, text, rel, False)
        return
    before = json.dumps(obj, sort_keys=True)
    obj = rewrite_forge(obj, tag_default(kind, rel), forge_ref_handler(R))
    if inner and inner[0] == "recipe":
        _, had_nbt = convert_recipe(obj)
        if had_nbt:
            lists["nbt_dropped"].append("/".join(rel))
            stats["nbt_dropped_files"] += 1
    obj = fix_conditions(obj)
    if has_set_nbt(obj):
        lists["set_nbt"].append("/".join(rel))
    if json.dumps(obj, sort_keys=True) != before:
        stats["json_converted"] += 1
        text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    emit(dst, text, rel, is_tag)


ID_RE = re.compile(r'^#?([a-z0-9_.\-]+):[a-z0-9_./\-]+$')
MOD_DECL_RE = re.compile(r'(?m)^\s*modId\s*=\s*"([^"]+)"')
DROPPED = set()
OTHER = []


def ref_ns(value):
    """Namespace of a single id or #tag string, None for anything else or dotted keys."""
    if not isinstance(value, str):
        return None
    m = ID_RE.match(value)
    if m and "." not in m.group(1):
        return m.group(1)
    return None


def ids_in(node, out):
    """Collect the namespaces of every id-like string inside a JSON value."""
    if isinstance(node, dict):
        for v in node.values():
            ids_in(v, out)
    elif isinstance(node, list):
        for v in node:
            ids_in(v, out)
    else:
        ns = ref_ns(node)
        if ns:
            out.add(ns)
    return out


def declared_mod_ids():
    """modIds of the [[mods]] tables in OLD mods/*.jar (nested jars included, *.disabled skipped)."""
    found = set()

    def scan_zip(zf, depth):
        for name in zf.namelist():
            if name in ("META-INF/mods.toml", "META-INF/neoforge.mods.toml"):
                text = zf.read(name).decode("utf-8", "replace")
                for block in re.split(r'(?m)^\s*\[\[', text)[1:]:
                    if block.startswith("mods]]"):
                        m = MOD_DECL_RE.search(block)
                        if m:
                            found.add(m.group(1))
            elif name.endswith(".jar") and depth < 3 and name.startswith("META-INF/jarjar/"):
                with zf.open(name) as f:
                    scan_zip(zipfile.ZipFile(io.BytesIO(f.read())), depth + 1)

    for jar in sorted((OLD / "mods").glob("*.jar")):
        try:
            with zipfile.ZipFile(jar) as zf:
                scan_zip(zf, 0)
        except (zipfile.BadZipFile, OSError):
            bad_jars.append(jar.name)
    return found


def own_namespaces():
    """Data namespaces of our own output (kubejs/data/<ns> and the moonlight packs)."""
    data_ns = set()
    for p in written:
        parts = p.relative_to(NEW).parts
        if parts[:2] == ("kubejs", "data") and len(parts) > 2:
            data_ns.add(parts[2])
        elif len(parts) > 3 and parts[0] == "moonlight-global-datapacks" and parts[2] == "data":
            data_ns.add(parts[3])
    return data_ns


def prune_entries(entries, counts):
    kept = []
    for e in entries:
        if isinstance(e, dict) and ref_ns(e.get("name")) in DROPPED:
            counts["entries"] += 1
            continue
        if isinstance(e, dict) and isinstance(e.get("children"), list):
            e["children"] = prune_entries(e["children"], counts)
        kept.append(e)
    return kept


def prune_loot(obj, counts):
    pools = obj.get("pools")
    if not isinstance(pools, list):
        return
    kept = []
    for pool in pools:
        if isinstance(pool, dict) and isinstance(pool.get("entries"), list):
            had = len(pool["entries"]) > 0
            pool["entries"] = prune_entries(pool["entries"], counts)
            if had and not pool["entries"]:
                counts["pools"] += 1
                continue
        kept.append(pool)
    obj["pools"] = kept


def split_ns(rel):
    """Return (inner path under the data namespace folder) for a path relative to NEW."""
    if rel[:2] == ("kubejs", "data") and len(rel) > 3:
        return rel[3:]
    if len(rel) > 5 and rel[0] == "moonlight-global-datapacks" and rel[2] == "data":
        return rel[4:]
    return ()


def prune_dropped():
    """Remove references to DROPPED mods from our output; list the JSON that still has them."""
    for p in sorted(written, key=lambda x: x.as_posix()):
        if p.suffix.lower() != ".json" or not p.exists():
            continue
        rel = p.relative_to(NEW).parts
        inner = split_ns(rel)
        if not inner:
            continue
        kind = inner[0]
        if kind == "tags":
            obj = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(obj.get("values"), list):
                continue
            kept, n = [], 0
            for v in obj["values"]:
                ref = v.get("id") if isinstance(v, dict) else v
                if ref_ns(ref) in DROPPED:
                    n += 1
                else:
                    kept.append(v)
            if n:
                obj["values"] = kept
                p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                stats["tag_entries_removed"] += n
        elif kind == "recipe":
            obj = json.loads(p.read_text(encoding="utf-8"))
            if ids_in(obj, set()) & DROPPED:
                p.unlink()
                written.discard(p)
                stats["recipes_deleted"] += 1
        elif kind == "loot_table":
            obj = json.loads(p.read_text(encoding="utf-8"))
            counts = Counter()
            prune_loot(obj, counts)
            if counts:
                p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                stats["loot_entries_removed"] += counts["entries"]
                stats["loot_pools_removed"] += counts["pools"]
        elif kind == "advancement":
            obj = json.loads(p.read_text(encoding="utf-8"))
            if ids_in(obj, set()) & DROPPED:
                p.unlink()
                written.discard(p)
                stats["advancements_deleted"] += 1
    for p in sorted(written, key=lambda x: x.as_posix()):
        if p.suffix.lower() == ".json" and p.exists():
            if ids_in(json.loads(p.read_text(encoding="utf-8")), set()) & DROPPED:
                OTHER.append(p.relative_to(NEW).as_posix())


def main():
    if str(NEW).startswith(str(OLD)) or OLD.resolve() in NEW.resolve().parents:
        sys.exit("refusing to run: NEW points inside OLD")
    known = {ln.strip() for ln in MODIDS.read_text(encoding="utf-8").splitlines() if ln.strip()}

    jobs = [("kubejs", OLD / "kubejs" / "data", NEW / "kubejs" / "data")]
    jobs += [("pack", OLD / "moonlight-global-datapacks" / p, NEW / "moonlight-global-datapacks" / p)
             for p in PACKS]
    for _, _, dst in jobs:
        if OLD.resolve() == dst.resolve() or OLD.resolve() in dst.resolve().parents:
            sys.exit("refusing to write into OLD")

    # Pass 1: which forge tags are referenced, and which of them have a c: equivalent in the jars.
    refs = Counter()
    for kind, src, _ in jobs:
        for p, rel in iter_files(src):
            collect_refs(kind, p, rel, refs)
    c_tags, n_jars = scan_c_tags()
    R = {key for key in refs if key[0] is not None and key in c_tags}
    U = {key: refs[key] for key in refs if key[0] is not None and key not in c_tags}
    UNTYPED = {key: refs[key] for key in refs if key[0] is None}
    stats["jars_scanned"] = n_jars
    stats["c_tags_found"] = len(c_tags)

    # Backup or clear the targets. Our own previous output (listed in the manifest) is simply replaced.
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    backups, stamp = [], None
    for _, _, dst in jobs:
        key = dst.relative_to(NEW).as_posix()
        if not dst.exists():
            continue
        present = {p.relative_to(dst).as_posix() for p, _ in iter_files(dst)}
        if present and present != set(manifest.get(key, [])):
            stamp = stamp or datetime.now().strftime("%Y%m%d-%H%M%S")
            bdir = HERE / f"backup-{stamp}"
            bdir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dst), str(bdir / key.replace("/", "_")))
            backups.append(key)
        else:
            shutil.rmtree(dst)

    for kind, src, dst in jobs:
        for p, rel in iter_files(src):
            process(kind, p, rel, dst, R)

    # Drop references to mods that existed in 1.20.1 but are absent from 1.21.1.
    DROPPED.update(declared_mod_ids() - known - own_namespaces())
    DROPPED.update(REMOVED_NS)
    prune_dropped()

    # Manifest of what this run wrote, per target root.
    new_manifest = {}
    for _, _, dst in jobs:
        key = dst.relative_to(NEW).as_posix()
        new_manifest[key] = sorted(p.relative_to(dst).as_posix() for p, _ in iter_files(dst)) if dst.exists() else []
    MANIFEST.write_text(json.dumps(new_manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # Validate every JSON written, and find ids whose namespace is not in modids.txt.
    skip_ns = own_namespaces() | {"forge"}
    json_ok = 0
    unk_files, unk_refs = {}, Counter()
    for p in sorted(written, key=lambda x: x.as_posix()):
        if p.suffix.lower() != ".json":
            continue
        rel = p.relative_to(NEW).as_posix()
        text = p.read_text(encoding="utf-8")
        try:
            json.loads(text)
            json_ok += 1
        except ValueError:
            lists["output_parse_fail"].append(rel)
        seen = set()
        for m in REF_RE.finditer(text):
            ns = m.group(1)
            if ns == "minecraft" or ns in known or ns in skip_ns:
                continue
            unk_refs[ns] += 1
            seen.add(ns)
        for ns in sorted(seen):
            unk_files.setdefault(ns, []).append(rel)

    write_report(known, U, json_ok, unk_files, unk_refs, backups, n_jars, UNTYPED)
    print(f"files={stats['files']} copied_text={stats['copied_text']} copied_raw={stats['copied_raw']} "
          f"json_converted={stats['json_converted']} deleted={stats['deleted']} "
          f"json_ok={json_ok} json_fail={len(lists['output_parse_fail'])} "
          f"written={len(written)}")


def write_report(known, U, json_ok, unk_files, unk_refs, backups, n_jars, UNTYPED):
    out = []
    w = out.append
    w("# Data port report: Society: Sunlit Valley (1.20.1) -> Pipinha's Village (1.21.1)")
    w("")
    w("Generated by `tools/dataport/port_data.py` (`python3 -I tools/dataport/port_data.py`).")
    w("")
    w("## Counts")
    w("")
    w(f"- Source files read (OLD kubejs/data + 3 packs): {stats['files']}")
    w(f"- Text files written (json/mcfunction/mcmeta, after text rules): {stats['copied_text']}")
    w(f"- Binary/other files copied unchanged (.nbt etc.): {stats['copied_raw']}")
    w(f"- JSON files converted in structure (recipe results, conditions): {stats['json_converted']}")
    w(f"- Files whose path changed (folder rename or forge->c): {stats['path_changed']}")
    w(f"- Files moved from forge to c namespace: {stats['forge_to_c']}")
    w(f"- Tag files merged into an existing c tag: {stats.get('tag_merged', 0)}")
    w(f"- Files deleted (removed namespaces): {stats['deleted']}")
    w(f"- Path collisions skipped: {stats['collision']}")
    w(f"- pack.mcmeta updated (pack_format 48, description renamed): {stats['mcmeta']}")
    w(f"- Recipe results converted to {{id, count}}: {stats['result_converted']}")
    w(f"- Recipe files with nbt dropped: {stats['nbt_dropped_files']}")
    w(f"- Condition keys renamed to neoforge:conditions: {stats['conditions_key_renamed']}")
    w(f"- Condition types forge: -> neoforge: : {stats['condition_type_renamed']}")
    w(f"- largemeals: -> large_meals: replacements: {stats['largemeals_replaced']}")
    w(f"- forge tag references rewritten to c:: {stats['forge_refs_rewritten']}")
    w(f"- forge tag references kept (typed, no c: tag of that registry type in mods/): {stats['forge_refs_kept']}")
    w(f"- forge tag references left untyped (mcfunction or no registry key): {stats['forge_refs_untyped']}")
    w(f"- Jars scanned in mods/: {n_jars}; c tags found: {stats['c_tags_found']}")
    w(f"- OLD JSON that failed to parse (copied as is): {stats['old_parse_fail']}")
    w(f"- Output JSON files that parse with json.load: {json_ok} pass, {len(lists['output_parse_fail'])} fail")
    w(f"- Backups made of pre-existing target content: {', '.join(backups) if backups else 'none'}")
    if bad_jars:
        w(f"- Jars that could not be read: {', '.join(bad_jars)}")
    w("")
    w(f"## nbt dropped ({len(lists['nbt_dropped'])} recipe files)")
    w("")
    w("Recipe result `nbt` removed, not converted to components. Recipe kept.")
    w("")
    for x in lists["nbt_dropped"]:
        w(f"- {x}")
    w("")
    w(f"## set_nbt ({len(lists['set_nbt'])} files, function left as is)")
    w("")
    for x in lists["set_nbt"]:
        w(f"- {x}")
    w("")
    w(f"## forge tags without c: equivalent ({len(U)} unique typed, kept as forge:)")
    w("")
    for typ, x in sorted(U):
        w(f"- {typ}: forge:{x} ({U[(typ, x)]} refs)")
    w("")
    w(f"## forge refs left untyped ({len(UNTYPED)} unique, kept as forge:)")
    w("")
    for _, x in sorted(UNTYPED):
        w(f"- forge:{x} ({UNTYPED[(None, x)]} refs)")
    w("")
    w(f"## Unknown namespaces in output JSON ({len(unk_files)} namespaces, not in tools/modcheck/modids.txt)")
    w("")
    w("Not deleted, only reported. Our own data namespaces and `forge` are excluded. Full file lists: `unknown_namespaces.json`.")
    w("")
    w("| namespace | refs | files | examples |")
    w("| --- | ---: | ---: | --- |")
    for ns in sorted(unk_files, key=lambda n: (-unk_refs[n], n)):
        ex = ", ".join(f"`{f}`" for f in unk_files[ns][:3])
        w(f"| {ns} | {unk_refs[ns]} | {len(unk_files[ns])} | {ex} |")
    w("")
    UNK_JSON.write_text(json.dumps({ns: {"refs": unk_refs[ns], "files": unk_files[ns]}
                                    for ns in sorted(unk_files)}, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    w(f"## Dropped mods (declared in OLD mods/, absent from NEW modids.txt; own data namespaces excluded) ({len(DROPPED)})")
    w("")
    w(", ".join(f"`{x}`" for x in sorted(DROPPED)))
    w("")
    w("## Pruned references to dropped mods")
    w("")
    w(f"- Tag entries removed: {stats['tag_entries_removed']}")
    w(f"- Recipe files deleted: {stats['recipes_deleted']}")
    w(f"- Loot pool entries removed: {stats['loot_entries_removed']}")
    w(f"- Loot pools removed (left empty): {stats['loot_pools_removed']}")
    w(f"- Advancement files deleted: {stats['advancements_deleted']}")
    w("")
    w(f"## Other JSON still referencing dropped mods, not edited ({len(OTHER)})")
    w("")
    for x in OTHER:
        w(f"- {x}")
    w("")
    w(f"## OLD JSON that failed to parse ({len(lists['parse_fail_old'])})")
    w("")
    for x in lists["parse_fail_old"]:
        w(f"- {x}")
    w("")
    w(f"## Output JSON that failed to parse ({len(lists['output_parse_fail'])})")
    w("")
    for x in lists["output_parse_fail"]:
        w(f"- {x}")
    w("")
    w(f"## Collisions skipped ({len(lists['collision'])})")
    w("")
    for x in lists["collision"]:
        w(f"- {x}")
    w("")
    REPORT.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
