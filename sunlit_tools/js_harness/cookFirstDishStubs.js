// Minimal KubeJS / Minecraft stubs for server_scripts/playerEvents/cookFirstDish.js.
// Used by HostileToggleHarness.java through run_cook_first_dish.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function (m) { OUT.push('     ' + m); }, error: function (m) { OUT.push('     err: ' + m); } };

function BlockItemStub(id) { this.id = id; }
var Java = { loadClass: function (name) { return BlockItemStub; } };

// Test catalogue: what each id is in game.
var CATALOGUE = {
  'farmersdelight:beef_stew': 'food',
  'farmersdelight:hot_cocoa': 'drink',
  'farmersdelight:roast_chicken_block': 'block',
  'society:tubasmoke_carton': 'other',
  'bakery:sandwich': 'food',
};
var GIVEN = [];
var Item = {
  of: function (id, count) {
    var kind = CATALOGUE[id];
    var item = kind === 'block' ? new BlockItemStub(id) : { id: id };
    return {
      id: id, count: count || 1,
      isEmpty: function () { return !kind; },
      getItem: function () { return item; },
      isEdible: function () { return kind === 'food'; },
      getUseAnimation: function () { return kind === 'drink' ? 'DRINK' : 'NONE'; },
      getHoverName: function () { return 'name:' + id; },
    };
  },
};
var TOLD = [];
var Text = { translatable: function (key) { var args = Array.prototype.slice.call(arguments, 1); return { gold: function () { return { key: key, args: args }; } }; } };

var global = {
  trades: new Map(),
  hasProfession: function (player, id) { return player.cook && id === 'cook'; },
  professionBoostedXp: function (player, tree, xp) { return Math.round(xp * 1.5); },
  giveExperience: function (server, player, tree, xp, exact) { player.xp[tree] = (player.xp[tree] || 0) + xp; },
  coinMap: [{ coin: 'numismatics:cog', value: 64 }, { coin: 'numismatics:sprocket', value: 16 }, { coin: 'numismatics:bevel', value: 8 }, { coin: 'numismatics:spur', value: 1 }],
};
global.calculateCoinsFromValue = function (price, output) {
  for (var i = 0; i < global.coinMap.length; i++) {
    var c = global.coinMap[i];
    if (c.value <= price) {
      if (price % c.value === 0) { output.push({ id: c.coin, count: price / c.value }); return output; }
      output.push({ id: c.coin, count: Math.floor(price / c.value) });
      global.calculateCoinsFromValue(price % c.value, output);
      return output;
    }
  }
};
[['farmersdelight:beef_stew', 90], ['farmersdelight:hot_cocoa', 40], ['farmersdelight:roast_chicken_block', 600],
 ['society:tubasmoke_carton', 2482], ['bakery:sandwich', 75]].forEach(function (e) { global.trades.set(e[0], { value: e[1] }); });

var HANDLERS = {};
var PlayerEvents = { tick: function (fn) { HANDLERS.tick = fn; }, loggedIn: function (fn) { HANDLERS.loggedIn = fn; } };
var BlockEvents = { rightClicked: function (fn) { HANDLERS.click = fn; } };

function compound() {
  return { m: {}, contains: function (k) { return this.m.hasOwnProperty(k); },
    putBoolean: function (k, v) { this.m[k] = v; }, getCompound: function (k) { return this.m[k] || compound(); },
    put: function (k, v) { this.m[k] = v; }, keys: function () { return Object.keys(this.m); } };
}
var SCHEDULED = [];
var SERVER = { scheduleInTicks: function (t, fn) { SCHEDULED.push(fn); }, runCommandSilent: function (c) {} };
function menu(name) { return { getClass: function () { return { getSimpleName: function () { return name; } }; } }; }

var P = {
  cook: true, fake: false, age: 0, xp: {}, crafted: {}, inv: [], server: SERVER, username: 'Dev', x: 0, y: 0, z: 0,
  level: { isClientSide: function () { return false; } },
  containerMenu: menu('InventoryMenu'),
  persistentData: compound(),
  isFake: function () { return this.fake; },
  getUuid: function () { return 'p1'; },
  tell: function (t) { TOLD.push(t); },
  give: function (s) { GIVEN.push(s.id + 'x' + s.count); },
  getInventory: function () {
    var inv = this.inv;
    return { getContainerSize: function () { return inv.length; },
      getItem: function (i) { var s = inv[i]; return { isEmpty: function () { return !s || s.count <= 0; }, getId: function () { return s.id; }, getCount: function () { return s.count; } }; } };
  },
};
P.stats = { getItemsCrafted: function (item) { return P.crafted[item.id] || 0; } };
