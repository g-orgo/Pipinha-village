console.info("[SOCIETY] surfaceHostileSpawns.js loaded");

// Hostile mobs only spawn in caves or in other dimensions.
// In the overworld every MONSTER category mob (vanilla or modded) is cancelled at or
// above the cave line (y 50, drowned y 30, same lines as config/incontrol/spawn.json)
// for the spawn reasons in SURFACE_HOSTILE_BLOCKED_TYPES. NeoForge fires
// FinalizeSpawnEvent for natural spawns, pillager patrols, phantoms, zombie sieges,
// structure mobs (outposts, witch huts, mansions, monuments, ocean ruins, templates)
// and spawner blocks, and a cancelled mob never joins the level (NeoForgeEventHandler
// at runtime, WorldGenRegion during chunk generation).
// Kept: raid mobs (the player starts a raid on purpose), spawn eggs, commands,
// buckets, dispensers, conversions, mob summons (evoker vexes), trial spawners,
// and the bosses in SURFACE_HOSTILE_KEEP_TYPES.
// Drops of the mobs that no longer show up on the surface come from the town chests
// (pool "mob" and the rich chest of tools/pack_tools/towns/loot.py).
//
// SURFACE_HOSTILE_DEBUG: one "[surfacehostile]" line per minute in
// logs/kubejs/startup.log with what was blocked (mob/reason x count).
//
// Startup scripts share one scope: top level names carry the SURFACE_HOSTILE /
// surfaceHostile prefix, and functions only use var (Rhino 2101).

var SURFACE_HOSTILE_DEBUG = true;
var SURFACE_HOSTILE_DIMENSION = "minecraft:overworld";
var SURFACE_HOSTILE_CAVE_Y = 50;
var SURFACE_HOSTILE_CAVE_Y_BY_TYPE = {
  "minecraft:drowned": 30,
};
var SURFACE_HOSTILE_BLOCKED_TYPES = [
  "NATURAL",
  "CHUNK_GENERATION",
  "STRUCTURE",
  "PATROL",
  "SPAWNER",
  "REINFORCEMENT",
  "JOCKEY",
  "EVENT",
];
var SURFACE_HOSTILE_KEEP_TYPES = [
  "minecraft:wither",
  "minecraft:ender_dragon",
  "minecraft:elder_guardian",
  "minecraft:warden",
];
var SURFACE_HOSTILE_REGISTRY = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries").ENTITY_TYPE;
var SURFACE_HOSTILE_RL = Java.loadClass("net.minecraft.resources.ResourceLocation");
var surfaceHostileFailed = false;
var surfaceHostileDebugCounts = {};
var surfaceHostileDebugSince = 0;

// entity.getType() can come back as the Java EntityType or, through KubeJS, as the id
// string: both are turned into the EntityType here.
function surfaceHostileEntityType(entity) {
  var type = entity.getType();
  if (type != null && typeof type.getCategory === "function") return type;
  return SURFACE_HOSTILE_REGISTRY.get(SURFACE_HOSTILE_RL.parse(String(type)));
}

function surfaceHostileDebug(id, reason) {
  if (!SURFACE_HOSTILE_DEBUG) return;
  try {
    var key = id + "/" + reason;
    var now = Date.now();
    var parts = [];
    surfaceHostileDebugCounts[key] = (surfaceHostileDebugCounts[key] || 0) + 1;
    if (surfaceHostileDebugSince === 0) surfaceHostileDebugSince = now;
    if (now - surfaceHostileDebugSince < 60000) return;
    Object.keys(surfaceHostileDebugCounts).forEach((k) => parts.push(k + " x" + surfaceHostileDebugCounts[k]));
    console.info("[surfacehostile] blocked on the surface in the last minute: " + parts.join(", "));
    surfaceHostileDebugCounts = {};
    surfaceHostileDebugSince = now;
  } catch (err) {
    console.error("[surfacehostile] debug log failed: " + err);
  }
}

NativeEvents.onEvent(Java.loadClass("net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent"), (e) => {
  if (surfaceHostileFailed) return;
  try {
    var reason = String(e.getSpawnType().name());
    var entity;
    var entityType;
    var id;
    var caveY;
    if (SURFACE_HOSTILE_BLOCKED_TYPES.indexOf(reason) < 0) return;
    if (String(e.getLevel().getLevel().dimension().location()) !== SURFACE_HOSTILE_DIMENSION) return;
    entity = e.getEntity();
    entityType = surfaceHostileEntityType(entity);
    if (String(entityType.getCategory().name()) !== "MONSTER") return;
    id = String(SURFACE_HOSTILE_REGISTRY.getKey(entityType));
    if (SURFACE_HOSTILE_KEEP_TYPES.indexOf(id) >= 0) return;
    caveY = SURFACE_HOSTILE_CAVE_Y_BY_TYPE[id];
    if (caveY === undefined) caveY = SURFACE_HOSTILE_CAVE_Y;
    if (Number(e.getY()) < caveY) return;
    // Raid waves spawn as EVENT with the raid already set; zombie sieges have no raid.
    if (reason === "EVENT" && typeof entity.getCurrentRaid === "function" && entity.getCurrentRaid() != null) return;
    e.setSpawnCancelled(true);
    surfaceHostileDebug(id, reason);
  } catch (err) {
    surfaceHostileFailed = true;
    console.error("[surfacehostile] spawn check failed: " + err);
  }
});
