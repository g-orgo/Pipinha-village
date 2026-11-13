// Fake world for kubejs/startup_scripts/forgeEvents/culinariaSkills.js.
var OUT = [];
var RESULT = 0;
var console = { info: function () {}, error: function (m) { OUT.push("ERRO " + m); RESULT++; } };
var global = { professionBoostedXp: function (p, t, xp) { return xp; } };
var FORGE_HANDLER = null;
var ForgeEvents = { onEvent: function (name, fn) { FORGE_HANDLER = fn; } };
var AABB = { ofBlock: function (pos) { return { inflate: function () { return pos; } }; } };

var RANDOM = 0;
Math.random = function () { return RANDOM; };

var makeDrop = function (uuid, id, count) {
  var stack = {
    id: id,
    count: count,
    nbt: "quality",
    copy: function () { return makeDrop(uuid, id, count).getItem(); },
    setCount: function (n) { this.count = n; },
    getCount: function () { return this.count; },
  };
  return {
    getType: function () { return "minecraft:item"; },
    getUuid: function () { return uuid; },
    getItem: function () { return stack; },
  };
};
var otherEntity = {
  getType: function () { return "minecraft:armor_stand"; },
  getUuid: function () { return "stand"; },
};

// One right click on a board. "cut" says whether the board consumed the item,
// "dropped" lists the entities the cut spawned.
var runCut = function (stages, cut, dropped) {
  var given = [];
  var xp = [];
  var entities = [makeDrop("old", "minecraft:dirt", 5), otherEntity];
  var stored = { isEmpty: function () { return false; }, getCount: function () { return 1; } };
  var level = {
    getBlock: function () { return { getId: function () { return "farmersdelight:cutting_board"; } }; },
    getBlockEntity: function () { return { getStoredItem: function () { return stored; } }; },
    getEntitiesWithin: function () { return entities; },
  };
  var clicker = {
    username: "dev",
    level: { isClientSide: function () { return false; } },
    isFake: function () { return false; },
    stages: { has: function (s) { return stages.indexOf(s) !== -1; } },
    getHeldItem: function () { return { getId: function () { return "farmersdelight:iron_knife"; } }; },
    give: function (s) { given.push(s.id + "x" + s.count + ":" + s.nbt); },
    getServer: function () {
      return {
        runCommandSilent: function (c) { xp.push(c); },
        scheduleInTicks: function (n, fn) {
          if (cut) {
            stored = { isEmpty: function () { return true; }, getCount: function () { return 0; } };
            entities = entities.concat(dropped);
          }
          fn();
        },
      };
    },
  };
  FORGE_HANDLER({
    getEntity: function () { return clicker; },
    getLevel: function () { return level; },
    getPos: function () { return {}; },
  });
  return { given: given.join(","), xp: xp.length };
};

var check = function (name, got, want) {
  var ok = got.given === want.given && got.xp === want.xp;
  if (!ok) RESULT++;
  OUT.push((ok ? "OK   " : "FALHA ") + name + " given=[" + got.given + "] xp=" + got.xp);
};

var both = ["culinaria_extra", "culinaria_double"];
var cabbage = function () { return [makeDrop("a", "farmersdelight:cabbage_leaf", 2)]; };

RANDOM = 0;
check("sem perk: so XP", runCut([], true, cabbage()), { given: "", xp: 1 });
check("extra: +1 da saida", runCut(["culinaria_extra"], true, cabbage()), { given: "farmersdelight:cabbage_leafx1:quality", xp: 1 });
check("double: dobra a saida", runCut(["culinaria_double"], true, cabbage()), { given: "farmersdelight:cabbage_leafx2:quality", xp: 1 });
check("extra + double", runCut(both, true, cabbage()), { given: "farmersdelight:cabbage_leafx1:quality,farmersdelight:cabbage_leafx2:quality", xp: 1 });
check("saidas multiplas no double", runCut(["culinaria_double"], true, [makeDrop("a", "x:a", 1), makeDrop("b", "x:b", 3)]), { given: "x:ax1:quality,x:bx3:quality", xp: 1 });
check("nao cortou: nada", runCut(both, false, cabbage()), { given: "", xp: 0 });
check("cortou sem saida nova: so XP", runCut(both, true, []), { given: "", xp: 1 });
RANDOM = 0.5;
check("roll alto: so XP", runCut(both, true, cabbage()), { given: "", xp: 1 });
RANDOM = 0.1;
check("roll 0.1: extra sim, double nao", runCut(both, true, cabbage()), { given: "farmersdelight:cabbage_leafx1:quality", xp: 1 });
