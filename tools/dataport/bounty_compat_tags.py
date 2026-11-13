#!/usr/bin/env python3
"""Convert bounty item objectives into item_tag objectives for compat groups.

Port of the 1.20.1 runtime script bountyCompatItems.js to pool data.

Every objective of type "minecraft:item" in
kubejs/data/bountiful/bounty_pools/**/*_objs.json whose content item belongs to
a sunlit:compat/<group> tag (kubejs/data/sunlit/tags/item/compat/<group>.json)
is switched to the Bountiful 8 item_tag format:

    "type": "item_tag", "content": "sunlit:compat/<group>"

The objective key (which Bountiful uses to find the icon), rarity, amount,
unitWorth and every other field are kept as they are. The script is
idempotent: converted objectives are no longer of type "minecraft:item".

Usage: python3 tools/dataport/bounty_compat_tags.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOLS_DIR = ROOT / "kubejs" / "data" / "bountiful" / "bounty_pools"
COMPAT_DIR = ROOT / "kubejs" / "data" / "sunlit" / "tags" / "item" / "compat"
COMPAT_PREFIX = "sunlit:compat/"
SOURCE_TYPE = "minecraft:item"
TARGET_TYPE = "item_tag"


def read_tag_values(path, seen):
    """Return the set of item ids of a tag file, resolving nested sunlit tags."""
    key = str(path)
    if key in seen:
        return seen[key]
    seen[key] = set()  # guards against cycles
    data = json.loads(path.read_text(encoding="utf-8"))
    items = set()
    for value in data.get("values", []):
        ref = value.get("id") if isinstance(value, dict) else value
        if not isinstance(ref, str):
            continue
        if ref.startswith("#"):
            name = ref[1:]
            if name.startswith(COMPAT_PREFIX):
                nested = COMPAT_DIR / (name[len(COMPAT_PREFIX):] + ".json")
                if nested.is_file():
                    items |= read_tag_values(nested, seen)
            continue
        items.add(ref)
    seen[key] = items
    return items


def load_groups():
    """Map each item id to the sorted list of compat groups that contain it."""
    seen = {}
    membership = {}
    for path in sorted(COMPAT_DIR.glob("*.json")):
        group = COMPAT_PREFIX + path.stem
        for item_id in read_tag_values(path, seen):
            membership.setdefault(item_id, []).append(group)
    return membership


def detect_indent(text):
    for line in text.splitlines():
        stripped = line.lstrip(" \t")
        if stripped and stripped != line:
            return "\t" if line.startswith("\t") else " " * (len(line) - len(stripped))
    return "\t"


def convert_file(path, membership):
    """Convert one pool file. Returns the number of converted objectives."""
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    content = data.get("content")
    if not isinstance(content, dict):
        return 0
    converted = 0
    for obj in content.values():
        if not isinstance(obj, dict) or obj.get("type") != SOURCE_TYPE:
            continue
        groups = membership.get(obj.get("content"))
        if not groups:
            continue
        obj["type"] = TARGET_TYPE
        obj["content"] = sorted(groups)[0]
        converted += 1
    if converted:
        indent = detect_indent(text)
        out = json.dumps(data, indent=indent, ensure_ascii=False)
        if text.endswith("\n"):
            out += "\n"
        path.write_text(out, encoding="utf-8")
    return converted


def main():
    if not COMPAT_DIR.is_dir():
        print(f"missing compat tag dir: {COMPAT_DIR}", file=sys.stderr)
        return 1
    membership = load_groups()
    total_files = 0
    total = 0
    for path in sorted(POOLS_DIR.rglob("*_objs.json")):
        count = convert_file(path, membership)
        if count:
            total_files += 1
            total += count
            print(f"{path.relative_to(ROOT)}: {count}")
    print(f"converted {total} objectives in {total_files} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
