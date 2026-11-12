#!/usr/bin/env python3
# Mechanical KubeJS 6 -> 7 port of the OLD scripts into Pipinha's Village.
# Regenerates kubejs/{startup_scripts,server_scripts,client_scripts,assets} from OLD,
# applies the proven rewrites and writes tools/kjsport/WORKLIST.md.
# Usage: python3 -I tools/kjsport/mechanical.py   (idempotent)
import datetime
import hashlib
import io
import json
import re
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

NEW = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village")
OLD = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley")
KJS = NEW / "kubejs"
OLD_KJS = OLD / "kubejs"
FOLDERS = ["startup_scripts", "server_scripts", "client_scripts", "assets"]
TOOLS = NEW / "tools" / "kjsport"
SYNTAX = TOOLS / "syntax"
MODS = NEW / "mods"
NEOFORGE_JAR = Path("/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries/"
                    "net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar")
DROPPED_SRC = NEW / "tools" / "dataport" / "REPORT.md"
RECON = TOOLS / "api_diff.json"
MANIFEST = TOOLS / "generated.json"
WORKLIST = TOOLS / "WORKLIST.md"

# Proven renames (old -> new). Order matters: JEIAddedEvents first, then JEIEvents.*.
RENAMES = [
    ("ForgeEvents.onEvent(", "NativeEvents.onEvent("),
    ("JEIAddedEvents.", "JEIEvents."),
    ("EntityEvents.hurt(", "EntityEvents.beforeHurt("),
    ("ItemEvents.tooltip(", "ItemEvents.modifyTooltips("),
    ("JEIEvents.addItems(", "RecipeViewerEvents.addEntries("),
    ("JEIEvents.hideItems(", "RecipeViewerEvents.removeEntries("),
    ("JEIEvents.removeCategories(", "RecipeViewerEvents.removeCategories("),
    ("ServerEvents.highPriorityData(", "ServerEvents.generateData("),
]
MANUAL = {"rename", "s1_event", "forge_unresolved", "recon_class", "tag_kept",
          "dropped_id", "nbt", "global", "syntax"}
APPLIED = {"display", "forge_rewritten", "tag_rewritten", "id_rename"}

FQ_RE = re.compile(r"net\.minecraftforge\.[A-Za-z0-9_.$]+")
TAG_HASH_RE = re.compile(r"#forge:([A-Za-z0-9_./-]+)")
TAG_QUOTE_RE = re.compile(r"(['\"])forge:([A-Za-z0-9_./-]+)\1")
TAG_ENTRY_RE = re.compile(r"^data/c/tags/items?/(.+)\.json$")
LARGE_RE = re.compile(r"(?<![\w$])largemeals:")
STR_RE = re.compile(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"|`[^`]*`")
PHRASE_RE = re.compile(r"Society: Sunlit Valley|Sunlit Valley")
GLOBAL_RE = re.compile(r"(?<![\w$.])global\.[A-Za-z_$][\w$]*\s*=(?!=)")


def rd(p):
    return p.read_bytes().decode("utf-8", "surrogateescape")


def wr(p, s):
    p.write_bytes(s.encode("utf-8", "surrogateescape"))


def lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def tree(root):
    out = []
    for f in FOLDERS:
        base = root / f
        if not base.exists():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file():
                out.append([p.relative_to(root).as_posix(),
                            hashlib.sha1(p.read_bytes()).hexdigest()])
    return out


def step1_copy():
    """Back up foreign NEW content once, then regenerate the four folders from OLD."""
    current = tree(KJS)
    prev = json.loads(rd(MANIFEST))["tree"] if MANIFEST.exists() else None
    backup = None
    if current and current != prev:
        backup = TOOLS / ("backup-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        for f in FOLDERS:
            if (KJS / f).exists():
                shutil.copytree(KJS / f, backup / f)
    for f in FOLDERS:
        if (KJS / f).exists():
            shutil.rmtree(KJS / f)
        shutil.copytree(OLD_KJS / f, KJS / f)
    return backup


def sub_sites(text, rel, pattern, repl, sites):
    """repl(match) -> (new_text_or_None, category, note). None keeps the text and only lists the site."""
    out, last = [], 0
    for m in pattern.finditer(text):
        new, cat, note = repl(m)
        sites.append(dict(rel=rel, line=lineno(text, m.start()), cat=cat, note=note))
        out.append(text[last:m.start()])
        out.append(new if new is not None else m.group(0))
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def neo_index():
    idx = defaultdict(list)
    with zipfile.ZipFile(NEOFORGE_JAR) as z:
        for n in z.namelist():
            if not n.endswith(".class"):
                continue
            base = n[:-6]
            if base.rsplit("/", 1)[-1] in ("module-info", "package-info"):
                continue
            fq = base.replace("/", ".")
            idx[fq.rsplit(".", 1)[-1]].append(fq)
    return idx


def forge_map(texts):
    idx = neo_index()
    mapping, unresolved = {}, {}
    for text in texts:
        for m in FQ_RE.finditer(text):
            parts = m.group(0).split(".")
            k = next((i for i, p in enumerate(parts) if p[:1].isupper()), None)
            if k is None:
                continue
            prefix = ".".join(parts[:k + 1])
            if prefix in mapping or prefix in unresolved:
                continue
            cands = idx.get(parts[k], [])
            if len(cands) == 1:
                mapping[prefix] = cands[0]
            else:
                unresolved[prefix] = len(cands)
    return mapping, unresolved


def item_tags():
    names = set()

    def scan(zf, depth):
        for n in zf.namelist():
            m = TAG_ENTRY_RE.match(n)
            if m:
                names.add(m.group(1))
            elif n.endswith(".jar") and depth < 2:
                try:
                    scan(zipfile.ZipFile(io.BytesIO(zf.read(n))), depth + 1)
                except zipfile.BadZipFile:
                    pass

    for jar in sorted(MODS.glob("*.jar")):
        with zipfile.ZipFile(jar) as z:
            scan(z, 0)
    return names


def apply_forge(text, rel, sites, mapping, unresolved):
    keys = sorted(set(mapping) | set(unresolved), key=len, reverse=True)
    if not keys:
        return text
    pat = re.compile(r"(?<![\w.])(?:" + "|".join(map(re.escape, keys)) + r")(?![\w])")

    def repl(m):
        p = m.group(0)
        if p in mapping:
            return mapping[p], "forge_rewritten", f"{p} -> {mapping[p]}"
        return None, "forge_unresolved", f"{p}: no unique NeoForge class ({unresolved[p]} candidates)"

    return sub_sites(text, rel, pat, repl, sites)


def apply_tags(text, rel, sites, item_set):
    def hash_repl(m):
        n = m.group(1)
        if n in item_set:
            return "#c:" + n, "tag_rewritten", f"#forge:{n} -> #c:{n}"
        return None, "tag_kept", f"#forge:{n} kept (no item tag c:{n} in mods)"

    def quote_repl(m):
        q, n = m.group(1), m.group(2)
        if n in item_set:
            return f"{q}c:{n}{q}", "tag_rewritten", f"forge:{n} -> c:{n}"
        return None, "tag_kept", f"{q}forge:{n}{q} kept (no item tag c:{n} in mods)"

    text = sub_sites(text, rel, TAG_HASH_RE, hash_repl, sites)
    return sub_sites(text, rel, TAG_QUOTE_RE, quote_repl, sites)


def display_pass(text, rel, sites):
    out, last = [], 0
    for lit in STR_RE.finditer(text):
        s = lit.group(0)
        if "Sunlit Valley" not in s:
            continue
        new_val = "Pipinha\\'s Village" if s[0] == "'" else "Pipinha's Village"
        pieces, pl = [], 0
        for pm in PHRASE_RE.finditer(s):
            sites.append(dict(rel=rel, line=lineno(text, lit.start() + pm.start()), cat="display",
                              note=f"{pm.group(0)} -> Pipinha's Village"))
            pieces.append(s[pl:pm.start()])
            pieces.append(new_val)
            pl = pm.end()
        pieces.append(s[pl:])
        out.append(text[last:lit.start()])
        out.append("".join(pieces))
        last = lit.end()
    out.append(text[last:])
    return "".join(out)


def apply_renames(text, rel, sites):
    for old, new in RENAMES:
        pat = re.compile(r"(?<![\w$.])" + re.escape(old))
        text = sub_sites(text, rel, pat,
                         lambda m, o=old, n=new: (n, "rename", f"{o.rstrip('(')} -> {n.rstrip('(')}: check callback"),
                         sites)
    return text


def dropped_ns():
    ns, on = [], False
    for line in rd(DROPPED_SRC).split("\n"):
        if line.startswith("## "):
            on = line.startswith("## Dropped mods")
            continue
        if on:
            ns += re.findall(r"`([a-z0-9_]+)`", line)
    return sorted(set(ns))


def load_syntax():
    res = {}
    for kind in ("new", "old"):
        f = SYNTAX / f"results_{kind}.txt"
        if not f.exists():
            res[kind] = None
            continue
        files, fails = set(), {}
        for line in rd(f).split("\n"):
            parts = line.split("\t")
            if len(parts) >= 2 and parts[0] in ("OK", "FAIL"):
                files.add(parts[1])
                if parts[0] == "FAIL":
                    fails[parts[1]] = (parts[2], parts[3] if len(parts) > 3 else "")
        res[kind] = {"files": files, "fails": fails}
    return res


def scan_manual(final, sites):
    recon = json.loads(rd(RECON))["sections"]
    renamed = {o.rstrip("(").rstrip(".") for o, _ in RENAMES}
    for sec, cat in (("1", "s1_event"), ("2", "recon_class"), ("6", "nbt")):
        for e in recon.get(sec, []):
            if sec != "6" and not e.get("issue"):
                continue
            if sec == "1" and e["key"] in renamed:
                continue
            for file, line in e["locations"]:
                rel = file[len("kubejs/"):] if file.startswith("kubejs/") else file
                if rel in final:
                    sites.append(dict(rel=rel, line=line, cat=cat, note=f"{e['key']}: {e.get('status', '')}"))
    ns = dropped_ns()
    alt = "|".join(sorted(map(re.escape, ns), key=len, reverse=True))
    drop_re = re.compile(r"(?<![\w$.-])(?:" + alt + r"):[\w./-]*")
    for rel, text in final.items():
        for m in drop_re.finditer(text):
            sites.append(dict(rel=rel, line=lineno(text, m.start()), cat="dropped_id", note=m.group(0)))
        if not rel.startswith("startup_scripts/"):
            for m in GLOBAL_RE.finditer(text):
                sites.append(dict(rel=rel, line=lineno(text, m.start()), cat="global",
                                  note="global assigned outside startup_scripts: " + m.group(0)))
    return len(ns)


def write_worklist(final, sites, syntax):
    by_file = defaultdict(list)
    for s in sites:
        by_file[s["rel"]].append(s)
    cols = ["rename", "s1_event", "forge_unresolved", "recon_class", "tag_kept", "dropped_id",
            "nbt", "global", "syntax", "syntax_preexisting", "display", "forge_rewritten",
            "tag_rewritten", "id_rename"]
    table = {f: Counter() for f in FOLDERS}
    need = Counter()
    nfiles = Counter(rel.split("/")[0] for rel in final)
    for rel, ss in by_file.items():
        folder = rel.split("/")[0]
        for s in ss:
            table[folder][s["cat"]] += 1
        if any(s["cat"] in MANUAL for s in ss):
            need[folder] += 1
    out = ["# KubeJS 6 -> 7 port worklist (Pipinha's Village)", "",
           "Generated by tools/kjsport/mechanical.py. Line numbers match OLD and NEW (no line is added or removed).",
           "Applied mechanically (no action needed): display, forge_rewritten, tag_rewritten, id_rename.",
           "Manual categories: rename (check callback), s1_event (event not registered in NEW), "
           "forge_unresolved, recon_class (recon S2), tag_kept, dropped_id, nbt (recon S6), global, syntax (new Rhino failure).", "",
           "## Summary", "",
           "| folder | js files | files needing work | " + " | ".join(cols) + " |",
           "|" + "---|" * (3 + len(cols))]
    tot = Counter()
    tot_files = tot_need = 0
    for f in FOLDERS:
        row = [str(nfiles[f]), str(need[f])] + [str(table[f][c]) for c in cols]
        out.append(f"| {f} | " + " | ".join(row) + " |")
        tot.update(table[f])
        tot_files += nfiles[f]
        tot_need += need[f]
    out.append("| **total** | " + " | ".join([str(tot_files), str(tot_need)] +
                                             [str(tot[c]) for c in cols]) + " |")
    out.append("")
    if syntax.get("new") is None:
        out.append("Syntax check: not run yet (results files missing).")
    else:
        nf = len(syntax["new"]["fails"])
        of = len(syntax["old"]["fails"]) if syntax.get("old") else "n/a"
        newonly = [r for r in syntax["new"]["fails"] if not (syntax.get("old") and r in syntax["old"]["fails"])]
        out.append(f"Syntax (Rhino 2101): NEW {len(syntax['new']['files'])} files, {nf} failures; "
                   f"OLD failures {of}; NEW failures not in OLD: {len(newonly)}.")
    out.append("")
    order = {f: i for i, f in enumerate(FOLDERS)}

    def manual_of(rel):
        return [s for s in by_file[rel] if s["cat"] in MANUAL]

    files = sorted([r for r in by_file if manual_of(r)],
                   key=lambda r: (order.get(r.split("/")[0], 9), -len(manual_of(r)), r))
    out += ["## Files needing manual work", ""]
    for rel in files:
        ms = sorted(manual_of(rel), key=lambda s: s["line"])
        out.append(f"### `kubejs/{rel}` ({len(ms)} sites)")
        lines = final.get(rel, "").split("\n")
        for s in ms:
            txt = lines[s["line"] - 1].strip().replace("`", "'")[:140] if 0 < s["line"] <= len(lines) else ""
            out.append(f"- L{s['line']} `{s['cat']}` {s['note']} | `{txt}`")
        out.append("")
    out += ["## Applied mechanically (listed for review)", ""]
    for rel in sorted(r for r in by_file if any(s["cat"] in APPLIED for s in by_file[r])):
        ms = sorted([s for s in by_file[rel] if s["cat"] in APPLIED], key=lambda s: s["line"])
        out.append(f"- `kubejs/{rel}`: " + "; ".join(f"L{s['line']} {s['note']}" for s in ms))
    out.append("")
    out += ["## Pre-existing syntax failures (OLD, not caused by the port)", ""]
    if syntax.get("old"):
        for rel, (line, msg) in sorted(syntax["old"]["fails"].items()):
            out.append(f"- `{rel}` L{line}: {msg[:120]}")
    out.append("")
    WORKLIST.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    TOOLS.mkdir(parents=True, exist_ok=True)
    backup = step1_copy()
    texts = {}
    for f in FOLDERS:
        for p in sorted((KJS / f).rglob("*.js")):
            texts[p] = rd(p)
    mapping, unresolved = forge_map(texts.values())
    item_set = item_tags()
    sites, final = [], {}
    for p, orig in texts.items():
        rel = p.relative_to(KJS).as_posix()
        text = apply_renames(orig, rel, sites)
        text = apply_forge(text, rel, sites, mapping, unresolved)
        text = sub_sites(text, rel, LARGE_RE,
                         lambda m: ("large_meals:", "id_rename", "largemeals: -> large_meals:"), sites)
        text = apply_tags(text, rel, sites, item_set)
        text = display_pass(text, rel, sites)
        if text != orig:
            wr(p, text)
        final[rel] = text
    ndrop = scan_manual(final, sites)
    syntax = load_syntax()
    if syntax.get("new"):
        for rel, (line, msg) in syntax["new"]["fails"].items():
            if rel in final:
                pre = syntax.get("old") and rel in syntax["old"]["fails"]
                sites.append(dict(rel=rel, line=int(line) if str(line).isdigit() else 0,
                                  cat="syntax_preexisting" if pre else "syntax", note=msg[:120]))
    write_worklist(final, sites, syntax)
    MANIFEST.write_text(json.dumps({"tree": tree(KJS)}, indent=1) + "\n", encoding="utf-8")
    c = Counter(s["cat"] for s in sites)
    print("backup:", backup.name if backup else "none (already generated)")
    print("js files:", len(texts), "| dropped namespaces:", ndrop)
    print("forge classes mapped:", len(mapping), "| unresolved:", len(unresolved), "| item tags:", len(item_set))
    print("counts:", dict(sorted(c.items())))


if __name__ == "__main__":
    main()
