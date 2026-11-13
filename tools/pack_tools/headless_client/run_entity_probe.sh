#!/bin/bash
# Usage: run_entity_probe.sh <scratch-dir>
# Same launch as run_probe.sh, but runs probe_entities.js (entity discovery, no scenarios).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/../.."; G="$1/game"
python3 -I "$HERE/prepare.py" "$G"
sed -i 's/earlyWindowControl *= *true/earlyWindowControl = false/' "$G/config/fml.toml"
rm -f "$G"/mods/*DistantHorizons*
cp "$HERE/probe_entities.js" "$G/kubejs/client_scripts/zz_probe.js"
sed -i -E 's/^renderDistance:.*/renderDistance:4/; s/^simulationDistance:.*/simulationDistance:5/; s/^pauseOnLostFocus:.*/pauseOnLostFocus:false/; s/^graphicsMode:.*/graphicsMode:0/; s/^fullscreen:.*/fullscreen:false/' "$G/options.txt"
[ -d "$G/saves/probe" ] || { mkdir -p "$G/saves"; cp -r "$ROOT/saves/Solito solamente" "$G/saves/probe"; }
LIBGL_ALWAYS_SOFTWARE=1 __GLX_VENDOR_LIBRARY_NAME=mesa MESA_GL_VERSION_OVERRIDE=4.6 exec xvfb-run -a -s "-screen 0 1280x720x24" nice -n 5 python3 -I "$HERE/launch.py" "$G" --quickPlaySingleplayer probe > "$1/game.out" 2>&1
