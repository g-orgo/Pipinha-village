#!/usr/bin/env bash
# Roda os scripts de startup do KubeJS fora do jogo, com o Rhino do próprio mod.
# Serve para pegar erro de sintaxe/tipo e conferir preços sem reiniciar o jogo.
#
# Uso: tools/pack_tools/js_harness/run.sh
# Precisa de docker (imagem eclipse-temurin:21-jdk) e internet na primeira vez
# (baixa gson e commons-lang3, que o Rhino do mod usa).
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
WORK="${TMPDIR:-/tmp}/sunlit-js-harness"

mkdir -p "$WORK"

RHINO="$(ls "$ROOT"/mods/rhino-*.jar 2>/dev/null | head -1)"
if [ -z "$RHINO" ]; then
  echo "rhino-*.jar não encontrado em mods/" >&2
  exit 1
fi
cp "$RHINO" "$WORK/rhino.jar"

if [ ! -s "$WORK/gson.jar" ]; then
  curl -sL --max-time 40 -o "$WORK/gson.jar" \
    https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar || true
fi
if [ ! -s "$WORK/commons-lang3.jar" ]; then
  curl -sL --max-time 40 -o "$WORK/commons-lang3.jar" \
    https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar || true
fi

python3 "$HERE/extract_data.py" "$ROOT" "$WORK/data.js" || exit 1

cp "$HERE/Harness.java" "$WORK/"
cp "$ROOT/kubejs/startup_scripts/globalPriceBalance.js" "$WORK/" 2>/dev/null
cp "$ROOT/kubejs/startup_scripts/globalProcessValue.js" "$WORK/" 2>/dev/null
cp "$ROOT/kubejs/client_scripts/tooltips/addPriceTooltips.js" "$WORK/" 2>/dev/null

docker run --rm -v "$WORK":/w -w /w eclipse-temurin:21-jdk sh -c \
  'javac -cp rhino.jar:gson.jar:commons-lang3.jar Harness.java && java -cp rhino.jar:gson.jar:commons-lang3.jar:. Harness'
