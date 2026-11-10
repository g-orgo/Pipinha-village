// priority: -22
// Shipping bin prices for drinks and drink ingredients that the pack left unpriced.
// Runs after globalRegistry.js (-20), globalRegistryAddonFoods.js (-21) and globalRegistryExtraPrices.js (-21),
// so every id already priced elsewhere is skipped. Pushed into the same global lists the registry
// uses for trade values, which keeps the price tooltips in sync automatically.

// NOTE: no Item.exists() check here on purpose. Startup scripts run in KubeJSForge's
// constructor (mod construction), before the item registry is populated, so Item.exists()
// returns false for every modded item and silently drops the whole list.
// Every id below was checked against the mod jars (models/blockstates/textures) instead.

const addDrinkPrices = (list, attribute, entries) => {
  entries.forEach((entry) => {
    const item = entry.item;
    const value = entry.value;
    if (global.trades.has(item)) return;
    list.push({ item: item, value: value });
    global.trades.set(item, {
      value: global.getConfiguredValue(value, attribute),
      multiplier:
        attribute === "wood"
          ? "shippingbin:wood_sell_multiplier"
          : attribute === "meat"
          ? "shippingbin:meat_sell_multiplier"
          : attribute === "gem"
          ? "shippingbin:gem_sell_multiplier"
          : "shippingbin:crop_sell_multiplier",
    });
  });
};

// Juices and other cold drinks (crop attribute, same as the rest of global.cocktails).
addDrinkPrices(global.cocktails, "crop", [
  { item: "society:ancient_juice", value: 180 },
  { item: "society:starfruit_juice", value: 240 },
  { item: "society:sparkpod_juice", value: 160 },
  { item: "society:mana_fruit_juice", value: 320 },
  { item: "society:steamed_milk", value: 64 },
  { item: "veggiesdelight:dandelion_juice", value: 60 },
  { item: "nethervinery:crimson_grapejuice", value: 100 },
  { item: "nethervinery:warped_grapejuice", value: 100 },
  { item: "longwings:apple_butterfly_brew_bowl", value: 90 },
  { item: "longwings:berry_butterfly_brew_bowl", value: 90 },
  { item: "longwings:melon_butterfly_brew_bowl", value: 100 },
]);

// Teas and coffees (crop attribute, same as the rest of global.herbalBrews).
addDrinkPrices(global.herbalBrews, "crop", [
  { item: "youkaishomecoming:han_palace", value: 30 },
  { item: "youkaishomecoming:shirayuki", value: 30 },
]);

// Raw tea leaves, coffee/tea ingredients and flowers sold like the other crops.
addDrinkPrices(global.crops, "crop", [
  { item: "farmersrespite:coffee_beans", value: 20 },
  { item: "youkaishomecoming:black_tea_leaves", value: 20 },
  { item: "youkaishomecoming:dark_tea_leaves", value: 20 },
  { item: "youkaishomecoming:coffee_powder", value: 20 },
  { item: "herbalbrews:hibiscus", value: 16 },
  { item: "herbalbrews:lavender_blossom", value: 16 },
]);
