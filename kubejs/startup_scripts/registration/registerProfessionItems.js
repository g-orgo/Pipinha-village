console.info("[SOCIETY] registerProfessionItems.js loaded");

// Profession crystals sold by the Guild. Behaviour lives in
// server_scripts/itemEvents/professionCrystals.js.
StartupEvents.registry("item", (e) => {
  e.create(`society:crystal_of_regret_professions`)
    .displayName("Crystal of Regret: Professions")
    .texture("society:item/crystal_of_regret_professions")
    .tooltip(Text.translatable("society.crystal_of_regret_professions.description").red())
    .tooltip(Text.translatable("society.crystal_of_regret_professions.description.warn").red());

  e.create(`society:crystal_of_ambition_professions`)
    .displayName("Crystal of Ambition: Professions")
    .texture("society:item/crystal_of_ambition_professions")
    .tooltip(Text.translatable("society.crystal_of_ambition_professions.description").gold())
    .tooltip(Text.translatable("society.crystal_of_ambition_professions.description.warn").gold());
});
