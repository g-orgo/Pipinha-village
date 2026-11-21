console.info("[SOCIETY] steadFastSkill.js loaded");

const steadfastThrottle = ((temp) => (entity, tick, identifier) => {
  // KubeJS 7: entity.age is undefined, so the throttle never held. Use the tick count.
  const { uuid } = entity;
  const age = global.playerTicks(entity);
  const key = `${uuid}${identifier}`;
  const now = temp[key];
  if (!now || age - now >= tick) {
    temp[key] = age;
    return false;
  }
  return true;
})({});

EntityEvents.beforeHurt((e) => {
  // KubeJS 7: the event exposes getEntity(); server and level come from the entity (EntityKJS).
  const entity = e.entity;
  const level = entity.level;
  const server = entity.server;
  // Fix windswept bug
  if (entity.isPlayer() && entity.getTicksFrozen() > 140) entity.setTicksFrozen(140);
  if (!entity.isPlayer() || steadfastThrottle(entity, 20, "steadfast_throttle")) return;
  if (entity.isPlayer() && Math.random() < 0.2 && entity.stages.has("steadfast")) {
    entity.heal(2);
    level.spawnParticles(
      "minecraft:heart",
      true,
      entity.x,
      entity.y + 1.5,
      entity.z,
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      5,
      0.01
    );
    server.runCommandSilent(
      `playsound species:item.wicked_treat.apply block @a ${entity.x} ${entity.y} ${entity.z}`
    );
  }
});
