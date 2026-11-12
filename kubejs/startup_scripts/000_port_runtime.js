// priority: 10000
// KubeJS 7 only allows assigning properties of `global` from startup scripts.
// Server/client scripts keep mutable runtime state inside this container instead:
// write `global.runtime.someKey = value`, never `global.someKey = value`.
global.runtime = {};
global.portBeTicks = {};

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
    if (list.length > 0) event.add(Array.isArray(ids) ? list : list[0], value);
  },
});
