console.info("[SOCIETY] dogFollowTick.js loaded");

// Forwards the server tick to global.sunlitDogFollowTick (defined in
// server_scripts/entities/dogFollowOwner.js). Runs once per tick, at phase START.
ForgeEvents.onEvent("net.minecraftforge.event.TickEvent$ServerTickEvent", (e) => {
  if (String(e.phase) !== "START") return;
  if (!global.sunlitDogFollowTick) return;
  global.sunlitDogFollowTick(e.getServer());
});
