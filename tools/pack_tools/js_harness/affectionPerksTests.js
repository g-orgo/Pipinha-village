// Scenarios for animalAffectionPerks.js (run after the stubs and the script).
var UUID_DMG = '7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e01';
var UUID_ARMOR = '7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e02';
var UUID_MOVE = '7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e03';
var UUID_FLY = '7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e05';
function amountOf(e, attr, uuid) { var m = e.getAttribute({ id: attr }).getModifier(uuid); return m ? m.getAmount() : null; }
function near(a, b) { return a !== null && Math.abs(a - b) < 0.001; }

// shouldPetFirst: hand, fake player, held item, tags and day.
var pet = makeEntity('minecraft:cat', {});
pet.tags = ['society:pet_animal'];
var empty = { isEmpty: function () { return true; } };
var held = { isEmpty: function () { return false; } };
check('pet first: empty main hand, not petted today', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, empty, pet, {}) === true);
check('pet first: off hand is ignored', global.sunlitShouldPetFirst(HAND.OFF, PLAYER, empty, pet, {}) === false);
function heldItem(id, tags) {
  return { id: id, isEmpty: function () { return false; }, hasTag: function (t) { return (tags || []).indexOf(t) !== -1; } };
}
check('pet first: pet with any plain held item is petted', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem('minecraft:stone'), pet, {}) === true);
['minecraft:lead', 'minecraft:saddle', 'minecraft:name_tag', 'minecraft:diamond_horse_armor', 'minecraft:red_dye', 'minecraft:water_bucket', 'moblassos:golden_lasso', 'society:mood_scanner']
  .forEach(function (id) { check('pet first: pet use item keeps its use (' + id + ')', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem(id), pet, {}) === false); });
check('pet first: feed tag keeps its use', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem('x:y', ['society:animal_feed']), pet, {}) === false);
var foodPet = makeEntity('minecraft:horse', {});
foodPet.tags = ['society:pet_animal'];
foodPet.isFood = function (item) { return item.id === 'minecraft:golden_carrot'; };
check('pet first: food the pet eats keeps its use', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem('minecraft:golden_carrot'), foodPet, {}) === false);
check('pet first: horse with a sword is petted', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem('minecraft:iron_sword'), foodPet, {}) === true);
var cow = makeEntity('minecraft:cow', {});
cow.tags = ['society:husbandry_animal'];
check('pet first: husbandry animal with held item is ignored', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, heldItem('minecraft:stone'), cow, {}) === false);
check('pet first: husbandry animal with empty hand is petted', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, empty, cow, {}) === true);
check('pet first: fake player is ignored', global.sunlitShouldPetFirst(HAND.MAIN, { isFake: function () { return true; } }, empty, pet, {}) === false);
var petted = makeEntity('minecraft:cat', { ageLastPet: 10 });
petted.tags = ['society:pet_animal'];
check('pet first: already petted today falls through', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, empty, petted, {}) === false);
var plain = makeEntity('minecraft:cow', {});
plain.tags = [];
check('pet first: non-society animal is ignored', global.sunlitShouldPetFirst(HAND.MAIN, PLAYER, empty, plain, {}) === false);

// Perk amounts per group at 4, 5 and 10 hearts.
var dog4 = makeEntity('minecraft:wolf', { affection: 400, tame: true, owner: 'owner-uuid' });
global.applyAffectionPerks(dog4, PLAYER, server);
check('dog at 4 hearts has no attack bonus', amountOf(dog4, 'generic.attack_damage', UUID_DMG) === null);
var dog5 = makeEntity('minecraft:wolf', { affection: 500, tame: true, owner: 'owner-uuid' });
global.applyAffectionPerks(dog5, PLAYER, server);
check('dog at 5 hearts gets 4/6 of attack (got ' + amountOf(dog5, 'generic.attack_damage', UUID_DMG) + ')', near(amountOf(dog5, 'generic.attack_damage', UUID_DMG), 4 / 6));
check('dog at 5 hearts gets 8/6 of armor', near(amountOf(dog5, 'generic.armor', UUID_ARMOR), 8 / 6));
var dog10 = makeEntity('minecraft:wolf', { affection: 1000, tame: true, owner: 'owner-uuid' });
global.applyAffectionPerks(dog10, PLAYER, server);
check('dog at 10 hearts gets full attack 4', near(amountOf(dog10, 'generic.attack_damage', UUID_DMG), 4));
check('dog at 10 hearts gets full armor 8', near(amountOf(dog10, 'generic.armor', UUID_ARMOR), 8));

var horse = makeEntity('minecraft:horse', { affection: 1000 });
global.applyAffectionPerks(horse, PLAYER, server);
check('horse at 10 hearts gets movement 0.2', near(amountOf(horse, 'generic.movement_speed', UUID_MOVE), 0.2));
var cat = makeEntity('minecraft:cat', { affection: 500 });
global.applyAffectionPerks(cat, PLAYER, server);
check('cat at 5 hearts gets flying 0.2/6', near(amountOf(cat, 'generic.flying_speed', UUID_FLY), 0.2 / 6));

// No re-add when unchanged: the same modifier object stays in place.
var before = dog10.getAttribute({ id: 'generic.attack_damage' }).getModifier(UUID_DMG);
global.applyAffectionPerks(dog10, PLAYER, server);
check('unchanged perk is not re-added', dog10.getAttribute({ id: 'generic.attack_damage' }).getModifier(UUID_DMG) === before);

// Removal below 5 hearts.
dog10._data.affection = 300;
global.applyAffectionPerks(dog10, PLAYER, server);
check('perk removed at 3 hearts', amountOf(dog10, 'generic.attack_damage', UUID_DMG) === null);

// Wolf Armor: once, own tamed wolf at 10 hearts, chest empty.
var wolf = makeEntity('minecraft:wolf', { affection: 1000, tame: true, owner: 'owner-uuid' });
global.applyAffectionPerks(wolf, PLAYER, server);
check('wolf at 10 hearts gets wolf armor', wolf._slots.CHEST !== null && wolf._slots.CHEST.id === 'minecraft:wolf_armor');
check('armor gift flag set', wolf._data.affectionArmorGiven === true);
check('armor gift message sent', SENT.some(function (c) { return c.indexOf('embers Owner') !== -1; }));
var sentBefore = SENT.length;
wolf._slots.CHEST = null;
global.applyAffectionPerks(wolf, PLAYER, server);
check('armor gift is not given twice', wolf._slots.CHEST === null && SENT.length === sentBefore);

var stranger = makeEntity('minecraft:wolf', { affection: 1000, tame: true, owner: 'someone-else' });
global.applyAffectionPerks(stranger, PLAYER, server);
check('no armor for another owner', stranger._slots.CHEST === null);
var fox = makeEntity('quark:shiba', { affection: 1000, tame: true, owner: 'owner-uuid' });
global.applyAffectionPerks(fox, PLAYER, server);
check('no armor for a non-vanilla wolf type', fox._slots.CHEST === null);
var wild = makeEntity('minecraft:wolf', { affection: 1000, tame: false });
global.applyAffectionPerks(wild, PLAYER, server);
check('no armor for untamed wolf', wild._slots.CHEST === null);

// Null attribute (shiba without attack damage): no throw, the other perks still apply.
var noAttack = makeEntity('quark:shiba', { affection: 1000, tame: true, owner: 'owner-uuid', noAttrs: ['generic.attack_damage'] });
var nullOk = true;
try { global.applyAffectionPerks(noAttack, PLAYER, server); } catch (e) { nullOk = false; }
check('null attack attribute does not throw', nullOk);
check('null attack attribute: armor still applied', near(amountOf(noAttack, 'generic.armor', UUID_ARMOR), 8));

// dogFollowOwner.js: teleport, dimension change, dismount and filters.
var SENT_MARK = SENT.length;
function tickPlayers(list) { server.players = list; global.sunlitDogFollowTick(server); }
function makePlayer(uuid, level, x, y, z) {
  var p = { uuid: uuid, level: level, x: x, y: y, z: z, riding: false, alive: true, persistentData: makeData() };
  p.isPassenger = function () { return p.riding; };
  p.isAlive = function () { return p.alive; };
  return p;
}
function makeDog(uuid, type, level, x, y, z, opts) {
  opts = opts || {};
  var d = makeEntity(type, { tame: opts.tame !== false, owner: opts.owner || 'P1', affection: 0 });
  d.uuid = uuid; d.x = x; d.y = y; d.z = z; d.level = level;
  d.isAlive = function () { return true; };
  d.isOrderedToSit = function () { return opts.sit === true; };
  d.isPassenger = function () { return false; };
  d.isLeashed = function () { return opts.leashed === true; };
  d.getCommand = function () { return opts.command === undefined ? 2 : opts.command; };
  d.save = function (tag) { tag.entity = d; return true; };
  d.remove = function (reason) { d.removed = reason; };
  d.moveTo = function (x2, y2, z2) { d.x = x2; d.y = y2; d.z = z2; };
  d.getYRot = function () { return 0; };
  d.getXRot = function () { return 0; };
  level.entities.push(d);
  return d;
}
function sentFor(uuid) { return SENT.slice(SENT_MARK).filter(function (c) { return c.indexOf(' tp ' + uuid + ' ') !== -1; }); }

// Teleport in the same dimension: only dogs near the OLD position follow.
var lvA = makeLevel('minecraft:overworld', []);
var lvB = makeLevel('minecraft:the_nether', []);
var owner1 = makePlayer('P1', lvA, 0, 64, 0);
tickPlayers([owner1]);
makeDog('D1', 'minecraft:wolf', lvA, 1, 64, 1);
makeDog('D1s', 'minecraft:wolf', lvA, 2, 64, 2, { sit: true });
makeDog('D1w', 'minecraft:wolf', lvA, 2, 64, 3, { command: 0 });
makeDog('D1t', 'minecraft:wolf', lvA, 2, 64, 4, { command: 1 });
makeDog('D1o', 'minecraft:wolf', lvA, 2, 64, 5, { owner: 'OTHER' });
makeDog('D1l', 'minecraft:wolf', lvA, 2, 64, 6, { leashed: true });
makeDog('D1c', 'minecraft:cow', lvA, 2, 64, 7, { tame: false });
makeDog('D1far', 'minecraft:wolf', lvA, 150, 64, 150);
owner1.x = 200; owner1.z = 200;
tickPlayers([owner1]);
check('teleport: following dog moved from the old position', sentFor('D1').length === 1 && SENT[SENT.length - 1].indexOf('execute in minecraft:overworld run tp D1 200 64 200') !== -1);
check('teleport: sitting, wander, stay, other owner, leashed, cow and far dogs not moved', ['D1s', 'D1w', 'D1t', 'D1o', 'D1l', 'D1c', 'D1far'].every(function (u) { return sentFor(u).length === 0; }));

// Small move does nothing.
var sentBeforeSmall = SENT.length;
owner1.x = 205;
tickPlayers([owner1]);
check('small move (5 blocks) does nothing', SENT.length === sentBeforeSmall);

// Dimension change: dogs from the old level follow into the new dimension.
var owner2 = makePlayer('P2', lvA, 0, 64, 0);
tickPlayers([owner2]);
var d4 = makeDog('D4', 'quark:shiba', lvA, 3, 64, 3, { owner: 'P2' });
owner2.level = lvB; owner2.x = 10; owner2.y = 70; owner2.z = 10;
tickPlayers([owner2]);
check('dimension change: dog follows into the new dimension', sentFor('D4').length === 1 && sentFor('D4')[0] === 'execute in minecraft:the_nether run tp D4 10 70 10');

// Dismount: a riding player gets off, following dogs near the owner are placed at its feet.
var owner3 = makePlayer('P3', lvA, 0, 64, 0);
owner3.riding = true;
tickPlayers([owner3]);
makeDog('D5', 'minecraft:wolf', lvA, 5, 64, 5, { owner: 'P3' });
owner3.riding = false;
tickPlayers([owner3]);
check('dismount: following dog placed at the owner feet', sentFor('D5').length === 1 && sentFor('D5')[0] === 'execute in minecraft:overworld run tp D5 0 64 0');

// Mount hides following dogs; dismount far away brings them back at the owner's feet.
var owner5 = makePlayer('P5', lvA, 0, 64, 0);
tickPlayers([owner5]);
var d7 = makeDog('D7', 'minecraft:wolf', lvA, 3, 64, 3, { owner: 'P5' });
var d7s = makeDog('D7s', 'minecraft:wolf', lvA, 4, 64, 4, { owner: 'P5', sit: true });
owner5.riding = true;
tickPlayers([owner5]);
check('mount: following dog removed from the world', d7.removed === 'UNLOADED_WITH_PLAYER');
check('mount: sitting dog stays', !d7s.removed);
check('mount: dog saved in the owner data', owner5.persistentData.contains('sunlitHiddenDogs'));
owner5.x = 10; owner5.z = 10; tickPlayers([owner5]);
owner5.x = 20; owner5.z = 20; tickPlayers([owner5]);
check('riding: hidden dog is not teleported', sentFor('D7').length === 0);
owner5.x = 500; owner5.z = 500;
tickPlayers([owner5]);
owner5.riding = false;
tickPlayers([owner5]);
check('dismount: hidden dog respawned at the owner feet', !d7.removed && d7.x === 500 && d7.z === 500 && lvA.added.indexOf(d7) !== -1);
check('dismount: owner data cleared', !owner5.persistentData.contains('sunlitHiddenDogs'));

// Login with dogs left hidden (session ended mid-ride) and not riding: dogs come back.
var owner6 = makePlayer('P6', lvB, 7, 70, 7);
var d8 = makeDog('D8', 'minecraft:wolf', lvA, 0, 64, 0, { owner: 'P6' });
var saved = new (Java.loadClass('net.minecraft.nbt.ListTag'))();
var savedTag = {}; d8.save(savedTag); d8.remove('UNLOADED_WITH_PLAYER'); saved.add(savedTag);
owner6.persistentData.put('sunlitHiddenDogs', saved);
tickPlayers([owner6]);
check('login: hidden dog restored in the owner level', !d8.removed && d8.level === lvB && d8.x === 7);

// Dead player is skipped.
var owner4 = makePlayer('P4', lvA, 0, 64, 0);
tickPlayers([owner4]);
makeDog('D6', 'minecraft:wolf', lvA, 1, 64, 1, { owner: 'P4' });
owner4.alive = false; owner4.x = 300; owner4.z = 300;
tickPlayers([owner4]);
check('dead player: dogs not moved', sentFor('D6').length === 0);

// Logout clears the state (the handler is registered).
check('logout handler registered', LOGGED_OUT.length === 1);
