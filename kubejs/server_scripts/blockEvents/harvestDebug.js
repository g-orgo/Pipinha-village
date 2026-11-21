console.info("[SOCIETY] harvestDebug.js loaded");

// Diagnostic for area harvesting with a hoe (Quark Simple Harvest on right click, Quark Hoe Harvesting
// on break; radius from Sunrise's hoe_aoe_style data map). Logs "[harvestdebug]" lines in
// logs/kubejs/server.log: mature crops around the clicked one before, and how many were harvested
// 2 ticks later. Observes only, never cancels. Turn off once the owner confirms in game.
const HARVEST_DEBUG = true;
const HARVEST_DEBUG_RADIUS = 3;

const harvestDebugLog = (msg) => {
  try {
    console.info(`[harvestdebug] ${msg}`);
  } catch (err) {
    console.error(`[harvestDebug] log failed: ${err}`);
  }
};

// Positions (relative offsets) of mature crops around pos, same layer.
const harvestDebugMature = (level, pos) => {
  const found = [];
  let dx = 0;
  let dz = 0;
  let state = null;
  for (dx = -HARVEST_DEBUG_RADIUS; dx <= HARVEST_DEBUG_RADIUS; dx++) {
    for (dz = -HARVEST_DEBUG_RADIUS; dz <= HARVEST_DEBUG_RADIUS; dz++) {
      state = level.getBlockState(pos.offset(dx, 0, dz));
      if (state.block.isMaxAge && state.block.isMaxAge(state)) found.push([dx, dz]);
    }
  }
  return found;
};

const harvestDebugResult = (level, pos, before, kind) => {
  let after = [];
  let afterKeys = [];
  let harvested = [];
  try {
    after = harvestDebugMature(level, pos);
    afterKeys = after.map((p) => `${p[0]},${p[1]}`);
    harvested = before.filter((p) => afterKeys.indexOf(`${p[0]},${p[1]}`) < 0);
    harvestDebugLog(
      `${kind} result at ${pos.getX()},${pos.getY()},${pos.getZ()}: now ${String(level.getBlock(pos).id)} ` +
        `harvested ${harvested.length} ${JSON.stringify(harvested)}, still mature ${after.length}`
    );
  } catch (err) {
    harvestDebugLog(`${kind} result failed: ${err}`);
  }
};

// Rhino 2101: no const/let inside nested blocks, so every local is declared at the top.
const harvestDebugWatch = (e, kind) => {
  if (!HARVEST_DEBUG) return;
  let block = null;
  let player = null;
  let level = null;
  let item = null;
  let pos = null;
  let before = [];
  let cooldown = false;
  try {
    block = e.block;
    player = e.player;
    level = e.level;
    if (!player || !block || !level) return;
    item = player.getMainHandItem();
    if (!item.hasTag("minecraft:hoes")) return;
    if (!block.hasTag("minecraft:crops")) return;
    pos = block.pos;
    before = harvestDebugMature(level, pos);
    cooldown = player.getCooldowns().isOnCooldown(item.getItem());
    harvestDebugLog(
      `${kind} ${item.id} on ${String(block.id)} ${String(block.getProperties())} ` +
        `at ${pos.getX()},${pos.getY()},${pos.getZ()} hand=${e.hand} crouching=${player.isCrouching()} ` +
        `cooldown=${cooldown} mature within ${HARVEST_DEBUG_RADIUS}: ${before.length} ${JSON.stringify(before)}`
    );
    level.server.scheduleInTicks(2, () => harvestDebugResult(level, pos, before, kind));
  } catch (err) {
    harvestDebugLog(`${kind} failed: ${err}`);
  }
};

BlockEvents.rightClicked((e) => {
  if (e.hand == "MAIN_HAND") harvestDebugWatch(e, "rightclick");
});

BlockEvents.broken((e) => harvestDebugWatch(e, "break"));
