// Stubs + tests for kubejs/server_scripts/blockEvents/autoClaimChunk.js, run by run_auto_claim.sh
// through HostileToggleHarness (evaluates: this file's stub part, the script, then runTests()).
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function () {}, error: function (m) { OUT.push('     ERR: ' + m); RESULT++; } };
var global = {};
var PLACED = null;
var BlockEvents = { placed: function (fn) { PLACED = fn; } };
var CLAIMED = {};
var CALLS = [];
var STATUS = [];
var API = {
  isManagerLoaded: function () { return true; },
  getManager: function () {
    return { getChunk: function (p) { return CLAIMED[p.key] || null; } };
  },
  claimAsPlayer: function (player, dim, pos, checkOnly) {
    CALLS.push(dim + ':' + pos.x + ',' + pos.z + ':' + checkOnly);
    var key = dim + ':' + pos.x + ',' + pos.z;
    if (CLAIMED[key] === 'other') return { isSuccess: function () { return false; } };
    CLAIMED[key] = 'me';
    return { isSuccess: function () { return true; } };
  },
};
var Java = {
  loadClass: function (name) {
    if (name.indexOf('FTBChunksAPI') >= 0) return { api: function () { return API; } };
    if (name.indexOf('ChunkDimPos') >= 0) return function (dim, x, z) { this.key = dim + ':' + x + ',' + z; };
    return function (x, z) { this.x = x; this.z = z; };
  },
};
var Text = {
  translatable: function (k, a) { return { green: function () { return k + '|' + a; } }; },
};
function player(fake) {
  return {
    isFake: function () { return fake; },
    level: { isClientSide: function () { return false; } },
    setStatusMessage: function (m) { STATUS.push(m); },
  };
}
function block(tags, hasBe, x, z) {
  return {
    level: { dimension: function () { return 'minecraft:overworld'; } },
    pos: { x: x, z: z },
    hasTag: function (t) { return tags.indexOf(t) >= 0; },
    getEntity: function () { return hasBe ? {} : null; },
    blockState: { hasBlockEntity: function () { return hasBe; } },
  };
}
function place(p, b) { PLACED({ player: p, block: b }); }

function runTests() {
  place(player(false), block([], true, 33, -17));
  check('chest claims its chunk (2,-2)', CALLS.length === 1 && CALLS[0] === 'minecraft:overworld:2,-2:false');
  check('success shows the status message', STATUS.length === 1 && STATUS[0] === 'sunlit_claims.auto_claimed|2, -2');
  place(player(false), block([], true, 40, -20));
  check('already claimed chunk is not claimed again', CALLS.length === 1);
  place(player(false), block(['minecraft:beds'], false, 100, 100));
  check('bed claims even without block entity check', CALLS.length === 2);
  place(player(false), block([], false, 300, 300));
  check('plain block (no block entity) never claims', CALLS.length === 2);
  place(player(false), block(['minecraft:all_signs'], true, 500, 500));
  check('sign does not claim', CALLS.length === 2);
  place(player(false), block(['minecraft:banners'], true, 520, 500));
  check('banner does not claim', CALLS.length === 2);
  place(player(true), block([], true, 700, 700));
  check('fake player (deployer) does not claim', CALLS.length === 2);
  place(null, block([], true, 720, 700));
  check('no player does not claim nor throw', CALLS.length === 2 && RESULT === 0);
  CLAIMED['minecraft:overworld:60,60'] = 'other';
  place(player(false), block([], true, 960, 960));
  check('chunk of another team: no claim call, no message', CALLS.length === 2 && STATUS.length === 2);
}
