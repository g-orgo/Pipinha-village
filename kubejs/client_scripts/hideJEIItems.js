// Ids that are not registered (mod not installed) make RecipeViewerEvents fail
// on the whole list, so they are filtered out before the call.
const existingItemIds = (ids) => ids.filter((id) => Item.exists(id));

RecipeViewerEvents.removeEntries('item', (e) => {
  e.remove(existingItemIds(global.removedItems));
  e.remove(existingItemIds(global.hiddenItems));
});
