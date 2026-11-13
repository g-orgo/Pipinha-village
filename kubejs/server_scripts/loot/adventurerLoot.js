console.info("[SOCIETY] adventurerLoot.js loaded");

LootJS.modifiers((e) => {
  e.addTableModifier(LootType.CHEST)
    .hasAnyStage("relic_hunter")
    .randomChance(0.10)
    .addLoot("society:relic_trove");
  e.addTableModifier(LootType.CHEST)
    .hasAnyStage("artifact_hunter")
    .randomChance(0.10)
    .addLoot("society:artifact_trove");
  e.addTableModifier(LootType.CHEST)
    .hasAnyStage("prismatic_realm")
    .randomChance(0.05)
    .addLoot("society:prismatic_shard");
});
