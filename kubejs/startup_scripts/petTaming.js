console.info("[SOCIETY] petTaming.js loaded");

// Taming by petting. Farm animals, dogs, cats and small critters (#society:tame_by_petting, written by
// tools/pack_tools/pet_guide/build_pet_guide.py from content.json "tame_by_petting") are tamed by one
// empty-hand right click from a real player. Their conventional taming is off: they left the
// Redomesticate item definitions, its built-in ones point to the empty #society:no_taming tag, and the
// taming items of a wild TamableAnimal (bone, fish, seeds, mod items) or ocelot (fish) are refused here.
// Mounts and big animals are not in the tag and keep their own taming.
// Only taming lives here; the daily petting (affection, hearts) stays in global.handleHusbandryBase.
// Caller: forgeEvents/petFirstInteraction.js, before the daily petting, so the same click tames and pets.
(function () {
  const TAG = "society:tame_by_petting";
  const DEBUG = true;
  const TAMABLE_ANIMAL = Java.loadClass("net.minecraft.world.entity.TamableAnimal");
  const OCELOT = Java.loadClass("net.minecraft.world.entity.animal.Ocelot");
  const FOX = Java.loadClass("net.minecraft.world.entity.animal.Fox");
  // Redomesticate makes every Mob an ITameableEntity/ICommandableMob (mixin) and reads the vanilla owner too.
  const TAMEABLE_UTILS = Java.loadClass("com.evandev.redomesticate.util.TameableUtils");
  const UNIVERSAL_AI = Java.loadClass("com.evandev.redomesticate.content.entity.ai.UniversalAIManager");
  // Redomesticate PetCommand ids: 0 WANDER, 1 SIT, 2 FOLLOW. Its own item taming sets WANDER.
  const COMMAND_WANDER = 0;
  // Items still usable on a wild TamableAnimal of the tag (husbandry tools, lead, name tag); any
  // other item (food, bone, seeds, a mod's taming item) would be a taming attempt.
  const FREE_ITEMS = ["minecraft:lead", "minecraft:name_tag", "minecraft:shears", "minecraft:brush"];
  const FREE_PATTERN = /^society:|spawn_egg$|bucket|lasso/;
  let errorLogged = false;

  const isEmptyHand = (item) => !item || item.isEmpty();

  // A mob of the tag that has no owner yet.
  const isWild = (target) => global.checkEntityTag(target, TAG) && !TAMEABLE_UTILS.isTamed(target);

  // True when the held item would tame the mob the conventional way.
  const isTamingItem = (target, item) => {
    let id = String(item.id);
    if (target instanceof TAMABLE_ANIMAL) return FREE_ITEMS.indexOf(id) === -1 && !FREE_PATTERN.test(id);
    if (target instanceof OCELOT) return target.isFood(item);
    return false;
  };

  // Vanilla owner for TamableAnimal (wolf, cat, parrot, mod pets: same as the bone or fish would do,
  // advancement included); the Redomesticate universal owner for any other Mob, with the same steps
  // as its item taming (InteractionHandler), so both ways end in the same state.
  const tame = (player, target, level) => {
    if (target instanceof TAMABLE_ANIMAL) {
      target.tame(player);
    } else {
      target["redomesticate$setTame"](true);
      target["redomesticate$setTameOwnerUUID"](player.getUUID());
      target["redomesticate$setCommand"](COMMAND_WANDER);
      if (target instanceof FOX) target.setSitting(false);
      target.setPersistenceRequired();
      UNIVERSAL_AI.applyPetAI(target);
    }
    target.setTarget(null);
    target.setLastHurtByMob(null);
    target.getNavigation().stop();
    level.spawnParticles("minecraft:heart", true, target.x, target.y + target.getBbHeight(), target.z, 0.4, 0.3, 0.4, 7, 0.1);
  };

  // Every animal of the pack (vanilla and mods) can be petted and shows the hearts HUD: any
  // Animal, WaterAnimal (fish, squid, dolphin) or AmbientCreature (bat). One that is not a
  // husbandry animal is handled like a pet (no feeding, fixed mood).
  const ANIMAL = Java.loadClass("net.minecraft.world.entity.animal.Animal");
  const WATER_ANIMAL = Java.loadClass("net.minecraft.world.entity.animal.WaterAnimal");
  const AMBIENT_CREATURE = Java.loadClass("net.minecraft.world.entity.ambient.AmbientCreature");
  const isTamedSafe = (target) => {
    try {
      return !!TAMEABLE_UTILS.isTamed(target);
    } catch (err) {
      return false;
    }
  };
  const isPackAnimal = (target) =>
    target instanceof ANIMAL || target instanceof WATER_ANIMAL || target instanceof AMBIENT_CREATURE;
  global.isTamedAnimal = isTamedSafe;
  global.isSocietyPet = (target) =>
    global.checkEntityTag(target, "society:pet_animal") ||
    (!global.checkEntityTag(target, "society:husbandry_animal") && (isTamedSafe(target) || isPackAnimal(target)));
  global.isPettableAnimal = (target) =>
    global.checkEntityTag(target, "society:husbandry_animal") || global.isSocietyPet(target);

  // Server side only. Returns "tamed" (the click tamed the mob), "refused" (a conventional taming
  // item was used: the click must be cancelled) or "none" (not a wild mob of the tag, go on).
  global.petTaming = {
    tag: TAG,
    isWild: isWild,
    onClick: (player, target, hand, item, level) => {
      let empty = false;
      try {
        if (!isWild(target)) return "none";
        empty = isEmptyHand(item);
        if (!empty && isTamingItem(target, item)) {
          if (!player.isFake()) player.setStatusMessage(Text.translatable("society.husbandry.tame_by_petting_hint").gold());
          if (DEBUG) console.info(`[SOCIETY] pet-tame refused: target=${target.type} hand=${hand} item=${item.id}`);
          return "refused";
        }
        if (!empty || String(hand) !== "MAIN_HAND" || player.isFake()) return "none";
        if (typeof target.isAngry === "function" && target.isAngry()) return "none";
        tame(player, target, level);
        player.setStatusMessage(Text.translatable("society.husbandry.tamed_by_petting", target.getDisplayName()).green());
        if (DEBUG) console.info(`[SOCIETY] pet-tame: player=${player.username} target=${target.type} tamed=${TAMEABLE_UTILS.isTamed(target)}`);
        return "tamed";
      } catch (err) {
        // A failure here must not block the daily petting that runs after it.
        if (!errorLogged) {
          errorLogged = true;
          console.error(`[SOCIETY] petTaming failed on ${target.type}: ${err}`);
        }
        return "none";
      }
    },
  };
})();
