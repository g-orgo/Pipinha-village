NativeEvents.onEvent(Java.loadClass("net.neoforged.neoforge.event.entity.player.CanPlayerSleepEvent"), (e) => {
  global.handleSkullSleep(e);
});
global.handleSkullSleep = (e) => {
  const { entity } = e;
  if (!entity.isPlayer()) return;
  const level = entity.level;
  level.getServer().players.forEach((p) => {
    if (p.getLevel().dimension === "society:skull_cavern") {
      entity.tell(
        Text.translatable("society.skull_cavern.cannot_sleep", p.username).red()
      );
      // 1.21.1: CanPlayerSleepEvent is not cancellable; setProblem blocks the sleep
      e.setProblem(Java.loadClass("net.minecraft.world.entity.player.Player$BedSleepingProblem").OTHER_PROBLEM);
    }
  });
};
