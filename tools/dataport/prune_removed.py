#!/usr/bin/env python3
"""Prune references to mods that left the pack from kubejs/data JSON files.

Removal is done on the raw text, so the formatting of each file (indent,
inline objects, line endings) is kept; only the entries that use a removed
id are cut out.

Rules:
- Array element: removed when any string inside it uses a removed id
  (shop trades, bounty/biome/loot entries, tag values, string lists).
- Object member: removed when its key uses a removed id (chiselling and
  hammering maps).
- Object member by value: only under kubejs/data/bountiful (entries nested
  below the root object), where each entry is a named object.
- Whole files: the prefixes and files listed in DELETE_* are removed.
- Lost Cities palettes/buildings and sunlit_towns paths are skipped.

Usage:
  python3 tools/dataport/prune_removed.py --dry-run
  python3 tools/dataport/prune_removed.py
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "kubejs", "data")

REMOVED = [
    "splendid_slimes", "splendid_cogs", "farmlife",
    "hamsters", "legendarycreatures", "liltractor", "croptania", "cfm",
    "redeco", "itemfilters", "refinedstorageaddons", "gensokyo",
]
_ALT = "|".join(REMOVED)
# "ns:" as an id, or "/ns/" as a path segment (everycomp:fs/botania/...)
USES_RE = re.compile(r"(?<![A-Za-z0-9_])(?:%s):|(?<=/)(?:%s)/" % (_ALT, _ALT))

SKIP_PARTS = ("lostcities", "sunlit_towns")

DELETE_PREFIXES = [
    "kubejs/data/croptania/",
    "kubejs/data/cozycafe/menu/farmlife/",
]
DELETE_FILES = [
    "kubejs/data/trofers/trofers/slimes.json",
]

DEC = json.JSONDecoder()
WS = " \t\r\n"


class Item:
    __slots__ = ("key", "kstart", "vend", "value", "child")

    def __init__(self, key, kstart, vend, value, child):
        self.key = key
        self.kstart = kstart
        self.vend = vend
        self.value = value
        self.child = child


class Container:
    __slots__ = ("kind", "open", "close", "items")

    def __init__(self, kind, opn, close, items):
        self.kind = kind
        self.open = opn
        self.close = close
        self.items = items


def skip(s, i):
    while i < len(s) and s[i] in WS:
        i += 1
    return i


def parse(s, i):
    """Return (container_or_None, end_index) for the value starting at i."""
    i = skip(s, i)
    c = s[i]
    if c not in "{[":
        _, end = DEC.raw_decode(s, i)
        return None, end
    close_ch = "}" if c == "{" else "]"
    opn = i
    i = skip(s, i + 1)
    items = []
    if s[i] == close_ch:
        return Container(c, opn, i, items), i + 1
    while True:
        i = skip(s, i)
        kstart = i
        key = None
        if c == "{":
            key, i = DEC.raw_decode(s, i)
            i = skip(s, i)
            if s[i] != ":":
                raise ValueError("expected ':' at %d" % i)
            i = skip(s, i + 1)
        else:
            kstart = i
        child, i = parse(s, i)
        items.append(Item(key, kstart, i, json.loads(s[kstart:i]) if c == "[" else None, child))
        # value for objects is recomputed below from the member value span
        i = skip(s, i)
        if s[i] == ",":
            i = i + 1
            continue
        if s[i] == close_ch:
            return Container(c, opn, i, items), i + 1
        raise ValueError("unexpected char %r at %d" % (s[i], i))


def fix_values(s, c):
    """Set Item.value to the decoded member value (objects store the value span start)."""
    for it in c.items:
        if c.kind == "{":
            # value span starts after the colon; recover by decoding from the key end
            j = it.kstart
            _, j = DEC.raw_decode(s, j)
            j = skip(s, j)
            j = skip(s, j + 1)
            it.value = json.loads(s[j:it.vend])
        if it.child is not None:
            fix_values(s, it.child)


def uses(v):
    if isinstance(v, str):
        return USES_RE.search(v) is not None
    if isinstance(v, dict):
        return any(uses(x) for x in v.values())
    if isinstance(v, list):
        return any(uses(x) for x in v)
    return False


def ranges_for(c, flags, s):
    n = len(c.items)
    if n == 0 or not any(flags):
        return []
    if all(flags):
        return [(c.open + 1, c.close)]
    t = n
    while t > 0 and flags[t - 1]:
        t -= 1
    out = []
    for i in range(n):
        if flags[i] and i < t:
            out.append((c.items[i].kstart, c.items[i + 1].kstart))
    if t < n:
        out.append((c.items[t - 1].vend, c.items[n - 1].vend))
    return out


def collect(s, c, path, value_mode, out, log):
    flags = []
    for it in c.items:
        removed = False
        if c.kind == "[":
            removed = uses(it.value)
        else:
            if it.key is not None and USES_RE.search(it.key):
                removed = True
            elif value_mode and len(path) >= 1 and uses(it.value):
                removed = True
        flags.append(removed)
    out.extend(ranges_for(c, flags, s))
    for idx, it in enumerate(c.items):
        label = it.key if c.kind == "{" else idx
        if flags[idx]:
            log.append((path + [label], it.value))
            continue
        if it.child is not None:
            collect(s, it.child, path + [label], value_mode, out, log)


def process_file(full, rel, dry, stats, log_lines):
    with open(full, encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        json.loads(text)
    except ValueError:
        log_lines.append("SKIP (not JSON): %s" % rel)
        return
    root, _ = parse(text, 0)
    if root is None:
        return
    fix_values(text, root)
    value_mode = rel.startswith("kubejs/data/bountiful/")
    ranges, log = [], []
    collect(text, root, [], value_mode, ranges, log)
    if not ranges:
        return
    new = text
    for a, b in sorted(ranges, reverse=True):
        new = new[:a] + new[b:]
    json.loads(new)  # must still parse
    folder = rel.split("/")[2]
    stats.setdefault(folder, [0, 0, 0])
    stats[folder][0] += 1
    stats[folder][2] += len(log)
    for path, val in log:
        preview = json.dumps(val, ensure_ascii=False)
        if len(preview) > 90:
            preview = preview[:90] + "..."
        log_lines.append("  %s :: %s -> %s" % (rel, "/".join(str(p) for p in path), preview))
    if not dry:
        with open(full, "w", encoding="utf-8", newline="") as f:
            f.write(new)


def main():
    dry = "--dry-run" in sys.argv
    stats, log_lines, deleted = {}, [], []
    for dirpath, _, files in os.walk(DATA):
        for name in files:
            if not name.endswith(".json"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            if any(p in rel for p in SKIP_PARTS):
                continue
            if rel in DELETE_FILES or any(rel.startswith(p) for p in DELETE_PREFIXES):
                deleted.append(rel)
                if not dry:
                    os.remove(full)
                continue
            process_file(full, rel, dry, stats, log_lines)
    if not dry:
        for p in DELETE_PREFIXES:
            d = os.path.join(ROOT, p.rstrip("/"))
            if os.path.isdir(d):
                for dirpath, _, _ in sorted(os.walk(d), key=lambda w: len(w[0]), reverse=True):
                    if not os.listdir(dirpath):
                        os.rmdir(dirpath)
    for line in log_lines:
        print(line)
    print("--- edited per folder: files / removals")
    for k in sorted(stats):
        print("%s: %d files, %d removals" % (k, stats[k][0], stats[k][2]))
    print("--- deleted files: %d" % len(deleted))
    for d in deleted:
        print("  " + d)


if __name__ == "__main__":
    main()
