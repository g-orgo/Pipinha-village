// Ids that are not registered (mod not installed) make RecipeViewerEvents fail
// on the whole list, so they are filtered out before the call.
// "@modid" entries hide a whole mod; Item.exists cannot parse them, so they are
// kept only when that mod is loaded.
const existingItemIds = (ids) =>
  ids.filter((id) => (String(id).charAt(0) === "@" ? Platform.isLoaded(String(id).substring(1)) : Item.exists(id)));

RecipeViewerEvents.removeEntries('item', (e) => {
  e.remove(existingItemIds(global.removedItems));
  e.remove(existingItemIds(global.hiddenItems));
});
