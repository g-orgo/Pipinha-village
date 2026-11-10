#!/bin/bash
# Usage: run_probe.sh <scratch-dir> <scenarios.json>
# Runs the real game without a window on an isolated copy of the instance. The instance is only read.
# Stop a stuck run by its path: pgrep -a java | grep <scratch-dir>. Never use pkill -f.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$HERE/../.."; G="$1/game"
python3 -I "$HERE/prepare.py" "$G"
sed -i 's/earlyWindowControl *= *true/earlyWindowControl = false/' "$G/config/fml.toml"
rm -f "$G"/mods/*DistantHorizons*
{ echo "global.probeScenarios = $(cat "$2")"; cat "$HERE/probe.js"; } > "$G/kubejs/client_scripts/zz_probe.js"
sed -i -E 's/^renderDistance:.*/renderDistance:4/; s/^simulationDistance:.*/simulationDistance:5/; s/^pauseOnLostFocus:.*/pauseOnLostFocus:false/; s/^graphicsMode:.*/graphicsMode:0/; s/^fullscreen:.*/fullscreen:false/' "$G/options.txt"
[ -d "$G/saves/probe" ] || { mkdir -p "$G/saves"; cp -r "$ROOT/saves/Solito solamente" "$G/saves/probe"; }
rm -rf "$G/screenshots"
LIBGL_ALWAYS_SOFTWARE=1 __GLX_VENDOR_LIBRARY_NAME=mesa MESA_GL_VERSION_OVERRIDE=4.6 exec xvfb-run -a -s "-screen 0 1280x720x24" nice -n 5 python3 -I "$HERE/launch.py" "$G" --quickPlaySingleplayer probe > "$1/game.out" 2>&1
