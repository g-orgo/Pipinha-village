// Tests for cookFirstDish.js. Runs after the stubs, the generated list and the script.
check('generated list loaded (' + COOK_FIRST_DISH_IDS.length + ' ids)', COOK_FIRST_DISH_IDS.length > 500);
var ALL_IDS = COOK_FIRST_DISH_IDS;

function poll() { for (var i = 0; i < 10; i++) { P.age++; HANDLERS.tick({ player: P }); } }
function xp() { return P.xp.culinaria || 0; }
function done(id) { return P.persistentData.getCompound('sunlitCookFirstDishes').contains(id); }
function click(blockId, change) {
  HANDLERS.click({ player: P, block: { id: blockId }, hand: 'MAIN_HAND' });
  change();
  var jobs = SCHEDULED; SCHEDULED = []; jobs.forEach(function (fn) { fn(); });
}

// Baseline: dishes crafted before the feature are done without pay.
P.crafted['bakery:sandwich'] = 2;
HANDLERS.loggedIn({ player: P });
check('baseline marks old dish done', done('bakery:sandwich'));
check('baseline pays nothing', xp() === 0 && GIVEN.length === 0);
check('carton is not in the generated list', ALL_IDS.indexOf('society:tubasmoke_carton') === -1);

poll();
check('first poll only snapshots', xp() === 0);
P.crafted['farmersdelight:beef_stew'] = 1; poll();
check('first beef stew: 15 + 90/10 = 24 XP (got ' + xp() + ')', xp() === 24);
check('coins = value 90: cog + sprocket + bevel + 2 spur (got ' + GIVEN.join(',') + ')',
  GIVEN.join(',') === 'numismatics:cogx1,numismatics:sprocketx1,numismatics:bevelx1,numismatics:spurx2');
check('message shows boosted XP 36', TOLD[0].key === 'society.cook.first_dish' && TOLD[0].args[2] === '36' && TOLD[0].args[1] === '90');
P.crafted['farmersdelight:beef_stew'] = 2; poll();
check('second beef stew pays nothing (got ' + xp() + ')', xp() === 24);

// Shop purchase raises the crafted stat but never pays.
P.containerMenu = menu('ShopMenu'); P.age++; HANDLERS.tick({ player: P });
P.containerMenu = menu('InventoryMenu');
P.crafted['farmersdelight:hot_cocoa'] = 1; poll();
check('bought cocoa (shop menu in window) pays nothing', xp() === 24 && !done('farmersdelight:hot_cocoa'));
P.crafted['farmersdelight:hot_cocoa'] = 2; poll();
check('cocoa made later pays: 15 + 4 = 19', xp() === 43 && done('farmersdelight:hot_cocoa'));

// Not a cook: nothing, and no done mark.
P.cook = false; P.crafted['farmersdelight:roast_chicken_block'] = 1; poll();
check('non-cook gets nothing', xp() === 43 && !done('farmersdelight:roast_chicken_block'));
P.cook = true; poll();
check('becoming a cook only restarts the snapshot', xp() === 43);

// Station click: feast placed into a station and taken back never pays.
P.inv = [{ id: 'farmersdelight:roast_chicken_block', count: 1 }];
click('kaleidoscope_cookery:steamer', function () { P.inv[0].count = 0; });
click('kaleidoscope_cookery:steamer', function () { P.inv[0].count = 1; });
check('dish put into a station and taken back pays nothing', xp() === 43);
click('minecraft:chest', function () { P.inv[0].count = 2; });
check('non-station block is ignored', xp() === 43);

// A new dish taken from a station pays once (feast block value 600 -> XP capped 75).
delete P.persistentData.m.sunlitCookDeposited;
click('kaleidoscope_cookery:pot', function () { P.inv[0].count = 3; });
check('station dish pays: 15 + 60 = 75 (got ' + xp() + ')', xp() === 118 && done('farmersdelight:roast_chicken_block'));
click('kaleidoscope_cookery:pot', function () { P.inv[0].count = 4; });
check('second station dish pays nothing', xp() === 118);
check('XP cap is 120', cookFdXp(100000) === 120);
