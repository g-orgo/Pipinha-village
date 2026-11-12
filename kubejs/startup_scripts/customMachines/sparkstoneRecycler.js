console.info("[SOCIETY] sparkstoneRecycler.js loaded");

const MANA_PER_RECYCLE = 5000;
const RECYCLER_MAX_MANA = MANA_PER_RECYCLE * 50;

global.checkSparkstoneRecyclers = (level, block) => {
  const { x, y, z } = block;
  const offsetsToCheck = [
    { x: 1, y: 0, z: 0 },
    { x: 0, y: 0, z: 1 },
    { x: -1, y: 0, z: 0 },
    { x: 0, y: 0, z: -1 },
    { x: 0, y: 1, z: 0 },
    { x: 0, y: -1, z: 0 },
  ];
  let recycled = false;
  let scannedBlock;
  let mana;
  offsetsToCheck.forEach((offset) => {
    if (!recycled) {
      scannedBlock = level.getBlock(
        new BlockPos(block.x + offset.x, block.y + offset.y, block.z + offset.z)
      );
      if ("society:sparkstone_recycler".equals(scannedBlock.id)) {
        mana = scannedBlock.getEntity().persistentData.getInt("mana");
        if (mana >= MANA_PER_RECYCLE && rnd10()) {
          scannedBlock.getEntity().persistentData.putInt("mana", mana - MANA_PER_AGE);
          recycled = true;
          level.server.runCommandSilent(`playsound minecraft:block.amethyst_block.chime block @a ${x} ${y} ${z}`);
          level.spawnParticles(
            "ribbits:spell",
            true,
            scannedBlock.x,
            scannedBlock.y + 0.5,
            scannedBlock.z,
            0.1 * rnd(1, 3),
            0.1 * rnd(1, 3),
            0.1 * rnd(1, 3),
            10,
            0.01
          );
        }
      }
    }
  });
  return recycled;
};

global.sparkstoneRecyclerTick = (entity) => {
  const { block } = entity;
  let mana = entity.persistentData.getInt("mana");
  let newProperties = entity.level.getBlock(block.getPos()).getProperties();
  if (mana >= MANA_PER_RECYCLE) newProperties.powered = true;
  else newProperties.powered = false;
  block.set(block.id, newProperties);
};

StartupEvents.registry("block", (event) => {
  event
    .create("society:sparkstone_recycler")
    .soundType("copper")
    .box(4, 0, 4, 12, 16, 12)
    .defaultCutout()
    .property(BlockProperties.FACING)
    .property(booleanProperty.create("powered"))
    .defaultState((state) => {
      state
        .set(BlockProperties.FACING, "up")
        .set(booleanProperty.create("powered"), false)
        .set(BlockProperties.WATERLOGGED, false);
    })
    .placementState((state) => {
      state
        .set(BlockProperties.FACING, state.clickedFace)
        .set(booleanProperty.create("powered"), false)
        .set(BlockProperties.WATERLOGGED, false);
    })
    .waterlogged()
    .tagBlock("minecraft:mineable/pickaxe")
    .tagBlock("minecraft:needs_stone_tool")
    .item((item) => {
      item.tooltip(Text.translatable("block.society.sparkstone_recycler.description").gray());
      item.tooltip(Text.translatable("society.working_block_entity.need_mana").aqua());
      item.tooltip(Text.translatable("block.society.sparkstone_recycler.description.compatible").green());
      item.parentModel("society:block/kubejs/sparkstone_recycler");
    })
    .parentModel("society:block/kubejs/sparkstone_recycler")
    .blockEntity((blockInfo) => {
      blockInfo.serverTicking();
      blockInfo.tickFrequency(200);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:sparkstone_recycler"] = (entity) => global.sparkstoneRecyclerTick(entity);
    });
});
