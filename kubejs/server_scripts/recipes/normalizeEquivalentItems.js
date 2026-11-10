// priority: -100
// Equivalent items (not duplicates) are made interchangeable as recipe inputs, without touching outputs:
// - coal <-> charcoal, in every recipe;
// - block of coal <-> block of charcoal, in every recipe;
// - ice <-> ice cube, only in food and drink recipes (ice as an ingredient, not as a block).
// Each group has the tag sunlit:compat/<group> (kubejs/data/sunlit/tags/items/compat/).
// Recipes with a KubeJS schema (vanilla types) use replaceInput. Recipes without a schema
// (Create, Botania, Let's Do, Youkai...) ignore replaceInput in KubeJS 6, so their JSON is rewritten:
// every input {"item": member} or {"tag": member tag} becomes {"tag": group tag}; result keys are skipped.
// Storage block packing/unpacking and the per-item Create milling stay as they are, so 9 charcoal
// still makes a block of charcoal and each item keeps its own milling output.

const SUNLIT_EQUIVALENT_GROUPS = [
  {
    tag: "sunlit:compat/coal",
    items: ["minecraft:coal", "minecraft:charcoal"],
    tags: [],
    exclude: [
      "minecraft:coal_block",
      "minecraft:coal",
      "quark:building/crafting/compressed/charcoal_block",
      "quark:building/crafting/compressed/charcoal_block_uncompress",
      "create:milling/coal",
      "create:milling/charcoal",
    ],
  },
  {
    tag: "sunlit:compat/coal_block",
    items: ["minecraft:coal_block", "quark:charcoal_block"],
    tags: ["forge:storage_blocks/coal", "forge:storage_blocks/charcoal"],
    exclude: [
      "minecraft:coal",
      "minecraft:coal_block",
      "quark:building/crafting/compressed/charcoal_block",
      "quark:building/crafting/compressed/charcoal_block_uncompress",
    ],
  },
  {
    tag: "sunlit:compat/ice",
    items: ["minecraft:ice", "youkaishomecoming:ice_cube"],
    tags: ["forge:ice_cubes"],
    only: [
      "atmospheric:orange_sorbet",
      "atmospheric:passion_fruit_sorbet",
      "beachparty:palm_bar_mixing/cocoa_cocktail",
      "beachparty:palm_bar_mixing/coconut_cocktail",
      "beachparty:palm_bar_mixing/honey_cocktail",
      "beachparty:palm_bar_mixing/melon_cocktail",
      "beachparty:palm_bar_mixing/pumpkin_cocktail",
      "beachparty:palm_bar_mixing/sweetberries_cocktail",
      "farmersdelight:melon_popsicle",
      "kaleidoscope_tavern:barrel/mother_snow",
      "youkaishomecoming:affogato_craft",
      "youkaishomecoming:affogato_remix",
      "youkaishomecoming:big_popsicle",
      "youkaishomecoming:cold_tofu",
      "youkaishomecoming:milk_popsicle",
      "youkaishomecoming:mixing/bowl_of_cream",
      "youkaishomecoming:shaved_ice_over_rice",
    ],
  },
];

const SUNLIT_EQUIVALENT_OUTPUT_KEYS = ["result", "results", "output", "outputs"];

// Rewrites the inputs of a parsed recipe JSON in place; returns true when something changed.
const sunlitRewriteEquivalentInputs = (node, group) => {
  if (node === null || typeof node !== "object") return false;
  let changed = false;
  if (Array.isArray(node)) {
    node.forEach((child) => {
      if (sunlitRewriteEquivalentInputs(child, group)) changed = true;
    });
    return changed;
  }
  if (typeof node.item === "string" && group.items.indexOf(node.item) >= 0) {
    delete node.item;
    node.tag = group.tag;
    return true;
  }
  if (typeof node.tag === "string" && group.tags.indexOf(node.tag) >= 0) {
    node.tag = group.tag;
    return true;
  }
  Object.keys(node).forEach((key) => {
    if (SUNLIT_EQUIVALENT_OUTPUT_KEYS.indexOf(key) >= 0) return;
    if (sunlitRewriteEquivalentInputs(node[key], group)) changed = true;
  });
  return changed;
};

const sunlitEquivalentNeedles = (group) =>
  group.items.concat(group.tags).map((id) => '"' + id + '"');

ServerEvents.recipes((event) => {
  let rewritten = 0;
  event.forEachRecipe({}, (recipe) => {
    const id = String(recipe.getId());
    SUNLIT_EQUIVALENT_GROUPS.forEach((group) => {
      if (group.only && group.only.indexOf(id) < 0) return;
      if (group.exclude && group.exclude.indexOf(id) >= 0) return;
      let replaced = false;
      group.items.forEach((item) => {
        if (recipe.replaceInput(item, "#" + group.tag)) replaced = true;
      });
      if (replaced || recipe.json == null) return;
      const text = String(JsonIO.toString(recipe.json));
      if (!sunlitEquivalentNeedles(group).some((needle) => text.indexOf(needle) >= 0)) return;
      const parsed = JSON.parse(text);
      if (!sunlitRewriteEquivalentInputs(parsed, group)) return;
      recipe.json = JsonIO.parseRaw(JSON.stringify(parsed));
      recipe.changed = true;
      rewritten++;
    });
  });
  console.info(`[sunlit] normalizeEquivalentItems: ${rewritten} JSON recipes rewritten`);
});
