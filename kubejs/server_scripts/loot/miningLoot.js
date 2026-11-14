console.info("[SOCIETY] miningLoot.js loaded");

const Player = Java.loadClass("net.minecraft.world.entity.player.Player");

const overworldOres = [
  "meadow:alpine_diamond_ore",
  "meadow:alpine_salt_ore",
  "meadow:alpine_redstone_ore",
  "meadow:alpine_coal_ore",
  "meadow:alpine_lapis_ore",
  "meadow:alpine_gold_ore",
  "meadow:alpine_iron_ore",
  "meadow:alpine_copper_ore",
  "minecraft:deepslate_gold_ore",
  "minecraft:gold_ore",
  "minecraft:deepslate_copper_ore",
  "minecraft:copper_ore",
  "minecraft:deepslate_iron_ore",
  "minecraft:iron_ore",
  "minecraft:deepslate_coal_ore",
  "minecraft:coal_ore",
  "minecraft:redstone_ore",
  "minecraft:deepslate_diamond_ore",
  "minecraft:diamond_ore",
  "minecraft:deepslate_lapis_ore",
  "minecraft:lapis_ore",
  "create:deepslate_zinc_ore",
  "create:zinc_ore",
  "minecraft:deepslate_redstone_ore",
  "minecraft:deepslate_emerald_ore",
  "minecraft:emerald_ore",
];
const netherOres = [
  "minecraft:nether_gold_ore",
  "minecraft:nether_quartz_ore",
  "etcetera:nether_bismuth_ore",
];
const skullCavernOres = [
  "oreganized:lead_ore",
  "oreganized:deepslate_lead_ore",
  "oreganized:silver_ore",
  "oreganized:deepslate_silver_ore",
  "society:iridium_ore",
  "society:deepslate_iridium_ore",
  "society:sparkstone_ore",
  "society:deepslate_sparkstone_ore",
];

// True when the tool in use does not have silk touch (vanilla inverted match_tool).
const notSilkTouch = (c) =>
  c.matchCustomCondition({
    condition: "minecraft:inverted",
    term: {
      condition: "minecraft:match_tool",
      predicate: {
        predicates: {
          "minecraft:enchantments": [
            { enchantments: "minecraft:silk_touch", levels: { min: 1 } },
          ],
        },
      },
    },
  });

const playerEntity = (c) =>
  c.matchEntityCustom((entity) => entity instanceof Player);

// Adds one entry to the pool, rolled with the given chance.
const chanceEntry = (p, entry, chance) => {
  p.when((c) => c.randomChance(chance));
  p.addEntry(LootEntry.of(entry));
};

// Pool that skips silk touch, optionally requires a player and optionally rolls a chance.
const lootPool = (p, entry, chance, playerOnly) => {
  p.when(notSilkTouch);
  if (playerOnly) p.when(playerEntity);
  if (chance !== undefined) p.when((c) => c.randomChance(chance));
  p.addEntry(LootEntry.of(entry));
};

// Single roll over [id, weight] pairs; ids that do not exist are skipped.
const weightedPool = (p, entries) => {
  p.rolls(1);
  entries.forEach(([id, weight]) => {
    if (Item.exists(id)) p.addEntry(LootEntry.of(id).withWeight(weight));
  });
};

const weightedLootPool = (p, entries, chance) => {
  p.when(notSilkTouch);
  p.when((c) => c.randomChance(chance));
  weightedPool(p, entries);
};

const addMiningLootToAllOres = (e, stage, chance, item, otherPool) => {
  overworldOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => lootPool(p, item, chance, false));
  });
  netherOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => lootPool(p, item, chance, false));
  });

  skullCavernOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => lootPool(p, item, chance, false));
  });
  if (otherPool && otherPool.length > 0) {
    otherPool.forEach((ore) => {
      e.addBlockModifier(ore)
        .hasAnyStage(stage)
        .pool((p) => lootPool(p, item, chance, false));
    });
  }
};
const addWeightedMiningLootToAllOres = (e, stage, chance, item, otherPool) => {
  overworldOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => weightedLootPool(p, item, chance));
  });
  netherOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => weightedLootPool(p, item, chance));
  });

  skullCavernOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(stage)
      .pool((p) => weightedLootPool(p, item, chance));
  });
  if (otherPool && otherPool.length > 0) {
    otherPool.forEach((ore) => {
      e.addBlockModifier(ore)
        .hasAnyStage(stage)
        .pool((p) => weightedLootPool(p, item, chance));
    });
  }
};
const addAdditionalGeodeRoll = (e, geodeStage) => {
  overworldOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(geodeStage)
      .pool((p) => lootPool(p, "society:geode", 0.1, false));
    e.addBlockModifier(ore)
      .matchBiome("#c:is_cold")
      .hasAnyStage(geodeStage)
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, false));
    e.addBlockModifier(ore)
      .matchPlayerCustom((p) => global.getSeasonFromLevel(p.level()) === "winter")
      .hasAnyStage(geodeStage)
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, false));
    e.addBlockModifier(ore)
      .matchBiome("#society:is_skull_cavern")
      .hasAnyStage(geodeStage)
      .pool((p) => lootPool(p, "society:omni_geode", 0.04, false));
  });
  netherOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage(geodeStage)
      .pool((p) => lootPool(p, "society:magma_geode", 0.1, false));
  });
};
LootJS.modifiers((e) => {
  overworldOres.forEach((ore) => {
    e.addBlockModifier(ore).pool((p) =>
      lootPool(p, "society:geode", 0.1, true)
    );
    e.addBlockModifier(ore)
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:earth_crystal", 0.1, false));
    e.addBlockModifier(ore)
      .matchBiome("#c:is_cold")
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, true));
    e.addBlockModifier(ore)
      .matchPlayerCustom((p) => global.getSeasonFromLevel(p.level()) === "winter")
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, true));
    e.addBlockModifier(ore)
      .matchBiome("#c:is_cold")
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:frozen_tear", 0.1, false));
    e.addBlockModifier(ore)
      .matchBiome("#society:is_skull_cavern")
      .pool((p) => lootPool(p, "society:omni_geode", 0.04, true));
    e.addBlockModifier(ore)
      .matchBiome("#society:is_skull_cavern")
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:jade", 0.02, false));
    e.addBlockModifier(ore)
      .hasAnyStage("blockchain")
      .pool((p) => lootPool(p, "numismatics:crown", 0.03, false));
    e.addBlockModifier(ore)
      .hasAnyStage("furniture_archaeologist")
      .pool((p) => lootPool(p, "society:furniture_box", 0.03, false));
    e.addBlockModifier(ore)
      .hasAnyStage("star_blessing")
      .matchDimension("minecraft:overworld")
      .pool((p) => lootPool(p, "society:pristine_star_shards", 0.02, false));
    e.addBlockModifier(ore)
      .hasAnyStage("star_blessing")
      .matchDimension("society:skull_cavern")
      .pool((p) => lootPool(p, "society:pristine_star_shards", 0.06, false));
  });
  e.addBlockModifier("society:geode_node")
    .matchBiome("#c:is_cold")
    .pool((p) => chanceEntry(p, "society:frozen_geode", 0.1));
  e.addBlockModifier("society:geode_node").pool((p) =>
    chanceEntry(p, "society:mining_monthly", 0.05)
  );
  e.addBlockModifier("society:geode_node")
    .matchDimension("minecraft:overworld")
    .hasAnyStage("prismatic_prospector")
    .pool((p) => chanceEntry(p, "society:prismatic_shard", 0.05));
  e.addBlockModifier("society:magma_geode_node").pool((p) =>
    chanceEntry(p, "society:mining_monthly", 0.1)
  );
  e.addBlockModifier("society:magma_geode_node")
    .matchDimension("minecraft:the_nether")
    .hasAnyStage("prismatic_prospector")
    .pool((p) => chanceEntry(p, "society:prismatic_shard", 0.2));
  e.addBlockModifier("society:omni_geode_node").pool((p) =>
    chanceEntry(p, "society:mining_monthly", 0.1)
  );
  e.addBlockModifier("society:omni_geode_node")
    .hasAnyStage("prismatic_prospector")
    .pool((p) => chanceEntry(p, "society:prismatic_shard", 0.3));
  e.addBlockModifier("minecraft:deepslate")
    .hasAnyStage("filthy_excavator")
    .pool((p) => chanceEntry(p, "society:geode", 0.02));
  e.addBlockModifier("minecraft:netherrack")
    .hasAnyStage("filthy_excavator")
    .pool((p) => chanceEntry(p, "society:magma_geode", 0.01));

  netherOres.forEach((ore) => {
    e.addBlockModifier(ore).pool((p) =>
      lootPool(p, "society:magma_geode", 0.1, true)
    );
    e.addBlockModifier(ore)
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:fire_quartz", 0.1, false));
    e.addBlockModifier(ore)
      .hasAnyStage("blockchain")
      .pool((p) => lootPool(p, "numismatics:crown", 0.06, false));
    e.addBlockModifier(ore)
      .hasAnyStage("furniture_archaeologist")
      .pool((p) => lootPool(p, "society:furniture_box", 0.01, false));
    e.addBlockModifier(ore)
      .hasAnyStage("star_blessing")
      .matchDimension("minecraft:the_nether")
      .pool((p) => lootPool(p, "society:pristine_star_shards", 0.04, false));
    e.addBlockModifier(ore)
      .hasAnyStage("star_blessing")
      .matchDimension("society:skull_cavern")
      .pool((p) => lootPool(p, "society:pristine_star_shards", 0.06, false));
  });
  skullCavernOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .matchBiome("#c:is_cold")
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, true));
    e.addBlockModifier(ore)
      .matchPlayerCustom((p) => global.getSeasonFromLevel(p.level()) === "winter")
      .pool((p) => lootPool(p, "society:frozen_geode", 0.1, true));
    e.addBlockModifier(ore)
      .matchBiome("#c:is_cold")
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:frozen_tear", 0.1, false));
    e.addBlockModifier(ore)
      .matchBiome("#society:is_skull_cavern")
      .pool((p) => lootPool(p, "society:omni_geode", 0.04, true));
    e.addBlockModifier(ore)
      .matchBiome("#society:is_skull_cavern")
      .hasAnyStage("mineralogist")
      .pool((p) => lootPool(p, "society:jade", 0.02, false));
    e.addBlockModifier(ore)
      .hasAnyStage("blockchain")
      .pool((p) => lootPool(p, "numismatics:crown", 0.03, false));
    e.addBlockModifier(ore)
      .hasAnyStage("furniture_archaeologist")
      .pool((p) => lootPool(p, "society:furniture_box", 0.03, false));
    e.addBlockModifier(ore)
      .hasAnyStage("star_blessing")
      .matchDimension("society:skull_cavern")
      .pool((p) => lootPool(p, "society:pristine_star_shards", 0.06, false));
  });
  [
    "minecraft:deepslate_gold_ore",
    "meadow:alpine_gold_ore",
    "minecraft:gold_ore",
  ].forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage("gold_rush")
      .pool((p) =>
        lootPool(p, Item.of("4x minecraft:raw_gold_block"), undefined, false)
      );
  });
  addMiningLootToAllOres(
    e,
    "the_spark_also_rises",
    1,
    Item.of("1x society:sparkstone")
  );

  addMiningLootToAllOres(
    e,
    "husbandry_mastery",
    0.01,
    Item.of("1x society:animal_cracker"),
    [
      "society:oak_supply_crate",
      "society:spruce_supply_crate",
      "society:palm_supply_crate",
      "society:grimwood_supply_crate",
    ]
  );
  ["society:sparkstone_ore", "society:deepslate_sparkstone_ore"].forEach(
    (ore) => {
      e.addBlockModifier(ore)
        .hasAnyStage("mining_mastery")
        .pool((p) =>
          lootPool(p, "society:the_spark_also_rises", 0.001, false)
        );
    }
  );

  addAdditionalGeodeRoll(e, "excavator");

  // Mastery Moon Statue
  const weightedRemains = [
    "betterarcheology:creeper_fossil_body",
    "betterarcheology:creeper_fossil_head",
    "betterarcheology:villager_fossil_body",
    "betterarcheology:villager_fossil_head",
    "betterarcheology:chicken_fossil_body",
    "betterarcheology:chicken_fossil_head",
    "betterarcheology:ocelot_fossil_body",
    "betterarcheology:ocelot_fossil_head",
    "betterarcheology:wolf_fossil_body",
    "betterarcheology:wolf_fossil_head",
    "betterarcheology:sheep_fossil_body",
    "betterarcheology:sheep_fossil_head",
    "betterarcheology:guardian_fossil_head",
    "betterarcheology:guardian_fossil_body",
    "crittersandcompanions:clam",
    "species:petrified_egg",
    "society:petrified_slime",
    "twigs:petrified_lichen",
    "atmospheric:petrified_armor_trim_smithing_template",
    "betterarcheology:fossiliferous_dirt",
    "minecraft:bone",
    "aquaculture:fish_bones",
    "netherdepthsupgrade:bonefish",
    "society:fantasy_box_bone",
    "betterarcheology:artifact_shards",
    "society:artifact_trove",
  ].map((remain) => [remain, 1]);

  addWeightedMiningLootToAllOres(e, "moon_remains", 0.05, weightedRemains);
  addAdditionalGeodeRoll(e, "moon_geode_roll");

  overworldOres.forEach((ore) => {
    e.addBlockModifier(ore)
      .hasAnyStage("moon_extra_ore")
      .modifyLoot(ItemFilter.ANY, (itemStack) => {
        if (itemStack.hasTag("c:raw_materials"))
          itemStack.setCount(itemStack.getCount() + 1);
        return itemStack;
      });
  });
});
