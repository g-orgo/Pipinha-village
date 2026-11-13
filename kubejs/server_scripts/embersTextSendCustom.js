// Restores `/emberstextapi sendcustom <players> <data> <duration> <text>`, which the 1.20.1 pack got from
// the `society` mod (EmbersTextAPIMixin). EmbersTextAPI 3.x only ships `send` (markup text), while every
// pack message goes through global.getEmbersTextAPICommand with a style compound plus Component JSON.
// Brigadier merges this literal into the one EmbersTextAPI registers, so its own subcommands stay intact.
//
// Supported style keys (case-insensitive, same names as the old mixin):
// anchor, align, offsetX, offsetY, background, bgAlpha, bgColor, color, wrap, scale/size, shadow,
// fadeIn, fadeOut, typewriter (old chars per tick), shakeRandom/charShakeRandom (amplitude).

const $ImmersiveMessage = Java.loadClass("net.tysontheember.emberstextapi.immersivemessages.api.ImmersiveMessage");
const $TextAnchor = Java.loadClass("net.tysontheember.emberstextapi.immersivemessages.api.TextAnchor");
const $TextAlign = Java.loadClass("net.tysontheember.emberstextapi.immersivemessages.api.TextAlign");
const $EmbersTextAPI = Java.loadClass("net.tysontheember.emberstextapi.EmbersTextAPI");
const $ComponentSerializer = Java.loadClass("net.minecraft.network.chat.Component$Serializer");

// Old typewriter speed was characters per tick; 3.x `typewriter speed` is characters per second.
const ETA_TICKS_PER_SECOND = 20;

const etaWarned = {};
const etaWarnOnce = (key, msg) => {
  if (etaWarned[key]) return;
  etaWarned[key] = true;
  console.warn("[embersTextSendCustom] " + msg);
};

// "#RRGGBB" (extra digits ignored) -> int; anything else is passed as a color name
const etaApplyColor = (msg, value, setterInt, setterName) => {
  let raw = String(value).trim();
  if (raw.startsWith("#")) {
    let rgb = parseInt(raw.substring(1, 7), 16);
    if (!isNaN(rgb)) msg[setterInt](rgb);
    return;
  }
  msg[setterName](raw);
};

// TOP_LEFT / BOTTOM_CENTER style values from the old API map to the 3.x horizontal TextAlign
const etaAlign = (value) => {
  let raw = String(value).toUpperCase();
  if (raw.indexOf("LEFT") >= 0) return $TextAlign.LEFT;
  if (raw.indexOf("RIGHT") >= 0) return $TextAlign.RIGHT;
  return $TextAlign.CENTER;
};

const etaBuildMessage = (server, data, duration, text) => {
  let component = $ComponentSerializer.fromJson(text, server.registryAccess());
  let msg = new $ImmersiveMessage(component, Math.max(1, Math.round(duration)));
  let offsetX = 0;
  let offsetY = 0;
  let keys = data.getAllKeys().iterator();
  while (keys.hasNext()) {
    let key = String(keys.next());
    try {
      switch (key.toLowerCase()) {
        case "anchor":
          msg.anchor($TextAnchor.valueOf(String(data.getString(key)).toUpperCase()));
          break;
        case "align":
          msg.align(etaAlign(data.getString(key)));
          break;
        case "offsetx":
          offsetX = data.getFloat(key);
          break;
        case "offsety":
          offsetY = data.getFloat(key);
          break;
        case "background":
          msg.background(data.getBoolean(key));
          break;
        case "bgalpha":
          msg.bgAlpha(data.getFloat(key));
          break;
        case "bgcolor":
          etaApplyColor(msg, data.getString(key), "bgColor(int)", "bgColor(java.lang.String)");
          break;
        case "color":
          etaApplyColor(msg, data.getString(key), "color(int)", "color(java.lang.String)");
          break;
        case "wrap":
          msg["wrap(int)"](data.getInt(key));
          break;
        case "scale":
        case "size":
          msg.scale(data.getFloat(key));
          break;
        case "shadow":
          msg.shadow(data.getBoolean(key));
          break;
        case "fadein":
          msg.fadeInTicks(data.getInt(key));
          break;
        case "fadeout":
          msg.fadeOutTicks(data.getInt(key));
          break;
        case "typewriter":
          msg.effect("typewriter speed=" + data.getFloat(key) * ETA_TICKS_PER_SECOND);
          break;
        case "shakerandom":
        case "charshakerandom":
          msg.effect("shake amplitude=" + data.getFloat(key));
          break;
        default:
          etaWarnOnce(key, "style key not supported on 1.21.1: " + key);
      }
    } catch (err) {
      etaWarnOnce(key + ":err", "bad value for " + key + ": " + err);
    }
  }
  if (offsetX !== 0 || offsetY !== 0) msg.offset(offsetX, offsetY);
  return msg;
};

ServerEvents.commandRegistry((event) => {
  const { commands: Commands, arguments: Arguments } = event;
  event.register(
    Commands.literal("emberstextapi")
      .requires((source) => source.hasPermission(2))
      .then(
        Commands.literal("sendcustom").then(
          Commands.argument("player", Arguments.PLAYERS.create(event)).then(
            Commands.argument("data", Arguments.NBT_COMPOUND.create(event)).then(
              Commands.argument("duration", Arguments.FLOAT.create(event)).then(
                Commands.argument("text", Arguments.GREEDY_STRING.create(event)).executes((ctx) => {
                  let players = Arguments.PLAYERS.getResult(ctx, "player");
                  let data = Arguments.NBT_COMPOUND.getResult(ctx, "data");
                  let duration = Arguments.FLOAT.getResult(ctx, "duration");
                  let text = String(Arguments.GREEDY_STRING.getResult(ctx, "text"));
                  let server = ctx.source.server;
                  let sent = 0;
                  players.forEach((player) => {
                    // A fresh message per player: ImmersiveMessage keeps per-instance animation state
                    $EmbersTextAPI.sendMessage(player, etaBuildMessage(server, data, duration, text));
                    sent++;
                  });
                  return sent;
                })
              )
            )
          )
        )
      )
  );
});
