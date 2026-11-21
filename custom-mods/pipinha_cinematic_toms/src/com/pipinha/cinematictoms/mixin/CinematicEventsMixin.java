package com.pipinha.cinematictoms.mixin;

import com.pipinha.cinematictoms.client.emi.SceneLookupScreen;
import net.neoforged.neoforge.client.event.ScreenEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "dev.dyslexic.cinematic.client.CinematicClient$Events", remap = false)
public abstract class CinematicEventsMixin {
    // The stand-in window behind an EMI recipe page carries the station's own menu, which Cinematic
    // takes for the scene's window arriving and cancels; EMI then finds no window and drops the page.
    // The stand-in is a consultation of the scene, not the station's window, so Cinematic leaves it be.
    @Inject(method = "onScreenOpening", at = @At("HEAD"), cancellable = true)
    private static void keepLookupWindow(ScreenEvent.Opening event, CallbackInfo ci) {
        if (event.getNewScreen() instanceof SceneLookupScreen) {
            ci.cancel();
        }
    }
}
