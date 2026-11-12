console.info("[SOCIETY] animalBase.js loaded");

const checkAnimal = global.animalBaseHelpers.checkAnimal;
const upgradeAnimal = global.animalBaseHelpers.upgradeAnimal;
const handleSpecialItem = global.animalBaseHelpers.handleSpecialItem;

// Game time of the last pet-first click per animal UUID. The off-hand event of the
// same click is cancelled too, so the vanilla/mod interaction never runs.
const petFirstTicks = {};

ItemEvents.entityInteracted((e) => {
  let { hand, player, item, target, level, server } = e;
  if (item === 'moblassos:diamond_lasso') return;
  let uuid = String(target.uuid);
  let now = Number(level.getLevelData().getGameTime());
  if (String(hand) === "OFF_HAND" && petFirstTicks[uuid] === now) {
    e.cancel();
    return;
  }
  if (global.sunlitShouldPetFirst(hand, player, item, target, level)) {
    // Keep only the entries of this tick, so the map never grows.
    Object.keys(petFirstTicks).forEach((key) => {
      if (petFirstTicks[key] !== now) delete petFirstTicks[key];
    });
    petFirstTicks[uuid] = now;
    global.handleHusbandryBase(hand, player, item, target, level, server);
    // Safety net: a petting click never leaves the player riding the animal.
    server.scheduleInTicks(1, () => {
      let vehicle = player.getVehicle();
      if (vehicle && String(vehicle.uuid) === uuid) player.stopRiding();
    });
    e.cancel();
    return;
  }
  global.handleHusbandryBase(hand, player, item, target, level, server);
});

BlockEvents.rightClicked(global.plushies, (e) => {
  let { level, hand, player, item, server, block } = e;
  if (hand == "OFF_HAND") return;
  let nbt = block.getEntityData();
  if (!nbt) return;
  let { animal } = nbt.data;
  if (!animal) return;
  let animalName = animal.name ? Text.of(animal.name) : global.getTranslatedEntityName(String(animal.type));
  if (item === "minecraft:air") {
    checkAnimal(
      player,
      level,
      server,
      animal,
      animalName,
      256,
      10
    );
  }
  global.executePlushieHusbandry(
    level,
    server,
    player,
    item,
    block,
    handleSpecialItem
  );
  if (
    player.stages.has("clockwork") &&
    item === "create:precision_mechanism" &&
    !animal.clockwork
  ) {
    nbt.merge({
      data: {
        animal: {
          clockwork: true,
        },
      },
    });
    upgradeAnimal(
      level,
      server,
      item,
      block,
      "trials:vault_activate",
      "supplementaries:bomb_explosion"
    );
    if (animal.bff) {
      nbt.merge({
        data: {
          animal: {
            bff: false,
          },
        },
      });
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          global.animalMessageSettings,
          80,
          Text.translatable("society.husbandry.mechanization").toJson()
        )
      );
    }
  }
  if (
    player.stages.has("husbandry_mastery") &&
    item === "society:animal_cracker" &&
    !animal.animalCracker
  ) {
    nbt.merge({
      data: {
        animal: {
          animalCracker: true,
        },
      },
    });
    server.runCommandSilent(
      `playsound minecraft:entity.generic.eat block @a ${player.x} ${player.y} ${player.z}`
    );
    upgradeAnimal(
      level,
      server,
      item,
      block,
      "stardew_fishing:chest_get",
      "farmersdelight:star"
    );
  }
  if (
    player.stages.has("bff") &&
    item === "society:friendship_necklace" &&
    !animal.bff
  ) {
    nbt.merge({
      data: {
        animal: {
          bff: true,
        },
      },
    });
    upgradeAnimal(
      level,
      server,
      item,
      block,
      "buzzier_bees:buttercup_bloom"
    );
    if (animal.clockwork) {
      nbt.merge({
        data: {
          animal: {
            clockwork: false,
          },
        },
      });
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          `{anchor:"BOTTOM_CENTER",background:1,wrap:220,align:"BOTTOM_CENTER",color:"#55FF55",offsetY:20}`,
          80,
          Text.translatable("society.husbandry.emancipation").toJson()
        )
      );
    }
  }
  global.setBlockEntityData(block, nbt)
});
