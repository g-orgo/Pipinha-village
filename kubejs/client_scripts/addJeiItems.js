RecipeViewerEvents.addEntries('item', (e) => {
  e.add("displaydelight:food_plate")
  e.add("displaydelight:small_food_plate")
  e.add("minecraft:bundle");
  e.add("snowyspirit:ginger_crate");
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
