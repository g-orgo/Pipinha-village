console.info("[SOCIETY] anyaGuideFix.js loaded");
// Fauna & Orchestra: a Anya (personagem misteriosa do inicio) deve entregar o
// manual Symphonia e desaparecer depois do dialogo. Quando o dialogo falha ela
// fica parada para sempre e o jogador pode ficar sem o livro: esta rede de
// seguranca garante o livro e dispensa a NPC depois da conversa.
const ANYA_TYPE = "faunaandorchestra:anya_ghost";
// 1.21.1: the book is a data component (PatchouliDataComponents.BOOK, a ResourceLocation).
const anyaPlayerHasBook = (player) => {
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
    console.log(`[SOCIETY] anyaGuideFix: inventario indisponivel (${err})`);
  }
  return found;
};

const anyaDismiss = (server, player) => {
  try {
    server.runCommandSilent(
      `execute as ${player.username} at @s run kill @e[type=${ANYA_TYPE},distance=..12,limit=1,sort=nearest]`
    );
  } catch (err) {
    console.log(`[SOCIETY] anyaGuideFix: falha ao dispensar Anya (${err})`);
  }
};

ItemEvents.entityInteracted((e) => {
  const { player, target } = e;
  if (!target || !target.type || !target.type.includes("anya")) return;
  const server = e.server;
  if (!server) return;
  // 15s para ler o dialogo; depois garante o livro e dispensa a NPC
  try {
    server.scheduleInTicks(300, () => {
      try {
        if (!anyaPlayerHasBook(player)) {
          player.give(Item.of('patchouli:guide_book[patchouli:book="faunaandorchestra:symphonia"]'));
          player.tell("Anya deixou o manual Symphonia com voce.");
        }
        anyaDismiss(server, player);
      } catch (err) {
        console.log(`[SOCIETY] anyaGuideFix: callback falhou (${err})`);
      }
    });
  } catch (err) {
    console.log(`[SOCIETY] anyaGuideFix: agendamento falhou (${err})`);
  }
});
