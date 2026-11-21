"""Rewrite Lost Cities palette/part "block" values using block_map.tsv.

Idempotent: a second run reports nothing changed. Formatting style of each
file (compact or indented, ensure_ascii, trailing newline) is preserved.
"""

import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saveport"))
import lc_ids
import state_rules

ROOT = lc_ids.ROOT
MAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "block_map.tsv")
PATTERN = os.path.join(ROOT, "moonlight-global-datapacks", "*", "data", "*", "lostcities", "**", "*.json")


def load_map():
    out = {}
    with open(MAP_PATH, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            old, new, rule = line.split("\t")
            base, _, props = new.partition("[")
            forced = []
            if props:
                for item in props.rstrip("]").split(","):
                    if item:
                        forced.append(tuple(item.split("=", 1)))
            out[old] = (base, forced, rule)
    return out


def parse_props(value):
    if "[" not in value:
        return []
    inner = value[value.index("[") + 1:value.rindex("]")]
    props = []
    for item in inner.split(","):
        if item:
            k, _, v = item.partition("=")
            props.append((k, v))
    return props


def render(new_id, props):
    if not props:
        return new_id
    return new_id + "[" + ",".join("%s=%s" % (k, v) for k, v in props) + "]"


def transform(value, mapping):
    base = value.split("[")[0]
    if base not in mapping:
        return value, None
    new_id, forced, rule = mapping[base]
    accepted = lc_ids.accepted_states(new_id)
    props = []
    pairs = parse_props(value)
    srule = state_rules.find(base, new_id)
    if srule:  # turn and reconnect furniture that changes mod (saveport/state_rules.tsv)
        pairs = list(state_rules.apply(srule, dict(pairs)).items())
    for k, v in pairs:
        if k == "upholstery" and new_id.startswith("redecorate:"):
            k = "fabric"  # Redecorate renamed Re:Deco's upholstery property
        if accepted is not None and k in accepted:
            allowed = accepted[k]
            if allowed is None or v in allowed:
                props.append((k, v))
    for item in forced:
        if item[0] not in [p[0] for p in props]:
            props.append(item)
    return render(new_id, props), rule


def walk(node, mapping, stats):
    changed = False
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k == "block" and isinstance(v, str):
                new, rule = transform(v, mapping)
                if new != v:
                    node[k] = new
                    stats[rule] += 1
                    changed = True
            elif isinstance(v, (dict, list)):
                if walk(v, mapping, stats):
                    changed = True
    elif isinstance(node, list):
        for v in node:
            if isinstance(v, (dict, list)):
                if walk(v, mapping, stats):
                    changed = True
    return changed


def main():
    mapping = load_map()
    stats = {"a": 0, "b": 0, "c": 0}
    files_changed = 0
    files = sorted(glob.glob(PATTERN, recursive=True))
    for path in files:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        try:
            data = json.loads(raw)
        except Exception as exc:
            print("parse error: %s: %s" % (path, exc))
            continue
        before = json.dumps(data, sort_keys=True)
        if not walk(data, mapping, stats):
            continue
        indent = None
        if raw.startswith("{\n\t") or raw.startswith("[\n\t"):
            indent = "\t"
        elif raw.startswith("{\n  ") or raw.startswith("[\n  "):
            indent = "  "
        if indent is None and "\n" not in raw:
            out = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
        else:
            out = json.dumps(data, indent=indent, ensure_ascii=True)
        if raw.endswith("\n"):
            out += "\n"
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
        files_changed += 1
    print("files changed: %d" % files_changed)
    print("substitutions: a=%d b=%d c=%d" % (stats["a"], stats["b"], stats["c"]))


if __name__ == "__main__":
    main()
