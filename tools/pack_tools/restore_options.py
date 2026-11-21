"""Canonical options.txt for Sunlit Valley (owner-approved standard, 2026-10-26).

options_canonical.txt holds the owner's ideal options.txt. When the game resets
options (resource reload failure, CurseForge bug), the tracked lines below are
restored from it. Untracked lines (new mods' keys, lastServer etc.) are kept.

Usage:
  python3 restore_options.py --status   list tracked lines that differ, change nothing
  python3 restore_options.py --apply    restore the differing lines (game must be closed)
  python3 restore_options.py --save     make the current options.txt the new canonical
  python3 restore_options.py --md       regenerate atalhos.md from the canonical file
"""
import os
import re
import shutil
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
INSTANCE = os.path.dirname(os.path.dirname(BASE))
OPTIONS = os.path.join(INSTANCE, "options.txt")
CANON = os.path.join(BASE, "options_canonical.txt")
PACKS = os.path.join(BASE, "packs_canonical.txt")
MD = os.path.join(INSTANCE, "atalhos.md")
GENERAL = ["lang", "guiScale", "renderDistance", "simulationDistance", "graphicsMode", "maxFps",
           "gamma", "fov", "particles", "ao", "renderClouds", "chatVisibility", "mouseSensitivity"]
KEY_NAMES = {"mouse.left": "Botão esq. mouse", "mouse.right": "Botão dir. mouse", "mouse.middle": "Botão meio mouse",
             "keyboard.space": "Espaço", "keyboard.left.shift": "Shift esq.", "keyboard.left.control": "Ctrl esq.",
             "keyboard.left.alt": "Alt esq.", "keyboard.enter": "Enter", "keyboard.backspace": "Backspace",
             "keyboard.tab": "Tab", "keyboard.escape": "Esc", "keyboard.left": "Seta esq.", "keyboard.right": "Seta dir.",
             "keyboard.up": "Seta cima", "keyboard.down": "Seta baixo", "keyboard.page.up": "PageUp",
             "keyboard.page.down": "PageDown", "keyboard.grave.accent": "Acento grave", "keyboard.world.1": "Tecla World 1"}
MODS = {"SHIFT": "Shift", "CONTROL": "Control", "ALT": "Alt"}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def tracked(line):
    key = line.split(":", 1)[0]
    return key == "resourcePacks" or key in GENERAL or key.startswith("key_") or key.startswith("soundCategory_")


def as_map(lines):
    return {l.split(":", 1)[0]: l for l in lines if ":" in l and tracked(l)}


def game_running():
    return bool(subprocess.run(["pgrep", "-f", "cpw.mods.bootstraplauncher"], capture_output=True).stdout.strip())


def diff():
    canon, cur = as_map(read(CANON)), as_map(read(OPTIONS))
    return {k: v for k, v in canon.items() if cur.get(k) != v}


def apply():
    if game_running():
        sys.exit("game is running: close it first, otherwise it overwrites options.txt on exit")
    fixes = diff()
    if not fixes:
        print("options.txt already matches the canonical file")
        return
    shutil.copy(OPTIONS, os.path.join(BASE, "options.before-restore.txt"))
    lines, seen = read(OPTIONS), set()
    for i, l in enumerate(lines):
        k = l.split(":", 1)[0]
        if k in fixes:
            lines[i] = fixes[k]
            seen.add(k)
    lines += [v for k, v in fixes.items() if k not in seen]
    with open(OPTIONS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"restored {len(fixes)} lines (backup: sunlit_tools/options.before-restore.txt)")


def key_label(value):
    base, _, mod = value.partition(":")
    name = base.removeprefix("key.")
    label = KEY_NAMES.get(name) or name.replace("keyboard.", "").replace("mouse.", "Botão mouse ")
    return f"{label} + {MODS.get(mod, mod)}" if mod else label


def write_md():
    lines = read(CANON)
    opts = dict(l.split(":", 1) for l in lines if ":" in l)
    packs = re.findall(r'"((?:[^"\\]|\\.)*)"', opts.get("resourcePacks", "[]"))
    out = ["# Backup das configurações (atalhos + resourcepacks + vídeo/geral)", "",
           f"> Padrão definido pelo dono em 2026-10-26. Gerado em {time.strftime('%Y-%m-%d')} a partir de",
           "> `sunlit_tools/options_canonical.txt` por `sunlit_tools/restore_options.py --md`.",
           "> Quando o options.txt for resetado por erro, restaurar com `restore_options.py --apply`",
           "> (jogo fechado). Para mudar o padrão: ajustar no jogo, fechar e rodar `--save` e `--md`.", "",
           "## Geral", ""]
    out += [f"- {k}: `{opts[k]}`" for k in GENERAL if k in opts]
    out += ["", f"## Resource packs ({len(packs)}, base em cima, topo embaixo)", ""]
    out += [f"{i}. `{p}`" for i, p in enumerate(packs, 1)]
    groups = {}
    for k, v in opts.items():
        if k.startswith("key_"):
            name = k[4:]
            group, _, rest = name.partition(".")
            groups.setdefault(group, []).append((re.sub(r"[._]", " ", rest or name), v))
    for group, items in groups.items():
        on = [(n, v) for n, v in items if v != "key.keyboard.unknown"]
        off = [n for n, v in items if v == "key.keyboard.unknown"]
        out += ["", f"## {group} ({len(on)} ativos, {len(off)} sem tecla)", ""]
        out += [f"- {n}: **{key_label(v)}**" for n, v in on]
        if off:
            out += ["", "Sem tecla: " + ", ".join(f"`{n}`" for n in off)]
    with open(MD, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"atalhos.md written: {len(packs)} packs, {sum(len(v) for v in groups.values())} keys")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--status"
    if mode == "--status":
        d = diff()
        print(f"{len(d)} tracked lines differ from canonical")
        for v in list(d.values())[:40]:
            print("  canonical:", v[:150])
    elif mode == "--apply":
        apply()
    elif mode == "--save":
        shutil.copy(OPTIONS, CANON)
        with open(PACKS, "w", encoding="utf-8") as f:
            f.write("\n".join(l for l in read(CANON) if l.startswith("resourcePacks:")) + "\n")
        print("canonical updated from options.txt")
    elif mode == "--md":
        write_md()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
