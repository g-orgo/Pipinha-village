// Entity clicks for the "Companheiros" quest chapter. Redomesticate cancels a taming click at
// the same priority as ItemEvents.entityInteracted, so that event may never see it. This native
// listener runs at LOWEST and also receives cancelled events; the handler itself is
// global.petGuideOnInteract, defined by server_scripts/entities/petGuideQuests.js (swapped on /reload).
console.info("[SOCIETY] petGuideInteract.js loaded");

global.petGuideInteractErrorLogged = false;

if (!global.petGuideInteractRegistered) {
  global.petGuideInteractRegistered = true;
  Java.loadClass("net.neoforged.neoforge.common.NeoForge").EVENT_BUS.addListener(
    Java.loadClass("net.neoforged.bus.api.EventPriority").LOWEST,
    true,
    Java.loadClass("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$EntityInteract"),
    (e) => {
      try {
        if (global.petGuideOnInteract) global.petGuideOnInteract(e);
      } catch (err) {
        if (!global.petGuideInteractErrorLogged) {
          global.petGuideInteractErrorLogged = true;
          console.error("[SOCIETY] petGuideInteract: " + err);
        }
      }
    }
  );
}
