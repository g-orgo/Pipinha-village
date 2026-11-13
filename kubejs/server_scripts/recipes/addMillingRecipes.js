console.info("[SOCIETY] addMillingRecipes.js loaded");

// Converts recipe objects written in the older shape to the 1.21.1 JSON shape:
// ingredient lists become neoforge types, results become {"id": ..., "count"/"amount": ...}.
const toIngredient121 = (ingredient) => {
  if (Array.isArray(ingredient)) {
    if (ingredient.length === 0) return ingredient;
    return { type: "neoforge:compound", children: ingredient.map(toIngredient121) };
  }
  if (ingredient.fluid !== undefined || ingredient.fluidTag !== undefined) {
    return {
      type: "neoforge:single",
      fluid: ingredient.fluid !== undefined ? ingredient.fluid : ingredient.fluidTag,
      amount: ingredient.amount,
    };
  }
  if (ingredient.tag !== undefined && ingredient.amount !== undefined) {
    return { type: "neoforge:tag", tag: ingredient.tag, amount: ingredient.amount };
  }
  return ingredient;
};

const toStack121 = (stack) => {
  if (stack.id !== undefined) return stack;
  if (stack.fluid !== undefined) return { id: stack.fluid, amount: stack.amount };
  const out = { id: stack.item };
  if (stack.count !== undefined) out.count = stack.count;
  if (stack.chance !== undefined) out.chance = stack.chance;
  return out;
};

const toRecipe121 = (recipe) => {
  const out = Object.assign({}, recipe);
  if (out.heatRequirement !== undefined) {
    out.heat_requirement = out.heatRequirement;
    delete out.heatRequirement;
  }
  if (out.ingredients !== undefined) out.ingredients = out.ingredients.map(toIngredient121);
  if (out.ingredient !== undefined) out.ingredient = toIngredient121(out.ingredient);
  if (out.input !== undefined) out.input = toIngredient121(out.input);
  if (out.results !== undefined) out.results = out.results.map(toStack121);
  if (out.result !== undefined) {
    const isList = Array.isArray(out.result);
    const stacks = isList ? out.result : [out.result];
    if (out.type === "farmersdelight:cutting") {
      out.result = stacks.map((stack) => ({ item: toStack121(stack) }));
    } else {
      out.result = isList ? stacks.map(toStack121) : toStack121(out.result);
    }
  }
  if (out.tool !== undefined && !Array.isArray(out.tool)) out.tool = [out.tool];
  return out;
};

ServerEvents.recipes((e) => {
  const custom = (recipe) => e.custom(toRecipe121(recipe));
  const addKnifeRecipe = (input, output, outputCount) => {
    custom({
      type: "farmersdelight:cutting",
      ingredients: [{ item: input }],
      tool: { tag: "c:tools/knife" },
      result: [{ item: output, count: outputCount }],
    });
  };
  const addMillRecipe = (input, output, outputCount) => {
    custom({
      type: "create:milling",
      ingredients: [
        {
          item: input,
        },
      ],
      processingTime: 400,
      results: [
        {
          count: outputCount,
          item: output,
        },
      ],
    });
    custom({
      type: "farm_and_charm:mincer",
      ingredient: {
        item: input,
      },
      recipe_type: "STONE",
      result: {
        count: outputCount,
        item: output,
      },
    });
  };
  custom({
    type: "farmersdelight:cutting",
    ingredients: [{ item: "minecraft:flint" }],
    tool: { tag: "minecraft:pickaxes" },
    result: [{ item: "twigs:pebble", count: 2 }],
  });
  addKnifeRecipe("farm_and_charm:barley", "society:animal_feed", 2);
  addKnifeRecipe("farm_and_charm:corn", "society:animal_feed", 4);
  addKnifeRecipe("farm_and_charm:oat", "society:animal_feed", 6);
  addKnifeRecipe("minecraft:wheat", "society:animal_feed", 8);
  addMillRecipe("farm_and_charm:barley_ball", "society:animal_feed_sack", 2);
  addMillRecipe("farm_and_charm:corn_bag", "society:animal_feed_sack", 4);
  addMillRecipe("farm_and_charm:oat_ball", "society:animal_feed_sack", 6);
  addMillRecipe("minecraft:hay_block", "society:animal_feed_sack", 8);
  addMillRecipe("society:animal_feed_sack", "society:animal_feed", 9);

  addMillRecipe('farm_and_charm:barley', 'farm_and_charm:flour', 1);
  addMillRecipe('farm_and_charm:corn', 'farm_and_charm:flour', 3);
  addMillRecipe('farm_and_charm:oat', 'farm_and_charm:flour', 6);
  addMillRecipe('minecraft:wheat', 'farm_and_charm:flour', 9);
  addMillRecipe('society:sparkstone', 'society:sparkstone_dust', 1);
  addMillRecipe('minecraft:flint', 'twigs:pebble', 2);
});
