console.info("[SOCIETY] disableHoeRichSoil.js loaded");

BlockEvents.rightClicked(
  [
    "farmersdelight:rich_soil",
    "vintagedelight:lush_grass_block",
  ],
  (e) => {
    const hoes = [
      "minecraft:wooden_hoe",
      "minecraft:stone_hoe",
      "minecraft:copper_hoe",
      "minecraft:iron_hoe",
      "mapperbase:steel_hoe",
      "minecraft:golden_hoe",
      "minecraft:diamond_hoe",
      "botania:manasteel_hoe",
      "minecraft:netherite_hoe",
      "aquaculture:neptunium_hoe",
      "botania:elementium_hoe",
      'farm_and_charm:pitchfork'
    ];
    if (hoes.includes(e.item.getId())) e.cancel()
  }
);
