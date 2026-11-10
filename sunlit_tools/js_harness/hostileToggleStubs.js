// Minimal KubeJS / Minecraft stubs for hostileSpawnToggle.js (startup + server).
// Used by HostileToggleHarness.java through run_hostile_toggle.sh.
var OUT = [];
var RESULT = 0;
function check(name, ok) { if (!ok) RESULT++; OUT.push((ok ? 'OK   ' : 'FAIL ') + name); }
var console = { info: function (m) { OUT.push('     log: ' + m); }, error: function (m) { OUT.push('     ERR: ' + m); RESULT++; } };
function cls(name) { return { getName: function () { return name; } }; }
function enumv(n) { return { name: function () { return n; }, toString: function () { return n; } }; }

var global = {};
var HANDLERS = {};
var ForgeEvents = { onEvent: function (name, fn) { HANDLERS[name] = fn; } };
var SERVER_HANDLERS = {};
var ServerEvents = {
  loaded: function (fn) { SERVER_HANDLERS.loaded = fn; },
  tick: function (fn) { SERVER_HANDLERS.tick = fn; },
};
var Platform = { isClientEnvironment: function () { return true; } };

function makeTag() {
  var data = {};
  return {
    getBoolean: function (k) { return data[k] === true; },
    putBoolean: function (k, v) { data[k] = v; },
  };
}
var SERVER = {
  persistentData: makeTag(),
  queued: [],
  execute: function (fn) { this.queued.push(fn); },
  runQueue: function () { while (this.queued.length) this.queued.shift()(); },
  dayTime: 0,
  overworld: function () { return { dayTime: SERVER.dayTime }; },
};
var SELECTED_PACKS = ['vanilla', 'file/Excalibur_V1.20.zip'];
var MC = {
  level: {},
  server: SERVER,
  getSingleplayerServer: function () { return this.server; },
  getResourcePackRepository: function () {
    return { getSelectedIds: function () { return { forEach: function (f) { SELECTED_PACKS.forEach(f); } }; } };
  },
};

function widget(className, x, y, w, extra) {
  var o = {
    x: x, y: y, w: w, active: true, visible: true,
    getClass: function () { return cls(className); },
    getX: function () { return this.x; }, getY: function () { return this.y; },
    setX: function (v) { this.x = v; }, setPosition: function (a, b) { this.x = a; this.y = b; },
    getWidth: function () { return this.w; }, setWidth: function (v) { this.w = v; },
  };
  for (var k in extra) o[k] = extra[k];
  return o;
}
var IMAGE_BUTTONS = [];
function ImageButtonStub(x, y, w, h, u, v, yd, tex, tw, th, press, label) {
  var b = widget('net.minecraft.client.gui.components.ImageButton', x, y, w, {});
  b.u = u; b.tex = tex; b.label = label; b.press = function () { press(b); };
  b.setTooltip = function (t) { b.tooltip = t; };
  IMAGE_BUTTONS.push(b);
  return b;
}
function ResourceLocationStub(ns, path) { return { ns: ns, path: path }; }
var Java = {
  loadClass: function (name) {
    if (name === 'net.minecraft.client.Minecraft') return { getInstance: function () { return MC; } };
    if (name === 'net.minecraft.client.gui.components.Tooltip') return { create: function (c) { return { text: c }; } };
    if (name === 'net.minecraft.client.gui.components.ImageButton') return ImageButtonStub;
    if (name === 'net.minecraft.resources.ResourceLocation') return ResourceLocationStub;
    throw new Error('unexpected class: ' + name);
  },
};
var Component = { translatable: function (k) { return { key: k }; } };
