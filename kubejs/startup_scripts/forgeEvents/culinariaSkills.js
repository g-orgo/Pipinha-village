console.info("[SOCIETY] culinariaSkills.js loaded");

// XP granted to the society:culinaria Puffish category from confirmed cuts on
// a Farmer's Delight cutting board. A right-click with a knife only starts a
// check: one tick later the stored item is compared with the one before the
// click, and XP is granted only if the board actually consumed it.
// The Extra Portions and Double Harvest perks read what the cut produced: item
// entities around the board that were not there before the click.
const CULINARIA_CATEGORY = "society:culinaria";
const CUTTING_BOARD_XP = 3;
const CUTTING_BOARD_BLOCK = "farmersdelight:cutting_board";
const CUTTING_EXTRA_CHANCE = 1 / 3;
const CUTTING_DOUBLE_CHANCE = 1 / 50;

const listBoardDrops = (level, pos) => {
  let drops = [];
  level.getEntitiesWithin(AABB.ofBlock(pos).inflate(1)).forEach((entity) => {
    if (String(entity.getType()) === "minecraft:item") drops.push(entity);
  });
  return drops;
};

const giveCutOutput = (clicker, stack, count) => {
  // A copy keeps the NBT of the output, such as its quality.
  let output = stack.copy();
  output.setCount(count);
  clicker.give(output);
};

const applyCuttingPerks = (clicker, level, pos, knownDrops) => {
  let outputs = [];
  listBoardDrops(level, pos).forEach((entity) => {
    if (!knownDrops[String(entity.getUuid())]) outputs.push(entity.getItem());
  });
  if (outputs.length === 0) return;

  if (clicker.stages.has("culinaria_extra") && Math.random() < CUTTING_EXTRA_CHANCE) {
    giveCutOutput(clicker, outputs[0], 1);
  }
  if (clicker.stages.has("culinaria_double") && Math.random() < CUTTING_DOUBLE_CHANCE) {
    outputs.forEach((stack) => giveCutOutput(clicker, stack, stack.getCount()));
  }
};

// Runs Puffish's own "experience add" command as the server. Cooks get the
// profession XP boost (global.professionBoostedXp, professionGlobals.js).
global.grantCulinariaXp = (player, amount) => {
  if (amount <= 0) return;
  let gained = global.professionBoostedXp(player, "culinaria", amount);
  player
    .getServer()
    .runCommandSilent(
      `puffish_skills experience add ${player.username} ${CULINARIA_CATEGORY} ${gained}`
    );
};

global.handleCuttingBoardRightClick = (e) => {
  try {
    let clicker = e.getEntity();
    if (clicker.level.isClientSide() || clicker.isFake()) return;

    let level = e.getLevel();
    let pos = e.getPos();
    if (String(level.getBlock(pos).getId()) !== CUTTING_BOARD_BLOCK) return;

    let heldId = String(clicker.getHeldItem("main_hand").getId());
    if (!heldId.startsWith("farmersdelight:") || !heldId.endsWith("_knife")) return;

    let be = level.getBlockEntity(pos);
    if (!be) return;
    let before = be.getStoredItem();
    if (before.isEmpty()) return;
    let beforeCount = before.getCount();

    let hasPerk = clicker.stages.has("culinaria_extra") || clicker.stages.has("culinaria_double");
    let knownDrops = {};
    if (hasPerk) {
      listBoardDrops(level, pos).forEach((entity) => {
        knownDrops[String(entity.getUuid())] = true;
      });
    }

    let server = clicker.getServer();
    server.scheduleInTicks(1, () => {
      try {
        let after = level.getBlockEntity(pos);
        if (!after) return;
        let stored = after.getStoredItem();
        if (stored.isEmpty() || stored.getCount() < beforeCount) {
          global.grantCulinariaXp(clicker, CUTTING_BOARD_XP);
          if (hasPerk) applyCuttingPerks(clicker, level, pos, knownDrops);
        }
      } catch (err) {
        console.error(`[culinaria] cutting board check failed: ${err}`);
      }
    });
  } catch (err) {
    console.error(`[culinaria] cutting board hook failed: ${err}`);
  }
};

// The body lives in a global function on purpose: declaring a local "player"
// directly inside the inline event callback makes Rhino throw
// "redeclaration of var player" on every click.
NativeEvents.onEvent("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$RightClickBlock", (e) => {
  global.handleCuttingBoardRightClick(e);
});
