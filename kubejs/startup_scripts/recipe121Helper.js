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
    if (stack.components !== undefined) out.components = stack.components;
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

// Returns false when the converted recipe uses an item or fluid id that is not
// registered in the installed mods (for example a removed mod such as nethervinery).
// Recipe scripts call it before e.custom so a missing id skips that one recipe
// instead of producing a parse error on load. Tags (#...) are not checked.
global.recipeIdsExist121 = (() => {
  // Query the vanilla registries directly: the wrapper helpers (Fluid.exists) let
  // unregistered vinery juice fluids through in the 20:10 log.
  const BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  const ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  const inRegistry = (registry, id) => {
    const rl = ResourceLocation.tryParse(id);
    return rl !== null && registry.containsKey(rl);
  };
  const isSkippable = (id) => typeof id !== "string" || id.charAt(0) === "#";
  // A missing mod namespace always means the id is absent, whatever the registry lookup says.
  const fluidExists = (id) =>
    isSkippable(id) || (Platform.isLoaded(id.split(":")[0]) && inRegistry(BuiltInRegistries.FLUID, id));
  const idExists = (id) =>
    isSkippable(id) ||
    (Platform.isLoaded(id.split(":")[0]) &&
      (inRegistry(BuiltInRegistries.ITEM, id) || inRegistry(BuiltInRegistries.FLUID, id)));
  return (recipe) => walk(recipe);
  function walk(node) {
    if (Array.isArray(node)) return node.every(walk);
    if (node === null || typeof node !== "object") return true;
    for (let key in node) {
      let value = node[key];
      if (key === "fluid" && typeof value === "string" && !fluidExists(value)) return false;
      if ((key === "item" || key === "id") && typeof value === "string" && !idExists(value)) return false;
      if (!walk(value)) return false;
    }
    return true;
  }
})();
