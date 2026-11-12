console.info("[SOCIETY] parkourSkills.js loaded");

// XP granted to the society:parkour Puffish category from ParCool actions.
// Sprint XP is handled in server_scripts/parkourSprintXp.js.
const PARKOUR_CATEGORY = "society:parkour";
const CHARGE_JUMP_XP = 15;
const SLIDE_XP = 8;
const SLIDE_COOLDOWN_TICKS = 40;
const CHARGE_JUMP_ACTION = "com.alrex.parcool.common.action.impl.ChargeJump";
const SLIDE_ACTION = "com.alrex.parcool.common.action.impl.Slide";

global.parkourSlideCooldown = {};

// Runs Puffish's own "experience add" command as the server.
global.grantParkourXp = (player, amount) => {
  if (amount <= 0) return;
  player
    .getServer()
    .runCommandSilent(
      `puffish_skills experience add ${player.username} ${PARKOUR_CATEGORY} ${amount}`
    );
};

global.handleParCoolStart = (e) => {
  const player = e.getPlayer();
  const action = e.getAction();

  if (action instanceof Java.type(CHARGE_JUMP_ACTION)) {
    // chargeTick is only updated on the client, so the charge check runs there
    // and the grant is requested from the server via a client-to-server packet.
    // Any charged jump counts (ParCool already requires at least 50% charge to start one).
    if (player.level.isClientSide()) {
      console.info("[SOCIETY] charge jump started, requesting parkour XP");
      player.sendData("society.parkour_charge_jump", {});
    }
    return;
  }

  if (player.level.isClientSide() || player.isFake()) return;

  if (action instanceof Java.type(SLIDE_ACTION)) {
    const id = String(player.getUuid());
    const last = global.parkourSlideCooldown[id];
    if (last !== undefined && player.age - last < SLIDE_COOLDOWN_TICKS) return;
    global.parkourSlideCooldown[id] = player.age;
    global.grantParkourXp(player, SLIDE_XP);
  }
};

NativeEvents.onEvent(Java.loadClass("com.alrex.parcool.api.action.ParCoolActionEvent$Start$Pre"), (e) => {
  global.handleParCoolStart(e);
});
