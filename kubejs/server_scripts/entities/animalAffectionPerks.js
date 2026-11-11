console.info("[SOCIETY] animalAffectionPerks.js loaded");

// Affection perks: pets gain attribute bonuses from their affection, starting at
// 5 hearts (fraction 1/6) and reaching the full bonus at 10 hearts (fraction 1).
// Tamed vanilla wolves that reach 10 hearts with their owner earn Wolf Armor once.
// Below 5 hearts the bonus is removed.
(function () {
  const $UUID = Java.loadClass("java.util.UUID");
  const $AttributeModifier = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier");
  const $Operation = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation");
  const $EquipmentSlot = Java.loadClass("net.minecraft.world.entity.EquipmentSlot");
  const $ForgeRegistries = Java.loadClass("net.minecraftforge.registries.ForgeRegistries");
  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");

  // Hearts needed before any bonus applies, and the hearts that give the full bonus.
  const PERK_START_HEARTS = 5;
  const PERK_FULL_HEARTS = 10;
  const WOLF_ARMOR_HEARTS = 10;
  const WOLF_ARMOR_ITEM = "minecraft:wolf_armor";
  const ARMOR_GIFT_KEY = "armor_gift";
  const ARMOR_FLAG = "affectionArmorGiven";

  // One fixed UUID per attribute, so each perk is a single modifier that gets replaced.
  const ATTRIBUTE_UUIDS = {
    "generic.attack_damage": "7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e01",
    "generic.armor": "7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e02",
    "generic.movement_speed": "7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e03",
    "horse.jump_strength": "7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e04",
    "generic.flying_speed": "7a1d9e02-3b6c-4f58-8e21-5c4b3a2f1e05",
  };

  // Perk groups, one per species group. Each entry: attribute id, amount at full
  // affection, operation. Amounts are multiplied by the affection fraction.
  const PERK_GROUPS = [
    {
      types: ["minecraft:wolf", "quark:shiba", "quark:foxhound", "wildernature:dog", "wildernature:red_wolf"],
      perks: [
        { attr: "generic.attack_damage", amount: 4, op: "ADDITION" },
        { attr: "generic.armor", amount: 8, op: "ADDITION" },
      ],
    },
    {
      types: ["buzzier_bees:grizzly_bear", "minecraft:polar_bear"],
      perks: [
        { attr: "generic.attack_damage", amount: 4, op: "ADDITION" },
        { attr: "generic.armor", amount: 6, op: "ADDITION" },
      ],
    },
    {
      types: ["minecraft:horse"],
      perks: [
        { attr: "generic.movement_speed", amount: 0.2, op: "MULTIPLY_BASE" },
        { attr: "horse.jump_strength", amount: 0.2, op: "MULTIPLY_BASE" },
      ],
    },
    {
      types: ["minecraft:axolotl", "crittersandcompanions:ferret"],
      perks: [
        { attr: "generic.attack_damage", amount: 2, op: "ADDITION" },
        { attr: "generic.movement_speed", amount: 0.15, op: "MULTIPLY_BASE" },
      ],
    },
    {
      types: ["minecraft:cat", "wildernature:hedgehog", "hamsters:hamster", "wildernature:owl", "minecraft:allay"],
      perks: [
        { attr: "generic.movement_speed", amount: 0.2, op: "MULTIPLY_BASE" },
        { attr: "generic.flying_speed", amount: 0.2, op: "MULTIPLY_BASE" },
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

  const attributeOf = (id) => $ForgeRegistries.ATTRIBUTES.getValue(new $ResourceLocation("minecraft", id));

  // Sets the permanent modifier for one attribute. Skips when unchanged, removes at 0.
  const setPerk = (target, attrId, amount, opName) => {
    let attribute = attributeOf(attrId);
    if (!attribute) return;
    let instance = target.getAttribute(attribute);
    if (!instance) return;
    let uuid = $UUID.fromString(ATTRIBUTE_UUIDS[attrId]);
    let current = instance.getModifier(uuid);
    if (amount <= 0) {
      if (current) instance.removeModifier(uuid);
      return;
    }
    if (current && Math.abs(current.getAmount() - amount) < 0.0001) return;
    if (current) instance.removeModifier(uuid);
    instance.addPermanentModifier(
      new $AttributeModifier(uuid, "Sunlit affection " + attrId, amount, $Operation[opName])
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

  // True when a click should pet the animal before any other interaction: a real
  // player with an empty main hand, on a pet or husbandry animal not petted yet today.
  global.sunlitShouldPetFirst = (hand, player, item, target, level) => {
    if (String(hand) !== "MAIN_HAND") return false;
    if (player.isFake()) return false;
    let empty = !item || (typeof item.isEmpty === "function" ? item.isEmpty() : String(item) === "minecraft:air");
    if (!empty) return false;
    if (!global.checkEntityTag(target, "society:pet_animal") && !global.checkEntityTag(target, "society:husbandry_animal")) return false;
    return Number(target.persistentData.getInt("ageLastPet")) !== Number(global.getDay(level));
  };
})();
