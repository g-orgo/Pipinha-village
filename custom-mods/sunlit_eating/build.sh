#!/bin/sh
# Builds sunlit_eating.jar. Usage: JDK=/path/to/jdk17 [OUT=/path/to.jar] ./build.sh
# Needs a JDK 17 (the bundled CurseForge Java is a JRE without javac). Install in mods/ only with the game closed.
set -e
cd "$(dirname "$0")"
LIB=../../../../Install/libraries
OUT=${OUT:-../../mods/sunlit_eating-1.0.0.jar}
CP="$LIB/org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar"
CP="$CP:$LIB/net/minecraftforge/javafmllanguage/1.20.1-47.4.0/javafmllanguage-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/fmlloader/1.20.1-47.4.0/fmlloader-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/forge/1.20.1-47.4.0/forge-1.20.1-47.4.0-universal.jar"
CP="$CP:$LIB/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar"
CP="$CP:$LIB/net/minecraftforge/eventbus/6.0.5/eventbus-6.0.5.jar"
CP="$CP:$LIB/net/minecraftforge/fmlcore/1.20.1-47.4.0/fmlcore-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/mergetool/1.1.5/mergetool-1.1.5-api.jar"
CP="$CP:../../mods/player-animation-lib-forge-1.0.2-rc1+1.20.jar"
CP="$CP:../../mods/kaleidoscope_immersiveEating-forge1.20.1-1.4.3.jar"
CP="$CP:../../mods/geckolib-forge-1.20.1-4.8.4.jar"
CP="$CP:$LIB/org/joml/joml/1.10.5/joml-1.10.5.jar"
CP="$CP:$LIB/com/google/code/gson/gson/2.10/gson-2.10.jar"
rm -rf out && mkdir out
"$JDK/bin/javac" -proc:none --release 17 -d out -cp "$CP" $(find src -name '*.java')
cp -r res/* out/
"$JDK/bin/jar" --create --file "$OUT" --manifest MANIFEST.MF -C out .
rm -rf out
