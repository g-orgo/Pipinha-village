console.info("[SOCIETY] hoeAoe.js loaded");

// Area per hoe while crouching: 0 = single block, below 1 = line ahead (2 or 3 blocks), 1+ = square radius.
// Every hoe of the pack is listed: a hoe missing here falls back to vanilla tilling, which makes
// minecraft:farmland, where Sunrise Gardening grows nothing.
const hoeTiers = new Map([
  ["minecraft:wooden_hoe", 0],
  ["minecraft:stone_hoe", 0.2],
  ["minecraft:copper_hoe", 0.2],
  ["minecraft:iron_hoe", 0.5],
  ["mapperbase:steel_hoe", 0.5],
  ["minecraft:golden_hoe", 1],
  ["minecraft:diamond_hoe", 2],
  ["botania:manasteel_hoe", 2],
  ["minecraft:netherite_hoe", 3],
  ["aquaculture:neptunium_hoe", 3],
  ["botania:elementium_hoe", 3],
]);

const hoeFarmland = new Map([
  ["aquaculture:neptunium_hoe", "sunrisegardening:hydrating_farmland"],
  ["botania:elementium_hoe", "sunrisegardening:hydrating_farmland"],
]);

const tryTill = (level, player, pos, farmland) => {
  const ground = level.getBlock(pos);
  if (!ground.hasTag("minecraft:dirt")) return false;
  const above = String(level.getBlock(pos.above()).id);
  if (
    above !== "minecraft:air" &&
    above !== "minecraft:water" &&
    above !== "minecraft:flowing_water"
  )
    return false;

  // 1.21.1: Sunrise Gardening only grows crops on its own tilled soil (Dew Drop replaced
  // minecraft:farmland in 1.20.1), so plain tilling makes sunrisegardening:tilled_soil.
  ground.set(farmland || "sunrisegardening:tilled_soil");
  player.swing();
  player.server.runCommandSilent(
    `playsound minecraft:item.hoe.till block @a ${player.x} ${player.y} ${player.z}`
  );
  return true;
};

BlockEvents.rightClicked(
  [
    "minecraft:dirt",
    "minecraft:rooted_dirt",
    "minecraft:coarse_dirt",
    "minecraft:dirt_path",
    "minecraft:grass_block",
  ],
  (e) => {
    const { item, block, player, level } = e;
    const id = `${item.id}`;
    if (!hoeTiers.has(id)) return;
    const hoe = hoeTiers.get(id);
    const farmland = hoeFarmland.get(id);
    // Rhino 2101: no const/let inside nested blocks, so every loop variable is declared here.
    const base = block.pos;
    let distance = 0;
    let pos = null;
    let i = 0;
    let dx = 0;
    let dz = 0;

    if (!player.isCrouching() || hoe === 0) {
      tryTill(level, player, base, farmland);
      e.cancel();
      return;
    }

    if (hoe < 1) {
      distance = hoe > 0.2 ? 3 : 2;
      pos = base;
      for (i = 0; i < distance && pos; i++) {
        tryTill(level, player, pos, farmland);
        pos = global.getFacing(player.facing, pos);
      }
    } else {
      for (dx = -hoe; dx <= hoe; dx++) {
        for (dz = -hoe; dz <= hoe; dz++) {
          tryTill(level, player, base.offset(dx, 0, dz), farmland);
        }
      }
    }
    global.addItemCooldown(player, item, 40);
  }
);
