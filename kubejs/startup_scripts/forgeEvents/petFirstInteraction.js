console.info("[SOCIETY] petFirstInteraction.js loaded");

const PET_FIRST_PRIORITY = Java.loadClass("net.neoforged.bus.api.EventPriority");
const ENTITY_INTERACT_EVENT = Java.loadClass("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract");
const PET_FIRST_DEBUG = true;
global.runtime.petFirstInteractionTicks = {};
let petFirstInteractionErrorLogged = false;

// Redomesticate may cancel tameable-animal clicks before ItemEvents sees them.
// Intercept an unpetted pet first, then let the normal animal handler apply affection.
NativeEvents.onEvent(PET_FIRST_PRIORITY.HIGHEST, ENTITY_INTERACT_EVENT, (e) => {
  let player = null;
  let target = null;
  let eventHand = null;
  let hand = "";
  let item = null;
  let level = null;
  let server = null;
  let uuid = "";
  let now = NaN;
  let ticks = null;
  let shouldPetFirst = false;
  try {
    player = e.getEntity();
    if (!player || player.isFake()) return;
    target = e.getTarget();
    eventHand = e.getHand();
    hand = String(eventHand);
    level = player.level;
    if (level.isClientSide()) return;
    server = player.server;
    uuid = String(target.uuid);
    now = Number(level.getLevelData().getGameTime());
    ticks = global.runtime.petFirstInteractionTicks;
    if (hand === "OFF_HAND" && ticks[uuid] === now) {
      e.setCanceled(true);
      return;
    }
    item = player.getItemInHand(eventHand);
    shouldPetFirst = global.sunlitShouldPetFirst(hand, player, item, target, level);
    if (global.checkEntityTag(target, "society:pet_animal") || global.checkEntityTag(target, "society:husbandry_animal")) {
      console.info(`[SOCIETY] pet-first check: target=${target.type} hand=${hand} day=${global.getDay(level)} last=${target.persistentData.getInt("ageLastPet")} item=${item.id} should=${shouldPetFirst}`);
    }
    if (!shouldPetFirst) return;

    Object.keys(ticks).forEach((key) => {
      if (ticks[key] !== now) delete ticks[key];
    });
    ticks[uuid] = now;
    // Redomesticate may consume an unpetted pet click before KubeJS ItemEvents runs.
    e.setCanceled(true);
    if (PET_FIRST_DEBUG) console.info(`[SOCIETY] pet-first: player=${player.username} target=${target.type} hand=${hand} day=${global.getDay(level)} item=${item.id}`);
    global.handleHusbandryBase(hand, player, item, target, level, server);
    server.scheduleInTicks(1, () => {
      let vehicle = player.getVehicle();
      if (vehicle && String(vehicle.uuid) === uuid) player.stopRiding();
    });
  } catch (err) {
    if (!petFirstInteractionErrorLogged) {
      petFirstInteractionErrorLogged = true;
      console.error(`[SOCIETY] petFirstInteraction failed: ${err}`);
    }
  }
});
