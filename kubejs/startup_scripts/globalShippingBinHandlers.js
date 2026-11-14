// Priority: 1000
// Cooked dishes (global.cooking) and their ids, built on first use so the order of startup
// scripts does not matter (globalRegistry.js runs after this file).
// Kept in script scope: values stored on `global` become a Java map, and reading a missing id from it
// threw a NullPointerException in tooltips for every item with quality.
let cookedDishIds = null;
let premiumDishIds = null;
const ensureDishSets = () => {
  if (cookedDishIds) return;
  const dishes = global.cooking || [];
  const cooked = {};
  dishes.forEach((dish) => (cooked[String(dish.item)] = true));
  // Top 10% of the cooking list by base value
  const values = dishes.map((dish) => dish.value).sort((a, b) => a - b);
  const cut = values.length ? values[Math.floor(values.length * 0.9)] : Infinity;
  const premium = {};
  dishes.forEach((dish) => {
    if (dish.value >= cut) premium[String(dish.item)] = true;
  });
  cookedDishIds = cooked;
  premiumDishIds = premium;
};

// Quality multiplier. Dishes use a steeper table; the "doubled" stage bonus still wins when higher.
global.getQualityMultiplier = (quality, doubled, itemId) => {
  ensureDishSets();
  const id = itemId ? String(itemId) : "";
  const isDish = !!id && cookedDishIds[id] === true;
  quality = Number(quality);
  let mult = 1;
  if (quality == 1) mult = isDish ? 1.3 : doubled ? 1.5 : 1.25;
  if (quality == 2) mult = isDish ? 1.75 : doubled ? 2 : 1.5;
  if (quality == 3) mult = isDish ? 3 : doubled ? 3 : 2;
  if (isDish && doubled) {
    if (quality == 1) mult = Math.max(mult, 1.5);
    if (quality == 2) mult = Math.max(mult, 2);
  }
  if (isDish && quality == 3 && premiumDishIds[id] === true) mult *= 1.2;
  return mult;
};

const calculateQualityValue = (number, quality, doubled, itemId) => {
  let value;
  if (quality) {
    value = Math.round(number * global.getQualityMultiplier(quality, doubled, itemId));
  } else {
    value = number;
  }
  return value;
};

// Seasonal crops: Serene Seasons tags (data/sereneseasons/tags/items/<season>_crops.json).
// Every season tag includes #year_round_crops, so an item with all four tags is year-round and gets no bonus.
const SEASON_TAGS = ["spring", "summer", "autumn", "winter"];
global.getSeasonalMultiplier = (item, season) => {
  if (!season || !item) return 1;
  // getSeasonFromLevel already returns lowercase names; normalize anyway and map "fall" to "autumn"
  season = String(season).toLowerCase();
  if (season === "fall") season = "autumn";
  // A duplicate is worth its canonical item, so it also counts the canonical seasons
  const canonical = global.canonicalItems ? global.canonicalItems[String(item.id)] : undefined;
  const canonicalItem = canonical && Item.exists(canonical) ? Item.of(canonical) : undefined;
  // society:<season>_bonus_crops gives the bonus without touching growth (see handleSeasonTags.js)
  const hasSeason = (stack, tagSeason) =>
    stack.hasTag(`sereneseasons:${tagSeason}_crops`) || stack.hasTag(`society:${tagSeason}_bonus_crops`);
  const inSeason = (tagSeason) => hasSeason(item, tagSeason) || (canonicalItem && hasSeason(canonicalItem, tagSeason));
  const matches = SEASON_TAGS.filter(inSeason).length;
  return matches > 0 && matches < SEASON_TAGS.length && inSeason(season) ? 1.08 : 1;
};
// Quality/age tiers that other mods store in item NBT scale the sale value.
// Kaleidoscope Tavern: "BrewLevel" 1..6 (Undrinkable, Inferior, Common, Fine, Crafted, Vintage)
// Vinery / NetherVinery: "Year" wine age in years (ages in the wine rack)
// Kaleidoscope Cookery: "kaleidoscope_cookery:quality" 0..3 (Poor, Standard, Excellent, Superb)
// Brewery: "beerQuality" int tier (beer quality shown on the tooltip)
// Cuisine Delight: "CookedFoodData" compound with a "score" 0..100 (plate quality)
global.getVariationMultiplier = (nbt, stack) => {
  if (!nbt) return 1;
  try {
    // Kaleidoscope Tavern brew levels: undrinkable is nearly worthless, vintage pays triple
    if (nbt.contains("BrewLevel")) {
      const brewTiers = [0.15, 0.4, 1, 1.5, 2, 3];
      const level = nbt.getInt("BrewLevel");
      if (level >= 1) return brewTiers[Math.min(level, 6) - 1];
    }
    // Vinery / NetherVinery: each year aged adds ~6.7%, capped at double value (15+ years)
    if (nbt.contains("Year")) {
      const year = nbt.getInt("Year");
      return Math.min(2, 1 + Math.max(0, year) * 0.0667);
    }
    // Kaleidoscope Cookery dish quality
    if (nbt.contains("kaleidoscope_cookery:quality")) {
      const cookeryTiers = [0.6, 1, 1.4, 1.8];
      const q = nbt.getInt("kaleidoscope_cookery:quality");
      return cookeryTiers[Math.max(0, Math.min(3, q))];
    }
    // Cuisine Delight plate score 0..100
    if (nbt.contains("CookedFoodData")) {
      const foodData = nbt.getCompound("CookedFoodData");
      if (foodData && foodData.contains("score")) {
        const score = Math.max(0, Math.min(100, foodData.getFloat("score")));
        return 0.5 + score / 100;
      }
    }
    // Brewery beer quality (tier 3 is the baseline)
    if (nbt.contains("beerQuality") && !(stack && global.getQualityLevel(stack))) {
      const q = Math.max(0, Math.min(5, nbt.getInt("beerQuality")));
      return Math.min(2, 0.4 + 0.2 * q);
    }
  } catch (e) {
    return 1;
  }
  return 1;
};

// Returns array of coins from price, prioritizing high value coins
const calculateCoinsFromValue = (price, output, coinMap) => {
  for (let i = 0; i < coinMap.length; i++) {
    let { coin, value } = coinMap[i];
    if (value <= price) {
      if (price % value === 0) {
        output.push({ coin: coin, count: price / value });
        return output;
      } else {
        output.push({ coin: coin, count: Math.floor(price / value) });
        calculateCoinsFromValue(price % value, output, coinMap);
      }
      return output;
    }
  }
};

const textComponentToLegacy = (data) => {
  const colorMap = {
    black: "§0", dark_blue: "§1", dark_green: "§2", dark_aqua: "§3",
    dark_red: "§4", dark_purple: "§5", gold: "§6", gray: "§7",
    dark_gray: "§8", blue: "§9", green: "§a", aqua: "§b",
    red: "§c", light_purple: "§d", yellow: "§e", white: "§f"
  };
  let prefix = "";
  if (data.color) prefix += colorMap[data.color.toLowerCase()] ?? "§f";
  if (data.bold) prefix += "§l";
  if (data.italic) prefix += "§o";
  if (data.underlined) prefix += "§n";
  if (data.strikethrough) prefix += "§m";
  if (data.obfuscated) prefix += "§k";
  const text = data.text ?? "";
  return prefix + text;
};


global.getShippingBinName = (nbt, legacy) => {
  if (nbt && nbt.contains('customName')) {
    let json = nbt.getString('customName');
    let data = JSON.parse(json);
    if (legacy) {
      return textComponentToLegacy(data);
    }
    else {
      return Text.of(data);
    }
  }
  return null;
};


// Base value of an attribute on a live entity (modifiers excluded), NaN when the entity lacks it.
global.getAttributeBaseValue = (entity, attributeId) => {
  if (!entity) return NaN;
  const BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  const ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  const holder = BuiltInRegistries.ATTRIBUTE.getHolder(ResourceLocation.parse(attributeId));
  if (!holder.isPresent()) return NaN;
  const attributes = entity.getAttributes();
  if (!attributes.hasAttribute(holder.get())) return NaN;
  return Number(attributes.getBaseValue(holder.get()));
};

// Sell multiplier of an entity for an attribute id. Same result as the old NBT helper: the base value, 1 when absent or 0.
global.getAttributeMultiplier = (entity, attributeId) => {
  return global.getAttributeBaseValue(entity, attributeId) || 1;
};

// Same lookup on the snapshot list cached in the shipping bin ({ Name, Base } entries).
global.getCachedAttributeMultiplier = (attributes, multiplier) => {
  return (
    Number(
      attributes.filter((obj) => {
        return obj.Name === multiplier;
      })[0]?.Base
    ) || 1
  );
};

// Item custom data (CompoundTag) readers. Each returns undefined when the key is missing.
global.getCustomString = (tag, key) => (tag && tag.contains(key) ? tag.getString(key) : undefined);
global.getCustomNumber = (tag, key) => (tag && tag.contains(key) ? tag.getDouble(key) : undefined);
global.getCustomSub = (tag, key, field) =>
  tag && tag.contains(key) && tag.getCompound(key).contains(field)
    ? tag.getCompound(key).getString(field)
    : undefined;

// Sunlit "artificial" mark: NBT SunlitArtificial:1b. Marked stacks sell for 70% of the stack total.
global.isSunlitArtificial = (nbt) => {
  if (!nbt) return false;
  return nbt.contains("SunlitArtificial") && nbt.getByte("SunlitArtificial") === 1;
};

// Stack total: the penalty applies to the total (count included), not per item.
global.createStackSaleValue = (itemValue, count, attributeMultiplier, nbt) => {
  const total = itemValue * count * attributeMultiplier;
  return global.isSunlitArtificial(nbt) ? Math.round(total * 0.7) : Math.round(total);
};

// industrial_miner stage: +25% per item on the Create metals (global.createMetalItems).
global.createMetalStageValue = (itemValue, itemId, stages) => {
  if (
    stages.toString().includes("industrial_miner") &&
    (global.createMetalItems || []).includes(String(itemId))
  ) {
    return Math.round(itemValue * 1.25);
  }
  return itemValue;
};

global.processShippingBinInventory = (
  inventory,
  inventorySlots,
  attributes,
  stages,
  returnRemoved,
  simulated
) => {
  let calculatedValue = 0;
  let itemValue = 0;
  let removedItems = [];
  // Coins from Create metals in this bin, read by processValueOutput for the mining XP
  global.lastCreateMetalSaleValue = 0;
  // Season of the last bin that was cached (see cacheShippingBin); undefined means no seasonal bonus
  const binSeason = global.shippingBinLevel ? global.getSeasonFromLevel(global.shippingBinLevel) : undefined;
  let slotItem;
  let isSellable;
  let isLongwing
  for (let i = 0; i < inventorySlots; i++) {
    slotItem = inventory.getStackInSlot(i).item;
    isLongwing = ["longwings:moth", "longwings:butterfly"].includes(slotItem.id);
    isSellable = global.trades.has(String(slotItem.id)) || isLongwing;
    if (isSellable) {
      let trade = global.trades.get(String(slotItem.id));
      let quality = undefined;
      let doubleQuality = false;
      let slotStack = inventory.getStackInSlot(i);
      let slotNbt = slotStack.customData;
      let variant = global.getCustomString(slotNbt, "variant");
      if (slotNbt && isLongwing && variant) {
        trade = global.trades.get(`longwings:variant/${variant}`);
      }
      quality = global.getQualityLevel(slotStack) || undefined;
      // UPDATE CACHING METHOD WHEN ADDING STAGES
      if (
        quality &&
        quality > 0 &&
        stages.toString().includes("the_quality_of_the_earth") &&
        trade.multiplier.equals("shippingbin:crop_sell_multiplier") &&
        !Item.of(slotItem).hasTag("minecraft:fishes")
      ) {
        doubleQuality = true;
      }
      itemValue = calculateQualityValue(trade.value, quality, doubleQuality, slotItem.id);
      itemValue = Math.round(itemValue * global.getVariationMultiplier(slotNbt, slotStack));
      itemValue = Math.round(itemValue * global.getSeasonalMultiplier(Item.of(slotItem), binSeason));
      if (
        stages.toString().includes("bluegill_meridian") &&
        slotItem.id == "aquaculture:bluegill"
      ) {
        itemValue = calculateQualityValue(666, quality);
      }
      if (
        stages.toString().includes("phenomenology_of_treasure") &&
        (Item.of(slotItem).hasTag("society:artifacts") ||
          Item.of(slotItem).hasTag("society:relics"))
      ) {
        itemValue *= 3;
      }
      if (
        stages.toString().includes("brine_and_punishment") &&
        Item.of(slotItem).hasTag("society:brine_and_punishment")
      ) {
        itemValue *= 2;
      }
      itemValue = global.createMetalStageValue(itemValue, slotItem.id, stages);
      if (isLongwing) {
        let size = 1.0;
        if (slotNbt.contains("nbt")) {
          let storedSize = global.getCustomNumber(slotNbt, "size");
          if (storedSize) {
            size = storedSize;
          }
        }
        if (stages.toString().includes("the_metamorphosize")) {
          itemValue += (Math.round((size / 0.01) * 4) * 3);
        } else {
          itemValue += Math.round((size / 0.01) * 4)
        }
      }
      let additionalValue = global.createStackSaleValue(
        itemValue,
        inventory.getStackInSlot(i).count,
        global.getCachedAttributeMultiplier(attributes, trade.multiplier),
        slotNbt
      );
      if (isNaN(additionalValue)) {
        console.log("SHIPPING BIN VALUE IS NAN! DEBUG LOG:")
        console.log("itemValue: " + itemValue)
        console.log("attrbMult: " + global.getCachedAttributeMultiplier(attributes, trade.multiplier))
        console.log("Trade Value: " + trade.value)
        calculatedValue += itemValue * inventory.getStackInSlot(i).count
      } else {
        calculatedValue += additionalValue
        if ((global.createMetalItems || []).includes(String(slotItem.id))) {
          global.lastCreateMetalSaleValue += additionalValue;
        }
      }

    }
    if (isSellable && !simulated) {
      if (returnRemoved) removedItems.push(i);
      else inventory.setStackInSlot(i, "minecraft:air");
    }
  }
  return { calculatedValue: calculatedValue, removedItems: removedItems };
};

const debugValueProcess = false;

global.handleShippingBinDebt = (
  value,
  player,
  server,
  block,
  inventory,
  extenalOutput
) => {
  if (!player) return value;
  let playerUUID = player.getUuid().toString();
  let binDebt = 0;
  let debtPaid;
  let totalDebt;
  let receipt;
  let newValue = value;
  if (!playerUUID) return value;
  if (server.persistentData.debts) {
    binDebt = server.persistentData.debts.filter((debt) => {
      return global.nbtStr(debt.uuid) === playerUUID;
    });
  }
  if (binDebt.length > 0 && global.nbtNum(binDebt[0].amount) > 0) {
    totalDebt = global.nbtNum(binDebt[0].amount);
    if (value >= totalDebt) {
      newValue = value - totalDebt;
      debtPaid = totalDebt;
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          `{anchor:"TOP_LEFT",background:1,color:"#55FF55",size:1,offsetY:36,offsetX:6,typewriter:1,align:"TOP_LEFT"}`,
          160,
          Text.translatable(
            "society.shipping_bin.debt_paid_all",
            global.formatPrice(debtPaid.toFixed())
          ).toJson()
        )
      );
      global.setDebt(server, playerUUID, 0);
    } else {
      debtPaid = value;
      newValue = 0;
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          `{anchor:"TOP_LEFT",background:1,color:"#FFFFFF",size:1,offsetY:36,offsetX:6,typewriter:1,align:"TOP_LEFT"}`,
          160,
          Text.translatable(
            "society.shipping_bin.debt_paid",
            global.formatPrice(debtPaid.toFixed())
          ).toJson()
        )
      );
      global.setDebt(server, playerUUID, totalDebt - debtPaid);
    }
  }
  if (debtPaid > 0) {
    let receiptAuthor = global.translatableWithFallback("society.hospital_receipt.author", "Pipinha's Village Hospital").getString();
    let receiptText = Text.translatable(
      "society.shipping_bin.debt_paid_note",
      player.username,
      global.formatPrice(debtPaid.toFixed()),
      global.formatPrice(totalDebt.toFixed())
    ).toJson();
    let receiptTitle = global.translatableWithFallback("society.shipping_bin.debt_paid_note.title", "Debt Payment Receipt").getString();
    receipt = global.getNotePaperItem(receiptAuthor, receiptText, receiptTitle);
    if (extenalOutput) {
      block.popItemFromFace(receipt, block.properties.get("facing"));
    } else {
      for (let j = 0; j < inventory.slots; j++) {
        if (inventory.getStackInSlot(j) === Item.of("minecraft:air")) {
          inventory.insertItem(j, receipt, false);
          break;
        }
      }
    }
  }
  return newValue;
};

global.processValueOutput = (
  value,
  slots,
  removedSlots,
  player,
  server,
  block,
  inventory,
  extenalOutput,
  ownerUUID
) => {
  if (value > 0) {
    let hasRoom = false;
    value = Math.round(
      global.handleShippingBinDebt(
        value,
        player,
        server,
        block,
        inventory,
        extenalOutput
      )
    );
    let outputs = calculateCoinsFromValue(
      value,
      [],
      extenalOutput ? global.coinMap : basicCoinMap
    );

    // Create metals sold here grant mining XP: 1 XP per 5 coins of metal actually paid out (once per bin run)
    let createMetalCoins = Math.min(global.lastCreateMetalSaleValue || 0, value);
    global.lastCreateMetalSaleValue = 0;
    let createMetalXp = Math.floor(createMetalCoins / 5);
    if (createMetalXp > 0 && player) {
      global.giveExperience(server, player, "mining", createMetalXp);
    }

    if (!outputs) outputs = [];

    if (debugValueProcess) {
      console.log(`slots: ${slots}`);
      console.log(`countNonEmpty: ${inventory.countNonEmpty()}`);
      console.log(`RemovedSlots: ${removedSlots.length}`);
      console.log(`calculateSlotsNeeded: ${calculateSlotsNeeded(outputs)}`);
    }
    hasRoom =
      extenalOutput ||
      slots -
      inventory.countNonEmpty() +
      removedSlots.length -
      calculateSlotsNeeded(outputs) >=
      0;
    if (hasRoom) {
      // Mercantil tree XP for the bin owner (mercantilGlobals.js).
      if (player) global.grantMercantilXp(server, player, value);
      if (!block.level.hasNeighborSignal(block.pos) && player) {
        server.runCommandSilent(
          `playsound etcetera:item.handbell.ring block @a ${player.x} ${player.y} ${player.z} 0.3`
        );
        let customName = global.getShippingBinName(block.getEntityData().data, true);
        let finalName = customName ? ` ${customName} ` : "";
        server.runCommandSilent(
          global.getEmbersTextAPICommand(
            player.username,
            `{anchor:"TOP_LEFT",background:1,color:"#FFFFFF",size:1,offsetY:36,offsetX:6,typewriter:1,align:"TOP_LEFT"}`,
            160,
            Text.translatable(
              "society.shipping_bin.goods_sold",
              finalName,
              global.formatPrice(value.toFixed()),
            ).toJson()
          )
        );
      }
      if (extenalOutput) {
        let facing = block.properties.get("facing");
        let account = global.GLOBAL_BANK.getAccount(ownerUUID);
        let card = inventory.getStackInSlot(0);
        if (card && card.hasTag("numismatics:cards")) {
          account = global.GLOBAL_BANK.getAccount(
            card.customData.getUUID("AccountID")
          );
        }
        if (account && account.getBalance() + value < 2147483000) {
          account.deposit(value);
        } else {
          outputs.forEach((output) => {
            let { coin, count } = output;
            for (let index = 0; index <= count; index += 64) {
              let difference = count - index;
              block.popItemFromFace(
                `${difference > 64 ? 64 : difference}x ${coin}`,
                facing
              );
            }
          });
        }
      } else {
        /**
         * Basic Shipping Bins only remove items when they're sure there's enough room.
         * Smart Shipping Bins remove items upon calculation because they output externally.
         */
        for (let i = 0; i < removedSlots.length; i++) {
          inventory.setStackInSlot(removedSlots[i], "minecraft:air");
        }
        outputs.forEach((output) => {
          let { coin, count } = output;
          for (let index = 0; index <= count; index += 64) {
            let difference = count - index;
            for (let i = 0; i < slots; i++) {
              if (inventory.getStackInSlot(i).item.id === "minecraft:air") {
                inventory.setStackInSlot(
                  i,
                  Item.of(`${difference > 64 ? 64 : difference}x ${coin}`)
                );
                break;
              }
            }
          }
        });
      }
    }

    if (!hasRoom && player) {
      server.runCommandSilent(
        `playsound stardew_fishing:fish_escape block @a ${player.x} ${player.y} ${player.z} 0.3`
      );
      server.runCommandSilent(
        global.getEmbersTextAPICommand(
          player.username,
          `{anchor:"TOP_LEFT",background:1,color:"#FF5555",size:1,offsetY:36,offsetX:6,typewriter:1,align:"TOP_LEFT"}`,
          160,
          Text.translatable("society.shipping_bin.full").toJson()
        )
      );
    }
  }
};

global.cacheShippingBin = (entity) => {
  const { level, block } = entity;
  // Season source for processShippingBinInventory, which receives no level of its own
  global.shippingBinLevel = level;
  const attributeMapping = [
    "shippingbin:crop_sell_multiplier",
    "shippingbin:wood_sell_multiplier",
    "shippingbin:gem_sell_multiplier",
    "shippingbin:meat_sell_multiplier",
  ];
  const stagesToFind = [
    "bluegill_meridian",
    "phenomenology_of_treasure",
    "brine_and_punishment",
    "the_quality_of_the_earth",
    "the_metamorphosize",
    "industrial_miner"
  ];
  let binPlayer;
  level.getServer().players.forEach((p) => {
    if (p.getUuid().toString() === global.nbtStr(block.getEntityData().data.owner)) {
      let newAttributes = [];
      let stages = [];
      attributeMapping.forEach((attr) => {
        newAttributes.push({
          Base: global.getAttributeBaseValue(p, attr),
          Name: attr,
        });
      });
      stagesToFind.forEach((stage) => {
        if (p.stages.has(stage)) stages.push(stage);
      });
      let nbt = block.getEntityData();
      nbt.merge({ data: { attributes: newAttributes, stages: stages } });
      global.setBlockEntityData(block, nbt)
      binPlayer = p;
    }
  });
  return binPlayer;
};
