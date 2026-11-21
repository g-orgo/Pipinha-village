#!/bin/sh
# Build pipinha_cinematic_toms with a detached eclipse-temurin:21-jdk container (no local JDK needed).
# Compiles against the NeoForge 21.1.265 client jar, the Mojang-named MC srg jar, the
# NeoForge universal jar, every library under LIB and the target mod jars in mods/.
set -eu

MOD_DIR="$(cd "$(dirname "$0")" && pwd)"
INST="$(cd "$MOD_DIR/../.." && pwd)"
LIB="/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries"
NAME="pipinha_cinematic_toms_build_$$"
JAR_NAME="pipinha_cinematic_toms-1.0.0.jar"

cleanup() {
  docker exec "$NAME" rm -rf /src/${OUT_DIR:-out} >/dev/null 2>&1 || true
  docker rm -f "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d --name "$NAME" \
  -v "$MOD_DIR":/src \
  -v "$LIB":/opt/libs:ro \
  -v "$INST/mods":/mods:ro \
  eclipse-temurin:21-jdk sleep 900 >/dev/null

docker exec "$NAME" rm -rf /src/${OUT_DIR:-out}
CP="/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-client.jar"
CP="$CP:/opt/libs/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar"
CP="$CP:/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar"
CP="$CP:$(docker exec "$NAME" sh -c 'find /opt/libs -name "*.jar" | grep -v -e /minecraftforge/ -e 1.20.1 | tr "\n" ":"')"
CP="$CP:$(docker exec "$NAME" sh -c 'find /mods -maxdepth 1 -name "*.jar" | tr "\n" ":"')"

docker exec "$NAME" sh -c "mkdir -p /src/${OUT_DIR:-out}/classes && \
  find /src/src -name '*.java' > /src/${OUT_DIR:-out}/sources.txt && \
  javac --release 21 -proc:none -nowarn -Xmaxerrs 1000 -encoding UTF-8 -cp '$CP' -d /src/${OUT_DIR:-out}/classes @/src/${OUT_DIR:-out}/sources.txt"

docker exec "$NAME" sh -c "cd /src/${OUT_DIR:-out}/classes && jar --create --file /src/${OUT_DIR:-out}/$JAR_NAME \
  --no-manifest . && cd /src/res && jar --update --file /src/${OUT_DIR:-out}/$JAR_NAME ."

cp "$MOD_DIR/${OUT_DIR:-out}/$JAR_NAME" "$INST/mods/$JAR_NAME"
docker exec "$NAME" rm -rf /src/${OUT_DIR:-out}
echo "built $INST/mods/$JAR_NAME"
