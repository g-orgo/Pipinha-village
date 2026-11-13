// priority: 1000
// Shared 1.21.1 recipe converter. Recipe scripts call global.toRecipe121(recipe).
// Lives in startup scripts because server and client scripts cannot assign to global.
global.toRecipe121 = (() => {
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

  // Single or list "result" values. Kept in a function, not in a block, because
  // Rhino rejected the block-scoped const of the previous inline version.
  const convertResult121 = (type, result) => {
    const isList = Array.isArray(result);
    const stacks = isList ? result : [result];
    if (type === "farmersdelight:cutting") return stacks.map((stack) => ({ item: toStack121(stack) }));
    return isList ? stacks.map(toStack121) : toStack121(result);
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
    if (out.result !== undefined) out.result = convertResult121(out.type, out.result);
    if (out.tool !== undefined && !Array.isArray(out.tool)) out.tool = [out.tool];
    return out;
  };

  return toRecipe121;
})();
