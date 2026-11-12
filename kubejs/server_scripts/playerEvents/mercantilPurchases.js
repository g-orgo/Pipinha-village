console.info("[SOCIETY] mercantilPurchases.js loaded");

// Mercantil XP for purchases at NPC shops (society_trading).
// The mod fires no event for a trade, and shift-click purchases leave no stat
// behind, so a purchase is read from the bought item showing up in the
// player's inventory (plus cursor) while a shop menu is open: the gain of the
// selected trade's result, in whole result stacks, times its spur cost
// (numismatics_cost). The XP and its daily cap live in
// global.grantMercantilPurchaseXp (startup_scripts/professions/mercantilGlobals.js).
// Barter trades (no spur cost), coin results (exchanges) and the Auto Trader
// give nothing. Items picked up from the ground are discounted, so tossing an
// item and picking it back up does not count as buying it.
const MERCANTIL_SHOP_MENUS = [
  "io.github.chakyl.societytrading.screen.ShopMenu",
  "io.github.chakyl.societytrading.screen.ImageShopMenu",
  "io.github.chakyl.societytrading.screen.ThinShopMenu",
];
const MERCANTIL_COIN_RESULT = /^numismatics:(spur|bevel|sprocket|cog|crown|sun|[a-z_]+_coin)$/;

const mercantilShopSnapshots = {};
const mercantilShopPickups = {};

const mercantilIsShopMenu = (menu) =>
  !!menu && MERCANTIL_SHOP_MENUS.some((name) => menu instanceof Java.type(name));

const mercantilCountHeld = (player, menu, stack) => {
  let count = player.getInventory().countItem(stack.getItem());
  let carried = menu.getCarried();
  if (!carried.isEmpty() && String(carried.getId()) === String(stack.getId())) {
    count += carried.getCount();
  }
  return count;
};

const mercantilShopSnapshot = (player, menu) => {
  let offer = menu.getSelectedTrade();
  if (!offer) return null;
  let result = offer.getResult();
  if (result.isEmpty()) return null;
  let itemId = String(result.getId());
  return {
    containerId: menu.containerId,
    itemId: itemId,
    stack: result,
    perTrade: Math.max(1, result.getCount()),
    cost: MERCANTIL_COIN_RESULT.test(itemId) ? 0 : Math.max(0, Number(offer.getNumismaticsCost())),
    held: mercantilCountHeld(player, menu, result),
  };
};

ItemEvents.pickedUp((e) => {
  let player = e.player;
  if (!player || player.isFake()) return;
  let uuid = String(player.getUuid());
  let picked = mercantilShopPickups[uuid] || (mercantilShopPickups[uuid] = {});
  let id = String(e.item.getId());
  picked[id] = (picked[id] || 0) + e.item.getCount();
});

PlayerEvents.tick((e) => {
  let { player, server } = e;
  if (player.level.isClientSide() || player.isFake()) return;
  let uuid = String(player.getUuid());
  let picked = mercantilShopPickups[uuid] || {};
  delete mercantilShopPickups[uuid];
  let menu = player.containerMenu;
  if (!mercantilIsShopMenu(menu)) {
    delete mercantilShopSnapshots[uuid];
    return;
  }

  try {
    let last = mercantilShopSnapshots[uuid];
    if (last && last.containerId === menu.containerId && last.cost > 0) {
      let gained = mercantilCountHeld(player, menu, last.stack) - last.held - (picked[last.itemId] || 0);
      let trades = Math.floor(gained / last.perTrade);
      if (trades > 0) global.grantMercantilPurchaseXp(server, player, trades * last.cost);
    }
    mercantilShopSnapshots[uuid] = mercantilShopSnapshot(player, menu);
  } catch (err) {
    delete mercantilShopSnapshots[uuid];
    console.error(`[mercantil] purchase hook failed: ${err}`);
  }
});

PlayerEvents.loggedOut((e) => {
  let uuid = String(e.player.getUuid());
  delete mercantilShopSnapshots[uuid];
  delete mercantilShopPickups[uuid];
});
