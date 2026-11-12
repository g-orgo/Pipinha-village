#!/usr/bin/env python3
"""Port the worldgen and dimension data of the data packs to Minecraft 1.21.1.

Run with: python3 -I tools/dataport/port_worldgen.py [--dry-run]

Sources: kubejs/data, moonlight-global-datapacks and datapacks (folders).
Idempotent: a second run changes nothing. Only files whose content changes
are written. JSON is written with 2-space indentation.

Fixes:
1. Provider objects (uniform, biased_to_bottom, clamped, clamped_normal,
   trapezoid, weighted_list) lose the nested "value" wrapper used before 1.20.5.
   Constant providers are left alone.
2. "offset" vectors with a component whose absolute value is 16 or more
   (1.21.1 limit) are clamped to +/-15, keeping the sign.
3. The block id "minecraft:grass" is renamed to "minecraft:short_grass" in
   every data JSON (exact value match, tags are not touched).
4. The trials structures (kubejs/data/trials/worldgen) and the whole
   rainbowoaks data folder are deleted. Every mod namespace in REMOVED_CANDIDATES
   that has no mod in tools/modcheck/modids.txt is pruned from worldgen and
   dimension JSON and tag JSON: list strings, list objects with a removed reference and
   object keys naming a removed id are dropped.
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DRY = "--dry-run" in sys.argv

SOURCES = [ROOT / "kubejs" / "data", ROOT / "moonlight-global-datapacks", ROOT / "datapacks"]
MODIDS_FILE = ROOT / "tools" / "modcheck" / "modids.txt"
DELETE_DIRS = [ROOT / "kubejs" / "data" / "trials" / "worldgen",
               ROOT / "kubejs" / "data" / "rainbowoaks"]
REMOVED_CANDIDATES = ["trials", "rainbowoaks", "species", "hamsters", "legendarycreatures",
                      "farmlife", "splendid_slimes", "moreminecarts"]
PROVIDERS = {"uniform", "biased_to_bottom", "clamped", "clamped_normal", "trapezoid", "weighted_list"}
SCOPE_DIRS = {"worldgen", "dimension", "dimension_type", "tags"}
OFFSET_LIMIT = 15

installed = {line.strip() for line in MODIDS_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}
REMOVED = {ns for ns in REMOVED_CANDIDATES if ns not in installed}
fixes = Counter()          # files changed per fix type
files_fixed = Counter()    # per fix type, set of file paths
changed_paths = {}
errors = []


def mark(kind, path):
    files_fixed[kind] += 1
    changed_paths.setdefault(path, set()).add(kind)


def fix_providers(node, path):
    """Flatten {"type": provider, "value": {...}} into {"type": provider, ...}."""
    if isinstance(node, list):
        return [fix_providers(x, path) for x in node]
    if not isinstance(node, dict):
        return node
    node = {k: fix_providers(v, path) for k, v in node.items()}
    t = node.get("type")
    v = node.get("value")
    if isinstance(t, str) and t.removeprefix("minecraft:") in PROVIDERS and isinstance(v, dict):
        if "type" in v:
            errors.append(f"{path}: provider value has its own type, skipped")
            return node
        out = {"type": t}
        out.update(v)
        for k, val in node.items():
            if k not in ("type", "value"):
                out[k] = val
        mark("provider_flatten", path)
        return out
    return node


def clamp_offsets(node, path):
    if isinstance(node, list):
        return [clamp_offsets(x, path) for x in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for k, v in node.items():
        if (k == "offset" and isinstance(v, list) and len(v) == 3
                and all(isinstance(x, int) and not isinstance(x, bool) for x in v)
                and any(abs(x) > OFFSET_LIMIT for x in v)):
            out[k] = [max(-OFFSET_LIMIT, min(OFFSET_LIMIT, x)) for x in v]
            mark("offset_clamp", path)
        else:
            out[k] = clamp_offsets(v, path)
    return out


def is_removed_ref(s):
    if not isinstance(s, str):
        return False
    body = s[1:] if s.startswith("#") else s
    return ":" in body and body.split(":", 1)[0] in REMOVED


def has_removed_ref(o):
    if isinstance(o, str):
        return is_removed_ref(o)
    if isinstance(o, dict):
        return any(has_removed_ref(v) for v in o.values())
    if isinstance(o, list):
        return any(has_removed_ref(v) for v in o)
    return False


def prune(node, path):
    if isinstance(node, list):
        out = []
        for el in node:
            if isinstance(el, str) and is_removed_ref(el):
                mark("prune_removed_ref", path)
                continue
            if isinstance(el, dict) and has_removed_ref(el):
                mark("prune_removed_ref", path)
                continue
            out.append(prune(el, path))
        return out
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if is_removed_ref(k):
                mark("prune_removed_ref", path)
                continue
            out[k] = prune(v, path)
        return out
    return node


def in_scope(rel):
    return any(part in SCOPE_DIRS for part in rel.parts[:-1])


def write_json(p, obj):
    if not DRY:
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    print(f"removed namespaces (no mod installed): {sorted(REMOVED)}")
    # Fix 4a: delete folders
    deleted = 0
    for d in DELETE_DIRS:
        if d.exists():
            files = [f for f in d.rglob("*") if f.is_file()]
            deleted += len(files)
            print(f"delete folder {d.relative_to(ROOT)} ({len(files)} files)")
            if not DRY:
                shutil.rmtree(d)
    fixes["delete_folder_files"] = deleted

    nonstandard = 0
    for src in SOURCES:
        if not src.exists():
            continue
        for p in sorted(src.rglob("*.json")):
            path = str(p.relative_to(ROOT))
            raw = p.read_text(encoding="utf-8")
            text = raw
            # Fix 3: grass id, all data JSON
            if "minecraft:grass" in text:
                text = text.replace('"minecraft:grass"', '"minecraft:short_grass"')
                if text != raw:
                    mark("grass_rename", path)
            rel = p.relative_to(ROOT)
            if in_scope(rel):
                try:
                    obj = json.loads(text)
                except json.JSONDecodeError as e:
                    errors.append(f"{path}: invalid JSON before port ({e})")
                    continue
                before = json.dumps(obj, sort_keys=False)
                obj = fix_providers(obj, path)
                obj = clamp_offsets(obj, path)
                obj = prune(obj, path)
                if json.dumps(obj, sort_keys=False) != before:
                    if raw != json.dumps(json.loads(raw), indent=2, ensure_ascii=False) + "\n":
                        nonstandard += 1
                    if not DRY:
                        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    text = None
            if text is not None and text != raw and not DRY:
                p.write_text(text, encoding="utf-8")

    # Validation: every changed JSON parses
    bad = []
    if not DRY:
        for path in changed_paths:
            try:
                json.loads((ROOT / path).read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                bad.append(f"{path}: {e}")

    print("files changed per fix type:")
    for kind in ["provider_flatten", "offset_clamp", "grass_rename", "prune_removed_ref"]:
        n = sum(1 for kinds in changed_paths.values() if kind in kinds)
        print(f"  {kind}: {n}")
    print(f"  delete_folder_files: {deleted}")
    print(f"changed files total: {len(changed_paths)}")
    print(f"changed files with non-2-space source formatting: {nonstandard}")
    print(f"parse failures after write: {len(bad)}")
    for b in bad[:20]:
        print("  " + b)
    for e in errors[:20]:
        print("  note: " + e)
    print("dry run" if DRY else "written")


if __name__ == "__main__":
    main()
