#!/bin/sh
# Builds pipinha_curiosfix-1.0.0.jar inside a detached JDK 21 container (no local JDK needed)
# and copies it to the instance mods folder. Usage: sh build.sh
# Compiles against the NeoForge, Curios, TrashSlot and Balm jars (mods/), so rebuild after updating them.
set -eu

MOD_NAME=pipinha_curiosfix
MOD_DIR=$(cd "$(dirname "$0")" && pwd)
INST=$(cd "$MOD_DIR/../.." && pwd)
LIB=/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries
IMAGE=eclipse-temurin:21
NAME=${MOD_NAME}_build_$$

cleanup() {
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    rm -rf -- "$MOD_DIR/out"
}
trap cleanup EXIT

rm -rf -- "$MOD_DIR/out"
mkdir -p "$MOD_DIR/out"

docker run -d --name "$NAME" \
    -v "$MOD_DIR":/src \
    -v "$LIB":/opt/libs:ro \
    -v "$INST/mods":/mods:ro \
    "$IMAGE" sleep 600 >/dev/null

docker exec -u "$(id -u):$(id -g)" -w /src "$NAME" sh -c '
set -eu
MOD_NAME=$1
CP=/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-client.jar
CP=$CP:/opt/libs/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar
CP=$CP:/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar
CP=$CP:/opt/libs/net/fabricmc/sponge-mixin/0.16.4+mixin.0.8.7/sponge-mixin-0.16.4+mixin.0.8.7.jar
CP=$CP:/mods/curios-neoforge-9.5.1+1.21.1.jar:/mods/trashslot-neoforge-1.21.1-21.1.11.jar:/mods/balm-neoforge-1.21.1-21.0.67.jar
CP=$CP:$(find /opt/libs -name "*.jar" | while read -r j; do jar tf "$j" >/dev/null 2>&1 && printf "%s:" "$j"; done)
mkdir -p /src/out/classes
javac -proc:none --release 21 -d /src/out/classes -cp "$CP" $(find src -name "*.java")
cp -r res/. /src/out/classes/
jar --create --file "/src/out/$MOD_NAME-1.0.0.jar" -C /src/out/classes .
' sh "$MOD_NAME"

cp -- "$MOD_DIR/out/$MOD_NAME-1.0.0.jar" "$INST/mods/$MOD_NAME-1.0.0.jar"
echo "built $INST/mods/$MOD_NAME-1.0.0.jar"
