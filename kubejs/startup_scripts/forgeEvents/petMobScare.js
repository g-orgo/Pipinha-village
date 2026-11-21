console.info("[SOCIETY] petMobScare.js loaded");

// Pets scare their natural enemies away, with a radius that grows with affection.
// Vanilla: wolves scare skeletons and cats scare creepers within 6 blocks.
// Pack: every dog of the pack scares skeletons (wither skeletons, strays and bogged
// included) and cats scare creepers, within 6 blocks plus 2 blocks per heart from
// 5 hearts on: 8 blocks at 5 hearts, 18 blocks at 10 hearts.
// It is the same AvoidEntityGoal vanilla uses, added to each skeleton and creeper
// when it joins a server level. The quest chapter "Companheiros" documents these numbers.
(function () {
  const $AvoidEntityGoal = Java.loadClass("net.minecraft.world.entity.ai.goal.AvoidEntityGoal");
  const $EntitySelector = Java.loadClass("net.minecraft.world.entity.EntitySelector");
  const $LivingEntity = Java.loadClass("net.minecraft.world.entity.LivingEntity");
  const $AbstractSkeleton = Java.loadClass("net.minecraft.world.entity.monster.AbstractSkeleton");
  const $Creeper = Java.loadClass("net.minecraft.world.entity.monster.Creeper");
  const $WeakHashMap = Java.loadClass("java.util.WeakHashMap");
  const $JoinEvent = Java.loadClass("net.neoforged.neoforge.event.entity.EntityJoinLevelEvent");

  const BASE_RADIUS = 6;
  const PER_HEART = 2;
  const START_HEARTS = 5;
  const MAX_HEARTS = 10;
  const MAX_RADIUS = BASE_RADIUS + PER_HEART * (MAX_HEARTS - START_HEARTS + 1);
  // Same priority and speeds as the vanilla avoid goals of skeletons and creepers.
  const GOAL_PRIORITY = 3;
  const WALK_SPEED = 1.0;
  const SPRINT_SPEED = 1.2;

  const DOG_TYPES = ["minecraft:wolf", "quark:shiba", "quark:foxhound", "wildernature:dog"];
  const CAT_TYPES = ["minecraft:cat"];

  // Mobs that already got the goal in this session; weak keys, so unloaded mobs are dropped.
  const handled = new $WeakHashMap();
  let joinFailed = false;
  let predicateErrorLogged = false;

  // 6 blocks below 5 hearts, then +2 per heart: 8 at 5 hearts, 18 at 10 hearts.
  global.petScareRadius = (hearts) => {
    if (hearts < START_HEARTS) return BASE_RADIUS;
    if (hearts > MAX_HEARTS) hearts = MAX_HEARTS;
    return BASE_RADIUS + PER_HEART * (hearts - START_HEARTS + 1);
  };

  const heartsOf = (pet) => {
    let affection = pet.persistentData.getInt("affection");
    let hearts = Math.floor((affection > 1000 ? 1000 : affection) / 100);
    return hearts < 0 ? 0 : hearts;
  };

  // Predicate on the candidate pet: right species, alive, and within its affection radius of the mob.
  const scaredBy = (mob, types) => (pet) => {
    let radius = BASE_RADIUS;
    try {
      if (!pet || !pet.isAlive()) return false;
      if (types.indexOf(String(pet.type)) === -1) return false;
      radius = global.petScareRadius(heartsOf(pet));
      return pet.distanceTo(mob) <= radius;
    } catch (err) {
      if (!predicateErrorLogged) {
        predicateErrorLogged = true;
        console.error("[SOCIETY] petMobScare predicate: " + err);
      }
      return false;
    }
  };

  NativeEvents.onEvent($JoinEvent, (e) => {
    let level = null;
    let entity = null;
    let types = null;
    if (joinFailed) return;
    try {
      level = e.getLevel();
      if (level.isClientSide()) return;
      entity = e.getEntity();
      if (entity instanceof $AbstractSkeleton) types = DOG_TYPES;
      else if (entity instanceof $Creeper) types = CAT_TYPES;
      else return;
      if (handled.containsKey(entity)) return;
      handled.put(entity, true);
      entity.goalSelector.addGoal(
        GOAL_PRIORITY,
        new $AvoidEntityGoal(
          entity,
          $LivingEntity,
          scaredBy(entity, types),
          MAX_RADIUS,
          WALK_SPEED,
          SPRINT_SPEED,
          $EntitySelector.NO_CREATIVE_OR_SPECTATOR
        )
      );
    } catch (err) {
      joinFailed = true;
      console.error("[SOCIETY] petMobScare: could not add the avoid goal, feature off this session: " + err);
    }
  });
})();
