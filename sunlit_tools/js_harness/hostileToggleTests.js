// Scenarios for hostileSpawnToggle.js (startup + server). See run_hostile_toggle.sh.
var SPAWN = 'net.minecraftforge.event.entity.living.MobSpawnEvent$FinalizeSpawn';
var INIT = 'net.minecraftforge.client.event.ScreenEvent$Init$Post';
var RENDER = 'net.minecraftforge.client.event.ScreenEvent$Render$Pre';

function spawnEvent(category, type) {
  var ev = {
    cancelled: false,
    getEntity: function () {
      return { getType: function () { return { getCategory: function () { return enumv(category); } }; }, getServer: function () { return SERVER; } };
    },
    getSpawnType: function () { return enumv(type); },
    setSpawnCancelled: function (v) { this.cancelled = v; },
  };
  HANDLERS[SPAWN](ev);
  return ev.cancelled;
}

check('handlers registered', !!HANDLERS[SPAWN] && !!HANDLERS[INIT] && !!HANDLERS[RENDER]);
check('spawns on by default: zombie natural allowed', spawnEvent('MONSTER', 'NATURAL') === false);
SERVER.persistentData.putBoolean('sunlitHostileSpawnsOff', true);
check('off: zombie natural cancelled', spawnEvent('MONSTER', 'NATURAL') === true);
check('off: spawner cancelled', spawnEvent('MONSTER', 'SPAWNER') === true);
check('off: chunk generation cancelled', spawnEvent('MONSTER', 'CHUNK_GENERATION') === true);
check('off: spawn egg allowed', spawnEvent('MONSTER', 'SPAWN_EGG') === false);
check('off: command allowed', spawnEvent('MONSTER', 'COMMAND') === false);
check('off: raid (EVENT) allowed', spawnEvent('MONSTER', 'EVENT') === false);
check('off: cow natural allowed', spawnEvent('CREATURE', 'NATURAL') === false);
SERVER.persistentData.putBoolean('sunlitHostileSpawnsOff', false);

function initEvent(screen) {
  var added = [];
  HANDLERS[INIT]({ getScreen: function () { return screen; }, addListener: function (w) { added.push(w); screen.list.push(w); } });
  return added;
}
function screenOf(name, list) {
  return { list: list, getClass: function () { return cls(name); }, children: function () { var l = this.list; return { forEach: function (f) { l.slice().forEach(f); } }; } };
}
function difficultyButton(x, y, w) {
  return widget('net.minecraft.client.gui.components.CycleButton', x, y, w, { getValue: function () { return { getClass: function () { return cls('net.minecraft.world.Difficulty'); } }; } });
}

// Options screen, normal world: difficulty 130 + lock 20 at x=200.
var diff = difficultyButton(200, 50, 130);
var lock = widget('net.minecraft.client.gui.components.LockIconButton', 330, 50, 20, { locked: false, setLocked: function (v) { this.locked = v; } });
var fov = widget('net.minecraft.client.gui.components.AbstractSliderButton', 40, 50, 150, {});
var added = initEvent(screenOf('net.minecraft.client.gui.screens.OptionsScreen', [fov, diff, lock]));
check('options: two toggle buttons added', added.length === 2);
check('options: difficulty greyed and 110 wide', diff.active === false && diff.w === 110);
check('options: lock shown locked, greyed, moved to 310', lock.locked === true && lock.active === false && lock.x === 310);
check('options: toggle at 330,50 (old lock spot)', added[0].x === 330 && added[0].y === 50 && added[1].x === 330);
check('options: row still ends at 350', added[0].x + 20 === 350);
check('options: excalibur texture', added[0].tex.path === 'textures/gui/hostile_spawns_excalibur.png');
check('options: on visible, off hidden', added[0].visible === true && added[1].visible === false);
check('options: uv on=0 off=20', added[0].u === 0 && added[1].u === 20);
added[0].press();
SERVER.runQueue();
check('options: press turns spawns off on the server', SERVER.persistentData.getBoolean('sunlitHostileSpawnsOff') === true);
check('options: now off visible', added[0].visible === false && added[1].visible === true);
added[1].press();
SERVER.runQueue();
check('options: press again turns spawns on', SERVER.persistentData.getBoolean('sunlitHostileSpawnsOff') === false);

// Options screen, hardcore (no lock).
var diffH = difficultyButton(200, 50, 150);
var addedH = initEvent(screenOf('net.minecraft.client.gui.screens.OptionsScreen', [diffH]));
check('options hardcore: toggle right of difficulty', diffH.w === 130 && addedH[0].x === 330);

// Options screen from the title screen (no world): nothing added.
MC.level = null;
check('options without world: nothing added', initEvent(screenOf('net.minecraft.client.gui.screens.OptionsScreen', [])).length === 0);
MC.level = {};

// Vanilla texture without Excalibur.
SELECTED_PACKS = ['vanilla'];
var diffV = difficultyButton(200, 50, 130);
var addedV = initEvent(screenOf('net.minecraft.client.gui.screens.OptionsScreen', [diffV]));
check('vanilla texture without excalibur', addedV[0].tex.path === 'textures/gui/hostile_spawns.png');

// Create world screen, Game tab: gamemode 210 at x=100, difficulty below.
var gm = widget('net.minecraft.client.gui.components.CycleButton', 100, 80, 210, { getValue: function () { return { getClass: function () { return cls('x.SelectedGameMode'); } }; } });
var diffC = difficultyButton(100, 108, 210);
var create = screenOf('net.minecraft.client.gui.screens.worldselection.CreateWorldScreen', [gm, diffC]);
var addedC = initEvent(create);
function frame() { HANDLERS[RENDER]({ getScreen: function () { return create; } }); }
check('create: pending reset to spawns on', global.pendingHostileSpawnsOff === false);
frame();
check('create: difficulty greyed, 190 wide', diffC.active === false && diffC.w === 190 && diffC.x === 100);
check('create: toggle at 290,108 and on visible', addedC[0].x === 290 && addedC[0].y === 108 && addedC[0].visible && !addedC[1].visible);
addedC[0].press();
frame();
check('create: press sets pending off', global.pendingHostileSpawnsOff === true && addedC[1].visible && !addedC[0].visible);
create.list = [addedC[0], addedC[1]];
frame();
check('create: other tab hides toggle', !addedC[0].visible && !addedC[1].visible);
create.list = [gm, diffC, addedC[0], addedC[1]];
diffC.x = 110;
frame();
check('create: back on Game tab, realigned, off shown', diffC.x === 100 && addedC[1].visible && addedC[1].x === 290);

// Server: new world gets the pending choice, old world does not.
SERVER.dayTime = 5;
SERVER_HANDLERS.loaded({ server: SERVER });
check('server: new world gets spawns off', SERVER.persistentData.getBoolean('sunlitHostileSpawnsOff') === true);
check('server: pending cleared', global.pendingHostileSpawnsOff === null);
SERVER.persistentData.putBoolean('sunlitHostileSpawnsOff', false);
global.pendingHostileSpawnsOff = true;
SERVER.dayTime = 50000;
SERVER_HANDLERS.loaded({ server: SERVER });
check('server: old world untouched', SERVER.persistentData.getBoolean('sunlitHostileSpawnsOff') === false && global.pendingHostileSpawnsOff === null);
