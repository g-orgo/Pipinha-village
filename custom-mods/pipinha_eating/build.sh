#!/bin/sh
# Builds pipinha_eating-1.0.0.jar inside a detached JDK 21 container and installs it in the instance mods/ folder.
# Usage: sh build.sh   (no host JDK needed; Docker only)
set -eu

MOD_DIR=$(cd "$(dirname "$0")" && pwd)
INST=$(cd "$MOD_DIR/../.." && pwd)
LIB="/var/home/Orgo/Documentos/curseforge/minecraft/Install/libraries"
OUT_JAR="$INST/mods/pipinha_eating-1.0.0.jar"
NAME="pipinha_eating_build_$$"

cleanup() {
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    rm -rf "$MOD_DIR/out"
}
trap cleanup EXIT

docker run -d --name "$NAME" \
    -v "$MOD_DIR":/src \
    -v "$LIB":/opt/libs:ro \
    -v "$INST/mods":/mods:ro \
    eclipse-temurin:21-jdk sleep 600 >/dev/null

CP="/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-client.jar"
CP="$CP:/opt/libs/net/minecraft/client/1.21.1-20240808.144430/client-1.21.1-20240808.144430-srg.jar"
CP="$CP:/opt/libs/net/neoforged/neoforge/21.1.265/neoforge-21.1.265-universal.jar"
CP="$CP:/mods/player-animation-lib-forge-2.0.4+1.21.1.jar"
CP="$CP:/mods/geckolib-neoforge-1.21.1-4.9.3.jar"
CP="$CP:/mods/kaleidoscope_ImmersiveEating-neoforge1.21.1-1.5.6.jar"

docker exec "$NAME" sh -c "
    set -eu
    LIBJARS=\$(find /opt/libs -name '*.jar' | grep -v '/net/minecraftforge/forge/1.20.1' | tr '\n' ':')
    rm -rf /src/out && mkdir -p /src/out/classes
    javac --release 21 -proc:none -d /src/out/classes -cp '$CP':\"\$LIBJARS\" \$(find /src/src -name '*.java')
    cp -r /src/res/. /src/out/classes/
    jar --create --file /src/out/pipinha_eating-1.0.0.jar -C /src/out/classes .
    chmod -R a+rwX /src/out
"

cp "$MOD_DIR/out/pipinha_eating-1.0.0.jar" "$OUT_JAR"
echo "Installed $OUT_JAR"
