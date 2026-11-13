console.info("[SOCIETY] addBottleRecipes.js loaded");

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
  const bottleRecipes = (item, fluid, amount, container) => {
    custom({
      type: "create:filling",
      ingredients: [
        {
          item: container,
        },
        {
          amount: amount,
          fluid: fluid,
        },
      ],
      results: [
        {
          item: item,
        },
      ],
    });
    custom({
      type: "create:emptying",
      ingredients: [
        {
          item: item,
        },
      ],
      results: [
        {
          item: container,
        },
        {
          amount: amount,
          fluid: fluid,
        },
      ],
    });
  };

  const recipes = [
    {
      item: "vinery:apple_juice",
      fluid: "vinery:apple_juice",
      amount: 250,
      container: "vinery:wine_bottle",
    },
    {
      item: "society:ancient_juice",
      fluid: "society:ancient_fruit_juice",
      amount: 250,
      container: "vinery:wine_bottle",
    },
    {
      item: "society:starfruit_juice",
      fluid: "society:starfruit_juice",
      amount: 250,
      container: "vinery:wine_bottle",
    },
    {
      item: "society:mana_fruit_juice",
      fluid: "society:mana_fruit_juice",
      amount: 250,
      container: "vinery:wine_bottle",
    },
    {
      item: "society:sparkpod_juice",
      fluid: "society:sparkpod_juice",
      amount: 250,
      container: "vinery:wine_bottle",
    },
    {
      item: "relics:relic_experience_bottle",
      fluid: "relics:relic_experience",
      amount: 50,
      container: "minecraft:glass_bottle",
    },
    {
      item: "society:pine_tar",
      fluid: "society:pine_tar",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "society:oak_resin",
      fluid: "society:oak_resin",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "society:mystic_syrup",
      fluid: "society:mystic_syrup",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "society:maple_syrup",
      fluid: "society:maple_syrup",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "society:aloe_preserves",
      fluid: "create_central_kitchen:aloe_gel",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "vintagedelight:vinegar_bottle",
      fluid: "society:vinegar",
      amount: 250,
      container: "minecraft:glass_bottle",
    },
    {
      item: "vintagedelight:vinegar_mason_jar",
      fluid: "society:vinegar",
      amount: 750,
      container: "bakery:jar",
    },
  ];
  recipes.forEach((recipe) => {
    bottleRecipes(recipe.item, recipe.fluid, recipe.amount, recipe.container);
  });
  custom({
    type: "create:filling",
    ingredients: [
      {
        tag: "society:raw_logs",
      },
      {
        amount: 50,
        fluid: "society:oak_resin",
      },
    ],
    results: [
      {
        item: "society:treated_log",
      },
    ],
  });
  // Goat Milk Bottle do H&H e trocada pela do FD ao obter (playerEvents/
  // goatMilkSwap.js: a H&H nao e bebivel de estomago cheio). Recria com a
  // garrafa do FD as receitas que pediam a H&H, mantendo os ids originais
  // para os advancements continuarem destravando.
  e.remove({ id: "hearthandharvest:goat_milk_crate" });
  custom({
    type: "hearthandharvest:bottle_crate",
    input: {
      item: "farmersdelight:milk_bottle",
    },
    result: {
      count: 1,
      item: "hearthandharvest:goat_milk_crate",
    },
  }).id("hearthandharvest:goat_milk_crate");
  e.remove({ id: "hearthandharvest:cooking/unripe_goat_cheese_wheel" });
  custom({
    type: "farmersdelight:cooking",
    cookingtime: 400,
    experience: 2.0,
    ingredients: [
      {
        item: "farmersdelight:milk_bottle",
      },
      {
        item: "farmersdelight:milk_bottle",
      },
      {
        item: "hearthandharvest:salt",
      },
      {
        item: "hearthandharvest:salt",
      },
    ],
    recipe_book_tab: "meals",
    result: {
      item: "hearthandharvest:unripe_goat_cheese_wheel",
    },
  }).id("hearthandharvest:cooking/unripe_goat_cheese_wheel");
  e.remove({
    id: "hearthandharvest:integration/brewinandchewin/fermenting/unripe_goat_cheese_wheel",
  });
  custom({
    type: "brewinandchewin:fermenting",
    category: "meals",
    experience: 1.0,
    ingredients: [
      {
        item: "farmersdelight:milk_bottle",
      },
      {
        item: "farmersdelight:milk_bottle",
      },
      {
        item: "hearthandharvest:salt",
      },
      [],
    ],
    result: {
      count: 1,
      item: "hearthandharvest:unripe_goat_cheese_wheel",
    },
    temperature: 5,
  }).id(
    "hearthandharvest:integration/brewinandchewin/fermenting/unripe_goat_cheese_wheel"
  );
});
