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

ServerEvents.recipes((event) => {
  SUNLIT_ROLL_RECIPES.forEach((id) => {
    event.forEachRecipe({ id: id }, (recipe) => {
      const parsed = JSON.parse(String(JsonIO.toString(recipe.json)));
      let changed = false;
      parsed.ingredients = parsed.ingredients.map((ingredient) => {
        if (!Array.isArray(ingredient)) return ingredient;
        if (!ingredient.some((option) => option.tag === "c:raw_meat")) return ingredient;
        changed = true;
        return SUNLIT_ROLL_STUFFING;
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
