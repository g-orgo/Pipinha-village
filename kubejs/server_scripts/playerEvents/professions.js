console.info("[SOCIETY] professions.js loaded");

// Profession choice and tree sync. Definitions, the profession limit and the
// XP boost live in startup_scripts/professions/professionGlobals.js. The five
// trees are always unlocked; the limit is the only gate on choosing.
// Contract quests (chapter "profissoes") carry the tag
// "sunlit_profession_<id>" and one custom task with a button: clicking it runs
// the check below, which grants the profession when the rules allow it.
// FTBQuestsEvents.customTask is keyed by the task id, not by the quest tag.
const professionContractTasks = {
  farmer: "6C85CC8060BA68C2",
  rancher: "4B71DBBC6FB0D822",
  fisher: "41A9A408D04E2F1F",
  winemaker: "38E09E8437EEF861",
  cook: "1AA7B4ABC5E7426A",
};

// Starter equipment handed over once, when the contract is signed.
const professionKits = {
  farmer: [
    "dew_drop_watering_cans:iron_watering_can",
    "minecraft:iron_hoe",
    "kaleidoscope_cookery:straw_hat",
    "kaleidoscope_cookery:farmer_leggings",
    "kaleidoscope_cookery:farmer_boots",
    "32x minecraft:bone_meal",
  ],
  rancher: ["society:milk_pail", "minecraft:shears", "2x minecraft:lead", "32x society:animal_feed"],
  fisher: [
    "aquaculture:iron_fishing_rod",
    "aquaculture:iron_fillet_knife",
    "aquaculture:tackle_box",
    "32x aquaculture:worm",
  ],
  winemaker: [
    "vinery:straw_hat",
    "vinery:winemaker_apron",
    "vinery:winemaker_leggings",
    "vinery:winemaker_boots",
    "8x vinery:red_grape_seeds",
    "8x vinery:white_grape_seeds",
    "16x vinery:wine_bottle",
  ],
  cook: [
    "kaleidoscope_cookery:iron_kitchen_knife",
    "farmersdelight:cooking_pot",
    "farmersdelight:skillet",
    "farmersdelight:cutting_board",
  ],
};

const professionName = (id) => Text.translatable(`society.profession.${id}`);

ServerEvents.loaded((e) => {
  global.professionIds.forEach((id) => {
    e.server.runCommandSilent(`scoreboard objectives add ${global.professionObjective(id)} dummy`);
  });
});

PlayerEvents.loggedIn((e) => {
  global.syncProfessions(e.server, e.player);
});

global.professionIds.forEach((id) => {
  FTBQuestsEvents.customTask(professionContractTasks[id], (e) => {
    e.setCheckTimer(0);
    e.setEnableButton(true);
    e.setMaxProgress(1);
    e.setCheck((task, player) => {
      let blocker = global.professionBlocker(player, id);
      if (blocker === "society.profession.already") {
        // Already signed: complete the quest anyway, so a contract signed
        // before a failed tree unlock never stays stuck at 0.
        task.setProgress(1);
        global.syncProfessions(player.server, player);
        player.tell(Text.translatable(blocker, professionName(id)).gray());
        return;
      }
      if (blocker === "society.profession.limit") {
        // Limit reached: the contract stays open, so it is not completed.
        let chosen = global.getProfessions(player);
        player.tell(
          Text.translatable(
            blocker,
            String(global.professionLimit(player)),
            professionName(chosen[0])
          ).gray()
        );
        return;
      }
      player.stages.add(global.professionStage(id));
      task.setProgress(1);
      console.info(`[professions] contract signed: ${player.username} -> ${id}`);
      global.syncProfessions(player.server, player);
      player.server.runCommandSilent(
        `playsound minecraft:ui.toast.challenge_complete player ${player.username} ${player.x} ${player.y} ${player.z}`
      );
      player.tell(
        Text.translatable(
          "society.profession.chosen",
          professionName(id),
          global.translatableWithFallback(`society_skills.${global.professions[id].tree}.category.title`, id)
        ).gold()
      );
      professionKits[id].forEach((item) => player.give(item));
      player.tell(Text.translatable("society.profession.kit", professionName(id)).green());
    });
  });
});
