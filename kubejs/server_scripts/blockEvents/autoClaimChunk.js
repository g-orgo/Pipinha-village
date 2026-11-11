console.info("[SOCIETY] autoClaimChunk.js loaded");

// Auto-claims (FTB Chunks) the chunk where a player deliberately places something that needs a
// loaded chunk or is worth protecting: every block with a block entity (chests, barrels, furnaces,
// crab traps, Society machines, Create parts...) and every bed. Only placement claims: opening a
// chest, breaking or walking around never does. Claimed chunks are the ones the regen script keeps
// (sunlit_tools/regen_chunks.py --so-claims). Signs and banners are trail markers, so they do not
// claim. 2026-11-11, owner request.
const $FTBChunksAPI = Java.loadClass("dev.ftb.mods.ftbchunks.api.FTBChunksAPI");
const $ChunkPos = Java.loadClass("net.minecraft.world.level.ChunkPos");
const $ChunkDimPos = Java.loadClass("dev.ftb.mods.ftblibrary.math.ChunkDimPos");

const AUTO_CLAIM_SKIP_TAGS = ["minecraft:all_signs", "minecraft:banners"];

global.autoClaimWanted = (block) => {
  if (block.hasTag("minecraft:beds")) return true;
  if (AUTO_CLAIM_SKIP_TAGS.some((tag) => block.hasTag(tag))) return false;
  return block.getEntity() != null || block.blockState.hasBlockEntity();
};

global.autoClaimChunk = (player, block) => {
  if (!player || player.isFake() || player.level.isClientSide()) return;
  if (!global.autoClaimWanted(block)) return;
  const api = $FTBChunksAPI.api();
  if (!api.isManagerLoaded()) return;
  const dimension = block.level.dimension();
  const cx = block.pos.x >> 4;
  const cz = block.pos.z >> 4;
  if (api.getManager().getChunk(new $ChunkDimPos(dimension, cx, cz)) != null) return;
  const result = api.claimAsPlayer(player, dimension, new $ChunkPos(cx, cz), false);
  if (result.isSuccess()) {
    player.setStatusMessage(Text.translatable("sunlit_claims.auto_claimed", `${cx}, ${cz}`).green());
  }
};

BlockEvents.placed((e) => {
  try {
    global.autoClaimChunk(e.player, e.block);
  } catch (err) {
    console.error(`[SOCIETY] autoClaimChunk failed: ${err}`);
  }
});
