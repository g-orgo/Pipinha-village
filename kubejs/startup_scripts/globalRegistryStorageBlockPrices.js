// priority: -24
// Shipping bin prices for crates, bags and storage blocks that the pack left unpriced.
// Runs after every other globalRegistry*.js file (-20 to -23), so the base items already have their final trade values.
// A storage block sells for exactly its contents: base trade value x item count, using the base's own multiplier.
// When a block accepts more than one base (tag or duplicate recipes), the cheapest base is used so crafting never profits.

// NOTE: no Item.exists() check here on purpose (see globalRegistryFoodPrices.js).
// Every id below was checked against the mod jars (models and crafting recipes) instead.

const storageBlock_lists = [
  global.crops,
  global.fruits,
  global.animalProducts,
  global.mushrooms,
  global.herbalBrews,
  global.artisanGoods,
  global.miscGeologist,
  global.miscAdventurer,
  global.cooking,
];

const storageBlock_findList = (item) => {
  let found = null;
  storageBlock_lists.forEach((list) => {
    list.forEach((entry) => {
      if (String(entry.item) === item) found = { list: list, value: entry.value };
    });
  });
  return found;
};

// Addon duplicates of pack crops had placeholder prices (1 to 5). They share recipes and crates with the
// original (see normalizeDuplicateItems.js), so they sell exactly like it: [duplicate, original].
[
  ["hearthandharvest:peanut", "vintagedelight:peanut"],
  ["culturaldelights:cucumber", "vintagedelight:cucumber"],
  ["youkaishomecoming:cucumber", "vintagedelight:cucumber"],
  ["culturaldelights:eggplant", "society:eggplant"],
  ["culturaldelights:pickle", "vintagedelight:pickle"],
  ["culturaldelights:corn_cob", "farm_and_charm:corn"],
  ["hauntedharvest:corn", "farm_and_charm:corn"],
  ["quark:ancient_fruit", "society:ancient_fruit"],
  ["minersdelight:cave_carrot", "minecraft:carrot"],
  ["youkaishomecoming:green_tea_leaves", "farmersrespite:green_tea_leaves"],
  ["youkaishomecoming:yellow_tea_leaves", "farmersrespite:yellow_tea_leaves"],
  ["youkaishomecoming:oolong_tea_leaves", "farmersrespite:green_tea_leaves"],
  ["youkaishomecoming:white_tea_leaves", "farmersrespite:green_tea_leaves"],
].forEach((pair) => {
  if (!global.trades.has(pair[1])) return;
  const original = global.trades.get(pair[1]);
  const source = storageBlock_findList(pair[1]);
  if (source !== null) source.list.push({ item: pair[0], value: source.value });
  global.trades.set(pair[0], { value: original.value, multiplier: original.multiplier });
});

// [storage block, [accepted base items], item count]
// hauntedharvest:corn_crate is repriced here too: it sold for 10 although it holds 9 corn.
[
  ["hauntedharvest:corn_crate", ["hauntedharvest:corn"], 9],
  ["atmospheric:carmine_block", ["atmospheric:carmine_husk"], 9],
  ["autumnity:foul_berry_basket", ["autumnity:foul_berries"], 9],
  ["autumnity:turkey_egg_crate", ["autumnity:turkey_egg"], 9],
  ["culturaldelights:avocado_crate", ["culturaldelights:avocado"], 9],
  ["culturaldelights:corn_cob_crate", ["culturaldelights:corn_cob", "farm_and_charm:corn", "hauntedharvest:corn"], 9],
  ["culturaldelights:cucumber_crate", ["culturaldelights:cucumber"], 9],
  ["culturaldelights:eggplant_crate", ["culturaldelights:eggplant"], 9],
  ["culturaldelights:pickle_crate", ["culturaldelights:pickle", "vintagedelight:pickle"], 9],
  ["culturaldelights:white_eggplant_crate", ["culturaldelights:white_eggplant"], 9],
  ["hearthandharvest:apple_crate", ["minecraft:apple"], 9],
  ["hearthandharvest:brown_mushroom_crate", ["minecraft:brown_mushroom"], 9],
  ["hearthandharvest:cherry_crate", ["hearthandharvest:cherry"], 9],
  ["hearthandharvest:cocoa_bean_bag", ["minecraft:cocoa_beans"], 9],
  ["hearthandharvest:crimson_fungus_crate", ["minecraft:crimson_fungus"], 9],
  ["hearthandharvest:egg_crate", ["minecraft:egg"], 9],
  ["hearthandharvest:golden_apple_crate", ["minecraft:golden_apple"], 9],
  ["hearthandharvest:golden_carrot_crate", ["minecraft:golden_carrot"], 9],
  ["hearthandharvest:peanut_crate", ["hearthandharvest:peanut"], 9],
  ["hearthandharvest:poisonous_potato_crate", ["minecraft:poisonous_potato"], 9],
  ["hearthandharvest:red_mushroom_crate", ["minecraft:red_mushroom"], 9],
  ["hearthandharvest:salt_bag", ["hearthandharvest:salt"], 9],
  ["hearthandharvest:turtle_egg_crate", ["minecraft:turtle_egg"], 9],
  ["hearthandharvest:warped_fungus_crate", ["minecraft:warped_fungus"], 9],
  ["herbalbrews:dried_green_tea_leaf_block", ["herbalbrews:dried_green_tea"], 9],
  ["herbalbrews:tea_leaf_crate", ["herbalbrews:green_tea_leaf"], 6],
  ["minersdelight:cave_carrot_crate", ["minersdelight:cave_carrot"], 9],
  ["quark:apple_crate", ["minecraft:apple"], 9],
  ["quark:beetroot_crate", ["minecraft:beetroot"], 9],
  ["quark:carrot_crate", ["minecraft:carrot"], 9],
  ["quark:golden_apple_crate", ["minecraft:golden_apple"], 9],
  ["quark:potato_crate", ["minecraft:potato"], 9],
  ["quarkdelight:ancient_fruit_crate", ["quark:ancient_fruit"], 9],
  ["supplementaries:feather_block", ["minecraft:feather"], 9],
  ["vinery:red_jungle_grape_bag", ["vinery:jungle_grapes_red"], 9],
  ["vinery:red_savanna_grape_bag", ["vinery:savanna_grapes_red"], 9],
  ["vinery:red_taiga_grape_bag", ["vinery:taiga_grapes_red"], 9],
  ["vinery:white_jungle_grape_bag", ["vinery:jungle_grapes_white"], 9],
  ["vinery:white_savanna_grape_bag", ["vinery:savanna_grapes_white"], 9],
  ["vinery:white_taiga_grape_bag", ["vinery:taiga_grapes_white"], 9],
  ["youkaishomecoming:black_grape_crate", ["youkaishomecoming:black_grape"], 9],
  ["youkaishomecoming:black_tea_bag", ["youkaishomecoming:black_tea_leaves"], 9],
  ["youkaishomecoming:coffee_bean_bag", ["youkaishomecoming:coffee_beans"], 9],
  ["youkaishomecoming:cucumber_crate", ["youkaishomecoming:cucumber"], 9],
  ["youkaishomecoming:dark_tea_bag", ["youkaishomecoming:dark_tea_leaves"], 9],
  ["youkaishomecoming:green_tea_bag", ["youkaishomecoming:green_tea_leaves"], 9],
  ["youkaishomecoming:oolong_tea_bag", ["youkaishomecoming:oolong_tea_leaves"], 9],
  ["youkaishomecoming:pod_crate", ["youkaishomecoming:pods"], 9],
  ["youkaishomecoming:red_grape_crate", ["youkaishomecoming:red_grape"], 9],
  ["youkaishomecoming:redbean_bag", ["youkaishomecoming:redbean"], 9],
  ["youkaishomecoming:soybean_bag", ["youkaishomecoming:soybean"], 9],
  ["youkaishomecoming:tea_leaf_bag", ["youkaishomecoming:tea_leaves"], 9],
  ["youkaishomecoming:white_grape_crate", ["youkaishomecoming:white_grape"], 9],
  ["youkaishomecoming:white_tea_bag", ["youkaishomecoming:white_tea_leaves"], 9],
  ["youkaishomecoming:yellow_tea_bag", ["youkaishomecoming:yellow_tea_leaves"], 9],
].forEach((entry) => {
  const block = entry[0];
  const count = entry[2];
  let cheapest = null;
  entry[1].forEach((base) => {
    if (!global.trades.has(base)) return;
    const trade = global.trades.get(base);
    if (cheapest === null || trade.value < cheapest.trade.value) cheapest = { item: base, trade: trade };
  });
  if (cheapest === null) return;
  const source = storageBlock_findList(cheapest.item);
  if (source !== null) source.list.push({ item: block, value: source.value * count });
  global.trades.set(block, { value: cheapest.trade.value * count, multiplier: cheapest.trade.multiplier });
});
