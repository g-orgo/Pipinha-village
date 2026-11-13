// Minimal KubeJS / Minecraft / LSO / ParCool stubs for server_scripts/parkourExerciseHeat.js.
// Used by HostileToggleHarness.java through run_exercise_heat.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function (m) { OUT.push('     log: ' + m); } };

var HANDLERS = {};
var PlayerEvents = {
  tick: function (fn) { HANDLERS.tick = fn; },
  respawned: function (fn) { HANDLERS.respawned = fn; },
  loggedOut: function (fn) { HANDLERS.loggedOut = fn; },
};

var HEATING = { id: 'legendarysurvivaloverhaul:heating_temperature' };
var WET = { value: 0 };
var DOING = {};
function action(name) {
  return { isDoing: function () { return DOING[name] === true; },
    getClass: function () { return { getSimpleName: function () { return name; } }; } };
}
var ACTIONS = ['ClingToCliff', 'HangDown', 'FastRun', 'Vault', 'Slide'].map(action);
function javaList(arr) { return { size: function () { return arr.length; }, get: function (i) { return arr[i]; } }; }

function makeAttr() {
  var mods = {};
  return {
    mods: mods,
    getModifier: function (u) { return mods[u] || null; },
    removeModifier: function (u) { delete mods[u]; },
    addTransientModifier: function (m) { if (mods[m.uuid]) throw 'duplicate modifier'; mods[m.uuid] = m; },
    total: function () { var t = 0; for (var k in mods) t += mods[k].amount; return t; },
  };
}

var Java = {
  loadClass: function (n) {
    if (n === 'java.util.UUID') return { fromString: function (s) { return s; } };
    if (n === 'net.minecraft.world.entity.ai.attributes.AttributeModifier')
      return function (u, name, amount, op) { this.uuid = u; this.amount = amount; this.op = op; this.getAmount = function () { return this.amount; }; };
    if (n === 'net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation') return { ADDITION: 'ADDITION' };
    if (n === 'sfiomn.legendarysurvivaloverhaul.registry.AttributeRegistry') return { HEATING_TEMPERATURE: { get: function () { return HEATING; } } };
    if (n === 'sfiomn.legendarysurvivaloverhaul.api.wetness.WetnessUtil')
      return { addWetness: function (p, v) { WET.value = Math.max(0, Math.min(400, WET.value + v)); } };
    if (n === 'sfiomn.legendarysurvivaloverhaul.util.CapabilityUtil')
      return { getWetnessCapability: function () { return { getWetness: function () { return WET.value; } }; } };
    if (n === 'com.alrex.parcool.common.capability.Parkourability')
      return { get: function () { return { getList: function () { return javaList(ACTIONS); } }; } };
    throw 'unknown class ' + n;
  },
};

var P = {
  age: 0, x: 0, z: 0, sprint: false, water: false, creative: false, attr: makeAttr(),
  level: { isClientSide: function () { return false; } },
  isFake: function () { return false; },
  getUuid: function () { return 'p1'; },
  getX: function () { return this.x; }, getZ: function () { return this.z; },
  isSprinting: function () { return this.sprint; },
  isInWater: function () { return this.water; },
  isPassenger: function () { return false; },
  isCreative: function () { return this.creative; },
  isSpectator: function () { return false; },
  getAttribute: function (a) { return a === HEATING ? this.attr : null; },
};

// Advances the player one second (20 ticks), moving `speed` blocks per second on X.
// LSO dries 3 wetness every 10 ticks out of water, as in WetnessCapability.
function second(speed) {
  for (var t = 0; t < 20; t++) {
    P.age++;
    P.x += (speed || 0) / 20;
    if (P.age % 10 === 0) WET.value = Math.max(0, WET.value - 3);
    HANDLERS.tick({ player: P });
  }
}
function seconds(n, speed) { for (var i = 0; i < n; i++) second(speed); }
function heat() { return P.attr.total(); }
function near(a, b) { return Math.abs(a - b) < 0.01; }
