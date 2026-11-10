console.info("[SOCIETY] worldCreationLock.js loaded");

// The difficulty is always HARD. A freshly created world (overworld game time
// still near zero) starts on HARD with the difficulty locked; every world, new
// or old, is pulled back to HARD if anything changes it (the /difficulty
// command ignores the lock). Older saves are not locked, their difficulty
// button is greyed out by startup_scripts/hostileSpawnToggle.js instead.
// The create world screen side lives in startup_scripts/forgeEvents/worldCreationLock.js.
const NEW_WORLD_MAX_GAME_TIME = 100;
const DIFFICULTY_CHECK_TICKS = 20;
let difficultyCheckFailed = false;

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

ServerEvents.tick((e) => {
  if (difficultyCheckFailed) return;
  try {
    let server = e.server;
    if (server.tickCount % DIFFICULTY_CHECK_TICKS !== 0) return;
    if (String(server.getWorldData().getDifficulty()) === "HARD") return;
    server.runCommandSilent("difficulty hard");
    console.info("[worldCreationLock] difficulty changed, set back to HARD");
  } catch (err) {
    difficultyCheckFailed = true;
    console.error(`[worldCreationLock] difficulty check failed: ${err}`);
  }
});
