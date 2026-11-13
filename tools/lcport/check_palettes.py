"""Report Lost Cities palette/part files that still use unknown block ids."""

import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lc_ids

ROOT = lc_ids.ROOT
PATTERN = os.path.join(ROOT, "moonlight-global-datapacks", "*", "data", "*", "lostcities", "**", "*.json")


def walk(node, unknown, counts):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "block" and isinstance(v, str):
                base = v.split("[")[0]
                if base not in unknown:
                    counts[base] += 1
            elif isinstance(v, (dict, list)):
                walk(v, unknown, counts)
    elif isinstance(node, list):
        for v in node:
            if isinstance(v, (dict, list)):
                walk(v, unknown, counts)


def main():
    blocks, _ = lc_ids.scan_known_ids()
    counts = Counter()
    bad_files = 0
    parse_errors = 0
    files = sorted(glob.glob(PATTERN, recursive=True))
    for path in files:
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as exc:
            parse_errors += 1
            print("parse error: %s: %s" % (os.path.relpath(path, ROOT), exc))
            continue
        local = Counter()
        walk(data, blocks, local)
        if local:
            bad_files += 1
            for base, n in local.items():
                counts[base] += n
    print("files scanned: %d" % len(files))
    print("%d palettes with unknown blocks" % bad_files)
    print("%d parse errors" % parse_errors)
    for base, n in counts.most_common():
        print("  %s x%d" % (base, n))


if __name__ == "__main__":
    main()
