console.info("[SOCIETY] addGrapeJuiceRecipes.js loaded");

const netherGrapeJuices = ["crimson", "warped"];
const nethergrapes = ["crimson_grape", "warped_grape"];
const nether = ["crimson", "warped"];

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
  const juiceFromPress = (juice, grape) => {
    custom({
      type: "create:compacting",
      ingredients: [
        {
          item: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${grape}`,
        },
      ],
      results: [
        {
          amount: 50,
          fluid: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${juice}_grape_juice`,
        },
      ],
    });
  };
  const spoutBottling = (juice) => {
    custom({
      type: "create:filling",
      ingredients: [
        {
          item: "vinery:wine_bottle",
        },
        {
          amount: 250,
          fluidTag: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${juice}_grape_juice`,
        },
      ],
      results: [
        {
          item: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${juice}_grapejuice`,
        },
      ],
    });
    custom({
      type: "create:emptying",
      ingredients: [
        {
          item: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${juice}_grapejuice`,
        },
      ],
      results: [
        {
          item: "vinery:wine_bottle",
        },
        {
          amount: 250,
          fluid: `${
            nether.includes(juice) ? "nethervinery" : "vinery"
          }:${juice}_grape_juice`,
        },
      ],
    });
  };
  const spoutBasicBottling = (juice, color) => {
    custom({
      type: "create:filling",
      ingredients: [
        {
          item: "vinery:wine_bottle",
        },
        {
          amount: 250,
          fluidTag: `vinery:${juice}_grape_juice`,
        },
      ],
      results: [
        {
          item: `vinery:${color}_grapejuice`,
        },
      ],
    });
  };
  netherGrapeJuices.forEach((juice, index) => {
    juiceFromPress(juice, nethergrapes[index]);
    spoutBottling(juice, nethergrapes[index]);
  });

  custom({
    type: "create:emptying",
    ingredients: [
      {
        item: `vinery:white_grapejuice`,
      },
    ],
    results: [
      {
        item: "vinery:wine_bottle",
      },
      {
        amount: 250,
        fluid: `vinery:white_grape_juice`,
      },
    ],
  });

  custom({
    type: "create:emptying",
    ingredients: [
      {
        item: `vinery:red_grapejuice`,
      },
    ],
    results: [
      {
        item: "vinery:wine_bottle",
      },
      {
        amount: 250,
        fluid: `vinery:red_grape_juice`,
      },
    ],
  });
  ["red", "red_savanna", "red_jungle", "red_taiga"].forEach((juice, index) => {
    spoutBasicBottling(juice, "red");
  });
  ["white", "white_savanna", "white_jungle", "white_taiga"].forEach(
    (juice, index) => {
      spoutBasicBottling(juice, "white");
    }
  );
  custom({
    type: "create:compacting",
    ingredients: [
      [
        { item: "vinery:red_grape" },
        { item: "vinery:savanna_grapes_red" },
        { item: "vinery:jungle_grapes_red" },
        { item: "vinery:taiga_grapes_red" },
      ],
    ],
    results: [
      {
        amount: 50,
        fluid: `vinery:red_grape_juice`,
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      [
        { item: "vinery:white_grape" },
        { item: "vinery:savanna_grapes_white" },
        { item: "vinery:jungle_grapes_white" },
        { item: "vinery:taiga_grapes_white" },
      ],
    ],
    results: [
      {
        amount: 50,
        fluid: `vinery:white_grape_juice`,
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "minecraft:apple",
      },
    ],
    results: [
      {
        item: "vinery:apple_mash",
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "vinery:apple_mash",
      },
    ],
    results: [
      {
        amount: 250,
        fluid: "vinery:apple_juice",
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "society:ancient_fruit",
      },
    ],
    results: [
      {
        amount: 250,
        fluid: "society:ancient_fruit_juice",
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "pamhc2trees:starfruititem",
      },
    ],
    results: [
      {
        amount: 250,
        fluid: "society:starfruit_juice",
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "society:sparkpod",
      },
    ],
    results: [
      {
        amount: 250,
        fluid: "society:sparkpod_juice",
      },
    ],
  });
  custom({
    type: "create:compacting",
    ingredients: [
      {
        item: "society:mana_fruit",
      },
    ],
    results: [
      {
        amount: 250,
        fluid: "society:mana_fruit_juice",
      },
    ],
  });
});
