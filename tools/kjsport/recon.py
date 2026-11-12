#!/usr/bin/env python3
"""Inventory of OLD (Society: Sunlit Valley, MC 1.20.1) KubeJS script API uses
that do not resolve against NEW (Pipinha's Village, MC 1.21.1) jars.

Read-only analysis. The OLD instance is never written. The only outputs are
API_DIFF.md and api_diff.json next to this script.

Run with: python3 -I tools/kjsport/recon.py
Stdlib only.
"""
import io
import json
import os
import re
import struct
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.abspath(os.path.join(HERE, "..", ".."))
OLD = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley"
LIBS = "/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries"
MAX_LOC = 10
BUILTIN_NS = {"minecraft", "kubejs"}
SCRIPT_DIRS = ["startup_scripts", "server_scripts", "client_scripts"]
OLD_LIB_JARS = [os.path.join(LIBS, "net/minecraftforge/forge/1.20.1-47.4.29/forge-1.20.1-47.4.29-universal.jar")]
MC_LIB_JARS = [
    os.path.join(LIBS, "net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar"),
    os.path.join(LIBS, "net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar"),
]
EVENT_JAR_RE = re.compile(r"kubejs|lootjs|morejs|ponderjs|entityjs|jade|ftb|additions", re.I)
JDK_PREFIXES = ("java.", "javax.", "jdk.", "sun.")
OBJECT_MEMBERS = {"toString", "equals", "hashCode", "getClass", "notify", "notifyAll", "wait", "clone",
                  "finalize", "class"}
ALIASES = {"JEIAddedEvents": "JEIEvents"}

SECTION_TITLES = {
    1: "1. Event groups and names not registered in NEW",
    2: "2. Java.loadClass classes (OLD, NEW, MC/NeoForge 1.21.1)",
    3: "3. Member accesses on loadClass aliases (NEW, MC and superclasses)",
    4: "4. Recipe types ns:id used in custom() or event.recipes.ns.id()",
    5: "5. Registry builder types and chained methods (heuristic)",
    6: "6. NBT-era API hits per file",
    7: "7. Item-id namespaces not in tools/modcheck/modids.txt",
}

RE_NAME = re.compile(r"^(?:[a-z][A-Za-z]+|[A-Z][A-Z_]+)$")
RE_GROUP = re.compile(r"^[A-Z][A-Za-z]+Events$")
EVENT_CALL = re.compile(r"\b([A-Z]\w*Events)\.(\w+)\s*\(")
LOAD = re.compile(r"Java\.loadClass\(\s*[\"']([\w.$]+)[\"']\s*\)")
ALIAS_DEF = re.compile(r"\b(?:var|let|const)\s+(\w+)\s*=\s*Java\.loadClass\(\s*[\"']([\w.$]+)[\"']\s*\)")
RECIPE_CUSTOM = re.compile(r"custom\s*\(\s*\{[^}]*?\btype\s*:\s*[\"']([a-z0-9_.-]+):([a-z0-9_./-]+)[\"']")
RECIPE_CALL = re.compile(r"event\.recipes\.([a-z0-9_]+)\.([a-z0-9_]+)\s*\(")
REG_CALL = re.compile(r"StartupEvents\.registry\(\s*[\"']([^\"']+)[\"']")
CREATE_CHAIN = re.compile(
    r"\.create\(\s*[\"'][^\"']*[\"'](?:\s*,\s*[\"'][^\"']*[\"'])?\s*\)"
    r"((?:\s*\.\w+\s*\((?:[^()]|\([^()]*\))*\))*)"
)
CHAIN_NAME = re.compile(r"\.(\w+)\s*\(")
NS_LITERAL = re.compile(r"[\"']([a-z][a-z0-9_.-]*):([a-z0-9_./-]+)[\"']")
NON_MOD_NS = {"http", "https", "file"}
NBT_RE = re.compile(r"\.nbt\b|\.(?:get|set)Nbt\(|\.(?:get|set)Tag\(|\bCompoundTag\b|\bNBT\b")
COLON_BYTES = re.compile(rb"[a-z0-9_.-]{1,64}:[a-z0-9_./-]{1,128}")
MODID_RE = re.compile(r'modId\s*=\s*"([^"]+)"')

STATS = {}
NEW_IDX = MC_IDX = OLD_IDX = None
MODIDS = set()
EV_CLASSES = []      # (simple, names_if_events_path, names_all, strings)
BASES = set()
KNOWN_STRINGS = set()
GRP_MEMO = {}
COLON = set()
DATA_NS = set()
MODS_BY_ID = defaultdict(list)
UTF_NS = {}
KJS_UTF = set()


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def norm(s):
    return s.replace("_", "").lower()


def is_jdk(c):
    return c.startswith(JDK_PREFIXES)


def jars_in(d):
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, n) for n in os.listdir(d) if n.endswith(".jar"))


def walk_jar(zf, depth=0):
    """Yield (ZipFile, entry name) for zf and for jars nested under META-INF/jar*."""
    names = zf.namelist()
    for n in names:
        yield zf, n
    if depth < 3:
        for n in names:
            if n.endswith(".jar") and n.startswith("META-INF/jar"):
                try:
                    sub = zipfile.ZipFile(io.BytesIO(zf.read(n)))
                except (zipfile.BadZipFile, KeyError):
                    continue
                yield from walk_jar(sub, depth + 1)


def parse_class(data):
    """Minimal class-file parser: super, interfaces, field and method names, UTF8 constants."""
    if data[:4] != b"\xca\xfe\xba\xbe":
        return None
    count = struct.unpack_from(">H", data, 8)[0]
    pos = 10
    cp = [None] * count
    i = 1
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            ln = struct.unpack_from(">H", data, pos)[0]
            cp[i] = (1, data[pos + 2:pos + 2 + ln].decode("utf-8", "replace"))
            pos += 2 + ln
        elif tag in (7, 8, 16, 19, 20):
            cp[i] = (tag, struct.unpack_from(">H", data, pos)[0])
            pos += 2
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            pos += 4
        elif tag in (5, 6):
            pos += 8
            i += 1
        elif tag == 15:
            pos += 3
        else:
            return None
        i += 1

    def utf(idx):
        e = cp[idx] if 0 < idx < count else None
        return e[1] if e and e[0] == 1 else ""

    def cls(idx):
        e = cp[idx] if 0 < idx < count else None
        return utf(e[1]).replace("/", ".") if e and e[0] == 7 else None

    _, _, super_i, n_if = struct.unpack_from(">HHHH", data, pos)
    pos += 8
    ifaces = []
    for _ in range(n_if):
        ifaces.append(cls(struct.unpack_from(">H", data, pos)[0]))
        pos += 2

    def read_members(p):
        n = struct.unpack_from(">H", data, p)[0]
        p += 2
        out = []
        for _ in range(n):
            _, name_i, desc_i, n_attr = struct.unpack_from(">HHHH", data, p)
            p += 8
            for _ in range(n_attr):
                ln = struct.unpack_from(">I", data, p + 2)[0]
                p += 6 + ln
            out.append((utf(name_i), utf(desc_i)))
        return out, p

    fields, pos = read_members(pos)
    methods, pos = read_members(pos)
    return {
        "super": cls(super_i) if super_i else None,
        "ifaces": [x for x in ifaces if x],
        "fields": {n for n, _ in fields},
        "methods": [(n, d) for n, d in methods if n not in ("<init>", "<clinit>")],
        "utf": {e[1] for e in cp if e and e[0] == 1},
    }


class ClassIndex:
    def __init__(self, jars):
        self.entries = {}
        self.simple = defaultdict(list)
        self.cache = {}
        for path in jars:
            try:
                top = zipfile.ZipFile(path)
            except (zipfile.BadZipFile, OSError):
                continue
            for zf, n in walk_jar(top):
                if n.endswith(".class") and not n.startswith("META-INF/"):
                    dotted = n[:-6].replace("/", ".")
                    if dotted not in self.entries:
                        self.entries[dotted] = (zf, n)
                        self.simple[dotted.rsplit(".", 1)[-1]].append(dotted)

    def info(self, dotted):
        if dotted not in self.cache:
            zf, n = self.entries[dotted]
            self.cache[dotted] = parse_class(zf.read(n))
        return self.cache[dotted]


def find_info(dotted):
    for idx in (NEW_IDX, MC_IDX):
        if dotted in idx.entries:
            return idx.info(dotted)
    return None


def resolvable(dotted):
    return is_jdk(dotted) or dotted in NEW_IDX.entries or dotted in MC_IDX.entries


def members_chain(start):
    """Field and method names of a class plus its superclasses and interfaces (NEW, then MC)."""
    fields, methods = set(), set()
    stack, seen = [start], set()
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        inf = find_info(c)
        if inf is None:
            continue
        fields |= inf["fields"]
        methods |= {n for n, _ in inf["methods"]}
        stack.extend(inf["ifaces"])
        if inf["super"]:
            stack.append(inf["super"])
    return fields, methods


def entry(sec, key, status, locs, issue, note="", detail=None):
    return {"section": sec, "key": key, "status": status,
            "locations": [list(x) for x in locs], "issue": issue,
            "note": note, "detail": detail or {}}


def load_scripts():
    files = []
    for d in SCRIPT_DIRS:
        base = os.path.join(OLD, "kubejs", d)
        for root, _, names in os.walk(base):
            for n in names:
                if n.endswith(".js"):
                    p = os.path.join(root, n)
                    with open(p, encoding="utf-8", errors="replace") as f:
                        files.append((os.path.relpath(p, OLD), f.read(), d))
    return sorted(files)


def load_modids():
    p = os.path.join(NEW, "tools", "modcheck", "modids.txt")
    with open(p, encoding="utf-8") as f:
        return {ln.strip() for ln in f if ln.strip() and not ln.startswith("#")}


def build_event_index():
    for path in jars_in(os.path.join(NEW, "mods")):
        if not EVENT_JAR_RE.search(os.path.basename(path)):
            continue
        for zf, n in walk_jar(zipfile.ZipFile(path)):
            if not n.endswith(".class") or n.startswith("META-INF/"):
                continue
            dotted = n[:-6].replace("/", ".")
            inf = parse_class(zf.read(n))
            if inf is None:
                continue
            simple = dotted.rsplit(".", 1)[-1]
            strs = inf["utf"]
            names_all = {norm(s) for s in strs if RE_NAME.match(s)}
            names_ev = names_all if "Events" in dotted else set()
            BASES.add(simple.split("$")[0])
            KNOWN_STRINGS.update(s for s in strs if RE_GROUP.match(s))
            EV_CLASSES.append((simple, names_ev, names_all, strs))


def grp_known(g):
    return g in BASES or g in KNOWN_STRINGS


def grp_names(g):
    if g not in GRP_MEMO:
        out = set()
        for simple, names_ev, names_all, strs in EV_CLASSES:
            if simple.startswith(g):
                out |= names_ev
            if g in strs:
                out |= names_all
        GRP_MEMO[g] = out
    return GRP_MEMO[g]


def utf_of_ns(ns):
    if ns not in UTF_NS:
        s = set()
        for path in MODS_BY_ID.get(ns, []):
            for zf, n in walk_jar(zipfile.ZipFile(path)):
                if n.endswith(".class") and not n.startswith("META-INF/"):
                    inf = parse_class(zf.read(n))
                    if inf:
                        s |= inf["utf"]
        UTF_NS[ns] = s
    return UTF_NS[ns]


def scan_new_strings():
    """One pass over NEW and MC jars: colon-joined constants, data/<ns>/ folders."""
    for path in jars_in(os.path.join(NEW, "mods")) + MC_LIB_JARS:
        try:
            top = zipfile.ZipFile(path)
        except (zipfile.BadZipFile, OSError):
            continue
        for zf, n in walk_jar(top):
            if n.startswith("data/"):
                parts = n.split("/")
                if len(parts) > 2:
                    DATA_NS.add(parts[1])
            elif n.endswith(".class") and not n.startswith("META-INF/"):
                COLON.update(m.decode("ascii") for m in COLON_BYTES.findall(zf.read(n)))


def scan_mod_ids():
    for path in jars_in(os.path.join(NEW, "mods")):
        try:
            zf = zipfile.ZipFile(path)
        except (zipfile.BadZipFile, OSError):
            continue
        names = zf.namelist()
        for cand in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml"):
            if cand in names:
                m = MODID_RE.search(zf.read(cand).decode("utf-8", "replace"))
                if m:
                    MODS_BY_ID[m.group(1)].append(path)
                break


def scan_kjs_utf():
    for path in jars_in(os.path.join(NEW, "mods")):
        if "kubejs" not in os.path.basename(path).lower():
            continue
        for zf, n in walk_jar(zipfile.ZipFile(path)):
            if n.endswith(".class") and not n.startswith("META-INF/"):
                inf = parse_class(zf.read(n))
                if inf:
                    KJS_UTF.update(inf["utf"])


def replacement_for(grp, ev):
    if grp == "ForgeEvents" and ev == "onEvent":
        plugin = find_info("dev.latvian.mods.kubejs.plugin.builtin.BuiltinKubeJSPlugin")
        wrapper = find_info("dev.latvian.mods.kubejs.plugin.builtin.wrapper.NativeEventWrapper")
        descs = [d for n, d in wrapper["methods"] if n == "onEvent"] if wrapper else []
        if plugin and "NativeEvents" in plugin["utf"] and descs:
            return {"name": "NativeEvents.onEvent", "status": "candidate",
                    "proof": "class-level only: constant NativeEvents in BuiltinKubeJSPlugin; method onEvent"
                             + descs[0] + " in NativeEventWrapper (descriptor read from class file; not executed)"}
        return {"name": None, "status": "unresolved", "proof": "NativeEvents or onEvent not found in NEW"}
    alias = ALIASES.get(grp)
    if alias and norm(ev) in grp_names(alias):
        return {"name": f"{alias}.{ev}", "status": "candidate",
                "proof": f"same event name present in NEW group {alias}"}
    return {"name": None, "status": "unresolved", "proof": "no replacement found in NEW"}


def section1(scripts):
    uses = defaultdict(list)
    for rel, text, _ in scripts:
        for m in EVENT_CALL.finditer(text):
            uses[(m.group(1), m.group(2))].append((rel, line_of(text, m.start())))
    out = []
    for (grp, ev), locs in sorted(uses.items()):
        known = grp_known(grp)
        if known and norm(ev) in grp_names(grp):
            continue
        status = "event name not found in NEW group" if known else "group not registered in NEW"
        rep = replacement_for(grp, ev)
        note = f"uses: {len(locs)}. Replacement: {rep['name'] or 'unresolved'} ({rep['status']}). {rep['proof']}"
        out.append(entry(1, f"{grp}.{ev}", status, locs, True, note, {"uses": len(locs), "replacement": rep}))
    return out


def section2(scripts):
    found = defaultdict(list)
    for rel, text, _ in scripts:
        for m in LOAD.finditer(text):
            found[m.group(1)].append((rel, line_of(text, m.start())))
    out = []
    for cls in sorted(found):
        if is_jdk(cls):
            out.append(entry(2, cls, "resolved (JDK)", found[cls], False, "JDK class"))
            continue
        in_old = cls in OLD_IDX.entries
        in_new = cls in NEW_IDX.entries
        in_mc = cls in MC_IDX.entries
        resolved = in_new or in_mc
        simple = cls.rsplit(".", 1)[-1]
        cands = [] if resolved else sorted(set(NEW_IDX.simple.get(simple, []) + MC_IDX.simple.get(simple, [])))[:5]
        status = ("resolved in NEW" if in_new else "resolved in MC/NeoForge 1.21.1") if resolved \
            else "missing in NEW and MC"
        note = f"in OLD: {'yes' if in_old else 'no'}; in NEW: {'yes' if in_new else 'no'}; in MC: {'yes' if in_mc else 'no'}"
        if cands:
            note += "; candidates: " + ", ".join(cands)
        out.append(entry(2, cls, status, found[cls], not resolved, note, {"candidates": cands}))
    return out


def section3(scripts):
    acc = defaultdict(list)
    cache = {}
    checked = 0
    skipped = 0
    for rel, text, _ in scripts:
        for alias, cls in ALIAS_DEF.findall(text):
            if not resolvable(cls) or is_jdk(cls):
                skipped += 1
                continue
            if cls not in cache:
                cache[cls] = members_chain(cls)
            f, m = cache[cls]
            for mm in re.finditer(r"\b" + re.escape(alias) + r"\.(\w+)", text):
                name = mm.group(1)
                checked += 1
                if name in f or name in m or name in OBJECT_MEMBERS:
                    continue
                acc[(cls, name)].append((rel, line_of(text, mm.start())))
    STATS["s3_checked"] = checked
    STATS["s3_skipped_aliases"] = skipped
    out = [entry(3, f"{cls}.{name}", "member not in class chain", locs, True, f"class: {cls}")
           for (cls, name), locs in sorted(acc.items())]
    out.insert(0, entry(3, "summary", f"{sum(len(v) for v in acc.values())} missing member uses out of "
                                       f"{checked} checked ({skipped} alias defs skipped: not NEW/MC)",
                        [], False))
    return out


def section4(scripts):
    acc = defaultdict(list)
    for rel, text, _ in scripts:
        for rx in (RECIPE_CUSTOM, RECIPE_CALL):
            for m in rx.finditer(text):
                acc[f"{m.group(1)}:{m.group(2)}"].append((rel, line_of(text, m.start())))
    out = []
    for key in sorted(acc):
        ns, rid = key.split(":", 1)
        if ns in BUILTIN_NS:
            ok, status = True, "builtin namespace (not verified)"
        elif key in COLON:
            ok, status = True, "type id string found in NEW classes"
        elif rid in utf_of_ns(ns):
            ok, status = True, "id constant found in NEW jar of mod " + ns
        elif ns in DATA_NS:
            ok, status = True, "namespace has data folder in NEW (type not verified)"
        else:
            ok, status = False, "type id not found in NEW"
        out.append(entry(4, key, status, acc[key], not ok))
    return out


def builder_methods():
    names = set()
    for simple, dotted_list in NEW_IDX.simple.items():
        if simple.endswith("Builder"):
            for d in dotted_list:
                names |= members_chain(d)[1]
    return names


def section5(scripts):
    out = []
    types = defaultdict(list)
    chains = defaultdict(list)
    for rel, text, stage in scripts:
        if stage != "startup_scripts":
            continue
        for m in REG_CALL.finditer(text):
            types[m.group(1)].append((rel, line_of(text, m.start())))
        for m in CREATE_CHAIN.finditer(text):
            for cm in CHAIN_NAME.finditer(m.group(1)):
                chains[cm.group(1)].append((rel, line_of(text, m.start(1) + cm.start())))
    for t in sorted(types):
        builder = t.capitalize() + "Builder"
        if builder in NEW_IDX.simple:
            ok, status = True, f"builder class {builder} found in NEW"
        elif t in KJS_UTF:
            ok, status = True, f"registry id '{t}' string found in KubeJS jars"
        else:
            ok, status = False, f"no builder {builder} and no '{t}' id string in KubeJS jars"
        out.append(entry(5, f"registry type '{t}'", status, types[t], not ok))
    if chains:
        known = builder_methods()
        for name in sorted(chains):
            if name not in known:
                out.append(entry(5, f".{name}()", "chained method not found in NEW *Builder classes (heuristic)",
                                 chains[name], True))
    return out


def section6(scripts):
    per_file = defaultdict(list)
    counts = defaultdict(lambda: defaultdict(int))
    for rel, text, _ in scripts:
        for m in NBT_RE.finditer(text):
            per_file[rel].append((rel, line_of(text, m.start())))
            counts[rel][m.group(0)] += 1
    out = []
    for rel in sorted(per_file):
        note = ", ".join(f"{k} {v}" for k, v in sorted(counts[rel].items()))
        out.append(entry(6, rel, f"{len(per_file[rel])} NBT-era hits", per_file[rel], True, note))
    return out


def section7(scripts):
    acc = defaultdict(list)
    for rel, text, _ in scripts:
        for m in NS_LITERAL.finditer(text):
            ns = m.group(1)
            if ns in MODIDS or ns in BUILTIN_NS or ns in NON_MOD_NS:
                continue
            acc[ns].append((rel, line_of(text, m.start()), m.group(2)))
    out = []
    for ns in sorted(acc):
        hits = acc[ns]
        sample = ", ".join(sorted({h[2] for h in hits})[:3])
        out.append(entry(7, f"{ns}:", "namespace not in modids.txt", [(h[0], h[1]) for h in hits], True,
                         f"sample ids: {sample}"))
    return out


def main():
    global NEW_IDX, MC_IDX, OLD_IDX, MODIDS
    MODIDS = load_modids()
    scripts = load_scripts()
    OLD_IDX = ClassIndex(jars_in(os.path.join(OLD, "mods")) + OLD_LIB_JARS)
    NEW_IDX = ClassIndex(jars_in(os.path.join(NEW, "mods")))
    MC_IDX = ClassIndex(MC_LIB_JARS)
    build_event_index()
    scan_new_strings()
    scan_mod_ids()
    scan_kjs_utf()

    sections = {
        1: section1(scripts),
        2: section2(scripts),
        3: section3(scripts),
        4: section4(scripts),
        5: section5(scripts),
        6: section6(scripts),
        7: section7(scripts),
    }

    issues = []
    for sec, ents in sections.items():
        for e in ents:
            if e["issue"]:
                for loc in e["locations"]:
                    issues.append((sec, loc[0], loc[1], e["key"]))
    per_file = defaultdict(lambda: defaultdict(int))
    for sec, f, _, _ in issues:
        per_file[f][sec] += 1
    file_rows = sorted(per_file.items(), key=lambda kv: -sum(kv[1].values()))

    lines = ["# KubeJS API diff: OLD 1.20.1 scripts vs NEW 1.21.1 jars", "",
             f"Generated by tools/kjsport/recon.py from {len(scripts)} OLD script files. "
             f"Locations are capped at {MAX_LOC} per entry here; full data is in api_diff.json.", ""]
    for sec in sorted(SECTION_TITLES):
        ents = sections[sec]
        nloc = sum(len(e["locations"]) for e in ents if e["issue"])
        lines += [f"## {SECTION_TITLES[sec]}", "", f"{len(ents)} entries, {nloc} issue locations.", ""]
        for e in ents:
            locs = e["locations"]
            shown = ", ".join(f"{x[0]}:{x[1]}" for x in locs[:MAX_LOC])
            more = f" (+{len(locs) - MAX_LOC} more)" if len(locs) > MAX_LOC else ""
            note = f" {e['note']}." if e["note"] else ""
            loc_txt = f" Locations: {shown}{more}" if locs else ""
            lines.append(f"- `{e['key']}`: {e['status']}.{note}{loc_txt}")
        lines.append("")
    lines += ["## 8. Per-file summary (issues sorted by total)", "",
              "| file | total | s1 | s2 | s3 | s4 | s5 | s6 | s7 |", "|---|---|---|---|---|---|---|---|---|"]
    for f, c in file_rows:
        lines.append(f"| {f} | {sum(c.values())} | " + " | ".join(str(c.get(s, 0)) for s in range(1, 8)) + " |")
    with open(os.path.join(HERE, "API_DIFF.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    payload = {"stats": STATS,
               "sections": {str(k): v for k, v in sections.items()},
               "files": [{"file": f, "total": sum(c.values()), "by_section": {str(k): v for k, v in c.items()}}
                         for f, c in file_rows]}
    with open(os.path.join(HERE, "api_diff.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    for sec in sorted(SECTION_TITLES):
        ents = sections[sec]
        nloc = sum(len(e["locations"]) for e in ents if e["issue"])
        print(f"section {sec}: {len(ents)} entries, {nloc} issue locations")
    print("top files:")
    for f, c in file_rows[:10]:
        print(f"  {sum(c.values())} {f}")
    print("S1 missing (all):")
    for e in sections[1]:
        print(f"  {e['key']} ({len(e['locations'])} locs) -> {e['detail']['replacement']['status']}")
    print("S2 missing non-JDK:")
    for e in sections[2]:
        if e["issue"]:
            print(f"  {e['key']}")
    print("S3 top 10 missing:")
    s3 = sorted((e for e in sections[3] if e["issue"]), key=lambda e: -len(e["locations"]))[:10]
    for e in s3:
        print(f"  {e['key']} ({len(e['locations'])})")
    print("S3 summary:", next(e["status"] for e in sections[3] if e["key"] == "summary"))
    fe = [e for e in sections[1] if e["key"] == "ForgeEvents.onEvent"]
    if fe:
        print(f"ForgeEvents.onEvent uses: {fe[0]['detail']['uses']}; replacement: {fe[0]['detail']['replacement']['status']}")
    print("ServerEvents.recipes in S1 issues:", any(e["key"] == "ServerEvents.recipes" for e in sections[1]))
    for m in ("net.minecraft.core.BlockPos", "net.minecraft.resources.ResourceLocation",
              "net.minecraft.nbt.CompoundTag"):
        print(f"resolved {m}:", resolvable(m))


if __name__ == "__main__":
    main()
