PIPINHA'S VILLAGE - MINECRAFT 1.21.1 (NEOFORGE 21.1.265)
=========================================================

Farming, trading and town life modpack. Based on Society: Sunlit Valley.

This 1.21.1 edition only exists because we wanted Create Aeronautics in the
pack, and it does not exist for 1.20.1. It comes with Create Aeronautics,
Aeronautics Camera Sync, Create High Seas, Sable, Let it Walk! (walking
machines), Create Waystones Integration and FTB Stuff & Things.

STATUS: scripts, quests, shops and towns from 1.20.1 are still being ported
step by step (plan in docs/migracao/PLANO.md).


HOW TO INSTALL (ABOUT 5 MINUTES)
--------------------------------

Close your launcher and Minecraft before you start.

1) Create the profile: in your launcher (CurseForge, Prism, MultiMC,
   Modrinth App...), Minecraft 1.21.1 with NeoForge 21.1.265.
2) Open the profile folder (CurseForge: right click the profile > Open
   Folder) and put Modpack.zip in it, plus the installer for your system,
   which is inside the zip: install.bat (Windows) or install.sh (Linux).
3) Install: on Windows, double click install.bat. On Linux, open a terminal
   in the profile folder and run: bash install.sh
4) Play: open the profile in your launcher. Give it 8 GB of memory.

The installer replaces the mods, kubejs, resourcepacks and
moonlight-global-datapacks folders with the pack's and copies the pack's
config and options.txt over yours (your old options.txt is saved as
options.txt.bak).
If the profile is not 1.21.1 with NeoForge 21.1.265, it warns you before
changing anything.

The installer did not run? Delete those four folders from the profile
folder and extract the contents of Modpack.zip into it, overwriting when
asked.


NOTES
-----

- Worlds from 1.20.1: open only a COPY of the save. Blocks and items from
  mods that did not come to 1.21.1 disappear in the conversion. Do not mix
  files from the two editions.
- More than 8 GB of memory on a 16 GB PC pushes the system into swap.
- If you added -XX:+UseZGC manually, remove it under CurseForge > right
  click the profile > Profile Options > Additional Arguments.
- If Windows says a path is too long, extract the zip to a short folder
  (for example C:\Pipinha) and copy the extracted folders into the profile.
- CurseForge modpack zip (smaller, the app downloads the mods): in the app,
  Create Custom Profile > Import and pick the .zip.
