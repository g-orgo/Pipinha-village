// Scenarios for parkourExerciseHeat.js (run after the stubs and the script).
check('handlers registered', typeof HANDLERS.tick === 'function' && typeof HANDLERS.respawned === 'function');

second(0);
check('standing still adds no heat', near(heat(), 0));

P.sprint = true;
seconds(10, 5.6);
check('10 s of sprinting gives +1.0 (got ' + heat().toFixed(2) + ')', near(heat(), 1.0));
seconds(40, 5.6);
check('heat caps at +4.0 (got ' + heat().toFixed(2) + ')', near(heat(), 4.0));
check('only one modifier on the attribute', Object.keys(P.attr.mods).length === 1);
check('no sweat right after reaching the cap (wet ' + WET.value + ')', WET.value === 0);
seconds(30, 5.6);
check('long time at the cap makes the player sweat (wet ' + WET.value + ')', WET.value >= 100 && WET.value <= 120);
seconds(60, 5.6);
check('sweat never passes the cap of 120 (wet ' + WET.value + ')', WET.value <= 120);

P.sprint = false;
seconds(10, 0);
check('resting 10 s cools to +2.0 (got ' + heat().toFixed(2) + ')', near(heat(), 2.0));
var wetAfterRest = WET.value;
check('sweat stops once below the cap and LSO dries it (wet ' + wetAfterRest + ')', wetAfterRest < 100);
seconds(15, 0);
check('resting long removes the modifier', Object.keys(P.attr.mods).length === 0);

P.sprint = true;
seconds(10, 1.0);
check('sprint key against a wall (1 b/s) does not count', near(heat(), 0));
P.sprint = false;

DOING.ClingToCliff = true;
seconds(20, 0);
check('hanging on a ledge 20 s gives +2.0 (got ' + heat().toFixed(2) + ')', near(heat(), 2.0));
DOING.ClingToCliff = false;
DOING.HangDown = true;
seconds(10, 0);
check('hanging from a bar keeps rising (+3.0, got ' + heat().toFixed(2) + ')', near(heat(), 3.0));
DOING.HangDown = false;
DOING.Vault = true;
seconds(5, 4);
check('other ParCool moves hold the heat (got ' + heat().toFixed(2) + ')', near(heat(), 3.0));
DOING.Vault = false;

P.sprint = true;
P.water = true;
seconds(5, 5.6);
check('sprint-swimming does not add heat (got ' + heat().toFixed(2) + ')', near(heat(), 2.0));
P.water = false;

P.x += 500;
second(5.6);
check('teleport second does not count (got ' + heat().toFixed(2) + ')', near(heat(), 1.8));
P.sprint = false;

P.creative = true;
second(0);
check('creative clears the heat', Object.keys(P.attr.mods).length === 0);
P.creative = false;

P.attr = makeAttr();
HANDLERS.respawned({ player: P });
P.sprint = true;
seconds(3, 5.6);
// The first second after a respawn has no previous position, so it does not count as running.
check('respawn starts cool and re-adds the modifier on the new body (got ' + heat().toFixed(2) + ')', near(heat(), 0.2));
