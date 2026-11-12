console.info("[SOCIETY] culinariaCooking.js loaded");

// Cooking XP and perks for the society:culinaria Puffish category.
// While a Farmer's Delight cooking pot menu is open, the pot's output slot
// (CookingPotMenu.INDEX_OUTPUT = 8) is snapshotted every tick. XP is granted
// only when that slot shrinks and the player (inventory plus cursor) gained
// the same item in that tick, so moving ingredients in and out gives nothing.
// Perk stages are granted by the culinaria definitions through
// "kubejs stages add @s <stage>".
const COOKING_XP = 4;
const COOKING_POT_OUTPUT_SLOT = 8;
const CULINARIA_EXTRA_CHANCE = 1 / 3;
const CULINARIA_DOUBLE_CHANCE = 1 / 50;

const culinariaPotSnapshots = {};

const countHeld = (player, menu, stack) => {
  let count = player.getInventory().countItem(stack.getItem());
  let carried = menu.getCarried();
  if (!carried.isEmpty() && String(carried.getId()) === String(stack.getId())) {
    count += carried.getCount();
  }
  return count;
};

PlayerEvents.tick((e) => {
  let { player } = e;
  if (player.level.isClientSide() || player.isFake()) return;

  let uuid = String(player.getUuid());
  let menu = player.containerMenu;
  if (!(menu instanceof Java.loadClass("vectorwing.farmersdelight.common.block.entity.container.CookingPotMenu"))) {
    delete culinariaPotSnapshots[uuid];
    return;
  }

  try {
    let output = menu.inventory.getStackInSlot(COOKING_POT_OUTPUT_SLOT);
    let last = culinariaPotSnapshots[uuid];
    let snapshot = {
      containerId: menu.containerId,
      itemId: output.isEmpty() ? "" : String(output.getId()),
      count: output.isEmpty() ? 0 : output.getCount(),
      held: output.isEmpty() ? 0 : countHeld(player, menu, output),
    };

    if (last && last.containerId === snapshot.containerId && last.itemId !== "") {
      let taken = last.count - (snapshot.itemId === last.itemId ? snapshot.count : 0);
      if (taken > 0) {
        let held = countHeld(player, menu, Item.of(last.itemId));
        if (held - last.held >= taken) {
          global.grantCulinariaXp(player, COOKING_XP * taken);
          if (player.stages.has("culinaria_extra") && Math.random() < CULINARIA_EXTRA_CHANCE) {
            player.give(Item.of(last.itemId, 1));
          }
          if (player.stages.has("culinaria_double") && Math.random() < CULINARIA_DOUBLE_CHANCE) {
            player.give(Item.of(last.itemId, taken));
          }
          // Cooking Specialty perk: one more dish from the pot.
          try {
            if (!player.isFake() && global.rollSpecialty(player, "culinaria", "dish_extra")) {
              player.give(Item.of(last.itemId, 1));
            }
          } catch (err) {
            console.error(`[specialty] dish perk failed: ${err}`);
          }
        }
      }
    }

    culinariaPotSnapshots[uuid] = snapshot;
  } catch (err) {
    console.error(`[culinaria] cooking hook failed: ${err}`);
  }
});
