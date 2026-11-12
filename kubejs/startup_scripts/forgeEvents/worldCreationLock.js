console.info("[SOCIETY] worldCreationLock.js loaded");

// New worlds are always HARD, on the default world type, with the Lost Cities
// profile from defaultconfigs (sunlit_cozy). The create world screen is
// enforced every frame: the difficulty snaps back to HARD, the world type back
// to minecraft:normal, and the Lost Cities "Cities" profile button is disabled
// (picking a profile there would override sunlit_cozy for the new world).
// The difficulty lock itself is applied server side (worldCreationLock.js).
const CREATE_WORLD_SCREEN = "net.minecraft.client.gui.screens.worldselection.CreateWorldScreen";
const LOST_CITIES_BUTTON = "Cities";
let worldCreationLockFailed = false;

global.enforceWorldCreationDefaults = (screen) => {
  if (worldCreationLockFailed) return;
  try {
    if (!(screen instanceof Java.loadClass(CREATE_WORLD_SCREEN))) return;
    let Difficulty = Java.loadClass("net.minecraft.world.Difficulty");
    let ui = screen.getUiState();
    if (String(ui.getDifficulty()) !== "HARD") ui.setDifficulty(Difficulty.HARD);

    let presetId = (entry) => {
      let holder = entry ? entry.preset() : null;
      if (!holder) return "";
      let key = holder.unwrapKey();
      return key.isPresent() ? String(key.get().location()) : "";
    };
    if (presetId(ui.getWorldType()) !== "minecraft:normal") {
      let normal = ui.getNormalPresetList().stream().filter((entry) => presetId(entry) === "minecraft:normal").findFirst();
      if (normal.isPresent()) ui.setWorldType(normal.get());
    }

    screen.children().forEach((widget) => {
      if (widget.getMessage && String(widget.getMessage().getString()) === LOST_CITIES_BUTTON) {
        widget.active = false;
      }
    });
  } catch (err) {
    worldCreationLockFailed = true;
    console.error(`[worldCreationLock] create world screen enforcement failed: ${err}`);
  }
};

if (Platform.isClientEnvironment()) {
  NativeEvents.onEvent(Java.loadClass("net.neoforged.neoforge.client.event.ScreenEvent$Render$Pre"), (e) => {
    global.enforceWorldCreationDefaults(e.getScreen());
  });
}
