// priority: -90
// Meat and fish recipes that follow real cooking (tags in tags/harmonizeMeatTags.js):
// - Cabbage rolls and bat rolls take a real stuffing: ground red meat (beef, pork, mutton
//   and their species), vegetables or mushrooms. They no longer take any meat or any fish.
// - Aquaculture tuna is cut into the same tuna slices as the Youkai tuna.

const SUNLIT_ROLL_RECIPES = ["farmersdelight:cooking/cabbage_rolls", "minersdelight:cooking/bat_rolls"];
const SUNLIT_ROLL_STUFFING = [
  { tag: "c:raw_beef" },
  { tag: "c:raw_pork" },
  { tag: "c:raw_mutton" },
  { tag: "c:vegetables" },
  { tag: "c:mushrooms" },
];

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

ServerEvents.recipes((event) => {
  const custom = (recipe) => event.custom(toRecipe121(recipe));
  SUNLIT_ROLL_RECIPES.forEach((id) => {
    event.forEachRecipe({ id: id }, (recipe) => {
      const parsed = JSON.parse(String(JsonIO.toString(recipe.json)));
      let changed = false;
      parsed.ingredients = parsed.ingredients.map((ingredient) => {
        if (ingredient.type !== "neoforge:compound") return ingredient;
        if (!ingredient.children.some((option) => option.tag === "c:foods/raw_meat")) return ingredient;
        changed = true;
        return { type: "neoforge:compound", children: SUNLIT_ROLL_STUFFING };
      });
      if (!changed) return;
      recipe.json = JsonIO.parseRaw(JSON.stringify(parsed));
      recipe.changed = true;
    });
  });

  event
    .custom({
      type: "farmersdelight:cutting",
      ingredients: [{ item: "aquaculture:tuna" }],
      result: [{ item: "youkaishomecoming:raw_tuna_slice", count: 3 }],
      tool: { tag: "c:tools/knife" },
    })
    .id("sunlit:cutting/aquaculture_tuna");
});
