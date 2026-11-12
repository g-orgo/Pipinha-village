// priority: -30
// Rebalance de preços (2026-10-29, pedido do dono).
// Roda depois de globalRegistry.js (-20) e dos addons de preço (-21..-23), então
// trabalha sobre os valores já registrados e mantém tooltip, caixa de envio e
// lojas iguais (todos leem global.trades).
//
// Regras:
// - Colheita fácil (multi-colheita / ciclo curto: berries, grãos, cana, cacau,
//   nether wart, uvas, folhas de chá/café, cogumelos): valor / 3.
// - Hortaliça de colheita única (raízes, folhosas, frutos grandes): valor / 1.5.
// - Colheita rara/lenta (frutas de árvore, ancient fruit, mana fruit, sparkpod,
//   mossberry, tubabacco, torchflower, flax...): valor não muda.
// - Caixas, sacos, fardos e blocos acompanham o fator do item base.
// - Sucos: uma etapa sobre a fruta, com o fator de etapa 1.35 (ver conventions.md).
//
// IMPORTANTE (Rhino do KubeJS): `const`/`let` soltos dentro de um bloco no topo do
// script quebram com "redeclaration of var". Por isso o corpo inteiro fica dentro
// de uma função, e a flag em `global` impede o corte de ser aplicado duas vezes.

const applyPriceBalance = () => {
  const EASY_CROPS = [
    // berries e frutinhas de arbusto
    "minecraft:sweet_berries",
    "minecraft:glow_berries",
    "society:blueberry",
    "society:boysenberry",
    "society:cranberry",
    "society:salmonberry",
    "society:crystalberry",
    "farm_and_charm:strawberry",
    "atmospheric:currant",
    "windswept:wild_berries",
    "windswept:holly_berries",
    "autumnity:foul_berries",
    "vintagedelight:gearo_berry",
    // grãos e afins
    "minecraft:wheat",
    "minecraft:sugar_cane",
    "minecraft:cocoa_beans",
    "minecraft:nether_wart",
    "farm_and_charm:barley",
    "farm_and_charm:oat",
    "farm_and_charm:corn",
    "farmersdelight:rice",
    "brewery:hops",
    // uvas
    "vinery:red_grape",
    "vinery:white_grape",
    "vinery:savanna_grapes_red",
    "vinery:savanna_grapes_white",
    "vinery:taiga_grapes_red",
    "vinery:taiga_grapes_white",
    "vinery:jungle_grapes_red",
    "vinery:jungle_grapes_white",
    "nethervinery:crimson_grape",
    "nethervinery:warped_grape",
    // folhas de chá/café e cogumelos
    "herbalbrews:yerba_mate_leaf",
    "herbalbrews:coffee_beans",
    "herbalbrews:rooibos_leaf",
    "herbalbrews:green_tea_leaf",
    "minecraft:brown_mushroom",
    "minecraft:red_mushroom",
    "quark:glow_shroom",
    // frutinhas pequenas
    "minecraft:apple",
    "vinery:cherry",
    // colheitas de mods externos, na mesma regra dos equivalentes acima
    "hearthandharvest:blueberries",
    "hearthandharvest:raspberry",
    "hearthandharvest:cherry",
    "kaleidoscope_tavern:grape",
    "kaleidoscope_tavern:green_grape",
    "kaleidoscope_tavern:gold_grape",
    "kaleidoscope_tavern:ice_grape",
    "youkaishomecoming:black_grape",
    "youkaishomecoming:white_grape",
    "youkaishomecoming:soybean",
    "youkaishomecoming:redbean",
    "youkaishomecoming:pods",
    "youkaishomecoming:green_coffee_bean",
    "kaleidoscope_cookery:rice_panicle",
    "kaleidoscope_cookery:fresh_tea_leaves",
    "farmersrespite:black_tea_leaves",
    "farmersrespite:green_tea_leaves",
    "farmersrespite:yellow_tea_leaves",
    "farmersrespite:coffee_berries",
  ];

  const NORMAL_CROPS = [
    "minecraft:carrot",
    "minecraft:potato",
    "minecraft:beetroot",
    "minecraft:melon",
    "minecraft:pumpkin",
    "minecraft:melon_slice",
    "farmersdelight:pumpkin_slice",
    "farm_and_charm:onion",
    "farm_and_charm:lettuce",
    "farmersdelight:tomato",
    "farmersdelight:cabbage",
    "veggiesdelight:garlic",
    "veggiesdelight:bellpepper",
    "veggiesdelight:turnip",
    "veggiesdelight:sweet_potato",
    "veggiesdelight:cauliflower",
    "veggiesdelight:broccoli",
    "veggiesdelight:zucchini",
    "vintagedelight:cucumber",
    "vintagedelight:ghost_pepper",
    "vintagedelight:peanut",
    "society:eggplant",
    "snowyspirit:ginger",
    "kaleidoscope_cookery:red_chili",
    "kaleidoscope_cookery:green_chili",
    "culturaldelights:white_eggplant",
    "minersdelight:cave_carrot",
  ];

  // Caixas/sacos/fardos que não seguem o nome do item base.
  const CONTAINER_ALIASES = {
    "minecraft:wheat": ["minecraft:hay_block"],
    "windswept:holly_berries": ["windswept:holly_berry_basket"],
    "windswept:wild_berries": ["windswept:wild_berry_basket"],
    "atmospheric:currant": ["atmospheric:currant_crate"],
    "society:blueberry": ["society:blueberry_crate"],
    "minecraft:sweet_berries": ["quark:berry_sack", "hearthandharvest:sweet_berry_crate"],
    "minecraft:glow_berries": ["quark:glowberry_sack", "hearthandharvest:glow_berry_crate"],
    "hearthandharvest:blueberries": ["hearthandharvest:blueberry_crate"],
    "kaleidoscope_tavern:grape": ["hearthandharvest:red_grape_crate"],
    "kaleidoscope_tavern:green_grape": ["hearthandharvest:green_grape_crate"],
    "youkaishomecoming:green_coffee_bean": ["youkaishomecoming:coffee_bean_bag"],
    "minersdelight:cave_carrot": ["minersdelight:cave_carrot_crate"],
  };

  const CONTAINER_SUFFIXES = [
    "_crate",
    "_bag",
    "_sack",
    "_basket",
    "_bundle",
    "_cask",
    "_block",
    "_ball",
    "_bale",
  ];

  const EASY_FACTOR = 1 / 3;
  const NORMAL_FACTOR = 1 / 1.5;
  const STEP_FACTOR = 1.35;

  const factorFor = (id) => {
    if (EASY_CROPS.includes(id)) return EASY_FACTOR;
    if (NORMAL_CROPS.includes(id)) return NORMAL_FACTOR;
    return 1;
  };

  const scalePrice = (value, factor) => Math.max(1, Math.round(value * factor));

  // Converte as listas de global (viram List/Map do Java) em objeto simples de
  // id -> valor, e devolve uma lista nova no fim (não mexe no Map do registro).
  const indexValues = (list) => {
    const out = {};
    list.forEach((entry) => {
      out[String(entry.item)] = Number(entry.value);
    });
    return out;
  };

  const rebuildList = (list, values) => {
    const out = [];
    list.forEach((entry) => {
      const id = String(entry.item);
      out.push({ item: id, value: values[id] !== undefined ? values[id] : Number(entry.value) });
    });
    return out;
  };

  const setTrade = (id, value) => {
    global.trades.set(id, {
      value: global.getConfiguredValue(value, "crop"),
      multiplier: "shippingbin:crop_sell_multiplier",
    });
  };

  const crops = indexValues(global.crops);
  // Frutas de mods externos só existem em global.fruits (o que está nas duas listas fica
  // com o valor de global.crops).
  const fruits = global.fruits ? indexValues(global.fruits) : {};
  Object.keys(fruits).forEach((id) => {
    if (crops[id] === undefined) crops[id] = fruits[id];
  });
  const newCrops = {};

  // 1) Colheitas fáceis e hortaliças normais.
  EASY_CROPS.concat(NORMAL_CROPS).forEach((id) => {
    if (crops[id] === undefined) return;
    newCrops[id] = scalePrice(crops[id], factorFor(id));
  });

  // 2) Caixas e blocos: mesmo fator do item base (casando pelo nome, mais os aliases).
  const containers = {};
  EASY_CROPS.concat(NORMAL_CROPS).forEach((id) => {
    if (crops[id] === undefined) return;
    const factor = factorFor(id);
    const name = id.split(":")[1];
    Object.keys(crops).forEach((entryId) => {
      const entryName = entryId.split(":")[1];
      const matchesName =
        entryName.startsWith(name) &&
        CONTAINER_SUFFIXES.some((suffix) => entryName.endsWith(suffix));
      if ((CONTAINER_ALIASES[id] || []).includes(entryId) || matchesName) {
        if (containers[entryId] === undefined) containers[entryId] = factor;
      }
    });
  });
  Object.keys(containers).forEach((id) => {
    if (crops[id] === undefined) return;
    newCrops[id] = scalePrice(crops[id], containers[id]);
  });

  // 2b) O item canônico (globalCanonicalItems.js) custa o mesmo que o duplicado que ele
  // substitui: é ele que circula, então não pode escapar do corte.
  if (global.canonicalItems) {
    Object.keys(global.canonicalItems).forEach((dup) => {
      if (newCrops[dup] === undefined) return;
      const canonical = String(global.canonicalItems[dup]);
      newCrops[canonical] = newCrops[dup];
    });
  }

  // 3) Sucos: uma etapa sobre a fruta, com o fator de etapa 1.35.
  const cocktails = indexValues(global.cocktails);
  const newCocktails = {};
  [
    ["society:ancient_juice", "society:ancient_fruit"],
    ["society:starfruit_juice", "pamhc2trees:starfruititem"],
    ["society:sparkpod_juice", "society:sparkpod"],
    ["society:mana_fruit_juice", "society:mana_fruit"],
  ].forEach((pair) => {
    const juice = pair[0];
    const fruit = pair[1];
    if (crops[fruit] === undefined || cocktails[juice] === undefined) return;
    newCocktails[juice] = Math.round(crops[fruit] * STEP_FACTOR);
  });

  // 3b) Sucos de mods externos: 2 frutas + 1 açúcar, uma etapa. Os vinhos deles partem daqui.
  const priceOf = (id) => (newCrops[id] !== undefined ? newCrops[id] : crops[id]);
  const sugar = priceOf("minecraft:sugar_cane");
  const newDrinks = {};
  [
    ["hearthandharvest:blueberry_juice", "hearthandharvest:blueberries"],
    ["hearthandharvest:raspberry_juice", "hearthandharvest:raspberry"],
    ["hearthandharvest:cherry_juice", "hearthandharvest:cherry"],
    ["hearthandharvest:red_grape_juice", "kaleidoscope_tavern:grape"],
    ["hearthandharvest:green_grape_juice", "kaleidoscope_tavern:green_grape"],
    ["kaleidoscope_tavern:grape_juice", "kaleidoscope_tavern:grape"],
  ].forEach((pair) => {
    const fruit = priceOf(pair[1]);
    if (fruit === undefined || sugar === undefined) return;
    newDrinks[pair[0]] = Math.round((fruit * 2 + sugar) * STEP_FACTOR);
  });

  // 3c) Seed Maker: selling the seeds of a run never beats selling its 3 crops. Quantity stays,
  // so planting keeps its yield; the seed price drops only where needed. The check follows the
  // shipping bin rounding (quality, then season) with the season bonus on the seed alone, the
  // worst case. Duplicates of a capped seed follow it. Unpriced outputs stay unpriced.
  // A function body, not an if block: Rhino rejects const inside blocks here.
  const capSeedMakerPrices = () => {
    const SEED_MAKER_INPUTS = 3;
    const SEED_SEASON_BONUS = 1.08;
    const QUALITY_MULTS = [1, 1.25, 1.5, 2, 3];
    const saleValue = (value, mult, season) => Math.round(Math.round(value * mult) * season);
    const seedPriceFits = (seed, count, crop) =>
      QUALITY_MULTS.every(
        (mult) =>
          count * saleValue(seed, mult, SEED_SEASON_BONUS) <=
          SEED_MAKER_INPUTS * saleValue(crop, mult, 1)
      );
    const seedCaps = {};
    Array.from(global.seedMakerRecipes.keys()).forEach((input) => {
      const output = String(global.seedMakerRecipes.get(input).output[0]).match(/^(\d+)x (.+)$/);
      const count = Number(output[1]);
      const seed = output[2];
      const crop = priceOf(String(input));
      let price = seedCaps[seed] !== undefined ? seedCaps[seed] : priceOf(seed);
      if (crop === undefined || price === undefined || count <= SEED_MAKER_INPUTS) return;
      while (price > 1 && !seedPriceFits(price, count, crop)) price--;
      seedCaps[seed] = price;
    });
    Object.keys(seedCaps).forEach((seed) => {
      if (seedCaps[seed] < priceOf(seed)) newCrops[seed] = seedCaps[seed];
    });
    Object.keys(global.canonicalItems || {}).forEach((dup) => {
      const seedCap = seedCaps[String(global.canonicalItems[dup])];
      if (seedCap !== undefined && priceOf(dup) > seedCap) newCrops[dup] = seedCap;
    });
  };
  if (global.seedMakerRecipes) capSeedMakerPrices();

  // 4) Aplica: lista nova (global.crops/global.cocktails) + valor de venda.
  let changed = 0;
  global.crops = rebuildList(global.crops, newCrops);
  if (global.fruits) global.fruits = rebuildList(global.fruits, newCrops);
  if (global.cooking) global.cooking = rebuildList(global.cooking, newDrinks);
  Object.keys(newDrinks).forEach((id) => {
    setTrade(id, newDrinks[id]);
    changed++;
  });
  // Os sucos da Tavern herdaram preço sem estar em lista nenhuma; sem lista não há tooltip.
  ["kaleidoscope_tavern:grape_juice", "hearthandharvest:green_grape_juice"].forEach((id) => {
    if (newDrinks[id] !== undefined && cocktails[id] === undefined) {
      global.cocktails.push({ item: id, value: newDrinks[id] });
    }
  });
  global.cocktails = rebuildList(global.cocktails, newCocktails);
  Object.keys(newCrops).forEach((id) => {
    setTrade(id, newCrops[id]);
    changed++;
  });
  Object.keys(newCocktails).forEach((id) => {
    setTrade(id, newCocktails[id]);
    changed++;
  });

  console.info(`[SOCIETY] globalPriceBalance.js: ${changed} preços rebalanceados`);
};

if (!global.priceBalanceApplied) {
  global.priceBalanceApplied = true;
  applyPriceBalance();
}
