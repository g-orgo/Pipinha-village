# REPORT startup-02c

- Files: `kubejs/startup_scripts/globalBlockEntityHandlers.js`, `globalAnimalHandlers.js`, `globalRegistry.js`. Nothing else touched.
- Syntax: Rhino 2101.2.7, container `kjs-syntax-startup-02c`, files=3 ok=3 fail=0 (container removed).
- NBT sites fixed: item quality via `global.setQualityLevel` / `getQualityLevel` (harvest output, item quality read, isSameQuality, milk, dropped loot); crop seed quality via `LevelData` attachment `q.level()`; `spawnTextDisplay` via `entity.mergeNbt`; wooly variant via `saveWithoutId` + `CompoundTag.getInt`.
- Features disabled: `cool.bot.dewdropfarmland.utils.CropHandlerUtils` (CropGrowthUtils removed, comment left).
- Removals: `splendid_slimes` plort and slime heart trade loops in globalRegistry.js (the source `global.plorts` is already empty; the `global.plorts`/`slimeHearts` globals are kept because `server_scripts/recipes/addSlimeRecipes.js` reads them). `qualityToInt` removed (only caller was the seed quality read).
- Verified by javap: `Entity.saveWithoutId(CompoundTag)`, `CompoundTag()`, `CompoundTag.getInt(String)`, `LevelData` attachment, `Quality.level()`.
- Not verified in game: `text` for text display (1.21.1 expects a Component, the JSON string may render raw); `LevelData` level scale equals the old 0..3; `saveWithoutId` reached from Rhino at runtime.
- Behavior change: `isSameQuality` compares levels, so two stacks with NBT but no quality now compare equal (old code returned false).
- Remaining in this batch: none.
