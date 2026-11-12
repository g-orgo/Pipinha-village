// Makes the title screen language and accessibility buttons follow the FancyMenu layout
// again on 1.21.1.
//
// FancyMenu 3.9.x identifies these two buttons by the translation key of their message,
// and it still looks for the 1.20.1 keys ("narrator.button.language" and
// "narrator.button.accessibility"). On 1.21.1 vanilla builds them with "options.language"
// and "options.accessibility", so FancyMenu cannot find them: they keep the gray vanilla
// look and their vanilla position, on top of the layout buttons. FancyMenu 3.10 fixes the
// keys, but it needs WaterMedia 3, and the pack is pinned to WaterMedia 2 (WaterFrames).
//
// This script swaps both buttons, right after the screen initializes (NeoForge
// ScreenEvent.Init.Post runs inside Screen.init, before FancyMenu applies the layout),
// for an equivalent icon button whose message uses the key FancyMenu expects. The new
// button draws no vanilla sprite, because the layout textures (btn_lang/btn_a11y) already
// contain the icon.
//
// Startup script because NeoForge events are only registered from startup scripts.
// Inside functions use `var`, never `const`/`let` (Rhino "redeclaration of var" issue).

var TITLE_SCREEN_CLASS = "net.minecraft.client.gui.screens.TitleScreen";
var SWAPS = [
  { vanillaKey: "options.language", fancyMenuKey: "narrator.button.language" },
  { vanillaKey: "options.accessibility", fancyMenuKey: "narrator.button.accessibility" },
];

var loggedError = false;

function swapTitleIconButtons(event) {
  var screen = event.getScreen();
  if (screen == null || String(screen).split("@")[0] != TITLE_SCREEN_CLASS) {
    return;
  }

  var $Component = Java.loadClass("net.minecraft.network.chat.Component");
  var $SpriteIconButton = Java.loadClass("net.minecraft.client.gui.components.SpriteIconButton");
  var $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");

  var listeners = event.getListenersList();
  var found = [];
  for (var i = 0; i < listeners.size(); i++) {
    var widget = listeners.get(i);
    var label = null;
    try {
      label = widget.getMessage().getString();
    } catch (error) {
      continue;
    }
    for (var s = 0; s < SWAPS.length; s++) {
      if (label == $Component.translatable(SWAPS[s].vanillaKey).getString()) {
        found.push({ widget: widget, swap: SWAPS[s] });
      }
    }
  }

  for (var f = 0; f < found.length; f++) {
    var original = found[f].widget;
    var replacement = buildReplacement(
      $Component,
      $SpriteIconButton,
      $ResourceLocation,
      original,
      found[f].swap.fancyMenuKey
    );
    event.removeListener(original);
    event.addListener(replacement);
  }
}

function buildReplacement($Component, $SpriteIconButton, $ResourceLocation, original, key) {
  var button = $SpriteIconButton
    .builder($Component.translatable(key), function (pressed) {
      original.onPress();
    }, true)
    .size(original.getWidth(), original.getHeight())
    // Zero-size sprite: the layout texture already draws the icon.
    .sprite($ResourceLocation.withDefaultNamespace("icon/language"), 0, 0)
    .build();
  button.setPosition(original.getX(), original.getY());
  return button;
}

try {
  NativeEvents.onEvent(
    Java.loadClass("net.neoforged.neoforge.client.event.ScreenEvent$Init$Post"),
    function (event) {
      try {
        swapTitleIconButtons(event);
      } catch (error) {
        if (!loggedError) {
          loggedError = true;
          console.error("[Pipinha] Failed to swap the title screen icon buttons: " + error);
        }
      }
    }
  );
} catch (error) {
  // Dedicated server: there are no client screens.
  console.warn("[Pipinha] Title screen icon buttons not registered: " + error);
}
