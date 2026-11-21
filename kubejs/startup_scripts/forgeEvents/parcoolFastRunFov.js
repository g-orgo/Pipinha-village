console.info("[SOCIETY] parcoolFastRunFov.js loaded");

// Keeps the camera FOV steady while ParCool's fast run turns on and off.
//
// Since 2026-11-18 fast run is automatic (`input = "ALWAYS"` in parcool-client.toml, as the
// 1.20.1 "Auto" control). ParCool 4.x applies fast run as a server-side MOVEMENT_SPEED
// modifier (`parcool:modi.fast_run`, ADD_VALUE), and vanilla widens the FOV with movement
// speed, so every start/stop of fast run pushed the FOV in and out while running.
// This listener rebuilds the FOV as if that one modifier were absent (same idea Via Romana
// uses for its road speed). Sprint, potions and every other speed change keep their effect.
//
// Client only: ComputeFovModifierEvent does not exist on a dedicated server.
// Startup scripts run twice per session, so the listener may be registered twice; each
// event object is handled once (=== on the wrapped event compares identity), so the correction is never applied twice.

// Diagnostic log: once per second, only when something toggled (fast run, sprint,
// exhaustion) or the FOV moved. Turn off only after the owner confirms in game.
const FAST_RUN_FOV_DEBUG = true;
const FAST_RUN_MODIFIER = "parcool:modi.fast_run";
const $Attributes = Java.loadClass("net.minecraft.world.entity.ai.attributes.Attributes");
const $Parkourability = Java.loadClass("com.alrex.parcool.common.Parkourability");
const $ParCoolActions = Java.loadClass("com.alrex.parcool.common.action.ParCoolActions");

global.fastRunFovErrorLogged = false;
global.fastRunFovLastEvent = null;
global.fastRunFovDebug = { until: 0, ticks: 0, fastRun: 0, sprint: 0, doing: 0, exhausted: 0,
  last: null, rawMin: 9, rawMax: 0, outMin: 9, outMax: 0 };

const fastRunFovError = (where, err) => {
  if (global.fastRunFovErrorLogged) return;
  global.fastRunFovErrorLogged = true;
  console.error(`[fovdebug] ${where}: ${err}`);
};

// Movement speed value without the fast run modifier. ADD_VALUE modifiers are summed with
// the base before both multipliers, so removing one scales the final value by (S - a) / S.
const speedWithoutFastRun = (inst) => {
  let value = inst.getValue();
  let sum = inst.getBaseValue();
  let fastRun = 0;
  let it = inst.getModifiers().iterator();
  let mod = null;
  while (it.hasNext()) {
    mod = it.next();
    if (mod.operation().ordinal() !== 0) continue;
    sum += mod.amount();
    if (String(mod.id()) === FAST_RUN_MODIFIER) fastRun += mod.amount();
  }
  if (fastRun === 0 || sum <= 0) return { value: value, without: value, fastRun: false };
  return { value: value, without: Math.max(0, value * (sum - fastRun) / sum), fastRun: true };
};

const fastRunFovDebug = (player, speed, raw, out) => {
  let d = global.fastRunFovDebug;
  let now = Date.now();
  let state = { fastRun: speed.fastRun, sprint: player.isSprinting(), doing: false, exhausted: false };
  let parkour = null;
  let toggles = 0;
  try {
    parkour = $Parkourability.get(player);
    state.doing = parkour.get($ParCoolActions.FAST_RUN).isDoing();
    state.exhausted = parkour.getStamina().isExhausted();
  } catch (err) {
    fastRunFovError("parcool state", err);
  }
  if (d.last !== null) {
    if (d.last.fastRun !== state.fastRun) d.fastRun++;
    if (d.last.sprint !== state.sprint) d.sprint++;
    if (d.last.doing !== state.doing) d.doing++;
    if (d.last.exhausted !== state.exhausted) d.exhausted++;
  }
  d.last = state;
  d.ticks++;
  d.rawMin = Math.min(d.rawMin, raw);
  d.rawMax = Math.max(d.rawMax, raw);
  d.outMin = Math.min(d.outMin, out);
  d.outMax = Math.max(d.outMax, out);
  if (now < d.until) return;
  toggles = d.fastRun + d.sprint + d.doing + d.exhausted;
  if (toggles > 0 || d.outMax - d.outMin > 0.01) {
    console.info(
      `[fovdebug] 1s/${d.ticks}t trocas: bonusFastRun=${d.fastRun} sprint=${d.sprint} ` +
        `fastRun=${d.doing} exausto=${d.exhausted} | fov vanilla ${d.rawMin.toFixed(3)}-${d.rawMax.toFixed(3)} ` +
        `-> pack ${d.outMin.toFixed(3)}-${d.outMax.toFixed(3)} | agora fastRun=${state.doing} sprint=${state.sprint}`
    );
  }
  d.until = now + 1000;
  d.ticks = 0;
  d.fastRun = d.sprint = d.doing = d.exhausted = 0;
  d.rawMin = d.outMin = 9;
  d.rawMax = d.outMax = 0;
};

const onComputeFov = (e) => {
  let player = null;
  let walking = 0;
  let inst = null;
  let speed = null;
  let raw = 1;
  let out = 1;
  try {
    // Rhino 2101 hides hashCode(); === on two wrapped Java objects compares identity.
    if (e === global.fastRunFovLastEvent) return;
    global.fastRunFovLastEvent = e;
    player = e.getPlayer();
    walking = player.getAbilities().getWalkingSpeed();
    inst = player.getAttribute($Attributes.MOVEMENT_SPEED);
    if (inst === null || walking === 0) return;
    speed = speedWithoutFastRun(inst);
    raw = e.getNewFovModifier();
    out = raw;
    if (speed.fastRun) {
      // Vanilla speed term: (speed / walkingSpeed + 1) / 2, multiplied into the modifier.
      out = raw * ((speed.without / walking + 1) / 2) / ((speed.value / walking + 1) / 2);
      e.setNewFovModifier(out);
    }
    if (FAST_RUN_FOV_DEBUG) fastRunFovDebug(player, speed, raw, out);
  } catch (err) {
    fastRunFovError("ComputeFovModifierEvent", err);
  }
};

let $ComputeFovModifierEvent = null;
try {
  $ComputeFovModifierEvent = Java.loadClass("net.neoforged.neoforge.client.event.ComputeFovModifierEvent");
} catch (err) {
  // Dedicated server: the client event class is missing, nothing to do.
}
if ($ComputeFovModifierEvent !== null) {
  NativeEvents.onEvent($ComputeFovModifierEvent, (e) => onComputeFov(e));
  console.info("[fovdebug] FOV sem o bonus da corrida rapida ativo");
}
