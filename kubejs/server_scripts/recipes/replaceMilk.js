// priority: -100
// 1.20.1 swapped the vanilla milk fluid for the pack's society:milk in every recipe that took it.
// KubeJS 2101 replaceInput does not accept fluid filters, so the recipe JSON is rewritten here:
// every ingredient fluid "minecraft:milk" (key "fluid" or "id") becomes "society:milk".
// Output keys are skipped, so results are never changed. Recipes that use the c:milk tag are
// covered by kubejs/data/c/tags/fluid/milk.json instead.

const MILK_FROM = "minecraft:milk";
const MILK_TO = "society:milk";
const MILK_OUTPUT_KEYS = ["result", "results", "output", "outputs"];

// Rewrites the milk fluid ids of a parsed recipe JSON in place; returns true when something changed.
const milkRewriteInputs = (node) => {
  if (node === null || typeof node !== "object") return false;
  let changed = false;
  if (Array.isArray(node)) {
    node.forEach((child) => {
      if (milkRewriteInputs(child)) changed = true;
    });
    return changed;
  }
  ["fluid", "id"].forEach((key) => {
    if (node[key] === MILK_FROM) {
      node[key] = MILK_TO;
      changed = true;
    }
  });
  Object.keys(node).forEach((key) => {
    if (MILK_OUTPUT_KEYS.indexOf(key) >= 0) return;
    if (milkRewriteInputs(node[key])) changed = true;
  });
  return changed;
};

ServerEvents.recipes((event) => {
  let rewritten = 0;
  event.forEachRecipe({}, (recipe) => {
    if (recipe.json == null) return;
    const text = String(JsonIO.toString(recipe.json));
    if (text.indexOf('"' + MILK_FROM + '"') < 0) return;
    const parsed = JSON.parse(text);
    if (!milkRewriteInputs(parsed)) return;
    recipe.json = JsonIO.parseRaw(JSON.stringify(parsed));
    recipe.changed = true;
    rewritten++;
  });
  console.info(`[sunlit] replaceMilk: ${rewritten} JSON recipes rewritten`);
});
