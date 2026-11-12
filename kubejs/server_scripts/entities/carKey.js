console.info("[SOCIETY] carKey.js loaded");

// KubeJS 7 (1.21.1): item NBT is gone. The stored car lives in the CUSTOM_DATA component,
// read with item.customData, written with item.setCustomData and cleared with item.remove.
BlockEvents.rightClicked((e) => {
  const { item, block, player } = e;
  if (item.getId() !== "society:car_key") return;
  const playerDrunk =
    player.potionEffects.isActive("brewery:drunk") ||
    player.potionEffects.isActive("brewery:blackout");

  const keyData = item.customData;
  if (!playerDrunk && !keyData.isEmpty() && block) {
    const DoubleTag = Java.loadClass("net.minecraft.nbt.DoubleTag");
    const DataComponents = Java.loadClass("net.minecraft.core.component.DataComponents");
    const keyTag = keyData.copy();
    let car = e.player.level.createEntity("automobility:automobile");
    if (keyTag.contains("car")) {
      const carTag = keyTag.getCompound("car");
      const pos = carTag.getList("Pos", 6);
      pos.set(0, DoubleTag.valueOf(Number(block.getX())));
      pos.set(1, DoubleTag.valueOf(Number(block.getY() + 2)));
      pos.set(2, DoubleTag.valueOf(Number(block.getZ())));
      car.setNbt(carTag);
    } else {
      const pos = keyTag.getList("Pos", 6);
      pos.set(0, DoubleTag.valueOf(Number(block.getX())));
      pos.set(1, DoubleTag.valueOf(Number(block.getY() + 2)));
      pos.set(2, DoubleTag.valueOf(Number(block.getZ())));
      car.setNbt(keyTag);
    }
    car.spawn();
    item.remove(DataComponents.CUSTOM_DATA);
  } else if (playerDrunk) {
    player.tell(
      Text.translatable("item.society.car_key.use_on_drunk").gray()
    );
  }
});

ItemEvents.entityInteracted("society:car_key", (e) => {
  const { item, target } = e;
  if (target.type !== "automobility:automobile" || item.customData.contains("car")) {
    return;
  }
  const keyTag = item.customData.copy();
  keyTag.put("car", target.getNbt());
  item.setCustomData(keyTag);
  target.setRemoved("unloaded_to_chunk");
  e.cancel();
});
