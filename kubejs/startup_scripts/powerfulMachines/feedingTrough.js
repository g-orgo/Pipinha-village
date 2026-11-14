console.info("[SOCIETY] feedingTrough.js loaded");

const feedFunction = (
  level,
  animal,
  day,
  inventory,
  hasAnimalFeed,
  hasCandiedFeed,
  hasManaFeed
) => {
  let data = animal.persistentData;
  if (!data.getInt("ageLastFed") || day < data.getInt("ageLastFed")) {
    data.ageLastFed = day;
  }
  if (day > data.ageLastFed) {
    let fed = false;
    let boost = 0;
    // prefer candied > mana > normal
    if (
      hasCandiedFeed &&
      global.useInventoryItems(inventory, "society:candied_animal_feed", 1) == 1
    ) {
      fed = true;
      boost = 100;
    } else if (hasManaFeed && global.useInventoryItems(inventory, "society:mana_feed", 1) == 1) {
      fed = true;
      boost = 30;
    } else if (
      hasAnimalFeed &&
      global.useInventoryItems(inventory, "society:animal_feed", 1) == 1
    ) {
      fed = true;
    }

    if (fed) {
      animal.heal(4);
      data.ageLastFed = day;
      if (boost > 0) data.affection = data.getInt("affection") + boost;
      level.spawnParticles(
        true,
        animal.x,
        animal.y + 1.5,
        animal.z,
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        5,
        0.01
      );
    }
  }
};
global.runFeedingTrough = (be, inventory, block, level) => {
  let radius = 6;
  let hasAnimalFeed = global.inventoryHasItems(inventory, "society:animal_feed", 1) == 1;
  let hasCandiedFeed = global.inventoryHasItems(inventory, "society:candied_animal_feed", 1) == 1;
  let hasManaFeed = global.inventoryHasItems(inventory, "society:mana_feed", 1) == 1;
  if (!(hasAnimalFeed || hasCandiedFeed || hasManaFeed)) return;
  let slots = inventory.getSlots();
  let feedCount = 0;

  let nearbyFarmAnimals;
  let day = global.getDay(level);
  nearbyFarmAnimals = level
    .getEntitiesWithin(AABB.ofBlock(block).inflate(radius))
    .filter((entity) => global.checkEntityTag(entity, "society:husbandry_animal"));

  nearbyFarmAnimals.forEach((animal) => {
    feedFunction(level, animal, day, inventory, hasAnimalFeed, hasCandiedFeed, hasManaFeed);
  });
  // Handle visual
  for (let i = 0; i < slots; i++) {
    if (inventory.getStackInSlot(i).hasTag("society:animal_feed"))
      feedCount += inventory.getStackInSlot(i).count;
  }
  let fill = 0;
  if (feedCount >= 512) fill = 4;
  else if (feedCount >= 256) fill = 3;
  else if (feedCount >= 128) fill = 2;
  else if (feedCount >= 8) fill = 1;
  be.block.set(be.block.id, {
    facing: be.block.properties.facing,
    fill: String(fill),
  });
};
StartupEvents.registry("block", (event) => {
  event
    .create("society:feeding_trough", "cardinal")
    .property(integerProperty.create("fill", 0, 4))
    .tagBlock("minecraft:mineable/axe")
    .tagBlock("minecraft:needs_stone_tool")
    .box(0, 0, 2, 16, 12, 14)
    .defaultCutout()
    .item((item) => {
      item.tooltip(Text.translatable("block.society.feeding_trough.description").gray());
      item.tooltip(Text.translatable("tooltip.society.area", `13x13x13`).green());
      item.modelGenerator((m) => m.parent("farm_and_charm:block/feeding_trough_size_0"));
    })
    .defaultState((state) => {
      state.set(integerProperty.create("fill", 0, 4), 0);
    })
    .placementState((state) => {
      state.set(integerProperty.create("fill", 0, 4), 0);
    })
    .blockEntity((blockInfo) => {
      blockInfo.inventory("inventory", Direction.ALL_SET, 9, 1);
      blockInfo.initialData({ fill: "0" });
      blockInfo.serverTicking();
      blockInfo.tickFrequency(300);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:feeding_trough"] = (entity) => {
        const { inventory, block, level } = entity;
        global.runFeedingTrough(entity, inventory, block, level);
      };
        blockInfo.rightClickOpensInventory("inventory");
    });
});
