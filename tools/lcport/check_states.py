"""Check (and optionally fix) block states and block entity NBT in Lost Cities palettes.

check_palettes.py only checks block ids. This script also checks:
  - properties: a property the 1.20.1 blockstate had and the 1.21.1 one lost is invalid
    (the game rejects the whole state); a value outside the 1.21.1 variants is invalid.
    Properties absent from both blockstates (non-visual, e.g. waterlogged) are only counted.
  - block entity "tag": item stacks still in 1.20 format ("Count", "tag"), unknown item ids,
    block entity ids of namespaces that are no longer installed.

Usage: python3 check_states.py [--fix]
--fix drops invalid properties (the block keeps its default value), converts item stacks to
the 1.21 format (count, no empty tag), drops items with unknown ids and drops tags whose block
entity namespace is gone. Idempotent; file formatting is kept like port_palettes.py does.
"""

import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lc_ids
import port_palettes

ROOT = lc_ids.ROOT
OLD_INSTANCE = os.path.join(os.path.dirname(ROOT), "Society: Sunlit Valley")
OLD_VANILLA = os.path.join(os.path.dirname(lc_ids.VANILLA_JAR), "..", "1.20.1", "1.20.1.jar")
PATTERN = os.path.join(ROOT, "moonlight-global-datapacks", "*", "data", "*", "lostcities", "palettes", "**", "*.json")


def old_props():
    """{block_id: set(prop names)} from the 1.20.1 jars (read only)."""
    saved = (lc_ids.MODS, lc_ids.VANILLA_JAR, lc_ids.KUBEJS_ASSETS)
    lc_ids.MODS = os.path.join(OLD_INSTANCE, "mods")
    lc_ids.VANILLA_JAR = os.path.normpath(OLD_VANILLA)
    lc_ids.KUBEJS_ASSETS = os.path.join(OLD_INSTANCE, "kubejs", "assets")
    out = {}
    try:
        for rel, raw in lc_ids._iter_blockstate_blobs():
            parts = rel.split("/")
            key = parts[1] + ":" + parts[-1][:-5]
            if key not in out:
                try:
                    out[key] = lc_ids.collect_state_keys(json.loads(raw.decode("utf-8")), set())
                except Exception:
                    out[key] = set()
    finally:
        lc_ids.MODS, lc_ids.VANILLA_JAR, lc_ids.KUBEJS_ASSETS = saved
    return out


class Checker:
    def __init__(self, fix):
        self.fix = fix
        self.blocks, self.items = lc_ids.scan_known_ids()
        self.namespaces = {b.split(":")[0] for b in self.blocks}
        self.old = old_props()
        self.stats = Counter()
        self.bad = Counter()

    def state(self, value):
        base = value.split("[")[0]
        props = port_palettes.parse_props(value)
        if base not in self.blocks:
            self.bad["unknown block " + base] += 1
            return value
        accepted = lc_ids.accepted_states(base) or {}
        keep = []
        for k, v in props:
            if k in accepted:
                allowed = accepted[k]
                if allowed is not None and v not in allowed:
                    self.bad["bad value %s[%s=%s]" % (base, k, v)] += 1
                    continue
            elif k in self.old.get(base, set()):
                self.bad["removed prop %s[%s]" % (base, k)] += 1
                continue
            else:
                self.stats["unverifiable prop %s" % k] += 1
            keep.append((k, v))
        return port_palettes.render(base, keep) if len(keep) != len(props) else value

    def tag(self, tag):
        """Return the fixed tag, or None to drop it."""
        be = tag.get("id", "")
        if ":" in be and be.split(":")[0] not in self.namespaces:
            self.bad["block entity of removed mod " + be] += 1
            return None
        for key, val in list(tag.items()):
            if not isinstance(val, list):
                continue
            kept = []
            for it in val:
                if not (isinstance(it, dict) and "id" in it):
                    kept.append(it)
                    continue
                if it["id"] not in self.items and it["id"] not in self.blocks:
                    self.bad["unknown item " + it["id"]] += 1
                    continue
                if "Count" in it:
                    self.bad["item stack in 1.20 format (Count)"] += 1
                    it["count"] = it.pop("Count")
                if it.get("tag") == {}:
                    del it["tag"]
                elif "tag" in it:
                    self.bad["item with 1.20 nbt tag " + it["id"]] += 1
                kept.append(it)
            tag[key] = kept
        return tag

    def walk(self, node):
        if isinstance(node, dict):
            if isinstance(node.get("block"), str):
                node["block"] = self.state(node["block"])
            if isinstance(node.get("tag"), dict):
                fixed = self.tag(node["tag"])
                if fixed is None:
                    del node["tag"]
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    self.walk(v)
        elif isinstance(node, list):
            for v in node:
                self.walk(v)


def dump(raw, data):
    indent = None
    if raw.startswith("{\n\t") or raw.startswith("[\n\t"):
        indent = "\t"
    elif raw.startswith("{\n  ") or raw.startswith("[\n  "):
        indent = "  "
    if indent is None and "\n" not in raw:
        out = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    else:
        out = json.dumps(data, indent=indent, ensure_ascii=True)
    return out + "\n" if raw.endswith("\n") else out


def main():
    fix = "--fix" in sys.argv
    chk = Checker(fix)
    files = sorted(glob.glob(PATTERN, recursive=True))
    changed = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        data = json.loads(raw)
        before = json.dumps(data, sort_keys=True)
        chk.walk(data)
        if json.dumps(data, sort_keys=True) != before:
            changed += 1
            if fix:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(dump(raw, data))
    print("palette files scanned: %d" % len(files))
    print("files %s: %d" % ("changed" if fix else "needing a fix", changed))
    print("problems: %d" % sum(chk.bad.values()))
    for k, n in sorted(chk.bad.items()):
        print("  %s x%d" % (k, n))
    print("unverifiable properties (absent from both blockstates, kept):")
    for k, n in chk.stats.most_common(12):
        print("  %s x%d" % (k, n))


if __name__ == "__main__":
    main()
