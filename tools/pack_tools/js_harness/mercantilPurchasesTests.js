// Scenarios for mercantilPurchases.js (run after the stubs, the globals and the script).
check('handlers registered', typeof HANDLERS.tick === 'function' && typeof HANDLERS.pickedUp === 'function');

var m = shopMenu();
P.containerMenu = m;
m.selected = offer('minecraft:wheat_seeds', 1, 25);
tick();
give('minecraft:wheat_seeds', 1); tick();
check('buying 25 spurs gives 10 XP (got ' + xp() + ')', xp() === 10);
give('minecraft:wheat_seeds', 3); tick();
check('three more (100 total) follow the curve: 20 XP (got ' + xp() + ')', xp() === 20);

m.selected = offer('minecraft:bread', 4, 300);
tick();
give('minecraft:bread', 8); tick();
check('stack of 4 per trade: 2 trades = 600 spurs, 700 total: 53 XP (got ' + xp() + ')', xp() === 53);
give('minecraft:bread', 4 * 20); tick();
check('daily cap of 100 XP (got ' + xp() + ')', xp() === 100);
give('minecraft:bread', 4); tick();
check('nothing past the cap (got ' + xp() + ')', xp() === 100);

P.level.day = 2;
pickup('minecraft:bread', 4); tick();
check('picking up the item does not count (got ' + xp() + ')', xp() === 100);
m.carried = stack('minecraft:bread', 4); tick();
check('item bought onto the cursor counts on the new day (got ' + xp() + ')', xp() === 135);

m.selected = offer('minecraft:oak_planks', 1, 0);
tick(); give('minecraft:oak_planks', 10); tick();
check('barter trade (no spur cost) gives nothing (got ' + xp() + ')', xp() === 135);
m.selected = offer('numismatics:prismatic_coin', 1, 5000);
tick(); give('numismatics:prismatic_coin', 1); tick();
check('coin result (exchange) gives nothing (got ' + xp() + ')', xp() === 135);

P.containerMenu = INVENTORY_MENU; tick();
give('minecraft:bread', 4); tick();
check('no shop open: nothing (got ' + xp() + ')', xp() === 135);
var m2 = shopMenu('ImageShopMenu');
P.containerMenu = m2; m2.selected = offer('minecraft:bread', 4, 300);
give('minecraft:bread', 4); tick();
check('first tick after opening only snapshots (got ' + xp() + ')', xp() === 135);
give('minecraft:bread', 4); tick();
check('ImageShopMenu purchases count (got ' + xp() + ')', xp() > 135);

P.level.day = 3; P.xp = {};
var m3 = shopMenu('ThinShopMenu');
P.containerMenu = m3; m3.selected = offer('minecraft:apple', 1, 4);
tick(); give('minecraft:apple', 1); tick(); give('minecraft:apple', 1); tick(); give('minecraft:apple', 1); tick(); give('minecraft:apple', 1); tick();
check('four 4-spur buys equal one 16-spur buy: 8 XP (got ' + xp() + ')', xp() === 8);
