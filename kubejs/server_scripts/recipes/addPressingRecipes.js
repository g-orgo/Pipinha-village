console.info("[SOCIETY] addPressingRecipes.js loaded");

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
  const createPressingRecipe = (input, output, compacting) => {
    custom({
      type: compacting ? "create:compacting" : "create:pressing",
      ingredients: [input],
      results: [
        {
          item: output,
        },
      ],
    });
  };
  const recipes = [
    {
      input: {
        item: "oreganized:lead_ingot",
      },
      output: "oreganized:lead_sheet",
    },
    {
      input: {
        item: "oreganized:silver_ingot",
      },
      output: "oreganized:silver_sheet",
    },
    {
      input: {
        amount: 250,
        fluid: "create_central_kitchen:sap",
      },
      output: "society:sap",
      compacting: true,
    },
  ];
  recipes.forEach((recipe) => {
    createPressingRecipe(recipe.input, recipe.output, recipe.compacting);
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "netherdepthsupgrade:lava_pufferfish",
      },
    ],
    results: [
      {
        item: "netherdepthsupgrade:lava_pufferfish",
      },
      {
        amount: 10,
        fluid: "minecraft:lava",
      },
    ],
  });
});
