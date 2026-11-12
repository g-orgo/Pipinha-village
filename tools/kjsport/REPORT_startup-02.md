# REPORT startup-02 (partial)

## Done
- forgeEvents/parkourSkills.js: rename -> `Java.loadClass("com.alrex.parcool.api.action.ParCoolActionEvent$Start$Pre")` (old `api.unstable...StartEvent` class gone in ParCool 4.0.2.0; getPlayer/getAction verified on the base class). Pre chosen so the grant fires once per start.
- forgeEvents/skullCavernChunkManager.js: rename -> `Java.loadClass("net.neoforged.neoforge.event.level.ChunkEvent$Load")`.
- forgeEvents/sunlitRetrofitChunks.js: same ChunkEvent$Load rename (getChunk/getLevel verified).
- forgeEvents/worldCreationLock.js: rename -> `Java.loadClass("net.neoforged.neoforge.client.event.ScreenEvent$Render$Pre")` (getScreen verified).
- Syntax: Rhino check of kubejs/startup_scripts, 127 files, 0 failures.

## Pending (not started)
- hostileSpawnToggle.js: 4 rename sites (MobSpawnEvent$FinalizeSpawn forge namespace, EntityJoinLevelEvent, ScreenEvent$Init$Post, ScreenEvent$Render$Pre).
- Item NBT (`.nbt`, `setNbt`): powerfulMachines/qualityWasher.js (2), powerfulMachines/picklingCan.js (1, Item.of with nbt arg), globalFish.js (1), powerfulMachines/caterpillarBox.js (3, includes entity mergeNbt).
- Entity NBT (`getNbt/setNbt`): globalAnimalHandlers.js (1), globalBlockEntityHandlers.js (878-885 entity NBT, 7 nbt sites incl. 244, 630-633), needs a 1.21 entity save/load replacement verified in the jars.
- recon_class (2) in globalBlockEntityHandlers.js: not checked.
- dropped_manual (2) in globalRegistry.js: not checked; the worklist lists many botania/splendid_slimes/farmlife lines there, needs review of the DROPPED list.
- Open question: quality_food data (read as `.nbt.quality_food`) may be a data component or attachment in the 1.21 port; confirm before switching to customData.
