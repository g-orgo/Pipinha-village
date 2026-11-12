#!/usr/bin/env python3
"""Port config values from the old 1.20.1 instance into the new 1.21.1 instance.

Reads the old instance (never writes it), merges values into files that already
exist in the new instance, copies configs of installed mods that the new
instance has not generated yet, and writes tools/configport/REPORT.md.

Run from the new instance root:
    python3 -I tools/configport/port_configs.py
"""

import datetime
import json
import math
import os
import re
import shutil
import tarfile
import time
import tomllib
from pathlib import Path

NEW_ROOT = Path(__file__).resolve().parents[2]
OLD_ROOT = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley")
MODIDS_FILE = NEW_ROOT / "tools" / "modcheck" / "modids.txt"
TOOL_DIR = NEW_ROOT / "tools" / "configport"
REPORT_PATH = TOOL_DIR / "REPORT.md"
FIRST_RUN_PATH = TOOL_DIR / "first_run.json"
F3_RUN_PATH = TOOL_DIR / "f3_run.json"

SKIP_DIR_NAMES = {"ftbquests", "fancymenu"}
SKIP_SUFFIXES = (".bak", ".old")
RESOURCE_ID_RE = re.compile(r"^#?([a-z][a-z0-9_.-]*):([a-z0-9_./-]*[a-z][a-z0-9_./-]*)$")
ALWAYS_ALLOWED_NS = {"minecraft", "forge", "neoforge", "c", "common"}


def is_kubejs_related(name):
    low = name.lower()
    return "kubejs" in low


def is_skipped_dir(name):
    return name in SKIP_DIR_NAMES or is_kubejs_related(name)


def load_modids():
    ids = set()
    for line in MODIDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            ids.add(line.lower())
    return ids


# ---------------------------------------------------------------------------
# TOML scanning (textual, keeps comments and formatting)
# ---------------------------------------------------------------------------

def _skip_string(text, i):
    """Return index just after a TOML string starting at i."""
    n = len(text)
    for quote in ('"""', "'''"):
        if text.startswith(quote, i):
            j = i + 3
            while j < n:
                if text.startswith(quote, j):
                    return j + 3
                if quote == '"""' and text[j] == "\\":
                    j += 2
                    continue
                j += 1
            return n
    quote = text[i]
    j = i + 1
    while j < n:
        if quote == '"' and text[j] == "\\":
            j += 2
            continue
        if text[j] == quote:
            return j + 1
        j += 1
    return n


def scan_value(text, i):
    """Return the end index of the TOML value starting at i."""
    n = len(text)
    if text.startswith('"""', i) or text.startswith("'''", i):
        return _skip_string(text, i)
    c = text[i]
    if c in "\"'":
        return _skip_string(text, i)
    if c in "[{":
        depth = 0
        j = i
        while j < n:
            ch = text[j]
            if ch == "#":
                k = text.find("\n", j)
                j = n if k < 0 else k + 1
                continue
            if ch in "\"'":
                j = _skip_string(text, j)
                continue
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
        return n
    j = i
    while j < n and text[j] not in "\r\n#":
        j += 1
    while j > i and text[j - 1] in " \t":
        j -= 1
    return j


def _unquote_key(part):
    part = part.strip()
    if len(part) >= 2 and part[0] == "'" and part[-1] == "'":
        return part[1:-1]
    if len(part) >= 2 and part[0] == '"' and part[-1] == '"':
        try:
            return tomllib.loads("k = " + part)["k"]
        except Exception:
            return part[1:-1]
    return part


def split_dotted(text):
    parts = []
    cur = []
    quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if quote:
            cur.append(c)
            if quote == '"' and c == "\\" and i + 1 < len(text):
                cur.append(text[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "\"'":
            quote = c
            cur.append(c)
            i += 1
            continue
        if c == ".":
            parts.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur).strip())
    return tuple(_unquote_key(p) for p in parts)


def scan_toml(text):
    """Map full key path -> (start, end, raw value text). Ambiguous keys skipped."""
    entries = {}
    ambiguous = set()
    section = ()
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        if text[i] == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if text[i] == "[":
            eol = text.find("\n", i)
            if eol < 0:
                eol = n
            line = text[i:eol]
            stripped = line.split("#", 1)[0].strip()
            if stripped.startswith("[["):
                inner = stripped[2:]
                if inner.endswith("]]"):
                    inner = inner[:-2]
            else:
                inner = stripped[1:]
                if inner.endswith("]"):
                    inner = inner[:-1]
            section = split_dotted(inner)
            i = eol + 1
            continue
        # key = value
        eq = -1
        quote = None
        j = i
        while j < n:
            c = text[j]
            if quote:
                if quote == '"' and c == "\\":
                    j += 2
                    continue
                if c == quote:
                    quote = None
            elif c in "\"'":
                quote = c
            elif c == "=":
                eq = j
                break
            elif c == "\n":
                break
            j += 1
        if eq < 0:
            # Not a key line we understand; move to next line.
            eol = text.find("\n", i)
            i = n if eol < 0 else eol + 1
            continue
        keytext = text[i:eq].strip()
        full = section + split_dotted(keytext)
        vstart = eq + 1
        while vstart < n and text[vstart] in " \t\r\n":
            vstart += 1
        if vstart >= n:
            break
        vend = scan_value(text, vstart)
        raw = text[vstart:vend]
        if full in entries:
            ambiguous.add(full)
        else:
            entries[full] = (vstart, vend, raw)
        eol = text.find("\n", vend)
        i = n if eol < 0 else eol + 1
    for key in ambiguous:
        entries.pop(key, None)
    return entries


def get_value(obj, path):
    cur = obj
    for part in path:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return _MISSING
    return cur


_MISSING = object()


def values_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, float):
        if math.isnan(a) and math.isnan(b):
            return True
        return a == b
    if isinstance(a, list):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        if set(a) != set(b):
            return False
        return all(values_equal(a[k], b[k]) for k in a)
    return a == b


def toml_literal(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(toml_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        items = []
        for k, v in value.items():
            items.append(toml_literal_key(k) + " = " + toml_literal(v))
        return "{" + ", ".join(items) + "}"
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return json.dumps(str(value), ensure_ascii=False)


def toml_literal_key(key):
    if re.fullmatch(r"[A-Za-z0-9_-]+", key):
        return key
    return json.dumps(key, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Resource id filtering
# ---------------------------------------------------------------------------

def is_resource_id(value, modids):
    if not isinstance(value, str):
        return False
    match = RESOURCE_ID_RE.match(value)
    if not match:
        return False
    ns = match.group(1)
    return ns not in modids and ns not in ALWAYS_ALLOWED_NS


def filter_list(values, modids, dropped, where):
    """Return a filtered list, recording dropped resource ids."""
    result = []
    for item in values:
        if isinstance(item, list):
            result.append(filter_list(item, modids, dropped, where))
        elif isinstance(item, str) and is_resource_id(item, modids):
            dropped.append(item)
        else:
            result.append(item)
    return result


def filter_tree(value, modids, dropped, where):
    """Filter resource ids in every list nested in a JSON value."""
    if isinstance(value, list):
        return filter_list(value, modids, dropped, where)
    if isinstance(value, dict):
        return {k: filter_tree(v, modids, dropped, where) for k, v in value.items()}
    return value


# ---------------------------------------------------------------------------
# JSON merge
# ---------------------------------------------------------------------------

def detect_indent(text):
    for line in text.splitlines()[1:]:
        match = re.match(r"^( +)\S", line)
        if match:
            width = len(match.group(1))
            return 4 if width >= 4 else 2
    return 2


# ---------------------------------------------------------------------------
# Mod detection for files missing in the new instance
# ---------------------------------------------------------------------------

def strip_known_suffixes(stem):
    candidates = [stem]
    low = stem.lower()
    for suffix in ("-client", "-common", "-server", ".client", ".server"):
        if low.endswith(suffix):
            candidates.append(stem[: -len(suffix)])
    for cand in list(candidates):
        trimmed = re.sub(r"-(?:forge|fabric|neoforge)(?:[._-].*)?$", "", cand, flags=re.I)
        trimmed = re.sub(r"-(?:\d[\w.]*)$", "", trimmed)
        if trimmed != cand:
            candidates.append(trimmed)
    return candidates


def mod_present(relpath, modids):
    parts = Path(relpath).parts
    if len(parts) > 1:
        return parts[0].lower() in modids
    stem = Path(parts[-1]).stem
    for cand in strip_known_suffixes(stem):
        if cand.lower() in modids:
            return True
    return False


# ---------------------------------------------------------------------------
# Sunlit display-name handling
# ---------------------------------------------------------------------------

SUNLIT_PHRASE = re.compile(r"Society:\s*Sunlit Valley|Sunlit Valley")


def rename_value(value):
    """Apply the display rename to strings inside a config value."""
    if isinstance(value, str):
        return SUNLIT_PHRASE.sub("Pipinha's Village", value)
    if isinstance(value, list):
        return [rename_value(item) for item in value]
    if isinstance(value, dict):
        return {key: rename_value(item) for key, item in value.items()}
    return value


def handle_sunlit(text, relpath):
    """Replace only the display phrases, keep ids untouched. Return records."""
    records = []
    new_lines = []
    for lineno, line in enumerate(text.splitlines(keepends=True), 1):
        if "sunlit" not in line.lower():
            new_lines.append(line)
            continue
        if SUNLIT_PHRASE.search(line):
            new_lines.append(SUNLIT_PHRASE.sub("Pipinha's Village", line))
            records.append((relpath, lineno, "replaced display name", line.strip()[:120]))
        else:
            new_lines.append(line)
            records.append((relpath, lineno, "left unchanged (not the display phrase)", line.strip()[:120]))
    return "".join(new_lines), records


# ---------------------------------------------------------------------------
# Round F3: old-name merges, as-is copies, line merges, lostcities text
# ---------------------------------------------------------------------------

OLD_NAME_MODS = ("bakery", "beachparty", "herbalbrews", "meadow", "vinery", "wildernature")

STEP2_DIRS = (
    "portable_blueprints",
    "easy_npc/skin",
    "easy_npc/preset",
    "xaero",
)
STEP2_GLOBS = (
    ("jei", "*.ini"),
)
STEP2_FILES = (
    "xaeropatreon.txt",
    "worldedit/worldedit.properties",
)
# Kept out of the generic pass so F3 owns them.
F3_EXCLUDED_PREFIXES = (
    "portable_blueprints/",
    "easy_npc/skin/",
    "easy_npc/preset/",
    "jei/",
    "xaero/",
    "xaeropatreon.txt",
    "worldedit/worldedit.properties",
    "relics/",
    "relics.yaml",
    "sunlit_cinematic_toms_trashslot.txt",
    "lostcities/profiles/sunlit_cozy.json",
)

STEP3_KV = (
    "MouseTweaks.cfg",
    "fastsuite.cfg",
    "packetfixer.properties",
    "handson_delight.properties",
    "sound_physics_remastered/occlusion.properties",
    "sound_physics_remastered/reflectivity.properties",
    "sound_physics_remastered/soundphysics.properties",
    "sound_physics_remastered/sound_rates.properties",
)
STEP3_EASYNPC_KV = (
    "easy_npc/dialog_client.cfg",
    "easy_npc/dialog_options.cfg",
    "easy_npc/highlight_client.cfg",
    "easy_npc/name_tag_client.cfg",
    "easy_npc/npc_base.cfg",
    "easy_npc/remote_texture.cfg",
    "easy_npc/render_entity_type_support.cfg",
    "easy_npc/security.cfg",
    "easy_npc/spawner_type.cfg",
    "easy_npc/storage.cfg",
)
STEP3_YAML = (
    "kiwi-client.yaml",
    "kiwi-common.yaml",
    "passablefoliage-common.yaml",
    "snowrealmagic-client.yaml",
    "snowrealmagic-common.yaml",
    "relics.yaml",
    "servercore/config.yml",
    "servercore/optimizations.yml",
)
STEP3_KEYED = (
    "chat_heads.json5",
    "ok_zoomer/config.json5",
    "spatial-gui.json5",
    "spatial-gui/profiles.json5",
    "trofers/general.json5",
    "yacl.json5",
    "extractinator.jsonc",
    "golemoverhaul.jsonc",
    "ftbxmodcompat.snbt",
)
STEP4_PROFILE = "config/lostcities/profiles/sunlit_cozy.json"
STEP4_TEXT = "Pipinha's Village: cidades com moradores, golens e loot temático por cômodo"

SCALAR_RE = re.compile(
    r'^(?:true|false|null|~|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
    r'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^\s{}\[\],]+)$'
)


def is_scalar(text):
    return bool(SCALAR_RE.match(text.strip()))


def format_path(path):
    return ".".join(str(part) for part in path if part is not None)


def mask_comments(text, in_block):
    """Blank out comments, keeping column positions. Tracks multi-line blocks."""
    out = list(text)
    i = 0
    quote = None
    n = len(text)
    while i < n:
        if in_block:
            if text.startswith("*/", i):
                in_block = False
                out[i] = out[i + 1] = " "
                i += 2
                continue
            out[i] = " "
            i += 1
            continue
        c = text[i]
        if quote:
            if c == "\\" and quote == '"' and i + 1 < n:
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c in "\"'":
            quote = c
            i += 1
            continue
        if text.startswith("//", i) or text.startswith("/*", i):
            if text.startswith("/*", i):
                in_block = True
                out[i] = out[i + 1] = " "
                i += 2
                continue
            for j in range(i, n):
                out[j] = " "
            break
        if c == "#":
            for j in range(i, n):
                out[j] = " "
            break
        i += 1
    return "".join(out), in_block


def parse_kv_lines(text):
    """Map key path -> (line index, value start, value end, raw value)."""
    entries = {}
    duplicates = set()
    sections = []
    for index, line in enumerate(text.splitlines(keepends=True)):
        raw = line.rstrip("\r\n")
        stripped = raw.strip()
        if not stripped or stripped[0] in "#!":
            continue
        close = stripped == "}" or stripped.startswith("} ")
        if close:
            if sections:
                sections.pop()
            continue
        opener = re.match(r"^([^=\s][^=]*?)\s*\{\s*$", stripped)
        if opener:
            sections.append(opener.group(1).strip())
            continue
        match = re.match(r"^([^=\s][^=]*?)\s*=\s*(.*)$", raw)
        if not match:
            continue
        key = match.group(1).strip()
        value_start = match.start(2)
        value_end = len(raw)
        while value_end > value_start and raw[value_end - 1] in " \t":
            value_end -= 1
        raw_value = raw[value_start:value_end]
        if not is_scalar(raw_value):
            continue
        path = tuple(sections) + (key,)
        if path in entries:
            duplicates.add(path)
        else:
            entries[path] = (index, value_start, value_end, raw_value)
    for path in duplicates:
        entries.pop(path, None)
    return entries


def parse_yaml_lines(text):
    entries = {}
    duplicates = set()
    stack = []  # (indent, key)
    for index, line in enumerate(text.splitlines(keepends=True)):
        raw = line.rstrip("\r\n")
        masked, _ = mask_comments(raw, False)
        stripped = masked.strip()
        if not stripped or stripped.startswith("---"):
            continue
        match = re.match(r"^(\s*)([A-Za-z0-9_.\-]+)\s*:\s*(.*)$", line)
        if not match or masked.lstrip().startswith("#"):
            continue
        indent = len(match.group(1))
        key = match.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parents = tuple(item[1] for item in stack)
        path = parents + (key,)
        value_start = match.start(3)
        value_end = len(raw)
        while value_end > value_start and masked[value_end - 1] in " \t":
            value_end -= 1
        raw_value = raw[value_start:value_end]
        if not raw_value:
            stack.append((indent, key))
            continue
        if not is_scalar(raw_value):
            continue
        if path in entries:
            duplicates.add(path)
        else:
            entries[path] = (index, value_start, value_end, raw_value)
    for path in duplicates:
        entries.pop(path, None)
    return entries


def parse_keyed_lines(text):
    """Brace-nesting parser for json5/jsonc/snbt scalar lines."""
    entries = {}
    duplicates = set()
    containers = []  # ("obj", key) or ("arr", None)
    in_block = False

    def current_path():
        return tuple(key for kind, key in containers if kind == "obj" and key is not None)

    for index, line in enumerate(text.splitlines(keepends=True)):
        raw = line.rstrip("\r\n")
        masked, in_block = mask_comments(raw, in_block)
        pos = len(masked) - len(masked.lstrip())
        # Consume closers that start the line before reading a key.
        while True:
            rest = masked[pos:].lstrip()
            if rest.startswith(("}", "]")):
                if containers:
                    containers.pop()
                pos = len(masked) - len(rest[1:].lstrip())
                continue
            break
        rest = masked[pos:]
        rest = rest.lstrip(" \t,")
        pos = len(masked) - len(rest) if rest else len(masked)
        if not rest:
            continue
        inside_array = bool(containers) and containers[-1][0] == "arr"
        match = re.match(
            r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[A-Za-z_][A-Za-z0-9_.\-]*)\s*:\s*(.*)$',
            rest,
        )
        key = None
        scan_start = pos
        if match:
            key_token = match.group(1)
            if key_token[:1] in "\"'":
                key = key_token[1:-1]
            else:
                key = key_token
            value_start = pos + match.start(2)
            value_end = len(masked)
            while value_end > value_start and masked[value_end - 1] in " \t,":
                value_end -= 1
            raw_value = masked[value_start:value_end]
            scan_start = value_start
            if not inside_array and is_scalar(raw_value):
                path = current_path() + (key,)
                if path in entries:
                    duplicates.add(path)
                else:
                    entries[path] = (index, value_start, value_end, raw_value)
        # Track every structural character on the line after the key.
        quote = None
        first_opener = True
        for offset in range(scan_start, len(masked)):
            char = masked[offset]
            if quote:
                if char == "\\" and quote == '"':
                    continue
                if char == quote:
                    quote = None
                continue
            if char in "\"'":
                quote = char
                continue
            if char in "{[":
                parent = key if (first_opener and char == "{" and match) else None
                containers.append(("obj" if char == "{" else "arr", parent))
                first_opener = False
            elif char in "}]":
                if containers:
                    containers.pop()
                first_opener = False
    for path in duplicates:
        entries.pop(path, None)
    return entries


def merge_simple(old_text, new_text, parser):
    """Replace scalar values in new_text with old values at the same path."""
    old_entries = parser(old_text)
    new_entries = parser(new_text)
    lines = new_text.splitlines(keepends=True)
    changes = []
    for path, (index, start, end, raw_value) in new_entries.items():
        if path not in old_entries:
            continue
        old_value = old_entries[path][3]
        if old_value == raw_value:
            continue
        line = lines[index]
        lines[index] = line[:start] + old_value + line[end:]
        changes.append((format_path(path), old_value, raw_value))
    return "".join(lines), changes


def merge_toml_text(old_text, new_text, modids):
    """Textual TOML merge used by the generic pass and by step 1."""
    old_data = tomllib.loads(old_text)
    new_data = tomllib.loads(new_text)
    old_entries = scan_toml(old_text)
    new_entries = scan_toml(new_text)
    replacements = []
    changes = []
    dropped = []
    for key, (start, end, new_raw) in new_entries.items():
        if key not in old_entries:
            continue
        old_val = get_value(old_data, key)
        new_val = get_value(new_data, key)
        if old_val is _MISSING or new_val is _MISSING:
            continue
        if type(old_val) is not type(new_val):
            continue
        old_cmp = rename_value(old_val)
        if values_equal(old_cmp, new_val):
            continue
        if isinstance(old_val, list):
            filtered = filter_list(old_val, modids, dropped, "")
            if values_equal(rename_value(filtered), new_val):
                continue
            if len(filtered) == len(old_val):
                literal = old_entries[key][2]
            else:
                literal = toml_literal(filtered)
        else:
            literal = old_entries[key][2]
        replacements.append((start, end, literal))
        changes.append((format_path(key), old_entries[key][2], new_raw))
    for start, end, literal in sorted(replacements, reverse=True):
        new_text = new_text[:start] + literal + new_text[end:]
    return new_text, changes, dropped


def f3_excluded(relpath):
    text = str(relpath).replace("\\", "/")
    return any(text == prefix.rstrip("/") or text.startswith(prefix) for prefix in F3_EXCLUDED_PREFIXES)


def collect_step2_files(old_config):
    found = []
    for rel in STEP2_DIRS:
        base = old_config / rel
        if base.is_dir():
            for path in sorted(base.rglob("*")):
                if path.is_file():
                    found.append(path.relative_to(old_config))
    for rel_dir, pattern in STEP2_GLOBS:
        base = old_config / rel_dir
        if base.is_dir():
            for path in sorted(base.glob(pattern)):
                if path.is_file():
                    found.append(path.relative_to(old_config))
    for rel in STEP2_FILES:
        path = old_config / rel
        if path.is_file():
            found.append(Path(rel))
    return found


def update_lostcities(path):
    text = read_text(path)
    data = json.loads(text)
    lostcity = data.get("lostcity") if isinstance(data, dict) else None
    if not isinstance(lostcity, dict):
        lostcity = {}
    old_text = lostcity.get("extraDescription")
    if old_text == STEP4_TEXT:
        return None, old_text, STEP4_TEXT
    new_text = text
    pattern = re.compile(r'("extraDescription"\s*:\s*)"(?:[^"\\]|\\.)*"')
    if not pattern.search(new_text):
        raise ValueError("extraDescription key not found")
    new_text = pattern.sub(lambda m: m.group(1) + json.dumps(STEP4_TEXT, ensure_ascii=False), new_text, count=1)
    desc = lostcity.get("description")
    if isinstance(desc, str) and "Sunlit" in desc:
        fixed = SUNLIT_PHRASE.sub("Pipinha's Village", desc)
        new_text = new_text.replace(json.dumps(desc, ensure_ascii=False), json.dumps(fixed, ensure_ascii=False), 1)
    return new_text, old_text, STEP4_TEXT


# ---------------------------------------------------------------------------
# Main porting logic
# ---------------------------------------------------------------------------

def walk_files(base):
    result = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if not is_skipped_dir(d))
        for name in sorted(filenames):
            if name.lower().endswith(SKIP_SUFFIXES):
                continue
            if is_kubejs_related(name):
                continue
            result.append(Path(dirpath, name))
    return result


def read_text(path):
    return path.read_text(encoding="utf-8", newline="")


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def make_backup(suffix=""):
    TOOL_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    target = TOOL_DIR / ("backup-" + stamp + suffix + ".tar.gz")
    counter = 1
    while target.exists():
        target = TOOL_DIR / ("backup-" + stamp + suffix + "-" + str(counter) + ".tar.gz")
        counter += 1
    with tarfile.open(target, "w:gz") as tar:
        for name in ("config", "defaultconfigs"):
            path = NEW_ROOT / name
            if path.exists():
                tar.add(path, arcname=name)
    return target


def main():
    modids = load_modids()
    stats = {
        "merged": [],          # (relpath, keys)
        "keys_changed": 0,
        "copied": [],
        "manual": [],          # (relpath, has_new)
        "skipped": [],         # (relpath, reason)
        "errors": [],          # (relpath, reason)
        "dropped": [],         # (relpath, entry)
    }
    planned_writes = []        # (path, text, relpath, kind)
    planned_copies = []        # (old_path, new_path, relpath)
    planned_deletes = []       # (path, relpath)
    f3 = {
        "step1": [],
        "step1_deleted": [],
        "step1_skipped": [],
        "step2_copied": [],
        "step2_skipped": [],
        "step3": [],
        "step3_skipped": [],
        "step4": None,
        "deleted": [],
    }

    old_config = OLD_ROOT / "config"
    new_config = NEW_ROOT / "config"

    # Step 2 is copied byte for byte, outside the generic merge pass.
    for relpath in collect_step2_files(old_config):
        rel = str(relpath).replace("\\", "/")
        new_path = new_config / relpath
        if new_path.exists():
            f3["step2_skipped"].append((rel, "already exists"))
            continue
        planned_copies.append((old_config / relpath, new_path, rel))
        f3["step2_copied"].append(rel)
    for rel, reason in (
        ("relics/**", "pending review"),
        ("oculus.properties", "mod not installed"),
        ("lithium.properties", "mod not installed"),
        ("splendid_slimes.cfg", "mod not installed"),
        ("maxenchantx/**", "mod not installed"),
        ("sunlit_cinematic_toms_trashslot.txt", "listed, not copied"),
    ):
        f3["step2_skipped"].append((rel, reason))

    # Step 1: merge old single-name TOML into the new -common TOML, then drop
    # the single-name copy made by the earlier run.
    for mod in OLD_NAME_MODS:
        old_path = old_config / (mod + ".toml")
        common_path = new_config / (mod + "-common.toml")
        duplicate = new_config / (mod + ".toml")
        rel_common = mod + "-common.toml"
        rel_duplicate = mod + ".toml"
        if duplicate.exists():
            planned_deletes.append((duplicate, rel_duplicate))
            f3["step1_deleted"].append(rel_duplicate)
        if not old_path.exists() or not common_path.exists():
            f3["step1_skipped"].append((rel_common, "old or new file missing"))
            continue
        try:
            old_text = read_text(old_path)
            new_text = read_text(common_path)
            merged, changes, dropped = merge_toml_text(old_text, new_text, modids)
        except Exception as exc:
            stats["errors"].append((rel_common, "step1 merge error: " + str(exc)[:100]))
            continue
        if changes:
            planned_writes.append((common_path, merged, rel_common, "merged"))
            stats["merged"].append((rel_common, len(changes)))
            stats["keys_changed"] += len(changes)
            stats["dropped"].extend((rel_common, entry) for entry in dropped)
        f3["step1"].append((rel_common, changes))

    # Step 3: line-based scalar merges.
    step3_groups = (
        (STEP3_KV, parse_kv_lines, "config/"),
        (STEP3_EASYNPC_KV, parse_kv_lines, "config/"),
        (STEP3_YAML, parse_yaml_lines, "config/"),
        (STEP3_KEYED, parse_keyed_lines, "config/"),
    )
    for rels, parser, prefix in step3_groups:
        for rel in rels:
            old_path = OLD_ROOT / prefix / rel
            new_path = NEW_ROOT / prefix / rel
            display = prefix + rel
            if not old_path.exists() or not new_path.exists():
                f3["step3_skipped"].append((display, "old or new file missing"))
                continue
            try:
                merged, changes = merge_simple(read_text(old_path), read_text(new_path), parser)
            except Exception as exc:
                stats["errors"].append((display, "step3 merge error: " + str(exc)[:100]))
                continue
            if changes:
                planned_writes.append((new_path, merged, display, "merged"))
                stats["merged"].append((display, len(changes)))
                stats["keys_changed"] += len(changes)
            f3["step3"].append((display, changes))
    # defaultconfigs snbt shares the keyed parser but lives outside config/.
    rel = "defaultconfigs/certain_questing_additions/client-config.snbt"
    old_path = OLD_ROOT / rel
    new_path = NEW_ROOT / rel
    if old_path.exists() and new_path.exists():
        try:
            merged, changes = merge_simple(read_text(old_path), read_text(new_path), parse_keyed_lines)
        except Exception as exc:
            stats["errors"].append((rel, "step3 merge error: " + str(exc)[:100]))
        else:
            if changes:
                planned_writes.append((new_path, merged, rel, "merged"))
                stats["merged"].append((rel, len(changes)))
                stats["keys_changed"] += len(changes)
            f3["step3"].append((rel, changes))
    else:
        f3["step3_skipped"].append((rel, "old or new file missing"))

    # Step 4: lostcities display text only.
    profile_path = NEW_ROOT / STEP4_PROFILE
    if profile_path.exists():
        try:
            new_text, old_text, new_value = update_lostcities(profile_path)
        except Exception as exc:
            stats["errors"].append((STEP4_PROFILE, "step4 error: " + str(exc)[:100]))
        else:
            if new_text is not None:
                planned_writes.append((profile_path, new_text, STEP4_PROFILE, "merged"))
                stats["merged"].append((STEP4_PROFILE, 1))
                stats["keys_changed"] += 1
            f3["step4"] = (old_text, new_value)
    else:
        f3["step4"] = ("missing", None)

    for old_path in walk_files(old_config):
        relpath = old_path.relative_to(old_config)
        rel = str(relpath)
        if f3_excluded(relpath) or (relpath.parent == Path(".") and relpath.stem in OLD_NAME_MODS and relpath.suffix.lower() == ".toml"):
            continue
        new_path = new_config / relpath
        suffix = old_path.suffix.lower()

        if new_path.exists():
            if suffix == ".toml":
                try:
                    old_text = read_text(old_path)
                    new_text = read_text(new_path)
                    merged, changes, dropped = merge_toml_text(old_text, new_text, modids)
                except Exception as exc:
                    stats["errors"].append((rel, "parse error: " + str(exc)[:100]))
                    continue
                if changes:
                    changed_text, sunlit = handle_sunlit(merged, rel)
                    planned_writes.append((new_path, changed_text, rel, "merged"))
                    stats["merged"].append((rel, len(changes)))
                    stats["keys_changed"] += len(changes)
                    stats["dropped"].extend((rel, entry) for entry in dropped)
                    stats.setdefault("sunlit", []).extend(sunlit)
            elif suffix == ".json":
                try:
                    old_text = read_text(old_path)
                    new_text = read_text(new_path)
                    old_data = json.loads(old_text)
                    new_data = json.loads(new_text)
                except Exception as exc:
                    stats["errors"].append((rel, "invalid JSON: " + str(exc)[:100]))
                    continue
                if not isinstance(old_data, dict) or not isinstance(new_data, dict):
                    stats["manual"].append((rel, True))
                    continue
                changes = []
                dropped = []
                def apply_merge(old_node, new_node, keypath):
                    if isinstance(old_node, dict) and isinstance(new_node, dict):
                        for key in list(new_node.keys()):
                            if key not in old_node:
                                continue
                            if type(old_node[key]) is not type(new_node[key]):
                                continue
                            if isinstance(new_node[key], dict):
                                apply_merge(old_node[key], new_node[key], keypath + (key,))
                            elif isinstance(new_node[key], list):
                                candidate = filter_list(old_node[key], modids, dropped, rel)
                                if not values_equal(rename_value(candidate), new_node[key]):
                                    new_node[key] = candidate
                                    changes.append(keypath + (key,))
                            else:
                                old_scalar = old_node[key]
                                if not values_equal(rename_value(old_scalar), new_node[key]):
                                    new_node[key] = old_scalar
                                    changes.append(keypath + (key,))
                    return new_node
                apply_merge(old_data, new_data, ())
                if changes:
                    indent = detect_indent(new_text)
                    out = json.dumps(new_data, indent=indent, ensure_ascii=False)
                    if new_text.endswith("\n"):
                        out += "\n"
                    if "\r\n" in new_text:
                        out = out.replace("\n", "\r\n")
                    changed_text, sunlit = handle_sunlit(out, rel)
                    planned_writes.append((new_path, changed_text, rel, "merged"))
                    stats["merged"].append((rel, len(changes)))
                    stats["keys_changed"] += len(changes)
                    stats["dropped"].extend((rel, entry) for entry in dropped)
                    stats.setdefault("sunlit", []).extend(sunlit)
            else:
                stats["manual"].append((rel, True))
            continue

        # File missing in the new instance.
        if suffix not in (".toml", ".json"):
            stats["manual"].append((rel, False))
            continue
        if not mod_present(relpath, modids):
            stats["skipped"].append((rel, "mod not installed"))
            continue

        if suffix == ".toml":
            try:
                text = read_text(old_path)
                tomllib.loads(text)
            except Exception as exc:
                stats["errors"].append((rel, "invalid TOML: " + str(exc)[:100]))
                continue
            changed_text, sunlit = handle_sunlit(text, rel)
            planned_writes.append((new_path, changed_text, rel, "copied"))
            stats["copied"].append(rel)
            stats.setdefault("sunlit", []).extend(sunlit)
        else:
            try:
                text = read_text(old_path)
                data = json.loads(text)
            except Exception as exc:
                stats["errors"].append((rel, "invalid JSON: " + str(exc)[:100]))
                continue
            dropped = []
            data = filter_tree(data, modids, dropped, rel)
            indent = detect_indent(text)
            out = json.dumps(data, indent=indent, ensure_ascii=False)
            if text.endswith("\n"):
                out += "\n"
            if "\r\n" in text:
                out = out.replace("\n", "\r\n")
            changed_text, sunlit = handle_sunlit(out, rel)
            planned_writes.append((new_path, changed_text, rel, "copied"))
            stats["copied"].append(rel)
            stats["dropped"].extend((rel, entry) for entry in dropped)
            stats.setdefault("sunlit", []).extend(sunlit)

    # ------------------------------------------------------------------
    # Step 2: defaultconfigs
    # ------------------------------------------------------------------
    old_defaults = OLD_ROOT / "defaultconfigs"
    new_defaults = NEW_ROOT / "defaultconfigs"
    if old_defaults.exists():
        for old_path in walk_files(old_defaults):
            relpath = old_path.relative_to(old_defaults)
            rel = str(relpath)
            new_path = new_defaults / relpath
            suffix = old_path.suffix.lower()
            if new_path.exists():
                stats["manual"].append(("defaultconfigs/" + rel, True))
                continue
            if suffix != ".toml":
                stats["skipped"].append(("defaultconfigs/" + rel, "not a .toml file"))
                continue
            if not mod_present(relpath, modids):
                stats["skipped"].append(("defaultconfigs/" + rel, "mod not installed"))
                continue
            try:
                text = read_text(old_path)
                tomllib.loads(text)
            except Exception as exc:
                stats["errors"].append(("defaultconfigs/" + rel, "invalid TOML: " + str(exc)[:100]))
                continue
            changed_text, sunlit = handle_sunlit(text, "defaultconfigs/" + rel)
            planned_writes.append((new_path, changed_text, "defaultconfigs/" + rel, "copied"))
            stats["copied"].append("defaultconfigs/" + rel)
            stats.setdefault("sunlit", []).extend(sunlit)

    # ------------------------------------------------------------------
    # Backup, then write.
    # ------------------------------------------------------------------
    backup_path = None
    has_changes = bool(planned_writes or planned_copies or planned_deletes)
    if has_changes:
        backup_path = make_backup("-f3")
        # Copies go first so a failure cannot leave a half-merged file behind.
        for old_path, new_path, _rel in planned_copies:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(old_path, new_path)
        for path, text, rel, kind in planned_writes:
            write_text(path, text)
        for path, rel in planned_deletes:
            if path.exists():
                path.unlink()
            f3["deleted"].append(rel)
    stats["backup"] = str(backup_path) if backup_path else None

    # Validation of every TOML/JSON file we actually authored. Files copied
    # byte for byte in step 2 are not rewritten, so they are reported apart.
    validation = {"toml_pass": 0, "toml_fail": 0, "json_pass": 0, "json_fail": 0}
    validation_failures = []
    check_paths = [(path, rel) for path, _text, rel, _kind in planned_writes]
    for path, rel in check_paths:
        try:
            if path.suffix.lower() == ".toml":
                tomllib.loads(read_text(path))
                validation["toml_pass"] += 1
            elif path.suffix.lower() == ".json":
                json.loads(read_text(path))
                validation["json_pass"] += 1
        except Exception as exc:
            key = "toml_fail" if path.suffix.lower() == ".toml" else "json_fail"
            validation[key] += 1
            validation_failures.append((rel, str(exc)[:100]))
    stats["validation"] = validation
    stats["validation_failures"] = validation_failures

    # Keep the first run data for the report even after the idempotency run.
    if not FIRST_RUN_PATH.exists() and (stats["keys_changed"] or stats["copied"]):
        TOOL_DIR.mkdir(parents=True, exist_ok=True)
        FIRST_RUN_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    if not F3_RUN_PATH.exists() and has_changes:
        TOOL_DIR.mkdir(parents=True, exist_ok=True)
        F3_RUN_PATH.write_text(json.dumps(f3, indent=2, ensure_ascii=False), encoding="utf-8")
    report_stats = stats
    if FIRST_RUN_PATH.exists():
        try:
            report_stats = json.loads(FIRST_RUN_PATH.read_text(encoding="utf-8"))
            if stats["validation"]["toml_pass"] + stats["validation"]["json_pass"] > 0:
                report_stats["validation"] = stats["validation"]
                report_stats["validation_failures"] = stats["validation_failures"]
            report_stats["current_keys_changed"] = stats["keys_changed"]
            report_stats["current_copied"] = len(stats["copied"])
        except Exception:
            report_stats = stats

    f3_report = f3
    if F3_RUN_PATH.exists():
        try:
            f3_report = json.loads(F3_RUN_PATH.read_text(encoding="utf-8"))
        except Exception:
            f3_report = f3
    f3_report = dict(f3_report)
    f3_report["current"] = {
        "keys_changed": stats["keys_changed"],
        "copied": len(planned_copies),
        "deleted": len(planned_deletes),
        "step4_changed": bool(f3["step4"] and f3["step4"][0] != f3["step4"][1]),
    }
    write_report(report_stats, stats, backup_path)
    write_f3_report(f3_report, validation, validation_failures)

    print("merged files: %d" % len(stats["merged"]))
    print("keys changed: %d" % stats["keys_changed"])
    print("copied files: %d" % len(stats["copied"]))
    print("manual files: %d" % len(stats["manual"]))
    print("skipped files: %d" % len(stats["skipped"]))
    print("errors: %d" % len(stats["errors"]))
    print("dropped ids: %d" % len(stats["dropped"]))
    print("toml validation: %d pass / %d fail" % (validation["toml_pass"], validation["toml_fail"]))
    print("json validation: %d pass / %d fail" % (validation["json_pass"], validation["json_fail"]))
    if backup_path:
        print("backup: %s" % backup_path)


def write_f3_report(f3, validation, validation_failures):
    lines = []
    lines.append("")
    lines.append("## Round F3")
    lines.append("")
    lines.append("### Step 1: old-name TOML merges")
    lines.append("")
    step1 = f3.get("step1", [])
    total1 = sum(len(change[1]) for change in step1)
    lines.append("Merged %d file(s), %d key(s)." % (len([c for c in step1 if c[1]]), total1))
    for rel, changes in step1:
        lines.append("- %s: %d key(s)" % (rel, len(changes)))
        for key, old_value, new_value in changes[:15]:
            lines.append("  - %s %s -> %s" % (key, old_value, new_value))
        if len(changes) > 15:
            lines.append("  - ... %d more" % (len(changes) - 15))
    deleted = f3.get("step1_deleted", [])
    lines.append("- deleted single-name copies: %s" % (", ".join(deleted) if deleted else "none"))
    skipped1 = f3.get("step1_skipped", [])
    if skipped1:
        lines.append("- skipped: %s" % "; ".join("%s (%s)" % (r, why) for r, why in skipped1))
    lines.append("")
    lines.append("### Step 2: copied as-is")
    lines.append("")
    copied2 = f3.get("step2_copied", [])
    lines.append("Copied %d file(s) from the old instance." % len(copied2))
    for rel in copied2[:15]:
        lines.append("- %s" % rel)
    if len(copied2) > 15:
        lines.append("- ... %d more" % (len(copied2) - 15))
    skipped2 = f3.get("step2_skipped", [])
    if skipped2:
        lines.append("Skipped:")
        for rel, reason in skipped2:
            lines.append("- %s (%s)" % (rel, reason))
    lines.append("")
    lines.append("### Step 3: line-based scalar merges")
    lines.append("")
    step3 = f3.get("step3", [])
    total3 = sum(len(change[1]) for change in step3)
    lines.append("Merged %d file(s), %d key(s)." % (len([c for c in step3 if c[1]]), total3))
    for rel, changes in step3:
        lines.append("- %s: %d key(s)" % (rel, len(changes)))
        for key, old_value, new_value in changes[:15]:
            lines.append("  - %s %s -> %s" % (key, old_value, new_value))
        if len(changes) > 15:
            lines.append("  - ... %d more" % (len(changes) - 15))
    skipped3 = f3.get("step3_skipped", [])
    if skipped3:
        lines.append("Skipped:")
        for rel, reason in skipped3:
            lines.append("- %s (%s)" % (rel, reason))
    lines.append("")
    lines.append("### Step 4: lostcities display text")
    lines.append("")
    step4 = f3.get("step4")
    if step4 and step4[0] not in (None, "missing"):
        lines.append("- %s extraDescription: %s -> %s" % (STEP4_PROFILE, step4[0], step4[1]))
    elif step4 and step4[0] == "missing":
        lines.append("- %s missing in the new instance" % STEP4_PROFILE)
    else:
        lines.append("- %s extraDescription already up to date" % STEP4_PROFILE)
    lines.append("")
    lines.append("### F3 idempotency and validation")
    lines.append("")
    current = f3.get("current", {})
    lines.append("- current run keys changed: %d" % current.get("keys_changed", 0))
    lines.append("- current run files copied: %d" % current.get("copied", 0))
    lines.append("- current run files deleted: %d" % current.get("deleted", 0))
    lines.append("- current run step 4 changed: %s" % ("yes" if current.get("step4_changed") else "no"))
    lines.append("- TOML validation: %d pass / %d fail" % (validation["toml_pass"], validation["toml_fail"]))
    lines.append("- JSON validation: %d pass / %d fail" % (validation["json_pass"], validation["json_fail"]))
    for rel, reason in validation_failures:
        lines.append("- validation failure: %s (%s)" % (rel, reason))
    REPORT_PATH.write_text(REPORT_PATH.read_text(encoding="utf-8") + "\n".join(lines), encoding="utf-8")


def write_report(report_stats, current, backup_path):
    lines = []
    lines.append("# Config port report")
    lines.append("")
    lines.append("Source: old 1.20.1 instance (read-only). Target: new 1.21.1 instance.")
    lines.append("")
    lines.append("## Counts")
    lines.append("")
    lines.append("- merged files: %d" % len(report_stats.get("merged", [])))
    lines.append("- keys changed: %d" % report_stats.get("keys_changed", 0))
    lines.append("- copied files: %d" % len(report_stats.get("copied", [])))
    lines.append("- manual files: %d" % len(report_stats.get("manual", [])))
    lines.append("- skipped files (mod not installed): %d" % len(report_stats.get("skipped", [])))
    lines.append("- errors: %d" % len(report_stats.get("errors", [])))
    if backup_path:
        lines.append("- backup: %s" % backup_path)
    val = report_stats.get("validation", {})
    lines.append("- TOML validation: %d pass / %d fail" % (val.get("toml_pass", 0), val.get("toml_fail", 0)))
    lines.append("- JSON validation: %d pass / %d fail" % (val.get("json_pass", 0), val.get("json_fail", 0)))
    current_keys = report_stats.get("current_keys_changed", current["keys_changed"])
    lines.append("- idempotency run keys changed: %d" % current_keys)
    lines.append("")
    lines.append("## Merged files")
    lines.append("")
    for rel, count in report_stats.get("merged", []):
        lines.append("- %s: %d keys" % (rel, count))
    if not report_stats.get("merged"):
        lines.append("- none")
    lines.append("")
    lines.append("## Copied files")
    lines.append("")
    for rel in report_stats.get("copied", []):
        lines.append("- %s" % rel)
    if not report_stats.get("copied"):
        lines.append("- none")
    lines.append("")
    lines.append("## Dropped resource ids")
    lines.append("")
    for rel, entry in report_stats.get("dropped", []):
        lines.append("- %s: %s" % (rel, entry))
    if not report_stats.get("dropped"):
        lines.append("- none")
    lines.append("")
    lines.append("## Sunlit occurrences in written files")
    lines.append("")
    for rel, lineno, action, snippet in report_stats.get("sunlit", []):
        lines.append("- %s:%d: %s: %s" % (rel, lineno, action, snippet))
    if not report_stats.get("sunlit"):
        lines.append("- none")
    lines.append("")
    lines.append("## Errors")
    lines.append("")
    for rel, reason in report_stats.get("errors", []):
        lines.append("- %s: %s" % (rel, reason))
    if not report_stats.get("errors"):
        lines.append("- none")
    lines.append("")
    lines.append("## Manual files")
    lines.append("")
    lines.append("Format: path (new instance has the file / lacks the file).")
    for rel, has_new in sorted(report_stats.get("manual", [])):
        lines.append("- %s (%s)" % (rel, "has" if has_new else "lacks"))
    if not report_stats.get("manual"):
        lines.append("- none")
    lines.append("")
    lines.append("## Skipped files")
    lines.append("")
    for rel, reason in sorted(report_stats.get("skipped", [])):
        lines.append("- %s (%s)" % (rel, reason))
    if not report_stats.get("skipped"):
        lines.append("- none")
    lines.append("")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
