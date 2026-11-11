// Scenarios for globalRegistryCreateMetals.js and the Create metal parts of globalShippingBinHandlers.js.
var MARKED = makeNbt({ SunlitArtificial: 1 });
var UNMARKED = makeNbt({ SunlitArtificial: 0 });
var NONE = undefined;
var NO_STAGES = stagesOf([]);
var MINER = stagesOf(['industrial_miner']);

// Price registry
check('registry: 16 create metal ids exposed', global.createMetalItems.length === 16);
check('registry: iron nugget priced 1', global.trades.get('minecraft:iron_nugget').value === 1);
check('registry: gold block priced 198', global.trades.get('minecraft:gold_block').value === 198);
check('registry: crushed zinc priced 11', global.trades.get('create:crushed_raw_zinc').value === 11);
check('registry: copper block priced 45', global.trades.get('minecraft:copper_block').value === 45);
check('registry: multiplier is gem sell', global.trades.get('create:zinc_ingot').multiplier === 'shippingbin:gem_sell_multiplier');
check('registry: wheat untouched', !global.trades.has('minecraft:wheat'));

// Penalty on the stack total
check('penalty: 64 marked iron nuggets -> 45', global.createStackSaleValue(1, 64, 1, MARKED) === 45);
check('penalty: 64 unmarked iron nuggets -> 64', global.createStackSaleValue(1, 64, 1, UNMARKED) === 64);
check('penalty: 64 nuggets without NBT -> 64', global.createStackSaleValue(1, 64, 1, NONE) === 64);

// industrial_miner bonus (per item, before the penalty)
var ingotMiner = global.createMetalStageValue(11, 'minecraft:iron_ingot', MINER);
check('bonus: iron ingot with industrial_miner per item -> 14', ingotMiner === 14);
check('bonus: marked iron ingot x10 with industrial_miner -> 98', global.createStackSaleValue(ingotMiner, 10, 1, MARKED) === 98);
check('bonus: unmarked iron ingot x10 with industrial_miner -> 140', global.createStackSaleValue(ingotMiner, 10, 1, UNMARKED) === 140);
check('bonus: no stage -> per item unchanged', global.createMetalStageValue(11, 'minecraft:iron_ingot', NO_STAGES) === 11);
check('bonus: industrial_miner on non-metal ignored', global.createMetalStageValue(7, 'minecraft:wheat', MINER) === 7);

// Non-metal item keeps the old math
check('non-metal: wheat x3 unchanged', global.createStackSaleValue(7, 3, 1, NONE) === 21);
check('marked: any item with SunlitArtificial gets the penalty (wheat x3 -> 15)', global.createStackSaleValue(7, 3, 1, MARKED) === 15);

// Mining XP from a sale worth 99 coins (floor(99 / 5))
var xpCalls = [];
global.giveExperience = function (server, player, category, xp) { xpCalls.push([category, xp]); };
global.handleShippingBinDebt = function (value) { return value; };
global.coinMap = {};
var basicCoinMap = {};
global.calculateCoinsFromValue = function () { return []; };
global.lastCreateMetalSaleValue = 99;
try { global.processValueOutput(99, 1, [], { username: 'test', isFake: function () { return false; } }, {}, {}, {}, false, 'uuid'); } catch (e) { OUT.push('     exc: ' + e); }
check('xp: 99 coins of metal -> 19 mining XP once', xpCalls.length === 1 && xpCalls[0][0] === 'mining' && xpCalls[0][1] === 19);
check('xp: accumulator reset after the sale', global.lastCreateMetalSaleValue === 0);
xpCalls = [];
global.lastCreateMetalSaleValue = 4;
try { global.processValueOutput(4, 1, [], {}, {}, {}, {}, false, 'uuid'); } catch (e) { }
check('xp: 4 coins of metal -> no XP call', xpCalls.length === 0);
