console.info("[SOCIETY] manaClock.js loaded");

const MANA_PER_AGE = 10000;
const CLOCK_MAX_MANA = MANA_PER_AGE * 26;
global.registerManaReceiver("society:mana_clock", global.persistentManaSpec(CLOCK_MAX_MANA));

global.manaClockTick = (entity) => {
  const { block, level } = entity;
  const { x, y, z } = block;
  const radius = 1;
  let mana = entity.persistentData.getInt("mana");
  if (mana >= MANA_PER_AGE) {
    let scanBlock;
    for (let pos of BlockPos.betweenClosed(
      new BlockPos(x - radius, y - radius, z - radius),
      [x + radius, y + radius, z + radius]
    )) {
      if (!level.isLoaded(pos)) continue;
      scanBlock = level.getBlock(pos);
      if (scanBlock.hasTag("society:golden_clock_advanced")) {
        global.handleProgress(level, scanBlock);
        entity.persistentData.putInt("mana", mana - MANA_PER_AGE);
        level.server.runCommandSilent(
          `playsound botania:gaia_trap block @a ${x} ${y} ${z}`
        );
        break;
      }
    }
  }
};

StartupEvents.registry("block", (event) => {
  event
    .create("society:mana_clock", "cardinal")
    .soundType("copper")
    .box(1, 0, 1, 15, 16, 15)
    .defaultCutout()
    .tagBlock("minecraft:mineable/pickaxe")
    .tagBlock("minecraft:needs_stone_tool")
    .item((item) => {
      item.tooltip(
        Text.translatable("block.society.mana_clock.description").gray()
      );
      item.tooltip(
        Text.translatable("society.working_block_entity.need_mana").aqua()
      );
      item.tooltip(Text.translatable("tooltip.society.area", `3x3`).green());
      item.parentModel("society:block/kubejs/mana_clock");
    })
    .parentModel("society:block/kubejs/mana_clock")
    .blockEntity((blockInfo) => {
      blockInfo.serverTicking();
      blockInfo.tickFrequency(200);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:mana_clock"] = (entity) => global.manaClockTick(entity);
    });
});
