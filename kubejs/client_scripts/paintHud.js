// Client renderer for global.paintUi (startup_scripts/zz_port_globalServer.js).
// Replaces the KubeJS 6 Painter: elements arrive over the "pipinha.paint"
// channel, are merged by id, and are drawn on every GUI frame.

const $PaintMinecraft = Java.loadClass("net.minecraft.client.Minecraft");
const $PaintComponentSerializer = Java.loadClass("net.minecraft.network.chat.Component$Serializer");
const $PaintResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
const $PaintBuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
const $PaintItemStack = Java.loadClass("net.minecraft.world.item.ItemStack");

const paintElements = {};
const paintItemStacks = {};
let paintLevelHash = 0;

const paintClear = () => {
  Object.keys(paintElements).forEach((id) => delete paintElements[id]);
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

// Plain strings are drawn as they are; strings that look like Text JSON are
// parsed into a component with the current registry access.
const paintText = (text, mc) => {
  if (text === undefined || text === null) return null;
  const str = String(text);
  const trimmed = str.trim();
  if (trimmed.charAt(0) === "{" || trimmed.charAt(0) === "[") {
    try {
      if (mc.level) {
        const component = $PaintComponentSerializer.fromJson(trimmed, mc.level.registryAccess());
        if (component) return component;
      }
    } catch (err) {
      return str;
    }
  }
  return str;
};

const paintItemStack = (id) => {
  if (!id) return null;
  const key = String(id);
  if (paintItemStacks[key] === undefined) {
    const item = $PaintBuiltInRegistries.ITEM.get($PaintResourceLocation.parse(key));
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

  if (type === "text") {
    const text = paintText(el.text, mc);
    if (text === null) return;
    w = font.width(text);
    h = 9;
    draw = () => g.drawString(font, text, 0, 0, paintColor(el.color, 0xFFFFFF), el.shadow === true);
  } else if (type === "item") {
    const stack = paintItemStack(el.item);
    if (stack === null) return;
    w = 16;
    h = 16;
    draw = () => g.renderItem(stack, 0, 0);
  } else if (type === "rectangle") {
    w = typeof el.w === "number" ? el.w : 0;
    h = typeof el.h === "number" ? el.h : 0;
    if (el.texture) {
      const texture = $PaintResourceLocation.parse(String(el.texture));
      draw = () => g.blit(texture, 0, 0, w, h, 0, 0, w, h, w, h);
    } else {
      const color = paintColor(el.color, -1);
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
  draw();
  pose.popPose();
};

const paintRender = (e) => {
  const mc = $PaintMinecraft.getInstance();
  // java.lang.System is blocked by the KubeJS class filter; ClientLevel keeps
  // Object.hashCode, which is the identity hash.
  const levelHash = mc.level ? mc.level.hashCode() : 0;
  if (levelHash !== paintLevelHash) {
    paintClear();
    paintLevelHash = levelHash;
  }
  if (!mc.level || mc.player === null) return;

  const list = Object.keys(paintElements).map((id) => paintElements[id]);
  if (list.length === 0) return;

  const g = e.getGuiGraphics();
  const screenW = g.guiWidth();
  const screenH = g.guiHeight();
  list
    .filter((el) => el.visible !== false)
    .sort((a, b) => (a.z || 0) - (b.z || 0))
    .forEach((el) => paintDrawElement(g, mc.font, mc, el, screenW, screenH));
};

NetworkEvents.dataReceived("pipinha.paint", (event) => {
  let data = null;
  try {
    data = JSON.parse(String(event.getData().getString("json")));
  } catch (err) {
    return;
  }
  if (!data) return;
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
