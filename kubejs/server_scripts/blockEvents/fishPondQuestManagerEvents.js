BlockEvents.rightClicked("society:fish_pond_manager", (e) => {
  const { item, hand, player, level, block } = e;
  if (hand !== "MAIN_HAND" || item !== "create:clipboard") return;
  global.addItemCooldown(player, item, 10);
  player.swing();
  // 1.21.1: clipboard pages are data component create:clipboard_content, not NBT.
  // Writing the quest pages to the held clipboard is disabled until ported.
  e.cancel();
});
