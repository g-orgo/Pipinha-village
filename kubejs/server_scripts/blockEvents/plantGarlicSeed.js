console.info("[SOCIETY] neptuniumHoe.js loaded");

BlockEvents.rightClicked(
  [
    "minecraft:farmland",
    "sunrisegardening:tilled_soil",
    "sunrisegardening:weak_fertilized_farmland",
    "sunrisegardening:strong_fertilized_farmland",
    "sunrisegardening:hyper_fertilized_farmland",
    "sunrisegardening:bountiful_fertilized_farmland",
    "sunrisegardening:low_quality_fertilized_farmland",
    "sunrisegardening:high_quality_fertilized_farmland",
    "sunrisegardening:pristine_quality_fertilized_farmland",
  ],
  (e) => {
    const { item, player, level, server, block } = e;
    const aboveBlock = level.getBlock(block.getPos().above());
    if (aboveBlock.id === "minecraft:air") {
      if (item.id === "veggiesdelight:garlic_seed") {
        aboveBlock.set("veggiesdelight:garlic_crop");
        if (!player.isCreative()) item.shrink(1);
        player.swing();
        server.runCommandSilent(
          `playsound minecraft:block.crop.break block @a ${player.x} ${player.y} ${player.z}`
        );
      }
    }
  }
);
