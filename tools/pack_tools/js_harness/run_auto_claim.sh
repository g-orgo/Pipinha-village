#!/usr/bin/env bash
# Tests kubejs/server_scripts/blockEvents/autoClaimChunk.js outside the game with KubeJS's Rhino
# (fake FTB Chunks API and placed events). Reuses the generic HostileToggleHarness runner.
# Usage: sunlit_tools/js_harness/run_auto_claim.sh (needs docker, eclipse-temurin:17-jdk).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
WORK="${TMPDIR:-/tmp}/sunlit-auto-claim"
mkdir -p "$WORK"
cp "$(ls "$ROOT"/mods/rhino-forge-*.jar | head -1)" "$WORK/rhino.jar"
for dep in gson:com/google/code/gson/gson/2.10.1/gson-2.10.1 commons-lang3:org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0; do
  name="${dep%%:*}"
  [ -s "$WORK/$name.jar" ] || curl -sL --max-time 40 -o "$WORK/$name.jar" "https://repo1.maven.org/maven2/${dep#*:}.jar"
done
cp "$HERE/HostileToggleHarness.java" "$HERE/autoClaimTests.js" "$WORK/"
cp "$ROOT/kubejs/server_scripts/blockEvents/autoClaimChunk.js" "$WORK/script.js"
echo 'runTests();' > "$WORK/run.js"
NAME="sunlit-auto-claim-$$"
docker run -d --name "$NAME" -v "$WORK":/w -w /w eclipse-temurin:17-jdk sh -c \
  'javac -cp rhino.jar HostileToggleHarness.java && java -cp rhino.jar:gson.jar:commons-lang3.jar:. HostileToggleHarness autoClaimTests.js script.js run.js' >/dev/null
docker wait "$NAME" >/dev/null
docker logs "$NAME" 2>&1 | tail -n 40
docker rm "$NAME" >/dev/null
