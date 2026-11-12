# REPORT startup-02b (KubeJS 6 -> 7, direct work, no opencode)

Files done (9):
- startup_scripts/hostileSpawnToggle.js: 4 NativeEvents classes via Java.loadClass (FinalizeSpawnEvent, EntityJoinLevelEvent, ScreenEvent$Init$Post, ScreenEvent$Render$Pre); state moved to global.runtime.pendingHostileSpawnsOff (4 uses).
- powerfulMachines/qualityWasher.js: quality check and clear via global.getQualityLevel / setQualityLevel(0).
- powerfulMachines/picklingCan.js: Item.of without NBT arg; customData copied, quality copied via helpers.
- globalFish.js: 3 quality Item.of branches -> setQualityLevel; hasBobber reads rod.customData.toString().
- powerfulMachines/caterpillarBox.js: egg child/size read via customData getString/getFloat; entity mergeNbt kept (kjs$mergeNbt verified).
- professions/professionGlobals.js: bumpQuality rewritten on quality helpers, $ListTag removed; fish extra gets quality copied.
- powerfulMachines/ribbitHut.js and autoGrabber.js: quality via setQualityLevel.
- globalRemovedItems.js: no change needed (item-id strings only).

Features disabled: none.
Removals: none.
Syntax: Rhino 2101.2.7, container kjs-syntax-startup-02b, files=9 ok=9 fail=0 (removed).
Legacy grep (.nbt, getNbt, setNbt, withNBT, getOrCreateTag) on the 9 files: no hits.

Bom senso:
- qualityWasher: now removes only the quality component (old code cleared all NBT).

Unverified in game: hasBobber data location (customData in 1.21), caterpillarBox size type, qualityWasher clearing only quality.
