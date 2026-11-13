console.info("[SOCIETY] addBottleRecipes.js loaded");

ServerEvents.recipes((e) => {
  const custom = (recipe) => {
    const converted = global.toRecipe121(recipe);
    // Return the recipe (or a no-op stub when skipped) so callers can chain .id().
    return global.recipeIdsExist121(converted) ? e.custom(converted) : { id: () => {} };
  };
  const bottleRecipes = (item, fluid, amount, container) => {
    // Skip the pair when the fluid is not registered: an unknown fluid id is read as
    // an item by Create and breaks both recipes.
    if (!Fluid.exists(fluid)) return;
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
