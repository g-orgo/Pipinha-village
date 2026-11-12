#!/usr/bin/env python3
# Pass 2 of the KubeJS 6 -> 7 port (Pipinha's Village). Edits kubejs/startup_scripts and
# kubejs/server_scripts in place: .hunger( -> .nutrition(, removes .meat(), removes
# self-contained entries holding ids of dropped mods, runs a Rhino syntax check on the
# changed files (reverts failing ones), then writes WORKLIST2.md and batches.json.
# Idempotent. Run with: python3 -I tools/kjsport/mechanical2.py
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KJS = ROOT / "tools" / "kjsport"
SYN = KJS / "syntax"
RHINO = ROOT / "mods" / "rhino-2101.2.7-build.85.jar"
FOLDERS = ["kubejs/startup_scripts", "kubejs/server_scripts"]
EXCLUDE = {
    "kubejs/startup_scripts/globalShippingBinHandlers.js",
    "kubejs/startup_scripts/globalMachineOwnerUtils.js",
    "kubejs/server_scripts/blockEvents/checkAttributes.js",
}
EXTRA_DROPPED = ["botania", "botania_seeds", "splendid_slimes", "create_slime", "cfm", "redeco",
                 "croptania", "farmlife", "dracovita", "gensokyodelight", "gensokyo"]
MANUAL_CATS = ("rename", "forge_unresolved", "recon_class", "tag_kept", "global")
CAP_FILES, CAP_SITES = 12, 120
CONTAINER = "kjs-syntax-m2"


def load_dropped():
    names = set(EXTRA_DROPPED)
    for line in (ROOT / "tools/dataport/REPORT.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("`apexcore`"):
            names.update(re.findall(r"`([a-z0-9_]+)`", line))
    return sorted(names, key=len, reverse=True)


ALT = "|".join(re.escape(n) for n in load_dropped())
DROP_RE = re.compile(r"(?:(?<=['\"`])|(?<=['\"`]#))(" + ALT + r")(?=:)")
MEAT_RE = re.compile(r"\.meat\(\s*\)")
KW_RE = re.compile(r"\b(if|case|else|switch|return|function|const|let|var)\b|=>")
STR_RE = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`[^`]*`")
NBT_RE = re.compile(r"\.nbt\b|getNbt\(|setNbt\(|withNBT|getOrCreateTag")
GLOBAL_RE = re.compile(r"\bglobal\.[A-Za-z_$][\w$]*\s*=(?!=)")


def removable(lines, i):
    # A line is removable only when it is one self-contained entry of a literal, not control flow.
    line = lines[i]
    if KW_RE.search(line):
        return False
    code = STR_RE.sub('""', line).split("//")[0]
    if any(code.count(o) != code.count(c) for o, c in ("()", "[]", "{}")):
        return False
    st = line.strip()
    if not st or st.endswith(";"):
        return False
    if st.endswith(","):
        return True
    if st[0] in "{['\"`":
        nxt = next((x.strip() for x in lines[i + 1:] if x.strip()), "")
        return nxt[:1] in ("]", "}", ")")
    return False


def transform(text):
    raw = text.split("\n")
    hunger, meat, out = [], [], []
    for n, line in enumerate(raw, 1):
        if ".hunger(" in line:
            hunger.append(n)
            line = line.replace(".hunger(", ".nutrition(")
        line2 = MEAT_RE.sub("", line)
        if line2 != line:
            meat.append(n)
        out.append(line2)
    removed, drop = [], set()
    for i, line in enumerate(out):
        ids = sorted(set(DROP_RE.findall(line)))
        if ids and removable(out, i):
            drop.add(i)
            removed.append((i + 1, ids))
    new = "\n".join(l for i, l in enumerate(out) if i not in drop)
    return new, {"hunger": hunger, "meat": meat, "removed": removed}


def baseline_fails():
    # tools/kjsport/syntax/results_new.txt: rel paths are relative to kubejs/.
    fails = set()
    for line in (SYN / "results_new.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("FAIL\t"):
            fails.add("kubejs/" + line.split("\t")[1])
    return fails


def syntax_check(changed, new_text, base):
    # Stages the changed files under <stage>/kubejs/ and runs SyntaxCheck in a detached container.
    tmp = Path(tempfile.mkdtemp(prefix="kjs-m2-"))
    stage, out = tmp / "stage", tmp / "out"
    out.mkdir(parents=True)
    for rel in changed:
        dst = stage / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(new_text[rel].encode("utf-8"))
    subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)
    cmd = ["docker", "run", "-d", "--name", CONTAINER, "--user", f"{os.getuid()}:{os.getgid()}",
           "-v", f"{stage / 'kubejs'}:/stage:ro", "-v", f"{out}:/out",
           "-v", f"{SYN}:/syn:ro", "-v", f"{RHINO}:/mods/rhino.jar:ro",
           "eclipse-temurin:21-jdk", "sh", "-c",
           "javac -cp /mods/rhino.jar -d /tmp/cls /syn/SyntaxCheck.java && "
           "java -cp /tmp/cls:/mods/rhino.jar SyntaxCheck /stage /out/res.txt"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"docker run failed: {r.stderr.strip()[-300:]}")
    deadline = time.time() + 600
    while time.time() < deadline:
        s = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", CONTAINER],
                           capture_output=True, text=True).stdout.strip()
        if s == "false":
            break
        time.sleep(2)
    else:
        sys.exit("syntax container timed out")
    code = subprocess.run(["docker", "inspect", "-f", "{{.State.ExitCode}}", CONTAINER],
                          capture_output=True, text=True).stdout.strip()
    logs = subprocess.run(["docker", "logs", "--tail", "60", CONTAINER],
                          capture_output=True, text=True)
    print((logs.stdout + logs.stderr)[-1500:])
    subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)
    res = out / "res.txt"
    if code != "0" or not res.exists():
        sys.exit(f"syntax container exit={code}, no results")
    fails = {}
    checked = 0
    for line in res.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if parts[0] == "OK":
            checked += 1
        elif parts[0] == "FAIL":
            key = "kubejs/" + parts[1]
            if key not in base:
                fails[key] = parts[2] + " " + (parts[3] if len(parts) > 3 else "")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"syntax: checked={checked} new_failures={len(fails)}")
    return fails


def load_old_sites():
    # Pending sites of the first worklist, matched by text (idempotent across runs).
    sites, cur = {}, None
    for line in (KJS / "WORKLIST.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"### `(.+?)`", line)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r"- L\d+ `([a-z_0-9]+)` (.*)$", line)
        if m and cur and m.group(1) in MANUAL_CATS and " | " in m.group(2):
            text = m.group(2).split(" | ", 1)[1].strip().strip("`").strip()
            sites.setdefault(cur, []).append((m.group(1), text))
    return sites


def site_counts(rel, text, old):
    ls = [l.strip() for l in text.split("\n")]
    avail, c = Counter(ls), Counter()
    for cat, t in old.get(rel, []):
        if avail[t] > 0:
            avail[t] -= 1
            c[cat] += 1
    c["nbt"] = sum(1 for l in ls if NBT_RE.search(l))
    c["dropped_manual"] = sum(1 for l in ls if DROP_RE.search(l))
    return {k: v for k, v in c.items() if v}


def read_section(path, heading):
    if not path.exists():
        return set()
    out, on = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line == heading
        elif on and line.startswith("- "):
            out.add(line[2:])
    return out


def pack(items, prefix):
    # items: [(rel, sites)] in path order, so subfolders stay contiguous.
    batches, cur, cs = [], [], 0
    for rel, s in items:
        if cur and (len(cur) >= CAP_FILES or cs + s > CAP_SITES):
            batches.append(cur)
            cur, cs = [], 0
        cur.append((rel, s))
        cs += s
    if cur:
        batches.append(cur)
    return [(f"{prefix}-{i:02d}", b) for i, b in enumerate(batches, 1)]


def main():
    rels = []
    for f in FOLDERS:
        for p in sorted((ROOT / f).rglob("*.js")):
            rel = p.relative_to(ROOT).as_posix()
            if rel not in EXCLUDE:
                rels.append(rel)
    old, base = load_old_sites(), baseline_fails()
    orig = {r: (ROOT / r).read_bytes().decode("utf-8") for r in rels}
    new, info = {}, {}
    for r in rels:
        new[r], info[r] = transform(orig[r])
    changed = [r for r in rels if new[r] != orig[r]]
    reverted = []
    if changed:
        fails = syntax_check(changed, new, base)
        for r, msg in sorted(fails.items()):
            new[r], info[r] = orig[r], None
            reverted.append((r, msg))
    applied = [r for r in changed if new[r] != orig[r]]
    for r in applied:
        (ROOT / r).write_bytes(new[r].encode("utf-8"))

    wl2 = KJS / "WORKLIST2.md"
    meat_log = read_section(wl2, "## Meat items (.meat() removed)")
    hunger_log = read_section(wl2, "## Hunger to nutrition")
    removed_log = read_section(wl2, "## Dropped-id lines removed")
    for r in applied:
        i = info[r]
        meat_log |= {f"{r}:L{n}" for n in i["meat"]}
        hunger_log |= {f"{r}:L{n}" for n in i["hunger"]}
        removed_log |= {f"{r}:L{n} {' '.join(ids)}" for n, ids in i["removed"]}

    counts = {r: site_counts(r, new[r], old) for r in rels}
    server_globals = [r for r in rels if r.startswith("kubejs/server_scripts")
                      and GLOBAL_RE.search(new[r])]
    sg = set(server_globals)
    startup_items = [(r, sum(counts[r].values())) for r in rels
                     if r.startswith("kubejs/startup_scripts") and sum(counts[r].values())]
    server_items = [(r, sum(counts[r].values())) for r in rels
                    if r.startswith("kubejs/server_scripts") and r not in sg and sum(counts[r].values())]
    batches = pack(startup_items, "startup") + pack(server_items, "server")
    if server_globals:
        batches.append(("server-globals", [(r, sum(counts[r].values())) for r in server_globals]))

    bj = {"excluded": sorted(EXCLUDE), "batches": []}
    lines = ["# KubeJS 7 port, pass 2 worklist (Pipinha's Village)", "",
             "Generated by tools/kjsport/mechanical2.py. Idempotent: rerunning changes nothing.", "",
             "## Summary", "",
             f"- Files in scope: {len(rels)} (excluded: {len(EXCLUDE)})",
             f"- Files changed this run: {len(applied)}",
             f"- Reverted (new Rhino failure): {len(reverted)}",
             f"- Hunger/meat/dropped entries recorded in total: {len(hunger_log)} hunger, "
             f"{len(meat_log)} meat, {len(removed_log)} dropped-id lines removed",
             f"- Dropped-id refs still present (manual): "
             f"{sum(c.get('dropped_manual', 0) for c in counts.values())}",
             f"- Remaining flagged sites: {sum(sum(c.values()) for c in counts.values())}", "",
             "## Hunger to nutrition", ""] + [f"- {x}" for x in sorted(hunger_log)] + [
             "", "## Meat items (.meat() removed)", "",
             "Meat was only removed, not tagged. Review these items for tags.", ""] + [
             f"- {x}" for x in sorted(meat_log)] + [
             "", "## Dropped-id lines removed", ""] + [f"- {x}" for x in sorted(removed_log)] + [
             "", "## Reverted files", ""] + [f"- {r}: {m}" for r, m in reverted] + [
             "", "## Batches", "", "| batch | files | sites | over cap |", "|---|---|---|---|"]
    for name, items in batches:
        sites = sum(s for _, s in items)
        over = "yes" if (len(items) > CAP_FILES or sites > CAP_SITES) and name != "server-globals" else "no"
        lines.append(f"| {name} | {len(items)} | {sites} | {over} |")
        entry = {"name": name, "file_count": len(items), "site_count": sites, "files": []}
        lines += ["", f"### {name}", ""]
        for r, _ in items:
            n = len(new[r].split("\n"))
            c = counts[r]
            detail = ", ".join(f"{k}={v}" for k, v in sorted(c.items()))
            lines.append(f"- `{r}` lines={n} {detail}")
            entry["files"].append({"path": r, "lines": n, "sites": c})
        bj["batches"].append(entry)
    lines += ["", "## Excluded (owned by another operator)", ""] + [f"- `{e}`" for e in sorted(EXCLUDE)]
    wl2.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (KJS / "batches.json").write_text(json.dumps(bj, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
    print(f"changed={len(applied)} reverted={len(reverted)} batches={len(batches)}")


if __name__ == "__main__":
    main()
