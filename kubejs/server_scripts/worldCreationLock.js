console.info("[SOCIETY] worldCreationLock.js loaded");

// A freshly created world starts on HARD with the difficulty locked. Only
// worlds that have just been created are touched (overworld game time still
// near zero), so existing saves keep whatever difficulty they already have.
// The create world screen side lives in startup_scripts/forgeEvents/worldCreationLock.js.
const NEW_WORLD_MAX_GAME_TIME = 100;

ServerEvents.loaded((e) => {
  try {
    let server = e.server;
    if (server.overworld().dayTime > NEW_WORLD_MAX_GAME_TIME) return;
    server.runCommandSilent("difficulty hard");
    server.setDifficultyLocked(true);
    console.info("[worldCreationLock] new world: difficulty set to HARD and locked");
  } catch (err) {
    console.error(`[worldCreationLock] difficulty lock failed: ${err}`);
  }
});
