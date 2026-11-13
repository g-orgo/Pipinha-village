"""Report unknown item/block ids in pack-owned loot tables.

Scans moonlight-global-datapacks/sunlit_towns/data/sunlit/loot_table/**
and kubejs/data/*/loot_table/**. Tag entries are skipped.
"""

import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lc_ids

ROOT = lc_ids.ROOT
PATTERNS = [
    os.path.join(ROOT, "moonlight-global-datapacks", "sunlit_towns", "data", "sunlit", "loot_table", "**", "*.json"),
    os.path.join(ROOT, "kubejs", "data", "*", "loot_table", "**", "*.json"),
]
KEYS = ("name", "id", "item", "block", "type")


def walk(node, items, counts):
    if isinstance(node, dict):
        ntype = node.get("type") if isinstance(node.get("type"), str) else ""
        table_ref = ntype in ("minecraft:loot_table", "loot_table", "aquaculture:neptunes_bounty")
        pool_node = "rolls" in node or "entries" in node
        func = node.get("function") if isinstance(node.get("function"), str) else ""
        for k, v in node.items():
            if k in KEYS and isinstance(v, str) and ":" in v and not v.startswith("#"):
                if k == "type":
                    continue
                if table_ref and k == "name":
                    continue
                if ntype == "minecraft:tag" and k == "name":
                    continue
                if pool_node and k == "name":
                    continue
                if func == "minecraft:set_potion" and k == "id":
                    continue
                if k in ("name", "item", "block") or k == "id":
                    base = v.split("[")[0]
                    if base not in items:
                        counts[base] += 1
            elif isinstance(v, (dict, list)):
                walk(v, items, counts)
    elif isinstance(node, list):
        for v in node:
            if isinstance(v, (dict, list)):
                walk(v, items, counts)


def main():
    _, items = lc_ids.scan_known_ids()
    counts = Counter()
    bad_files = 0
    parse_errors = 0
    files = []
    for pat in PATTERNS:
        files.extend(glob.glob(pat, recursive=True))
    files = sorted(set(files))
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            parse_errors += 1
            print("parse error: %s: %s" % (os.path.relpath(path, ROOT), exc))
            continue
        local = Counter()
        walk(data, items, local)
        if local:
            bad_files += 1
            for base, n in local.items():
                counts[base] += n
    print("files scanned: %d" % len(files))
    print("%d unknown ids" % sum(counts.values()))
    print("%d files with unknown ids" % bad_files)
    print("%d parse errors" % parse_errors)
    for base, n in counts.most_common():
        print("  %s x%d" % (base, n))


if __name__ == "__main__":
    main()
