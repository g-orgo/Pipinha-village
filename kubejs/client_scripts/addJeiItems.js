RecipeViewerEvents.addEntries('item', (e) => {
  // Unregistered ids would fail the whole add call, so they are filtered out first.
  [
    "displaydelight:food_plate",
    "displaydelight:small_food_plate",
    "minecraft:bundle",
    "snowyspirit:ginger_crate",
  ]
    .filter((id) => Item.exists(id))
    .forEach((id) => e.add(id));
  const trophyNames = [
    "pantry",
    "vault",
    "boiler_room",
    "crafts_room",
    "fish_tank",
    "artifacts",
    "minerals",
    "crops",
    "fish",
    "brews",
    "gems",
    "relics",
    "cooking",
    "wheels",
    "perfection",
  ];
  trophyNames.forEach((name) => {
    e.add(Item.of(`trofers:large_pillar[trofers:trophy="trofers:${name}"]`));
  });
});
