console.info("[SOCIETY] dogFollowOwner.js loaded");

// Tamed animals in follow mode (any tamed mob, not only dogs; mounts excluded) come along when their owner moves without walking: after a
// teleport (any method, including dimension changes) they are placed at the owner's
// feet. While the owner rides a vehicle (horse, boat, cart...) they disappear: they
// are saved into the owner's data and come back at the owner's feet on dismount. Driven every server tick by
// startup_scripts/dogFollowTick.js through global.sunlitDogFollowTick.

(function () {
  PlayerEvents.loggedOut((e) => {
    const states = global.runtime.dogFollowStates;
    if (states) delete states[String(e.player.uuid)];
  });
})();
