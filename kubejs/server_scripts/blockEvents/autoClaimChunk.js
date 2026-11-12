console.info("[SOCIETY] autoClaimChunk.js loaded");

// Auto-claims (FTB Chunks) the chunk where a player deliberately places something that needs a
// loaded chunk or is worth protecting: every block with a block entity (chests, barrels, furnaces,
// crab traps, Society machines, Create parts...) and every bed. Only placement claims: opening a
// chest, breaking or walking around never does. Claimed chunks are the ones the regen script keeps
// (sunlit_tools/regen_chunks.py --so-claims). Signs and banners are trail markers, so they do not
// claim. 2026-11-11, owner request.

BlockEvents.placed((e) => {
  try {
    global.autoClaimChunk(e.player, e.block);
  } catch (err) {
    console.error(`[SOCIETY] autoClaimChunk failed: ${err}`);
  }
});
