console.info("[SOCIETY] bountyCompatItems.js loaded");

// Bounty papers (Bountiful) ask for one exact item id, so a request for 8 Society
// blueberries ignored the Hearth and Harvest ones. Every objective whose item has a
// sunlit:compat/<group> tag (kubejs/data/sunlit/tags/items/compat/, same groups as
// recipes/normalizeDuplicateItems.js) is turned into a Bountiful item_tag objective,
// keeping the original item's name and icon, so any item of the group counts.
// Runs on login and whenever a bounty paper lands in the inventory, which also
// covers papers that were already taken before this script existed.
const BOUNTY_COMPAT_KEY = "bountiful:bounty_data";

const getCompatTag = (itemId) => {
  if (!Item.exists(itemId)) return null;
  let tag = null;
  Item.of(itemId)
    .item.builtInRegistryHolder()
    .tags()
    .map((tagKey) => String(tagKey.location()))
    .toList()
    .forEach((loc) => {
      if (!tag && loc.startsWith("sunlit:compat/")) tag = loc;
    });
  return tag;
};

const convertBountyPaper = (stack) => {
  if (!stack || stack.id !== "bountiful:bounty" || !stack.nbt) return false;
  const raw = stack.nbt.getString(BOUNTY_COMPAT_KEY);
  if (!raw) return false;
  let data;
  try {
    data = JSON.parse(raw);
  } catch (err) {
    return false;
  }
  if (!data.objectives) return false;
  let changed = false;
  data.objectives.forEach((obj) => {
    if (obj.logicId !== "minecraft:item" || obj.nbt) return;
    const tag = getCompatTag(obj.content);
    if (!tag) return;
    const item = Item.of(obj.content).item;
    obj.logicId = "bountiful:item_tag";
    obj.name = obj.name || String(Text.translatable(item.getDescriptionId()).getString());
    obj.icon = obj.icon || obj.content;
    obj.content = tag;
    changed = true;
  });
  if (changed) stack.nbt.putString(BOUNTY_COMPAT_KEY, JSON.stringify(data));
  return changed;
};

const convertBountyInventory = (player) => {
  player.inventory.items.forEach((stack) => convertBountyPaper(stack));
};

PlayerEvents.loggedIn((e) => convertBountyInventory(e.player));

PlayerEvents.inventoryChanged((e) => {
  if (!e.item || e.item.id !== "bountiful:bounty") return;
  convertBountyInventory(e.player);
});
