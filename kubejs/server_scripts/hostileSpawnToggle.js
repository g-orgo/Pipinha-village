console.info("[SOCIETY] hostileSpawnToggle.js loaded");

// Applies the hostile spawn choice made on the create world screen to the new
// world. Spawn blocking and the toggle buttons live in
// startup_scripts/hostileSpawnToggle.js. Same "new world" test as
// worldCreationLock.js (overworld game time still near zero).
const HOSTILE_TOGGLE_NEW_WORLD_MAX_TIME = 100;

ServerEvents.loaded((e) => {
  try {
    let pending = global.pendingHostileSpawnsOff;
    global.pendingHostileSpawnsOff = "none";
    if (pending !== true && pending !== false) return;
    if (e.server.overworld().dayTime > HOSTILE_TOGGLE_NEW_WORLD_MAX_TIME) return;
    global.setHostileSpawnsOff(e.server, pending === true);
  } catch (err) {
    console.error(`[hostileSpawnToggle] applying the create world choice failed: ${err}`);
  }
});
