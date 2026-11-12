//priority: 100
console.info("[SOCIETY] seedMaker.js loaded");

global.seedMakerRecipes = new Map([
  ["farm_and_charm:corn", { output: ["6x farm_and_charm:kernels"] }],
  ["minecraft:wheat", { output: ["6x minecraft:wheat_seeds"] }],
  ["vinery:jungle_grapes_red", { output: ["6x vinery:jungle_grape_seeds_red"] }],
  ["vinery:jungle_grapes_white", { output: ["6x vinery:jungle_grape_seeds_white"] }],
  ["herbalbrews:green_tea_leaf", { output: ["6x herbalbrews:tea_blossom"] }],
  ["snowyspirit:ginger", { output: ["6x snowyspirit:ginger_flower"] }],
  ["minecraft:pumpkin", { output: ["6x minecraft:pumpkin_seeds"] }],
  ["minecraft:melon_slice", { output: ["6x minecraft:melon_seeds"] }],
  ["minecraft:beetroot", { output: ["6x minecraft:beetroot_seeds"] }],
  ["brewery:hops", { output: ["6x brewery:hop_trellis_seed"] }],
  ["farm_and_charm:lettuce", { output: ["6x farm_and_charm:lettuce_seeds"] }],
  ["supplementaries:flax", { output: ["6x supplementaries:flax_seeds"] }],
  ["society:eggplant", { output: ["6x society:eggplant_seed"] }],
  ["farm_and_charm:strawberry", { output: ["6x farm_and_charm:strawberry_seed"] }],
  ["farm_and_charm:oat", { output: ["6x farm_and_charm:oat_seeds"] }],
  ["farm_and_charm:barley", { output: ["6x farm_and_charm:barley_seeds"] }],
  ["nethervinery:crimson_grape", { output: ["6x nethervinery:crimson_grape_seeds"] }],
  ["nethervinery:warped_grape", { output: ["6x nethervinery:warped_grape_seeds"] }],
  ["vinery:red_grape", { output: ["6x vinery:red_grape_seeds"] }],
  ["vinery:white_grape", { output: ["6x vinery:white_grape_seeds"] }],
  ["vinery:savanna_grapes_red", { output: ["6x vinery:savanna_grape_seeds_red"] }],
  ["vinery:savanna_grapes_white", { output: ["6x vinery:savanna_grape_seeds_white"] }],
  ["vinery:taiga_grapes_red", { output: ["6x vinery:taiga_grape_seeds_red"] }],
  ["vinery:taiga_grapes_white", { output: ["6x vinery:taiga_grape_seeds_white"] }],
  ["farmersdelight:cabbage", { output: ["6x farmersdelight:cabbage_seeds"] }],
  ["vintagedelight:cucumber", { output: ["6x vintagedelight:cucumber_seeds"] }],
  ["vintagedelight:ghost_pepper", { output: ["6x vintagedelight:ghost_pepper_seeds"] }],
  ["society:ancient_fruit", { output: ["1x society:ancient_fruit_seed"] }],
  ["farmersdelight:tomato", { output: ["6x farmersdelight:tomato_seeds"] }],
  ["etcetera:cotton_flower", { output: ["6x etcetera:cotton_seeds"] }],
  ["society:tubabacco_leaf", { output: ["6x society:tubabacco_leaf_seed"] }],
  ["society:blueberry", { output: ["6x society:blueberry_seed"] }],
  ["minecraft:pitcher_plant", { output: ["6x minecraft:pitcher_pod"] }],
  ["minecraft:torchflower", { output: ["6x minecraft:torchflower_seeds"] }],
  ["veggiesdelight:bellpepper", { output: ["6x veggiesdelight:bellpepper_seeds"] }],
  ["veggiesdelight:cauliflower", { output: ["6x veggiesdelight:cauliflower_seeds"] }],
  ["veggiesdelight:garlic", { output: ["6x veggiesdelight:garlic_seed"] }],
  [
    { output: ["6x botania_seeds:light_blue_mystical_flower_seed"] },
  ],
  [
    { output: ["6x botania_seeds:magenta_mystical_flower_seed"] },
  ],
  [
    { output: ["6x botania_seeds:light_gray_mystical_flower_seed"] },
  ],
  // Rice is also a food priced like its panicle, so it stays unit for unit (see globalPriceBalance.js).
  ["farmersdelight:rice_panicle", { output: ["3x farmersdelight:rice"] }],
  ["minecraft:potato", { output: ["6x society:potato_seed"] }],
  ["minecraft:carrot", { output: ["6x society:carrot_seed"] }],
  ["farm_and_charm:onion", { output: ["6x society:onion_seed"] }],
  ["vintagedelight:peanut", { output: ["6x society:peanut_seed"] }],
  ["veggiesdelight:sweet_potato", { output: ["6x society:sweet_potato_seed"] }],
  ["mysticaloaktree:wise_oak", { output: ["1x botania:overgrowth_seed"] }],
  ["atmospheric:currant", { output: ["6x atmospheric:currant_seedling"] }],
  ["atmospheric:aloe_leaves", { output: ["6x atmospheric:aloe_kernels"] }],
  ["veggiesdelight:turnip", { output: ["6x veggiesdelight:turnip_seeds"] }],
  ["veggiesdelight:broccoli", { output: ["6x veggiesdelight:broccoli_seeds"] }],
  ["veggiesdelight:zucchini", { output: ["6x veggiesdelight:zucchini_seeds"] }],
  ["society:cranberry", { output: ["6x society:cranberry_seed"] }],
  ["society:sparkpod", { output: ["16x society:sparkstone"] }],
  ["hearthandharvest:blueberries", { output: ["6x hearthandharvest:blueberry_pips"] }],
  ["kaleidoscope_cookery:lettuce", { output: ["6x kaleidoscope_cookery:lettuce_seed"] }],
  ["kaleidoscope_cookery:red_chili", { output: ["6x kaleidoscope_cookery:chili_seed"] }],
  ["kaleidoscope_cookery:green_chili", { output: ["6x kaleidoscope_cookery:chili_seed"] }],
  ["culturaldelights:cucumber", { output: ["6x culturaldelights:cucumber_seeds"] }],
  ["culturaldelights:eggplant", { output: ["6x culturaldelights:eggplant_seeds"] }],
  ["youkaishomecoming:cucumber", { output: ["6x youkaishomecoming:cucumber_seeds"] }],
  ["youkaishomecoming:black_grape", { output: ["6x youkaishomecoming:black_grape_seeds"] }],
  ["youkaishomecoming:tea_leaves", { output: ["6x youkaishomecoming:tea_seeds"] }],
  ["farmersrespite:green_tea_leaves", { output: ["6x farmersrespite:tea_seeds"] }],
  ["farmersrespite:black_tea_leaves", { output: ["6x farmersrespite:tea_seeds"] }],
  ["farmersrespite:yellow_tea_leaves", { output: ["6x farmersrespite:tea_seeds"] }],
  ["youkaishomecoming:red_grape", { output: [`6x youkaishomecoming:red_grape_seeds`] }],
  ["youkaishomecoming:white_grape", { output: [`6x youkaishomecoming:white_grape_seeds`] }],
  ["hearthandharvest:raspberry", { output: ["6x hearthandharvest:raspberry_pips"] }],
  ["kaleidoscope_tavern:green_grape", { output: ["6x vinery:white_grape_seeds"] }],
  ["kaleidoscope_tavern:gold_grape", { output: ["6x vinery:white_grape_seeds"] }],
  ["kaleidoscope_tavern:ice_grape", { output: ["6x vinery:white_grape_seeds"] }],
  ["culturaldelights:white_eggplant", { output: ["6x culturaldelights:eggplant_seeds"] }],
]);

StartupEvents.registry("block", (event) => {
  event
    .create("society:seed_maker", "cardinal")
    .property(booleanProperty.create("working"))
    .property(booleanProperty.create("mature"))
    .property(booleanProperty.create("upgraded"))
    .box(2, 0, 2, 14, 19, 14)
    .defaultCutout()
    .soundType("copper")
    .tagBlock("minecraft:mineable/pickaxe")
    .tagBlock("minecraft:mineable/axe")
    .tagBlock("minecraft:needs_stone_tool")
    .item((item) => {
      item.tooltip(Text.translatable("block.society.seed_maker.description").gray());
      item.tooltip(Text.translatable("society.working_block_entity.preserve_quality").green());
      item.modelJson({
        parent: "society:block/kubejs/seed_maker/seed_maker_off",
      });
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
        if (!upgraded && item == "society:ancient_cog") {
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
            type: block.properties.get("type"),
            working: block.properties.get("working"),
            mature: block.properties.get("mature"),
            upgraded: true,
          });
        }
      }

      if (upgraded && block.properties.get("mature") === "true" && rnd5()) {
        block.popItemFromFace("society:ancient_fruit_seed", facing);
      }

      global.handleBERightClick(
        "unusualfishmod:crab_scuttling",
        click,
        global.seedMakerRecipes,
        3,
        true
      );
    })
    .blockEntity((blockInfo) => {
      blockInfo.initialData({ stage: 0, recipe: "", quality: 0 });
      blockInfo.serverTick(artMachineTickRate, 0, (entity) => {
        global.handleBETick(entity, global.seedMakerRecipes, 1);
      });
    }).blockstateJson = {
    multipart: getCardinalMultipartJson("seed_maker"),
  };
});
