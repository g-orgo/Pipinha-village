console.info("[SOCIETY] canonicalItemLoot.js loaded");

// Blocks, chests, mobs and fishing drop the canonical item instead of a duplicate
// (startup_scripts/globalCanonicalItems.js).
LootJS.modifiers((e) => {
  const modifier = e.addLootTableModifier(/.*/);
  Object.keys(global.canonicalItems).forEach((dup) => {
    modifier.replaceLoot(dup, global.canonicalItems[dup], true);
  });
});
