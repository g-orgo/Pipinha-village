// Potions (water bottles included, they are minecraft:potion + NBT) stack to 16.
// The LSO purified water bottle is a real item, so it can go to 64.
ItemEvents.modification((e) => {
  e.modify("minecraft:potion", (item) => {
    item.maxStackSize = 16;
  });
  e.modify("legendarysurvivaloverhaul:purified_water_bottle", (item) => {
    item.maxStackSize = 64;
  });
});
