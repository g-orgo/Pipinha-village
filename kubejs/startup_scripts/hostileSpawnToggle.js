// Hostile mob spawn toggle, next to the difficulty button.
//
// The difficulty is always HARD and can't be changed (worldCreationLock.js), so
// the only choice left to the player is whether hostile mobs spawn. A 20x20
// toggle sits right of the difficulty button in two places:
// - Options screen inside a singleplayer world: flips the world setting now.
// - Create world screen (Game tab): picked before the world exists, written to
//   the new world on its first load (server_scripts/hostileSpawnToggle.js).
//
// The setting lives in server.persistentData (HOSTILE_TOGGLE_KEY, missing =
// mobs spawn). When it is on, every MONSTER category mob is cancelled for the
// spawn reasons in HOSTILE_TOGGLE_BLOCKED_TYPES (natural, chunk generation,
// spawners, structures, patrols, reinforcements, jockeys, summons). Spawn eggs,
// commands, buckets, dispensers, conversions and raids stay allowed.
// Turning it on also clears the hostile mobs already in the world, like Peaceful:
// the loaded ones at once, the ones in unloaded chunks when those chunks load.
// Named, leashed and persistent mobs (raids included) and bosses are kept.
//
// The button texture follows the active resource packs: with Excalibur selected
// it uses hostile_spawns_excalibur.png, otherwise the vanilla styled
// hostile_spawns.png (both from sunlit_tools/gen_hostile_toggle_icons.py).
//
// Inside functions only `var` (Rhino "redeclaration of var" bug, see
// replayViewerButton.js). Top level names carry the HOSTILE_TOGGLE / hostileToggle
// prefix because startup scripts share one scope.

var HOSTILE_TOGGLE_KEY = "sunlitHostileSpawnsOff";
var HOSTILE_TOGGLE_BLOCKED_TYPES = [
  "NATURAL",
  "CHUNK_GENERATION",
  "SPAWNER",
  "STRUCTURE",
  "PATROL",
  "REINFORCEMENT",
  "JOCKEY",
  "MOB_SUMMONED",
];
var HOSTILE_TOGGLE_KEEP_TYPES = [
  "minecraft:wither",
  "minecraft:ender_dragon",
  "minecraft:elder_guardian",
  "minecraft:warden",
];
var HOSTILE_TOGGLE_OPTIONS_SCREEN = "net.minecraft.client.gui.screens.OptionsScreen";
var HOSTILE_TOGGLE_CREATE_SCREEN = "net.minecraft.client.gui.screens.worldselection.CreateWorldScreen";
var HOSTILE_TOGGLE_LOCK_BUTTON = "net.minecraft.client.gui.components.LockIconButton";
var HOSTILE_TOGGLE_DIFFICULTY = "net.minecraft.world.Difficulty";
var HOSTILE_TOGGLE_SIZE = 20;
var hostileToggleSpawnFailed = false;
var hostileToggleUiFailed = false;
var hostileToggleJoinFailed = false;
var hostileToggleCreate = null;

global.isHostileSpawnsOff = function (server) {
  return server != null && server.persistentData.getBoolean(HOSTILE_TOGGLE_KEY);
};

// A hostile mob that goes away when spawns are off: MONSTER category mob, not a boss,
// not named, leashed or persistent (picked up items, raid members).
function hostileToggleRemovable(entity) {
  if (entity == null || String(entity.getType().getCategory().name()) !== "MONSTER") return false;
  var id = String(Java.loadClass("net.minecraft.world.entity.EntityType").getKey(entity.getType()));
  if (HOSTILE_TOGGLE_KEEP_TYPES.indexOf(id) >= 0) return false;
  if (typeof entity.isPersistenceRequired !== "function") return false;
  if (entity.isPersistenceRequired() || entity.requiresCustomPersistence()) return false;
  if (entity.hasCustomName() || entity.isLeashed()) return false;
  return true;
}

global.removeHostileMobs = function (server) {
  var doomed = [];
  server.getAllLevels().forEach((level) => {
    level.getAllEntities().forEach((entity) => {
      if (hostileToggleRemovable(entity)) doomed.push(entity);
    });
  });
  doomed.forEach((entity) => entity.discard());
  console.info("[hostileSpawnToggle] removed " + doomed.length + " hostile mobs");
};

global.setHostileSpawnsOff = function (server, off) {
  server.persistentData.putBoolean(HOSTILE_TOGGLE_KEY, off);
  console.info("[hostileSpawnToggle] hostile spawns " + (off ? "OFF" : "ON"));
  if (!off) return;
  try {
    global.removeHostileMobs(server);
  } catch (err) {
    console.error("[hostileSpawnToggle] removing hostile mobs failed: " + err);
  }
};

// Choice made on the create world screen, applied by the server script on the
// new world's first load. "none" = nothing pending. Never store null: global is a Java map and
// reading a key whose value is null throws in KubeJS's Rhino (NativeJavaMap.get).
global.pendingHostileSpawnsOff = "none";

ForgeEvents.onEvent("net.minecraftforge.event.entity.living.MobSpawnEvent$FinalizeSpawn", (e) => {
  if (hostileToggleSpawnFailed) return;
  try {
    var entity = e.getEntity();
    if (String(entity.getType().getCategory().name()) !== "MONSTER") return;
    if (HOSTILE_TOGGLE_BLOCKED_TYPES.indexOf(String(e.getSpawnType().name())) < 0) return;
    if (global.isHostileSpawnsOff(entity.getServer())) e.setSpawnCancelled(true);
  } catch (err) {
    hostileToggleSpawnFailed = true;
    console.error("[hostileSpawnToggle] spawn check failed: " + err);
  }
});

// Hostile mobs saved in chunks that were unloaded when spawns went off: dropped as they load.
ForgeEvents.onEvent("net.minecraftforge.event.entity.EntityJoinLevelEvent", (e) => {
  if (hostileToggleJoinFailed) return;
  try {
    if (!e.loadedFromDisk()) return;
    var level = e.getLevel();
    if (level.isClientSide()) return;
    if (!global.isHostileSpawnsOff(level.getServer())) return;
    if (hostileToggleRemovable(e.getEntity())) e.setCanceled(true);
  } catch (err) {
    hostileToggleJoinFailed = true;
    console.error("[hostileSpawnToggle] loaded mob check failed: " + err);
  }
});

function hostileToggleClient() {
  return Java.loadClass("net.minecraft.client.Minecraft").getInstance();
}

function hostileToggleTexture() {
  var ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  var excalibur = false;
  hostileToggleClient().getResourcePackRepository().getSelectedIds().forEach((id) => {
    if (String(id).toLowerCase().indexOf("excalibur_v1") >= 0) excalibur = true;
  });
  return new ResourceLocation("kubejs", excalibur ? "textures/gui/hostile_spawns_excalibur.png" : "textures/gui/hostile_spawns.png");
}

function hostileToggleButton(texture, u, key, onPress) {
  var Tooltip = Java.loadClass("net.minecraft.client.gui.components.Tooltip");
  var ImageButton = Java.loadClass("net.minecraft.client.gui.components.ImageButton");
  var label = Component.translatable(key);
  var button = new ImageButton(0, 0, HOSTILE_TOGGLE_SIZE, HOSTILE_TOGGLE_SIZE, u, 0, HOSTILE_TOGGLE_SIZE, texture, 64, 64, onPress, label);
  button.setTooltip(Tooltip.create(label));
  return button;
}

// Two image buttons on the same spot, only the one matching the state is visible.
function hostileTogglePair(event, isOff, onChange) {
  var texture = hostileToggleTexture();
  var pair = { on: null, off: null };
  pair.show = (off) => {
    pair.on.visible = !off;
    pair.off.visible = off;
  };
  pair.place = (x, y) => {
    pair.on.setPosition(x, y);
    pair.off.setPosition(x, y);
  };
  pair.on = hostileToggleButton(texture, 0, "sunlit.hostile_spawns.on", () => {
    pair.show(true);
    onChange(true);
  });
  pair.off = hostileToggleButton(texture, HOSTILE_TOGGLE_SIZE, "sunlit.hostile_spawns.off", () => {
    pair.show(false);
    onChange(false);
  });
  event.addListener(pair.on);
  event.addListener(pair.off);
  pair.show(isOff);
  return pair;
}

function hostileToggleIsDifficulty(widget) {
  try {
    if (String(widget.getClass().getName()).indexOf("CycleButton") < 0) return false;
    var value = widget.getValue();
    return value != null && String(value.getClass().getName()) === HOSTILE_TOGGLE_DIFFICULTY;
  } catch (err) {
    return false;
  }
}

function hostileToggleOptionsInit(event, screen) {
  var client = hostileToggleClient();
  var server = client.getSingleplayerServer();
  if (server == null || client.level == null) return;
  var difficulty = null;
  var lock = null;
  screen.children().forEach((widget) => {
    if (hostileToggleIsDifficulty(widget)) difficulty = widget;
    else if (String(widget.getClass().getName()) === HOSTILE_TOGGLE_LOCK_BUTTON) lock = widget;
  });
  if (difficulty == null) return;

  // Difficulty is fixed: the button and the lock stay greyed out, the lock shown closed.
  difficulty.active = false;
  difficulty.setWidth(difficulty.getWidth() - HOSTILE_TOGGLE_SIZE);
  var x = difficulty.getX() + difficulty.getWidth();
  if (lock != null) {
    lock.setLocked(true);
    lock.active = false;
    lock.setX(x);
    x += lock.getWidth();
  }
  var pair = hostileTogglePair(event, global.isHostileSpawnsOff(server), (off) => {
    server.execute(() => global.setHostileSpawnsOff(server, off));
  });
  pair.place(x, difficulty.getY());
}

function hostileToggleCreateInit(event, screen) {
  if (hostileToggleCreate == null || hostileToggleCreate.screen !== screen) {
    global.pendingHostileSpawnsOff = false;
  }
  var pair = hostileTogglePair(event, global.pendingHostileSpawnsOff === true, (off) => {
    global.pendingHostileSpawnsOff = off;
  });
  pair.on.visible = false;
  pair.off.visible = false;
  hostileToggleCreate = { screen: screen, pair: pair };
}

// Create world tabs add and remove their widgets, so the toggle follows the
// difficulty button every frame: shown and placed only while the Game tab is open.
function hostileToggleCreateRender(screen) {
  if (hostileToggleCreate == null || hostileToggleCreate.screen !== screen) return;
  var difficulty = null;
  var reference = null;
  screen.children().forEach((widget) => {
    if (hostileToggleIsDifficulty(widget)) difficulty = widget;
    else if (String(widget.getClass().getName()).indexOf("CycleButton") >= 0 && reference == null) reference = widget;
  });
  var pair = hostileToggleCreate.pair;
  if (difficulty == null || reference == null) {
    pair.on.visible = false;
    pair.off.visible = false;
    return;
  }
  difficulty.active = false;
  var width = reference.getWidth() - HOSTILE_TOGGLE_SIZE;
  if (difficulty.getWidth() !== width) difficulty.setWidth(width);
  if (difficulty.getX() !== reference.getX()) difficulty.setX(reference.getX());
  pair.place(reference.getX() + width, difficulty.getY());
  pair.show(global.pendingHostileSpawnsOff === true);
}

if (Platform.isClientEnvironment()) {
  ForgeEvents.onEvent("net.minecraftforge.client.event.ScreenEvent$Init$Post", (e) => {
    if (hostileToggleUiFailed) return;
    try {
      var screen = e.getScreen();
      var name = String(screen.getClass().getName());
      if (name === HOSTILE_TOGGLE_OPTIONS_SCREEN) hostileToggleOptionsInit(e, screen);
      else if (name === HOSTILE_TOGGLE_CREATE_SCREEN) hostileToggleCreateInit(e, screen);
    } catch (err) {
      hostileToggleUiFailed = true;
      console.error("[hostileSpawnToggle] screen init failed: " + err);
    }
  });
  ForgeEvents.onEvent("net.minecraftforge.client.event.ScreenEvent$Render$Pre", (e) => {
    if (hostileToggleUiFailed) return;
    try {
      hostileToggleCreateRender(e.getScreen());
    } catch (err) {
      hostileToggleUiFailed = true;
      console.error("[hostileSpawnToggle] create world screen update failed: " + err);
    }
  });
}
