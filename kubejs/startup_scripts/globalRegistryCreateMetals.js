// priority: -21
// Shipping bin prices for the metals Create processes: crushed ores, ingots, nuggets and blocks.
// Runs after globalRegistry.js (-20) and before globalPriceBalance.js (-30), so the balance pass
// sees these ids like any other entry. Same mechanism as the ore entries: global.getConfiguredValue
// with "gem" and the shippingbin:gem_sell_multiplier attribute, stored in global.trades so the bin
// and the price tooltips read the same value.
// Ids already priced elsewhere are kept as they are and reported in the log, never overwritten.

const CREATE_METAL_PRICES = [
  // copper
  { item: "create:crushed_raw_copper", value: 5 },
  { item: "minecraft:copper_ingot", value: 5 },
  { item: "create:copper_nugget", value: 1 },
  { item: "minecraft:copper_block", value: 45 },
  // iron
  { item: "create:crushed_raw_iron", value: 11 },
  { item: "minecraft:iron_ingot", value: 11 },
  { item: "minecraft:iron_nugget", value: 1 },
  { item: "minecraft:iron_block", value: 99 },
  // gold
  { item: "create:crushed_raw_gold", value: 22 },
  { item: "minecraft:gold_ingot", value: 22 },
  { item: "minecraft:gold_nugget", value: 2 },
  { item: "minecraft:gold_block", value: 198 },
  // zinc
  { item: "create:crushed_raw_zinc", value: 11 },
  { item: "create:zinc_ingot", value: 11 },
  { item: "create:zinc_nugget", value: 1 },
  { item: "create:zinc_block", value: 99 },
];

// Read by the bin (globalShippingBinHandlers.js) for the industrial_miner bonus and the SunlitArtificial penalty.
global.createMetalItems = CREATE_METAL_PRICES.map((entry) => entry.item);

CREATE_METAL_PRICES.forEach((entry) => {
  if (global.trades.has(entry.item)) {
    console.log(`[createMetals] ${entry.item} already has a shipping bin price, kept as is`);
    return;
  }
  global.trades.set(entry.item, {
    value: global.getConfiguredValue(entry.value, "gem"),
    multiplier: "shippingbin:gem_sell_multiplier",
  });
});
