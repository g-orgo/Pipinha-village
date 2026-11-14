console.info("[SOCIETY] customBlockEntityBroken.js loaded");

const handleBrokenMachine = (block) => {
  const machine = global.artisanMachineDefinitions.filter((obj) => {
    return obj.id === block.id;
  })[0];
  if (!machine) return;
  let working = block.properties.get("working").toLowerCase() == "true";
  if (machine.upgrade && block.properties.get("upgraded").toLowerCase() == "true") {
    block.popItem(machine.upgrade);
  }
  const nbt = block.getEntityData();
  // 1.21.1: NBT fields are Tag objects; read them through global.nbtStr/nbtNum.
  const recipeId = global.nbtStr(nbt.data.recipe);
  const currentRecipe = machine.recipes.get(recipeId);
  if (block.properties.get("mature").toLowerCase() == "true") {
    (currentRecipe ? currentRecipe.output : []).forEach((element) => {
      block.popItem(element);
    });
    if (
      currentRecipe &&
      block.id == "society:ancient_cask" &&
      block.properties.get("upgraded").toLowerCase() == "true"
    ) block.popItem(Item.of(`3x ${Item.of(`${currentRecipe.output[0]}`).id}`));
  } else if (!["society:charging_rod", "society:tapper", "society:mushroom_log"].includes(block.id)) {
    let stage = global.nbtNum(nbt.data.stage);
    if (
      currentRecipe &&
      block.id == "society:ancient_cask" &&
      block.properties.get("upgraded").toLowerCase() == "true"
    ) {
      if (working) block.popItem(Item.of(`4x ${recipeId}`));
      else block.popItem(Item.of(`${stage}x ${recipeId}`));
    } else if (
      block.id == "society:deluxe_worm_farm" &&
      block.properties.get("upgraded").toLowerCase() == "true"
    ) {
      // Do nothing because of infinity worm upgrade
    } else if (
      currentRecipe &&
      block.id == "society:preserves_jar" &&
      block.properties.get("upgraded").toLowerCase() == "true"
    ) {
      if (working) block.popItem(Item.of(`3x ${recipeId}`));
      else block.popItem(Item.of(`${stage}x ${recipeId}`));
    } else if (currentRecipe) {
      if (nbt.data.originalInputs && nbt.data.originalInputs.size() > 0) {
        nbt.data.originalInputs.forEach((item) => {
          block.popItem(Item.of(`${global.nbtNum(item.Count)}x ${global.nbtStr(item.id)}`));
        });
      } else {
        if (working) block.popItem(Item.of(`${machine.maxInput}x ${recipeId}`));
        else block.popItem(Item.of(`${stage}x ${recipeId}`));
      }
    }
  }
};

BlockEvents.broken(global.artisanMachineIds, (e) => {
  handleBrokenMachine(e.block);
});

BlockEvents.broken("society:fish_pond", (e) => {
  const { block } = e;
  const nbt = block.getEntityData();
  const fishType = global.nbtStr(nbt.data.type);
  if (fishType !== "") {
    block.popItem(
      Item.of(
        "society:fish_pond",
        `{type:"${fishType}",population:${global.nbtNum(nbt.data.population)},max_population:${global.nbtNum(
          nbt.data.max_population
        )},quest:${block.properties.get("quest")},quest_id:${global.nbtNum(nbt.data.quest_id)}}`
      )
    );
  } else {
    block.popItem(Item.of("society:fish_pond"));
  }
  if (block.properties.get("upgraded").toLowerCase() == "true") {
    block.popItem(Item.of("society:sea_biscut"));
  }
});

BlockEvents.broken("society:prize_machine", (e) => {
  const nbt = e.block.getEntityData();
  e.block.popItem(Item.of("society:prize_machine", `{prize:${global.nbtNum(nbt.data.prize)}}`));
});

BlockEvents.broken("society:coin_leaderboard", (e) => {
  global.clearOldTextDisplay(e.block, e.level, "leaderboard");
});

BlockEvents.broken("society:shipping_bin_monitor", (e) => {
  global.clearOldTextDisplay(e.block, e.level, "shipping_bin_monitor");
});

BlockEvents.broken("society:fish_pond_basket", (e) => {
  const { block } = e;
  if (block.properties.get("upgraded").toLowerCase() == "true") {
    block.popItem(Item.of("minecraft:bucket"));
  }
});
BlockEvents.broken("society:auto_grabber", (e) => {
  const { block } = e;
  if (block.properties.get("upgraded").toLowerCase() == "true") {
    block.popItem(Item.of("society:magic_shears"));
  }
});
