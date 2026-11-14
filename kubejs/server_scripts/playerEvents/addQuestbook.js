console.info("[SOCIETY] addQuestbook.js loaded");

// Kit inicial Sunlit (2026-10-09, pedido do dono): o bau bonus do vanilla usa a
// loot table fixa de kubejs/data/minecraft/loot_tables/chests/spawn_bonus_chest.json
// (picareta + machado de ferro, mochila de cobre, 3 paes, cantil vazio:
// cantil novo e o item base sem NBT, `legendarysurvivaloverhaul:canteen`).
// Sem bau bonus na criacao do mapa, o kit entra no inventario junto dos guias.
const sunlitStartKit = (player) => {
  try {
    player.give("minecraft:iron_pickaxe");
    player.give("minecraft:iron_axe");
    player.give("sophisticatedbackpacks:copper_backpack");
    player.give(Item.of("minecraft:bread", 3));
    player.give("legendarysurvivaloverhaul:canteen");
  } catch (err) {
    console.log(`[SOCIETY] addQuestbook: kit inicial falhou (${err})`);
  }
};

// bau bonus nasce a poucos blocos do spawn; se tem bau por perto, o jogador
// pega o kit la. Varredura grossa (de 2 em 2) num cubo de ~20 blocos.
const sunlitHasBonusChest = (player) => {
  try {
    const level = player.level;
    const p = player.blockPosition();
    for (let dx = -20; dx <= 20; dx += 2) {
      for (let dz = -20; dz <= 20; dz += 2) {
        for (let dy = -6; dy <= 6; dy += 2) {
          let st = level.getBlockState(p.offset(dx, dy, dz));
          if (!st.isAir() && /chest$/.test(String(st.getBlock().getDescriptionId()))) return true;
        }
      }
    }
  } catch (err) {}
  return false;
};

// Trava dupla contra livro repetido (2026-10-16): além do stage, confere o
// inventário. Se o jogador já tem o ftbquests:book em mãos, não ganha outro.
const sunlitHasQuestBook = (player) => {
  let found = false;
  try {
    player.inventory.items.forEach((item) => {
      if (!found && item.id === "ftbquests:book") found = true;
    });
  } catch (err) {}
  return found;
};

PlayerEvents.loggedIn((e) => {
  const { player } = e;
  if (player.stages.has("starting_items_4_0")) {
    player.tell(Text.translatable("society.login_update.title").gray());
    player.tell(Text.translatable("society.login_update.desc_0").white());
    player.tell(Text.translatable("society.login_update.desc_1").white());
    player.give("furniture:blueprints");
    player.stages.add("starting_items_4_1");
    player.stages.remove("starting_items_4_0");
  }
  if (!player.stages.has("starting_items_4_1")) {
    player.stages.add("starting_items_4_1");
    if (!sunlitHasQuestBook(player)) player.give("ftbquests:book");
    if (!sunlitHasBonusChest(player)) sunlitStartKit(player);
    if (global.multiplayerSharestones) {
      player.give("waystones:white_sharestone");
      player.give(
        Item.of(
          global.getNotePaperItem(
            global.translatableWithFallback("society.starting_item_sharestone.author", "Society").getString(),
            Text.translatable("society.starting_item_sharestone.text").toJson(),
            global.translatableWithFallback("society.starting_item_sharestone.title", "Server Welcome").getString(),
          )
        )
      );
    }
  }
});
