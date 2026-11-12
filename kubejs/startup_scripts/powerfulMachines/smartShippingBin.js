// priority: 1
console.info("[SOCIETY] smartShippingBin.js loaded");

StartupEvents.registry("block", (event) => {
  event
    .create("shippingbin:smart_shipping_bin", "cardinal")
    .tagBlock("minecraft:mineable/axe")
    .item((item) => {
      item.tooltip(
        Text.translatable("tooltip.society.smart_shipping_bin").gray()
      );
      item.tooltip(
        Text.translatable("tooltip.society.smart_shipping_bin.warn").red()
      );
      itemitem.parentModel("society:block/kubejs/smart_shipping_bin");
    })
    .blockEntity((blockInfo) => {
      blockInfo.inventory(9, 6);
      blockInfo.initialData({ owner: "-1" });
      blockInfo.serverTicking();
      blockInfo.tickFrequency(4000);
      blockInfo.tickOffset(0);
      global.portBeTicks["shippingbin:smart_shipping_bin"] = (entity) => {
        const { inventory, block, level } = entity;
        if (global.susFunctionLogging) console.log("[SOCIETY-SUSFN] smartShippingBin.js");
        let slots = entity.inventory.getSlots();
        let value = 0;
        let binPlayer = global.cacheShippingBin(entity);
        let blockData = block.getEntityData().data;
        let playerAttributes = blockData.attributes;
        let playerStages = blockData.stages;
        let ownerUUID = blockData.owner;
        if (!playerStages || !playerAttributes) return;
        value = global.processShippingBinInventory(
          inventory,
          slots,
          playerAttributes,
          playerStages
        ).calculatedValue;

        global.processValueOutput(
          value,
          slots,
          undefined,
          binPlayer,
          level.getServer(),
          block,
          inventory,
          true,
          ownerUUID
        );
      };
        blockInfo.rightClickOpensInventory();
      blockInfo.attachCapability(
        CapabilityBuilder.ITEM.blockEntity()
          .insertItem((blockEntity, slot, stack, simulate) =>
            blockEntity.inventory.insertItem(slot, stack, simulate)
          )
          .getSlotLimit((blockEntity, slot) => blockEntity.inventory.getSlotLimit(slot))
          .getSlots((blockEntity) => blockEntity.inventory.slots)
          .getStackInSlot((blockEntity, slot) => blockEntity.inventory.getStackInSlot(slot))
      );
    });
});
