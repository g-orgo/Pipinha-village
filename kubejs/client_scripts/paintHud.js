// Client renderer for global.paintUi (startup_scripts/zz_port_globalServer.js).
// Replaces the KubeJS 6 Painter: elements arrive over the "pipinha.paint"
// channel, are merged by id, and are drawn on every GUI frame.

const $PaintMinecraft = Java.loadClass("net.minecraft.client.Minecraft");
const $PaintComponent = Java.loadClass("net.minecraft.network.chat.Component");
const $PaintComponentSerializer = Java.loadClass("net.minecraft.network.chat.Component$Serializer");
const $PaintResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
const $PaintBuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
const $PaintItemStack = Java.loadClass("net.minecraft.world.item.ItemStack");

const paintElements = {};
const paintItemStacks = {};
let paintFailed = false;
let paintLoggedParseError = false;
// Debug logging for the animal HUD; switch to false once confirmed in game.
const PAINT_DEBUG = true;
let paintLoggedDraw = false;
let paintSelfTested = false;
// Debug output must never break the HUD: any error inside a debug message is logged and ignored.
const paintDebug = (message) => {
  try {
    console.info(`[paintHud] ${message()}`);
  } catch (err) {
    console.info(`[paintHud] debug message failed: ${err}`);
  }
};

const paintClear = () => {
  Object.keys(paintElements).forEach((id) => delete paintElements[id]);
  paintFailed = false; // a new session gets a fresh try after a render error
  paintLoggedDraw = false;
  Object.keys(paintTextCache).forEach((key) => delete paintTextCache[key]);
};

// Accepts "#RRGGBB" and "#AARRGGBB". Malformed values (e.g. "#FFFFFFF") use the
// last six hex digits as RGB and full alpha.
const paintColor = (value, fallback) => {
  if (typeof value !== "string") return fallback;
  const hex = value.replace(/[^0-9a-fA-F]/g, "");
  if (hex.length === 0) return fallback;
  const alpha = hex.length === 8 ? parseInt(hex.substring(0, 2), 16) : 255;
  const rgb = parseInt(hex.substring(Math.max(0, hex.length - 6)), 16);
  return ((alpha << 24) | rgb) | 0;
};

// Plain strings become literal components (legacy § codes still apply); strings that look
// like Text JSON become components. Results are cached per string, since this runs every frame.
// Every local is declared at the top of its function: Rhino 2101 fails on declarations
// inside nested blocks ("redeclaration of var").
const paintTextCache = {};
const paintLogParseError = (how, err) => {
  if (paintLoggedParseError) return;
  paintLoggedParseError = true;
  console.error(`[paintHud] text JSON not parsed by ${how}: ${err}`);
};
const paintText = (text, mc) => {
  let str = null;
  let trimmed = null;
  let component = null;
  if (text === undefined || text === null) return null;
  str = String(text);
  if (paintTextCache[str] !== undefined) return paintTextCache[str];
  trimmed = str.trim();
  if (trimmed.charAt(0) === "{" || trimmed.charAt(0) === "[") {
    // 1) KubeJS's own text wrapper: no Java overload choice involved.
    try {
      component = Text.of(JSON.parse(trimmed));
    } catch (err) {
      component = null;
      paintLogParseError("Text.of", err);
    }
    // 2) Vanilla serializer, with the overload picked by explicit signature.
    if (!component && mc.level) {
      try {
        component = $PaintComponentSerializer["fromJson(java.lang.String,net.minecraft.core.HolderLookup$Provider)"](
          trimmed, mc.level.registryAccess());
      } catch (err) {
        component = null;
        paintLogParseError("Component.Serializer.fromJson", err);
      }
    }
  }
  // Always hand a Component to Font/GuiGraphics: a JS string makes the overload
  // choice (String, Component, FormattedCharSequence) ambiguous in Rhino.
  if (!component) component = $PaintComponent.literal(str);
  paintTextCache[str] = component;
  return component;
};

const paintItemStack = (id) => {
  if (!id) return null;
  const key = String(id);
  let item = null;
  if (paintItemStacks[key] === undefined) {
    item = $PaintBuiltInRegistries.ITEM.get($PaintResourceLocation.parse(key));
    paintItemStacks[key] = new $PaintItemStack(item, 1);
  }
  return paintItemStacks[key];
};

const paintDrawElement = (g, font, mc, el, screenW, screenH) => {
  const scale = typeof el.scale === "number" ? el.scale : 1;
  const type = el.type || "text";
  const alignX = el.alignX || "left";
  const alignY = el.alignY || "top";
  let w = 0;
  let h = 0;
  let draw = null;
  let label = null;
  let stack = null;
  let texture = null;
  let color = 0;

  if (type === "text") {
    label = paintText(el.text, mc);
    if (label === null) return;
    // Overloads are picked by explicit signature: Rhino finds drawString(String, float...)
    // and drawString(Component, int...) equally good for a Component and JS numbers.
    w = font["width(net.minecraft.network.chat.FormattedText)"](label);
    h = 9;
    draw = () => g["drawString(net.minecraft.client.gui.Font,net.minecraft.network.chat.Component,int,int,int,boolean)"](
      font, label, 0, 0, paintColor(el.color, 0xFFFFFF), el.shadow === true);
  } else if (type === "item") {
    stack = paintItemStack(el.item);
    if (stack === null) return;
    w = 16;
    h = 16;
    draw = () => g.renderItem(stack, 0, 0);
  } else if (type === "rectangle") {
    w = typeof el.w === "number" ? el.w : 0;
    h = typeof el.h === "number" ? el.h : 0;
    if (el.texture) {
      texture = $PaintResourceLocation.parse(String(el.texture));
      draw = () => g.blit(texture, 0, 0, w, h, 0, 0, w, h, w, h);
    } else {
      color = paintColor(el.color, -1);
      draw = () => g.fill(0, 0, w, h, color);
    }
  } else {
    return;
  }

  const anchorX = alignX === "center" ? screenW / 2 : alignX === "right" ? screenW : 0;
  const anchorY = alignY === "center" ? screenH / 2 : alignY === "bottom" ? screenH : 0;
  const boxW = w * scale;
  const boxH = h * scale;
  const offsetX = alignX === "center" ? boxW / 2 : alignX === "right" ? boxW : 0;
  const offsetY = alignY === "center" ? boxH / 2 : alignY === "bottom" ? boxH : 0;
  const x = anchorX + (typeof el.x === "number" ? el.x : 0) - offsetX;
  const y = anchorY + (typeof el.y === "number" ? el.y : 0) - offsetY;

  const pose = g.pose();
  pose.pushPose();
  pose.translate(x, y, 0);
  pose.scale(scale, scale, 1);
  try {
    draw();
  } finally {
    pose.popPose();
  }
};

const paintRenderFrame = (e) => {
  const mc = $PaintMinecraft.getInstance();
  // Elements are cleared on LoggingIn/LoggingOut (below), so no per-level tracking here.
  if (!mc.level || mc.player === null) return;
  if (PAINT_DEBUG && !paintSelfTested) {
    paintSelfTested = true;
    paintDebug(() => `self-test: JSON text -> ${paintText('{"text":"Teste","bold":false}', mc)}`);
  }

  const list = Object.keys(paintElements).map((id) => paintElements[id]);
  if (list.length === 0) return;
  if (PAINT_DEBUG && !paintLoggedDraw && paintElements.animalName) {
    paintLoggedDraw = true;
    paintDebug(() => `drawing ${list.length} elements; name text -> ${paintText(paintElements.animalName.text, mc)}`);
  }

  const g = e.getGuiGraphics();
  const screenW = g.guiWidth();
  const screenH = g.guiHeight();
  list
    .filter((el) => el.visible !== false)
    .sort((a, b) => (a.z || 0) - (b.z || 0))
    .forEach((el) => paintDrawElement(g, mc.font, mc, el, screenW, screenH));
};

// Runs every frame inside the GUI render: an exception here would crash the client,
// so any error is logged once and the HUD stops drawing instead.
const paintRender = (e) => {
  if (paintFailed) return;
  try {
    paintRenderFrame(e);
  } catch (err) {
    paintFailed = true;
    console.error(`[paintHud] HUD disabled after render error: ${err}`);
  }
};

NetworkEvents.dataReceived("pipinha.paint", (event) => {
  let data = null;
  try {
    data = JSON.parse(String(event.getData().getString("json")));
  } catch (err) {
    console.error(`[paintHud] bad packet: ${err}`);
    return;
  }
  if (!data) return;
  if (PAINT_DEBUG && data.animalName && data.animalName.text) paintDebug(() => `received animal hud: ${Object.keys(data).join(",")}`);
  Object.keys(data).forEach((id) => {
    const spec = data[id];
    if (!spec) return;
    if (spec.remove === true) {
      delete paintElements[id];
      return;
    }
    paintElements[id] = Object.assign({}, paintElements[id] || {}, spec);
  });
});

NativeEvents.onEvent("net.neoforged.neoforge.client.event.RenderGuiEvent$Post", paintRender);
NativeEvents.onEvent("net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent$LoggingIn", paintClear);
NativeEvents.onEvent("net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent$LoggingOut", paintClear);
