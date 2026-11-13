// priority: 10000
// KubeJS 7 only allows assigning properties of `global` from startup scripts.
// Server/client scripts keep mutable runtime state inside this container instead:
// write `global.runtime.someKey = value`, never `global.someKey = value`.
global.runtime = {};
global.portBeTicks = {};

// Meadow 1.21 renamed its cheese blocks to wheels (meadow:cheese_block -> meadow:cheese_wheel).
// Aged products keep the 1.20.1 ids (society:aged_cheese_block, ...) because prices, shops,
// recipes, quests and converted saves use them. Maps an input path to the aged id suffix.
global.agedName = (path) => {
  const p = String(path);
  if (p === "cheese_wheel") return "cheese_block";
  if (p.endsWith("_cheese_wheel") && p !== "tribull_cheese_wheel") return p.replace(/_cheese_wheel$/, "_cheese_block");
  return p;
};

// Item ids that are not registered in this 1.21.1 instance are dropped before they reach
// ItemEvents, so one missing id cannot abort a whole modification or tooltip handler.
// Tags ("#"), the "*" wildcard and non-string entries (ItemStacks, objects) are kept as they are.
global.existingItems = (ids) =>
  [].concat(ids).filter((id) => typeof id !== "string" || id === "*" || id.startsWith("#") || Item.exists(id));

// Wraps an ItemEvents modification or tooltip event so modify and add skip missing ids.
// Skips the call entirely when no id is left.
global.guardItemEvent = (event) => ({
  modify: (ids, fn) => {
    const list = global.existingItems(ids);
    if (list.length > 0) event.modify(Array.isArray(ids) ? list : list[0], fn);
  },
  add: (ids, value) => {
    const list = global.existingItems(ids);
    if (list.length === 0) return;
    // KubeJS 7: add() takes a text list; a builder callback belongs to modify().
    if (typeof value === "function") event.modify(Array.isArray(ids) ? list : list[0], value);
    else event.add(Array.isArray(ids) ? list : list[0], value);
  },
});
