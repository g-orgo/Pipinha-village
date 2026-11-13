// Botania Seeds (1.20.1 addon, botania_seeds-1.1.1). It has no 1.21.1 port, so the 16 mystical
// flower crops and their seed items are recreated here with the original ids.
// Textures, models, blockstates and lang come from the 1.20.1 jar, copied to kubejs/assets/botania_seeds.
// Each crop grows into the mystical flower of its color (botania:<color>_mystical_flower).
// The seed item keeps the <color>_mystical_flower_seed id (KJS 7 would name it *_seeds).
const BOTANIA_SEED_COLORS = [
  "white",
  "orange",
  "magenta",
  "light_blue",
  "yellow",
  "lime",
  "pink",
  "gray",
  "light_gray",
  "cyan",
  "purple",
  "blue",
  "brown",
  "green",
  "red",
  "black",
];

StartupEvents.registry("block", (e) => {
  BOTANIA_SEED_COLORS.forEach((color) => {
    e.create("botania_seeds:" + color + "_mystical_flower_crop", "crop")
      .age(4, (builder) => {
        builder
          .shape(0, 0, 0, 0, 16, 3, 16)
          .shape(1, 0, 0, 0, 16, 6, 16)
          .shape(2, 0, 0, 0, 16, 9, 16)
          .shape(3, 0, 0, 0, 16, 12, 16)
          .shape(4, 0, 0, 0, 16, 16, 16);
      })
      .survive((state, level, pos) => global.surviveCheck(level, pos))
      .noSeeds()
      .crop("botania:" + color + "_mystical_flower", 1)
      .tagBlock("minecraft:mineable/hoe")
      .tagBlock("minecraft:crops")
      .randomTick((tick) => {})
      .noItem();
  });
});

StartupEvents.registry("item", (e) => {
  const $ItemNameBlockItem = Java.loadClass("net.minecraft.world.item.ItemNameBlockItem");
  const $ItemProperties = Java.loadClass("net.minecraft.world.item.Item$Properties");
  const $BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  BOTANIA_SEED_COLORS.forEach((color) => {
    const cropId = "botania_seeds:" + color + "_mystical_flower_crop";
    e.createCustom("botania_seeds:" + color + "_mystical_flower_seed", () => new $ItemNameBlockItem($BuiltInRegistries.BLOCK.get($ResourceLocation.parse(cropId)), new $ItemProperties()));
  });
});
