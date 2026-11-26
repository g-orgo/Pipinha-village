// TEMP diagnostic
// Logs food items (DataComponents.FOOD) that have no entry in global.trades. Remove after the price audit.
// Rhino 2101: no const/let inside functions or blocks; declare with let at the top of the function.
ServerEvents.loaded((event) => {
  let BuiltInRegistries;
  let DataComponents;
  let missing = [];
  let total = 0;
  try {
    BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
    DataComponents = Java.loadClass("net.minecraft.core.component.DataComponents");
    BuiltInRegistries.ITEM.forEach((item) => {
      let id;
      if (!item.getDefaultInstance().has(DataComponents.FOOD)) return;
      total++;
      id = String(BuiltInRegistries.ITEM.getKey(item));
      if (!global.trades.has(id)) missing.push(id);
    });
    console.info(`[pricecheck] food without trade: ${missing.length} of ${total}: ${missing.join(", ")}`);
  } catch (e) {
    console.info(`[pricecheck] failed: ${e}`);
  }
});
