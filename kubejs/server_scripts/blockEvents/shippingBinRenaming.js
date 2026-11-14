console.info("[SOCIETY] shippingBinNamed.js loaded");

const shippingBins = [
  "shippingbin:basic_shipping_bin",
  "shippingbin:smart_shipping_bin",
];

const getCustomNameJson = (item) => {
  if (!item || !item.customName) return null;
  return String(item.customName.string);
};

const getStoredCustomName = (nbt) => {
  if (!nbt || !nbt.data) return null;
  return global.nbtStr(nbt.data.customName) || global.nbtStr(nbt.data.custom_name) || null;
};


BlockEvents.placed(shippingBins, (e) => {
  const { player, block } = e;
  if (!player) return;
  let item = player.getHeldItem("main_hand");
  if (item.id !== block.id) item = player.getHeldItem("off_hand");
  if (item.id !== block.id) return;
  const customName = getCustomNameJson(item);
  if (!customName) return;
  let nbt = block.getEntityData();
  nbt.merge({ data: { customName: customName } });
  global.setBlockEntityData(block, nbt);
});

BlockEvents.broken(shippingBins, (e) => {
  const { block } = e;
  const nbt = block.getEntityData();
  const customName = getStoredCustomName(nbt);
  const drop = Item.of(block.id);
  if (customName) drop.setCustomName(String(customName));
  block.popItem(drop);
});
