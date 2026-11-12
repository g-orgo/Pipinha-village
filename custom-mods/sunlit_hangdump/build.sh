#!/bin/sh
# Builds sunlit_hangdump.jar. Usage: JDK=/path/to/jdk17 ./build.sh
# Needs a JDK 17 (the bundled CurseForge Java is a JRE without javac).
set -e
cd "$(dirname "$0")"
LIB=../../../../Install/libraries
CP="$LIB/net/minecraftforge/forge/1.20.1-47.4.29/forge-1.20.1-47.4.29-universal.jar:$LIB/net/minecraftforge/eventbus/6.2.33/eventbus-6.2.33.jar:$LIB/net/minecraftforge/fmlloader/1.20.1-47.4.29/fmlloader-1.20.1-47.4.29.jar:$LIB/net/minecraftforge/javafmllanguage/1.20.1-47.4.29/javafmllanguage-1.20.1-47.4.29.jar:$(ls $LIB/org/slf4j/slf4j-api/*/slf4j-api-*.jar | tail -1)"
rm -rf out && mkdir out
"$JDK/bin/javac" -proc:none --release 17 -d out -cp "$CP" $(find src -name '*.java')
cp -r res/* out/
"$JDK/bin/jar" --create --file ../../mods/sunlit_hangdump-1.0.0.jar --manifest MANIFEST.MF -C out .
rm -rf out
