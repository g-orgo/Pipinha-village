# REPORT launch3

Scope: fixes from the owner's 3rd launch (logs/kubejs/startup.log), direct work, no opencode.

- Inventory API: `blockInfo.inventory(W, H)` -> `inventory("inventory", Direction.ALL_SET, W, H)` in powerfulMachines and customMachines; `rightClickOpensInventory()` -> `rightClickOpensInventory("inventory")`.
- Capabilities: ITEM `attachCapability` pass-through removed (no rules dropped) in 17 machine files. FLUID converted to `fluidTank("fluid", Direction.ALL_SET, 10000)` in powerfulMachines/autoTapper.js and juiceInserter.js. CapabilityBuilder no longer used.
- Block entity inventory reads: `entity.inventory` -> `entity.attachments.inventory` in autoWormFarm.js, manaMilker.js, smartShippingBin.js. Level block reads left unchanged (see blockers).
- `Java.type(` -> `Java.loadClass(` in 5 startup/server scripts.
- registerBlocks.js: `.textureAll(` -> `.texture(`.
- 4 models JSON: `"forge_data"` -> `"neoforge_data"`.
- registration/registerItems.js: `.rarity("epic")` added to numismatics:ancient_coin and numismatics:prismatic_coin builders.
- registration/modifyItems.js: removed numismatics:ancient_coin, numismatics:prismatic_coin, society:ancient_fruit_seed, society:sparkpod_seed from the epic rarity list (the first two moved into builders; the last two have no kubejs registration and no mod asset found).

Validation: greps (a) and (b) empty. Rhino 2101.2.7 SyntaxCheck over kubejs/: files=380 ok=380 fail=0 (container kjs-syntax-launch3, removed).

Open: autoTapper.js and juiceInserter.js still use 1.20 ForgeCapabilities/ForgeData in tick logic. Level block `.inventory` reads and preventChestVoid.js:41 unverified. Remaining epic-list ids (cluttered, domesticationinnovation, several society records) not verified against mod jars; the next launch will show any that still fail.
