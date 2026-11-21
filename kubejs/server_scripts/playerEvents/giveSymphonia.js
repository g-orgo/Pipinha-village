console.info("[SOCIETY] giveSymphonia.js loaded");
// Sunlit: o player ja comeca com o Symphonia no inventario e pode skippar a
// apresentacao da Anya (faunaandorchestra: character_spawn=false no config).
// O mod so entrega o livro no PRIMEIRO login; quem ja entrou antes (saves
// existentes como o New World) ficaria sem. Este handler garante o livro em
// todo login para quem nao tem, e dispensa qualquer Anya ghost por perto
// sem precisar falar com ela.
// 1.21.1: the book is a data component (PatchouliDataComponents.BOOK, a ResourceLocation).
const SYMPHONIA_BOOK = Item.of('patchouli:guide_book[patchouli:book="faunaandorchestra:symphonia"]');

const symphoniaHasBook = (player) => {
  let found = false;
  let $PatchouliBook;
  try {
    $PatchouliBook = Java.loadClass("vazkii.patchouli.common.item.PatchouliDataComponents").BOOK;
    player.inventory.items.forEach((item) => {
      if (found || item.id !== "patchouli:guide_book") return;
      const book = item.get($PatchouliBook);
      if (book && `${book}` === "faunaandorchestra:symphonia") found = true;
    });
  } catch (err) {
    console.log(`[SOCIETY] giveSymphonia: inventario indisponivel (${err})`);
  }
  return found;
};

PlayerEvents.loggedIn((e) => {
  const { player, server } = e;
  try {
    // Uma vez por jogador (2026-10-14, pedido do dono): antes o livro voltava
    // a TODO login sempre que não estava no inventário (guardado no baú,
    // na mochila ou jogado fora = livro novo a cada spawn). Agora o stage
    // garante entrega única; quem perdeu o livro fala com a Anya de novo
    // (anyaGuideFix.js entrega se estiver sem).
    if (!player.stages.has("sunlit_symphonia_book")) {
      if (!symphoniaHasBook(player)) player.give(SYMPHONIA_BOOK);
      player.stages.add("sunlit_symphonia_book");
    }
    if (server) {
      server.runCommandSilent(
        `execute as ${player.username} at @s run kill @e[type=faunaandorchestra:anya_ghost,distance=..32]`
      );
    }
  } catch (err) {
    console.log(`[SOCIETY] giveSymphonia: falhou (${err})`);
  }
});
