console.info("[SOCIETY] disableDispenser.js loaded");

const DispenserBlock = Java.loadClass(
  "net.minecraft.world.level.block.DispenserBlock"
);
// 1.21.1: Rhino does not turn a JS function into DispenseItemBehavior here; the vanilla NOOP keeps the item in the dispenser.
const $DispenseItemBehavior = Java.loadClass(
  "net.minecraft.core.dispenser.DispenseItemBehavior"
);
[
  "minecraft:bone_meal",
  "minecraft:carrot",
  "minecraft:potato",
  "farm_and_charm:onion",
  "veggiesdelight:sweet_potato",
].forEach((id) => {
  if (Item.exists(id)) DispenserBlock.registerBehavior(Item.of(id).item, $DispenseItemBehavior.NOOP);
});
