console.info("[SOCIETY] dogFollowOwner.js loaded");

// Dogs in follow mode come along when their owner moves without walking: after a
// teleport (any method, including dimension changes) they are placed at the owner's
// feet. While the owner rides a vehicle (horse, boat, cart...) they disappear: they
// are saved into the owner's data and come back at the owner's feet on dismount. Driven every server tick by
// startup_scripts/dogFollowTick.js through global.sunlitDogFollowTick.
(function () {
  const $AABB = Java.loadClass("net.minecraft.world.phys.AABB");
  const $CompoundTag = Java.loadClass("net.minecraft.nbt.CompoundTag");
  const $ListTag = Java.loadClass("net.minecraft.nbt.ListTag");
  const $EntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
  const $RemovalReason = Java.loadClass("net.minecraft.world.entity.Entity$RemovalReason");

  // Owner data key holding the dogs hidden while riding (list of entity NBT).
  const HIDDEN_KEY = "sunlitHiddenDogs";
  // Tag type id of a compound inside a ListTag.
  const TAG_COMPOUND = 10;
  // Radius around the owner where following dogs are hidden on mount.
  const MOUNT_SEARCH = 48;

  // Blocks moved between two ticks that count as a teleport.
  const TELEPORT_DISTANCE = 16;
  // Search radius around the old position (teleport) or the owner (dismount).
  const TELEPORT_SEARCH = 48;
  const DISMOUNT_SEARCH = 96;
  // Dog types that can be put in follow mode.
  const DOG_TYPES = [
    "minecraft:wolf",
    "quark:shiba",
    "quark:foxhound",
    "wildernature:dog",
    "wildernature:red_wolf",
  ];
  // Domestication Innovation command value for follow.
  const COMMAND_FOLLOW = 2;

  // Per-player state keyed by UUID string: dimension, position, the Level object, riding flag.
  const states = {};
  let errorLogged = false;

  const logOnce = (error) => {
    if (errorLogged) return;
    errorLogged = true;
    console.error("[SOCIETY] dogFollowOwner: " + error);
  };

  const listSize = (list) => (typeof list.size === "function" ? list.size() : list.length);
  const listGet = (list, i) => (typeof list.get === "function" ? list.get(i) : list[i]);

  const eachPlayer = (server, fn) => {
    let players = server.players;
    let count = listSize(players);
    for (let i = 0; i < count; i++) fn(listGet(players, i));
  };

  // Plain multiplication: the exponent operator gives wrong results in KubeJS's Rhino.
  const square = (v) => v * v;
  const distance3 = (a, b) => Math.sqrt(square(a.x - b.x) + square(a.y - b.y) + square(a.z - b.z));

  const isFollowingDog = (dog, ownerUuid) => {
    if (DOG_TYPES.indexOf(String(dog.type)) === -1) return false;
    if (!dog.isAlive() || !dog.isTame()) return false;
    if (String(dog.getOwnerUUID()) !== ownerUuid) return false;
    if (dog.isOrderedToSit() || dog.isPassenger() || dog.isLeashed()) return false;
    if (typeof dog.getCommand === "function" && Number(dog.getCommand()) !== COMMAND_FOLLOW) return false;
    return true;
  };

  // Following dogs of one owner within a radius of a point, in the given level.
  const followingDogsNear = (level, point, radius, ownerUuid) => {
    let box = new $AABB(
      point.x - radius, point.y - radius, point.z - radius,
      point.x + radius, point.y + radius, point.z + radius
    );
    let found = [];
    let list = level.getEntitiesWithin(box);
    let count = listSize(list);
    for (let i = 0; i < count; i++) {
      let entity = listGet(list, i);
      if (isFollowingDog(entity, ownerUuid)) found.push(entity);
    }
    return found;
  };

  const moveDogsTo = (server, dogs, player, dim, pos) => {
    dogs.forEach((dog) => {
      server.runCommandSilent(
        `execute in ${dim} run tp ${String(dog.uuid)} ${pos.x} ${pos.y} ${pos.z}`
      );
    });
  };

  // Saves the following dogs near the owner into its data and removes them from the world.
  const hideDogs = (player, level, pos, ownerUuid) => {
    let dogs = followingDogsNear(level, pos, MOUNT_SEARCH, ownerUuid);
    if (dogs.length === 0) return;
    let data = player.persistentData;
    let list = data.contains(HIDDEN_KEY) ? data.getList(HIDDEN_KEY, TAG_COMPOUND) : new $ListTag();
    dogs.forEach((dog) => {
      let tag = new $CompoundTag();
      if (!dog.save(tag)) return;
      list.add(tag);
      dog.remove($RemovalReason.UNLOADED_WITH_PLAYER);
    });
    data.put(HIDDEN_KEY, list);
  };

  // Brings the hidden dogs back at the owner's feet, in the owner's current level.
  const restoreDogs = (player, level, pos) => {
    let data = player.persistentData;
    if (!data.contains(HIDDEN_KEY)) return;
    let list = data.getList(HIDDEN_KEY, TAG_COMPOUND);
    data.remove(HIDDEN_KEY);
    let count = listSize(list);
    for (let i = 0; i < count; i++) {
      let dog = $EntityType.loadEntityRecursive(list.getCompound(i), level, (entity) => {
        entity.moveTo(pos.x, pos.y, pos.z, entity.getYRot(), entity.getXRot());
        return entity;
      });
      if (dog) level.tryAddFreshEntityWithPassengers(dog);
    }
  };

  const tickPlayer = (server, player) => {
    let uuid = String(player.uuid);
    let level = player.level;
    let dim = String(level.dimension);
    let pos = { x: player.x, y: player.y, z: player.z };
    let riding = player.isPassenger();
    let state = states[uuid];
    if (state) {
      let teleported = state.dim !== dim || distance3(state, pos) > TELEPORT_DISTANCE;
      let mounted = !state.riding && riding;
      let dismounted = state.riding && !riding;
      if (teleported) {
        let dogs = followingDogsNear(state.level, state, TELEPORT_SEARCH, uuid);
        moveDogsTo(server, dogs, player, dim, pos);
      }
      if (mounted) {
        hideDogs(player, level, pos, uuid);
      } else if (dismounted) {
        restoreDogs(player, level, pos);
        let dogs = followingDogsNear(level, pos, DISMOUNT_SEARCH, uuid);
        moveDogsTo(server, dogs, player, dim, pos);
      }
    } else if (!riding) {
      // First tick after login: dogs left hidden by a session that ended mid-ride.
      restoreDogs(player, level, pos);
    }
    states[uuid] = { dim: dim, x: pos.x, y: pos.y, z: pos.z, riding: riding, level: level };
  };

  global.sunlitDogFollowTick = (server) => {
    try {
      eachPlayer(server, (player) => {
        try {
          if (!player.isAlive()) return;
          tickPlayer(server, player);
        } catch (error) {
          logOnce(error);
        }
      });
    } catch (error) {
      logOnce(error);
    }
  };

  PlayerEvents.loggedOut((e) => {
    delete states[String(e.player.uuid)];
  });
})();
