#!/bin/bash
# Usage: run_render_probe.sh <scratch-dir> <comma-separated ids>  (renders mobs facing front for gen_mob_faces_render.py)
# Same launch as run_entity_probe.sh, but runs probe_render.js for the given ids (default: the 10 calibration mobs).
# Writes the RENDER| lines to <scratch-dir>/render.txt. Wrap the call with: systemd-run --user --scope -p MemoryMax=9G
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/../.."; G="$1/game"
IDS="${2:-pig,cow,sheep,horse,chicken,wolf,fox,rabbit,cat,goat}"
JSON="[$(echo "$IDS" | sed -E 's/([^,]+)/"\1"/g')]"
python3 -I "$HERE/prepare.py" "$G"
sed -i 's/earlyWindowControl *= *true/earlyWindowControl = false/' "$G/config/fml.toml"
rm -f "$G"/mods/*DistantHorizons*
sed "s/__TARGETS__/$JSON/" "$HERE/probe_render.js" > "$G/kubejs/client_scripts/zz_render_probe.js"
sed -i -E 's/^renderDistance:.*/renderDistance:4/; s/^simulationDistance:.*/simulationDistance:5/; s/^pauseOnLostFocus:.*/pauseOnLostFocus:false/; s/^graphicsMode:.*/graphicsMode:0/; s/^fullscreen:.*/fullscreen:false/' "$G/options.txt"
[ -d "$G/saves/probe" ] || { mkdir -p "$G/saves"; cp -r "$ROOT/saves/Solito solamente" "$G/saves/probe"; }
LIBGL_ALWAYS_SOFTWARE=1 __GLX_VENDOR_LIBRARY_NAME=mesa MESA_GL_VERSION_OVERRIDE=4.6 xvfb-run -a -s "-screen 0 1280x720x24" nice -n 5 python3 -I "$HERE/launch.py" "$G" --quickPlaySingleplayer probe > "$1/game.out" 2>&1 || true
grep -h "RENDER|" "$G/logs/kubejs/client.log" > "$1/render.txt" || true
grep -q "RENDER|ALLDONE" "$1/render.txt" || { echo "run_render_probe: no RENDER|ALLDONE, see $1/game.out" >&2; exit 1; }
echo "run_render_probe: $(grep -c 'RENDER|{' "$1/render.txt") entities written to $1/render.txt"

