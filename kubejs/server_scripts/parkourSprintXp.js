console.info("[SOCIETY] parkourSprintXp.js loaded");

// Sprint XP: every 40 ticks (2 seconds) of sprinting grants 15 XP to society:parkour.
// Sprint time accumulates across short breaks; it only counts while actually moving.
const SPRINT_TICKS_PER_REWARD = 40;
const SPRINT_XP_PER_REWARD = 15;
// Swimming (sprint-swimming or sprinting in water) grants the same XP at a longer interval (6 seconds).
const SWIM_TICKS_PER_REWARD = 120;
// Minimum horizontal speed (blocks per tick) to count a tick as sprinting.
const SPRINT_MIN_TICK_DELTA = 0.1;
// Single-tick horizontal deltas above this are teleports and are ignored.
const SPRINT_MAX_TICK_DELTA = 10;

const sprintLastPos = {};
const sprintTicks = {};
const swimTicks = {};

PlayerEvents.tick((e) => {
  const { player } = e;
  if (player.level.isClientSide() || player.isFake()) return;

  const id = String(player.getUuid());
  const x = player.getX();
  const z = player.getZ();
  const last = sprintLastPos[id];
  sprintLastPos[id] = { x: x, z: z };
  if (!last) return;

  const dx = x - last.x;
  const dz = z - last.z;
  const delta = Math.sqrt(dx * dx + dz * dz);
  if (delta < SPRINT_MIN_TICK_DELTA || delta > SPRINT_MAX_TICK_DELTA) return;
  if (!player.isSprinting()) return;

  const swimming = player.isSwimming() || player.isInWater();
  const counters = swimming ? swimTicks : sprintTicks;
  const interval = swimming ? SWIM_TICKS_PER_REWARD : SPRINT_TICKS_PER_REWARD;
  const ticks = (counters[id] || 0) + 1;
  if (ticks >= interval) {
    counters[id] = 0;
    global.grantParkourXp(player, SPRINT_XP_PER_REWARD);
  } else {
    counters[id] = ticks;
  }
});
