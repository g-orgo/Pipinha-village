#!/usr/bin/env bash
# Tests kubejs/server_scripts/entities/dogFollowOwner.js outside the game with KubeJS's
# Rhino: hide on mount, restore on dismount, no loss on load errors, death or legacy data.
# Usage: sunlit_tools/js_harness/run_dog_follow.sh (needs docker, eclipse-temurin:17-jdk).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
WORK="${TMPDIR:-/tmp}/sunlit-dog-follow"
mkdir -p "$WORK"
cp "$(ls "$ROOT"/mods/rhino-forge-*.jar | head -1)" "$WORK/rhino.jar"
for dep in gson:com/google/code/gson/gson/2.10.1/gson-2.10.1 commons-lang3:org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0; do
  name="${dep%%:*}"
  [ -s "$WORK/$name.jar" ] || curl -sL --max-time 40 -o "$WORK/$name.jar" "https://repo1.maven.org/maven2/${dep#*:}.jar"
done
cp "$HERE/HostileToggleHarness.java" "$HERE/dogFollowStubs.js" "$HERE/dogFollowTests.js" "$WORK/"
cp "$ROOT/kubejs/server_scripts/entities/dogFollowOwner.js" "$WORK/server.js"
docker run --rm -v "$WORK":/w -w /w eclipse-temurin:17-jdk sh -c \
  'javac -cp rhino.jar HostileToggleHarness.java && java -cp rhino.jar:gson.jar:commons-lang3.jar:. HostileToggleHarness dogFollowStubs.js server.js dogFollowTests.js'
