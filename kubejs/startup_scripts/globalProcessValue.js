// priority: -40
// Quanto de valor cada item ganhou por passar por um subprocesso (2026-10-29, pedido do dono).
// Roda depois do globalPriceBalance.js (-30), então usa os preços já rebalanceados.
// Fonte: as receitas das máquinas da Society (global.*Recipes, priority 100).
// Para cada saída: custo do ingrediente x quantidade de saída vs valor da saída;
// guarda a diferença por item e o % sobre o custo do ingrediente.
// Usado pelo tooltip de preço (kubejs/client_scripts/tooltips/addPriceTooltips.js).
//
// ATENÇÃO: `global.processValue` é um objeto simples (id -> { coins, pct }) de
// propósito. Map/Set guardados em `global` mudam de tipo quando outro script lê,
// e objeto simples com acesso por colchete funciona nos dois casos.

// The Seed Maker stays out on purpose: it adds no value (globalPriceBalance.js, step 3c).
const MACHINE_RECIPES = [
  global.mayonnaiseMachineRecipes,
  global.cheesePressRecipes,
  global.wineKegRecipes,
  global.preservesJarRecipes,
  global.dehydratorRecipes,
  global.oilMakerRecipes,
  global.loomRecipes,
  global.picklingRecipes,
  global.fishSmokerRecipes,
  global.espressoMachineRecipes,
  global.tapperRecipes,
  global.mushroomLogRecipes,
  global.baitMakerRecipes,
  global.deluxeWormFarmRecipes,
  global.recyclingMachineRecipes,
  // extractinator é lista de { input, output } (loot table), não Map: serve para
  // exercitar o caminho de lista aqui também (as saídas não são itens, então
  // nenhuma delas acaba registrada).
  global.extractinatorRecipes,
];

const tradeValue = (id) => {
  if (!id || !global.trades.has(id)) return 0;
  const trade = global.trades.get(id);
  if (!trade) return 0;
  const value = Number(trade.value);
  return isNaN(value) ? 0 : value;
};

const parseOutput = (output) => {
  const text = String(output);
  const match = text.match(/^(\d+)\s*x\s*(.+)$/);
  if (match) return { count: Number(match[1]), id: match[2].trim() };
  return { count: 1, id: text.trim() };
};

// Aceita Map do JS, Map do Java e lista de { input, output }.
// Sem `const`/`let` dentro de bloco (Rhino do KubeJS quebra com "redeclaration of var").
// Array PRIMEIRO: lista também tem .keys(), então testar .keys antes de Array.isArray
// fazia o código chamar .get() numa lista e estourar "Cannot find function get".
const recipeEntries = (source) => {
  const out = [];
  if (!source) return out;
  if (Array.isArray(source)) {
    source.forEach((recipe) => {
      if (recipe && typeof recipe === "object" && recipe.input) {
        out.push([String(recipe.input), recipe]);
      }
    });
    return out;
  }
  if (typeof source.get === "function" && typeof source.keys === "function") {
    Array.from(source.keys()).forEach((key) => out.push([String(key), source.get(key)]));
    return out;
  }
  if (typeof source.get === "function" && typeof source.keySet === "function") {
    Array.from(source.keySet()).forEach((key) => out.push([String(key), source.get(key)]));
  }
  return out;
};

// A saída pode estar em `output` (lista de strings) ou `pickle` (string).
const recipeOutput = (recipe) => {
  if (!recipe) return null;
  if (recipe.output && recipe.output.length > 0) return recipe.output[0];
  if (typeof recipe.pickle === "string") return recipe.pickle;
  return null;
};

const info = {};

const register = (outputId, coins, pct, inputId, inputCost) => {
  if (coins <= 0 || pct <= 0) return;
  const current = info[outputId];
  // Receitas alternativas: fica com o ingrediente mais caro (bônus mais conservador)
  if (current && current.inputCost >= inputCost) return;
  info[outputId] = { coins: coins, pct: pct, input: inputId, inputCost: inputCost };
};

MACHINE_RECIPES.forEach((map) => {
  recipeEntries(map).forEach((entry) => {
    const inputId = entry[0];
    const recipe = entry[1];
    const raw = recipeOutput(recipe);
    if (!raw) return;
    const out = parseOutput(raw);
    const inputCost = tradeValue(inputId);
    const outputValue = tradeValue(out.id);
    if (inputCost <= 0 || outputValue <= 0) return;
    const perItemCost = inputCost / Math.max(1, out.count);
    const coins = Math.round(outputValue - perItemCost);
    const pct = Math.round((coins / perItemCost) * 100);
    register(out.id, coins, pct, inputId, perItemCost);
  });
});

// `global.processValue` guarda "moedas|porcentagem" em texto de propósito: string
// atravessa qualquer conversão que o `global` do KubeJS faça entre scripts
// (Map -> lista, objeto -> JSON), diferente de objeto aninhado.
const exportTable = {};
Object.keys(info).forEach((id) => {
  exportTable[id] = info[id].coins + "|" + info[id].pct;
});
global.processValue = exportTable;

console.info(`[SOCIETY] globalProcessValue.js: ${Object.keys(info).length} itens com bônus de subprocesso`);
