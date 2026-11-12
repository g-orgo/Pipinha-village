ItemEvents.modification((event) => {
  const e = global.guardItemEvent(event);

  // 1.21.1 data-component helpers: KJS 7 exposes no setters for mining speed,
  // attack damage or armor, so they are written through data components
  const DataComponents = Java.loadClass("net.minecraft.core.component.DataComponents");
  const Attributes = Java.loadClass("net.minecraft.world.entity.ai.attributes.Attributes");
  const Tool = Java.loadClass("net.minecraft.world.item.component.Tool");
  const ToolRule = Java.loadClass("net.minecraft.world.item.component.Tool$Rule");
  const AttributeModifier = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier");
  const AttributeEntry = Java.loadClass("net.minecraft.world.item.component.ItemAttributeModifiers$Entry");
  const ArrayList = Java.loadClass("java.util.ArrayList");
  const JavaFloat = Java.loadClass("java.lang.Float");
  const JavaOptional = Java.loadClass("java.util.Optional");

  // Multiplies the max durability by factor, skipping items without durability
  const scaleMaxDamage = (item, factor) => {
    const maxDamage = item.getComponentMap().get(DataComponents.MAX_DAMAGE);
    if (maxDamage != null && maxDamage > 0) {
      item.setMaxDamage(Math.round(maxDamage * factor));
    }
  };

  // Applies fn to the mining speed of every Tool rule that defines one
  const setMiningSpeed = (item, fn) => {
    const tool = item.getComponentMap().get(DataComponents.TOOL);
    if (tool == null) return;
    const rules = new ArrayList();
    for (let i = 0; i < tool.rules().size(); i++) {
      const rule = tool.rules().get(i);
      const speed = rule.speed();
      const newSpeed = speed.isPresent()
        ? JavaOptional.of(JavaFloat.valueOf(String(fn(speed.get()))))
        : speed;
      rules.add(new ToolRule(rule.blocks(), newSpeed, rule.correctForDrops()));
    }
    item.setTool(new Tool(rules, tool.defaultMiningSpeed(), tool.damagePerBlock()));
  };

  // Replaces the amount of every modifier of the given attribute, keeping id, operation and slot
  const mapAttributeAmount = (item, attribute, fn) => {
    const entries = item.getAttributeModifiers().modifiers();
    const newEntries = new ArrayList();
    for (let i = 0; i < entries.size(); i++) {
      const entry = entries.get(i);
      if (entry.attribute().equals(attribute)) {
        const old = entry.modifier();
        const modifier = new AttributeModifier(old.id(), fn(old.amount()), old.operation());
        newEntries.add(new AttributeEntry(entry.attribute(), modifier, entry.slot()));
      } else {
        newEntries.add(entry);
      }
    }
    item.setAttributeModifiers(newEntries);
  };

  // Armor points are the ARMOR modifier amount directly
  const setArmorPoints = (item, points) => {
    mapAttributeAmount(item, Attributes.ARMOR, () => points);
  };

  // Vanilla attack damage is a modifier on top of the player base of 1.0,
  // so a total damage value maps to total - 1 on the modifier
  const setAttackDamage = (item, total) => {
    mapAttributeAmount(item, Attributes.ATTACK_DAMAGE, () => total - 1);
  };

  const addAttackDamage = (item, delta) => {
    mapAttributeAmount(item, Attributes.ATTACK_DAMAGE, (amount) => amount + delta);
  };

  e.modify("*", (item) => {
    scaleMaxDamage(item, 3);
  });
  e.modify("gag:energized_hearthstone", (item) => {
    item.setMaxDamage(2);
  });
  e.modify("gag:hearthstone", (item) => {
    item.setMaxDamage(2);
  });
  e.modify("gag:escape_rope", (item) => {
    item.setMaxDamage(1024);
  });
  global.geodeList.forEach((geodeItem) => {
    const { item } = geodeItem;
    e.modify(item, (item) => {
      item.rarity = "uncommon";
    });
  });
  global.frozenGeodeList.forEach((geodeItem) => {
    const { item } = geodeItem;
    e.modify(item, (item) => {
      item.rarity = "rare";
    });
  });
  global.magmaGeodeList.forEach((geodeItem) => {
    const { item } = geodeItem;
    e.modify(item, (item) => {
      item.rarity = "epic";
    });
  });
  e.modify("society:sparkstone", (item) => {
    item.rarity = "epic";
  });
  e.modify("numismatics:neptunium_coin", (item) => {
    item.rarity = "rare";
  });
  e.modify(
    [
      "society:ancient_fruit",
      "society:ancient_fruit_seed",
      "society:sunlit_crystal",
      "society:plushie_wand",
      "society:treasure_totem",
      "society:recycled_core",
      "society:bubble_totem",
      "society:mystic_syrup",
      "society:net_bobber",
      "society:needle_bobber",
      "society:sparkpod",
      "society:sparkpod_seed",
      "cluttered:willow_sapling",
      "cluttered:willow_log",
      "cluttered:flowering_willow_log",
      "cluttered:flowering_willow_leaves",
      "cluttered:willow_leaves",
      "cluttered:willow_vines",
      "society:women_who_run_with_the_plushies",
      "society:the_spark_also_rises",
      "society:the_red_and_the_black",
      "society:the_quality_of_the_earth",
      "society:pond_house_five",
      "society:animal_cracker",
      "society:moon_statue",
      "society:roe_recycler",
      "minecraft:enchanting_table",
      "society:spinel"
    ],
    (item) => {
      item.rarity = "epic";
    },
  );
  e.modify(
    ["society:milk_pail", "society:magic_shears", "society:mood_scanner"],
    (item) => {
      item.maxStackSize = 1;
    },
  );
  e.modify("society:aquamarine", (item) => {
    item.rarity = "uncommon";
  });
  e.modify("society:amethyst_chunk", (item) => {
    item.rarity = "uncommon";
  });
  e.modify("society:ruby", (item) => {
    item.rarity = "rare";
  });
  e.modify("society:topaz", (item) => {
    item.rarity = "rare";
  });
  e.modify("society:magic_rope", (item) => {
    item.rarity = "rare";
  });
  e.modify("society:magic_tunnel", (item) => {
    item.rarity = "rare";
  });
  e.modify("quark:diamond_heart", (item) => {
    item.rarity = "epic";
  });
  e.modify("society:jade", (item) => {
    item.rarity = "epic";
  });
  e.modify("society:prismatic_shard", (item) => {
    item.rarity = "epic";
  });
  e.modify("society:prismatic_shard_block", (item) => {
    item.rarity = "epic";
  });
  e.modify("society:golden_clock", (item) => {
    item.rarity = "epic";
  });
  const goldVanillaTools = [
    "minecraft:golden_hoe",
    "minecraft:golden_axe",
    "minecraft:golden_pickaxe",
    "minecraft:golden_shovel",
  ];
  goldVanillaTools.forEach((tool) => {
    e.modify(tool, (item) => {
      setMiningSpeed(item, () => 7);
      item.setTier((tier) => {
        tier.setIncorrectBlocksForDropsTag("minecraft:incorrect_for_diamond_tool");
        tier.setSpeed(7);
      });
    });
  });
  const goldHammers = [
    "justhammers:gold_reinforced_impact_hammer",
    "justhammers:gold_hammer",
    "justhammers:gold_destructor_hammer",
    "justhammers:gold_impact_hammer",
    "justhammers:gold_reinforced_hammer",
  ];
  goldHammers.forEach((tool) => {
    e.modify(tool, (item) => {
      setMiningSpeed(item, () => 7);
      item.setTier((tier) => {
        tier.setIncorrectBlocksForDropsTag("minecraft:incorrect_for_diamond_tool");
        tier.setSpeed(7);
      });
    });
  });
  e.modify("minecraft:golden_sword", (item) => {
    setAttackDamage(item, 5.5);
  });
  e.modify("minecraft:golden_axe", (item) => {
    setAttackDamage(item, 8);
  });
  const goldTools = [
    "farmersdelight:golden_knife",
    "aquaculture:gold_fishing_rod",
    "aquaculture:gold_fillet_knife",
    "sewingkit:gold_sewing_needle",
    "justhammers:gold_reinforced_hammer",
    "minecraft:golden_sword",
    "minecraft:golden_hoe",
    "minecraft:golden_axe",
    "minecraft:golden_pickaxe",
    "minecraft:golden_shovel",
    "justhammers:gold_reinforced_impact_hammer",
    "justhammers:gold_destructor_hammer",
    "justhammers:gold_impact_hammer",
    "justhammers:gold_hammer",
  ];
  goldTools.forEach((tool) => {
    e.modify(tool, (item) => {
      // 1.20.1 had a justhammers x2 branch that never matched (tool is a string), so every gold tool got x16; keep that.
      scaleMaxDamage(item, 16);
    });
  });
  e.modify("minecraft:golden_helmet", (item) => {
    scaleMaxDamage(item, 3);
    setArmorPoints(item, 2.5);
  });
  e.modify("minecraft:golden_chestplate", (item) => {
    scaleMaxDamage(item, 3);
    setArmorPoints(item, 7);
  });
  e.modify("minecraft:golden_leggings", (item) => {
    scaleMaxDamage(item, 3);
    setArmorPoints(item, 5.5);
  });
  e.modify("minecraft:golden_boots", (item) => {
    scaleMaxDamage(item, 3);
    setArmorPoints(item, 2.5);
  });
  e.modify("twigs:twig", (item) => (item.burnTime = 200));
  const netheriteTools = [
    "minecraft:netherite_axe",
    "minecraft:netherite_hoe",
    "minecraft:netherite_pickaxe",
    "minecraft:netherite_shovel",
  ];
  netheriteTools.forEach((armor) => {
    e.modify(armor, (item) => {
      setMiningSpeed(item, (speed) => speed + 1);
      addAttackDamage(item, 2);
    });
  });
  e.modify("minecraft:netherite_sword", (item) => {
    setAttackDamage(item, 10);
  });
  e.modify("minecraft:netherite_helmet", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 4);
  });
  e.modify("minecraft:netherite_chestplate", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 9);
  });
  e.modify("minecraft:netherite_leggings", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 7);
  });
  e.modify("minecraft:netherite_boots", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 3);
  });
  e.modify("botania:terrasteel_helmet", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 4);
  });
  e.modify("botania:terrasteel_chestplate", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 9);
  });
  e.modify("botania:terrasteel_leggings", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 7);
  });
  e.modify("botania:terrasteel_boots", (item) => {
    scaleMaxDamage(item, 1.5);
    setArmorPoints(item, 3);
  });

  e.modify("botania:manasteel_sword", (item) => {
    setAttackDamage(item, 7);
  });
  e.modify("botania:elementium_sword", (item) => {
    setAttackDamage(item, 8);
  });
  e.modify("oreganized:electrum_sword", (item) => {
    setAttackDamage(item, 8);
  });
  // Netherite Tier
  e.modify("botania:terra_sword", (item) => {
    setAttackDamage(item, 10);
  });
  e.modify("botania:star_sword", (item) => {
    setAttackDamage(item, 10);
  });
  e.modify("botania:thunder_sword", (item) => {
    setAttackDamage(item, 10);
  });
});
