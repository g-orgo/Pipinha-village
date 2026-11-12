// Metal nugget/ingot/block crafting that keeps the "artificial" mark.
// Nuggets from the gravel crushing farm carry custom_data {SunlitArtificial:1b}; any crafted
// result that uses a marked input inherits the mark, so the sell penalty survives
// nugget <-> ingot <-> block conversions.
// The recipes are re-added with "_manual_only" ids, which Create skips in
// press/mixer automation, so the marked metal cannot be bypassed by machines.

// 1.21.1: the mark is a data component (custom_data), not NBT.
const ARTIFICIAL_DATA = "[minecraft:custom_data={SunlitArtificial:1b}]";

// True when any stack in the grid that matches one of the ingredient specs is marked.
const hasArtificialInput = (grid, specs) =>
  specs.some((spec) => {
    const found = grid.findAll(Ingredient.of(spec));
    for (let i = 0; i < found.size(); i++) {
      const stack = found.get(i);
      const data = stack.customData;
      if (data && String(data).indexOf("SunlitArtificial") >= 0) return true;
    }
    return false;
  });

// Keeps the result unchanged unless a marked input is present in the grid.
const propagateArtificial = (grid, result, specs) =>
  hasArtificialInput(grid, specs)
    ? Item.of(result.id + ARTIFICIAL_DATA, result.count)
    : result;

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
  const PREFIX = "society:artificial/";

  // Iron
  e.shaped(Item.of("minecraft:iron_ingot", 1), ["###", "###", "###"], {
    "#": "minecraft:iron_nugget",
  })
    .id(PREFIX + "iron_ingot_from_nuggets_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:iron_nugget"])
    );
  e.shapeless(Item.of("minecraft:iron_nugget", NINE), ["minecraft:iron_ingot"])
    .id(PREFIX + "iron_nugget_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:iron_ingot"])
    );
  e.shaped(Item.of("minecraft:iron_block", 1), ["###", "###", "###"], {
    "#": "minecraft:iron_ingot",
  })
    .id(PREFIX + "iron_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:iron_ingot"])
    );
  e.shapeless(Item.of("minecraft:iron_ingot", NINE), ["minecraft:iron_block"])
    .id(PREFIX + "iron_ingot_from_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:iron_block"])
    );

  // Gold
  e.shaped(Item.of("minecraft:gold_ingot", 1), ["###", "###", "###"], {
    "#": "minecraft:gold_nugget",
  })
    .id(PREFIX + "gold_ingot_from_nuggets_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:gold_nugget"])
    );
  e.shapeless(Item.of("minecraft:gold_nugget", NINE), ["minecraft:gold_ingot"])
    .id(PREFIX + "gold_nugget_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:gold_ingot"])
    );
  e.shaped(Item.of("minecraft:gold_block", 1), ["###", "###", "###"], {
    "#": "minecraft:gold_ingot",
  })
    .id(PREFIX + "gold_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:gold_ingot"])
    );
  e.shapeless(Item.of("minecraft:gold_ingot", NINE), ["minecraft:gold_block"])
    .id(PREFIX + "gold_ingot_from_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:gold_block"])
    );

  // Copper
  e.shaped(Item.of("minecraft:copper_ingot", 1), ["CCC", "CCC", "CCC"], {
    C: "#c:nuggets/copper",
  })
    .id(PREFIX + "copper_ingot_from_nuggets_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:nuggets/copper"])
    );
  e.shapeless(Item.of("create:copper_nugget", NINE), ["#c:ingots/copper"])
    .id(PREFIX + "copper_nugget_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:ingots/copper"])
    );
  e.shaped(Item.of("minecraft:copper_block", 1), ["###", "###", "###"], {
    "#": "minecraft:copper_ingot",
  })
    .id(PREFIX + "copper_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:copper_ingot"])
    );
  e.shapeless(Item.of("minecraft:copper_ingot", NINE), ["minecraft:copper_block"])
    .id(PREFIX + "copper_ingot_from_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["minecraft:copper_block"])
    );

  // Zinc
  e.shaped(Item.of("create:zinc_ingot", 1), ["###", "###", "###"], {
    "#": "#c:nuggets/zinc",
  })
    .id(PREFIX + "zinc_ingot_from_nuggets_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:nuggets/zinc"])
    );
  e.shapeless(Item.of("create:zinc_nugget", NINE), ["#c:ingots/zinc"])
    .id(PREFIX + "zinc_nugget_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:ingots/zinc"])
    );
  e.shaped(Item.of("create:zinc_block", 1), ["###", "###", "###"], {
    "#": "#c:ingots/zinc",
  })
    .id(PREFIX + "zinc_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:ingots/zinc"])
    );
  e.shapeless(Item.of("create:zinc_ingot", NINE), ["#c:storage_blocks/zinc"])
    .id(PREFIX + "zinc_ingot_from_block_manual_only")
    .modifyResult((grid, result) =>
      propagateArtificial(grid, result, ["#c:storage_blocks/zinc"])
    );
});
