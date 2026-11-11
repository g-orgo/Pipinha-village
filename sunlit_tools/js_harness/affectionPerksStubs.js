// Minimal KubeJS / Minecraft / Forge stubs for server_scripts/entities/animalAffectionPerks.js.
// Used by HostileToggleHarness.java through run_affection_perks.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function (m) { OUT.push('     log: ' + m); }, error: function (m) { OUT.push('     err: ' + m); } };

var Java = {
  loadClass: function (name) {
    if (name === 'java.util.UUID') return { fromString: function (s) { return s; } };
    if (name === 'net.minecraft.world.entity.ai.attributes.AttributeModifier') {
      return function (uuid, nm, amount, op) { this.uuid = uuid; this.name = nm; this.amount = amount; this.op = op; this.getAmount = function () { return amount; }; };
    }
    if (name === 'net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation') {
      return { ADDITION: 'ADDITION', MULTIPLY_BASE: 'MULTIPLY_BASE' };
    }
    if (name === 'net.minecraft.world.entity.EquipmentSlot') {
      return { valueOf: function (s) { return s; } };
    }
    if (name === 'net.minecraftforge.registries.ForgeRegistries') {
      return { ATTRIBUTES: { getValue: function (rl) { return ATTR_BY_ID[rl.id] || null; } } };
    }
    if (name === 'net.minecraft.resources.ResourceLocation') {
      return function (ns, path) { this.id = path; };
    }
    if (name === 'net.minecraft.world.phys.AABB') {
      return function (x1, y1, z1, x2, y2, z2) { this.minX = x1; this.minY = y1; this.minZ = z1; this.maxX = x2; this.maxY = y2; this.maxZ = z2; };
    }
    throw new Error('unknown class ' + name);
  },
};

// Hand objects behave like the Java InteractionHand enum: only toString() gives the name.
var HAND = {
  MAIN: { toString: function () { return 'MAIN_HAND'; } },
  OFF: { toString: function () { return 'OFF_HAND'; } },
};

// Player and entity event registrations used by dogFollowOwner.js.
var LOGGED_OUT = [];
var PlayerEvents = { loggedOut: function (fn) { LOGGED_OUT.push(fn); } };

// Level stub: getEntitiesWithin returns the entities whose position is inside the AABB.
function makeLevel(dim, entities) {
  return {
    dimension: dim,
    entities: entities || [],
    getEntitiesWithin: function (box) {
      return this.entities.filter(function (e) {
        return e.x >= box.minX && e.x <= box.maxX && e.y >= box.minY && e.y <= box.maxY && e.z >= box.minZ && e.z <= box.maxZ;
      });
    },
  };
}

// Attribute ids verified in the client srg jar; one stub attribute object per id.
var ATTR_BY_ID = {};
function makeAttribute(id) {
  var mods = {};
  ATTR_BY_ID[id] = { id: id };
  return {
    mods: mods,
    getModifier: function (u) { return mods[u] || null; },
    removeModifier: function (u) { delete mods[u]; },
    addPermanentModifier: function (m) { mods[m.uuid] = m; },
    total: function () { var t = 0; for (var k in mods) t += mods[k].amount; return t; },
  };
}
['generic.attack_damage', 'generic.armor', 'generic.movement_speed', 'horse.jump_strength', 'generic.flying_speed']
  .forEach(function (id) { ATTR_BY_ID[id] = { id: id }; });

function makeEntity(type, opts) {
  opts = opts || {};
  var attrs = {};
  var data = { affection: opts.affection || 0, ageLastPet: opts.ageLastPet || 0, affectionArmorGiven: false };
  var slots = { CHEST: opts.chest || null };
  return {
    type: type,
    customName: null,
    persistentData: {
      getInt: function (k) { return data[k] || 0; },
      getBoolean: function (k) { return data[k] === true; },
      putBoolean: function (k, v) { data[k] = v; },
    },
    getAttribute: function (attr) {
      if ((opts.noAttrs || []).indexOf(attr.id) !== -1) return null;
      if (!attrs[attr.id]) attrs[attr.id] = makeAttribute(attr.id);
      return attrs[attr.id];
    },
    isTame: function () { return opts.tame === true; },
    getOwnerUUID: function () { return opts.owner || null; },
    getItemBySlot: function (s) { return { isEmpty: function () { return slots[s] === null; } }; },
    setItemSlot: function (s, item) { slots[s] = item; },
    level: { spawnParticles: function () {} },
    x: 0, y: 64, z: 0,
    _attrs: attrs, _data: data, _slots: slots,
  };
}

var Item = { of: function (id) { return { id: id }; } };
var Text = { translatable: function (key, a) { return { toJson: function () { return key + ':' + a; } }; } };

var SENT = [];
var server = { runCommandSilent: function (cmd) { SENT.push(cmd); } };
var PLAYER = { uuid: 'owner-uuid', username: 'Owner', isFake: function () { return false; } };
var DAY = 10;
var global = {
  getDay: function () { return DAY; },
  checkEntityTag: function (entity, tag) { return entity.tags ? entity.tags.indexOf(tag) !== -1 : false; },
  getTranslatedEntityName: function (t) { return t; },
  getEmbersTextAPICommand: function (name, style, time, json) { return 'embers ' + name + ' ' + time + ' ' + json; },
};
