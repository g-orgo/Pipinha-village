console.info("[SOCIETY] mercantil.js loaded");

// Keeps the Mercantil discount stages (mercantilGlobals.js) in line with the
// Haggle nodes and the professions the player follows.
PlayerEvents.loggedIn((e) => {
  try {
    global.syncMercantilStages(e.player);
  } catch (err) {
    console.error(`[mercantil] login sync failed: ${err}`);
  }
});

// Bountiful has no completion event. Turning a paper in only happens when the
// board is right clicked with it in hand: that consumes the stack, while an
// unfinished or expired paper stays intact. The block runs after this listener,
// so the XP is decided one tick later by looking at the same stack.
BlockEvents.rightClicked("bountiful:bountyboard", (e) => {
  let { player, server } = e;
  if (!player || player.isFake()) return;
  let stack = player.getItemInHand(e.hand);
  if (stack.id !== "bountiful:bounty") return;
  let xp = global.mercantilBountyXp(stack);
  server.scheduleInTicks(1, () => {
    if (stack.isEmpty()) global.grantMercantilNpcXp(server, player, xp);
  });
});

PlayerEvents.tick((e) => {
  let player = e.player;
  if (!player || player.isFake() || global.playerTicks(player) % 100 != 0) return;
  try {
    global.syncMercantilStages(player);
  } catch (err) {
    console.error(`[mercantil] sync failed: ${err}`);
  }
});
