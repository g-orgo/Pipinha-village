#!/usr/bin/env bash
# Pipinha's Village installer (Linux). Same behavior as install.bat.
# Close your launcher and Minecraft first. Three ways to run it:
#  a) Put this file and Modpack.zip in the profile folder and run: bash install.sh
#  b) Put this file and the GitHub zip (Code > Download ZIP) in the profile
#     folder and run: bash install.sh /path/to/the/zip
#  c) From a clone of the GitHub repository, run:
#     bash install.sh "/path/to/profile folder"
set -euo pipefail

echo "Close your launcher and Minecraft before running this installer."

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARG="${1:-}"
PY="$(command -v python3 || true)"
TMP=""

cleanup() {
    if [ -n "$TMP" ] && [ -d "$TMP" ]; then
        rm -rf -- "$TMP"
    fi
}
trap cleanup EXIT

# 1) Find the source folder, the zip and the target instance.
ZIP=""
if [ -n "$ARG" ] && [ -d "$ARG" ]; then
    # Repository clone mode: this file lives in the clone, the argument is the profile.
    SRC="$HERE"
    INST="$(cd "$ARG" && pwd)"
else
    INST="$HERE"
    if [ -n "$ARG" ] && [ -f "$ARG" ]; then
        ZIP="$ARG"
    elif [ -f "$HERE/Modpack.zip" ]; then
        ZIP="$HERE/Modpack.zip"
    else
        for f in "$HERE"/Pipinha-village*.zip; do
            if [ -f "$f" ]; then
                ZIP="$f"
                break
            fi
        done
    fi
    if [ -z "$ZIP" ]; then
        echo "Zip not found (no Modpack.zip next to this file). Nothing to install."
        exit 1
    fi
fi

# 2) Game folder: Prism/MultiMC keep the game in minecraft/ or .minecraft/ next to instance.cfg.
GAMEDIR="$INST"
if [ -f "$INST/instance.cfg" ]; then
    if [ -d "$INST/minecraft" ]; then
        GAMEDIR="$INST/minecraft"
    elif [ -d "$INST/.minecraft" ]; then
        GAMEDIR="$INST/.minecraft"
    fi
fi
echo "Game folder: $GAMEDIR"

# 3) Version check before anything is touched.
if [ -f "$INST/minecraftinstance.json" ]; then
    META="CurseForge minecraftinstance.json"
    WANT_LOADER="neoforge-21.1.265"
    if [ -n "$PY" ]; then
        FOUND="$("$PY" -I -c '
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print(d.get("gameVersion") or "?", ((d.get("baseModLoader") or {}).get("name")) or "?")
' "$INST/minecraftinstance.json" 2>/dev/null)" || FOUND="? ?"
    else
        JSON="$(tr -d '\n' < "$INST/minecraftinstance.json")"
        GV="$(printf '%s' "$JSON" | grep -o '"gameVersion" *: *"[^"]*"' | head -n 1 \
            | sed -E 's/.*: *"([^"]*)"/\1/' || true)"
        LN="$(printf '%s' "$JSON" | grep -o '"name" *: *"neoforge-[^"]*"' | head -n 1 \
            | sed -E 's/.*: *"([^"]*)"/\1/' || true)"
        FOUND="${GV:-?} ${LN:-?}"
    fi
elif [ -f "$INST/mmc-pack.json" ]; then
    META="Prism/MultiMC mmc-pack.json"
    WANT_LOADER="21.1.265"
    if [ -n "$PY" ]; then
        FOUND="$("$PY" -I -c '
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
v = {c.get("uid"): c.get("version") for c in d.get("components", [])}
print(v.get("net.minecraft") or "?", v.get("net.neoforged") or "?")
' "$INST/mmc-pack.json" 2>/dev/null)" || FOUND="? ?"
    else
        JSON="$(tr -d '\n' < "$INST/mmc-pack.json")"
        MC_V="$(printf '%s' "$JSON" | grep -o '"uid" *: *"net\.minecraft"[^}]*' \
            | grep -o '"version" *: *"[^"]*"' | head -n 1 \
            | sed -E 's/.*: *"([^"]*)"/\1/' || true)"
        NF_V="$(printf '%s' "$JSON" | grep -o '"uid" *: *"net\.neoforged"[^}]*' \
            | grep -o '"version" *: *"[^"]*"' | head -n 1 \
            | sed -E 's/.*: *"([^"]*)"/\1/' || true)"
        FOUND="${MC_V:-?} ${NF_V:-?}"
    fi
else
    META=""
fi

if [ -n "$META" ]; then
    GOT_MC="$(echo "$FOUND" | awk '{print $1}')"
    GOT_LOADER="$(echo "$FOUND" | awk '{print $2}')"
    if [ "$GOT_MC" != "1.21.1" ] || [ "$GOT_LOADER" != "$WANT_LOADER" ]; then
        echo "Profile mismatch ($META): found Minecraft '$GOT_MC' and loader '$GOT_LOADER'."
        echo "Expected Minecraft '1.21.1' and loader '$WANT_LOADER'."
        printf 'Continue anyway? [y/N] '
        ANSWER=""
        read -r ANSWER || true
        case "$ANSWER" in
            y|Y|yes|YES) ;;
            *) echo "Aborted. Nothing was changed."; exit 1 ;;
        esac
    fi
else
    echo "No launcher metadata found (Modrinth App or another launcher)."
    echo "Make sure the profile is Minecraft 1.21.1 with NeoForge 21.1.265."
fi

# 4) Extract the zip (or use the repository clone) and find the pack root.
mkdir -p "$GAMEDIR"
if [ -n "$ZIP" ]; then
    echo "Extracting $ZIP"
    TMP="$GAMEDIR/.pipinha_install_tmp"
    rm -rf -- "$TMP"
    mkdir -p "$TMP"
    if command -v unzip >/dev/null 2>&1; then
        unzip -q "$ZIP" -d "$TMP"
    elif [ -n "$PY" ]; then
        "$PY" -I -m zipfile -e "$ZIP" "$TMP"
    else
        echo "Neither unzip nor python3 is available to extract $ZIP. Nothing was changed."
        exit 1
    fi
    SRC="$TMP"
    # The GitHub zip wraps everything in one top folder (Pipinha-village-main).
    if [ ! -d "$SRC/mods" ]; then
        for d in "$TMP"/*/; do
            if [ -d "$d/mods" ]; then
                SRC="${d%/}"
                break
            fi
        done
    fi
fi

for need in mods kubejs; do
    if [ ! -d "$SRC/$need" ]; then
        echo "No $need/ folder in the source ($SRC). Nothing was changed."
        exit 1
    fi
done

# 5) Replace mods, kubejs, resource packs and moonlight datapacks with the pack's.
for dir in mods kubejs resourcepacks moonlight-global-datapacks; do
    rm -rf -- "$GAMEDIR/$dir"
done
echo "Copying files into $GAMEDIR"
SKIP=" install.bat install.sh README.md AGENTS.md CLAUDE.md HANDOFF.md docs tools custom-mods options.txt "
for entry in "$SRC"/* "$SRC"/.[!.]*; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    case "$name" in .git*) continue ;; esac
    case "$SKIP" in *" $name "*) continue ;; esac
    cp -a -- "$entry" "$GAMEDIR/"
done

# 6) options.txt: the pack's file replaces the player's; the old one is kept as options.txt.bak.
PACK_OPT="$SRC/options.txt"
if [ -f "$PACK_OPT" ]; then
    if [ -f "$GAMEDIR/options.txt" ]; then
        cp -- "$GAMEDIR/options.txt" "$GAMEDIR/options.txt.bak"
        echo "Your previous options.txt was saved as options.txt.bak"
    fi
    cp -- "$PACK_OPT" "$GAMEDIR/options.txt"
fi

cleanup
TMP=""
echo ""
echo "Files installed."
echo "Recommended: 8 GB of allocated memory in the profile (no more on a 16 GB PC)."
echo "Java settings were not changed."
