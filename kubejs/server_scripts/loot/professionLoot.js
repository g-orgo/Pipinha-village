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

LootJS.modifiers((e) => {
  e.addBlockModifier(global.cropList).apply((c) => specialtyLootPerk("context", () => {
    let player = c.getPlayer();
    if (!player || player.isFake() || global.specialtyTier(player, "farming") === 0) return;

    let state = c.destroyedBlock.blockState;
    let crop = state.block;
    if (!crop.isMaxAge || !crop.isMaxAge(state)) return;
    let longCycle = typeof crop.getMaxAge === "function" && crop.getMaxAge() >= 7;
    let tier = global.specialtyTier(player, "farming");

    specialtyLootPerk("extra", () => {
      if (!global.rollSpecialty(player, "farming", "crop_extra")) return;
      c.forEachLoot((item) => {
        if (!isSeedItem(item)) item.setCount(item.getCount() + 1);
      });
    });

    specialtyLootPerk("quality", () => {
      let perk = longCycle ? "crop_quality_long" : "crop_quality";
      if (!global.rollSpecialty(player, "farming", perk)) return;
      c.forEachLoot((item) => {
        if (!isSeedItem(item)) global.bumpQuality(item);
      });
    });

    specialtyLootPerk("seed", () => {
      if (!global.rollSpecialty(player, "farming", "crop_seed")) return;
      let seed = Item.of(crop.asItem());
      if (!seed.isEmpty()) c.addLoot(seed);
    });

    specialtyLootPerk("feed", () => {
      if (global.rollSpecialty(player, "farming", "feed_drop")) c.addLoot("society:animal_feed");
    });

    specialtyLootPerk("worm", () => {
      if (!global.rollSpecialty(player, "farming", "worm_drop")) return;
      c.addLoot(tier === 2 ? "2x aquaculture:worm" : "aquaculture:worm");
    });
  }));
});
