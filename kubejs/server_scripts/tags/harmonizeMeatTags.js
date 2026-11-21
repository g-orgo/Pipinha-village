// priority: -50
// Meat and fish harmonization: every meat or fish from any mod joins the species tag it
// belongs to in real life, so it fits every recipe that already accepts that species.
// - Poultry (duck, goose, turkey, pelican, cassowary, galliraptor) counts as chicken.
// - Bovine and red game (buffalo, bison, tribull, venison) counts as beef.
// - Boar and frozen porkchop count as pork; goat and rack of lamb count as mutton.
// - White fish counts as cod, salmonids as salmon, every tuna as tuna.
// Finished dishes leave the plain cooked-meat tags (goulash is not "cooked mutton"), and
// non-meat oddities (spider leg, arthropod, rotten flesh, tartare) leave the generic meat tags.
// Recipes that hardcode the vanilla item are moved to these tags in
// recipes/normalizeEquivalentItems.js (dish recipes only).

const SUNLIT_MEAT_SPECIES = [
  {
    raw: ["c:foods/raw_chicken", "c:raw_chicken", "farm_and_charm:raw_chicken"],
    cooked: ["c:foods/cooked_chicken", "c:cooked_chicken", "farm_and_charm:cooked_chicken"],
    rawItems: [
      "untitledduckmod:raw_duck",
      "untitledduckmod:raw_goose",
      "autumnity:turkey",
      "autumnity:turkey_piece",
      "wildernature:pelican_meat",
      "wildernature:cassowary_meat",
      "wildernature:turkey_meat",
    ],
    cookedItems: [
      "untitledduckmod:cooked_duck",
      "untitledduckmod:cooked_goose",
      "autumnity:cooked_turkey",
      "autumnity:cooked_turkey_piece",
      "wildernature:cooked_pelican_meat",
      "wildernature:cooked_cassowary_meat",
      "wildernature:cooked_turkey_meat",
    ],
  },
  {
    raw: ["c:foods/raw_beef", "c:raw_beef", "farm_and_charm:raw_beef"],
    cooked: ["c:foods/cooked_beef", "c:cooked_beef", "farm_and_charm:cooked_beef"],
    rawItems: [
      "meadow:raw_buffalo_meat",
      "wildernature:bison_meat",
      "wildernature:venison",
      "youkaishomecoming:raw_venison",
    ],
    cookedItems: [
      "meadow:cooked_buffalo_meat",
      "wildernature:cooked_bison_meat",
      "wildernature:cooked_venison",
      "youkaishomecoming:grilled_venison",
    ],
  },
  {
    raw: ["c:foods/raw_pork", "c:raw_pork", "farm_and_charm:raw_pork"],
    cooked: ["c:foods/cooked_pork", "c:cooked_pork", "farm_and_charm:cooked_pork"],
    rawItems: ["youkaishomecoming:raw_boarchop", "snowpig:frozen_porkchop"],
    cookedItems: ["youkaishomecoming:grilled_boarchop"],
  },
  {
    raw: ["c:foods/raw_mutton", "c:raw_mutton", "farm_and_charm:raw_mutton"],
    cooked: ["c:foods/cooked_mutton", "c:cooked_mutton", "farm_and_charm:cooked_mutton"],
    rawItems: ["windswept:goat", "large_meals:raw_mutton_rack"],
    cookedItems: ["windswept:cooked_goat"],
  },
];

// Composite dishes that mods put in the plain cooked-meat tags.
const SUNLIT_DISHES_NOT_COOKED_MEAT = [
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
const SUNLIT_PLAIN_COOKED_TAGS = [
  "c:foods/cooked_chicken",
  "c:cooked_chicken",
  "c:foods/cooked_beef",
  "c:cooked_beef",
  "c:foods/cooked_pork",
  "c:cooked_pork",
  "c:foods/cooked_mutton",
  "c:cooked_mutton",
];

// Items that are not meat (or are a finished dish) but sat in the generic meat tags.
const SUNLIT_NOT_GENERIC_MEAT = [
  "minersdelight:spider_leg",
  "minersdelight:arthropod",
  "minersdelight:crunchy_bar",
  "minecraft:rotten_flesh",
  "candlelight:beef_tartare",
];

// 1.21 names (the 1.20.1 forge:raw_fishes/* tags are kept as synonyms in harmonizeFoodTags.js).
const SUNLIT_FISH_SPECIES = {
  "c:foods/raw_cod": [
    "aquaculture:atlantic_cod",
    "aquaculture:pollock",
    "aquaculture:atlantic_halibut",
    "aquaculture:pacific_halibut",
  ],
  "c:foods/raw_salmon": ["aquaculture:pink_salmon", "aquaculture:rainbow_trout", "aquaculture:brown_trout"],
  "c:foods/raw_tuna": ["youkaishomecoming:raw_tuna", "aquaculture:tuna", "unusualfishmod:raw_blizzard_tuna"],
};

ServerEvents.tags("item", (e) => {
  SUNLIT_MEAT_SPECIES.forEach((species) => {
    species.rawItems.forEach((item) => {
      species.raw.forEach((tag) => e.add(tag, item));
      e.add("c:foods/raw_meat", item);
      e.add("c:raw_meat", item);
      e.add("brewinandchewin:raw_meats", item);
    });
    species.cookedItems.forEach((item) => {
      species.cooked.forEach((tag) => e.add(tag, item));
      e.add("c:foods/cooked_meat", item);
      e.add("c:cooked_meat", item);
    });
  });
  e.add("forge:raw_venison", "wildernature:venison");
  e.add("forge:cooked_venison", "wildernature:cooked_venison");
  e.add("forge:raw_boar", "snowpig:frozen_porkchop");

  SUNLIT_DISHES_NOT_COOKED_MEAT.forEach((dish) => {
    SUNLIT_PLAIN_COOKED_TAGS.forEach((tag) => e.remove(tag, dish));
  });
  SUNLIT_NOT_GENERIC_MEAT.forEach((item) => {
    ["c:foods/raw_meat", "c:raw_meat", "brewinandchewin:raw_meats"].forEach((tag) => e.remove(tag, item));
  });
  // Miner's Delight puts its whole insect tag in c:foods/raw_meat; Candlelight puts the
  // tartare dish in its raw beef tag, which forge:raw_beef and c:raw_beef include.
  e.remove("c:foods/raw_meat", "#minersdelight:raw_insect_meat");
  e.remove("c:raw_meat", "#minersdelight:raw_insect_meat");
  ["c:foods/raw_beef", "c:raw_beef", "candlelight:raw_beef"].forEach((tag) => e.remove(tag, "candlelight:beef_tartare"));

  Object.keys(SUNLIT_FISH_SPECIES).forEach((tag) => {
    SUNLIT_FISH_SPECIES[tag].forEach((fish) => e.add(tag, fish));
  });
});
