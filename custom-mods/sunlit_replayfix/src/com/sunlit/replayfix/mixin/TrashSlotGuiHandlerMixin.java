package com.sunlit.replayfix.mixin;

import net.blay09.mods.balm.api.event.client.screen.ScreenInitEvent;
import net.blay09.mods.trashslot.client.TrashSlotGuiHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// Replay Mod's GUI library (jGui) initializes a hidden screen right after every real screen.
// TrashSlot treats it as "a non-container screen was opened" and clears the current screen's
// settings, so the trash slot is never drawn. TrashSlot already skips com.replaymod screens;
// this extends the same skip to the jGui package.
@Mixin(value = TrashSlotGuiHandler.class, remap = false)
public abstract class TrashSlotGuiHandlerMixin {
    @Inject(method = "onScreenInit", at = @At("HEAD"), cancellable = true, remap = false)
    private static void sunlit_replayfix$skipJGuiScreens(ScreenInitEvent.Post event, CallbackInfo ci) {
        if (event.getScreen() != null && event.getScreen().getClass().getName().startsWith("de.johni0702.minecraft.gui")) {
            ci.cancel();
        }
    }
}
