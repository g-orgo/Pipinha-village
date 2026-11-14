// Sunlit: stretches the day and the night without changing the 24000-tick day.
// Inside each phase, HOLD out of every CYCLE server ticks the clock is held back by one tick,
// spread evenly over the cycle.
// Daylight (ticks 0-12000): 1300 + 10700 / (107 / 227) = 24000 server ticks, 20 min.
// Night (ticks 12000-24000): 12000 / (2 / 3) = 18000 server ticks, 15 min.
// Day machines, the shipping bin and the player day counter run on dayTime windows sized
// to their tick rate, all ending at or before tick 1200. Inside a window a slower clock
// would make them run twice, so the slowdown only starts after the last one.
const $SunlitSetTimePacket = Java.loadClass("net.minecraft.network.protocol.game.ClientboundSetTimePacket");
const $SunlitGameRules = Java.loadClass("net.minecraft.world.level.GameRules");

const SUNLIT_TIME_PHASES = [
  { from: 1300, until: 12000, hold: 120, cycle: 227 },
  { from: 12000, until: 24000, hold: 1, cycle: 3 },
];

console.info("[Sunlit] sunlitLongerDay.js loaded");

const sunlitShouldHoldTime = (serverTick, timeOfDay) => {
  for (let i = 0; i < SUNLIT_TIME_PHASES.length; i++) {
    let phase = SUNLIT_TIME_PHASES[i];
    if (timeOfDay < phase.from || timeOfDay >= phase.until) continue;
    return (serverTick * phase.hold) % phase.cycle < phase.hold;
  }
  return false;
};

ServerEvents.tick((e) => {
  const { server } = e;
  const overworld = server.overworld();
  const dayTime = Number(overworld.dayTime());
  if (!sunlitShouldHoldTime(Number(server.getTickCount()), dayTime % 24000)) return;
  if (!overworld.getGameRules().getBoolean($SunlitGameRules.RULE_DAYLIGHT)) return;
  const heldTime = dayTime - 1;
  overworld.setDayTime(heldTime);
  // getGameTime() does not resolve on the level in Rhino, so it is read from the level data.
  // Clients predict +1 per tick and vanilla only resyncs once a second, so without this
  // the sun would visibly step back every second.
  server.getPlayerList().broadcastAll(new $SunlitSetTimePacket(overworld.getLevelData().getGameTime(), heldTime, true));
});
