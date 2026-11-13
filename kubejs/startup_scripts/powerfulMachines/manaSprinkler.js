console.info("[SOCIETY] manaSprinkler.js loaded");

const MANA_PER_SPRINKLE = 50;
const SPRINKLER_MAX_MANA = MANA_PER_SPRINKLE * 25 * 8;
global.registerManaReceiver("society:mana_sprinkler", global.persistentManaSpec(SPRINKLER_MAX_MANA));

global.manaSprinklerScan = (entity, radius) => {
  const { block, level } = entity;
  const { x, y, z } = block;
  let scanBlock;
  let sprinklerMana = entity.persistentData.getInt("mana");
  let flowerBE
  let triggeredSpread = false;

  for (let pos of BlockPos.betweenClosed(
    new BlockPos(x - radius, y - radius, z - radius),
    [x + radius, y + radius, z + radius]
  )) {
    if (!level.isLoaded(pos)) continue;
    scanBlock = level.getBlock(pos);
    if (scanBlock.id == "society:mana_fruit_crop") {
      sprinklerMana = entity.persistentData.getInt("mana");
      flowerBE = scanBlock.entity
      if (sprinklerMana > MANA_PER_SPRINKLE && flowerBE.persistentData.getInt("mana") < FRUIT_MAX_MANA) {
        flowerBE.persistentData.putInt("mana", flowerBE.persistentData.getInt("mana") + MANA_PER_SPRINKLE);
        entity.persistentData.putInt("mana", entity.persistentData.getInt("mana") - MANA_PER_SPRINKLE);
        flowerBE.setChanged()
        entity.setChanged()
        triggeredSpread = true;
        level.spawnParticles(
          "windswept:will_o_the_wisp",
          true,
          scanBlock.x + 0.5,
          scanBlock.y + 1.25,
          scanBlock.z + 0.5,
          0, 0, 0,
          1,
          0.01
        );
      }
    }
  }
  if (triggeredSpread) {
    level.server.runCommandSilent(
      `playsound doapi:water_sprinkler block @a ${x} ${y} ${z} 0.5 1`
    );
    level.server.runCommandSilent(
      `playsound minecraft:entity.blaze.shoot block @a ${x} ${y} ${z} 0.5 1`
    );
  }
};

StartupEvents.registry("block", (event) => {
  event
    .create("society:mana_sprinkler")
    .tagBlock("minecraft:mineable/axe")
    .tagBlock("minecraft:needs_stone_tool")
    .tagBlock("dew_drop_farmland_growth:sprinkler_tier_2")
    .defaultCutout()
    .soundType("wood")
    .item((item) => {
      item.tooltip(
        Text.translatable("block.society.mana_sprinkler.description").aqua()
      );
      item.tooltip(Text.translatable(
        "tooltip.society.area",
        `5x5`
      ).green())
      item.tooltip(
        Text.translatable("block.society.mana_sprinkler.need_mana").aqua()
      );
      item.parentModel("society:block/kubejs/mana_sprinkler");
    })
    .parentModel("society:block/kubejs/mana_sprinkler")
    .blockEntity((blockInfo) => {
      blockInfo.serverTicking();
      blockInfo.tickFrequency(20);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:mana_sprinkler"] = (entity) => {
        global.manaSprinklerScan(entity, 2);
      };
    });
});
