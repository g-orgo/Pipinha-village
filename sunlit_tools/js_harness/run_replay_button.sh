#!/usr/bin/env bash
# Testa kubejs/startup_scripts/replayViewerButton.js fora do jogo, com o Rhino do KubeJS.
# Monta uma tela inicial falsa (posicoes do layout do FancyMenu), dispara o evento de
# render e confere a posicao final do botao do Replay Viewer em varios cenarios.
#
# Uso: sunlit_tools/js_harness/run_replay_button.sh
# Precisa de docker (imagem eclipse-temurin:17-jdk) e internet na primeira vez.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
WORK="${TMPDIR:-/tmp}/sunlit-js-harness"

mkdir -p "$WORK"

RHINO="$(ls "$ROOT"/mods/rhino-forge-*.jar 2>/dev/null | head -1)"
if [ -z "$RHINO" ]; then
  echo "rhino-forge-*.jar nao encontrado em mods/" >&2
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

cp "$HERE/ReplayButtonHarness.java" "$WORK/"
cp "$HERE/replayStubs.js" "$WORK/"
cp "$HERE/replayButtonTests.js" "$WORK/"
cp "$ROOT/kubejs/startup_scripts/replayViewerButton.js" "$WORK/"

docker run --rm -v "$WORK":/w -w /w eclipse-temurin:17-jdk sh -c \
  'javac -cp rhino.jar:gson.jar:commons-lang3.jar ReplayButtonHarness.java && java -cp rhino.jar:gson.jar:commons-lang3.jar:. ReplayButtonHarness'
