// priority: -100
// Duplicate items across mods are normalized so any recipe that asked for one of them
// accepts any other from the same group (example: society:blueberry <-> hearthandharvest:blueberries).
//
// Each group also has the tag sunlit:compat/<group> (kubejs/data/sunlit/tags/items/compat/),
// and its members are added to the forge/c/farmersdelight tags those items already used.
// This script only handles recipes that hardcode one of the ids: the input is swapped for the tag.
// The first id of a group is the canonical one when the group is listed in global.canonicalItems
// (startup_scripts/globalCanonicalItems.js): Kaleidoscope first, then Farmer's Delight and the
// addons of both. Recipe outputs of a duplicate are swapped for the canonical item.
// Runs with the lowest priority so recipes registered by other scripts are covered too.

const SUNLIT_DUPLICATE_GROUPS = {
  "ancient_fruit": ["society:ancient_fruit", "quark:ancient_fruit"],
  "apple_cider": ["farmersdelight:apple_cider", "vinery:apple_cider"],
  "apple_jam": ["bakery:apple_jam", "hearthandharvest:apple_jam"],
  "apple_juice": ["legendarysurvivaloverhaul:apple_juice", "vinery:apple_juice"],
  "apple_pie": ["farmersdelight:apple_pie", "bakery:apple_pie"],
  "apple_pie_slice": ["farmersdelight:apple_pie_slice", "bakery:apple_pie_slice"],
  "bacon": ["farmersdelight:bacon", "farm_and_charm:bacon"],
  "black_tea": ["farmersrespite:black_tea", "youkaishomecoming:black_tea"],
  "black_tea_leaves": ["farmersrespite:black_tea_leaves", "youkaishomecoming:black_tea_leaves"],
  "bloody_mary": ["kaleidoscope_tavern:bloody_mary", "brewinandchewin:bloody_mary"],
  "blueberry": ["society:blueberry", "hearthandharvest:blueberries"],
  "borscht": ["kaleidoscope_cookery:borscht", "youkaishomecoming:borscht"],
  "bread": ["minecraft:bread", "bakery:bread"],
  "butter": ["farm_and_charm:butter", "youkaishomecoming:butter"],
  "candy_cane": ["snowyspirit:candy_cane", "windswept:candy_cane"],
  "carrot_cake": ["veggiesdelight:carrot_cake", "hearthandharvest:carrot_cake"],
  "carrot_cake_slice": ["veggiesdelight:carrot_cake_slice", "hearthandharvest:carrot_cake_slice"],
  "carrot_juice": ["legendarysurvivaloverhaul:carrot_juice", "veggiesdelight:carrot_juice"],
  "champagne": ["kaleidoscope_tavern:champagne", "youkaishomecoming:champagne"],
  "cheese_sandwich": ["meadow:cheese_sandwich", "refurbished_furniture:cheese_sandwich"],
  "cherry_wine": ["vinery:cherry_wine", "hearthandharvest:cherry_wine"],
  "chocolate_cake_slice": ["bakery:chocolate_cake_slice", "create_central_kitchen:chocolate_cake_slice"],
  "coffee": ["farmersrespite:coffee", "herbalbrews:coffee"],
  "coffee_beans": ["farmersrespite:coffee_beans", "youkaishomecoming:coffee_beans", "herbalbrews:coffee_beans"],
  "coffee_berries": ["farmersrespite:coffee_berries", "youkaishomecoming:coffee_berries"],
  "cooked_rice": ["kaleidoscope_cookery:cooked_rice", "farmersdelight:cooked_rice"],
  "cooking_oil": ["kaleidoscope_cookery:oil", "hearthandharvest:cooking_oil"],
  "corn": ["culturaldelights:corn_cob", "farm_and_charm:corn", "hauntedharvest:corn"],
  "corn_kernels": ["culturaldelights:corn_kernels", "farm_and_charm:kernels"],
  "crab": ["crabbersdelight:crab", "youkaishomecoming:crab"],
  "cucumber": ["vintagedelight:cucumber", "culturaldelights:cucumber", "youkaishomecoming:cucumber"],
  "cucumber_seeds": ["vintagedelight:cucumber_seeds", "culturaldelights:cucumber_seeds", "youkaishomecoming:cucumber_seeds"],
  "dog_food": ["farm_and_charm:dog_food", "farmersdelight:dog_food"],
  "dough": ["kaleidoscope_cookery:raw_dough", "farmersdelight:wheat_dough", "create:dough", "farm_and_charm:dough", "bakery:dough", "candlelight:dough", "refurbished_furniture:dough"],
  "dragon_fruit": ["atmospheric:dragon_fruit", "pamhc2trees:dragonfruititem"],
  "dumpling": ["kaleidoscope_cookery:dumpling", "farmersdelight:dumplings", "brewery:dumplings"],
  "eggplant": ["society:eggplant", "culturaldelights:eggplant"],
  "flour": ["kaleidoscope_cookery:flour", "farm_and_charm:flour", "create:wheat_flour", "refurbished_furniture:wheat_flour"],
  "fried_egg": ["kaleidoscope_cookery:fried_egg", "farmersdelight:fried_egg", "cuisinedelight:fried_egg"],
  "fried_rice": ["farmersdelight:fried_rice", "cuisinedelight:fried_rice"],
  "ginger": ["snowyspirit:ginger", "culturaldelights:ginger"],
  "gingerbread_cookie": ["snowyspirit:gingerbread_cookie", "windswept:gingerbread_cookie"],
  "glow_berry_jam": ["bakery:glowberry_jam", "hearthandharvest:glow_berry_jam", "refurbished_furniture:glow_berry_jam"],
  "glow_squid": ["miners_delight:glow_squid", "culturaldelights:glow_squid"],
  "grape_green": ["kaleidoscope_tavern:green_grape", "hearthandharvest:green_grapes"],
  "grape_juice_green": ["kaleidoscope_tavern:green_grape_juice", "hearthandharvest:green_grape_juice"],
  "grape_juice_red": ["kaleidoscope_tavern:grape_juice", "vinery:red_grapejuice", "youkaishomecoming:red_grape_juice", "hearthandharvest:red_grape_juice"],
  "grape_juice_white": ["vinery:white_grapejuice", "youkaishomecoming:white_grape_juice"],
  "grape_red": ["kaleidoscope_tavern:grape", "vinery:red_grape", "youkaishomecoming:red_grape", "hearthandharvest:red_grapes"],
  "grape_seeds_red": ["vinery:red_grape_seeds", "youkaishomecoming:red_grape_seeds"],
  "grape_seeds_white": ["vinery:white_grape_seeds", "youkaishomecoming:white_grape_seeds"],
  "grape_white": ["vinery:white_grape", "youkaishomecoming:white_grape"],
  "green_tea": ["farmersrespite:green_tea", "youkaishomecoming:green_tea"],
  "green_tea_leaves": ["farmersrespite:green_tea_leaves", "youkaishomecoming:green_tea_leaves"],
  "jerky": ["brewinandchewin:jerky", "hearthandharvest:jerky"],
  "kimchi": ["vintagedelight:kimchi", "brewinandchewin:kimchi"],
  "lavender": ["herbalbrews:lavender", "windswept:lavender"],
  "lettuce": ["kaleidoscope_cookery:lettuce", "farm_and_charm:lettuce"],
  "lettuce_seeds": ["kaleidoscope_cookery:lettuce_seed", "farm_and_charm:lettuce_seeds"],
  "mantou": ["kaleidoscope_cookery:mantou", "youkaishomecoming:mantou"],
  "mashed_potatoes": ["veggiesdelight:mashed_potatoes", "hearthandharvest:mashed_potatoes"],
  "mead": ["kaleidoscope_tavern:honey_wine", "brewinandchewin:mead", "hearthandharvest:mead", "vinery:mead", "youkaishomecoming:mead"],
  "melon_juice": ["kaleidoscope_tavern:watermelon_juice", "farmersdelight:melon_juice", "legendarysurvivaloverhaul:melon_juice"],
  "minced_beef": ["farmersdelight:minced_beef", "farm_and_charm:minced_beef"],
  "oat": ["farm_and_charm:oat", "vintagedelight:oat"],
  "oat_seeds": ["farm_and_charm:oat_seeds", "vintagedelight:oat_seeds"],
  "onion": ["farm_and_charm:onion", "farmersdelight:onion"],
  "onion_soup": ["farmersdelight:onion_soup", "farm_and_charm:onion_soup", "hearthandharvest:onion_soup"],
  "oolong_tea": ["kaleidoscope_cookery:oolong", "herbalbrews:oolong_tea", "youkaishomecoming:oolong_tea"],
  "passion_fruit": ["atmospheric:passion_fruit", "pamhc2trees:passionfruititem"],
  "peanut": ["vintagedelight:peanut", "hearthandharvest:peanut"],
  "pickle": ["vintagedelight:pickle", "culturaldelights:pickle"],
  "pickled_beetroot": ["vintagedelight:pickled_beetroot", "hearthandharvest:pickled_beetroots"],
  "pickled_onion": ["vintagedelight:pickled_onion", "hearthandharvest:pickled_onions"],
  "popcorn": ["culturaldelights:popcorn", "hauntedharvest:popcorn"],
  "potato_soup": ["farm_and_charm:potato_soup", "largemeals:potato_soup"],
  "pumpkin_pie_slice": ["farmersdelight:pumpkin_pie_slice", "create_central_kitchen:pumpkin_pie_slice"],
  "quiche": ["brewinandchewin:quiche", "bakery:quiche"],
  "raisins": ["hearthandharvest:raisins", "youkaishomecoming:raisin"],
  "raw_pasta": ["farm_and_charm:raw_pasta", "farmersdelight:raw_pasta"],
  "red_wine": ["vinery:red_wine", "youkaishomecoming:red_wine"],
  "rice": ["kaleidoscope_cookery:rice", "farmersdelight:rice"],
  "rice_panicle": ["kaleidoscope_cookery:rice_panicle", "farmersdelight:rice_panicle"],
  "roasted_chestnut": ["pamhc2trees:roastedchestnutitem", "windswept:roasted_chestnuts"],
  "roasted_peanut": ["vintagedelight:roasted_peanut", "hearthandharvest:roasted_peanuts"],
  "rotten_tomato": ["farmersdelight:rotten_tomato", "farm_and_charm:rotten_tomato"],
  "salt": ["vintagedelight:salt", "hearthandharvest:salt"],
  "seafood_miso_soup": ["kaleidoscope_cookery:seafood_miso_soup", "youkaishomecoming:seafood_miso_soup"],
  "squid": ["miners_delight:squid", "culturaldelights:squid"],
  "sweet_berry_cake_slice": ["bakery:sweetberry_cake_slice", "create_central_kitchen:sweet_berry_cake_slice"],
  "sweet_berry_jam": ["brewinandchewin:sweet_berry_jam", "bakery:sweetberry_jam", "hearthandharvest:sweet_berry_jam", "refurbished_furniture:sweet_berry_jam"],
  "sweet_berry_wine": ["kaleidoscope_tavern:sweet_berry_wine", "hearthandharvest:sweet_berry_wine"],
  "syrup": ["autumnity:syrup_bottle", "hearthandharvest:syrup_bottle"],
  "tea_leaves_fresh": ["kaleidoscope_cookery:fresh_tea_leaves", "youkaishomecoming:tea_leaves"],
  "tea_seeds": ["farmersrespite:tea_seeds", "youkaishomecoming:tea_seeds", "kaleidoscope_cookery:tea_seed"],
  "tentacles": ["miners_delight:tentacles", "oceansdelight:tentacles"],
  "toast": ["bakery:toast", "refurbished_furniture:toast"],
  "tomato": ["kaleidoscope_cookery:tomato", "farmersdelight:tomato", "farm_and_charm:tomato"],
  "tomato_sauce": ["farmersdelight:tomato_sauce", "create_central_kitchen:tomato_sauce"],
  "tomato_seeds": ["kaleidoscope_cookery:tomato_seed", "farmersdelight:tomato_seeds", "farm_and_charm:tomato_seeds"],
  "vodka": ["kaleidoscope_tavern:vodka", "brewinandchewin:vodka"],
  "yellow_tea": ["farmersrespite:yellow_tea", "youkaishomecoming:yellow_tea"],
  "yellow_tea_leaves": ["farmersrespite:yellow_tea_leaves", "youkaishomecoming:yellow_tea_leaves"]
};

ServerEvents.recipes((event) => {
  Object.keys(global.canonicalItems).forEach((dup) => {
    event.replaceOutput({}, dup, global.canonicalItems[dup]);
  });
  Object.keys(SUNLIT_DUPLICATE_GROUPS).forEach((group) => {
    const tag = "#sunlit:compat/" + group;
    SUNLIT_DUPLICATE_GROUPS[group].forEach((item) => {
      event.replaceInput({}, item, tag);
    });
  });
});
