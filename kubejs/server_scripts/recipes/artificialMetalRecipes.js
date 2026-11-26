// Metal nugget/ingot/block crafting that keeps the "artificial" mark.
// Nuggets from the gravel crushing farm carry custom_data {SunlitArtificial:1b}; any crafted
// result that uses a marked input inherits the mark, so the sell penalty survives
// nugget <-> ingot <-> block conversions.
// The recipes are re-added with "_manual_only" ids, which Create skips in
// press/mixer automation, so the marked metal cannot be bypassed by machines.

// 1.21.1: the mark is a data component (custom_data), not NBT.
const ARTIFICIAL_DATA = "[minecraft:custom_data={SunlitArtificial:1b}]";
const ARTIFICIAL_RECIPE_PREFIX = "society:artificial/";

// All recipes in this file contain only one metal type, so any marked input must be
// the metal that is being converted.
const hasArtificialInput = (grid) => {
  let i;
  let stack;
  let data;
  for (i = 0; i < grid.size(); i++) {
    stack = grid.getItem(i);
    data = stack.customData;
    if (data && String(data).indexOf("SunlitArtificial") >= 0) return true;
  }
  return false;
};

// KubeJS 7 requires recipe-result changes through ServerEvents.modifyRecipeResult.
// The event begins with the normal result; event.exit() returns that result to the recipe.
const propagateArtificial = (event) => {
  let result;
  try {
    if (hasArtificialInput(event.grid)) {
      result = Item.of(event.item.id + ARTIFICIAL_DATA, event.item.count);
      if (!result.isEmpty()) event.item = result;
    }
  } catch (err) {
    console.error("[SOCIETY] artificial metal result propagation failed; preserving normal recipe result:", err);
  }
  event.exit();
};

const artificialRecipeIds = [
  "iron_ingot_from_nuggets_manual_only",
  "iron_nugget_manual_only",
  "iron_block_manual_only",
  "iron_ingot_from_block_manual_only",
  "gold_ingot_from_nuggets_manual_only",
  "gold_nugget_manual_only",
  "gold_block_manual_only",
  "gold_ingot_from_block_manual_only",
  "copper_ingot_from_nuggets_manual_only",
  "copper_nugget_manual_only",
  "copper_block_manual_only",
  "copper_ingot_from_block_manual_only",
  "zinc_ingot_from_nuggets_manual_only",
  "zinc_nugget_manual_only",
  "zinc_block_manual_only",
  "zinc_ingot_from_block_manual_only",
];

artificialRecipeIds.forEach((id) => {
  ServerEvents.modifyRecipeResult(ARTIFICIAL_RECIPE_PREFIX + id, propagateArtificial);
});

ServerEvents.recipes((e) => {
  const removedIds = [
    "minecraft:iron_ingot_from_nuggets",
    "minecraft:iron_nugget",
    "minecraft:iron_block",
    "minecraft:iron_ingot_from_iron_block",
    "minecraft:gold_ingot_from_nuggets",
    "minecraft:gold_nugget",
    "minecraft:gold_block",
    "minecraft:gold_ingot_from_gold_block",
    "create:crafting/materials/copper_ingot",
    "create:crafting/materials/copper_nugget",
    "minecraft:copper_block",
    "minecraft:copper_ingot",
    "create:crafting/materials/zinc_ingot_from_compacting",
    "create:crafting/materials/zinc_nugget_from_decompacting",
    "create:crafting/materials/zinc_block_from_compacting",
    "create:crafting/materials/zinc_ingot_from_decompacting",
  ];
  removedIds.forEach((id) => e.remove({ id: id }));

  const NINE = 9;
  // Iron
  e.shaped(Item.of("minecraft:iron_ingot", 1), ["###", "###", "###"], {
    "#": "minecraft:iron_nugget",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "iron_ingot_from_nuggets_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "iron_ingot_from_nuggets_manual_only");
  e.shapeless(Item.of("minecraft:iron_nugget", NINE), ["minecraft:iron_ingot"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "iron_nugget_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "iron_nugget_manual_only");
  e.shaped(Item.of("minecraft:iron_block", 1), ["###", "###", "###"], {
    "#": "minecraft:iron_ingot",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "iron_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "iron_block_manual_only");
  e.shapeless(Item.of("minecraft:iron_ingot", NINE), ["minecraft:iron_block"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "iron_ingot_from_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "iron_ingot_from_block_manual_only");

  // Gold
  e.shaped(Item.of("minecraft:gold_ingot", 1), ["###", "###", "###"], {
    "#": "minecraft:gold_nugget",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "gold_ingot_from_nuggets_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "gold_ingot_from_nuggets_manual_only");
  e.shapeless(Item.of("minecraft:gold_nugget", NINE), ["minecraft:gold_ingot"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "gold_nugget_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "gold_nugget_manual_only");
  e.shaped(Item.of("minecraft:gold_block", 1), ["###", "###", "###"], {
    "#": "minecraft:gold_ingot",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "gold_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "gold_block_manual_only");
  e.shapeless(Item.of("minecraft:gold_ingot", NINE), ["minecraft:gold_block"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "gold_ingot_from_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "gold_ingot_from_block_manual_only");

  // Copper
  e.shaped(Item.of("minecraft:copper_ingot", 1), ["CCC", "CCC", "CCC"], {
    C: "#c:nuggets/copper",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "copper_ingot_from_nuggets_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "copper_ingot_from_nuggets_manual_only");
  e.shapeless(Item.of("create:copper_nugget", NINE), ["#c:ingots/copper"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "copper_nugget_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "copper_nugget_manual_only");
  e.shaped(Item.of("minecraft:copper_block", 1), ["###", "###", "###"], {
    "#": "minecraft:copper_ingot",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "copper_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "copper_block_manual_only");
  e.shapeless(Item.of("minecraft:copper_ingot", NINE), ["minecraft:copper_block"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "copper_ingot_from_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "copper_ingot_from_block_manual_only");

  // Zinc
  e.shaped(Item.of("create:zinc_ingot", 1), ["###", "###", "###"], {
    "#": "#c:nuggets/zinc",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "zinc_ingot_from_nuggets_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "zinc_ingot_from_nuggets_manual_only");
  e.shapeless(Item.of("create:zinc_nugget", NINE), ["#c:ingots/zinc"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "zinc_nugget_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "zinc_nugget_manual_only");
  e.shaped(Item.of("create:zinc_block", 1), ["###", "###", "###"], {
    "#": "#c:ingots/zinc",
  })
    .id(ARTIFICIAL_RECIPE_PREFIX + "zinc_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "zinc_block_manual_only");
  e.shapeless(Item.of("create:zinc_ingot", NINE), ["#c:storage_blocks/zinc"])
    .id(ARTIFICIAL_RECIPE_PREFIX + "zinc_ingot_from_block_manual_only")
    .modifyResult(ARTIFICIAL_RECIPE_PREFIX + "zinc_ingot_from_block_manual_only");
});
