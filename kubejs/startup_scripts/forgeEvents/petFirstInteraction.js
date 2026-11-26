console.info("[SOCIETY] petFirstInteraction.js loaded");

const PET_FIRST_PRIORITY = Java.loadClass("net.neoforged.bus.api.EventPriority");
const ENTITY_INTERACT_EVENT = Java.loadClass("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract");
const PET_FIRST_RESULT = Java.loadClass("net.minecraft.world.InteractionResult");
const PET_FIRST_DEBUG = true;
global.runtime.petFirstInteractionTicks = {};
let petFirstInteractionErrorLogged = false;

// Redomesticate may cancel tameable-animal clicks before ItemEvents sees them.
// Intercept an unpetted pet first, then let the normal animal handler apply affection.
// Taming by petting (petTaming.js) runs before it, so one click on a wild animal of
// #society:tame_by_petting tames it and, when it is due, also pets it.
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
  let pettable = false;
  let showHearts = false;
  let taming = "none";
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
    taming = global.petTaming ? global.petTaming.onClick(player, target, hand, item, level) : "none";
    if (taming === "refused") {
      e.setCanceled(true);
      return;
    }
    if (taming === "tamed") {
      e.setCanceled(true);
      e.setCancellationResult(PET_FIRST_RESULT.SUCCESS);
    }
    shouldPetFirst = global.sunlitShouldPetFirst(hand, player, item, target, level);
    // Every animal of the pack: husbandry animals, pets and any other animal (petTaming.js).
    pettable = global.isPettableAnimal(target);
    if (pettable) {
      console.info(`[SOCIETY] pet-first check: target=${target.type} hand=${hand} day=${global.getDay(level)} last=${target.persistentData.getInt("ageLastPet")} item=${item.id} should=${shouldPetFirst}`);
    }
    // An empty-hand click after today's petting only shows the hearts HUD. Redomesticate and
    // vanilla consume the owner's click on a tamed animal (sit, follow) before animalBase.js
    // sees it, so the HUD is sent from here and the click is not cancelled.
    showHearts = !shouldPetFirst && taming !== "tamed" && pettable && hand === "MAIN_HAND" && item.isEmpty();
    if (!shouldPetFirst && taming !== "tamed" && !showHearts) return;

    Object.keys(ticks).forEach((key) => {
      if (ticks[key] !== now) delete ticks[key];
    });
    ticks[uuid] = now;
    if (showHearts) {
      global.handleHusbandryBase(hand, player, item, target, level, server);
      return;
    }
    if (!shouldPetFirst) return;
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
