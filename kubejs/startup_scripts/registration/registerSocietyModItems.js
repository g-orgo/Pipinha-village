console.info("[SOCIETY] registerSocietyModItems.js loaded");

// Items that the 1.20.1 society jar (Society 1.22) registered and that the pack still uses
// in shops, quests and scripts. Ids are kept as they were. Models and textures come from
// kubejs/assets/society/models/item and textures/item (copied from the old jar).
StartupEvents.registry("item", (e) => {
  e.create("society:invitation");
  e.create("society:villager");
  e.create("society:face_note");
  e.create("society:monocle");
  e.create("society:red_glasses");
  e.create("society:spiral_glasses");
});
