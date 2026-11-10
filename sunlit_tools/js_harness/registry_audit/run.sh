#!/usr/bin/env bash
# Loads the startup scripts that build prices and machine recipes, in priority order, on the
# mod's own Rhino and writes the result (global.trades, price lists, machine maps) to
# $WORK/dump.json. Use it to diff prices before and after a change, without the game.
# Usage: sunlit_tools/js_harness/registry_audit/run.sh [work dir]
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
WORK="${1:-${TMPDIR:-/tmp}/sunlit-registry-audit}"
mkdir -p "$WORK"
rm -rf "$WORK/s"
mkdir -p "$WORK/s"
cp -r "$ROOT/kubejs/startup_scripts/." "$WORK/s/"
cp "$HERE/Audit.java" "$HERE/stubs.js" "$HERE/dump.js" "$HERE/order.txt" "$WORK/"
cp "$ROOT"/mods/rhino-forge-*.jar "$WORK/rhino.jar"
[ -s "$WORK/gson.jar" ] || curl -sL --max-time 40 -o "$WORK/gson.jar" https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar
[ -s "$WORK/commons-lang3.jar" ] || curl -sL --max-time 40 -o "$WORK/commons-lang3.jar" https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar
NAME="sunlit-audit-$$"
docker run -d --name "$NAME" -v "$WORK":/w:z -w /w eclipse-temurin:17-jdk sh -c \
  'javac -cp rhino.jar:gson.jar:commons-lang3.jar Audit.java && java -cp rhino.jar:gson.jar:commons-lang3.jar:. Audit' >/dev/null
timeout 150 docker wait "$NAME" >/dev/null
docker logs "$NAME" 2>&1 | grep -v '^OK' | tail -n 40
docker rm -f "$NAME" >/dev/null
echo "dump: $WORK/dump.json"
