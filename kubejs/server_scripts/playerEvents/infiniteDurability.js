// Infinite durability for tools and armor, as described by the "No Durability?" quest.
// Using an item never wears it down: its damage is held at a stored floor ("SunlitWear").
// Dying (keepInventory is on) raises that floor by 15% + 15 for hotbar and armor items,
// reduced by Unbreaking. Anvil repairs lower the floor, so repairs stick.
// 1.21.1: the floor is stored in the minecraft:custom_data component, not item NBT.
const $WearComponents = Java.loadClass("net.minecraft.core.component.DataComponents");
const $WearCustomData = Java.loadClass("net.minecraft.world.item.component.CustomData");
const $WearCompoundTag = Java.loadClass("net.minecraft.nbt.CompoundTag");
const $WearEnchantments = Java.loadClass("net.minecraft.world.item.enchantment.Enchantments");
const $WearEnchantmentHelper = Java.loadClass("net.minecraft.world.item.enchantment.EnchantmentHelper");
const $WearRegistries = Java.loadClass("net.minecraft.core.registries.Registries");

const WEAR_TAG = "SunlitWear";
const WEAR_EXCLUDED = ["minecraft:elytra"];
// Hotbar 0-8, armor 36-39, offhand 40 in the player Inventory container.
const WEAR_USE_SLOTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 36, 37, 38, 39, 40];
const WEAR_DEATH_SLOTS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 36, 37, 38, 39];

const isWearTracked = (stack) =>
  !stack.isEmpty() && stack.isDamageableItem() && !WEAR_EXCLUDED.includes(String(stack.getId()));

// Returns the stored floor, or null when the item has no floor yet.
const readWearFloor = (stack) => {
  const custom = stack.get($WearComponents.CUSTOM_DATA);
  if (!custom) return null;
  const tag = custom.copyTag();
  return tag.contains(WEAR_TAG) ? tag.getInt(WEAR_TAG) : null;
};

const writeWearFloor = (stack, value) => {
  const custom = stack.get($WearComponents.CUSTOM_DATA);
  const tag = custom ? custom.copyTag() : new $WearCompoundTag();
  tag.putInt(WEAR_TAG, value);
  stack.set($WearComponents.CUSTOM_DATA, $WearCustomData.of(tag));
};

const unbreakingHolder = (level) =>
  level.registryAccess()
    .registryOrThrow($WearRegistries.ENCHANTMENT)
    .getHolderOrThrow($WearEnchantments.UNBREAKING);

const holdWearFloor = (stack) => {
  if (!isWearTracked(stack)) return;
  const damage = stack.getDamageValue();
  const floor = readWearFloor(stack);
  if (floor === null) {
    writeWearFloor(stack, damage);
    return;
  }
  if (damage > floor) stack.setDamageValue(floor);
  else if (damage < floor) writeWearFloor(stack, damage);
};

PlayerEvents.tick((e) => {
  const { player } = e;
  if (player.level.isClientSide()) return;
  const inventory = player.getInventory();
  // One-time repair of gear worn down before this script existed.
  if (!player.persistentData.getBoolean("sunlitWearMigrated")) {
    for (let i = 0; i < inventory.getContainerSize(); i++) {
      let stack = inventory.getItem(i);
      if (!isWearTracked(stack)) continue;
      stack.setDamageValue(0);
      writeWearFloor(stack, 0);
    }
    player.persistentData.putBoolean("sunlitWearMigrated", true);
  }
  WEAR_USE_SLOTS.forEach((slot) => holdWearFloor(inventory.getItem(slot)));
  // Items moved around the main inventory are checked once per second.
  if (player.age % 20 === 0) {
    for (let i = 9; i < 36; i++) holdWearFloor(inventory.getItem(i));
  }
});

EntityEvents.death((e) => {
  const { entity } = e;
  if (!entity.isPlayer() || entity.level.isClientSide()) return;
  const inventory = entity.getInventory();
  const unbreaking_holder = unbreakingHolder(entity.level);
  WEAR_DEATH_SLOTS.forEach((slot) => {
    let stack = inventory.getItem(slot);
    if (!isWearTracked(stack)) return;
    let max = stack.getMaxDamage();
    let unbreaking = $WearEnchantmentHelper.getItemEnchantmentLevel(unbreaking_holder, stack);
    let loss = Math.floor((max * 0.15 + 15) / (1 + unbreaking));
    let floor = Math.max(stack.getDamageValue(), readWearFloor(stack) || 0);
    // Never push an item to the edge: keep at least 5% (min 10) so a single use cannot break it.
    let minLeft = Math.min(max - 1, Math.max(10, Math.ceil(max * 0.05)));
    let next = Math.max(floor, Math.min(floor + loss, max - minLeft));
    stack.setDamageValue(next);
    writeWearFloor(stack, next);
  });
});
