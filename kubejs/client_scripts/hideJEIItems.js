RecipeViewerEvents.removeEntries('item', (e) => {
  e.remove(global.removedItems);
  e.remove(global.hiddenItems);
});
