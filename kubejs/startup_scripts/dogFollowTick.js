console.info("[SOCIETY] dogFollowTick.js loaded");

// Forwards the server tick to global.sunlitDogFollowTick (defined in
// server_scripts/entities/dogFollowOwner.js). Runs once per tick (NeoForge Pre).
NativeEvents.onEvent("net.neoforged.neoforge.event.tick.ServerTickEvent$Pre", (e) => {
  if (!global.sunlitDogFollowTick) return;
  global.sunlitDogFollowTick(e.getServer());
});
