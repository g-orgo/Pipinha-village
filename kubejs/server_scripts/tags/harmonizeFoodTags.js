// priority: -60
// Food families: every tag that means the same ingredient ends up with the same items, so a
// recipe that asks for "egg", "raw beef" or "milk" accepts every egg, bovine or milk of any mod,
// whichever of the 1.21 tag names (c:foods/x, c:x, farm_and_charm:x, leftover forge:x) it uses.
// - tags: synonyms; each one receives the union of all of them, plus items and include.
// - include: narrower tags pulled into the union (duck counts as chicken), left untouched.
// - into: tags that only receive the union (they keep meaning something narrower).
// - remove / removeTags: items and nested tags taken out of every synonym (dishes, insects,
//   non-food eggs).
// Only items are added, never tag references, so no tag cycle can form.
// Runs after tags/harmonizeMeatTags.js (-50), which fills the species, and before
// tags/canonicalItemTags.js (-100). Vanilla items named in dishes move to these tags in
// recipes/normalizeEquivalentItems.js.

const FOOD_DISHES_NOT_PLAIN_COOKED = [
  "candlelight:chicken_with_vegetables",
  "farm_and_charm:chicken_wrapped_in_bacon",
  "farm_and_charm:stuffed_chicken",
  "farm_and_charm:beef_patty_with_vegetables",
  "farm_and_charm:potato_with_roast_meat",
  "farm_and_charm:sausage_with_oat_patty",
  "farm_and_charm:bacon_with_eggs",
  "farm_and_charm:goulash",
  "farm_and_charm:lamb_with_corn",
];
const FOOD_NOT_MEAT = [
  "minersdelight:spider_leg",
  "minersdelight:arthropod",
  "minersdelight:crunchy_bar",
  "minecraft:rotten_flesh",
  "candlelight:beef_tartare",
];
const FOOD_COOKED_NOT_MEAT = [
  "minersdelight:baked_spider_leg",
  "minersdelight:cooked_arthropod",
  "minersdelight:crunchy_bar",
  "minersdelight:vegan_patty",
];
const FOOD_FRIED_EGGS = ["farmersdelight:fried_egg", "kaleidoscope_cookery:fried_egg", "cuisinedelight:fried_egg"];

const FOOD_FAMILIES = [
  {
    name: "eggs",
    tags: ["c:eggs", "c:foods/eggs", "forge:eggs", "bakery:eggs", "meadow:egg"],
    include: ["minecraft:eggs"],
    items: [
      "minecraft:egg", "autumnity:turkey_egg", "wildernature:turkey_egg", "untitledduckmod:duck_egg",
      "untitledduckmod:goose_egg", "society:cracked_egg", "society:large_egg", "society:large_duck_egg",
      "society:large_goose_egg", "society:large_turkey_egg", "society:large_galliraptor_egg",
      "society:penguin_egg", "society:flamingo_egg",
    ],
    remove: FOOD_FRIED_EGGS.concat([
      "quark:egg_parrot_blue", "quark:egg_parrot_gray", "quark:egg_parrot_green",
      "quark:egg_parrot_red_blue", "quark:egg_parrot_yellow_blue", "species:birt_egg",
    ]),
  },
  { name: "fried_eggs", tags: ["c:foods/cooked_egg", "c:foods/cooked_eggs", "forge:cooked_eggs", "sunlit:compat/fried_egg"], items: FOOD_FRIED_EGGS },
  {
    name: "raw_chicken",
    tags: ["c:foods/raw_chicken", "c:raw_chicken", "farm_and_charm:raw_chicken", "forge:foods/raw_chicken"],
    include: ["c:foods/raw_duck", "c:foods/raw_turkey"],
    items: ["wildernature:turkey_meat"],
  },
  {
    name: "cooked_chicken",
    tags: ["c:foods/cooked_chicken", "c:cooked_chicken", "farm_and_charm:cooked_chicken", "candlelight:cooked_chicken", "culturaldelights:cooked_chickens"],
    include: ["c:foods/cooked_duck", "c:foods/cooked_turkey"],
    items: ["farm_and_charm:cooked_chicken_parts", "wildernature:cooked_turkey_meat"],
    remove: FOOD_DISHES_NOT_PLAIN_COOKED,
  },
  {
    name: "raw_beef",
    tags: ["c:foods/raw_beef", "c:raw_beef", "farm_and_charm:raw_beef", "forge:foods/raw_beef", "candlelight:raw_beef"],
    include: ["youkaishomecoming:raw_venison"],
    remove: ["candlelight:beef_tartare"],
  },
  {
    name: "cooked_beef",
    tags: ["c:foods/cooked_beef", "c:cooked_beef", "farm_and_charm:cooked_beef", "culturaldelights:cooked_beefs"],
    include: ["youkaishomecoming:cooked_venison"],
    items: ["farm_and_charm:cooked_minced_beef"],
    remove: FOOD_DISHES_NOT_PLAIN_COOKED,
  },
  { name: "raw_pork", tags: ["c:foods/raw_pork", "c:raw_pork", "farm_and_charm:raw_pork"], items: ["youkaishomecoming:raw_boarchop_bits"] },
  {
    name: "cooked_pork",
    tags: ["c:foods/cooked_pork", "c:cooked_pork", "farm_and_charm:cooked_pork", "candlelight:cooked_pork"],
    items: ["farm_and_charm:cooked_bacon"],
    remove: FOOD_DISHES_NOT_PLAIN_COOKED,
  },
  { name: "raw_bacon", tags: ["c:foods/raw_bacon", "c:raw_bacon", "farm_and_charm:raw_bacon", "sunlit:compat/bacon"] },
  { name: "cooked_bacon", tags: ["c:foods/cooked_bacon"], items: ["farmersdelight:cooked_bacon", "farm_and_charm:cooked_bacon"] },
  { name: "raw_mutton", tags: ["c:foods/raw_mutton", "c:raw_mutton", "farm_and_charm:raw_mutton", "forge:foods/raw_mutton"] },
  {
    name: "cooked_mutton",
    tags: ["c:foods/cooked_mutton", "c:cooked_mutton", "farm_and_charm:cooked_mutton", "culturaldelights:cooked_muttons"],
    items: ["farm_and_charm:cooked_lamb_ham", "large_meals:cooked_mutton_rack"],
    remove: FOOD_DISHES_NOT_PLAIN_COOKED,
  },
  {
    name: "raw_meat",
    tags: ["c:foods/raw_meat", "c:raw_meat", "brewinandchewin:raw_meats"],
    remove: FOOD_NOT_MEAT,
    removeTags: ["minersdelight:raw_insect_meat"],
  },
  {
    name: "cooked_meat",
    tags: ["c:foods/cooked_meat", "c:cooked_meat"],
    remove: FOOD_DISHES_NOT_PLAIN_COOKED.concat(FOOD_COOKED_NOT_MEAT),
    removeTags: ["minersdelight:cooked_insect_meat"],
  },
  { name: "raw_cod", tags: ["c:foods/raw_cod", "forge:foods/raw_cod", "forge:foods/raw_fishes/cod", "forge:raw_fishes/cod"] },
  { name: "cooked_cod", tags: ["c:foods/cooked_cod", "forge:cooked_fishes/cod"], items: ["farm_and_charm:cooked_cod"] },
  { name: "raw_salmon", tags: ["c:foods/raw_salmon", "forge:foods/raw_salmon", "forge:foods/raw_fishes/salmon", "forge:raw_fishes/salmon"] },
  { name: "cooked_salmon", tags: ["c:foods/cooked_salmon"], items: ["farm_and_charm:cooked_salmon"] },
  {
    // Whole tunas only; the Youkai tag also holds slices, so it just receives the other tunas.
    name: "raw_tuna",
    tags: ["c:foods/raw_tuna", "forge:raw_fishes/tuna"],
    items: ["youkaishomecoming:raw_tuna", "aquaculture:tuna", "unusualfishmod:raw_blizzard_tuna"],
    into: ["youkaishomecoming:raw_tuna"],
  },
  {
    name: "raw_fish",
    tags: ["c:foods/raw_fish", "c:raw_fishes", "farm_and_charm:raw_fishes", "forge:foods/raw_fishes", "vintagedelight:raw_fish"],
    items: ["aquaculture:fish_fillet_raw", "unusualfishmod:unusual_fillet"],
  },
  { name: "cooked_fish", tags: ["c:foods/cooked_fish", "c:cooked_fishes", "farm_and_charm:cooked_fishes", "forge:cooked_fishes"] },
  // Society milk comes in two sizes: small (bottle) and large (bucket). Any milk counts as milk.
  { name: "small_milk", tags: ["society:small_milk"], items: ["farmersdelight:milk_bottle", "hearthandharvest:goat_milk_bottle", "minersdelight:milk_cup"] },
  {
    name: "large_milk",
    tags: ["society:large_milk"],
    items: [
      "minecraft:milk_bucket", "meadow:wooden_milk_bucket", "meadow:wooden_goat_milk_bucket",
      "meadow:wooden_sheep_milk_bucket", "meadow:wooden_buffalo_milk_bucket", "meadow:wooden_warped_milk_bucket",
      "meadow:wooden_grain_milk_bucket", "meadow:wooden_amethyst_milk_bucket", "windswept:wooden_milk_bucket",
    ],
  },
  {
    name: "milk",
    tags: ["c:drinks/milk", "c:foods/milk", "c:milk", "bakery:milk", "farm_and_charm:milk"],
    include: ["society:small_milk", "society:large_milk"],
  },
  {
    name: "cheese",
    tags: [
      "c:foods/cheese", "c:cheese", "c:cheeses", "forge:foods/cheese", "forge:cheeses", "meadow:cheese",
      "meadow:cheeses", "candlelight:cheeses", "culturaldelights:cheese_wedges",
      "brewinandchewin:foods/cheese_wedge", "hearthandharvest:cheese_slices",
    ],
  },
  { name: "butter", tags: ["c:butter", "forge:butter", "candlelight:butter", "farm_and_charm:butter", "youkaishomecoming:butter", "sunlit:compat/butter"] },
  // Tags that recipes still ask for but no mod fills in 1.21.1.
  { name: "bread", tags: ["c:foods/bread", "forge:bread"] },
  { name: "chili", tags: ["c:crops/chilipepper", "forge:chilipepper"] },
  { name: "soybean", tags: ["youkaishomecoming:soybean", "c:soybeans"] },
  { name: "strawberry", tags: ["c:crops/strawberry", "farm_and_charm:strawberries"] },
  { name: "wheat", tags: ["farm_and_charm:wheat", "meadow:wheat"] },
];

// Gives every synonym of one family the same items; returns how many items the family has.
const foodHarmonizeFamily = (e, family, missing) => {
  let remove = family.remove || [];
  let union = {};
  family.tags.forEach((tag) => remove.forEach((item) => e.remove(tag, item)));
  family.tags.forEach((tag) => (family.removeTags || []).forEach((inner) => e.remove(tag, "#" + inner)));
  family.tags.concat(family.include || []).forEach((tag) => {
    e.get(tag).getObjectIds().forEach((id) => {
      union[String(id)] = true;
    });
  });
  (family.items || []).forEach((item) => {
    if (Item.exists(item)) union[item] = true;
    else missing.push(item);
  });
  remove.forEach((item) => delete union[item]);
  let members = Object.keys(union).filter((item) => Item.exists(item));
  family.tags.concat(family.into || []).forEach((tag) => members.forEach((item) => e.add(tag, item)));
  return members.length;
};

ServerEvents.tags("item", (e) => {
  let missing = [];
  let report = [];
  FOOD_FAMILIES.forEach((family) => {
    try {
      report.push(`${family.name}=${foodHarmonizeFamily(e, family, missing)}`);
    } catch (err) {
      console.error(`[sunlit] harmonizeFoodTags: family ${family.name} failed: ${err}`);
    }
  });
  console.info(`[sunlit] harmonizeFoodTags: ${report.join(" ")}`);
  if (missing.length > 0) console.info(`[sunlit] harmonizeFoodTags: items not in this pack: ${missing.join(" ")}`);
});
