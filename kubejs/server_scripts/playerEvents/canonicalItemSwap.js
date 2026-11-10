console.info("[SOCIETY] canonicalItemSwap.js loaded");

// A duplicate item that lands in the inventory becomes its canonical item
// (startup_scripts/globalCanonicalItems.js), keeping count and NBT (quality stars included).
// The event slot is a menu index, so the whole inventory is scanned by its own indexes.
PlayerEvents.inventoryChanged((e) => {
  if (!e.item || e.item.isEmpty() || !global.canonicalItems[`${e.item.id}`]) return;
  const inventory = e.player.getInventory();
  for (let i = 0; i < inventory.getContainerSize(); i++) {
    let stack = inventory.getItem(i);
    let canonical = global.canonicalItems[`${stack.id}`];
    if (!canonical) continue;
    inventory.setItem(i, Item.of(`${stack.count}x ${canonical}`, stack.nbt));
  }
});
