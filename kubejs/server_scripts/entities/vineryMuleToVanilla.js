console.info("[SOCIETY] vineryMuleToVanilla.js loaded");

// The Let's Do Vinery trader mule is not part of the pack: every one that appears
// (old spawn eggs, mules already saved in the world) becomes a vanilla mule with
// the same data (owner, saddle, chest, items, name, health, position, UUID).
// The new mule is built before the old one is cancelled, so a failure keeps the old one.
EntityEvents.spawned("vinery:mule", (e) => {
  const old = e.entity;
  let mule;
  let holder = null;
  try {
    const nbt = old.getNbt();
    nbt.remove("DespawnDelay");
    mule = e.level.createEntity("minecraft:mule");
    mule.setNbt(nbt);
    if (old.isLeashed()) holder = old.getLeashHolder();
  } catch (err) {
    console.error(`[SOCIETY] vineryMuleToVanilla: ${err}`);
    return;
  }
  e.cancel();
  e.server.scheduleInTicks(1, () => {
    mule.spawn();
    if (holder) {
      try {
        mule.setLeashedTo(holder, true);
      } catch (err) {
        console.error(`[SOCIETY] vineryMuleToVanilla leash: ${err}`);
      }
    }
  });
});
