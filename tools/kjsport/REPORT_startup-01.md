# REPORT startup-01

Status: done (12 batch files ported, operator worked directly, no opencode).

## Files and sites
- dogFollowTick.js: TickEvent$ServerTickEvent (phase check) -> neoforge tick ServerTickEvent$Pre (fires once per tick, phase check removed).
- forgeEvents/nerfHero.js: net.minecraftforge.eventbus.api.Event -> MobEffectEvent$Applicable$Result; Result.DENY -> DO_NOT_APPLY (verified in neoforge 21.1.265).
- forgeEvents/noSneakEating.js: MinecraftForge.EVENT_BUS -> NeoForge.EVENT_BUS; EventPriority -> net.neoforged.bus.api.EventPriority.
- forgeEvents/noSneakEating.js: wouldDrinkFluid now returns false (LSO CapabilityUtil missing in 1.21.1), so the client hand-drink block is disabled. Feature disabled.
- forgeEvents/fishingSkills.js: Item.of(id, drop.nbt) -> drop.withCount(n) (keeps data components; drop.nbt does not exist on 1.21.1).
- forgeEvents/husbandryTwins.js: comment only (Forge -> NeoForge).
- entityModification/modifyGolems.js: removed hay golem farmland fertilizer block (dew_drop_farmland_growth mod is not in the pack). Removal, listed. The hay golem tick now only scans.

## Unchanged (verified valid)
modifyChicken, modifyLongwings, modifyRibbits, culinariaSkills (RightClickBlock.getPos, getHitVec present), equipBankCard (CurioChangeEvent.getIdentifier), fishingRodLeveling.
Entity getNbt/setNbt/nbt remain valid (EntityKJS); not item NBT.

## Validation
- Rhino syntax (kjs-syntax-startup-01, detached, rhino-2101.2.7): all 12 batch files OK. One unrelated FAIL (startup_scripts/zz_port_runtime.js, file not found in instance) is outside this batch.
- grep for .nbt / withNBT / getOrCreateTag on batch files: only entity NBT hits remain (justified above).
- Not verified in game (owner tests).

Bom senso:
- Replaced the ThirstUtil/CapabilityUtil lookup with a disabled no-op rather than inventing a replacement API.
- Removed the dew_drop farmland branch because the mod is absent from the pack.
