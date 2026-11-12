console.info("[SOCIETY] professionCrystals.js loaded");

// Profession crystals sold by the Guild (guild.json).
// Crystal of Regret: Professions drops every profession the player follows and
// reopens their contract quests. Bought profession slots are kept.
// Crystal of Ambition: Professions adds one profession slot
// (global.addProfessionSlots). Its price rises with each crystal bought: the
// guild shows only the trade gated by profession_slot_offer_<n>, where n is
// the next purchase. A crystal counts as bought the first time it reaches a
// player inventory (it is then marked with sunlit_slot_bought), so storing
// crystals does not keep the price low.
const AMBITION_CRYSTAL = "society:crystal_of_ambition_professions";
const SLOTS_BOUGHT_KEY = "sunlitProfessionSlotsBought";

// Contract quest per profession (chapter profissoes.snbt).
const professionContractQuests = {
  farmer: "5B1F0A3C7D2E4F61",
  rancher: "5B1F0A3C7D2E4F62",
  fisher: "5B1F0A3C7D2E4F63",
  winemaker: "5B1F0A3C7D2E4F64",
  cook: "5B1F0A3C7D2E4F65",
};

const maxExtraSlots = () => global.professionIds.length - global.PROFESSION_LIMIT_DEFAULT;

const slotsBought = (player) =>
  Math.max(
    player.persistentData.getInt(SLOTS_BOUGHT_KEY) || 0,
    player.persistentData.getInt("sunlitProfessionSlots") || 0
  );

// Keeps exactly one profession_slot_offer_<n> stage, or none once every slot
// has been bought.
const syncSlotOffer = (player) => {
  let bought = slotsBought(player);
  for (let n = 1; n <= maxExtraSlots(); n++) {
    let stage = `profession_slot_offer_${n}`;
    let wanted = n === bought + 1;
    if (wanted && !player.stages.has(stage)) player.stages.add(stage);
    if (!wanted && player.stages.has(stage)) player.stages.remove(stage);
  }
};

PlayerEvents.loggedIn((e) => {
  syncSlotOffer(e.player);
});

PlayerEvents.inventoryChanged((e) => {
  if (!e.item || e.item.id !== AMBITION_CRYSTAL) return;
  let player = e.player;
  let fresh = 0;
  player.inventory.items.forEach((item) => {
    if (item.id !== AMBITION_CRYSTAL || global.getItemCustomTag(item).getBoolean('sunlit_slot_bought')) return;
    fresh += item.count;
    let crystalTag = global.getItemCustomTag(item);
    crystalTag.putBoolean('sunlit_slot_bought', true);
    global.setItemCustomTag(item, crystalTag);
  });
  if (fresh === 0) return;
  player.persistentData.putInt(SLOTS_BOUGHT_KEY, Math.min(maxExtraSlots(), slotsBought(player) + fresh));
  syncSlotOffer(player);
});

ItemEvents.rightClicked("society:crystal_of_regret_professions", (e) => {
  let { player, item, server } = e;
  let chosen = global.getProfessions(player);
  if (chosen.length === 0) {
    player.tell(Text.translatable("society.crystal_of_regret_professions.fail").red());
    return;
  }
  chosen.forEach((id) => {
    player.stages.remove(global.professionStage(id));
    server.runCommandSilent(
      `ftbquests change_progress ${player.username} reset ${professionContractQuests[id]}`
    );
  });
  // Scoreboard boost and Mercantil discount stages follow the professions.
  global.syncProfessions(server, player);
  global.syncMercantilStages(player);
  server.runCommandSilent(
    `playsound stardew_fishing:fish_escape block @a ${player.x} ${player.y} ${player.z}`
  );
  item.count--;
  console.info(`[professions] reset: ${player.username} dropped ${chosen.join(", ")}`);
  player.tell(
    Text.translatable(
      "society.crystal_of_regret_professions.success",
      String(global.professionLimit(player))
    ).gray()
  );
});

ItemEvents.rightClicked(AMBITION_CRYSTAL, (e) => {
  let { player, item, server } = e;
  if (global.professionLimit(player) >= global.professionIds.length) {
    player.tell(Text.translatable("society.crystal_of_ambition_professions.fail").red());
    return;
  }
  global.addProfessionSlots(player, 1);
  syncSlotOffer(player);
  server.runCommandSilent(
    `playsound minecraft:ui.toast.challenge_complete player ${player.username} ${player.x} ${player.y} ${player.z}`
  );
  item.count--;
  console.info(`[professions] slot added: ${player.username} -> ${global.professionLimit(player)}`);
  player.tell(
    Text.translatable(
      "society.crystal_of_ambition_professions.success",
      String(global.professionLimit(player))
    ).gold()
  );
});
