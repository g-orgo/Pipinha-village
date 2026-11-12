console.info("[SOCIETY] professionGlobals.js loaded");

// API (global.*):
// professionIds / professions: the five profession ids and their Puffish tree.
// getProfessions(player): ids of the professions the player follows.
// hasProfession(player, id): true when the player follows that profession.
// professionLimit(player): how many professions the player may follow.
// addProfessionSlots(player, amount): raises the extra profession slots.
// professionBlocker(player, id): translation key explaining why a profession
//   cannot be chosen, or null.
// specialtyTier(player, tree): 0, 1 or 2 from the specialty_<tree>_<tier> stage.
// specialtyChance(player, tree, perk): best chance among the player's professions.
// rollSpecialty(player, tree, perk): random roll against specialtyChance.
// bumpQuality(stack): raises the quality tier of a stack by one (max 3).
// professionBoostedXp(player, tree, xp): boosted experience for a chosen tree.
// applyViniculturePerks(blockId, player, stack): vinicultura perks.
// applySpecialtyArtisan(blockId, player, stack): Specialty perks on wine output.
// applySpecialtyHusbandry(player, stack, canHaveQuality): Specialty perks on products.
// applySpecialtyFishing(player, drops): Specialty perks on fishing drops.
// State: players follow up to professionLimit professions (default 1, extra
// slots in persistentData "sunlitProfessionSlots"). All trees are always
// unlocked. Specialty I/II nodes grant specialty_<tree>_1/2, and their effect
// depends on the profession the player follows.

global.professions = {
  farmer: { tree: "farming" },
  rancher: { tree: "husbandry" },
  fisher: { tree: "fishing" },
  winemaker: { tree: "vinicultura" },
  cook: { tree: "culinaria" },
};
global.professionIds = ["farmer", "rancher", "fisher", "winemaker", "cook"];
global.PROFESSION_XP_BOOST = 0.5;

global.professionStage = (id) => `profession_${id}`;
global.professionObjective = (id) => `sunlit_prof_${global.professions[id].tree}`;

global.getProfessions = (player) =>
  global.professionIds.filter((id) => player.stages.has(global.professionStage(id)));

global.professionForTree = (tree) =>
  global.professionIds.find((id) => global.professions[id].tree === tree);

// Experience gained in a chosen profession's tree is boosted. Trees that
// belong to no profession, or to a profession not chosen, are unchanged.
global.professionBoostedXp = (player, tree, xp) => {
  let id = global.professionForTree(tree);
  if (!id || !player.stages.has(global.professionStage(id))) return xp;
  return Math.round(xp * (1 + global.PROFESSION_XP_BOOST));
};

// Wine machines feed the winemaker tree instead of farming.
global.vinicultureMachines = ["society:wine_keg", "society:aging_cask", "society:ancient_cask"];
global.artisanXpTree = (blockId) =>
  global.vinicultureMachines.includes(String(blockId)) ? "vinicultura" : "farming";

// Vinicultura perks, applied to the stack a player takes out of a wine machine.
global.applyViniculturePerks = (blockId, player, stack) => {
  if (!player || !global.vinicultureMachines.includes(String(blockId))) return;
  if (player.stages.has("vinicultura_extra") && Math.random() < 1 / 3) {
    stack.count = stack.count + 1;
  }
  if (player.stages.has("vinicultura_double") && Math.random() < 1 / 50) {
    stack.count = stack.count * 2;
  }
};

// Profession limit: one profession by default, more through guild slots.
global.PROFESSION_LIMIT_DEFAULT = 1;
global.professionLimit = (player) => {
  let extra = player.persistentData.getInt("sunlitProfessionSlots") || 0;
  return Math.min(global.professionIds.length, global.PROFESSION_LIMIT_DEFAULT + extra);
};
global.addProfessionSlots = (player, amount) => {
  let extra = player.persistentData.getInt("sunlitProfessionSlots") || 0;
  let max = global.professionIds.length - global.PROFESSION_LIMIT_DEFAULT;
  player.persistentData.putInt("sunlitProfessionSlots", Math.max(0, Math.min(max, extra + amount)));
};
global.hasProfession = (player, id) => player.stages.has(global.professionStage(id));
// Translation key explaining why the profession cannot be chosen, or null.
global.professionBlocker = (player, id) => {
  let chosen = global.getProfessions(player);
  if (chosen.includes(id)) return "society.profession.already";
  if (chosen.length >= global.professionLimit(player)) return "society.profession.limit";
  return null;
};

// Specialty nodes: tier 1 and tier 2 stages per tree. Tier II replaces tier I.
global.specialtyStage = (tree, tier) => `specialty_${tree}_${tier}`;
global.specialtyTier = (player, tree) => {
  if (!player || !player.stages) return 0;
  if (player.stages.has(global.specialtyStage(tree, 2))) return 2;
  if (player.stages.has(global.specialtyStage(tree, 1))) return 1;
  return 0;
};

// Chances per perk: { professionId: [tierI, tierII] }.
global.SPECIALTY_PERKS = {
  farming: {
    crop_extra: { farmer: [0.20, 0.35] },
    crop_seed: { farmer: [0.10, 0.15] },
    crop_quality: { cook: [0.15, 0.30] },
    crop_quality_long: { cook: [0.25, 0.45] },
    grape_extra: { winemaker: [0.20, 0.35] },
    feed_drop: { rancher: [0.10, 0.20] },
    worm_drop: { fisher: [0.10, 0.20] },
    hydration: { farmer: [0, 1] },
    replant_ahead: { farmer: [0, 0.25] },
  },
  husbandry: {
    product_extra: { rancher: [0.20, 0.30], fisher: [0.05, 0.10], winemaker: [0.05, 0.10] },
    product_quality: { cook: [0.20, 0.35] },
    fertilizer_drop: { farmer: [0.10, 0.20] },
    twins: { rancher: [0, 0.20], cook: [0, 0.10] },
  },
  fishing: {
    fish_extra: { fisher: [0.20, 0.35], rancher: [0.05, 0.10], winemaker: [0.05, 0.10] },
    fish_quality: { cook: [0.15, 0.30] },
    fertilizer_drop: { farmer: [0.10, 0.20] },
  },
  vinicultura: {
    wine_quality: { winemaker: [0.20, 0.35], cook: [0.10, 0.20] },
    wine_extra: { winemaker: [0.10, 0.20], farmer: [0.05, 0.10], rancher: [0.05, 0.10], fisher: [0.05, 0.10] },
  },
  culinaria: {
    dish_extra: {
      cook: [0.15, 0.25],
      farmer: [0.05, 0.10],
      rancher: [0.05, 0.10],
      fisher: [0.05, 0.10],
      winemaker: [0.05, 0.10],
    },
  },
};

global.specialtyChance = (player, tree, perk) => {
  if (!player || !player.stages || player.isFake()) return 0;
  let tier = global.specialtyTier(player, tree);
  if (tier === 0) return 0;
  let table = (global.SPECIALTY_PERKS[tree] || {})[perk] || {};
  let best = 0;
  global.getProfessions(player).forEach((id) => {
    let values = table[id];
    if (values) best = Math.max(best, values[tier - 1]);
  });
  return best;
};
global.rollSpecialty = (player, tree, perk) => Math.random() < global.specialtyChance(player, tree, perk);

// Raises the quality tier of a stack by one (max 3), using the quality_food:quality component.
global.bumpQuality = (stack) => {
  if (!stack || stack.isEmpty()) return;
  let current = global.getQualityLevel(stack);
  if (current >= 3) return;
  global.setQualityLevel(stack, current + 1);
};

global.applySpecialtyArtisan = (blockId, player, stack) => {
  if (!player || player.isFake() || !global.vinicultureMachines.includes(String(blockId))) return;
  try {
    if (global.rollSpecialty(player, "vinicultura", "wine_quality")) global.bumpQuality(stack);
    if (global.rollSpecialty(player, "vinicultura", "wine_extra")) stack.count = stack.count + 1;
  } catch (err) {
    console.error(`[specialty] artisan failed: ${err}`);
  }
};

global.applySpecialtyHusbandry = (player, stack, canHaveQuality) => {
  if (!player || !player.stages || player.isFake() || !stack) return stack;
  try {
    if (stack.count < stack.maxStackSize && global.rollSpecialty(player, "husbandry", "product_extra")) {
      stack.count = stack.count + 1;
    }
    if (canHaveQuality && global.rollSpecialty(player, "husbandry", "product_quality")) {
      global.bumpQuality(stack);
    }
    if (global.rollSpecialty(player, "husbandry", "fertilizer_drop")) {
      player.give("farm_and_charm:fertilizer");
    }
  } catch (err) {
    console.error(`[specialty] husbandry failed: ${err}`);
  }
  return stack;
};

global.applySpecialtyFishing = (player, drops) => {
  if (!player || !player.stages || player.isFake() || !drops) return;
  try {
    drops.forEach((drop) => {
      if (!drop.hasTag("minecraft:fishes")) return;
      if (global.rollSpecialty(player, "fishing", "fish_extra")) {
        let extra = Item.of(`1x ${drop.id}`);
        extra.setCustomData(drop.customData);
        global.setQualityLevel(extra, global.getQualityLevel(drop));
        player.give(extra);
      }
      if (global.rollSpecialty(player, "fishing", "fish_quality")) global.bumpQuality(drop);
    });
    if (global.rollSpecialty(player, "fishing", "fertilizer_drop")) {
      player.give("farm_and_charm:fertilizer");
    }
  } catch (err) {
    console.error(`[specialty] fishing failed: ${err}`);
  }
};
