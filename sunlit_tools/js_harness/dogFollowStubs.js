// Minimal KubeJS / Minecraft stubs for server_scripts/entities/dogFollowOwner.js.
// Used by HostileToggleHarness.java through run_dog_follow.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = {
  info: function (m) { OUT.push('     log: ' + m); },
  error: function (m) { OUT.push('     err: ' + m); },
};
var HANDLERS = {};
var PlayerEvents = { loggedOut: function (fn) { HANDLERS.loggedOut = fn; } };
var global = {};

function javaList(arr) { return { size: function () { return arr.length; }, get: function (i) { return arr[i]; } }; }

function CompoundTag() { this.m = {}; }
CompoundTag.prototype.contains = function (k) { return Object.prototype.hasOwnProperty.call(this.m, k); };
CompoundTag.prototype.put = function (k, v) { this.m[k] = v; };
CompoundTag.prototype.putFloat = function (k, v) { this.m[k] = v; };
CompoundTag.prototype.remove = function (k) { delete this.m[k]; };
CompoundTag.prototype.getList = function (k) { return this.contains(k) ? this.m[k] : new ListTag(); };
CompoundTag.prototype.getCompound = function (k) { return this.contains(k) ? this.m[k] : new CompoundTag(); };
function ListTag() { this.a = []; }
ListTag.prototype.add = function (v) { this.a.push(v); return true; };
ListTag.prototype.size = function () { return this.a.length; };
ListTag.prototype.get = function (i) { return this.a[i]; };
ListTag.prototype.getCompound = function (i) { return this.a[i]; };

// Set by tests: a UUID whose next load throws once.
var FAIL_LOAD = {};
function makeDog(level, uuid, x, z) {
  var d = { type: 'minecraft:wolf', uuid: uuid, x: x, y: 64, z: z, level: level, alive: true, sit: false, owner: 'owner-1' };
  d.isAlive = function () { return d.alive; };
  d.isTame = function () { return true; };
  d.getOwnerUUID = function () { return d.owner; };
  d.isOrderedToSit = function () { return d.sit; };
  d.isPassenger = function () { return false; };
  d.isLeashed = function () { return false; };
  d.save = function (tag) {
    tag.put('id', d.type); tag.put('UUID', d.uuid); tag.put('Owner', d.owner);
    tag.put('Pos', { a: [d.x, d.y, d.z] });
    return true;
  };
  d.remove = function () { d.alive = false; level.ents.splice(level.ents.indexOf(d), 1); };
  return d;
}
function makeLevel(dim) {
  var level = { dim: dim, ents: [] };
  level.dimension = dim;
  level.getEntitiesWithin = function (box) {
    return javaList(level.ents.filter(function (e) {
      return e.x >= box.x0 && e.x <= box.x1 && e.z >= box.z0 && e.z <= box.z1;
    }));
  };
  level.tryAddFreshEntityWithPassengers = function (e) {
    if (level.ents.some(function (o) { return o.uuid === e.uuid; })) return false;
    level.ents.push(e); return true;
  };
  return level;
}
function makePlayer(level, x, z) {
  var p = { uuid: 'owner-1', level: level, x: x, y: 64, z: z, riding: false, alive: true,
    persistentData: new CompoundTag(), forge: new CompoundTag() };
  p.isPassenger = function () { return p.riding; };
  p.isAlive = function () { return p.alive; };
  p.getForgePersistentData = function () { return p.forge; };
  return p;
}
var SERVER = { players: [], runCommandSilent: function () {} };

var Java = {
  loadClass: function (n) {
    if (n === 'net.minecraft.world.phys.AABB') {
      return function (x0, y0, z0, x1, y1, z1) { this.x0 = x0; this.z0 = z0; this.x1 = x1; this.z1 = z1; };
    }
    if (n === 'net.minecraft.nbt.CompoundTag') return CompoundTag;
    if (n === 'net.minecraft.nbt.ListTag') return ListTag;
    if (n === 'net.minecraft.nbt.DoubleTag') return { valueOf: function (v) { return v; } };
    if (n === 'net.minecraft.world.entity.Entity$RemovalReason') return { UNLOADED_WITH_PLAYER: 'uwp' };
    if (n === 'net.minecraft.world.entity.EntityType') {
      return {
        loadEntityRecursive: function (tag, level, fn) {
          var uuid = tag.m.UUID;
          if (FAIL_LOAD[uuid]) { delete FAIL_LOAD[uuid]; throw 'simulated load error'; }
          var p = tag.m.Pos.a;
          return fn(makeDog(level, uuid, p[0], p[2]));
        },
      };
    }
    throw 'unexpected class ' + n;
  },
};
