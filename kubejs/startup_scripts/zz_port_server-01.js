// 1.21.1 port: helpers used by server scripts of the blockEvents batch.
// Item NBT is now data components: the plushie data goes to minecraft:custom_data
// and the quality goes to quality_food:quality through the 000_port_quality.js helpers.

// Creates a plushie stack. `snbt` is the SNBT compound stored in minecraft:custom_data.
global.makePlushieItem = (id, quality, snbt) => {
  const stack = Item.of(`${id}[minecraft:custom_data=${snbt}]`);
  global.setQualityLevel(stack, Number(quality) || 0);
  return stack;
};

// Creates the plushie stack that carries an animal, keeping the base quality.
global.withPlushieAnimal = (id, baseItem, animal, name) => {
  const stack = Item.of(id);
  stack.setCustomData(
    global.getPlushieItemNbt(baseItem.customData, animal.type, name, animal, animal)
  );
  global.setQualityLevel(stack, global.getQualityLevel(baseItem));
  return stack;
};
