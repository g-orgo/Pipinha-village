// priority: -100
// Items that must never be sellable in the shipping bin. Runs last (lowest priority), after every other startup script, so nothing re-adds them to global.trades.
// global.trades is a Map (globalRegistry.js), so delete() is used.
const UNSELLABLE_ITEMS = [
  "legendarysurvivaloverhaul:purified_water_bottle",
  "farmersdelight:milk_bottle",
  "hearthandharvest:goat_milk_bottle",
  "vintagedelight:nut_milk_bottle",
];
if (global.trades) {
  UNSELLABLE_ITEMS.forEach((id) => global.trades.delete(id));
}
