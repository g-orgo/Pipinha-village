#!/usr/bin/env python3
"""Read-only scan: item/block ids and textures referenced by the pack that do not exist in 1.21.1.

Writes only IDSCAN.md and idscan_renames.json next to this script. Run with: python3 -I check_ids.py
"""
import collections
import difflib
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KJS = ROOT / "kubejs"
OLD_MODS = ROOT.parent / "Society: Sunlit Valley" / "mods"
# The versions jar is the only 1.21.1 client jar that carries assets/ and data/ (the srg/slim jars do not).
CLIENT_JAR = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Install/versions/1.21.1/1.21.1.jar")
TEMPLATE_CREATE_RE = re.compile(r'\.create\(\s*`([a-z0-9_.-]+):\$\{')
TYPE_KEY_RE = re.compile(r'"(type|trigger|condition|function|tag)"\s*:\s*$')

ID_RE = re.compile(r'["\']([a-z][a-z0-9_.-]*):([a-z0-9_./-]+)["\']')
CREATE_RE = re.compile(r'\.create\(\s*["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\']')
CROP_RE = re.compile(r'\.crop\(\s*["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\']')
LOOT_NAME_RE = re.compile(r'"name"\s*:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"')
ASSET_RE = re.compile(r'assets/([a-z0-9_.-]+)/(models/item|blockstates|textures)/(.+)\.(json|png)$')
LOOT_RE = re.compile(r'data/([a-z0-9_.-]+)/loot_table/(blocks/)?(.+)\.json$')
# Lines that are clearly not item/block usage (sounds, entities, recipe ids, worldgen, etc.).
SKIP_RE = re.compile(r'sound|particle|entit|advancement|loot|biome|dimension|enchant|villager|profession|'
                     r'structure|damage|worldgen|predicate|painting|\bid\s*:|"id"|lostcities|sunlit_towns', re.I)
# Lines that look like item/block usage. Anything else that survives is marked "maybe".
# Structural keys and registry constants that look like ids but are not items or blocks.
NOT_ITEM = {"minecraft:item", "minecraft:block", "minecraft:air", "minecraft:crafting_shaped",
            "minecraft:crafting_shapeless", "minecraft:uniform", "minecraft:set_count",
            "minecraft:explosion_decay", "minecraft:binomial", "forge:conditions", "forge:false",
            "forge:true", "shippingbin:crop_sell_multiplier"}
ITEM_RE = re.compile(r'item|block|ingredient|output|input|result|stack|give|ore|seed|bucket|fluid|crop|slot|'
                     r'shaped|shapeless|smelt|cook|sell|price|food|tool', re.I)


def collect(jars):
    """Return known ids (with source), known textures, namespaces, en_us lang and loot tables."""
    known, textures, namespaces, lang, loot = {}, set(), set(), {}, []
    for jp in jars:
        try:
            z = zipfile.ZipFile(jp)
        except (OSError, zipfile.BadZipFile) as exc:
            print(f"warn: cannot open {jp}: {exc}", file=sys.stderr)
            continue
        src = jp.name
        for n in z.namelist():
            m = ASSET_RE.match(n)
            if m:
                ns, folder, path, ext = m.groups()
                namespaces.add(ns)
                if folder == "textures" and ext == "png":
                    textures.add(f"{ns}:{path}")
                elif ext == "json" and folder == "models/item":
                    known.setdefault(f"{ns}:{path}", src)
                elif ext == "json" and folder == "blockstates":
                    known.setdefault(f"{ns}:{path}", src)
                continue
            m = LOOT_RE.match(n)
            if m:
                ns, is_block, path = m.groups()
                namespaces.add(ns)
                text = z.read(n).decode("utf-8", "ignore")
                ids = set(LOOT_NAME_RE.findall(text))
                loot.append({"ns": ns, "base": path.split("/")[-1], "ids": ids, "file": f"{src}!{n}"})
                if is_block:
                    known.setdefault(f"{ns}:{path}", src)
                continue
            m = re.match(r'data/([a-z0-9_.-]+)/', n)
            if m:
                namespaces.add(m.group(1))
            m = re.match(r'assets/([a-z0-9_.-]+)/lang/en_us\.json$', n)
            if m:
                try:
                    lang.update(json.loads(z.read(n).decode("utf-8", "ignore")))
                except json.JSONDecodeError:
                    pass
    return known, textures, namespaces, lang, loot


def kjs_sources():
    for folder in ("startup_scripts", "server_scripts", "client_scripts"):
        yield from sorted((KJS / folder).rglob("*.js"))
    yield from sorted((KJS / "data").rglob("*.json"))


def main():
    for p in (CLIENT_JAR,):
        if not p.exists():
            sys.exit(f"missing client jar: {p}")
    new_jars = sorted(ROOT.joinpath("mods").glob("*.jar"))
    old_jars = sorted(OLD_MODS.glob("*.jar"))
    if not new_jars:
        sys.exit("no jars in new mods folder")

    known, textures, namespaces, lang_new, loot_new = collect(new_jars + [CLIENT_JAR])
    old_known, _, old_ns, lang_old, loot_old = collect(old_jars)
    namespaces.add("minecraft")

    # KubeJS-created ids (startup scripts) and kubejs assets.
    kjs_ids = {}
    for f in sorted((KJS / "startup_scripts").rglob("*.js")):
        text = f.read_text("utf-8", "ignore")
        for m in CREATE_RE.finditer(text):
            cid = m.group(1)
            ns = cid.split(":")[0]
            namespaces.add(ns)
            kjs_ids.setdefault(cid, "kubejs-create")
            window = text[m.end(): m.end() + 800]
            nxt = window.find(".create(")
            window = window[:nxt] if nxt != -1 else window
            if re.search(r"[Bb]ucket|[Ff]luid", window):
                kjs_ids.setdefault(cid + "_bucket", "kubejs-fluid guess")
        # Template creations: e.create(`ns:${item}`) inside an array literal followed by ].forEach(...)
        for m in TEMPLATE_CREATE_RE.finditer(text):
            ns = m.group(1)
            namespaces.add(ns)
            end = text.rfind("].forEach", 0, m.start())
            begin = text.rfind("[", 0, end) if end != -1 else -1
            if begin == -1:
                continue
            for name in re.findall(r'["\']([a-z0-9_]+)["\']', text[begin:end]):
                kjs_ids.setdefault(f"{ns}:{name}", "kubejs-create (array loop)")
        for m in CROP_RE.finditer(text):
            cid = m.group(1)
            namespaces.add(cid.split(":")[0])
            kjs_ids.setdefault(cid, "kubejs-crop")
            kjs_ids.setdefault(cid + "_seeds", "kubejs-crop seed guess")
    for k, v in kjs_ids.items():
        known.setdefault(k, v)

    # Textures and item/block models from kubejs/assets.
    model_refs = collections.defaultdict(set)  # texture key -> files
    for f in sorted((KJS / "assets").rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(KJS / "assets").as_posix()
        m = re.match(r'([a-z0-9_.-]+)/textures/(.+)\.png$', rel)
        if m:
            textures.add(f"{m.group(1)}:{m.group(2)}")
            namespaces.add(m.group(1))
            continue
        m = re.match(r'([a-z0-9_.-]+)/(models/item|blockstates)/(.+)\.json$', rel)
        if m:
            # A model file alone does not register an item: do not count it as known.
            namespaces.add(m.group(1))
        if rel.endswith(".json") and "/models/" in rel:
            try:
                data = json.loads(f.read_text("utf-8", "ignore"))
            except json.JSONDecodeError:
                continue
            for val in (data.get("textures") or {}).values():
                if isinstance(val, str) and not val.startswith("#"):
                    key = val if ":" in val else f"minecraft:{val}"
                    model_refs[key].add(rel)

    # Item/block id references in scripts and kubejs data.
    refs = collections.defaultdict(lambda: {"files": set(), "maybe": set()})
    skipped_ns = collections.Counter()
    scanned = 0
    for f in kjs_sources():
        rel = f.relative_to(ROOT).as_posix()
        if "lostcities" in rel or "sunlit_towns" in rel:
            continue
        scanned += 1
        for line in f.read_text("utf-8", "ignore").splitlines():
            if SKIP_RE.search(line):
                continue
            for m in ID_RE.finditer(line):
                ns, path = m.group(1), m.group(2)
                key = f"{ns}:{path}"
                if ns not in namespaces:
                    if ns in old_ns:
                        skipped_ns[ns] += 1
                    continue
                if key in known or key in NOT_ITEM or TYPE_KEY_RE.search(line[:m.start()]):
                    continue
                if path.startswith(("textures/", "recipes/")) or path.startswith("mineable/") \
                        or path.startswith("needs_") or path.endswith(".png"):
                    continue
                refs[key]["files"].add(rel)
                if not ITEM_RE.search(line):
                    refs[key]["maybe"].add(rel)

    # Rename evidence and proposals.
    by_ns = collections.defaultdict(list)
    for k in known:
        by_ns[k.split(":")[0]].append(k.split(":", 1)[1])

    def lang_name(table, ns, path):
        for t in ("item", "block"):
            v = table.get(f"{t}.{ns}.{path}")
            if isinstance(v, str) and v:
                return v
        return None

    name_index = collections.defaultdict(list)
    for lk, lv in lang_new.items():
        if isinstance(lv, str) and lk.split(".")[0] in ("item", "block"):
            name_index[lv.lower()].append(lk)

    rows = []
    for key in refs:
        ns, path = key.split(":", 1)
        proposal, conf, evidence = "none", "none", "no candidate"
        name = lang_name(lang_old, ns, path)
        if name:
            cands = set()
            for lk in name_index.get(name.lower(), ()):
                parts = lk.split(".", 2)
                if len(parts) == 3 and f"{parts[1]}:{parts[2]}" in known:
                    cands.add(f"{parts[1]}:{parts[2]}")
            same = [c for c in cands if c.startswith(ns + ":")]
            pick = same if same else list(cands)
            if len(pick) == 1:
                proposal, conf = pick[0], "high"
                evidence = f'same display name "{name}"'
            elif pick:
                evidence = f'display name "{name}" matches {len(pick)} ids'
        if conf != "high":
            old_bases = {e["base"] for e in loot_old if e["ns"] == ns and key in e["ids"]}
            lc = set()
            for e in loot_new:
                if e["ns"] == ns and e["base"] in old_bases:
                    for i in e["ids"]:
                        if i.startswith(ns + ":") and i in known and i not in old_known:
                            lc.add((i, e["base"]))
            if len({i for i, _ in lc}) == 1:
                i, base = next(iter(lc))
                proposal, conf = i, "high"
                evidence = f"loot table {ns}:{base} drops it in 1.21.1 (same table name)"
            elif lc:
                evidence = "loot tables share name with " + ", ".join(sorted({i for i, _ in lc})[:3])
        if conf != "high":
            pool = by_ns.get(ns, [])
            close = difflib.get_close_matches(path, pool, n=1, cutoff=0.6)
            if close:
                proposal, conf = f"{ns}:{close[0]}", "low"
                evidence = f"fuzzy name match ({difflib.SequenceMatcher(None, path, close[0]).ratio():.2f})"
        rows.append({"id": key, "files": refs[key]["files"], "maybe": len(refs[key]["maybe"]),
                     "proposal": proposal, "conf": conf, "evidence": evidence})
    rows.sort(key=lambda r: (-len(r["files"]), r["id"]))

    # Textures.
    tex_rows = []
    for key, files in sorted(model_refs.items()):
        if key in textures:
            continue
        ns, path = key.split(":", 1)
        close = difflib.get_close_matches(path, [t.split(":", 1)[1] for t in textures if t.startswith(ns + ":")],
                                          n=1, cutoff=0.6)
        if close:
            tex_rows.append((key, files, f"{ns}:{close[0]}", "low", "fuzzy name match"))
        else:
            tex_rows.append((key, files, "none", "none", "no candidate"))

    high = {r["id"]: r["proposal"] for r in rows if r["conf"] == "high"}
    unknown_item = sum(1 for r in rows if len(r["files"]) > r["maybe"])
    counts = collections.Counter(r["conf"] for r in rows)
    total_files = {f for r in rows for f in r["files"]}

    def cell(s):
        return str(s).replace("|", "/")

    out = [
        "# IDSCAN: ids and textures missing in 1.21.1",
        "",
        "Generated by `tools/kjsport/check_ids.py` (read-only). Scanned new jars, client jar, kubejs scripts and kubejs/data.",
        "",
        "## Summary",
        "",
        f"- Known ids (jars + client + kubejs-created): {len(known)}",
        f"- Known textures: {len(textures)}",
        f"- Script/data files scanned: {scanned} (files with unknown refs: {len(total_files)})",
        f"- Unknown ids: {len(rows)} (item-like context: {unknown_item}, maybe: {len(rows) - unknown_item})",
        f"- Proposals: high {counts['high']}, low {counts['low']}, none {counts['none']}",
        f"- Missing textures in kubejs models: {len(tex_rows)}",
        f"- Referenced namespaces present in old instance but not installed in 1.21.1: "
        + (", ".join(f"{k} ({v})" for k, v in skipped_ns.most_common()) or "none"),
        "",
        "Note: `_seeds` and `_bucket` ids created by KubeJS are guesses (confidence not applied to them).",
        "",
        "## Unknown ids",
        "",
        "| id | files (count) | proposal | confidence | evidence |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        files = f"{len(r['files'])}" + (f" ({r['maybe']} maybe)" if r["maybe"] else "")
        out.append(f"| {cell(r['id'])} | {files} | {cell(r['proposal'])} | {r['conf']} | {cell(r['evidence'])} |")
    out += ["", "## Missing textures (kubejs/assets models)", "",
            "| texture | files (count) | proposal | confidence | evidence |", "|---|---|---|---|---|"]
    for key, files, prop, conf, ev in tex_rows:
        out.append(f"| {cell(key)} | {len(files)} | {cell(prop)} | {conf} | {cell(ev)} |")
    (HERE / "IDSCAN.md").write_text("\n".join(out) + "\n", "utf-8")
    (HERE / "idscan_renames.json").write_text(json.dumps(dict(sorted(high.items())), indent=2) + "\n", "utf-8")

    print(f"known={len(known)} textures={len(textures)} unknown={len(rows)} "
          f"high={counts['high']} low={counts['low']} none={counts['none']} missing_textures={len(tex_rows)}")
    for r in rows[:10]:
        print(f"{r['id']} | {len(r['files'])} | {r['proposal']} | {r['conf']}")


if __name__ == "__main__":
    main()
