// priority: -21
console.info("[SOCIETY] caterpillarBox.js loaded");

global.handleCaterpillarBox = (e) => {
  const { inventory, level, block } = e;
  const { x, y, z } = block;
  let slots = inventory.getSlots();
  let slotItem;
  if (!inventory.isEmpty()) {
    for (let i = 0; i < slots; i++) {
      slotItem = inventory.getStackInSlot(i);
      if (slotItem.id == "society:caterpillar_eggs") {
        let type = "butterfly";
        let longwingDef;
        let eggData = slotItem.customData;
        let child = eggData.getString("child");
        if (child) {
          global.longwings.forEach((wing) => {
            if (wing.variant === child) {
              longwingDef = wing
            }
          })
          type = longwingDef.type;
        }
        let longwing = level.createEntity("longwings:" + type);
        if (longwingDef) {
          longwing.mergeNbt({ Variant: longwingDef.variant, size: Math.round(Math.min(global.getLongwingSize(longwingDef.size) * 2, eggData.getFloat("size")) * 100) / 100});
        }
        longwing.setPosition(x, y + 1, z);
        longwing.spawn();
        slotItem.shrink(1);
        return;
      }
    }
  }
};

StartupEvents.registry("block", (event) => {
  event
    .create("society:caterpillar_box")
    .tagBlock("minecraft:mineable/axe")
    .soundType("wood")
    .defaultCutout()
    .item((item) => {
      item.tooltip(Text.translatable("block.society.caterpillar_box.description").gray());
      item.tooltip(Text.translatable("society.working_block_entity.can_use_hopper").green());
      item.parentModel("society:block/kubejs/caterpillar_box");
    })
    .parentModel("society:block/kubejs/caterpillar_box")
    .blockEntity((blockInfo) => {
      blockInfo.inventory(9, 1);
      blockInfo.serverTicking();
      blockInfo.tickFrequency(6000);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:caterpillar_box"] = (entity) => {
        global.handleCaterpillarBox(entity);
      };
        blockInfo.rightClickOpensInventory();
      blockInfo.attachCapability(
        CapabilityBuilder.ITEM.blockEntity()
          .insertItem((blockEntity, slot, stack, simulate) =>
            blockEntity.inventory.insertItem(slot, stack, simulate)
          )
          .getSlotLimit((blockEntity, slot) =>
            blockEntity.inventory.getSlotLimit(slot)
          )
          .getSlots((blockEntity) => blockEntity.inventory.slots)
          .getStackInSlot((blockEntity, slot) =>
            blockEntity.inventory.getStackInSlot(slot)
          )
      );
    });
});
