// Stubs for globalRegistryCreateMetals.js and globalShippingBinHandlers.js (Rhino, outside the game).
// Loaded before the scripts under test. See run_create_metals.sh.
var OUT = [];
var RESULT = 0;
var console = {
  log: function (m) { OUT.push('     log: ' + m); },
  info: function (m) { OUT.push('     log: ' + m); },
  error: function (m) { OUT.push('     ERR: ' + m); }
};
function check(name, ok) {
  OUT.push((ok ? 'PASS ' : 'FAIL ') + name);
  if (!ok) RESULT++;
}
var global = {};
// Minimal Map-like object with the methods the scripts use (Rhino has no Map in this scope).
global.trades = new Map();
global.getConfiguredValue = function (value, mult) { return Math.round(value); };
// Mimics the CompoundTag methods used by the scripts (contains / getByte / getInt).
function makeNbt(values) {
  return {
    contains: function (k) { return Object.prototype.hasOwnProperty.call(values, k); },
    getByte: function (k) { return values[k]; },
    getInt: function (k) { return values[k]; }
  };
}
var stagesOf = function (list) { return { toString: function () { return list.join(','); } }; };
