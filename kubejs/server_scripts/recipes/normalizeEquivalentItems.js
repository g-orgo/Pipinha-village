// priority: -100
// Equivalent items (not duplicates) are made interchangeable as recipe inputs, without touching outputs:
// - coal <-> charcoal, in every recipe;
// - block of coal <-> block of charcoal, in every recipe;
// - ice <-> ice cube, only in food and drink recipes (ice as an ingredient, not as a block);
// - meat and fish of the same species, only in dish recipes (see the species list below).
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
    tags: ["c:storage_blocks/coal", "c:storage_blocks/charcoal"],
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
    tags: ["c:ice_cubes"],
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

// Meat and fish species (tags filled in tags/harmonizeMeatTags.js): a dish that asks for the
// vanilla item accepts every meat of the same species (duck where chicken goes, bison where
// beef goes, halibut where cod goes). dishesOnly keeps one-input transforms item-specific:
// cooking, cutting and mincing a chicken still make chicken products.
[
  ["minecraft:chicken", "c:raw_chicken"],
  ["minecraft:cooked_chicken", "c:cooked_chicken"],
  ["minecraft:beef", "c:raw_beef"],
  ["minecraft:cooked_beef", "c:cooked_beef"],
  ["minecraft:porkchop", "c:raw_pork"],
  ["minecraft:cooked_porkchop", "c:cooked_pork"],
  ["minecraft:mutton", "c:raw_mutton"],
  ["minecraft:cooked_mutton", "c:cooked_mutton"],
  ["minecraft:cod", "c:foods/raw_cod"],
  ["minecraft:cooked_cod", "c:foods/cooked_cod"],
  ["minecraft:salmon", "c:foods/raw_salmon"],
  ["minecraft:cooked_salmon", "c:foods/cooked_salmon"],
  ["youkaishomecoming:raw_tuna", "forge:raw_fishes/tuna"],
  ["quark:crab_leg", "sunlit:compat/crab_leg"],
].forEach((pair) => SUNLIT_EQUIVALENT_GROUPS.push({ tag: pair[1], items: [pair[0]], tags: [], dishesOnly: true }));

const SUNLIT_EQUIVALENT_OUTPUT_KEYS = ["result", "results", "output", "outputs"];
// Keys that are not food inputs when counting the distinct inputs of a dish.
const SUNLIT_NOT_DISH_INPUT_KEYS = ["tool", "container"];

// Collects the distinct item/tag inputs of a parsed recipe JSON (outputs, tools and containers skipped).
const sunlitDistinctInputs = (node, acc) => {
  if (node === null || typeof node !== "object") return acc;
  if (Array.isArray(node)) {
    node.forEach((child) => sunlitDistinctInputs(child, acc));
    return acc;
  }
  if (typeof node.item === "string") acc[node.item] = true;
  if (typeof node.tag === "string") acc["#" + node.tag] = true;
  Object.keys(node).forEach((key) => {
    if (SUNLIT_EQUIVALENT_OUTPUT_KEYS.indexOf(key) >= 0 || SUNLIT_NOT_DISH_INPUT_KEYS.indexOf(key) >= 0) return;
    sunlitDistinctInputs(node[key], acc);
  });
  return acc;
};

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

// Mods whose recipes using meat or fish are crafts, not food (brews, decoration blocks).
const SUNLIT_NOT_DISH_NAMESPACES = ["botania", "cluttered"];

// True when the recipe names the item itself and has at least one other distinct input.
const sunlitIsDishWith = (recipe, item) => {
  if (recipe.json == null) return false;
  if (SUNLIT_NOT_DISH_NAMESPACES.indexOf(String(recipe.getId()).split(":")[0]) >= 0) return false;
  let found = sunlitDistinctInputs(JSON.parse(String(JsonIO.toString(recipe.json))), {});
  return found[item] === true && Object.keys(found).length >= 2;
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
      if (group.dishesOnly) {
        // Only dishes that name the item itself: replaceInput would also swap broad tags
        // that merely contain it (forge:raw_meat), and one-input transforms stay as they are.
        if (!sunlitIsDishWith(recipe, group.items[0])) return;
      }
      let replaced = false;
      group.items.forEach((item) => {
        // Unknown recipe types (UnknownKubeRecipe) have no replaceInput; skip them.
        try {
          if (recipe.replaceInput(item, "#" + group.tag)) replaced = true;
        } catch (err) {
          return;
        }
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
