#!/usr/bin/env python3
"""Mirror the Modpack.zip file set into the Pipinha-village git repository.

Modpack.zip is the source of truth for what gets distributed; each listed file
is copied from the instance (its newest copy). Files in the repository that are
no longer listed are removed. Then the change is committed and pushed.

Usage (from anywhere):
    python3 tools/pack_tools/sync_repo.py -m "Commit message" [--no-push] [--dry-run]
"""
import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import zipfile

INSTANCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.environ.get("PIPINHA_REPO", "/var/home/Orgo/Documentos/Pipinha-village-1.21.1")
BRANCH = "1.21.1"
REMOTE = "git@github.com:g-orgo/Pipinha-village.git"
# Files that only exist in the repository (not in Modpack.zip).
REPO_ONLY = {"README.md", ".gitattributes", ".gitignore"}
MAX_BYTES = 95 * 1024 * 1024  # GitHub rejects files over 100 MB.
ATTRIBUTION = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def git(*args, check=True):
    return subprocess.run(["git", "-C", REPO, *args], check=check, text=True,
                          capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--message", required=True)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(os.path.join(REPO, ".git")):
        sys.exit(f"Repository clone not found at {REPO} (git clone {REMOTE} {REPO})")
    with zipfile.ZipFile(os.path.join(INSTANCE, "Modpack.zip")) as z:
        names = {n for n in z.namelist() if not n.endswith("/")}
    probe = subprocess.run(["git", "-C", REPO, "rev-parse", "--abbrev-ref", "HEAD"],
                           check=False, text=True, capture_output=True)
    if probe.returncode != 0:
        sys.exit(f"Refusing to run: cannot read the branch of {REPO}")
    current = probe.stdout.strip()
    if current != BRANCH:
        sys.exit(f"Refusing to run: {REPO} is on branch '{current}', expected '{BRANCH}'")

    copied, missing, too_big = 0, [], []
    for rel in sorted(names):
        src = os.path.join(INSTANCE, rel)
        dst = os.path.join(REPO, rel)
        if not os.path.isfile(src):
            missing.append(rel)
            continue
        if os.path.getsize(src) > MAX_BYTES:
            too_big.append(rel)
            continue
        if os.path.isfile(dst) and filecmp.cmp(src, dst, shallow=False):
            continue
        copied += 1
        if not a.dry_run:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    removed = 0
    for dp, dn, fn in os.walk(REPO):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), REPO).replace(os.sep, "/")
            if rel in names or rel in REPO_ONLY:
                continue
            removed += 1
            if not a.dry_run:
                os.remove(os.path.join(dp, f))

    print(f"copied/updated {copied}, removed {removed}, listed {len(names)}")
    for rel in missing:
        print("WARN listed in Modpack.zip but missing in the instance:", rel)
    if too_big:
        sys.exit("Files over the GitHub limit: " + ", ".join(too_big))
    if a.dry_run:
        return

    git("add", "-A")
    if not git("status", "--porcelain").stdout.strip():
        print("Nothing to commit.")
        return
    git("commit", "-q", "-m", f"{a.message}\n\n{ATTRIBUTION}")
    print(git("log", "--oneline", "-1").stdout.strip())
    if not a.no_push:
        r = git("push", "-q", "origin", f"HEAD:{BRANCH}", check=False)
        print("push ok" if r.returncode == 0 else "push FAILED:\n" + r.stderr[-1500:])
        if r.returncode:
            sys.exit(1)


if __name__ == "__main__":
    main()
