package com.pipinha.cinematictoms.mixin;

import dev.emi.emi.api.EmiApi;
import dev.emi.emi.screen.EmiScreenManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = EmiScreenManager.class, remap = false)
public abstract class EmiScreenManagerMixin {
    // EMI's quick craft (a plain left click on a craftable or a favorite with a recipe) fills straight
    // into the container window under the sidebar and dereferences it. A scene has none, which crashed
    // the game (2026-10-30). Without a window the click goes on to "show recipe" instead, and that
    // page's fill button works on the scene through its stand-in window.
    @Inject(method = "craftInteraction", at = @At("HEAD"), cancellable = true)
    private static void skipWithoutWindow(CallbackInfoReturnable<Boolean> cir) {
        if (EmiApi.getHandledScreen() == null) {
            cir.setReturnValue(false);
        }
    }
}
