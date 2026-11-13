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

const insertPriceLines = (e, index, lines) => {
  lines.forEach((line, offset) => {
    e.lines.add(index + offset, Text.of(line));
  });
};

const getStackBonusValueTooltips = (e, number, item, attribute, quality) => {
  let value = number;
  let clientStages = Client.player.stages;
  let bonusTooltips = [];
  let qualityDoubled = false;
  let attributeMult = global.getAttributeMultiplier(
    Client.player,
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
    if (item.customData && item.customData.getDouble("size")) {
      size = item.customData.getDouble("size");
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
  insertPriceLines(e, 1, [
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
    insertPriceLines(e, 2 + index, [bonus]);
  });
  if (attributeMult > 1) {
    insertPriceLines(e, bonusTooltips.length + 2, [
      getAttributeText(attribute),
      Text.green(` +${Math.round((attributeMult - 1) * 100)}%`),
    ]);
  } else {
    insertPriceLines(e, bonusTooltips.length + 2, [getAttributeText(attribute)]);
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
const priceSources = {};

const renderPriceTooltip = (e, value, attribute) => {
  const item = e.item;
  const quality = global.getQualityLevel(item) || undefined;
  // Brew levels, wine age and other mod quality tiers change the real sale value
  const variation = global.getVariationMultiplier(item.customData, item);
  const adjustedValue = variation === 1 ? value : Math.round(value * variation);
  if (e.shift) {
    getStackBonusValueTooltips(e, adjustedValue, item, attribute, quality);
  } else {
    // Quality is applied inside formatNumber; the seasonal bonus multiplies the value first (same result as the bin, up to rounding)
    const seasonal = global.getSeasonalMultiplier(item, getTooltipSeason());
    insertPriceLines(e, 1, [
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
    let nextLine = 2;
    if (seasonal > 1) {
      insertPriceLines(e, nextLine, [
        getSeasonalBonusText(
          seasonal,
          seasonalBonusCoins(adjustedValue, seasonal, quality, false, item.id)
        ),
      ]);
      nextLine++;
    }
    // Gravel nuggets and their crafted metal carry SunlitArtificial: sell value is cut by 30%
    if (item.customData && item.customData.getByte("SunlitArtificial") === 1) {
      insertPriceLines(e, nextLine, [
        Text.translatable("item.society.artificial_penalty").red(),
      ]);
      nextLine++;
    }
    const subprocess = getSubprocessBonusText(item.id);
    if (subprocess) insertPriceLines(e, nextLine, [subprocess]);
  }
};

ItemEvents.dynamicTooltips("pipinha:price", (e) => {
  const source = priceSources[String(e.item.id)];
  if (source) renderPriceTooltip(e, source.value, source.attribute);
});

const addPriceTooltip = (tooltip, sellable, attribute) => {
  const id = String(sellable.item);
  // One tooltip per item id: a repeated item keeps its first price (same as the crop dedupe)
  if (priceSources[id]) return;
  priceSources[id] = {
    value: global.getConfiguredValue(sellable.value, attribute),
    attribute: attribute,
  };
  tooltip.modify(sellable.item, (text) => text.dynamic("pipinha:price"));
};

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

ItemEvents.dynamicTooltips("pipinha:coin", (e) => {
  const id = String(e.item.id);
  const coin = id.split(":")[1];
  if (!id.includes("_coin")) {
    e.lines.remove(1);
  }
  if (e.shift) {
    insertPriceLines(e, 1, [
      Text.translatable(
        "tooltip.society.coins",
        `${calculateCost(coin, 1, e.item.count)}`
      ).white(),
      Text.of(" "),
      Text.translatable("tooltip.society.stack_value").gray(),
    ]);
  } else {
    insertPriceLines(e, 1, [
      Text.translatable(
        "tooltip.society.coins",
        `${calculateCost(coin, 1, 1)}`
      ).white(),
      Text.of(" "),
      Text.translatable(
        "tooltip.society.hold_key",
        Text.translatable("key.keyboard.shift").gray()
      ).darkGray(),
    ]);
  }
});

const getLongwingTooltips = (e) => {
  const item = e.item;
  let variant;
  let size = 1.0;
  let price = 1;
  if (item.customData) {
    if (item.customData.contains("variant")) {
      variant = item.customData.getString("variant");
    }
    if (item.customData.getDouble("size")) {
      size = item.customData.getDouble("size");
    }
  }
  global.longwings.forEach((wing) => {
    if (wing.variant == variant) price = (16 - wing.rarity) * 78;
  });
  price += Math.round((size / 0.01) * 4);
  if (e.shift) {
    getStackBonusValueTooltips(e, price, item, "meat", 0);
  } else {
    insertPriceLines(e, 1, [
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
};
// Item.of('longwings:moth', '{size:1.0f,variant:"small_emerald"}')
ItemEvents.dynamicTooltips("pipinha:longwing", (e) => getLongwingTooltips(e));

ItemEvents.modifyTooltips((event) => {
  const tooltip = global.guardItemEvent(event);
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
    tooltip.modify(coin, (text) => text.dynamic("pipinha:coin"));
  });

  tooltip.modify("longwings:butterfly", (text) => text.dynamic("pipinha:longwing"));
  tooltip.modify("longwings:moth", (text) => text.dynamic("pipinha:longwing"));
  // Ore
  global.ore.forEach((item) => {
    addPriceTooltip(tooltip, item, "gem");
  });
  // Pristine
  global.pristine.forEach((item) => {
    addPriceTooltip(tooltip, item, "gem");
  });
  // Geodes
  global.geodeList.forEach((geodeItem) => {
    addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  global.frozenGeodeList.forEach((geodeItem) => {
    addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  global.magmaGeodeList.forEach((geodeItem) => {
    addPriceTooltip(tooltip, geodeItem, "gem");
    tooltip.add(
      geodeItem.item,
      Text.translatable("tooltip.society.item_type.mineral").gray()
    );
  });
  // Gem
  global.gems.forEach((gem) => {
    addPriceTooltip(tooltip, gem, "gem");
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
    addPriceTooltip(tooltip, gem, "gem");
  });
  // Artifact
  global.artifacts.forEach((artifact) => {
    addPriceTooltip(tooltip, artifact, "meat");
  });
  global.relics.forEach((artifact) => {
    addPriceTooltip(tooltip, artifact, "meat");
  });
  // Crops
  // A crop listed twice (a duplicate and its canonical item share an entry) gets one price line
  const pricedCropIds = {};
  global.crops.forEach((crop) => {
    if (pricedCropIds[String(crop.item)]) return;
    pricedCropIds[String(crop.item)] = true;
    addPriceTooltip(tooltip, crop, "crop");
  });
  // Fruits (skip the ones already priced through global.crops so the line is not duplicated)
  global.fruits.forEach((fruit) => {
    if (pricedCropIds[String(fruit.item)]) return;
    addPriceTooltip(tooltip, fruit, "crop");
  });
  // Meat
  global.animalProducts.forEach((meat) => {
    addPriceTooltip(tooltip, meat, "crop");
  });
  // Wines
  global.wines.forEach((wine) => {
    addPriceTooltip(tooltip, wine, "wood");
  });
  // Brews
  global.brews.forEach((brew) => {
    addPriceTooltip(tooltip, brew, "wood");
  });
  // Preserves
  global.preserves.forEach((jar) => {
    addPriceTooltip(tooltip, jar, "wood");
  });
  // Dehydrated
  global.dehydrated.forEach((jar) => {
    addPriceTooltip(tooltip, jar, "wood");
  });
  // Artisan goods
  global.artisanGoods.forEach((good) => {
    addPriceTooltip(tooltip, good, "wood");
  });
  // Fish
  global.fish.forEach((fish) => {
    addPriceTooltip(tooltip, fish, "crop");
  });
  global.smokedFish.forEach((fish) => {
    addPriceTooltip(tooltip, fish, "wood");
  });
  global.agedRoe.forEach((fish) => {
    addPriceTooltip(tooltip, fish, "wood");
  });
  // Cocktails
  global.cocktails.forEach((cocktail) => {
    addPriceTooltip(tooltip, cocktail, "crop");
  });
  // herbalbrews
  global.herbalBrews.forEach((brew) => {
    addPriceTooltip(tooltip, brew, "crop");
  });
  // Logs
  global.logs.forEach((log) => {
    addPriceTooltip(tooltip, log, "crop");
  });
  // Cooking
  global.cooking.forEach((dish) => {
    addPriceTooltip(tooltip, dish, "crop");
  });
  // Misc
  global.miscAdventurer.forEach((miscItem) => {
    addPriceTooltip(tooltip, miscItem, "meat");
  });
});
