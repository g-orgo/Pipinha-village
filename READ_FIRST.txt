PIPINHA'S VILLAGE - MINECRAFT 1.21.1 (NEOFORGE 21.1.265)
=========================================================

Farming, trading and town life modpack. Based on Society: Sunlit Valley.

This 1.21.1 edition only exists because we wanted Create Aeronautics in the
pack, and it does not exist for 1.20.1. It comes with Create Aeronautics,
Aeronautics Camera Sync, Create High Seas and Sable.

STATUS: the 1.21.1 edition is being migrated from the 1.20.1 one. Mods are in
place; scripts, quests, shops and towns are being ported step by step (plan in
docs/migracao/PLANO.md). The 1.20.1 edition stays the playable one until then.


INSTALL WITH THE INSTALLER (RECOMMENDED)
----------------------------------------

Close the launcher and Minecraft first.

- Windows: put install.bat and Modpack.zip in the profile folder (CurseForge:
  right click the profile > Open Folder), then double click install.bat.
- Linux: put install.sh and Modpack.zip in the profile folder, then run:
  bash install.sh

The installer replaces mods/, kubejs/, resourcepacks/ and
moonlight-global-datapacks/ with the pack's files and keeps your options.txt
(only the resource pack lines are updated). If the profile is not Minecraft
1.21.1 with NeoForge 21.1.265, it asks before continuing.


MANUAL INSTALL (IF THE INSTALLER DOES NOT RUN)
----------------------------------------------

1) In the CurseForge app create a profile for Minecraft 1.21.1 with
   NeoForge 21.1.265 (or import the modpack zip, below).
2) Delete the "mods", "resourcepacks" and "kubejs" folders inside the
   instance folder (CurseForge: right click the profile > Open Folder).
3) Unzip this file into the instance folder, keeping the folder structure
   (mods/, resourcepacks/, config/, kubejs/, moonlight-global-datapacks/ ...).
   Overwrite existing files when asked.

Do not mix files from the 1.20.1 edition with this one: 1.20.1 jars and
scripts do not load on 1.21.1.


IMPORT INTO CURSEFORGE (MODPACK ZIP)
------------------------------------

The modpack zip (manifest.json) is smaller: the CurseForge app downloads the
mods at install time. It is generated in dist/ by
tools/pack_tools/export_curseforge.py (details in docs/PUBLICAR.md).

1) In the CurseForge app click "Create Custom Profile".
2) Click "Import" and choose the .zip file.
3) Confirm the profile name and wait for the app to download the mods.
4) Open the profile. Config and kubejs files are in the zip.


NOTES
-----

- Worlds from the 1.20.1 edition must be converted on a copy, never on the
  original save. Blocks and items from mods that did not come to 1.21.1
  disappear in the conversion.
- Java uses the default G1 garbage collector. If you added -XX:+UseZGC
  manually, remove it under CurseForge > right click the profile >
  Profile Options > Additional Arguments.
- Recommended: allocate 8 GB of memory to the profile. On a 16 GB PC, more
  than that pushes the system into swap.
- Rendering uses Sodium + Iris (Embeddium and Oculus do not exist here).
- If Windows says a path is too long, extract the zip to a shorter folder
  (for example C:\Pipinha) and copy the extracted folders into the instance.
