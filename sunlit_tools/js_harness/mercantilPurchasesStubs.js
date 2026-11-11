// Minimal KubeJS / Minecraft / society_trading stubs for
// server_scripts/playerEvents/mercantilPurchases.js plus the purchase part of
// startup_scripts/professions/mercantilGlobals.js.
// Used by HostileToggleHarness.java through run_mercantil_purchases.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function (m) {}, error: function (m) { OUT.push('     err: ' + m); } };
var global = {
  getDay: function (level) { return level.day; },
  getProfessions: function () { return []; },
  giveExperience: function (server, player, tree, xp, mastery) { player.xp[tree] = (player.xp[tree] || 0) + xp; },
};

var HANDLERS = {};
var PlayerEvents = {
  tick: function (fn) { HANDLERS.tick = fn; },
  loggedIn: function (fn) {},
  loggedOut: function (fn) { HANDLERS.loggedOut = fn; },
};
var ItemEvents = { pickedUp: function (fn) { HANDLERS.pickedUp = fn; } };

function stack(id, count) {
  return { id: id, count: count,
    isEmpty: function () { return this.count <= 0; },
    getId: function () { return this.id; }, getCount: function () { return this.count; },
    getItem: function () { return this.id; } };
}
function offer(id, count, cost) {
  return { getResult: function () { return stack(id, count); }, getNumismaticsCost: function () { return cost; } };
}
var NEXT_ID = 1;
function shopMenu(cls) {
  var name = 'io.github.chakyl.societytrading.screen.' + (cls || 'ShopMenu');
  return { containerId: NEXT_ID++, selected: null, carried: stack('minecraft:air', 0),
    getClass: function () { return { getName: function () { return name; } }; },
    getCarried: function () { return this.carried; },
    getSelectedTrade: function () { return this.selected; } };
}
var INVENTORY_MENU = { containerId: 0, getClass: function () { return { getName: function () { return 'net.minecraft.world.inventory.InventoryMenu'; } }; } };

var P = {
  inv: {}, xp: {}, data: {}, fake: false,
  level: { day: 1, isClientSide: function () { return false; } },
  containerMenu: INVENTORY_MENU,
  isFake: function () { return this.fake; },
  getUuid: function () { return 'p1'; },
  getInventory: function () { var inv = this.inv; return { countItem: function (item) { return inv[item] || 0; } }; },
};
P.persistentData = {
  getInt: function (k) { return P.data[k] || 0; },
  putInt: function (k, v) { P.data[k] = v | 0; },
};
var SERVER = {};
function tick() { HANDLERS.tick({ player: P, server: SERVER }); }
function give(id, n) { P.inv[id] = (P.inv[id] || 0) + n; }
function pickup(id, n) { give(id, n); HANDLERS.pickedUp({ player: P, item: stack(id, n) }); }
function xp() { return P.xp.mercantil || 0; }
