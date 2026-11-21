// Server side of the charged-jump XP: the client sends this channel when ParCool
// starts a charge jump at full charge (see startup_scripts/forgeEvents/parkourSkills.js).
(function () {
  const CJ_XP = 15;
  const CJ_COOLDOWN_TICKS = 10;
  const cjLastAge = {};

  NetworkEvents.dataReceived("society.parkour_charge_jump", (e) => {
    const player = e.player;
    if (!player || player.isFake()) return;
    const id = String(player.getUuid());
    const last = cjLastAge[id];
    if (last !== undefined && global.playerTicks(player) - last < CJ_COOLDOWN_TICKS) return;
    cjLastAge[id] = global.playerTicks(player);
    global.grantParkourXp(player, CJ_XP);
  });
})();
