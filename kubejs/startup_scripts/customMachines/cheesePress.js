//priority: 100
console.info("[SOCIETY] mayonnaiseMachine.js loaded");

global.cheesePressRecipes = new Map([
  ["society:sheep_milk", { output: ["1x meadow:sheep_cheese_slice"] }],
  ["society:milk", { output: ["1x meadow:cheese_slice"] }],
  ["society:buffalo_milk", { output: ["1x meadow:buffalo_cheese_slice"] }],
  ["society:goat_milk", { output: ["1x meadow:goat_cheese_slice"] }],
  ["society:warped_milk", { output: ["1x meadow:warped_cheese_slice"] }],
  ["society:grain_milk", { output: ["1x meadow:grain_cheese_slice"] }],
  ["society:amethyst_milk", { output: ["1x meadow:amethyst_cheese_slice"] }],
  ["society:large_sheep_milk", { output: ["1x meadow:sheep_cheese_wheel"] }],
  ["society:large_milk", { output: ["1x meadow:cheese_wheel"] }],
  [
    "society:large_buffalo_milk",
    { output: ["1x meadow:buffalo_cheese_wheel"] },
  ],
  ["society:large_goat_milk", { output: ["1x meadow:goat_cheese_wheel"] }],
  ["society:large_warped_milk", { output: ["1x meadow:warped_cheese_wheel"] }],
  ["society:large_grain_milk", { output: ["1x meadow:grain_cheese_wheel"] }],
  [
    "society:large_amethyst_milk",
    { output: ["1x meadow:amethyst_cheese_wheel"] },
  ],
]);

StartupEvents.registry("block", (event) => {
  event
    .create("society:cheese_press", "cardinal")
    .property(booleanProperty.create("working"))
    .property(booleanProperty.create("mature"))
    .property(booleanProperty.create("upgraded"))
    .soundType("copper")
    .box(2, 0, 2, 14, 19, 14)
    .defaultCutout()
    .tagBlock("minecraft:mineable/pickaxe")
    .tagBlock("minecraft:mineable/axe")
    .tagBlock("minecraft:needs_stone_tool")
    .displayName("Artisan Cheese Press")
    .item((item) => {
      item.tooltip(Text.translatable("block.society.cheese_press.description").gray());
      item.tooltip(Text.translatable("society.working_block_entity.preserve_quality").green());
      item.modelGenerator((m) => m.parent("society:block/kubejs/cheese_press/cheese_press_off"));
    })
    .defaultState((state) => {
      state
        .set(booleanProperty.create("working"), false)
        .set(booleanProperty.create("mature"), false)
        .set(booleanProperty.create("upgraded"), false)
    })
    .placementState((state) => {
      state
        .set(booleanProperty.create("working"), false)
        .set(booleanProperty.create("mature"), false)
        .set(booleanProperty.create("upgraded"), false)
    })
    .rightClick((click) => {
      const { player, item, block, hand, level } = click;
      if (player.isFake()) return;
      const upgraded = block.properties.get("upgraded").toLowerCase() == "true";
      const facing = block.properties.get("facing").toLowerCase();

      if (hand == "OFF_HAND") return;
      if (hand == "MAIN_HAND") {
        if (!upgraded && item == "society:pink_matter") {
          if (!player.isCreative()) item.count--;
          level.spawnParticles(
            "farmersdelight:star",
            true,
            block.x,
            block.y + 1,
            block.z,
            0.2 * rnd(1, 2),
            0.2 * rnd(1, 2),
            0.2 * rnd(1, 2),
            3,
            0.01
          );
          block.set(block.id, {
            facing: facing,
            working: block.properties.get("working"),
            mature: block.properties.get("mature"),
            upgraded: true
          });
        }
      }
      let outputCount = 1;
      if (player.stages.has("rancher") && Math.random() <= 0.2) {
        outputCount = 2;
      }
      global.handleBERightClick(
        "species:block.frozen_meat.place",
        click,
        global.cheesePressRecipes,
        3,
        false,
        false,
        outputCount,
        false,
        true
      );
    })
    .blockEntity((blockInfo) => {
      blockInfo.initialData({ stage: 0, recipe: "", quality: 0 });
      blockInfo.serverTicking();
      blockInfo.tickFrequency(artMachineTickRate);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:cheese_press"] = (entity) => {
        global.handleBETick(entity, global.cheesePressRecipes, 2);
      };
    });
});
