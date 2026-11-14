#!/usr/bin/env python3
"""Build Modpack.zip, the player-facing archive, from the instance folder.

The archive holds the pack content plus install.bat / install.sh. A player
drops it next to the installer in a Minecraft 1.21.1 + NeoForge 21.1.265
profile folder and runs the installer.

Usage (from anywhere):
    python3 tools/pack_tools/build_modpack.py [--dry-run] [--out PATH]
"""
import argparse
import fnmatch
import os
import shutil
import sys
import time
import zipfile

INSTANCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(INSTANCE, "Modpack.zip")
MAX_BYTES = 95 * 1024 * 1024  # GitHub rejects files over 100 MB.

INCLUDE_DIRS = [
    "mods", "config", "defaultconfigs", "kubejs", "resourcepacks", "shaderpacks",
    "moonlight-global-datapacks", "patchouli_books", "keybinding presets",
]
REQUIRED_DIRS = ["mods", "config", "kubejs", "resourcepacks"]
INCLUDE_FILES = [
    "options.txt", "install.bat", "install.sh", "README.txt", "READ_FIRST.txt",
    "READ_FIRST_PT-BR.txt", "atalhos.md", "LEIA-ME-ATUALIZACAO-2026-11-13.txt",
]

# Only the INCLUDE_DIRS/INCLUDE_FILES lists reach the zip, so saves, logs, docs,
# tools and the other instance-only paths are already out at the top level.
# Nested names are pack content (e.g. kubejs/data/c/tags/item/tools), so only
# tool artifacts are skipped below the top level.
EXCLUDED_NAMES = {"__pycache__", ".git"}
EXCLUDED_FILE_PATTERNS = ["*.log", "*.bak*", ".DS_Store"]

STORED_EXTENSIONS = (".jar", ".zip", ".png", ".ogg")
EXECUTABLE_ENTRIES = {"install.sh"}


def is_excluded_dir(name):
    return name in EXCLUDED_NAMES


def is_excluded_file(name):
    if name in EXCLUDED_NAMES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDED_FILE_PATTERNS)


def collect():
    """Return (entries, warnings, missing_required). Entries are (abs_path, arcname, top)."""
    entries, warnings, missing_required = [], [], []
    for top in INCLUDE_DIRS:
        base = os.path.join(INSTANCE, top)
        if not os.path.isdir(base):
            if top in REQUIRED_DIRS:
                missing_required.append(top)
            else:
                warnings.append(f"optional folder not found, skipped: {top}")
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = sorted(d for d in dn if not is_excluded_dir(d))
            for f in sorted(fn):
                if is_excluded_file(f):
                    continue
                full = os.path.join(dp, f)
                arc = os.path.relpath(full, INSTANCE).replace(os.sep, "/")
                entries.append((full, arc, top))
    for f in INCLUDE_FILES:
        full = os.path.join(INSTANCE, f)
        if os.path.isfile(full):
            entries.append((full, f, "(root)"))
        else:
            warnings.append(f"root file not found, skipped: {f}")
    for top in REQUIRED_DIRS:
        if top in missing_required:
            warnings.append(f"required folder missing: {top}")
    return entries, warnings, missing_required


def options_bytes(path):
    """Return options.txt content with the lastServer value blanked (copy only)."""
    with open(path, "rb") as fh:
        data = fh.read()
    out = []
    for line in data.splitlines(keepends=True):
        if line.startswith(b"lastServer:"):
            eol = b"\r\n" if line.endswith(b"\r\n") else (b"\n" if line.endswith(b"\n") else b"")
            out.append(b"lastServer:" + eol)
        else:
            out.append(line)
    return b"".join(out)


def summarize(entries):
    per_top = {}
    total = 0
    for full, _, top in entries:
        size = os.path.getsize(full)
        total += size
        count, sized = per_top.get(top, (0, 0))
        per_top[top] = (count + 1, sized + size)
    return per_top, total


def write_zip(entries, out):
    tmp = out + ".tmp"
    try:
        with zipfile.ZipFile(tmp, "w", allowZip64=True) as z:
            for full, arc, _ in entries:
                st = os.stat(full)
                zi = zipfile.ZipInfo(arc, date_time=time.localtime(st.st_mtime)[:6])
                zi.compress_type = (zipfile.ZIP_STORED
                                    if os.path.splitext(arc)[1].lower() in STORED_EXTENSIONS
                                    else zipfile.ZIP_DEFLATED)
                mode = 0o100755 if arc in EXECUTABLE_ENTRIES else 0o100644
                zi.external_attr = mode << 16
                with z.open(zi, "w", force_zip64=st.st_size > 2 ** 31) as dst:
                    if arc == "options.txt":
                        dst.write(options_bytes(full))
                    else:
                        with open(full, "rb") as src:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
        os.replace(tmp, out)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="list and summarize, write nothing")
    ap.add_argument("--out", default=DEFAULT_OUT, help="output zip (default: INST/Modpack.zip)")
    a = ap.parse_args()

    entries, warnings, missing_required = collect()
    for w in warnings:
        print("WARN", w)
    if missing_required:
        print("ERROR required folder(s) missing:", ", ".join(missing_required))
        return 1

    too_big = [arc for full, arc, _ in entries if os.path.getsize(full) > MAX_BYTES]
    if too_big:
        print("ERROR files over 95 MB:", ", ".join(too_big))
        return 1

    per_top, total = summarize(entries)
    for top, (count, size) in per_top.items():
        print(f"{top}: {count} files, {size / (1024 * 1024):.1f} MB")
    print(f"total: {len(entries)} files, {total / (1024 * 1024):.1f} MB")

    if a.dry_run:
        print("dry run: nothing written")
        return 0

    write_zip(entries, a.out)
    print(f"written: {a.out} ({os.path.getsize(a.out) / (1024 * 1024):.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
