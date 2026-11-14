console.info("[SOCIETY] fishingLoot.js loaded");


// Vanilla any_of over biome location checks. LootJS 3.7 matchAnyOf only takes built
// conditions, so the biome tags go through the vanilla condition codec instead.
const anyBiome = (tags) => ({
  condition: "minecraft:any_of",
  terms: tags.map((tag) => ({ condition: "minecraft:location_check", predicate: { biomes: tag } })),
});

LootJS.modifiers((e) => {
  // Has any stage check is to prevent jellies from being fished up from Crab Traps. Yeah it's weird.
  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("starting_items_4_1")
    .matchCustomCondition(anyBiome(["#minecraft:is_ocean", "#minecraft:is_beach"]))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:ocean_jelly"));
    });
  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .matchCustomCondition(anyBiome(["#minecraft:is_ocean", "#minecraft:is_beach"]))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:ocean_jelly"));
    });

  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("starting_items_4_1")
    .matchCustomCondition(anyBiome(["#minecraft:is_river"]))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:river_jelly"));
    });

  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .matchCustomCondition(anyBiome(["#minecraft:is_river"]))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:river_jelly"));
    });

  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:furniture_box"));
    });
  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("frozen_treasure")
    .matchPlayerCustom((p) => global.getSeasonFromLevel(p.level()) === "winter")
    .pool((p) => {
      p.when((c) => c.randomChance(0.45));
      p.addEntry(LootEntry.of("aquaculture:treasure_chest"));
    });

  e.addTableModifier(LootType.FISHING)
    .matchPlayerCustom((p) => p.getMainHandItem().getComponents().toString().contains("aquaculture:iron_hook"))
    .pool((p) => {
      p.when((c) => c.randomChance(0.5));
      p.addEntry(LootEntry.of("crabbersdelight:crab_trap_bait"));
      p.apply((f) => f.limitCount(4, 16));
    });

  e.addTableModifier(LootType.FISHING)
    .matchPlayerCustom((p) => p.getMainHandItem().getComponents().toString().contains("aquaculture:diamond_hook"))
    .pool((p) => {
      p.when((c) => c.randomChance(0.25));
      p.addEntry(LootEntry.of("crabbersdelight:deluxe_crab_trap_bait"));
      p.apply((f) => f.limitCount(1, 4));
    });

  e.addTableModifier(LootType.FISHING)
    .matchCustomCondition(anyBiome(["#minecraft:is_ocean", "#minecraft:is_beach"]))
    .matchPlayerCustom((p) => p.getMainHandItem().getComponents().toString().contains("aquaculture:redstone_hook"))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:ocean_jelly"));
      p.apply((f) => f.limitCount(1, 2));
    });

  e.addTableModifier(LootType.FISHING)
    .matchCustomCondition(anyBiome(["#minecraft:is_river"]))
    .matchPlayerCustom((p) => p.getMainHandItem().getComponents().toString().contains("aquaculture:redstone_hook"))
    .pool((p) => {
      p.when((c) => c.randomChance(0.1));
      p.addEntry(LootEntry.of("society:river_jelly"));
      p.apply((f) => f.limitCount(1, 2));
    });

  e.addTableModifier(LootType.FISHING)
    .matchPlayerCustom((p) => p.getMainHandItem().getComponents().toString().contains("aquaculture:nether_star_hook"))
    .pool((p) => {
      p.when((c) => c.randomChance(0.04));
      p.addEntry(LootEntry.of("society:relic_trove"));
      p.apply((f) => f.limitCount(1, 1));
    });
  e.addBlockModifier("aquaculture:neptunes_bounty")
    .hasAnyStage("prismatic_bounty")
    .matchMainHand(ItemFilter.hasEnchantment("minecraft:silk_touch").negate())
    .replaceLoot(
      "aquaculture:neptunes_bounty",
      "society:prismatic_shard",
      true
    );

  // Mastery
  e.addTableModifier(LootType.FISHING)
    .hasAnyStage("husbandry_mastery")
    .pool((p) => {
      p.when((c) => c.randomChance(0.01));
      p.addEntry(LootEntry.of("society:animal_cracker"));
      p.when((c) => c.randomChance(0.05));
      p.addEntry(LootEntry.of("society:plushie_capsule"));
    });
});
