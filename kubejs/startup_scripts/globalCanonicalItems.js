// priority: -30
// Content is centered on Kaleidoscope (Cookery and Tavern) and Farmer's Delight with their addons.
// Each duplicate item below is swapped for its canonical item wherever the player can get it
// (inventory, recipe outputs, loot), so only the canonical one circulates.
// Groups and the recipe side live in server_scripts/recipes/normalizeDuplicateItems.js.
// Runs after every price registry (lowest is -24) and after the machine definitions (100).

global.canonicalItems = {
  "bakery:apple_pie": "farmersdelight:apple_pie",
  "bakery:apple_pie_slice": "farmersdelight:apple_pie_slice",
  "bakery:dough": "kaleidoscope_cookery:raw_dough",
  "bakery:sweetberry_jam": "brewinandchewin:sweet_berry_jam",
  "brewery:dumplings": "kaleidoscope_cookery:dumpling",
  "brewinandchewin:bloody_mary": "kaleidoscope_tavern:bloody_mary",
  "brewinandchewin:kimchi": "vintagedelight:kimchi",
  "brewinandchewin:mead": "kaleidoscope_tavern:honey_wine",
  "brewinandchewin:vodka": "kaleidoscope_tavern:vodka",
  "candlelight:dough": "kaleidoscope_cookery:raw_dough",
  "create:dough": "kaleidoscope_cookery:raw_dough",
  "create:wheat_flour": "kaleidoscope_cookery:flour",
  "create_central_kitchen:sweet_berry_cake_slice": "bakery:sweetberry_cake_slice",
  "cuisinedelight:fried_egg": "kaleidoscope_cookery:fried_egg",
  "cuisinedelight:fried_rice": "farmersdelight:fried_rice",
  "culturaldelights:cucumber": "vintagedelight:cucumber",
  "culturaldelights:cucumber_seeds": "vintagedelight:cucumber_seeds",
  "culturaldelights:eggplant": "society:eggplant",
  "culturaldelights:glow_squid": "minersdelight:glow_squid",
  "culturaldelights:pickle": "vintagedelight:pickle",
  "culturaldelights:squid": "minersdelight:squid",
  "farm_and_charm:bacon": "farmersdelight:bacon",
  "farm_and_charm:corn": "culturaldelights:corn_cob",
  "farm_and_charm:dough": "kaleidoscope_cookery:raw_dough",
  "farm_and_charm:flour": "kaleidoscope_cookery:flour",
  "farm_and_charm:kernels": "culturaldelights:corn_kernels",
  "farm_and_charm:lettuce": "kaleidoscope_cookery:lettuce",
  "farm_and_charm:lettuce_seeds": "kaleidoscope_cookery:lettuce_seed",
  "farm_and_charm:minced_beef": "farmersdelight:minced_beef",
  "farm_and_charm:onion_soup": "farmersdelight:onion_soup",
  "farm_and_charm:rotten_tomato": "farmersdelight:rotten_tomato",
  "farm_and_charm:tomato": "kaleidoscope_cookery:tomato",
  "farm_and_charm:tomato_seeds": "kaleidoscope_cookery:tomato_seed",
  "farmersdelight:cooked_rice": "kaleidoscope_cookery:cooked_rice",
  "farmersdelight:dog_food": "farm_and_charm:dog_food",
  "farmersdelight:dumplings": "kaleidoscope_cookery:dumpling",
  "farmersdelight:fried_egg": "kaleidoscope_cookery:fried_egg",
  "farmersdelight:melon_juice": "kaleidoscope_tavern:watermelon_juice",
  "farmersdelight:onion": "farm_and_charm:onion",
  "farmersdelight:raw_pasta": "farm_and_charm:raw_pasta",
  "farmersdelight:rice": "kaleidoscope_cookery:rice",
  "farmersdelight:rice_panicle": "kaleidoscope_cookery:rice_panicle",
  "farmersdelight:tomato": "kaleidoscope_cookery:tomato",
  "farmersdelight:tomato_seeds": "kaleidoscope_cookery:tomato_seed",
  "farmersdelight:wheat_dough": "kaleidoscope_cookery:raw_dough",
  "hauntedharvest:corn": "culturaldelights:corn_cob",
  "hauntedharvest:popcorn": "culturaldelights:popcorn",
  "hearthandharvest:carrot_cake": "veggiesdelight:carrot_cake",
  "hearthandharvest:carrot_cake_slice": "veggiesdelight:carrot_cake_slice",
  "hearthandharvest:cooking_oil": "kaleidoscope_cookery:oil",
  "hearthandharvest:green_grapes": "kaleidoscope_tavern:green_grape",
  "hearthandharvest:jerky": "brewinandchewin:jerky",
  "hearthandharvest:mashed_potatoes": "veggiesdelight:mashed_potatoes",
  "hearthandharvest:mead": "kaleidoscope_tavern:honey_wine",
  "hearthandharvest:onion_soup": "farmersdelight:onion_soup",
  "hearthandharvest:peanut": "vintagedelight:peanut",
  "hearthandharvest:pickled_beetroots": "vintagedelight:pickled_beetroot",
  "hearthandharvest:pickled_onions": "vintagedelight:pickled_onion",
  "hearthandharvest:red_grape_juice": "vinery:red_grapejuice",
  "hearthandharvest:red_grapes": "kaleidoscope_tavern:grape",
  "hearthandharvest:roasted_peanuts": "vintagedelight:roasted_peanut",
  "hearthandharvest:salt": "vintagedelight:salt",
  "hearthandharvest:sweet_berry_jam": "brewinandchewin:sweet_berry_jam",
  "hearthandharvest:sweet_berry_wine": "kaleidoscope_tavern:sweet_berry_wine",
  "herbalbrews:coffee": "farmersrespite:coffee",
  "herbalbrews:coffee_beans": "farmersrespite:coffee_beans",
  "herbalbrews:oolong_tea": "kaleidoscope_cookery:oolong",
  "oceansdelight:tentacles": "minersdelight:tentacles",
  "refurbished_furniture:dough": "kaleidoscope_cookery:raw_dough",
  "refurbished_furniture:sweet_berry_jam": "brewinandchewin:sweet_berry_jam",
  "refurbished_furniture:wheat_flour": "kaleidoscope_cookery:flour",
  "vinery:apple_cider": "farmersdelight:apple_cider",
  "vinery:mead": "kaleidoscope_tavern:honey_wine",
  "vinery:red_grape": "kaleidoscope_tavern:grape",
  "vintagedelight:oat": "farm_and_charm:oat",
  "vintagedelight:oat_seeds": "farm_and_charm:oat_seeds",
  "youkaishomecoming:black_tea": "farmersrespite:black_tea",
  "youkaishomecoming:black_tea_leaves": "farmersrespite:black_tea_leaves",
  "youkaishomecoming:borscht": "kaleidoscope_cookery:borscht",
  "youkaishomecoming:champagne": "kaleidoscope_tavern:champagne",
  "youkaishomecoming:coffee_beans": "farmersrespite:coffee_beans",
  "youkaishomecoming:coffee_berries": "farmersrespite:coffee_berries",
  "youkaishomecoming:crab": "crabbersdelight:crab",
  "youkaishomecoming:cucumber": "vintagedelight:cucumber",
  "youkaishomecoming:cucumber_seeds": "vintagedelight:cucumber_seeds",
  "youkaishomecoming:green_tea": "farmersrespite:green_tea",
  "youkaishomecoming:green_tea_leaves": "farmersrespite:green_tea_leaves",
  "youkaishomecoming:mantou": "kaleidoscope_cookery:mantou",
  "youkaishomecoming:mead": "kaleidoscope_tavern:honey_wine",
  "youkaishomecoming:oolong_tea": "kaleidoscope_cookery:oolong",
  "youkaishomecoming:red_grape": "kaleidoscope_tavern:grape",
  "youkaishomecoming:red_grape_juice": "vinery:red_grapejuice",
  "youkaishomecoming:seafood_miso_soup": "kaleidoscope_cookery:seafood_miso_soup",
  "youkaishomecoming:tea_leaves": "kaleidoscope_cookery:fresh_tea_leaves",
  "youkaishomecoming:yellow_tea": "farmersrespite:yellow_tea",
  "youkaishomecoming:yellow_tea_leaves": "farmersrespite:yellow_tea_leaves"
};

global.toCanonicalItem = (id) => global.canonicalItems[id] || id;

const canonicalizeOutput = (value) => {
  if (typeof value !== "string") return value;
  const match = value.match(/^(\d+x )?(#?[a-z0-9_.-]+:[a-z0-9_/.-]+)$/);
  if (!match || !global.canonicalItems[match[2]]) return value;
  return (match[1] || "") + global.canonicalItems[match[2]];
};

// Canonical items inherit the price of the duplicate when they have none of their own.
Object.keys(global.canonicalItems).forEach((dup) => {
  const canonical = global.canonicalItems[dup];
  if (global.trades.has(dup) && !global.trades.has(canonical)) {
    const trade = global.trades.get(dup);
    global.trades.set(canonical, { value: trade.value, multiplier: trade.multiplier });
  }
});

// Artisan machines accept the canonical item wherever they accepted the duplicate,
// and never hand out a duplicate.
[
  "agingCaskRecipes",
  "ancientCaskRecipes",
  "baitMakerRecipes",
  "cheesePressRecipes",
  "dehydratorRecipes",
  "deluxeWormFarmRecipes",
  "espressoMachineRecipes",
  "fishSmokerRecipes",
  "loomRecipes",
  "mayonnaiseMachineRecipes",
  "mushroomLogRecipes",
  "oilMakerRecipes",
  "picklingRecipes",
  "preservesJarRecipes",
  "recyclingMachineRecipes",
  "seedMakerRecipes",
  "tapperRecipes",
  "wineKegRecipes",
].forEach((name) => {
  const recipes = global[name];
  if (!recipes) return;
  recipes.forEach((recipe) => {
    if (!recipe || typeof recipe !== "object") return;
    Object.keys(recipe).forEach((key) => {
      const value = recipe[key];
      if (Array.isArray(value)) recipe[key] = value.map(canonicalizeOutput);
      else recipe[key] = canonicalizeOutput(value);
    });
  });
  Object.keys(global.canonicalItems).forEach((dup) => {
    const canonical = global.canonicalItems[dup];
    if (recipes.has(dup) && !recipes.has(canonical)) recipes.set(canonical, recipes.get(dup));
  });
});
