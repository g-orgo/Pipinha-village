// priority: -10
console.info("[SOCIETY] professionLoot.js loaded");

// Farming Specialty perks on fully grown crops. Each perk is isolated in its
// own try/catch so one failing perk never breaks the normal drops.
const specialtyLootPerk = (label, fn) => {
  try {
    fn();
  } catch (err) {
    console.error(`[specialty] crop loot ${label} failed: ${err}`);
  }
};

const isSeedItem = (item) => String(item.id).includes("seed");

const profLootParams = Java.loadClass("net.minecraft.world.level.storage.loot.parameters.LootContextParams");
const profCropBlock = Java.loadClass("net.minecraft.world.level.block.CropBlock");

// Crop is fully grown: CropBlock.isMaxAge for crops, otherwise the "age" property at its maximum.
const isProfessionCropMaxGrown = (state) => {
  const block = state.block;
  if (block instanceof profCropBlock) return block.isMaxAge(state);
  const ageProp = block.getStateDefinition().getProperty("age");
  if (!ageProp) return false;
  const maxAge = Math.max.apply(null, Java.from(ageProp.getPossibleValues()));
  return Number(state.getValue(ageProp)) === maxAge;
};

// Adds an item by id (with a count) only when the mod providing it is loaded.
const profAddLootId = (loot, id, count) => {
  if (Item.exists(id)) loot.addItem(Item.of(id, count));
};

LootJS.modifiers((e) => {
  e.addBlockModifier(global.cropList).customAction((context, loot) => specialtyLootPerk("context", () => {
    // 1.21 LootContext has no getPlayerOrNull: the breaking entity is THIS_ENTITY.
    const player = context.getParamOrNull(profLootParams.THIS_ENTITY);
    if (!player || !player.isPlayer() || player.isFake() || global.specialtyTier(player, "farming") === 0) return;

    const state = context.getParamOrNull(profLootParams.BLOCK_STATE);
    if (!state || !isProfessionCropMaxGrown(state)) return;
    const crop = state.block;
    const longCycle = crop instanceof profCropBlock && crop.getMaxAge() >= 7;
    const tier = global.specialtyTier(player, "farming");

    specialtyLootPerk("extra", () => {
      if (!global.rollSpecialty(player, "farming", "crop_extra")) return;
      loot.modifyItems((item) => {
        if (!isSeedItem(item)) item.setCount(item.getCount() + 1);
        return item;
      });
    });

    specialtyLootPerk("quality", () => {
      const perk = longCycle ? "crop_quality_long" : "crop_quality";
      if (!global.rollSpecialty(player, "farming", perk)) return;
      loot.modifyItems((item) => {
        if (!isSeedItem(item)) global.bumpQuality(item);
        return item;
      });
    });

    specialtyLootPerk("seed", () => {
      if (!global.rollSpecialty(player, "farming", "crop_seed")) return;
      const seed = Item.of(crop.asItem());
      if (!seed.isEmpty()) loot.addItem(seed);
    });

    specialtyLootPerk("feed", () => {
      if (global.rollSpecialty(player, "farming", "feed_drop")) profAddLootId(loot, "society:animal_feed", 1);
    });

    specialtyLootPerk("worm", () => {
      if (!global.rollSpecialty(player, "farming", "worm_drop")) return;
      profAddLootId(loot, "aquaculture:worm", tier === 2 ? 2 : 1);
    });
  }));
});
