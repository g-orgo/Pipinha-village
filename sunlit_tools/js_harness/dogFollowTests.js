// Scenarios for dogFollowOwner.js: hide on mount, restore on dismount, no loss on errors or death.
var L = makeLevel('minecraft:overworld');
var P = makePlayer(L, 0, 0);
SERVER.players = [P];
var tick = function () { global.sunlitDogFollowTick(SERVER); };
var stored = function (p) {
  var pp = p.forge.contains('PlayerPersisted') ? p.forge.getCompound('PlayerPersisted') : null;
  return pp && pp.contains('sunlitHiddenDogs') ? pp.getList('sunlitHiddenDogs').size() : 0;
};
var at = function (uuid) { return L.ents.filter(function (e) { return e.uuid === uuid; }); };
L.ents.push(makeDog(L, 'dog-a', 3, 3), makeDog(L, 'dog-b', -4, 2));

tick();
P.riding = true; tick();
check('mount hides both dogs (world ' + L.ents.length + ', stored ' + stored(P) + ')', L.ents.length === 0 && stored(P) === 2);
P.x = 500; P.z = 500; tick();
P.riding = false; FAIL_LOAD['dog-b'] = true; tick();
check('dismount brings dog-a to the owner', at('dog-a').length === 1 && at('dog-a')[0].x === 500);
check('dog-b load error keeps it stored (stored ' + stored(P) + ')', at('dog-b').length === 0 && stored(P) === 1);
tick();
check('next tick on foot retries dog-b', at('dog-b').length === 1 && stored(P) === 0);

// Death while mounted: Forge copies only PlayerPersisted to the new player.
P.riding = true; tick();
check('mount again hides both', L.ents.length === 0 && stored(P) === 2);
var P2 = makePlayer(L, 900, 900);
P2.forge.put('PlayerPersisted', P.forge.getCompound('PlayerPersisted'));
SERVER.players = [P2];
tick();
check('respawned owner gets both dogs back at the respawn point', at('dog-a').length === 1 && at('dog-b').length === 1 && at('dog-a')[0].x === 900 && stored(P2) === 0);

// Legacy data left by the old script in KubeJS persistentData is migrated and restored on login.
HANDLERS.loggedOut({ player: P2 });
var legacy = new ListTag(); var t = new CompoundTag(); makeDog(L, 'dog-c', 0, 0).save(t); legacy.add(t);
P2.persistentData.put('sunlitHiddenDogs', legacy);
tick();
check('legacy hidden dog restored on login', at('dog-c').length === 1 && !P2.persistentData.contains('sunlitHiddenDogs'));

// A stored copy of a dog that is already in the world is dropped, not duplicated.
var dup = new ListTag(); var t2 = new CompoundTag(); at('dog-a')[0].save(t2); dup.add(t2);
P2.forge.getCompound('PlayerPersisted').put('sunlitHiddenDogs', dup);
tick();
check('duplicate UUID is not added twice', at('dog-a').length === 1 && stored(P2) === 0);
