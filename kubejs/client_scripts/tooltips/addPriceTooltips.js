// Same quality math as calculateQualityValue in globalShippingBinHandlers.js (dish table, premium dishes)
const formatNumber = (number, quality, doubled, itemId) => {
  let value;
  if (quality) {
    value = Math.round(number * global.getQualityMultiplier(quality, doubled, itemId));
  } else {
    value = number;
  }
  return global.formatPrice(value);
};

// Season of the player's current level, used for the seasonal crop bonus
// getSeasonFromLevel returns "spring" | "summer" | "autumn" | "winter" (seasonsSupportStartup.js L5-16)
const getTooltipSeason = () => {
  const level = Client.player && Client.player.level;
  return level ? global.getSeasonFromLevel(level) : undefined;
};

const getStackBonusValueTooltips = (text, number, item, attribute, quality) => {
  let value = number;
  let clientStages = Client.player.stages;
  let bonusTooltips = [];
  let qualityDoubled = false;
  let attributeMult = global.getAttributeMultiplier(
    Client.player.nbt.Attributes,
    `shippingbin:${attribute}_sell_multiplier`
  );
  let hasMultipliers = attributeMult > 1;
  if (
    clientStages.has("bluegill_meridian") &&
    item.id == "aquaculture:bluegill"
  ) {
    hasMultipliers = true;
    value = 666;
    bonusTooltips.push(
      Text.translatable("item.society.bluegill_meridian.price_modifier").aqua()
    );
  }
  if (
    clientStages.has("phenomenology_of_treasure") &&
    (item.hasTag("society:artifacts") || item.hasTag("society:relics"))
  ) {
    hasMultipliers = true;
    value *= 3;
    bonusTooltips.push(
      Text.translatable(
        "item.society.phenomenology_of_treasure.price_modifier"
      ).aqua()
    );
  }
  if (
    clientStages.has("brine_and_punishment") &&
    item.hasTag("society:brine_and_punishment")
  ) {
    hasMultipliers = true;
    value *= 2;
    bonusTooltips.push(
      Text.translatable(
        "item.society.brine_and_punishment.price_modifier"
      ).aqua()
    );
  }

  if (
    clientStages.has("the_metamorphosize") &&
    ["longwings:moth", "longwings:butterfly"].includes(item.id)
  ) {
    hasMultipliers = true;
    let size = 1.0;
    if (item.nbt) {
      if (item.nbt.size && typeof item.nbt.size !== "function") {
        size = item.nbt.size;
      }
    }
    let increase = Number(Math.round((size / 0.01) * 4) * 2);
    value += increase;
    bonusTooltips.push(
      Text.translatable(
        "item.society.the_metamorphosize.price_modifier", String(increase)
      ).aqua()
    );
  }
  if (
    quality > 0 &&
    clientStages.has("the_quality_of_the_earth") &&
    attribute.equals("crop") &&
    !item.hasTag("minecraft:fishes")
  ) {
    hasMultipliers = true;
    qualityDoubled = true
    bonusTooltips.push(
      Text.translatable(
        "item.society.the_quality_of_the_earth.price_modifier"
      ).aqua()
    );
  }
  value = Math.round(value * item.count * attributeMult);
  const seasonalMult = global.getSeasonalMultiplier(item, getTooltipSeason());
  if (seasonalMult > 1) {
    let before = value;
    value = Math.round(value * seasonalMult);
    bonusTooltips.push(
      getSeasonalBonusText(
        seasonalMult,
        seasonalBonusCoins(before, seasonalMult, quality, qualityDoubled, item.id)
      )
    );
  }
  text.add(1, [
    Text.translatable(
      "tooltip.society.coins",
      `${formatNumber(value, quality, qualityDoubled, item.id)}`
    ).white(),
    Text.of(" "),
    Text.translatable("tooltip.society.stack_value")
      .gray()
      .append(
        hasMultipliers
          ? Text.translatable("tooltip.society.multipliers")
          : Text.empty()
      ),
  ]);
  bonusTooltips.forEach((bonus, index) => {
    text.add(2 + index, [bonus]);
  });
  if (attributeMult > 1) {
    text.add(bonusTooltips.length + 2, [
      getAttributeText(attribute),
      Text.green(` +${Math.round((attributeMult - 1) * 100)}%`),
    ]);
  } else {
    text.add(bonusTooltips.length + 2, [getAttributeText(attribute)]);
  }
};

// Bônus sazonal: "3 moedas (+8%)". As moedas são o que o bônus adiciona no valor
// final (já com a qualidade aplicada); a porcentagem fica entre parênteses.
const seasonalBonusCoins = (baseValue, multiplier, quality, doubled, itemId) => {
  if (!(multiplier > 1) || !(baseValue > 0)) return 0;
  const q = quality ? global.getQualityMultiplier(quality, doubled, itemId) : 1;
  return Math.round(Math.round(baseValue * multiplier) * q) - Math.round(baseValue * q);
};

const getSeasonalBonusText = (multiplier, coins) => {
  const pct = Math.round((multiplier - 1) * 100);
  if (!(coins > 0)) {
    return Text.translatable("item.society.seasonal_bonus_only", String(pct)).aqua();
  }
  return Text.translatable(
    "item.society.seasonal_bonus",
    global.formatPrice(coins),
    String(pct)
  ).aqua();
};

// Bônus de subprocesso: "316 moedas (+1580%)".
// Fonte: global.processValue (kubejs/startup_scripts/globalProcessValue.js),
// no formato "moedas|porcentagem" em texto.
const getSubprocessBonusText = (itemId) => {
  const table = global.processValue;
  if (!table) return null;
  const raw = table[itemId];
  if (!raw) return null;
  const parts = String(raw).split("|");
  const coins = Number(parts[0]);
  const pct = Number(parts[1]);
  if (!(coins > 0) || !(pct > 0)) return null;
  return Text.translatable(
    "item.society.subprocess_bonus",
    global.formatPrice(coins),
    String(pct)
  ).aqua();
};

const getAttributeText = (attribute) => {
  switch (attribute) {
    case "crop":
      return Text.translatable("tooltip.society.farmer_product").gold();
    case "wood":
      return Text.translatable("tooltip.society.artisan_product").gold();
    case "gem":
      return Text.translatable("tooltip.society.geologist_product").gold();
    case "meat":
      return Text.translatable("tooltip.society.adventurer_product").gold();
    default:
      console.log(`Invalid attribute`);
  }
};
global.addPriceTooltip = (tooltip, sellable, attribute) => {
  let value = global.getConfiguredValue(sellable.value, attribute);
  tooltip.addAdvanced(sellable.item, (item, advanced, text) => {
    let quality;
    if (item.nbt && item.nbt.quality_food) {
      quality = item.nbt.quality_food.quality;
    }
    // Brew levels, wine age and other mod quality tiers change the real sale value
    const variation = global.getVariationMultiplier(item.nbt);
    const adjustedValue = variation === 1 ? value : Math.round(value * variation);
    if (tooltip.shift) {
      getStackBonusValueTooltips(text, adjustedValue, item, attribute, quality);
    } else {
      // Quality is applied inside formatNumber; the seasonal bonus multiplies the value first (same result as the bin, up to rounding)
      const seasonal = global.getSeasonalMultiplier(item, getTooltipSeason());
      text.add(1, [
        Text.translatable(
          "tooltip.society.coins",
          `${formatNumber(seasonal > 1 ? Math.round(adjustedValue * seasonal) : adjustedValue, quality, false, item.id)}`
        ).white(),
        Text.of(" "),
        Text.translatable(
          "tooltip.society.hold_key",
          Text.translatable("key.keyboard.shift").gray()
        ).darkGray(),
      ]);
      if (seasonal > 1) {
        text.add(2, [
          getSeasonalBonusText(
            seasonal,
            seasonalBonusCoins(adjustedValue, seasonal, quality, false, item.id)
          ),
        ]);
      }
      const subprocess = getSubprocessBonusText(item.id);
      if (subprocess) text.add(seasonal > 1 ? 3 : 2, [subprocess]);
    }
  });
};

ItemEvents.tooltip((tooltip) => {
  const calculateCost = (coin, count, stackSize) => {
    let value = 0;
    switch (coin) {
      case "spur":
        value = 1;
        break;
      case "bevel":
        value = 8;
        break;
      case "sprocket":
        value = 16;
        break;
      case "cog":
        value = 64;
        break;
      case "crown":
        value = 512;
        break;
      case "sun":
        value = 4096;
        break;
      case "neptunium_coin":
        value = 32768;
        break;
      case "ancient_coin":
        value = 262144;
        break;
      case "prismatic_coin":
        value = 16777216;
        break;
      default:
        console.log(`Invalid coin`);
    }
    return formatNumber(value * count * (stackSize || 1));
  };
  const coinTooltips = [
    "numismatics:spur",
    "numismatics:bevel",
    "numismatics:sprocket",
    "numismatics:cog",
    "numismatics:crown",
    "numismatics:sun",
    "numismatics:neptunium_coin",
    "numismatics:ancient_coin",
    "numismatics:prismatic_coin",
  ];
  coinTooltips.forEach((coin) => {
    tooltip.addAdvanced(coin, (item, advanced, text) => {
      if (!coin.includes("_coin")) {
        text.remove(1);
      }
      if (tooltip.shift) {
        text.add(1, [
          Text.translatable(
            "tooltip.society.coins",
            `${calculateCost(coin.path, 1, item.count)}`
          ).white(),
          Text.of(" "),
          Text.translatable("tooltip.society.stack_value").gray(),
        ]);
      } else {
        text.add(1, [
          Text.translatable(
            "tooltip.society.coins",
            `${calculateCost(coin.path, 1, 1)}`
          ).white(),
          Text.of(" "),
          Text.translatable(
            "tooltip.society.hold_key",
            Text.translatable("key.keyboard.shift").gray()
          ).darkGray(),
        ]);
      }
    });
  });

  tooltip.addAdvanced("splendid_slimes:plort", (item, advanced, text) => {
    let plortType;
    let price;
    if (item.nbt && item.nbt.plort) {
      plortType = item.nbt.plort.id;
    }
    global.plorts.forEach((plort) => {
      if (plort.type == plortType) price = plort.value;
    });
    if (tooltip.shift) {
      getStackBonusValueTooltips(text, price, item, "crop", 0);
    } else {
      text.add(1, [
        Text.translatable(
          "tooltip.society.coins",
          `${formatNumber(price, 0)}`
        ).white(),
        Text.of(" "),
        Text.translatable(
          "tooltip.society.hold_key",
          Text.translatable("key.keyboard.shift").gray()
        ).darkGray(),
      ]);
    }
  });

  tooltip.addAdvanced("splendid_slimes:slime_heart", (item, advanced, text) => {
    let heartType;
    let price;
    if (item.nbt && item.nbt.slime) {
      heartType = item.nbt.slime.id;
    }
    global.slimeHearts.forEach((heart) => {
      if (heart.type == heartType) price = heart.value;
    });
    if (tooltip.shift) {
      getStackBonusValueTooltips(text, price, item, "crop", 0);
    } else {
      text.add(1, [
        Text.translatable(
          "tooltip.society.coins",
          `${formatNumber(price, 0)}`
        ).white(),
        Text.of(" "),
        Text.translatable(
          "tooltip.society.hold_key",
          Text.translatable("key.keyboard.shift").gray()
        ).darkGray(),
      ]);
    }
  });
  const getLongwingTooltips = (item, text) => {
    let variant;
    let size = 1.0;
    let price = 1;
    if (item.nbt) {
      if (item.nbt.variant) {
        variant = item.nbt.variant;
      }
      if (item.nbt.size && typeof item.nbt.size !== "function") {
        size = item.nbt.size;
      }
    }
    global.longwings.forEach((wing) => {
      if (wing.variant == variant) price = (16 - wing.rarity) * 78;
    });
    price += Math.round((size / 0.01) * 4)
    if (tooltip.shift) {
      getStackBonusValueTooltips(text, price, item, "meat", 0);
    } else {
      text.add(1, [
        Text.translatable(
          "tooltip.society.coins",
          `${formatNumber(price, 0)}`
        ).white(),
        Text.of(" "),
        Text.translatable(
          "tooltip.society.hold_key",
          Text.translatable("key.keyboard.shift").gray()
        ).darkGray(),
      ]);
    }
  }
  // Item.of('longwings:moth', '{size:1.0f,variant:"small_emerald"}')
  tooltip.addAdvanced("longwings:butterfly", (item, advanced, text) => {
    getLongwingTooltips(item, text)
  });
  tooltip.addAdvanced("longwings:moth", (item, advanced, text) => {
    getLongwingTooltips(item, text)
  });
  // Ore
  global.ore.forEach((item) => {
    global.addPriceTooltip(tooltip, item, "gem");
  });
  // Pristine
  global.pristine.forEach((item) => {
    global.addPriceTooltip(tooltip, item, "gem");
  });
  // Geodes
  global.geodeList.forEach((geodeItem) => {
    global.addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  global.frozenGeodeList.forEach((geodeItem) => {
    global.addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  global.magmaGeodeList.forEach((geodeItem) => {
    global.addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  // Gem
  global.gems.forEach((gem) => {
    global.addPriceTooltip(tooltip, gem, "gem");
    tooltip.add(
      gem.item,
      Text.translatable("tooltip.society.item_type.gem").gray()
    );
  });
  [
    "society:sparkstone",
    "minecraft:emerald",
    "minecraft:diamond",
    "minecraft:amethyst_shard",
    "minecraft:quartz",
    "society:prismatic_shard",
    "minecraft:prismarine_crystals",
  ].forEach((gem) => {
    tooltip.add(gem, Text.translatable("tooltip.society.item_type.gem").gray());
  });
  global.miscGeologist.forEach((gem) => {
    global.addPriceTooltip(tooltip, gem, "gem");
  });
  // Artifact
  global.artifacts.forEach((artifact) => {
    global.addPriceTooltip(tooltip, artifact, "meat");
  });
  global.relics.forEach((artifact) => {
    global.addPriceTooltip(tooltip, artifact, "meat");
  });
  // Crops
  // A crop listed twice (a duplicate and its canonical item share an entry) gets one price line
  const pricedCropIds = {};
  global.crops.forEach((crop) => {
    if (pricedCropIds[String(crop.item)]) return;
    pricedCropIds[String(crop.item)] = true;
    global.addPriceTooltip(tooltip, crop, "crop");
  });
  // Fruits (skip the ones already priced through global.crops so the line is not duplicated)
  global.fruits.forEach((fruit) => {
    if (pricedCropIds[String(fruit.item)]) return;
    global.addPriceTooltip(tooltip, fruit, "crop");
  });
  // Meat
  global.animalProducts.forEach((meat) => {
    global.addPriceTooltip(tooltip, meat, "crop");
  });
  // Wines
  global.wines.forEach((wine) => {
    global.addPriceTooltip(tooltip, wine, "wood");
  });
  // Brews
  global.brews.forEach((brew) => {
    global.addPriceTooltip(tooltip, brew, "wood");
  });
  // Preserves
  global.preserves.forEach((jar) => {
    global.addPriceTooltip(tooltip, jar, "wood");
  });
  // Dehydrated
  global.dehydrated.forEach((jar) => {
    global.addPriceTooltip(tooltip, jar, "wood");
  });
  // Artisan goods
  global.artisanGoods.forEach((good) => {
    global.addPriceTooltip(tooltip, good, "wood");
  });
  // Fish
  global.fish.forEach((fish) => {
    global.addPriceTooltip(tooltip, fish, "crop");
  });
  global.smokedFish.forEach((fish) => {
    global.addPriceTooltip(tooltip, fish, "wood");
  });
  global.agedRoe.forEach((fish) => {
    global.addPriceTooltip(tooltip, fish, "wood");
  });
  // Cocktails
  global.cocktails.forEach((cocktail) => {
    global.addPriceTooltip(tooltip, cocktail, "crop");
  });
  // herbalbrews
  global.herbalBrews.forEach((brew) => {
    global.addPriceTooltip(tooltip, brew, "crop");
  });
  // Logs
  global.logs.forEach((log) => {
    global.addPriceTooltip(tooltip, log, "crop");
  });
  // Cooking
  global.cooking.forEach((dish) => {
    global.addPriceTooltip(tooltip, dish, "crop");
  });
  // Misc
  global.miscAdventurer.forEach((miscItem) => {
    global.addPriceTooltip(tooltip, miscItem, "meat");
  });
});
