# KJS 6 -> 7 port, batch server-01 (+ server-06 tags)

Done (12 blockEvents + 1 tag file, all Rhino-checked: 59/59 ok, 0 fail, including unchanged files and the zz_port file):
- Emptied (dropped mods): checkCustomManaBlock.js, disableQuarkMysticalFlowers.js (botania), slimeContainProtect.js (splendid_slimes).
- NBT -> data component: compactingDrawerExploit.js (global.getQualityLevel), placeNbtMachine.js (item.customData), shippingBinRenaming.js (customName / setCustomName), plushieMechanics.js (customData + quality helpers), neptuniumHoe.js (botania clause removed).
- Disabled until ported: fishPondQuestManagerEvents.js (clipboard write, create:clipboard_content not verified; guarded with e.cancel()).
- Created: startup_scripts/zz_port_server-01.js (makePlushieItem, withPlushieAnimal).
- Unchanged, justified: carpet.js (only commented getNbt/setNbt), disableSaltSnowball.js and fruitInstaBreak.js (forge:shovels/shears, no c: tag in jars), tags/harmonizeMeatTags.js (6 forge: tags kept: raw_fishes/cod, raw_fishes/salmon, raw_fishes/tuna, raw_venison, cooked_venison, raw_boar; no c: equivalent).
- Grep of batch files for .nbt / getNbt / setNbt / withNBT / getOrCreateTag: only carpet.js comments and plushieMechanics.js entity getNbt/setNbt (lines 114, 116).

Risks for the brain:
- startup_scripts/zz_port_globalServer.js (other unit, not edited): getPlushieItemNbt uses currentNbt.copy() and newNbt.animal = {}; withPlushieAnimal passes baseItem.customData (CompoundTag), so this may fail. Owning unit must fix.
- Entity getNbt/setNbt on animal variant (plushieMechanics.js 114-116): names exist in EntityKJS, signatures not verified.

Remaining: none in batch scope. Not verified in game (owner tests).
