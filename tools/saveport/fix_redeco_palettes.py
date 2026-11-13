"""Re-point palette values that came from Re:Deco blocks to their Redecorate targets.

The 1.21.1 palettes already had their redeco ids replaced by the old targets.
This walks the 1.20.1 palette next to each 1.21.1 palette in parallel. Wherever
the 1.20.1 "block" value is a redeco id, the 1.21.1 value is recomputed from the
original 1.20.1 value with the current block_map.tsv. Other values are not touched.

Usage: python3 fix_redeco_palettes.py [--dry-run]
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


def walk_pair(old, new, mapping, out):
    """Collect (path, new_value) for redeco blocks; old and new share structure."""
    if isinstance(old, dict) and isinstance(new, dict):
        for k, ov in old.items():
            if k not in new:
                continue
            if k == "block" and isinstance(ov, str) and ov.split("[")[0].startswith("redeco:"):
                if ov.split("[")[0] in mapping and isinstance(new[k], str):
                    value, _ = pp.transform(ov, mapping)
                    if value != new[k]:
                        new[k] = value
                        out.append(value)
                else:
                    out.append(None)  # redeco id without a mapping
            elif isinstance(ov, (dict, list)):
                walk_pair(ov, new[k], mapping, out)
    elif isinstance(old, list) and isinstance(new, list):
        for ov, nv in zip(old, new):
            if isinstance(ov, (dict, list)):
                walk_pair(ov, nv, mapping, out)


def main():
    dry = "--dry-run" in sys.argv
    mapping = pp.load_map()
    files = 0
    changed_files = 0
    values = 0
    unmapped = 0
    for old_path in sorted(glob.glob(os.path.join(OLD_ROOT, REL), recursive=True)):
        with open(old_path, encoding="utf-8") as fh:
            raw_old = fh.read()
        if "redeco:" not in raw_old:
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
        walk_pair(old, new, mapping, out)
        unmapped += out.count(None)
        applied = [v for v in out if v is not None]
        if not applied:
            continue
        values += len(applied)
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
    print("files with redeco: %d, files changed: %d, values set: %d, redeco without mapping: %d"
          % (files, changed_files, values, unmapped))


if __name__ == "__main__":
    main()
