console.info("[SOCIETY] neptuniumHoe.js loaded");

BlockEvents.rightClicked(
  [
    "sunrisegardening:weak_fertilized_farmland",
    "sunrisegardening:strong_fertilized_farmland",
    "sunrisegardening:hyper_fertilized_farmland",
    "sunrisegardening:bountiful_fertilized_farmland",
    "sunrisegardening:low_quality_fertilized_farmland",
    "sunrisegardening:high_quality_fertilized_farmland",
    "sunrisegardening:pristine_quality_fertilized_farmland",
  ],
  (e) => {
    const { item, player, server, block } = e;
    if (item.id === "farm_and_charm:pitchfork") {
      const blockId = String(block.getId());
      if (0.5 < Math.random()) {
        block.popItemFromFace(
          blockId.substring(0, blockId.length - 10) + "r",
          "up"
        );
      }
      server.runCommandSilent(
        `playsound minecraft:item.armor.equip_leather block @a ${player.x} ${player.y} ${player.z}`
      );
      server.runCommandSilent(
        `playsound minecraft:item.hoe.till block @a ${player.x} ${player.y} ${player.z}`
      );
      player.swing();
      block.set("minecraft:dirt");
      e.cancel();
    }
  }
);
