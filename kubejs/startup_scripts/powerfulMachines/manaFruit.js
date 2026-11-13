console.info("[SOCIETY] manaFruit.js loaded");

const MANA_DRAIN = 2500;
const FRUIT_MAX_MANA = MANA_DRAIN * 4;
global.registerManaReceiver("society:mana_fruit_crop", global.persistentManaSpec(FRUIT_MAX_MANA));

global.handleManaFruit = (e) => {
  const { level, block } = e;
  const { x, y, z } = block;
  let dayTime = level.dayTime();
  let morningModulo = dayTime % 24000;
  let blockProperties = level.getBlock(block.pos).getProperties();
  let age = Number(blockProperties.get("age"));
  if (!global.surviveCheck(level, block.pos))
    level.destroyBlock(block.pos, true);
  if (age < 7 && morningModulo >= 20 && morningModulo < 40) {
    let mana = e.persistentData.getInt("mana");

    if (mana >= MANA_DRAIN) {
      blockProperties.age = String(
        age +
          CropGrowthUtils.getFertilizerIncrease(
            age,
            7,
            level.getBlockState(block.pos.below())
          )
      );
      block.set(block.id, blockProperties);
      e.persistentData.putInt("mana", mana - MANA_DRAIN);
      level.server.runCommandSilent(
        `playsound minecraft:block.enchantment_table.use block @a ${x} ${y} ${z}`
      );
      level.spawnParticles(
        "windswept:will_o_the_wisp",
        true,
        x,
        y + 0.25,
        z,
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        5,
        0.01
      );
    } else if (age > 0) {
      blockProperties.age = String(age - 1);
      block.set(block.id, blockProperties);
      level.server.runCommandSilent(
        `playsound minecraft:entity.evoker.cast_spell block @a ${x} ${y} ${z}`
      );
      level.spawnParticles(
        true,
        x,
        y + 0.25,
        z,
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        0.1 * rnd(1, 4),
        5,
        0.01
      );
    }
  }
};
StartupEvents.registry("block", (e) => {
  e
    .create("society:mana_fruit_crop")
    .defaultCutout()
    .hardness(0)
    .resistance(0)
    .displayName("Mana Fruit Seed")
    .mapColor("grass")
    .soundType("azalea_leaves")
    .box(1, 0, 1, 15, 4, 15)
    .property(integerProperty.create("age", 0, 7))
    .defaultState((state) => {
      state.set(integerProperty.create("age", 0, 7), 0);
    })
    .placementState((state) => {
      state.set(integerProperty.create("age", 0, 7), 0);
    })
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .blockEntity((blockInfo) => {
      blockInfo.serverTicking();
      blockInfo.tickFrequency(20);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:mana_fruit_crop"] = (entity) => global.handleManaFruit(entity);
    })
    .item((item) => {
      item.tooltip(
        Text.translatable("society.working_block_entity.need_mana").aqua()
      );
      item.modelGenerator((m) => {
        m.parent("minecraft:item/generated");
        m.texture("layer0", "society:item/mana_fruit_seed");
      });
    });
});
