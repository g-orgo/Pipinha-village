// Sunlit: stretches the daylight part of the cycle without changing the 24000-tick day.
// HOLD_TICKS out of every HOLD_CYCLE server ticks the clock is held back by one tick
// (9 of 25 = 0.64x speed), spread evenly so two holds are never consecutive.
// Daylight (ticks 0-12000) then lasts 1300 + 10700 / 0.64 = ~18019 server ticks, about 15 min.
// Day machines, the shipping bin and the player day counter run on dayTime windows sized
// to their tick rate, all ending at or before tick 1200. Inside a window a slower clock
// would make them run twice, so the slowdown only starts after the last one.
const $SunlitSetTimePacket = Java.loadClass("net.minecraft.network.protocol.game.ClientboundSetTimePacket");
const $SunlitGameRules = Java.loadClass("net.minecraft.world.level.GameRules");

const HOLD_TICKS = 9;
const HOLD_CYCLE = 25;
const SLOW_FROM_TICK = 1300;
const SLOW_UNTIL_TICK = 12000;

console.info("[Sunlit] sunlitLongerDay.js loaded");

ServerEvents.tick((e) => {
  const { server } = e;
  if ((server.getTickCount() * HOLD_TICKS) % HOLD_CYCLE >= HOLD_TICKS) return;
  const overworld = server.overworld();
  const dayTime = Number(overworld.dayTime());
  const timeOfDay = dayTime % 24000;
  if (timeOfDay < SLOW_FROM_TICK || timeOfDay >= SLOW_UNTIL_TICK) return;
  if (!overworld.getGameRules().getBoolean($SunlitGameRules.RULE_DAYLIGHT)) return;
  const heldTime = dayTime - 1;
  overworld.setDayTime(heldTime);
  // getGameTime() does not resolve on the level in Rhino, so it is read from the level data.
  // Clients predict +1 per tick and vanilla only resyncs once a second, so without this
  // the sun would visibly step back every second.
  server.getPlayerList().broadcastAll(new $SunlitSetTimePacket(overworld.getLevelData().getGameTime(), heldTime, true));
});
