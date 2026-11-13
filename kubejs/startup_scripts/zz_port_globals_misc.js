// Global functions and static tables moved from server_scripts for the KubeJS 7 port.
// Runtime state lives in global.runtime (see 000_port_runtime.js); nothing here reads it at load time.

(function () {
const $FTBChunksAPI = Java.loadClass("dev.ftb.mods.ftbchunks.api.FTBChunksAPI");
const $ChunkPos = Java.loadClass("net.minecraft.world.level.ChunkPos");
const $ChunkDimPos = Java.loadClass("dev.ftb.mods.ftblibrary.math.ChunkDimPos");

const AUTO_CLAIM_SKIP_TAGS = ["minecraft:all_signs", "minecraft:banners"];

global.autoClaimWanted = (block) => {
  if (block.hasTag("minecraft:beds")) return true;
  if (AUTO_CLAIM_SKIP_TAGS.some((tag) => block.hasTag(tag))) return false;
  return block.getEntity() != null || block.blockState.hasBlockEntity();
};

global.autoClaimChunk = (player, block) => {
  if (!player || player.isFake() || player.level.isClientSide()) return;
  if (!global.autoClaimWanted(block)) return;
  const api = $FTBChunksAPI.api();
  if (!api.isManagerLoaded()) return;
  const dimension = block.level.dimension();
  const cx = block.pos.x >> 4;
  const cz = block.pos.z >> 4;
  if (api.getManager().getChunk(new $ChunkDimPos(dimension, cx, cz)) != null) return;
  const result = api.claimAsPlayer(player, dimension, new $ChunkPos(cx, cz), false);
  if (result.isSuccess()) {
    player.setStatusMessage(Text.translatable("sunlit_claims.auto_claimed", `${cx}, ${cz}`).green());
  }
};
})();

(function () {
  const $AttributeModifier = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier");
  const $Operation = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation");
  const $EquipmentSlot = Java.loadClass("net.minecraft.world.entity.EquipmentSlot");
  const $BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");

  // Hearts needed before any bonus applies, and the hearts that give the full bonus.
  const PERK_START_HEARTS = 5;
  const PERK_FULL_HEARTS = 10;
  const WOLF_ARMOR_HEARTS = 10;
  const WOLF_ARMOR_ITEM = "minecraft:wolf_armor";
  const ARMOR_GIFT_KEY = "armor_gift";
  const ARMOR_FLAG = "affectionArmorGiven";

  // One fixed id per attribute, so each perk is a single modifier that gets replaced.
  const ATTRIBUTE_PATHS = {
    "generic.attack_damage": "attack_damage",
    "generic.armor": "armor",
    "generic.movement_speed": "movement_speed",
    "horse.jump_strength": "jump_strength",
    "generic.flying_speed": "flying_speed",
  };
  const modifierIdOf = (attrId) => $ResourceLocation.fromNamespaceAndPath("society", "affection_" + ATTRIBUTE_PATHS[attrId]);

  // Perk groups, one per species group. Each entry: attribute id, amount at full
  // affection, operation. Amounts are multiplied by the affection fraction.
  const PERK_GROUPS = [
    {
      types: ["minecraft:wolf", "quark:shiba", "quark:foxhound", "wildernature:dog", "wildernature:red_wolf"],
      perks: [
        { attr: "generic.attack_damage", amount: 4, op: "ADD_VALUE" },
        { attr: "generic.armor", amount: 8, op: "ADD_VALUE" },
      ],
    },
    {
      types: ["buzzier_bees:grizzly_bear", "minecraft:polar_bear"],
      perks: [
        { attr: "generic.attack_damage", amount: 4, op: "ADD_VALUE" },
        { attr: "generic.armor", amount: 6, op: "ADD_VALUE" },
      ],
    },
    {
      types: ["minecraft:horse"],
      perks: [
        { attr: "generic.movement_speed", amount: 0.2, op: "ADD_MULTIPLIED_BASE" },
        { attr: "horse.jump_strength", amount: 0.2, op: "ADD_MULTIPLIED_BASE" },
      ],
    },
    {
      types: ["minecraft:axolotl", "crittersandcompanions:ferret"],
      perks: [
        { attr: "generic.attack_damage", amount: 2, op: "ADD_VALUE" },
        { attr: "generic.movement_speed", amount: 0.15, op: "ADD_MULTIPLIED_BASE" },
      ],
    },
    {
      perks: [
        { attr: "generic.movement_speed", amount: 0.2, op: "ADD_MULTIPLIED_BASE" },
        { attr: "generic.flying_speed", amount: 0.2, op: "ADD_MULTIPLIED_BASE" },
      ],
    },
  ];

  const groupOf = (type) => {
    for (let i = 0; i < PERK_GROUPS.length; i++) {
      if (PERK_GROUPS[i].types.indexOf(type) !== -1) return PERK_GROUPS[i];
    }
    return null;
  };

  const affectionHearts = (target) => {
    let affection = target.persistentData.getInt("affection");
    let hearts = Math.floor((affection > 1000 ? 1000 : affection) / 100);
    if (hearts < 0) hearts = 0;
    return hearts;
  };

  // 0 below 5 hearts, 1/6 at 5 hearts, 1 at 10 hearts.
  const perkFraction = (hearts) => {
    if (hearts < PERK_START_HEARTS) return 0;
    return (hearts - (PERK_START_HEARTS - 1)) / (PERK_FULL_HEARTS - PERK_START_HEARTS + 1);
  };

  const attributeOf = (attrId) => $BuiltInRegistries.ATTRIBUTE.getHolder($ResourceLocation.fromNamespaceAndPath("minecraft", ATTRIBUTE_PATHS[attrId])).orElse(null);

  // Sets the permanent modifier for one attribute. Skips when unchanged, removes at 0.
  const setPerk = (target, attrId, amount, opName) => {
    let attribute = attributeOf(attrId);
    if (!attribute) return;
    let instance = target.getAttribute(attribute);
    if (!instance) return;
    let modifierId = modifierIdOf(attrId);
    let current = instance.getModifier(modifierId);
    if (amount <= 0) {
      if (current) instance.removeModifier(modifierId);
      return;
    }
    if (current && Math.abs(current.amount() - amount) < 0.0001) return;
    if (current) instance.removeModifier(modifierId);
    instance.addPermanentModifier(
      new $AttributeModifier(modifierId, amount, $Operation[opName])
    );
  };

  const sendGiftMessage = (target, player, server) => {
    if (!player || !server || player.isFake()) return;
    let name = target.customName ? target.customName : global.getTranslatedEntityName(String(target.type));
    server.runCommandSilent(
      global.getEmbersTextAPICommand(
        player.username,
        '{anchor:"BOTTOM_CENTER",background:1,wrap:220,align:"BOTTOM_CENTER",color:"#FFAA00",offsetY:20}',
        40,
        Text.translatable("society.husbandry.pet." + ARMOR_GIFT_KEY, name).toJson()
      )
    );
  };

  // Tamed wolves bonded with their owner at 10 hearts get Wolf Armor once, ever.
  const maybeGiveWolfArmor = (target, hearts, player, server) => {
    if (String(target.type) !== "minecraft:wolf") return;
    if (hearts < WOLF_ARMOR_HEARTS) return;
    if (!player || !target.isTame()) return;
    if (String(target.getOwnerUUID()) !== String(player.uuid)) return;
    let data = target.persistentData;
    if (data.getBoolean(ARMOR_FLAG)) return;
    let chest = $EquipmentSlot.valueOf("CHEST");
    if (!target.getItemBySlot(chest).isEmpty()) return;

    target.setItemSlot(chest, Item.of(WOLF_ARMOR_ITEM));
    data.putBoolean(ARMOR_FLAG, true);
    if (server) {
      let x = target.x;
      let y = target.y;
      let z = target.z;
      server.runCommandSilent(`playsound minecraft:item.armor.equip_leather neutral ${player.username} ${x} ${y} ${z} 1 1`);
    }
    target.level.spawnParticles("minecraft:heart", true, target.x, target.y + 1, target.z, 0.4, 0.4, 0.4, 5, 0.01);
    sendGiftMessage(target, player, server);
  };

  // Applies (or removes) the affection perks of one pet. Safe to call every time a pet is handled.
  global.applyAffectionPerks = (target, player, server) => {
    let hearts = affectionHearts(target);
    let fraction = perkFraction(hearts);
    let group = groupOf(String(target.type));
    if (group) {
      group.perks.forEach((perk) => {
        setPerk(target, perk.attr, perk.amount * fraction, perk.op);
      });
    }
    maybeGiveWolfArmor(target, hearts, player, server);
  };

  // Items a pet or the pack reacts to on a click (taming, feeding, saddling, naming,
  // leashing, dyeing, catching, pack tools). Holding one keeps its normal use.
  const PET_USE_ITEMS = [
    "minecraft:lead",
    "minecraft:name_tag",
    "minecraft:saddle",
    "minecraft:chest",
    "minecraft:bowl",
    "minecraft:shears",
    "minecraft:brush",
    "society:magic_shears",
    "society:milk_pail",
    "society:mood_scanner",
    "society:sunlit_crystal",
    "society:miracle_potion",
    "society:animal_cracker",
    "society:friendship_necklace",
    "numismatics:crown",
    "create:precision_mechanism",
    "quark:diamond_heart",
  ];
  const PET_USE_TAGS = [
    "society:animal_feed",
    "society:plushies",
    "minecraft:flowers",
    "c:tools/fishing_rods",
  ];

  const isPetUseItem = (item, target) => {
    let id = String(item.id);
    if (PET_USE_ITEMS.indexOf(id) !== -1) return true;
    if (/bucket|lasso|armor|_dye$|spawn_egg/.test(id)) return true;
    if (typeof item.hasTag === "function" && PET_USE_TAGS.some((tag) => item.hasTag(tag))) return true;
    if (typeof target.isFood === "function" && target.isFood(item)) return true;
    return false;
  };

  // True when a click should pet the animal before any other interaction, on a pet or
  // husbandry animal not petted yet today, by a real player's main hand. Husbandry
  // animals need an empty hand; pets also accept any held item that is not a pet use
  // item, so the first click of the day never mounts a horse or toggles sitting.
  global.sunlitShouldPetFirst = (hand, player, item, target, level) => {
    if (String(hand) !== "MAIN_HAND") return false;
    if (player.isFake()) return false;
    let empty = !item || (typeof item.isEmpty === "function" ? item.isEmpty() : String(item) === "minecraft:air");
    let pet = global.checkEntityTag(target, "society:pet_animal");
    if (!pet && !global.checkEntityTag(target, "society:husbandry_animal")) return false;
    if (!empty && (!pet || isPetUseItem(item, target))) return false;
    return Number(target.persistentData.getInt("ageLastPet")) !== Number(global.getDay(level));
  };
})();

(function () {
const debug = false;

const debugData = (player, level, data, hearts) => {
  player.tell(`:heart: ${data.getInt("affection")}-${hearts} hearts`);
  player.tell(
    `Day: ${Number(
      (Math.floor(Number(level.dayTime() / 24000)) + 1).toFixed()
    )}`
  );
  player.tell(`Mood: ${data.getInt("lastMood")}`);
  player.tell(`Day Mood last set: ${data.getInt("ageLastSetMood")}`);
  player.tell(`Pet: ${data.getInt("ageLastPet")}`);
  player.tell(`Fed: ${data.getInt("ageLastFed")}`);
  player.tell(`Boosted feed: ${data.getInt("ageLastBoosted")}`);
  player.tell(`Dropped Special: ${data.getInt("ageLastDroppedSpecial")}`);
  player.tell(`Milked: ${data.getInt("ageLastMilked")}`);
  player.tell(`Magic Harvested: ${data.getInt("ageLastMagicHarvested")}`);
};

const initializeFarmAnimal = (day, target, level) => {
  let data = target.persistentData;
  if (!data.getInt("affection")) {
    data.affection = 1;
    level.spawnParticles(
      "minecraft:heart",
      true,
      target.x,
      target.y + 1.5,
      target.z,
      0,
      0.1,
      0,
      1,
      0.01
    );
  }
  let newBaseDay = day - 1;
  if (!data.getInt("ageLastPet")) data.ageLastPet = newBaseDay;
  if (!data.getInt("ageLastFed")) data.ageLastFed = newBaseDay;
  if (!data.getInt("ageLastDroppedSpecial")) data.ageLastDroppedSpecial = newBaseDay;
  if (!data.getInt("ageLastMagicHarvested")) data.ageLastMagicHarvested = newBaseDay;
  if (!data.getInt("ageLastMoodSet")) data.ageLastMoodSet = newBaseDay;
  if (!data.getInt("ageLastBred")) data.ageLastBred = newBaseDay;
  if (!data.getInt("ageLastMilked") && global.checkEntityTag(target, "society:milkable_animal"))
    data.ageLastMilked = newBaseDay;
};

// Anti-frustration feature to be forgiving when re-logging
const handleFarmAnimalBackwardsCompat = (target, day) => {
  let data = target.persistentData;
  if (
    day < data.getInt("ageLastPet") ||
    data.getInt("ageLastPet") - day > 5000
  ) {
    let newDay = day - 1;
    data.ageLastPet = newDay;
    data.ageLastMagicHarvested = newDay;
    data.ageLastMilked = newDay;
    data.ageLastDroppedSpecial = newDay;
    data.ageLastBred = newDay;
    data.ageLastFed = newDay;
    data.ageLastMoodSet = newDay;
  }
};

const checkAnimal = (
  player,
  level,
  server,
  data,
  name,
  mood,
  hearts,
  color,
  petted
) => {
  let nameColor = color || "#55FF55";
  // After a real petting, the line above the hearts reads "Petted <name>".
  let nameText = petted
    ? Text.translatable("society.husbandry.petted", name.noColor()).toJson()
    : name.noColor().toJson();
  let heartsToDisplay = 10;
  let icons = [];
  if (mood < 64) icons.push("☹");
  if (mood > 160) icons.push("☺");
  if (data.animalCracker) icons.push("🡅");
  if (data.clockwork) icons.push("⚙");
  if (data.bff) icons.push("❤");
  if (data.bribed) icons.push("💰");
  let iconString = "";
  icons.forEach((icon, index) => {
    iconString += icon;
    if (index < icons.length - 1) iconString += " ";
  });
  global.renderUiText(
    player,
    server,
    {
      animalNameIcons: {
        type: "text",
        x: 0,
        y: -88,
        text: iconString,
        color: nameColor,
        alignX: "center",
        alignY: "bottom",
      },
      animalName: {
        type: "text",
        x: 0,
        y: -78,
        text: `${nameText}`,
        color: nameColor,
        alignX: "center",
        alignY: "bottom",
      },
      animalNameShadow: {
        type: "text",
        x: 1,
        z: -1,
        y: -77,
        text: `${nameText}`,
        color: "#000000",
        alignX: "center",
        alignY: "bottom",
      },
      affection: {
        type: "text",
        x: 0,
        y: -66,
        text: `§c${hearts > 0 ? `❤`.repeat(Math.min(hearts, heartsToDisplay)) : ""
          }§0${hearts < heartsToDisplay ? `❤`.repeat(heartsToDisplay - hearts) : ""
          }`,
        color: "#FFAA00",
        alignX: "center",
        alignY: "bottom",
      },
      affectionShadow: {
        type: "text",
        x: 1,
        z: -1,
        y: -65,
        text: `❤`.repeat(heartsToDisplay),
        color: "#000000",
        alignX: "center",
        alignY: "bottom",
      },
    },
    global.mainUiElementIds
  );
  debug && debugData(player, level, data, hearts);
};

const handlePet = (name, data, mood, day, peckish, hungry, e) => {
  let { player, item, target, level, server } = e;
  let ageLastPet = data.getInt("ageLastPet");
  let affection = data.getInt("affection");
  let hearts = Math.floor(affection / 100);
  if (hearts > 10) hearts = 10;
  else if (hearts < 0) hearts = 0;
  let affectionIncreaseMult =
    player.stages.has("animal_whisperer") || data.bribed ? 2 : 1;
  if (player.stages.has("animal_fancy")) affectionIncreaseMult += 1;
  let affectionIncrease = 10 * affectionIncreaseMult;

  if (target.isBaby()) {
    affectionIncrease =
      affectionIncrease * (player.stages.has("fostering") ? 10 : 2);
  }
  let errorText = "";

  if (day > ageLastPet) {
    let livableArea = global.getAnimalIsNotCramped(target, 1.1);
    if (!player.isFake()) {
      debug &&
        player.tell(
          `Increased Affection by: ${affectionIncrease} from petting`
        );
      data.affection = affection + affectionIncrease;
    }
    if (hungry || (!data.clockwork && player.isFake()) || !livableArea) {
      data.affection = affection - (hungry ? 15 : 25);
    }
    data.ageLastPet = day;
    level.spawnParticles(
      (!data.clockwork && player.isFake()) || hungry
        ? "minecraft:angry_villager"
        : "minecraft:heart",
      true,
      target.x,
      target.y + 1.5,
      target.z,
      0,
      0.1,
      0,
      1,
      0.01
    );
    global.giveExperience(server, player, "husbandry", Math.max(10, 20 * hearts));
    if (!livableArea && !data.clockwork) {
      errorText = Text.translatable(
        "society.husbandry.crowded",
        name
      ).toJson();
    }
    if (
      !hungry &&
      peckish &&
      !player.isFake() &&
      !item.hasTag("society:animal_feed")
    ) {
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          `{anchor:"BOTTOM_CENTER",background:1,wrap:220,align:"BOTTOM_CENTER",color:"#FFAA00",offsetY:20}`,
          40,
          Text.translatable("society.husbandry.peckish", name).toJson()
        )
      );
    }
    if (hungry) {
      errorText = Text.translatable(
        "society.husbandry.starved",
        name
      ).toJson();
    }
    if (errorText && !player.isFake()) {
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          global.animalMessageSettings,
          40,
          errorText
        )
      );
    }
  }
  let petted = day > ageLastPet && !player.isFake();
  if (petted || item === "minecraft:air" || item === 'society:mood_scanner') {
    // Petting always shows the status (name and hearts), not only on empty-hand clicks.
    let shownHearts = hearts;
    if (petted) {
      shownHearts = Math.floor(Math.min(data.getInt("affection"), 1000) / 100);
      if (shownHearts < 0) shownHearts = 0;
    }
    let nameColor;
    if (peckish) {
      nameColor = "#FFAA00";
    }
    if (hungry) {
      nameColor = "#FF5555";
    }
    checkAnimal(player, level, server, data, name, mood, shownHearts, nameColor, petted);
  }
  // Raise Max health
  let affectionHealth = hearts * 4;
  if (target.maxHealth < affectionHealth) {
    target.setMaxHealth(affectionHealth);
    target.setHealth(affectionHealth);
  }
};

const handleMilk = (name, data, day, hungry, e) => {
  let { player, item, target, level, server } = e;
  if (player.cooldowns.isOnCooldown(item)) return;
  if (player.isFake() && data.getInt("affection") < 100) return;
  let errorText;
  let milkItem = global.getMilk(level, target, data, player, day, true, undefined, player.stages);

  if (milkItem !== -1) {
    let milk = level.createEntity("minecraft:item");
    milk.x = player.x;
    milk.y = player.y;
    milk.z = player.z;
    milk.item = milkItem;
    milk.spawn();
    server.runCommandSilent(
      `playsound minecraft:entity.cow.milk block @a ${player.x} ${player.y} ${player.z}`
    );
    global.giveExperience(server, player, "husbandry", 30);
    level.spawnParticles(
      "minecraft:note",
      true,
      target.x,
      target.y + 1.5,
      target.z,
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      3,
      0.01
    );
  } else if (target.isBaby()) {
    errorText = Text.translatable(
      "society.husbandry.action.young",
      name
    ).toJson();
  } else if (hungry) {
    errorText = Text.translatable(
      "society.husbandry.action.hungry",
      name
    ).toJson();
  } else {
    errorText = Text.translatable(
      "society.husbandry.action.cooldown_1",
      name
    ).toJson();
  }
  if (errorText && !player.isFake()) {
    server.runCommandSilent(
      global.getEmbersTextAPICommand(
        player.username,
        global.animalMessageSettings,
        20,
        errorText
      )
    );
  }
};

const handleFeed = (data, day, e) => {
  let { player, item, target, level, server } = e;
  if (player.cooldowns.isOnCooldown(item)) return;
  let ageLastFed = data.getInt("ageLastFed");
  let affection = data.getInt("affection");
  let affectionIncrease = {
    "society:animal_feed": 10,
    "society:candied_animal_feed": 100,
    "society:mana_feed": 30,
  }[item.id];
  let affectionIncreaseMult =
    player.stages.has("animal_whisperer") || data.bribed ? 2 : 1;
  if (player.stages.has("animal_fancy")) affectionIncreaseMult += 0.5;
  // Cap affection increase at 100
  let totalNewAffection = Math.min(
    affectionIncrease * affectionIncreaseMult,
    100
  );
  if (day > ageLastFed) {
    server.runCommandSilent(
      `playsound minecraft:entity.generic.eat block @a ${player.x} ${player.y} ${player.z}`
    );
    target.heal(4);
    global.giveExperience(server, player, "husbandry", 20);
    data.affection = affection + totalNewAffection;
    debug &&
      player.tell(`Increased Affection by: ${totalNewAffection} from feeding`);
    data.ageLastFed = day;
    level.spawnParticles(
      true,
      target.x,
      target.y + 1.5,
      target.z,
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      0.1 * rnd(1, 4),
      5,
      0.01
    );
    item.count--;
    global.addItemCooldown(player, item, 10);
  }
};

const handleSheepMagicShears = (e) => {
  let { target, level, server } = e;
  if (target.readyForShearing()) {
    target.setSheared(true);
    let woolItem = Item.of(target.getColor().getName() + "_wool");
    let i = Math.ceil(Math.random() * 4);
    for (let j = 0; j < i; j++) {
      let wool = level.createEntity("minecraft:item");

      wool.x = target.x + rnd(0, 0.5);
      wool.y = target.y + 0.5;
      wool.z = target.z + rnd(0, 0.5);
      wool.item = Item.of(woolItem);
      wool.spawn();
      wool.setDeltaMovement(
        wool
          .getDeltaMovement()
          .add(
            (Math.random() - Math.random()) * 0.1,
            Math.random() * 0.05,
            (Math.random() - Math.random()) * 0.1
          )
      );
    }

    server.runCommandSilent(
      `playsound minecraft:entity.sheep.shear block @a ${target.x} ${target.y} ${target.z}`
    );
  }
};

const handleMagicHarvest = (name, data, e) => {
  let { player, level, target, item, server } = e;
  if (player.cooldowns.isOnCooldown(item)) return;
  if (["minecraft:sheep", "wildernature:minisheep"].includes(target.type)) handleSheepMagicShears(e);
  let affection = data.getInt("affection");
  let hearts = Math.floor((affection > 1000 ? 1000 : affection) / 100);

  let errorText = "";
  let droppedLoot = global.getMagicShearsOutput(level, target, player, undefined, player.stages);
  if (droppedLoot !== -1) {
    server.runCommandSilent(
      `playsound minecraft:entity.sheep.shear block @a ${player.x} ${player.y} ${player.z}`
    );
    global.giveExperience(server, player, "husbandry", 15);
    for (let i = 0; i < droppedLoot.length; i++) {
      let specialItem = level.createEntity("minecraft:item");
      let dropItem = droppedLoot[i];
      specialItem.x = player.x;
      specialItem.y = player.y;
      specialItem.z = player.z;
      specialItem.item = dropItem;
      specialItem.spawn();
    }
    global.addItemCooldown(player, item, 1);
  } else {
    errorText = Text.translatable(
      "society.husbandry.action.cooldown_2",
      name
    ).toJson();
    if (hearts < 5) {
      errorText = Text.translatable(
        "society.husbandry.action.need_hearts",
        name
      ).toJson();
    }
    if (!player.isFake())
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          global.animalMessageSettings,
          40,
          errorText
        )
      );
    global.addItemCooldown(player, item, 10);
  }
};

const handleSpecialItem = (
  data,
  day,
  chance,
  hungry,
  minHearts,
  mult,
  item,
  hasQuality,
  plushieModifiers,
  e
) => {
  let { player, target, level, server } = e;
  let affection;
  let mood;
  let resolvedItem = item;
  let resolvedChance = chance;
  let resolvedHasQuality = hasQuality
  let dropAmount = mult * (plushieModifiers && plushieModifiers.doubleDrops ? 2 : 1);
  if (plushieModifiers) {
    affection = 1000;
    mood = 256;
    resolvedChance = chance + plushieModifiers.probabilityIncrease;
    if (plushieModifiers.processItems) {
      let processOutput = global.getProcessedItem(item, dropAmount);
      resolvedItem = processOutput.item.id;
      dropAmount = Math.round(dropAmount / processOutput.divisor) *  processOutput.item.count;
      resolvedHasQuality = processOutput.preserveQuality
    }
  } else {
    affection = data.getInt("affection") || 0;
    mood = global.getOrFetchMood(level, target, day, player);
  }
  let hearts = Math.floor(affection / 100);

  let quality = 0;

  if (
    (!hungry || plushieModifiers) &&
    hearts >= minHearts &&
    Math.random() <= resolvedChance
  ) {
    if (item.includes("large")) {
      if (Math.random() > (mood + hearts * 10) / 256) {
        return;
      }
    }
    if (plushieModifiers) {
      data.affection =
        affection + (player.stages.has("animal_whisperer") ? 20 : 10);
    }
    let specialItem = level.createEntity("minecraft:item");
    if (resolvedHasQuality && mood >= 160) {
      quality = global.getHusbandryQuality(hearts, mood);
    }
    specialItem.x = player.x;
    specialItem.y = player.y;
    specialItem.z = player.z;
    let specialStack = Item.of(`${dropAmount}x ${resolvedItem}`,
      quality > 0 ? `{quality_food:{effects:[],quality:${quality}}}` : null
    );
    // Husbandry Specialty perks (rancher, fisher, winemaker, cook, farmer).
    if (player && !plushieModifiers) {
      try {
        global.applySpecialtyHusbandry(player, specialStack, mood >= 160);
      } catch (err) {
        console.error(`[specialty] animal drop perks failed: ${err}`);
      }
    }
    specialItem.item = specialStack;
    specialItem.spawn();
    server.runCommandSilent(
      `playsound stardew_fishing:dwop block @a ${player.x} ${player.y} ${player.z}`
    );
    global.giveExperience(server, player, "husbandry", 60);
    if (target.x) {
      level.spawnParticles(
        "farmersdelight:star",
        true,
        target.x,
        target.y + 1,
        target.z,
        0.2 * rnd(1, 4),
        0.2 * rnd(1, 4),
        0.2 * rnd(1, 4),
        3,
        0.01
      );
    }
  }
};

const upgradeAnimal = (level, server, item, target, sound, particle) => {
  item.count--;
  server.runCommandSilent(
    `playsound ${sound} block @a ${target.x} ${target.y} ${target.z}`
  );
  level.spawnParticles(
    particle,
    true,
    target.x,
    target.y + 1.5,
    target.z,
    0.2 * rnd(0, 2),
    0.2 * rnd(0, 2),
    0.2 * rnd(0, 2),
    3,
    0.01
  );
};

global.handleHusbandryBase = (hand, player, item, target, level, server) => {
  let pet = global.checkEntityTag(target, "society:pet_animal");
  let eventData = {
    player: player,
    item: item,
    target: target,
    level: level,
    server: server,
  };
  if (hand == "OFF_HAND") return;
  if (!global.checkEntityTag(target, "society:husbandry_animal") && !pet)
    return;
  if (item.id === "society:sunlit_crystal") return;
  server.scheduleInTicks(1, () => {
    if (hand == "MAIN_HAND") {
      let day = global.getDay(level);
      handleFarmAnimalBackwardsCompat(target, day);
      initializeFarmAnimal(day, target, level);
      let data = target.persistentData;
      let name = target.customName ? target.customName : global.getTranslatedEntityName(String(target.type));
      let ageLastFed = data.getInt("ageLastFed");
      let peckish = !pet && day - ageLastFed == 1;
      let hungry = !pet && day - ageLastFed > 1;
      let affection = data.getInt("affection");
      let lostProduce = mood < 64 && Math.random() < mood / 64;
      let hearts = Math.floor((affection > 1000 ? 1000 : affection) / 100);
      player.swing();
      let mood = global.getOrFetchMood(level, target, day, player, false, true);
      handlePet(name, data, mood, day, peckish, hungry, eventData);
      if (pet) {
        if (global.applyAffectionPerks) {
          try {
            global.applyAffectionPerks(target, player, server);
          } catch (error) {
            console.error("[SOCIETY] applyAffectionPerks: " + error);
          }
        }
        return;
      }
      if (item.hasTag("society:animal_feed") && !pet)
        handleFeed(data, day, eventData);
      if (!lostProduce) {
        if (
          item === "society:milk_pail" &&
          global.checkEntityTag(target, "society:milkable_animal")
        ) {
          handleMilk(name, data, day, hungry, eventData);
        }
        global.handleSpecialHarvest(
          level,
          target,
          player,
          server,
          undefined,
          undefined,
          undefined,
          handleSpecialItem,
          player.stages,
        );
      }
      if (
        player.stages.has("biomancer") &&
        [
          "bakery:bread_knife",
          "farmersdelight:iron_knife",
          "farmersdelight:diamond_knife",
          "farmersdelight:netherite_knife",
          "farmersdelight:golden_knife",
          "aquaculture:wooden_fillet_knife",
          "aquaculture:stone_fillet_knife",
          "aquaculture:iron_fillet_knife",
          "aquaculture:gold_fillet_knife",
          "farmersdelight:flint_knife",
          "aquaculture:neptunium_fillet_knife",
          "aquaculture:diamond_fillet_knife",
          "refurbished_furniture:knife",
        ].includes(item.id)
      ) {
        if (player.cooldowns.isOnCooldown(item)) return;
        if (hearts < 5) {
          server.runCommandSilent(
            global.getEmbersTextAPICommand(
              player.username,
              global.animalMessageSettings,
              40,
              Text.translatable(
                "society.husbandry.action.need_hearts",
                name
              ).toJson()
            )
          );
        } else {
          let heart = level.createEntity("minecraft:item");
          heart.x = player.x;
          heart.y = player.y;
          heart.z = player.z;
          heart.item = Item.of("quark:diamond_heart");
          heart.spawn();
          server.runCommandSilent(
            `playsound minecraft:entity.sheep.shear block @a ${player.x} ${player.y} ${player.z}`
          );
          level.spawnParticles(
            "minecraft:angry_villager",
            true,
            target.x,
            target.y + 1.5,
            target.z,
            0.2 * rnd(1, 4),
            0.2 * rnd(1, 4),
            0.2 * rnd(1, 4),
            5,
            0.01
          );
          data.affection = affection - 100;
          global.addItemCooldown(player, item, 5);
        }
      }
      if (
        player.stages.has("bribery") &&
        item === "numismatics:crown" &&
        !data.bribed
      ) {
        if (player.cooldowns.isOnCooldown(item)) return;
        data.bribed = true;
        data.affection = affection + 100;
        item.count--;
        server.runCommandSilent(
          `playsound stardew_fishing:complete block @a ${player.x} ${player.y} ${player.z}`
        );
        level.spawnParticles(
          true,
          target.x,
          target.y + 1.5,
          target.z,
          0.2 * rnd(0, 1),
          0.2 * rnd(0, 1),
          0.2 * rnd(0, 1),
          5,
          0.01
        );
        global.addItemCooldown(player, item, 1);
      }
      if (
        player.stages.has("clockwork") &&
        item === "create:precision_mechanism" &&
        !data.clockwork
      ) {
        data.clockwork = true;
        upgradeAnimal(
          level,
          server,
          item,
          target,
          "minecraft:block.vault.activate",
          "supplementaries:bomb_explosion"
        );
        if (data.bff) {
          data.bff = false;
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
        !data.animalCracker
      ) {
        data.animalCracker = true;
        server.runCommandSilent(
          `playsound minecraft:entity.generic.eat block @a ${player.x} ${player.y} ${player.z}`
        );
        upgradeAnimal(
          level,
          server,
          item,
          target,
          "stardew_fishing:chest_get",
          "farmersdelight:star"
        );
      }
      if (
        player.stages.has("bff") &&
        item === "society:friendship_necklace" &&
        !data.bff
      ) {
        data.bff = true;
        upgradeAnimal(
          level,
          server,
          item,
          target,
          "buzzier_bees:buttercup_bloom"
        );
        if (data.clockwork) {
          data.clockwork = false;
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
      if (
        player.stages.has("transplanting") &&
        item === "quark:diamond_heart" &&
        hearts < 10
      ) {
        if (player.cooldowns.isOnCooldown(item)) return;
        data.affection = affection + 100;
        if (!player.isCreative()) item.count--;
        server.runCommandSilent(
          `playsound aquaculture:fish_flop block @a ${player.x} ${player.y} ${player.z}`
        );
        level.spawnParticles(
          "minecraft:heart",
          true,
          target.x,
          target.y + 1.5,
          target.z,
          0.2 * rnd(0, 2),
          0.2 * rnd(0, 2),
          0.2 * rnd(0, 2),
          5,
          0.01
        );
        global.addItemCooldown(player, item, 1);
      }
      if (!lostProduce && item === "society:magic_shears") {
        handleMagicHarvest(name, data, eventData);
      }
      if (affection > 1075) {
        // Cap affection at 1075
        data.affection = 1075;
      }
      if (affection < 0) data.affection = 0;
    }
  });
};
  global.animalBaseHelpers = { checkAnimal: checkAnimal, upgradeAnimal: upgradeAnimal, handleSpecialItem: handleSpecialItem };
})();

(function () {
  const $AABB = Java.loadClass("net.minecraft.world.phys.AABB");
  const $CompoundTag = Java.loadClass("net.minecraft.nbt.CompoundTag");
  const $ListTag = Java.loadClass("net.minecraft.nbt.ListTag");
  const $EntityType = Java.loadClass("net.minecraft.world.entity.EntityType");
  const $RemovalReason = Java.loadClass("net.minecraft.world.entity.Entity$RemovalReason");
  const $DoubleTag = Java.loadClass("net.minecraft.nbt.DoubleTag");

  // Owner data key holding the dogs hidden while riding (list of entity NBT).
  const HIDDEN_KEY = "sunlitHiddenDogs";
  // Forge copies this sub-tag of the player's Forge data to the new player on respawn,
  // so hidden dogs survive the owner dying while riding. KubeJS persistentData does not.
  const PERSISTED_KEY = "PlayerPersisted";
  // Tag type id of a compound inside a ListTag.
  const TAG_COMPOUND = 10;
  // Radius around the owner where following dogs are hidden on mount.
  const MOUNT_SEARCH = 48;

  // Blocks moved between two ticks that count as a teleport.
  const TELEPORT_DISTANCE = 16;
  // Search radius around the old position (teleport) or the owner (dismount).
  const TELEPORT_SEARCH = 48;
  const DISMOUNT_SEARCH = 96;
  // Dog types that can be put in follow mode.
  const DOG_TYPES = [
    "minecraft:wolf",
    "quark:shiba",
    "quark:foxhound",
    "wildernature:dog",
    "wildernature:red_wolf",
  ];
  // Domestication Innovation command value for follow.
  const COMMAND_FOLLOW = 2;

  // Per-player state keyed by UUID string: dimension, position, the Level object, riding flag.
  const dogStates = () => {
    if (!global.runtime.dogFollowStates) global.runtime.dogFollowStates = {};
    return global.runtime.dogFollowStates;
  };

  const logOnce = (error) => {
    if (global.runtime.dogFollowErrorLogged) return;
    global.runtime.dogFollowErrorLogged = true;
    console.error("[SOCIETY] dogFollowOwner: " + error);
  };

  const listSize = (list) => (typeof list.size === "function" ? list.size() : list.length);
  const listGet = (list, i) => (typeof list.get === "function" ? list.get(i) : list[i]);

  const eachPlayer = (server, fn) => {
    let players = server.players;
    let count = listSize(players);
    for (let i = 0; i < count; i++) fn(listGet(players, i));
  };

  // Plain multiplication: the exponent operator gives wrong results in KubeJS's Rhino.
  const square = (v) => v * v;
  const distance3 = (a, b) => Math.sqrt(square(a.x - b.x) + square(a.y - b.y) + square(a.z - b.z));

  const isFollowingDog = (dog, ownerUuid) => {
    if (DOG_TYPES.indexOf(String(dog.type)) === -1) return false;
    if (!dog.isAlive() || !dog.isTame()) return false;
    if (String(dog.getOwnerUUID()) !== ownerUuid) return false;
    if (dog.isOrderedToSit() || dog.isPassenger() || dog.isLeashed()) return false;
    if (typeof dog.getCommand === "function" && Number(dog.getCommand()) !== COMMAND_FOLLOW) return false;
    return true;
  };

  // Following dogs of one owner within a radius of a point, in the given level.
  const followingDogsNear = (level, point, radius, ownerUuid) => {
    let box = new $AABB(
      point.x - radius, point.y - radius, point.z - radius,
      point.x + radius, point.y + radius, point.z + radius
    );
    let found = [];
    let list = level.getEntitiesWithin(box);
    let count = listSize(list);
    for (let i = 0; i < count; i++) {
      let entity = listGet(list, i);
      if (isFollowingDog(entity, ownerUuid)) found.push(entity);
    }
    return found;
  };

  const moveDogsTo = (server, dogs, player, dim, pos) => {
    dogs.forEach((dog) => {
      server.runCommandSilent(
        `execute in ${dim} run tp ${String(dog.uuid)} ${pos.x} ${pos.y} ${pos.z}`
      );
    });
  };

  // The player's respawn-safe compound (Forge data > PlayerPersisted), created on demand.
  const persistedData = (player) => {
    let forgeData = player.getPersistentData();
    if (!forgeData.contains(PERSISTED_KEY)) forgeData.put(PERSISTED_KEY, new $CompoundTag());
    return forgeData.getCompound(PERSISTED_KEY);
  };

  // Moves dogs hidden by older versions of this script (KubeJS persistentData) to persistedData.
  const migrateLegacy = (player) => {
    let legacy = player.persistentData;
    if (!legacy.contains(HIDDEN_KEY)) return;
    let from = legacy.getList(HIDDEN_KEY, TAG_COMPOUND);
    let data = persistedData(player);
    let list = data.contains(HIDDEN_KEY) ? data.getList(HIDDEN_KEY, TAG_COMPOUND) : new $ListTag();
    let count = listSize(from);
    for (let i = 0; i < count; i++) list.add(from.getCompound(i));
    data.put(HIDDEN_KEY, list);
    legacy.remove(HIDDEN_KEY);
  };

  const hasHiddenDogs = (player) => {
    migrateLegacy(player);
    return persistedData(player).contains(HIDDEN_KEY);
  };

  // Saves the following dogs near the owner into its data and removes them from the world.
  // Each dog leaves the world only after its NBT is stored.
  const hideDogs = (player, level, pos, ownerUuid) => {
    let dogs = followingDogsNear(level, pos, MOUNT_SEARCH, ownerUuid);
    if (dogs.length === 0) return;
    let data = persistedData(player);
    let list = data.contains(HIDDEN_KEY) ? data.getList(HIDDEN_KEY, TAG_COMPOUND) : new $ListTag();
    data.put(HIDDEN_KEY, list);
    dogs.forEach((dog) => {
      let tag = new $CompoundTag();
      if (!dog.save(tag)) return;
      list.add(tag);
      dog.remove($RemovalReason.UNLOADED_WITH_PLAYER);
    });
  };

  // Brings the hidden dogs back at the owner's feet, in the owner's current level.
  // The position goes into the NBT before loading: Entity.moveTo is overloaded under
  // different SRG names and Rhino picks the wrong one. A dog that fails to load stays
  // in the list and is retried on the next tick; nothing is dropped before it is back.
  const restoreDogs = (player, level, pos) => {
    if (!hasHiddenDogs(player)) return;
    let data = persistedData(player);
    let list = data.getList(HIDDEN_KEY, TAG_COMPOUND);
    let kept = new $ListTag();
    let count = listSize(list);
    for (let i = 0; i < count; i++) {
      let tag = list.getCompound(i);
      try {
        let where = new $ListTag();
        where.add($DoubleTag.valueOf(pos.x));
        where.add($DoubleTag.valueOf(pos.y));
        where.add($DoubleTag.valueOf(pos.z));
        tag.put("Pos", where);
        tag.putFloat("FallDistance", 0);
        let dog = $EntityType.loadEntityRecursive(tag, level, (entity) => entity);
        // false here means a dog with that UUID is already in the world: nothing to bring back.
        if (dog) level.tryAddFreshEntityWithPassengers(dog);
        else kept.add(tag);
      } catch (error) {
        kept.add(tag);
        logOnce(error);
      }
    }
    if (listSize(kept) > 0) data.put(HIDDEN_KEY, kept);
    else data.remove(HIDDEN_KEY);
  };

  const tickPlayer = (server, player) => {
    let uuid = String(player.uuid);
    let level = player.level;
    let dim = String(level.dimension);
    let pos = { x: player.x, y: player.y, z: player.z };
    let riding = player.isPassenger();
    let state = dogStates()[uuid];
    if (state) {
      let teleported = state.dim !== dim || distance3(state, pos) > TELEPORT_DISTANCE;
      let mounted = !state.riding && riding;
      let dismounted = state.riding && !riding;
      if (teleported) {
        let dogs = followingDogsNear(state.level, state, TELEPORT_SEARCH, uuid);
        moveDogsTo(server, dogs, player, dim, pos);
      }
      if (mounted) {
        hideDogs(player, level, pos, uuid);
      } else if (dismounted) {
        restoreDogs(player, level, pos);
        let dogs = followingDogsNear(level, pos, DISMOUNT_SEARCH, uuid);
        moveDogsTo(server, dogs, player, dim, pos);
      }
    } else if (!riding) {
      // First tick after login: dogs left hidden by a session that ended mid-ride.
      restoreDogs(player, level, pos);
    }
    if (!riding && state && !state.riding && hasHiddenDogs(player)) {
      // On foot with dogs still stored (respawn after dying mounted, or a failed restore).
      restoreDogs(player, level, pos);
    }
    dogStates()[uuid] = { dim: dim, x: pos.x, y: pos.y, z: pos.z, riding: riding, level: level };
  };

  global.sunlitDogFollowTick = (server) => {
    try {
      eachPlayer(server, (player) => {
        try {
          if (!player.isAlive()) return;
          tickPlayer(server, player);
        } catch (error) {
          logOnce(error);
        }
      });
    } catch (error) {
      logOnce(error);
    }
  };
})();

// Mirrors the profession stages into the scoreboard read by the
// experience.json boost multipliers, and makes sure every tree is unlocked in
// Puffish (old saves may still have trees locked from before the change).
global.syncProfessions = (server, player) => {
  global.professionIds.forEach((id) => {
    let chosen = player.stages.has(global.professionStage(id));
    let tree = global.professions[id].tree;
    // A failing command must never abort the caller (the contract task still
    // has to complete), so each step is guarded on its own.
    try {
      server.runCommandSilent(
        `scoreboard players set ${player.username} ${global.professionObjective(id)} ${chosen ? 1 : 0}`
      );
    } catch (err) {
      console.error(`[professions] scoreboard sync failed for ${id}: ${err}`);
    }
    try {
      server.runCommandSilent(`puffish_skills category unlock ${player.username} society:${tree}`);
    } catch (err) {
      console.error(`[professions] category unlock failed for ${id}: ${err}`);
    }
  });
};
