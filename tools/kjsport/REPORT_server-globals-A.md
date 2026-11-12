# REPORT server-globals-A

Status: done (no opencode: BATCH_ORDER says work directly).

## Files
- Moved `kubejs/server_scripts/globalServer.js` -> `kubejs/startup_scripts/zz_port_globalServer.js` (whole file, unchanged; file only defines globals and helpers).
- Moved `kubejs/server_scripts/entities/globalAnimalVariables.js` -> `kubejs/startup_scripts/zz_port_globalAnimalVariables.js` (whole file, unchanged; only literal tables).

## Globals moved (same names, no reader changes needed)
- globalServer.js (15): mainUiElementIds, renderUiText, clearUiItemPaint, renderUiItemText, calculateCoinValue, getPigColoredName, calculateCoinsFromValue, overworldRadar, netherRadar, handleFee, teleportHome, addAttributesFromStages, addItemCooldown, getPlushieItemNbt, setPlushieExtractedPD.
- globalAnimalVariables.js (7): husbandryAnimals, milkableAnimals, coopMasterAnimals, tierTwoHusbandryAnimals, tierThreeHusbandryAnimals, coldMobs, animalMessageSettings.

## Runtime state
- None. No `global.<name>` of these files is mutated anywhere in `kubejs/` (checked push/splice/set/assign), so nothing moved to `global.runtime`.

## Reader changes for other owners
- None required. All names keep their `global.` name and are defined in startup.

## Sites in WORKLIST2
- Forge registries, nbt, getForgePersistentData: none present in either file (grep clean).
- dropped_manual farmlife: WORKLIST2 lists lines 23, 36, 59, 76, 103, 109 of globalAnimalVariables.js, but the file contains no farmlife or DROPPED-list mod id at those lines (they are wildernature/minecraft/etc. entity ids). Nothing removed. Worklist entries look stale or false positive; brain to confirm.
- Java names: the files contain no Java class or member references introduced or changed by this unit, so the javap container was not run.

## Validation
- Rhino syntax check (`tools/kjsport/syntax/SyntaxCheck.java`, container `kjs-syntax-server-globals-A`, detached): files=2 ok=2 fail=0.

## Side effects to know
- The functions and tables now also load on the client (startup runs on both sides). Harmless: they are pure definitions.
- Server-only code runs only when called, so load order is safe.

## Remaining
- Nothing in this unit. Brain to decide on the farmlife worklist entries.
