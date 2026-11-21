#!/bin/sh
# Builds pipinha_qualityfix-1.0.0.jar inside a detached JDK 21 container and copies it to the instance mods folder.
set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
INST="$(cd "$HERE/../.." && pwd)"
LIBS="$INST/../../Install/libraries"
MODS="$INST/mods"
NAME="pipinha_qf_build_$$"
IMAGE="eclipse-temurin:21-jdk"

cleanup() {
    docker rm -f "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

rm -rf "$HERE/out"
mkdir -p "$HERE/out"

docker run -d --name "$NAME" \
    -v "$HERE:/src:ro" \
    -v "$HERE/out:/out" \
    -v "$MODS:/mods:ro" \
    -v "$LIBS:/opt/libs:ro" \
    --entrypoint sh "$IMAGE" -c "sleep infinity" >/dev/null

docker exec "$NAME" sh -c '
set -eu
LIBS=/opt/libs
CP="$LIBS/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar"
CP="$CP:$LIBS/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar"
CP="$CP:$LIBS/net/neoforged/fancymodloader/loader/4.0.45/loader-4.0.45.jar"
CP="$CP:$(find $LIBS -path "*/org/ow2/asm/*" -name "*9.7.1*.jar" | tr "\n" ":")"
CP="$CP:$(find $LIBS -path "*/org/spongepowered/mixin/0.8.5/*" -name "mixin-0.8.5.jar"):$(find $LIBS -path "*/com/mojang/datafixerupper/8.0.16/*" -name "*.jar")"
CP="$CP:$(find $LIBS -name "*.jar" -not -path "*/minecraftforge/*" -not -path "*1.20.1*" -not -path "*-extra.jar" -not -path "*-srg.jar" | tr "\n" ":")"
CP="$CP:/mods/FarmersDelight-1.21.1-1.3.4.jar:/mods/minersdelight-1.21.1-1.4.5.jar:/mods/quality_food-1.21.1-2.4.5.jar:/mods/BrewinAndChewin-neoforge-4.5.0+1.21.1.jar"
rm -rf /tmp/classes && mkdir -p /tmp/classes
find /src/src/main/java -name "*.java" > /tmp/sources.txt
javac --release 21 -proc:none -nowarn -cp "$CP" -d /tmp/classes @/tmp/sources.txt
cp -r /src/src/main/resources/. /tmp/classes/
cd /tmp/classes && jar --create --file /out/pipinha_qualityfix-1.0.0.jar .
'

cp "$HERE/out/pipinha_qualityfix-1.0.0.jar" "$MODS/pipinha_qualityfix-1.0.0.jar"
rm -rf "$HERE/out"
echo "built: $MODS/pipinha_qualityfix-1.0.0.jar"
