console.info("[SOCIETY] specialtyFarming.js loaded");

// Farming Specialty perks: grape picking, farmland hydration tracking.
// Crop harvest perks live in professionLoot.js and havestHandling.js.
const $DewUtil = Java.loadClass("cool.bot.botslib.util.Util");

const TILLED_KEY = "sunlitTilledFarmland";
const TILLED_MAX = 512;

const GRAPE_BUSHES = {
  "vinery:red_grape_bush": "vinery:red_grape",
  "vinery:white_grape_bush": "vinery:white_grape",
  "vinery:savanna_grape_bush_red": "vinery:savanna_grapes_red",
  "vinery:savanna_grape_bush_white": "vinery:savanna_grapes_white",
  "vinery:taiga_grape_bush_red": "vinery:taiga_grapes_red",
  "vinery:taiga_grape_bush_white": "vinery:taiga_grapes_white",
  "vinery:jungle_grape_bush_red": "vinery:jungle_grapes_red",
  "vinery:jungle_grape_bush_white": "vinery:jungle_grapes_white",
  "nethervinery:crimson_grape_bush": "nethervinery:crimson_grape",
  "nethervinery:warped_grape_bush": "nethervinery:warped_grape",
};

// Tilled farmland map stored as JSON in persistentData:
// "<dimension>|x|y|z" -> { w: last day watered, c: last day kept moist by the perk }
const readTilled = (player) => {
  let raw = player.persistentData.getString(TILLED_KEY);
  if (!raw) return {};
  try {
    return JSON.parse(raw) || {};
  } catch (err) {
    return {};
  }
};

const saveTilled = (player, map) => {
  player.persistentData.putString(TILLED_KEY, JSON.stringify(map));
};

// Grape picking: a bush that lost age after a right click may drop one more grape.
BlockEvents.rightClicked((e) => {
  let { player, block, hand, server, level } = e;
  if (hand != "MAIN_HAND" || !player || player.isFake()) return;
  let grape = GRAPE_BUSHES[String(block.id)];
  if (!grape) return;
  let oldAge = Number(block.getProperties().get("age"));
  let pos = block.pos;
  server.scheduleInTicks(2, () => {
    try {
      let after = level.getBlock(pos);
      if (String(after.id) !== String(block.id)) return;
      let newAge = Number(after.getProperties().get("age"));
      if (!(newAge < oldAge)) return;
      if (!global.rollSpecialty(player, "farming", "grape_extra")) return;
      after.popItemFromFace(Item.of(`1x ${grape}`), "up");
    } catch (err) {
      console.error(`[specialty] grape picking failed: ${err}`);
    }
  });
});

// Farmland tilled by a farmer with a hoe is remembered for the hydration perk.
BlockEvents.rightClicked((e) => {
  let { player, item, block, hand, server, level } = e;
  if (hand != "MAIN_HAND" || !player || player.isFake()) return;
  if (!item.hasTag("minecraft:hoes") || !global.hasProfession(player, "farmer")) return;
  let pos = block.pos;
  server.scheduleInTicks(1, () => {
    try {
      if (!level.getBlock(pos).hasTag("dewdrop:waterable")) return;
      let map = readTilled(player);
      map[`${String(level.dimension)}|${pos.x}|${pos.y}|${pos.z}`] = { w: -1, c: -1 };
      let keys = Object.keys(map);
      if (keys.length > TILLED_MAX) delete map[keys[0]];
      saveTilled(player, map);
    } catch (err) {
      console.error(`[specialty] tilled farmland tracking failed: ${err}`);
    }
  });
});

// Hydration (farmer, tier II): every 200 ticks, farmland watered yesterday
// that is dry today gets one extra moist day. Once per real watering.
PlayerEvents.tick((e) => {
  let player = e.player;
  if (!player || player.isFake() || player.age % 200 != 0) return;
  try {
    if (global.specialtyChance(player, "farming", "hydration") < 1) return;
    let level = player.level;
    let today = global.getDay(level);
    let prefix = `${String(level.dimension)}|`;
    let map = readTilled(player);
    let changed = false;
    Object.keys(map).forEach((key) => {
      if (!key.startsWith(prefix)) return;
      let coords = key.slice(prefix.length).split("|").map(Number);
      let pos = new BlockPos(coords[0], coords[1], coords[2]);
      if (!level.isLoaded(pos)) return;
      if (!level.getBlock(pos).hasTag("dewdrop:waterable")) {
        delete map[key];
        changed = true;
        return;
      }
      let entry = map[key];
      if ($DewUtil.isMoistWaterable(level, pos)) {
        if (entry.c !== today && entry.w !== today) {
          entry.w = today;
          changed = true;
        }
      } else if ($DewUtil.isDryWaterable(level, pos) && entry.w === today - 1 && entry.c !== today) {
        $DewUtil.setMoist(level, pos);
        entry.c = today;
        changed = true;
      }
    });
    if (changed) saveTilled(player, map);
  } catch (err) {
    console.error(`[specialty] hydration failed: ${err}`);
  }
});
