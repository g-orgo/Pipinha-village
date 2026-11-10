#!/bin/sh
# Builds sunlit_replayfix.jar. Usage: JDK=/path/to/jdk17 ./build.sh
# Needs a JDK 17 (the bundled CurseForge Java is a JRE without javac).
set -e
cd "$(dirname "$0")"
LIB=../../../../Install/libraries
CP="$LIB/org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar"
CP="$CP:$LIB/net/minecraftforge/javafmllanguage/1.20.1-47.4.0/javafmllanguage-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/fmlloader/1.20.1-47.4.0/fmlloader-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/forge/1.20.1-47.4.0/forge-1.20.1-47.4.0-universal.jar"
CP="$CP:$LIB/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar"
CP="$CP:$LIB/com/google/guava/guava/31.1-jre/guava-31.1-jre.jar"
CP="$CP:$LIB/org/apache/logging/log4j/log4j-api/2.19.0/log4j-api-2.19.0.jar"
CP="$CP:../../mods/reforgedplaymod-1.20.1-0.3.1.jar"
CP="$CP:$LIB/net/minecraftforge/eventbus/6.0.5/eventbus-6.0.5.jar"
CP="$CP:../../mods/trashslot-forge-1.20.1-15.1.3.jar:../../mods/balm-forge-1.20.1-7.3.38-all.jar"
rm -rf out && mkdir out
"$JDK/bin/javac" -proc:none --release 17 -d out -cp "$CP" $(find src -name '*.java')
cp -r res/* out/
"$JDK/bin/jar" --create --file ../../mods/sunlit_replayfix-1.0.0.jar --manifest MANIFEST.MF -C out .
rm -rf out
