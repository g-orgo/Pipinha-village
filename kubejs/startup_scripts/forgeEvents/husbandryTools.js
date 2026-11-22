console.info("[SOCIETY] husbandryTools.js loaded");

const HUSBANDRY_TOOL_PRIORITY = Java.loadClass("net.neoforged.bus.api.EventPriority");
const HUSBANDRY_ENTITY_INTERACT = Java.loadClass("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract");
const HUSBANDRY_TOOLS_DEBUG = true;
global.runtime.nativeHusbandryToolTicks = {};
let husbandryToolsErrorLogged = false;

NativeEvents.onEvent(HUSBANDRY_TOOL_PRIORITY.HIGHEST, HUSBANDRY_ENTITY_INTERACT, (e) => {
  let player = null;
  let target = null;
  let hand = "";
  let item = null;
  let level = null;
  let server = null;
  let uuid = "";
  let now = NaN;
  let ticks = null;
  let itemId = "";
  let milkPail = false;
  let magicShears = false;
  try {
    player = e.getEntity();
    if (!player || player.isFake()) return;
    hand = String(e.getHand());
    if (hand !== "MAIN_HAND") return;
    level = player.level;
    if (level.isClientSide()) return;
    target = e.getTarget();
    if (!global.checkEntityTag(target, "society:husbandry_animal")) return;
    item = player.getItemInHand(e.getHand());
    itemId = String(item.id);
    milkPail = itemId === "society:milk_pail";
    magicShears = itemId === "society:magic_shears";
    if (!milkPail && !magicShears) return;

    server = player.server;
    uuid = String(target.uuid);
    now = Number(level.getLevelData().getGameTime());
    ticks = global.runtime.nativeHusbandryToolTicks;
    Object.keys(ticks).forEach((key) => {
      if (ticks[key] !== now) delete ticks[key];
    });
    ticks[uuid] = now;
    e.setCanceled(true);
    if (HUSBANDRY_TOOLS_DEBUG) console.info(`[SOCIETY] husbandry-tool: player=${player.username} target=${target.type} item=${itemId}`);
    global.handleHusbandryBase(hand, player, item, target, level, server);
  } catch (err) {
    if (!husbandryToolsErrorLogged) {
      husbandryToolsErrorLogged = true;
      console.error(`[SOCIETY] husbandryTools failed: ${err}`);
    }
  }
});
