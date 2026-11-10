#!/bin/sh
# Builds sunlit_qualityfix.jar. Usage: JDK=/path/to/jdk17 ./build.sh [output jar]
# Needs a JDK 17 (the bundled CurseForge Java is a JRE without javac).
set -e
cd "$(dirname "$0")"
OUT="${1:-../../mods/sunlit_qualityfix-1.0.0.jar}"
LIB=../../../../Install/libraries
MODS=../../mods
CP="$LIB/org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar"
CP="$CP:$LIB/net/minecraftforge/forge/1.20.1-47.4.0/forge-1.20.1-47.4.0-universal.jar"
CP="$CP:$LIB/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar"
CP="$CP:$LIB/net/minecraftforge/javafmllanguage/1.20.1-47.4.0/javafmllanguage-1.20.1-47.4.0.jar"
CP="$CP:$MODS/quality_food-1.20.1-2.4.3-all.jar"
CP="$CP:$MODS/FarmersDelight-1.20.1-1.3.2.jar"
CP="$CP:$MODS/miners_delight-1.20.1-1.4.5-backport.jar"
CP="$CP:$MODS/BrewinAndChewin-1.20.1-3.2.1.jar"
rm -rf out && mkdir out
"$JDK/bin/javac" -proc:none --release 17 -d out -cp "$CP" $(find src -name '*.java')
cp -r res/* out/
"$JDK/bin/jar" --create --file "$OUT" --manifest MANIFEST.MF -C out .
rm -rf out
