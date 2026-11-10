console.info("[SOCIETY] husbandryTwins.js loaded");

// Husbandry Specialty perk (rancher, cook): a bred animal may give one extra baby.
// Hooked on Forge BabyEntitySpawnEvent; the extra baby is a copy of the child.
global.handleSpecialtyTwins = (e) => {
  try {
    let parent = e.getParentA();
    let child = e.getChild();
    if (!parent || !child || parent.level.isClientSide()) return;
    if (!global.checkEntityTag(parent, "society:husbandry_animal")) return;
    // The Miracle Potion sets InLove without a love cause, so fall back to the
    // nearest player.
    let player = e.getCausedByPlayer();
    if (!player) player = parent.level.getNearestPlayer(parent, 16);
    if (!player || player.isFake()) return;
    if (!global.rollSpecialty(player, "husbandry", "twins")) return;
    let level = child.level;
    let extra = level.createEntity(String(child.type));
    extra.x = child.x;
    extra.y = child.y;
    extra.z = child.z;
    extra.setAge(-24000);
    extra.spawn();
    player.tell(Text.translatable("society.specialty.twins").green());
  } catch (err) {
    console.error(`[specialty] twins perk failed: ${err}`);
  }
};

ForgeEvents.onEvent(
  "net.minecraftforge.event.entity.living.BabyEntitySpawnEvent",
  (e) => {
    global.handleSpecialtyTwins(e);
  }
);
