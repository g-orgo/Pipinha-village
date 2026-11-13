console.info("[SOCIETY] canonicalItemLoot.js loaded");

// Blocks, chests, mobs and fishing drop the canonical item instead of a duplicate
// (startup_scripts/globalCanonicalItems.js).
LootJS.modifiers((e) => {
  const modifier = e.addTableModifier(/.*/);
  Object.keys(global.canonicalItems).forEach((dup) => {
    if (!Item.exists(dup)) return;
    modifier.replaceLoot(dup, global.canonicalItems[dup], true);
  });
});
