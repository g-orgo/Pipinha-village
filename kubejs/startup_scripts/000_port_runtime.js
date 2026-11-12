// priority: 10000
// KubeJS 7 only allows assigning properties of `global` from startup scripts.
// Server/client scripts keep mutable runtime state inside this container instead:
// write `global.runtime.someKey = value`, never `global.someKey = value`.
global.runtime = {};
global.portBeTicks = {};
