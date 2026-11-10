#!/usr/bin/env python3
"""Build a CurseForge modpack zip (manifest.json + modlist.html + overrides/).

Mods that came from CurseForge are referenced in manifest.json (the launcher
downloads them). Only files that are not from CurseForge are shipped inside
overrides/. Standard library only.

Usage:
    python3 sunlit_tools/export_curseforge.py --version 1.0.0 [--name N]
        [--author A] [--out dist/] [--dry-run]
"""

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTANCE_JSON = ROOT / "minecraftinstance.json"

# Top-level folders copied to overrides/ (only when they exist and have files).
OVERRIDE_DIRS = [
    "config",
    "defaultconfigs",
    "configureddefaults",
    "kubejs",
    "moonlight-global-datapacks",
    "easy_npc",
    "portable_blueprints",
    "patchouli_books",
    "quests_structures",
    "schematics",
]

# Folders that hold addon files (category id -> folder).
PACK_FOLDERS = ["mods", "resourcepacks", "shaderpacks"]

# Names skipped anywhere inside overrides/ (backups, logs, caches).
SKIP_DIR_NAMES = {
    "log", "logs", "cache", "caches", "backup", "backups", "bak",
    "crash-reports", "screenshots", "replay_recordings",
}
SKIP_FILE_SUFFIXES = (".log",)
SKIP_FILE_MARKERS = (".bak",)
SKIP_PACK_SUFFIXES = (".txt",)  # loose notes next to packs, not pack content

DISABLED = ".disabled"


def safe_name(text):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "modpack"


def is_skipped(rel_parts, name):
    for part in rel_parts:
        if part.lower() in SKIP_DIR_NAMES:
            return True
    if name.lower().endswith(SKIP_FILE_SUFFIXES):
        return True
    if any(m in name.lower() for m in SKIP_FILE_MARKERS):
        return True
    return False


def load_addons():
    data = json.loads(INSTANCE_JSON.read_text(encoding="utf-8"))
    return data.get("name", ""), data["installedAddons"]


def resolve_addon_file(addon):
    """Return (path, disabled) for the addon on disk, or (None, False)."""
    paths = addon.get("filePaths") or []
    if not paths:
        return None, False
    p = Path(paths[0])
    if p.is_file():
        return p, p.name.endswith(DISABLED)
    # The instance json may record the enabled name while the disk file is disabled.
    dp = p.with_name(p.name + DISABLED)
    if dp.is_file():
        return dp, True
    return None, False


def collect_overrides(cf_files):
    """Return list of (relative_posix_path, absolute_path) for overrides/."""
    items = []
    for d in OVERRIDE_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(ROOT)
            if is_skipped(rel.parts[:-1], f.name):
                continue
            items.append((rel.as_posix(), f))

    # Non-CurseForge files from the addon folders.
    for folder in PACK_FOLDERS:
        base = ROOT / folder
        if not base.is_dir():
            continue
        for f in sorted(base.iterdir()):
            if not f.is_file() or f.resolve() in cf_files:
                continue
            if folder != "mods" and f.name.lower().endswith(SKIP_PACK_SUFFIXES):
                continue
            if is_skipped((), f.name):
                continue
            items.append((f"{folder}/{f.name}", f))
    return items


def build(args):
    instance_name, addons = load_addons()
    name = args.name or instance_name or "Modpack"
    author = args.author or ""

    files, missing, cf_paths = [], [], set()
    required_false = 0
    for a in addons:
        path, disabled = resolve_addon_file(a)
        if path is None:
            missing.append(a.get("name", "?"))
            continue
        cf_paths.add(path.resolve())
        if disabled:
            required_false += 1
        files.append({
            "projectID": int(a["addonID"]),
            "fileID": int(a["installedFile"]["id"]),
            "required": not disabled,
            "_name": a.get("name", ""),
            "_url": a.get("webSiteURL") or "",
        })

    overrides = collect_overrides(cf_paths)
    manifest = {
        "minecraft": {
            "version": "1.20.1",
            "modLoaders": [{"id": "forge-47.4.0", "primary": True}],
        },
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": name,
        "version": args.version,
        "author": author,
        "files": [{k: v for k, v in f.items() if not k.startswith("_")} for f in files],
        "overrides": "overrides",
    }

    total_size = sum(p.stat().st_size for _, p in overrides)
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    zip_path = out_dir / f"{safe_name(name)}-{safe_name(args.version)}.zip"

    print(f"Instance: {instance_name}")
    print(f"Addons in instance json: {len(addons)}")
    print(f"Addons on disk (manifest files): {len(files)}")
    print(f"  required=false (.disabled on disk): {required_false}")
    print(f"Addons missing on disk (skipped): {len(missing)}")
    for m in missing:
        print(f"  - {m}")
    print(f"Override files: {len(overrides)}, total size: {total_size / 1048576:.1f} MiB")

    if args.dry_run:
        print("Dry run: nothing written.")
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    modlist = ["<!DOCTYPE html>", "<html lang=\"pt-BR\">", "<head><meta charset=\"utf-8\">",
               f"<title>{name} - lista de mods</title></head>", "<body>",
               f"<h1>{name} {args.version}</h1>", "<ul>"]
    for f in files:
        if f["_url"]:
            modlist.append(f"<li><a href=\"{f['_url']}\">{f['_name']}</a></li>")
        else:
            modlist.append(f"<li>{f['_name']}</li>")
    modlist += ["</ul>", "</body>", "</html>", ""]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("modlist.html", "\n".join(modlist))
        for rel, path in overrides:
            z.write(path, f"overrides/{rel}")

    print(f"Wrote: {zip_path}")
    print(f"Zip size: {zip_path.stat().st_size / 1048576:.1f} MiB")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", required=True)
    p.add_argument("--name", default=None, help="default: name from minecraftinstance.json")
    p.add_argument("--author", default=None)
    p.add_argument("--out", default="dist/")
    p.add_argument("--dry-run", action="store_true")
    return build(p.parse_args())


if __name__ == "__main__":
    sys.exit(main())
