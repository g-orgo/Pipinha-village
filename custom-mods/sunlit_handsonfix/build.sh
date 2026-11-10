#!/bin/sh
# Builds sunlit_handsonfix.jar. Usage: JDK=/path/to/jdk17 ./build.sh
# Needs a JDK 17 (the bundled CurseForge Java is a JRE without javac).
set -e
cd "$(dirname "$0")"
LIB=../../../../Install/libraries
CP="$LIB/org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar"
CP="$CP:$LIB/net/minecraftforge/javafmllanguage/1.20.1-47.4.0/javafmllanguage-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraftforge/fmlloader/1.20.1-47.4.0/fmlloader-1.20.1-47.4.0.jar"
CP="$CP:$LIB/net/minecraft/client/1.20.1-20230612.114412/client-1.20.1-20230612.114412-srg.jar"
rm -rf out && mkdir out
"$JDK/bin/javac" -proc:none --release 17 -d out -cp "$CP" $(find src -name '*.java')
cp -r res/* out/
"$JDK/bin/jar" --create --file ../../mods/sunlit_handsonfix-1.0.0.jar --manifest MANIFEST.MF -C out .
rm -rf out
