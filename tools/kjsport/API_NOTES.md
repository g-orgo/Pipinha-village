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
  `removeCategories`, `removeRecipes`, `addInformation`, `groupEntries`. They are COMMON handlers (fine in
  client_scripts) and entry handlers REQUIRE a target type: `RecipeViewerEvents.addEntries('item', e => ...)`
  (also 'fluid'); mechanical renames left them without the target: add it.
- `ServerEvents.generateData` (old `highPriorityData`), `ServerEvents.recipes`, `afterRecipes`,
  `modifyRecipeIngredient`, `modifyRecipeResult`, `compostableRecipes`, `tags`, `loaded`, `tick`, `commandRegistry`.
- `PlayerEvents`: advancement chat chestClosed chestOpened cloned decorateChat inventoryChanged
  inventoryClosed inventoryOpened loggedIn loggedOut respawned stageAdded stageRemoved tick (re-verified 2026-11-12).
- `EntityEvents`: beforeHurt checkSpawn death drops spawned.

## Tooltips (verified with javap, 2026-11-12)
- `ItemEvents.modifyTooltips(e => e.add(ingredient, text => {...}))`; also `e.add(ingredient, [lines])`,
  `e.modify(...)`, `e.modifyAll(...)`. No `addAdvanced` in KubeJS 7.
- `TextActionBuilder` (`text`): `add`, `insert(index, [lines])`, `removeLine`, `removeText`,
  `removeExactText`, `clear`, `dynamic(id)`.
- `ItemEvents.dynamicTooltips` is a `TargetedEventHandler<String>`: `ItemEvents.dynamicTooltips('my_id', e => {...})`,
  triggered by `text.dynamic('my_id')`. Event: `e.item`, `e.lines`, `e.add(...)`, `e.addAll(...)`,
  `e.shift`, `e.ctrl`, `e.alt`, `e.advanced`, `e.creative`, `e.flags`.

## Attributes (Minecraft 1.21.1, verified with javap)
- `LivingEntity.getAttributes()` -> `AttributeMap` with `hasAttribute(Holder)`, `getValue(Holder)`, `getBaseValue(Holder)`;
  `LivingEntity.getAttributeValue(Holder)`.
- Holder: `BuiltInRegistries.ATTRIBUTE.getHolder(ResourceLocation.parse('ns:id'))` returns `Optional<Holder.Reference>`.
- Entity NBT `Attributes` list is gone as a reliable read (1.21 renamed keys to `attributes`/`id`/`base`); read live values.

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

## Facts verified by batch operators (2026-11-12, reuse them instead of re-checking)
- KubeJS ItemStack methods live on `dev.latvian.mods.kubejs.core.ItemStackKJS` (mixin interface; `kjs$foo` -> `foo`).
- `JEIEvents.registerCategories/registerRecipes` come from KubeJS Additions 6.0.0 (`pie.ilikepiefoo.compat.jei.JEIEvents`).
- LSO 2.4.7.2: no CapabilityUtil; `WetnessUtil` has static addWetness(Player,int), activateWetness, deactivateWetness, isWetnessActive(Player).
- ParCool 4.0.2.0: `com.alrex.parcool.common.Parkourability.get(Player)`, `getStamina()`;
  action start event `com.alrex.parcool.api.action.ParCoolActionEvent$Start$Pre`.
- NeoForge: ChunkEvent$Load, ScreenEvent$Render$Pre, ServerTickEvent$Pre, CanPlayerSleepEvent (not cancellable: use setProblem),
  MobEffectEvent$Applicable$Result.DO_NOT_APPLY. `NeoForgeMod.BLOCK_REACH` is gone (vanilla attribute `minecraft:player.block_interaction_range`).
- FTB Chunks 2101.1.23: no `EntityIcons`; MapIconEvent, EntityMapIcon, FTBChunksClientConfig exist.
- Bountiful 8.0.0-beta.2 keeps bounty data in its own data components (BountyStack), not in a custom-data JSON key.
- Quality Food 2.x: see the Quality Food decision in BATCH_ORDER.md.
- `BuiltInRegistries.X.get(rl)` returns the default entry for missing ids: guard with `containsKey(rl)`.
- Enchantments (1.21.1): `Enchantments.UNBREAKING` is a `ResourceKey`, not an Enchantment. Get the Holder with
  `server.registryAccess().registryOrThrow(Registries.ENCHANTMENT).getHolderOrThrow(key)`
  (`net.minecraft.core.registries.Registries`); then `EnchantmentHelper.getItemEnchantmentLevel(holder, stack)`,
  `stack.enchant(holder, level)` (KubeJS also has `kjs$enchant(Holder, int)`).
- ItemStack (vanilla 1.21.1): `has(DataComponentType)`, `isDamageableItem()`, `setDamageValue(int)`,
  `transmuteCopy(ItemLike[, count])` (copies components to another item: replaces `Item.of(newId, stack.nbt)`).
  Unbreakable = component `DataComponents.UNBREAKABLE`. KubeJS: `withCustomName(Component)`, `withLore([...])`.
- Tool tags: there is no `c:tools/pickaxes|shovels|axes` in 1.21.1; use vanilla `#minecraft:pickaxes`,
  `#minecraft:shovels`, `#minecraft:axes`, `#minecraft:hoes`; shears -> `#c:tools/shear`; generic -> `#c:tools/mining_tool`.
