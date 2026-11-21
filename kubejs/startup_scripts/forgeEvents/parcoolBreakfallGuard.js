console.info("[SOCIETY] parcoolBreakfallGuard.js loaded");

// Restores ParCool 3.4 (1.20.1) client options that ParCool 4.x no longer has:
// - lowest_fall_distance_for_breakfall = 3.0: ParCool 4.x starts the breakfall (roll/tap)
//   on any landing while the key is held, so even a normal jump rolled. Short falls are
//   cancelled here.
// - enable_vault_in_air = false: ParCool 4.x vaults while airborne; here vault needs ground.
//
// ParCool 4.x posts ParCoolActionEvent$TryToStart for Breakfall in two places:
// - every server tick (ActionProcessor -> Action.isReadyToStart). Breakfall.canStart() is
//   always false, so that check never starts anything and is left alone here.
// - on landing, inside LivingFallEvent (Breakfall.onLand, NORMAL priority), right before
//   startExplicitly(). Only this one decides the roll, so the guard records the fall at
//   HIGHEST, judges TryToStart only while that landing is open, and closes it at LOWEST.
//
// KubeJS 7 (2101): entity.level is a property (level() throws) and the UUID comes from
// getUuid() (getStringUUID is not exposed).
const BREAKFALL_ACTION = Java.loadClass("com.alrex.parcool.common.action.impl.Breakfall");
const VAULT_ACTION = Java.loadClass("com.alrex.parcool.common.action.impl.Vault");
const EVENT_PRIORITY = Java.loadClass("net.neoforged.bus.api.EventPriority");
const LIVING_FALL_EVENT = Java.loadClass("net.neoforged.neoforge.event.entity.living.LivingFallEvent");
const MIN_FALL_DISTANCE = 3.0;
// Diagnostic log of each landing decision. Turn off only after the owner confirms in game.
const BREAKFALL_GUARD_DEBUG = true;

global.breakfallGuardErrorLogged = false;
// Player UUID -> fall distance of the landing being processed right now.
global.parcoolLandingFalls = {};

const breakfallGuardError = (where, err) => {
  if (global.breakfallGuardErrorLogged) return;
  global.breakfallGuardErrorLogged = true;
  console.error(`[SOCIETY] breakfall guard: ${where} failed (logged once): ${err}`);
};

const breakfallGuardDebug = (message) => {
  if (!BREAKFALL_GUARD_DEBUG) return;
  try {
    console.info(`[SOCIETY] breakfall guard: ${message}`);
  } catch (err) {
    breakfallGuardError("debug log", err);
  }
};

const serverPlayerKey = (entity) => {
  if (!entity || !entity.isPlayer() || entity.level.isClientSide()) return null;
  return String(entity.getUuid());
};

// Open the landing before ParCool's Breakfall.onLand reads the same event.
NativeEvents.onEvent(EVENT_PRIORITY.HIGHEST, LIVING_FALL_EVENT, (e) => {
  let key = null;
  try {
    key = serverPlayerKey(e.getEntity());
    if (key === null) return;
    global.parcoolLandingFalls[key] = Number(e.getDistance());
  } catch (err) {
    breakfallGuardError("fall record", err);
  }
});

// Close the landing after every listener ran.
NativeEvents.onEvent(EVENT_PRIORITY.LOWEST, LIVING_FALL_EVENT, (e) => {
  let key = null;
  try {
    key = serverPlayerKey(e.getEntity());
    if (key === null) return;
    delete global.parcoolLandingFalls[key];
  } catch (err) {
    breakfallGuardError("fall close", err);
  }
});

NativeEvents.onEvent(
  Java.loadClass("com.alrex.parcool.api.action.ParCoolActionEvent$TryToStart"),
  (e) => {
    // Rhino 2101: no const/let inside nested blocks, so everything is declared up here.
    let action = null;
    let player = null;
    let key = null;
    let distance = NaN;
    try {
      action = e.getAction();
      if (action instanceof VAULT_ACTION) {
        player = e.getPlayer();
        if (!player.onGround()) e.setCanceled(true);
        return;
      }
      if (!(action instanceof BREAKFALL_ACTION)) return;

      player = e.getPlayer();
      key = serverPlayerKey(player);
      if (key === null) return;
      distance = global.parcoolLandingFalls[key];
      // No landing open: this is the per-tick readiness check, which never starts a roll.
      if (distance === undefined) return;

      if (isNaN(distance) || distance < MIN_FALL_DISTANCE) {
        e.setCanceled(true);
        breakfallGuardDebug(`landing ${distance} blocks -> blocked (min ${MIN_FALL_DISTANCE})`);
      } else {
        breakfallGuardDebug(`landing ${distance} blocks -> roll allowed`);
      }
    } catch (err) {
      breakfallGuardError("TryToStart", err);
    }
  }
);
