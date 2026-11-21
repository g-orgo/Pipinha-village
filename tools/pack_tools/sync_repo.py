#!/usr/bin/env python3
"""Commit and push the instance folder, which is itself the Pipinha-village repository.

The instance is a git worktree on branch 1.21.1. What gets versioned is set by the root
.gitignore: the Modpack.zip file set (tools/pack_tools/build_modpack.py INCLUDE_DIRS and
INCLUDE_FILES, same artifact exclusions) plus the dev files (docs, tools, custom-mods, agent
notes). Keep the two lists in step when either changes.

Usage (from anywhere):
    python3 tools/pack_tools/sync_repo.py -m "Commit message" [--no-push] [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys

INSTANCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BRANCH = "1.21.1"
MAX_BYTES = 95 * 1024 * 1024  # GitHub rejects files over 100 MB.
ATTRIBUTION = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
PRIVATE_FILES = {"servers.dat", "usernamecache.json", "usercache.json"}


def git(*args, check=True):
    return subprocess.run(["git", "-C", INSTANCE, *args], check=check, text=True,
                          capture_output=True)


def pending_paths():
    """Paths `git add -A` would stage (new or changed), relative to the instance."""
    out = git("add", "-A", "--dry-run").stdout
    return [m.group(1) for m in re.finditer(r"^add '(.+)'$", out, re.M)]


def check_safe(paths):
    """Refuse files GitHub rejects and the owner's private data."""
    problems = []
    for rel in paths:
        full = os.path.join(INSTANCE, rel)
        if os.path.basename(rel) in PRIVATE_FILES:
            problems.append(f"private file: {rel}")
        elif os.path.isfile(full) and os.path.getsize(full) > MAX_BYTES:
            problems.append(f"over 95 MB: {rel}")
    options = os.path.join(INSTANCE, "options.txt")
    if os.path.isfile(options):
        with open(options, encoding="utf-8", errors="replace") as fh:
            if re.search(r"^lastServer:\S", fh.read(), re.M):
                problems.append("options.txt has lastServer set (clear it before committing)")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--message", required=True)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    probe = git("rev-parse", "--abbrev-ref", "HEAD", check=False)
    if probe.returncode != 0:
        sys.exit(f"Refusing to run: {INSTANCE} is not a git worktree")
    if probe.stdout.strip() != BRANCH:
        sys.exit(f"Refusing to run: branch is '{probe.stdout.strip()}', expected '{BRANCH}'")

    paths = pending_paths()
    problems = check_safe(paths)
    status = git("status", "--porcelain").stdout.splitlines()
    print(f"changed entries: {len(status)}, files to stage: {len(paths)}")
    if problems:
        sys.exit("Refusing to commit:\n  " + "\n  ".join(problems))
    if a.dry_run or not status:
        print("Nothing to commit." if not status else "Dry run, nothing staged.")
        return

    git("add", "-A")
    git("commit", "-q", "-m", f"{a.message}\n\n{ATTRIBUTION}")
    print(git("log", "--oneline", "-1").stdout.strip())
    if not a.no_push:
        r = git("push", "-q", "origin", f"HEAD:{BRANCH}", check=False)
        print("push ok" if r.returncode == 0 else "push FAILED:\n" + r.stderr[-1500:])
        if r.returncode:
            sys.exit(1)


if __name__ == "__main__":
    main()
