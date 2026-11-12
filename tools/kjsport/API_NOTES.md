# KubeJS 6 (1.20.1) -> KubeJS 7 (2101.7.2, NeoForge 1.21.1): verified API notes

Every name below was read from the class files of `mods/kubejs-neoforge-2101.7.2-build.381.jar`
(2026-11-12). KubeJS exposes Java methods named `kjs$foo` to JS as `foo` (and bean `getFoo`/`setFoo`
as property `foo`). Anything not listed here is unverified: check the jar before using it.

## Events (renamed by tools/kjsport/mechanical.py; callbacks still need review)
- `NativeEvents.onEvent([priority,] eventClass, e => {})`: takes a Java Class, not a string.
  Pass `Java.loadClass('net.neoforged.neoforge.event...')`. Forge event classes live under
  `net.neoforged.neoforge.event.*`; the bus class is `net.neoforged.neoforge.common.NeoForge` (`NeoForge.EVENT_BUS`).
- `EntityEvents.beforeHurt` (old `hurt`), `ItemEvents.modifyTooltips` (old `tooltip`, client),
  `ItemEvents.dynamicTooltips` also exists.
- Recipe viewer: `RecipeViewerEvents.addEntries`, `removeEntries`, `removeEntriesCompletely`,
  `removeCategories`, `removeRecipes`, `addInformation`, `groupEntries` (server side in KubeJS 7).
- `ServerEvents.generateData` (old `highPriorityData`), `ServerEvents.recipes`, `afterRecipes`,
  `modifyRecipeIngredient`, `modifyRecipeResult`, `compostableRecipes`, `tags`, `loaded`, `tick`, `commandRegistry`.
- `PlayerEvents`: advancement chat chestClosed chestOpened cloned decorateChat inventoryChanged
  inventoryClosed inventoryOpened loggedIn stageAdded stageRemoved tick. (`respawned`/`loggedOut` are
  not in the 2101 PlayerEvents class: check KubeJS Additions `AdditionalEvents` before using them.)
- `EntityEvents`: beforeHurt checkSpawn death drops spawned.

## Item builder (StartupEvents.registry('item', ...))
- Food: `.food(food => food.nutrition(n).saturation(s).alwaysEdible().fastToEat().eatSeconds(t).effect(...).usingConvertsTo(...))`.
  `hunger(` is gone, use `nutrition(`. `meat()` is gone (1.21 has no meat flag; use item tags such as `c:foods/...`).
- Other builder names present: maxStackSize unstackable rarity fireResistant durability tool
  displayName formattedDisplayName texture color tint group burnTime(check) containerItem craftRemainder components.

## Item NBT -> data components (1.20.5+)
- Read: `stack.customData` / `stack.getCustomData()` (CompoundTag of `minecraft:custom_data`),
  `stack.get(componentType)`, `stack.componentString`, `stack.componentMap`.
- Write: `stack.setCustomData(tag)`, `stack.set(type, value)`, `stack.remove(type)`,
  `stack.setCustomName(text)`, `stack.setLore([...])`, `stack.setCustomModelData(n)`,
  `stack.setDyedColor(rgb)`, `stack.setGlintOverride(bool)`, `stack.setRarity(...)`, `stack.setTooltipHidden(...)`.
- Create: `Item.of('ns:id[minecraft:custom_data={key:1b}]')` (component string syntax) or create then `setCustomData`.
- Gone: `stack.nbt`, `getNbt/setNbt`, `withNBT`, `getOrCreateTag`, `Item.of(id, count, {nbt})`.
- Equality: `stack.areComponentsEqual(other)`, `stack.areItemsEqual(other)`, `stack.equalsIgnoringCount(other)`.

## Entities and players
- `entity.persistentData` still exists (`WithPersistentData`); NeoForge keeps `Entity#getPersistentData()`.
- Capabilities were replaced by data attachments in NeoForge 1.21 (affects mod classes like
  quality_food `LevelData`, LSO `CapabilityUtil`, ParCool `Parkourability`): find the 1.21.1 class in the jar.

## global
- `global.x = ...` is only allowed in startup scripts. Static tables: define them in a startup
  script. Runtime state in server scripts: module-level `let` in the server script, or `server.persistentData`.
