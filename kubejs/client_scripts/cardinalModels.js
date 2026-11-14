// See global.cardinalParent in startup_scripts/000_port_runtime.js.
// The after_mods asset stage loads above KubeJS's internal generated assets, so these models win.
ClientEvents.generateAssets("after_mods", (event) => {
  const parents = global.cardinalParents || {};
  Object.keys(parents).forEach((id) => {
    event.blockModel(id, (model) => model.parent(parents[id]));
  });
});
