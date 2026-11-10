console.info("[SOCIETY] goatMilkSwap.js loaded");

// A Goat Milk Bottle do Hearth and Harvest e comida SEM alwaysEat: com a fome
// cheia o DrinkableItem do FD recusa o gole e o botao direito nao faz nada.
// Troca ao obter pela Milk Bottle do FD (sempre bebivel, tambem remove 1
// efeito). As receitas que pediam a garrafa H&H (engradado, queijo de cabra)
// foram recriadas com a garrafa do FD em recipes/addBottleRecipes.js, entao
// nada da cadeia se perde.
PlayerEvents.inventoryChanged((e) => {
  if (!e.item || e.item.id !== "hearthandharvest:goat_milk_bottle") return;
  let n = 0;
  e.player.inventory.items.forEach((item) => {
    if (item.id === "hearthandharvest:goat_milk_bottle") {
      n += item.count;
      item.count = 0;
    }
  });
  if (n > 0) {
    e.player.give(Item.of("farmersdelight:milk_bottle", n));
    e.player.tell(Text.translatable("society.goat_milk.swapped").gray());
  }
});
