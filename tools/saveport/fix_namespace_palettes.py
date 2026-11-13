"""Re-point palette values that came from a given mod namespace back to their 1.20.1 values.

Generalised copy of fix_redeco_palettes.py. The 1.21.1 palettes had the ids of a
missing mod replaced by substitutes. This walks the 1.20.1 palette next to each
1.21.1 palette in parallel. Wherever the 1.20.1 "block" value starts with the
given namespace, the 1.21.1 value is recomputed from the original 1.20.1 value
with the current block_map.tsv. Values from other namespaces are not touched.

Usage: python3 fix_namespace_palettes.py <namespace> [--dry-run]
Example: python3 fix_namespace_palettes.py youkaishomecoming --dry-run
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lcport"))
import lc_ids  # noqa: E402
import port_palettes as pp  # noqa: E402

NEW_ROOT = lc_ids.ROOT
OLD_ROOT = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley"
REL = os.path.join("moonlight-global-datapacks", "*", "data", "*", "lostcities", "**", "*.json")


def walk_pair(old, new, mapping, ns, out):
    """Collect values set for namespace blocks; old and new share structure."""
    if isinstance(old, dict) and isinstance(new, dict):
        for k, ov in old.items():
            if k not in new:
                continue
            if k == "block" and isinstance(ov, str) and ov.split("[")[0].startswith(ns + ":"):
                value, _ = pp.transform(ov, mapping)
                if value != new[k]:
                    new[k] = value
                    out.append(value)
            elif isinstance(ov, (dict, list)):
                walk_pair(ov, new[k], mapping, ns, out)
    elif isinstance(old, list) and isinstance(new, list):
        for ov, nv in zip(old, new):
            if isinstance(ov, (dict, list)):
                walk_pair(ov, nv, mapping, ns, out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print("usage: fix_namespace_palettes.py <namespace> [--dry-run]")
        sys.exit(2)
    ns = args[0]
    dry = "--dry-run" in sys.argv
    mapping = pp.load_map()
    files = 0
    changed_files = 0
    values = 0
    for old_path in sorted(glob.glob(os.path.join(OLD_ROOT, REL), recursive=True)):
        with open(old_path, encoding="utf-8") as fh:
            raw_old = fh.read()
        if ns + ":" not in raw_old:
            continue
        rel = os.path.relpath(old_path, OLD_ROOT)
        new_path = os.path.join(NEW_ROOT, rel)
        if not os.path.isfile(new_path):
            print("missing counterpart: %s" % rel)
            continue
        files += 1
        with open(new_path, encoding="utf-8") as fh:
            raw_new = fh.read()
        old = json.loads(raw_old)
        new = json.loads(raw_new)
        out = []
        walk_pair(old, new, mapping, ns, out)
        if not out:
            continue
        values += len(out)
        changed_files += 1
        if dry:
            continue
        indent = None
        if raw_new.startswith("{\n\t") or raw_new.startswith("[\n\t"):
            indent = "\t"
        elif raw_new.startswith("{\n  ") or raw_new.startswith("[\n  "):
            indent = "  "
        if indent is None and "\n" not in raw_new:
            text = json.dumps(new, ensure_ascii=True, separators=(",", ":"))
        else:
            text = json.dumps(new, indent=indent, ensure_ascii=True)
        if raw_new.endswith("\n"):
            text += "\n"
        with open(new_path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    print("namespace %s: files with namespace: %d, files changed: %d, values set: %d%s"
          % (ns, files, changed_files, values, " (dry run)" if dry else ""))


if __name__ == "__main__":
    main()
