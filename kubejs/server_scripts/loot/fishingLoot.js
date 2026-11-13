console.info("[SOCIETY] fishingLoot.js loaded");

LootJS.modifiers((e) => {
  // Has any stage check is to prevent jellies from being fished up from Crab Traps. Yeah it's weird.
  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("starting_items_4_1")
    .anyBiome("#minecraft:is_ocean", "#minecraft:is_beach")
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:ocean_jelly");
    });
  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .anyBiome("#minecraft:is_ocean", "#minecraft:is_beach")
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:ocean_jelly");
    });

  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("starting_items_4_1")
    .anyBiome("#minecraft:is_river")
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:river_jelly");
    });

  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .anyBiome("#minecraft:is_river")
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:river_jelly");
    });

  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("wooden_pollution")
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:furniture_box");
    });
  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("frozen_treasure")
    .playerPredicate((p) => global.getSeasonFromLevel(p.level) === "winter")
    .pool((p) => {
      p.randomChance(0.45).addLoot("aquaculture:treasure_chest");
    });

  e.addTypeModifier(LootType.FISHING)
    .playerPredicate((p) => p.getHeldItem("main_hand").getComponents().toString().contains("aquaculture:iron_hook"))
    .pool((p) => {
      p.randomChance(0.5).addLoot("crabbersdelight:crab_trap_bait");
      p.limitCount([4, 16]);
    });

  e.addTypeModifier(LootType.FISHING)
    .playerPredicate((p) => p.getHeldItem("main_hand").getComponents().toString().contains("aquaculture:diamond_hook"))
    .pool((p) => {
      p.randomChance(0.25).addLoot("crabbersdelight:deluxe_crab_trap_bait");
      p.limitCount([1, 4]);
    });

  e.addTypeModifier(LootType.FISHING)
    .anyBiome("#minecraft:is_ocean", "#minecraft:is_beach")
    .playerPredicate((p) => p.getHeldItem("main_hand").getComponents().toString().contains("aquaculture:redstone_hook"))
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:ocean_jelly");
      p.limitCount([1, 2]);
    });

  e.addTypeModifier(LootType.FISHING)
    .anyBiome("#minecraft:is_river")
    .playerPredicate((p) => p.getHeldItem("main_hand").getComponents().toString().contains("aquaculture:redstone_hook"))
    .pool((p) => {
      p.randomChance(0.1).addLoot("society:river_jelly");
      p.limitCount([1, 2]);
    });

  e.addTypeModifier(LootType.FISHING)
    .playerPredicate((p) => p.getHeldItem("main_hand").getComponents().toString().contains("aquaculture:nether_star_hook"))
    .pool((p) => {
      p.randomChance(0.04).addLoot("society:relic_trove");
      p.limitCount([1, 1]);
    });
  e.addBlockModifier("aquaculture:neptunes_bounty")
    .hasAnyStage("prismatic_bounty")
    .not((n) =>
      n.matchMainHand(ItemFilter.hasEnchantment("minecraft:silk_touch"))
    )
    .replaceLoot(
      "aquaculture:neptunes_bounty",
      "society:prismatic_shard",
      true
    );

  // Mastery
  e.addTypeModifier(LootType.FISHING)
    .hasAnyStage("husbandry_mastery")
    .pool((p) => {
      p.randomChance(0.01).addLoot("society:animal_cracker");
      p.randomChance(0.05).addLoot("society:plushie_capsule");
    });
});
