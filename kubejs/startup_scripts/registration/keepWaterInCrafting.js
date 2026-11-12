// Water buckets used as a crafting ingredient are NOT consumed anymore.
//
// Recipes that need "flour + water" (kaleidoscope_cookery flour_from_N_wheat ->
// raw_dough in the crafting table, farm_and_charm dough in the crafting bowl)
// take a minecraft:water_bucket and hand back an empty bucket, so every dough
// needed a new bucket of water. Setting the item's crafting remainder to the
// item itself returns the bucket still full, in the crafting table and in the
// Farm & Charm crafting bowl (it drops getCraftingRemainingItem()).
//
// Only crafting is affected: buckets used on blocks (fill/place water) behave
// exactly like vanilla, so there is no free bucket / free water loop.
ItemEvents.modification((e) => {
  e.modify("minecraft:water_bucket", (item) => {
    item.setCraftingRemainder(item.item());
  });
  e.modify("meadow:wooden_water_bucket", (item) => {
    item.setCraftingRemainder(item.item());
  });
});
