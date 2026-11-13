console.info("[SOCIETY] addRefurbishedWorkbenchRecipes.js loaded");

ServerEvents.recipes((e) => {
  Ingredient.of("@fantasyfurniture").stacks.forEach((item) => {
    if (item.toString().includes("furniture_station")) return;
    e.custom({
      type: "tanukidecor:diy",
      result: {
        id: item.id,
      },
    });
  });

  global.lootFurniture.forEach((item) => {
    // 1.21 ItemStack codec uses "id"; skip ids from mods that are not installed
    if (!Item.exists(item)) return;
    e.custom({
      type: "tanukidecor:diy",
      result: {
        id: item,
      },
    });
  });
});
