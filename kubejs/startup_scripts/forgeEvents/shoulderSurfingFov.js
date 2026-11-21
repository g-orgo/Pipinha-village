console.info("[SOCIETY] shoulderSurfingFov.js loaded");

// Third person (Shoulder Surfing) camera FOV, as in the 1.20.1 pack: base FOV 60 instead of
// the player's FOV option, with sprint and other FOV effects still applied on top.
//
// Shoulder Surfing 5.3.1 for 1.21.1 ships a broken override: its @ModifyVariable in
// GameRenderer.getFov expects a float local, but on 1.21.1 the FOV local is a double, so it
// rewrites partialTick to the override value instead. Result: the base FOV never changes
// (stays at the option, 90) and Mth.lerp(60, oldFov, fov) blows every FOV transition up 60x,
// which shows as a flash at the start and end of sprinting. So `fov_override_enabled` is
// false in shouldersurfing-client.toml and this listener applies `fov_override` instead.
//
// Client only: ViewportEvent.ComputeFov does not exist on a dedicated server.
// Startup scripts may register twice; each event object is handled once.

const SS_FOV_FALLBACK = 60.0;

global.ssFovLastEvent = null;
global.ssFovErrorLogged = false;

let $ssFovConfig = null;
let $ssFovApi = null;
let $ssFovMinecraft = null;
let $ssFovEvent = null;
try {
  $ssFovEvent = Java.loadClass("net.neoforged.neoforge.client.event.ViewportEvent$ComputeFov");
  $ssFovMinecraft = Java.loadClass("net.minecraft.client.Minecraft");
  $ssFovApi = Java.loadClass("com.github.exopandora.shouldersurfing.api.client.ShoulderSurfing");
  $ssFovConfig = Java.loadClass("com.github.exopandora.shouldersurfing.config.Config");
} catch (err) {
  // Dedicated server or Shoulder Surfing missing: nothing to do.
  $ssFovEvent = null;
}

const ssFovTarget = () => {
  let value = SS_FOV_FALLBACK;
  try {
    value = Number($ssFovConfig.CLIENT.getCameraConfig().getFovOverride());
  } catch (err) {
    value = SS_FOV_FALLBACK;
  }
  if (!(value >= 30 && value <= 110)) value = SS_FOV_FALLBACK;
  return value;
};

const ssFovOnCompute = (e) => {
  let base = 0;
  try {
    // Rhino 2101 hides hashCode(); === on two wrapped Java objects compares identity.
    if (e === global.ssFovLastEvent) return;
    global.ssFovLastEvent = e;
    // Hand and item rendering also call getFov, without the FOV option; leave those alone.
    if (!e.usedConfiguredFov()) return;
    if (!$ssFovApi.getInstance().isShoulderSurfing()) return;
    base = Number($ssFovMinecraft.getInstance().options.fov().get());
    if (!(base > 0)) return;
    e.setFOV(e.getFOV() * ssFovTarget() / base);
  } catch (err) {
    if (global.ssFovErrorLogged) return;
    global.ssFovErrorLogged = true;
    console.error(`[ssfov] ComputeFov failed: ${err}`);
  }
};

if ($ssFovEvent !== null) {
  NativeEvents.onEvent($ssFovEvent, (e) => ssFovOnCompute(e));
  console.info("[ssfov] third person FOV override active");
}
