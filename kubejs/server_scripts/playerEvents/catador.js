console.info("[SOCIETY] catador.js loaded");

// Catador tree (society:catador), shared by every profession.
// XP:
//   - first open of each loot container (Lootr stat lootr:looted_stat), given by
//     the puffish increase_stat source in categories/catador/experience.json;
//   - stepping into a chunk nobody has spent time around yet (CATADOR_CHUNK_XP);
//   - entering a structure the player had never been in (CATADOR_STRUCTURE_XP).
// A chunk counts as new while its inhabited time (ticks with a player within
// 128 blocks, kept by vanilla in the chunk data) is below
// CATADOR_NEW_CHUNK_TICKS. Rewarding it raises the inhabited time to that
// value, so each chunk pays once for the whole world. Discovered structures are
// kept per player in persistentData (CATADOR_STRUCTURES_KEY).
// Perks (stages from the tree nodes):
//   catador_rummage_<1..3>   chance of an extra portion of one item when a loot
//                            container is opened for the first time;
//   catador_keen_nose_<1|2>  coins for each new structure, one bevel per node.

const CATADOR_TREE = "catador";
const CATADOR_CHECK_TICKS = 40;
const CATADOR_NEW_CHUNK_TICKS = 2400;
const CATADOR_CHUNK_XP = 3;
const CATADOR_STRUCTURE_XP = 50;
const CATADOR_RUMMAGE_CHANCE = [0.2, 0.35, 0.5];
const CATADOR_KEEN_NOSE_COIN = "numismatics:bevel";
const $CatadorResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
const CATADOR_LOOTED_STAT = new $CatadorResourceLocation("lootr", "looted_stat");
const CATADOR_LOOTED_KEY = "catadorLooted";
const CATADOR_STRUCTURES_KEY = "catadorStructures";
const CATADOR_PLAYER_SLOTS = 36;
const $CatadorRegistries = Java.loadClass("net.minecraft.core.registries.Registries");

const catadorRummageChance = (player) => {
  for (let tier = CATADOR_RUMMAGE_CHANCE.length; tier > 0; tier--) {
    if (player.stages.has(`catador_rummage_${tier}`)) return CATADOR_RUMMAGE_CHANCE[tier - 1];
  }
  return 0;
};

// The custom stat registry looks values up by identity, so a new ResourceLocation equal to the
// Lootr id has no key (NPE in Stat.buildName). Use the instance Lootr registered.
const $CatadorBuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
const catadorLootedStatId = () => $CatadorBuiltInRegistries.CUSTOM_STAT.get(CATADOR_LOOTED_STAT);

const catadorLootedCount = (player) => {
  let id = catadorLootedStatId();
  return id ? player.stats.get(id) : 0;
};

// Extra portion: copies half (rounded up) of a random stack of the container
// into an empty slot of it, or into the player's inventory when it is full.
const catadorRummage = (player, menu) => {
  let size = menu.slots.size() - CATADOR_PLAYER_SLOTS;
  if (size <= 0) return;
  let filled = [];
  let empty = [];
  for (let i = 0; i < size; i++) {
    let slot = menu.slots.get(i);
    if (slot.hasItem()) filled.push(slot);
    else empty.push(slot);
  }
  if (filled.length === 0) return;
  let source = filled[Math.floor(Math.random() * filled.length)].getItem();
  let bonus = source.copy();
  bonus.setCount(Math.max(1, Math.ceil(source.getCount() / 2)));
  let target = empty.find((slot) => slot.mayPlace(bonus));
  if (target) target.set(bonus);
  else player.give(bonus);
  menu.broadcastChanges();
};

PlayerEvents.loggedIn((e) => {
  let player = e.player;
  if (!player || player.isFake()) return;
  // Baseline so loot opened before this tree existed does not count.
  if (!player.persistentData.contains(CATADOR_LOOTED_KEY)) {
    player.persistentData.putInt(CATADOR_LOOTED_KEY, catadorLootedCount(player));
  }
});

// Lootr raises the stat before it opens the menu, so a higher value here means
// this container was just looted for the first time by this player.
PlayerEvents.inventoryOpened((e) => {
  let player = e.player;
  if (!player || player.isFake()) return;
  try {
    let looted = catadorLootedCount(player);
    let known = player.persistentData.getInt(CATADOR_LOOTED_KEY);
    if (looted <= known) return;
    player.persistentData.putInt(CATADOR_LOOTED_KEY, looted);
    let chance = catadorRummageChance(player);
    if (chance > 0 && Math.random() < chance) catadorRummage(player, e.inventoryContainer);
  } catch (err) {
    console.error(`[catador] rummage failed: ${err}`);
  }
});

const catadorCheckChunk = (server, player, level, pos) => {
  let chunk = level.getChunkAt(pos);
  if (chunk.getInhabitedTime() >= CATADOR_NEW_CHUNK_TICKS) return;
  chunk.setInhabitedTime(CATADOR_NEW_CHUNK_TICKS);
  chunk.setUnsaved(true);
  global.giveExperience(server, player, CATADOR_TREE, CATADOR_CHUNK_XP, true);
};

const catadorCheckStructures = (server, player, level, pos) => {
  let manager = level.structureManager();
  let found = manager.getAllStructuresAt(pos);
  if (found.isEmpty()) return;
  let registry = level.registryAccess().registryOrThrow($CatadorRegistries.STRUCTURE);
  let known = player.persistentData.getCompound(CATADOR_STRUCTURES_KEY);
  let added = 0;
  let it = found.keySet().iterator();
  while (it.hasNext()) {
    let structure = it.next();
    let start = manager.getStructureWithPieceAt(pos, structure);
    if (!start || !start.isValid()) continue;
    let chunkPos = start.getChunkPos();
    let key = `${level.dimension().location()}|${registry.getKey(structure)}|${chunkPos.x},${chunkPos.z}`;
    if (known.contains(key)) continue;
    known.putBoolean(key, true);
    added++;
  }
  if (added === 0) return;
  player.persistentData.put(CATADOR_STRUCTURES_KEY, known);
  global.giveExperience(server, player, CATADOR_TREE, CATADOR_STRUCTURE_XP * added, true);
  let coins = 0;
  if (player.stages.has("catador_keen_nose_1")) coins++;
  if (player.stages.has("catador_keen_nose_2")) coins++;
  if (coins > 0) player.give(Item.of(CATADOR_KEEN_NOSE_COIN, coins * added));
};

PlayerEvents.tick((e) => {
  let player = e.player;
  if (!player || player.isFake() || player.isSpectator()) return;
  if (player.age % CATADOR_CHECK_TICKS != 0) return;
  let server = e.server;
  let level = player.level;
  let pos = player.blockPosition();
  try {
    catadorCheckChunk(server, player, level, pos);
    catadorCheckStructures(server, player, level, pos);
  } catch (err) {
    console.error(`[catador] exploration check failed: ${err}`);
  }
});
