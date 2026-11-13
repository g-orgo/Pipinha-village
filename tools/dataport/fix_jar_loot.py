#!/usr/bin/env python3
"""Fix loot tables that fail to parse on NeoForge 1.21.1.

Reads the failing loot table ids from logs/latest.log, finds each table inside
mods/*.jar and writes a 1.21 version to kubejs/data/<ns>/loot_table/<path>.json:

- Table whose block/item is not registered by any jar or KubeJS: an empty
  table with the original "type" (no pools), so the reload no longer fails.
- Registered table: the jar table converted from the 1.20 format.

Ids that already have a file in kubejs/data are skipped.
Run from the instance root, repeatable: python3 tools/dataport/fix_jar_loot.py
"""
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
LOG = ROOT / "logs" / "latest.log"
MODS = ROOT / "mods"
KJS_DATA = ROOT / "kubejs" / "data"

FAIL_RE = re.compile(r"Couldn't parse element ResourceKey\[minecraft:root / minecraft:loot_table\]:(\S+?) - ")


UNKNOWN_ITEM_RE = re.compile(r"Unknown registry key in minecraft:(item|block): '")


def failing_ids():
    """Return {id: error_text} for every loot table the log reports as unparsable."""
    errors = {}
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        m = FAIL_RE.search(line)
        if m:
            errors.setdefault(m.group(1), line)
    return errors


def index_jars():
    """Map each jar to its member names and collect the assets/loot tables."""
    jar_members = {}
    for jar in sorted(MODS.glob("*.jar")):
        with zipfile.ZipFile(jar) as z:
            jar_members[jar] = set(n for n in z.namelist() if n.startswith(("assets/", "data/")))
    return jar_members


def find_table_in_jars(jar_members, ns, path):
    member = f"data/{ns}/loot_table/{path}.json"
    for jar, names in jar_members.items():
        if member in names:
            return jar, member
    return None, None


def is_registered(error_line, path):
    """Registered means the game accepts the table's item/block at runtime.

    The log is the ground truth: an "Unknown registry key in minecraft:item/block" error for this
    table means the item is not registered (for example, railways tracks for absent mods). Jar
    assets are not used because a jar can ship models for items that only register when another
    mod is present. Entity tables (entities/...) are treated as registered, so a converted copy is
    preferred over an empty one.
    """
    if path.startswith("entities/"):
        return True
    return UNKNOWN_ITEM_RE.search(error_line) is None


def convert_1_20_to_1_21(node):
    """Convert a 1.20 loot table structure to the 1.21 format."""
    if isinstance(node, list):
        return [convert_1_20_to_1_21(x) for x in node]
    if not isinstance(node, dict):
        return node
    out = {}
    is_loot_table_entry = node.get("type") in ("loot_table", "minecraft:loot_table")
    is_looting = node.get("function") == "minecraft:looting_enchant"
    if is_looting:
        out["function"] = "minecraft:enchanted_count_increase"
        out["enchantment"] = "minecraft:looting"
        if "count" in node:
            out["count"] = convert_1_20_to_1_21(node["count"])
        if "limit" in node:
            out["limit"] = node["limit"]
        return out
    for key, value in node.items():
        if key == "name" and is_loot_table_entry:
            out["value"] = value
        elif key == "entity" and value == "killer":
            out["entity"] = "attacker"
        else:
            out[key] = convert_1_20_to_1_21(value)
    return out


def main():
    errors = failing_ids()
    jar_members = index_jars()
    stats = {"empty": 0, "converted": 0, "skipped_existing": 0, "not_in_jar": 0}
    report = []
    for full, error_line in sorted(errors.items()):
        ns, path = full.split(":", 1)
        target = KJS_DATA / ns / "loot_table" / f"{path}.json"
        if target.exists():
            stats["skipped_existing"] += 1
            continue
        jar, member = find_table_in_jars(jar_members, ns, path)
        if jar is None:
            stats["not_in_jar"] += 1
            report.append(f"NOT IN JAR: {full}")
            continue
        registered = is_registered(error_line, path)
        if registered:
            with zipfile.ZipFile(jar) as z:
                table = json.loads(z.read(member).decode("utf-8"))
            data = convert_1_20_to_1_21(table)
            stats["converted"] += 1
        else:
            with zipfile.ZipFile(jar) as z:
                original_type = json.loads(z.read(member).decode("utf-8")).get("type", "minecraft:block")
            data = {"type": original_type, "pools": []}
            stats["empty"] += 1
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(json.dumps(stats))
    for line in report:
        print(line)


if __name__ == "__main__":
    main()
