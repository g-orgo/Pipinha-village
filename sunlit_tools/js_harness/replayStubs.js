// Stubs minimos do KubeJS + uma tela inicial falsa para testar
// kubejs/startup_scripts/replayViewerButton.js fora do jogo.
// Usado por sunlit_tools/js_harness/ReplayButtonHarness.java.

// O Rhino do KubeJS nao tem o print do shell; guardamos a saida para o Java imprimir.
var OUT = [];
function print(m) { OUT.push(String(m)); }

var LANG = {
  'replaymod.gui.replayviewer': 'Replay Viewer',
  'menu.multiplayer': 'Multiplayer',
  'fml.menu.mods': 'Mods',
  'options.accessibility': 'Accessibility Options',
};

var MC = { screen: null };

var Java = {
  loadClass: function (name) {
    if (name === 'net.minecraft.client.Minecraft') {
      return { getInstance: function () { return MC; } };
    }
    throw new Error('classe inesperada no teste: ' + name);
  },
};

var Component = {
  translatable: function (key) {
    return { getString: function () { return LANG[key] === undefined ? key : LANG[key]; } };
  },
};

// ForgeEvents so existe nos scripts de startup; o script registra o render da tela.
var RENDER = null;
var RENDER_EVENT_NAME = null;

var ForgeEvents = {
  onEvent: function (name, fn) {
    RENDER_EVENT_NAME = name;
    RENDER = fn;
  },
};

// A tela vem do proprio evento (ScreenEvent$Render$Pre).
function RENDER_FRAME() {
  if (RENDER == null) {
    throw new Error('handler de render nao registrado');
  }
  RENDER({ getScreen: function () { return MC.screen; } });
}

var LOG = [];

var console = {
  info: function (m) { LOG.push('INFO ' + m); },
  warn: function (m) { LOG.push('WARN ' + m); },
  error: function (m) { LOG.push('ERROR ' + m); },
};

// Widget com posicao customizada do FancyMenu: getX()/getY() devolvem customX/customY
// quando eles estao definidos, exatamente como o mixin MixinAbstractWidget faz.
var FANCY_CUSTOM = {};

// Widget falso: guarda posicao e registra cada setPosition.
function widget(className, label, x, y, width, height) {
  var pos = { x: x, y: y };
  var moves = [];
  var custom = { x: null, y: null };
  var self = {
    pos: pos,
    moves: moves,
    custom: custom,
    getClass: function () { return { getName: function () { return className; } }; },
    getMessage: function () {
      if (label === null) {
        return null;
      }
      return { getString: function () { return label; } };
    },
    getX: function () { return custom.x === null ? pos.x : custom.x; },
    getY: function () { return custom.y === null ? pos.y : custom.y; },
    getWidth: function () { return width; },
    getHeight: function () { return height; },
    setPosition: function (nx, ny) {
      pos.x = nx;
      pos.y = ny;
      moves.push(nx + ',' + ny);
    },
    getCustomXFancyMenu: function () { return custom.x; },
    getCustomYFancyMenu: function () { return custom.y; },
    setCustomXFancyMenu: function (v) { custom.x = v; },
    setCustomYFancyMenu: function (v) { custom.y = v; },
  };
  return self;
}

function screenOf(className, widgets) {
  return {
    getClass: function () { return { getName: function () { return className; } }; },
    children: function () {
      return {
        size: function () { return widgets.length; },
        get: function (i) { return widgets[i]; },
      };
    },
  };
}

var TITLE = 'net.minecraft.client.gui.screens.TitleScreen';
