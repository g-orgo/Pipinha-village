#!/usr/bin/env python3
"""Port KubeJS 6 model, blockstate and block-entity tick builder calls to KubeJS 7.

Usage: python3 tools/kjsport/port_models.py [--dry-run] DIR [DIR ...]
DIR is relative to kubejs/startup_scripts (e.g. registration, powerfulMachines).
Sites that cannot be converted automatically are printed as MANUAL.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SS = ROOT / "kubejs" / "startup_scripts"
ASSETS = ROOT / "kubejs" / "assets"
RUNTIME = SS / "000_port_runtime.js"
TICKS = ROOT / "kubejs" / "server_scripts" / "zz_port_be_ticks.js"
TICKS_LINE = ('Object.keys(global.portBeTicks).forEach((id) => { '
              'BlockEvents.blockEntityTick(id, (e) => global.portBeTicks[id](e.entity)); });\n')

SOUND_MAP = {
    "botania:starcaller": "minecraft:block.amethyst_block.chime",
    "botania:gaia_trap": "minecraft:block.beacon.activate",
    "botania:mana_pool_craft": "minecraft:block.enchantment_table.use",
    "botania:virus_infect": "minecraft:entity.evoker.cast_spell",
    "botania:spreader_fire": "minecraft:entity.blaze.shoot",
}

DRY = "--dry-run" in sys.argv
DIRS = [a for a in sys.argv[1:] if not a.startswith("--")]
MANUAL = []
CHANGED = {"files": set(), "static": [], "static_overwritten": [], "static_same": 0,
           "blockstates": 0, "ticks": 0, "parent": 0, "generator": 0, "model_rename": 0,
           "statements_dropped": 0, "sounds": []}


def mask(text, keep_strings):
    """Return text with comments (and strings unless keep_strings) replaced by spaces."""
    out = list(text)
    n = len(text)

    def blank(a, b):
        for k in range(a, b):
            if out[k] != "\n":
                out[k] = " "

    i = 0
    while i < n:
        if text.startswith("//", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            blank(i, j)
            i = j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            blank(i, j)
            i = j
        elif text[i] in "\"'`":
            c = text[i]
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            j += 1
            if not keep_strings:
                blank(i, j)
            i = j
        else:
            i += 1
    return "".join(out)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def match_close(full, i):
    """Index of the bracket closing the one opened at i (full mask), or -1."""
    depth = 0
    for k in range(i, len(full)):
        c = full[k]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return k
    return -1


def split_args(full, open_i, close_i):
    args, depth, start = [], 0, open_i + 1
    for k in range(open_i + 1, close_i):
        c = full[k]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            args.append((start, k))
            start = k + 1
    if full[open_i + 1:close_i].strip():
        args.append((start, close_i))
    return args


def nearest_create(code, pos):
    found = None
    for m in re.finditer(r'\.create\(\s*"([a-z0-9_.-]+:[^"]+)"', code):
        if m.start() >= pos:
            break
        found = m.group(1)
    return found


def split_id(block_id):
    if not block_id or ":" not in block_id:
        return None, None
    ns, path = block_id.split(":", 1)
    return ns, path


HELPER_SRC = SS / "globalBlockEntityHandlers.js"


def helper_prelude():
    """Top-level blockstate helper consts (getCardinalMultipartJson*), copied as JS source."""
    if not HELPER_SRC.exists():
        return ""
    out, keep = [], False
    for line in HELPER_SRC.read_text(encoding="utf-8").splitlines():
        if re.match(r"const get\w*Multipart\w* = ", line):
            keep = True
        if keep:
            out.append(line)
            if line == "};":
                keep = False
    return "\n".join(out) + "\n"


PRELUDE = helper_prelude()


def eval_literal(expr):
    try:
        out = subprocess.run(
            ["node", "-e",
             "const vm=require('vm');const e=process.argv[1];const pre=process.argv[2];"
             "console.log(JSON.stringify(vm.runInNewContext(pre+';('+e+')',{},{timeout:1000})));",
             expr, PRELUDE],
            capture_output=True, text=True, timeout=20)
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
    if out.returncode != 0:
        return None, out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "eval failed"
    return json.loads(out.stdout), None


def write_asset(kind, ns, path, data, rel_label, file_rel):
    """kind is 'blockstates' or 'models/item' or 'models/block'. Returns True when written or same."""
    target = ASSETS / ns / kind / (path + ".json")
    body = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if target.exists():
        old = target.read_text(encoding="utf-8")
        if json.loads(old) == data:
            CHANGED["static_same"] += 1
            return True
        CHANGED["static_overwritten"].append(f"{rel_label} ({file_rel})")
    else:
        CHANGED["static"].append(f"{rel_label} ({file_rel})")
    if not DRY:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return True


def indent_of(text, pos):
    ls = text.rfind("\n", 0, pos) + 1
    m = re.match(r"[ \t]*", text[ls:pos])
    return m.group(0)


def convert_file(fpath):
    rel = fpath.relative_to(ROOT).as_posix()
    text = fpath.read_text(encoding="utf-8")
    code = mask(text, keep_strings=True)
    full = mask(text, keep_strings=False)
    edits = []  # (start, end, replacement)

    def manual(pos, why):
        MANUAL.append(f"{rel}:{line_of(text, pos)}: {why}")

    # 1. blockstateJson = {...}
    for m in re.finditer(r"\.blockstateJson\s*=\s*\{", full):
        s = m.start()
        open_i = m.end() - 1
        close_i = match_close(full, open_i)
        ns, path = split_id(nearest_create(code, s))
        if close_i < 0 or ns is None:
            manual(s, "blockstateJson: no block id or unbalanced braces")
            continue
        obj_text = text[open_i:close_i + 1]
        data, err = eval_literal(obj_text)
        if data is None:
            manual(s, f"blockstateJson: literal not static ({err})")
            continue
        write_asset("blockstates", ns, path, data, f"{ns}:{path}", rel)
        CHANGED["blockstates"] += 1
        edits.append((s, close_i + 1, ""))

    # 2. modelJson({...}) on items
    for m in re.finditer(r"\.modelJson\s*\(", full):
        s = m.start()
        open_i = m.end() - 1
        close_i = match_close(full, open_i)
        if close_i < 0:
            manual(s, "modelJson: unbalanced")
            continue
        args = split_args(full, open_i, close_i)
        if len(args) != 1:
            manual(s, "modelJson: unexpected argument count")
            continue
        a, b = args[0]
        data, err = eval_literal(text[a:b])
        if not isinstance(data, dict):
            manual(s, f"modelJson: literal not static ({err})")
            continue
        receiver = re.search(r"(\w+)\s*$", full[:s])
        recv = receiver.group(1) if receiver else None
        ns, path = split_id(nearest_create(code, s))
        keys = set(data.keys())
        if keys == {"parent"} and isinstance(data["parent"], str) and recv is not None:
            edits.append((s, close_i + 1, f".parentModel({json.dumps(data['parent'])})"))
            CHANGED["parent"] += 1
            continue
        if ns is None:
            manual(s, "modelJson: no item id for static file")
            continue
        if keys == {"parent", "textures"} and isinstance(data["textures"], dict) \
                and all(isinstance(v, str) for v in data["textures"].values()):
            lines = [".modelGenerator((m) => {",
                     f"  m.parent({json.dumps(data['parent'])});"]
            for k, v in data["textures"].items():
                lines.append(f"  m.texture({json.dumps(k)}, {json.dumps(v)});")
            lines.append("})")
            edits.append((s, close_i + 1, ("\n" + indent_of(text, s)).join(lines)))
            CHANGED["generator"] += 1
            continue
        # Anything else: static item model file; the generated/overridden file is the item model.
        write_asset("models/item", ns, path, data, f"{ns}:item/{path}", rel)
        end = close_i + 1
        mm = re.match(r"\s*;", full[end:])
        if not mm:
            manual(s, "modelJson: static file written but call is an expression, remove by hand")
            continue
        end += mm.end()
        ls = text.rfind("\n", 0, s) + 1
        if text[ls:s].strip() == "":
            le = text.find("\n", end)
            le = len(text) if le < 0 else le + 1
            edits.append((ls, le, ""))
        else:
            edits.append((s, end, ""))
        CHANGED["statements_dropped"] += 1

    # 3. .model("...") block parent -> .parentModel(...)
    for m in re.finditer(r"\.model\s*\(", full):
        s = m.start()
        edits.append((s + 0, m.end(), ".parentModel("))
        CHANGED["model_rename"] += 1

    # 4. serverTick(RATE, OFFSET, cb) -> builder flags + global.portBeTicks[id]
    for m in re.finditer(r"(\w+)\s*\.serverTick\s*\(", full):
        s = m.start()
        recv = m.group(1)
        open_i = m.end() - 1
        close_i = match_close(full, open_i)
        args = split_args(full, open_i, close_i) if close_i > 0 else []
        block_id = nearest_create(code, s)
        after = re.match(r"\s*[;,]", full[close_i + 1:]) or re.match(r"[ \t]*\r?\n", full[close_i + 1:])
        if len(args) != 3 or not after or block_id is None:
            manual(s, "serverTick: unexpected shape or missing block id")
            continue
        rate = text[args[0][0]:args[0][1]].strip()
        offset = text[args[1][0]:args[1][1]].strip()
        cb = text[args[2][0]:args[2][1]].strip()
        ind = indent_of(text, s)
        repl = (f"{recv}.serverTicking();\n{ind}{recv}.tickFrequency({rate});\n"
                f"{ind}{recv}.tickOffset({offset});\n{ind}global.portBeTicks[{json.dumps(block_id)}] = {cb}")
        consumed = after.end() if after.group(0).strip() in (";", ",") else 0
        edits.append((s, close_i + 1 + consumed, repl + ";"))
        CHANGED["ticks"] += 1

    # 5. foreign sound ids in these files (Botania removed)
    new_text_sounds = text
    for old, new in SOUND_MAP.items():
        if old in text:
            CHANGED["sounds"].append(f"{rel}: {old} -> {new}")

    # Apply edits in reverse, skipping overlaps.
    edits.sort(key=lambda e: e[0], reverse=True)
    out = text
    last_start = len(text) + 1
    applied = 0
    for a, b, r in edits:
        if b > last_start:
            manual(a, "overlapping edit skipped")
            continue
        out = out[:a] + r + out[b:]
        last_start = a
        applied += 1
    for old, new in SOUND_MAP.items():
        out = out.replace(old, new)
    if out != text:
        CHANGED["files"].add(rel)
        if not DRY:
            fpath.write_text(out, encoding="utf-8")
    return applied


def ensure_runtime_and_ticks():
    if CHANGED["ticks"] == 0:
        return
    src = RUNTIME.read_text(encoding="utf-8")
    if "global.portBeTicks" not in src:
        src = src.replace("global.runtime = {};", "global.runtime = {};\nglobal.portBeTicks = {};", 1)
        if not DRY:
            RUNTIME.write_text(src, encoding="utf-8")
        CHANGED["files"].add(RUNTIME.relative_to(ROOT).as_posix())
    if not TICKS.exists() or TICKS.read_text(encoding="utf-8") != TICKS_LINE:
        if not DRY:
            TICKS.parent.mkdir(parents=True, exist_ok=True)
            TICKS.write_text(TICKS_LINE, encoding="utf-8")
        CHANGED["files"].add(TICKS.relative_to(ROOT).as_posix())


def main():
    targets = []
    for d in DIRS:
        base = SS / d
        if base.is_file():
            targets.append(base)
        else:
            targets.extend(sorted(base.rglob("*.js")))
    for f in targets:
        t = f.read_text(encoding="utf-8")
        if re.search(r"modelJson|blockstateJson|\.model\(|serverTick\(|itemModelJson", t):
            convert_file(f)
    ensure_runtime_and_ticks()
    print(f"dry_run={DRY}")
    print(f"files_changed={len(CHANGED['files'])}")
    print(f"blockstates={CHANGED['blockstates']} static_new={len(CHANGED['static'])} "
          f"static_same={CHANGED['static_same']} static_overwritten={len(CHANGED['static_overwritten'])}")
    print(f"parentModel(modelJson)={CHANGED['parent']} modelGenerator={CHANGED['generator']} "
          f"model_rename={CHANGED['model_rename']} static_statements_dropped={CHANGED['statements_dropped']} "
          f"serverTick={CHANGED['ticks']}")
    for s in CHANGED["static"]:
        print("STATIC", s)
    for s in CHANGED["static_overwritten"]:
        print("OVERWRITTEN", s)
    for s in sorted(set(CHANGED["sounds"])):
        print("SOUND", s)
    for s in MANUAL:
        print("MANUAL", s)


if __name__ == "__main__":
    main()
