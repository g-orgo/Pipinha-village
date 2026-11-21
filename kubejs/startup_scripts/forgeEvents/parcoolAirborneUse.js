console.info("[SOCIETY] parcoolAirborneUse.js loaded");

// Keeps ParCool's grab (right mouse, `key.parcool.hang`) from opening doors mid-jump.
//
// ParCool 4.x shares the right mouse button with vanilla "use". HangOn only cancels the
// use key while it is already hanging (HangOn.onInput checks isDoing()), so the press that
// starts the grab, and the repeats of a held button (vanilla repeats use every 4 ticks),
// still used the block under the crosshair: a door on top of the wall being climbed
// opened instead of the player grabbing the ledge.
//
// Rule: while the player is airborne, right-clicking a block does not use the block
// (doors, trapdoors, buttons, levers, containers). The held item still works, so placing
// blocks while jumping (pillaring) and buckets mid-fall keep working.
// Airborne means: not on ground, no ground within GROUND_MARGIN below the feet, not
// riding, not flying (creative or elytra), not in water or lava and not on a ladder,
// vine or scaffolding (opening a trapdoor from a ladder stays as vanilla).
//
// RightClickBlock fires on the client (prediction) and again on the server (the real
// use), so the same physical rule runs on both sides. The ground margin keeps both sides
// agreeing around the landing tick, when the onGround flag can differ by a tick.
//
// KubeJS 7 (2101): members that share a name with a field may come as a property instead
// of a method (`entity.level`), so `level`, `onGround` and Vec3 `y` are read through airborneMember().
const GROUND_MARGIN = 0.2;
// Diagnostic log: at most once per second per side, only when a block use is denied.
// Turn off only after the owner confirms in game.
const AIRBORNE_USE_DEBUG = true;
const $TriState = Java.loadClass("net.neoforged.neoforge.common.util.TriState");

global.airborneUseErrorLogged = false;
global.airborneUseLastLog = { client: 0, server: 0 };

const airborneUseError = (where, err) => {
  if (global.airborneUseErrorLogged) return;
  global.airborneUseErrorLogged = true;
  console.error(`[parcooluse] ${where} failed (logged once): ${err}`);
};

const airborneMember = (obj, name) => {
  if (typeof obj[name] === "function") return obj[name]();
  return obj[name];
};

global.isParkourAirborne = (player) => {
  let level = null;
  let below = null;
  if (airborneMember(player, "onGround")) return false;
  if (player.isPassenger() || player.isSpectator()) return false;
  if (player.getAbilities().flying || player.isFallFlying()) return false;
  if (player.isInWater() || player.isInLava() || player.onClimbable()) return false;
  level = airborneMember(player, "level");
  below = player.getBoundingBox().move(0, -GROUND_MARGIN, 0);
  return level["noCollision(net.minecraft.world.entity.Entity,net.minecraft.world.phys.AABB)"](player, below);
};

global.handleAirborneBlockUse = (e) => {
  let player = null;
  let side = "server";
  let now = 0;
  try {
    player = e.getEntity();
    if (!player || !global.isParkourAirborne(player)) return;
    e.setUseBlock($TriState.FALSE);
    if (!AIRBORNE_USE_DEBUG) return;
    side = airborneMember(player, "level").isClientSide() ? "client" : "server";
    now = Date.now();
    if (now - global.airborneUseLastLog[side] < 1000) return;
    global.airborneUseLastLog[side] = now;
    console.info(
      `[parcooluse] ${side}: uso de bloco negado no ar ` +
        `(${String(airborneMember(player, "level").getBlockState(e.getPos()).getBlock())} em ${String(e.getPos())}, ` +
        `mao ${String(e.getHand())}, item ${String(e.getItemStack().getItem())}, vy ${Number(airborneMember(player.getDeltaMovement(), "y")).toFixed(2)})`
    );
  } catch (err) {
    airborneUseError("RightClickBlock", err);
  }
};

// The body lives in a global function: a local declared directly inside the inline
// callback makes Rhino throw "redeclaration of var" on every click.
NativeEvents.onEvent("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$RightClickBlock", (e) => {
  global.handleAirborneBlockUse(e);
});
