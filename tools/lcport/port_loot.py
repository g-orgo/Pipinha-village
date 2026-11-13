"""Rewrite unknown item/block ids in pack-owned loot tables.

Uses loot_map.tsv. Unknown ids with no mapping are dropped together with their
entry; a pool left without entries is removed. Idempotent.
"""

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lc_ids

ROOT = lc_ids.ROOT
MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loot_map.tsv")
PATTERNS = [
    os.path.join(ROOT, "moonlight-global-datapacks", "sunlit_towns", "data", "sunlit", "loot_table", "**", "*.json"),
    os.path.join(ROOT, "kubejs", "data", "*", "loot_table", "**", "*.json"),
]
KEYS = ("name", "id", "item", "block")


def load_map():
    out = {}
    with open(MAP_PATH, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            old, new = line.split("\t")
            out[old] = new
    return out


class Stats:
    def __init__(self):
        self.replaced = 0
        self.dropped = 0
        self.pools_removed = 0
        self.changed = 0


def fix_entry(node, mapping, items, stats):
    """Return replacement value or None when the entry must be dropped."""
    base = node.split("[")[0]
    if base in items:
        return node
    if base in mapping:
        stats.replaced += 1
        return mapping[base]
    return None


def walk(node, mapping, items, stats):
    changed = False
    if isinstance(node, dict):
        ntype = node.get("type") if isinstance(node.get("type"), str) else ""
        table_ref = ntype in ("minecraft:loot_table", "loot_table", "aquaculture:neptunes_bounty")
        pool_node = "rolls" in node or "entries" in node
        func = node.get("function") if isinstance(node.get("function"), str) else ""
        for k, v in list(node.items()):
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
                new = fix_entry(v, mapping, items, stats)
                if new is None:
                    node["__drop__"] = True
                elif new != v:
                    node[k] = new
                    changed = True
            elif isinstance(v, (dict, list)):
                if walk(v, mapping, items, stats):
                    changed = True
        return changed
    if isinstance(node, list):
        is_entries = False
        keep = []
        for v in node:
            if isinstance(v, (dict, list)):
                if walk(v, mapping, items, stats):
                    changed = True
                if isinstance(v, dict) and v.pop("__drop__", False):
                    stats.dropped += 1
                    changed = True
                    continue
            keep.append(v)
        if keep != node:
            node[:] = keep
            changed = True
        return changed
    return False


def main():
    mapping = load_map()
    _, items = lc_ids.scan_known_ids()
    stats = Stats()
    files = []
    for pat in PATTERNS:
        files.extend(glob.glob(pat, recursive=True))
    files = sorted(set(files))
    for path in files:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        try:
            data = json.loads(raw)
        except Exception as exc:
            print("parse error: %s: %s" % (os.path.relpath(path, ROOT), exc))
            continue
        if not walk(data, mapping, items, stats):
            continue
        # remove pools that lost every entry
        pools = data.get("pools") if isinstance(data, dict) else None
        if isinstance(pools, list):
            kept = [p for p in pools if not (isinstance(p, dict) and isinstance(p.get("entries"), list) and not p["entries"])]
            if len(kept) != len(pools):
                stats.pools_removed += len(pools) - len(kept)
                data["pools"] = kept
        if raw.startswith("{\n\t") or raw.startswith("[\n\t"):
            out = json.dumps(data, indent="\t", ensure_ascii=True)
        elif raw.startswith("{\n  ") or raw.startswith("[\n  "):
            out = json.dumps(data, indent=2, ensure_ascii=True)
        elif "\n" not in raw:
            sep = (", ", ": ") if ": " in raw else (",", ":")
            out = json.dumps(data, ensure_ascii=True, separators=sep)
        else:
            out = json.dumps(data, ensure_ascii=True)
        if raw.endswith("\n"):
            out += "\n"
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
        stats.changed += 1
    print("files changed: %d" % stats.changed)
    print("entries replaced: %d" % stats.replaced)
    print("entries dropped: %d" % stats.dropped)
    print("pools removed: %d" % stats.pools_removed)


if __name__ == "__main__":
    main()
