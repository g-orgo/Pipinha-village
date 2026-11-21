package com.pipinha.hudfade.mixin;

import com.mojang.blaze3d.systems.RenderSystem;
import neoforge.com.krookedlilly.autohidehud.AutoHideHUD;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * While Auto Hide HUD fades a layer (getAlpha() below 1), no shader color may be more opaque than
 * the fade and blending may not be turned off, so mod layers that reset the color or disable blending
 * fade like the vanilla ones. Auto Hide HUD itself sets exactly the fade, which min() leaves as is.
 */
@Mixin(RenderSystem.class)
public abstract class RenderSystemMixin {

    @ModifyVariable(method = "setShaderColor", at = @At("HEAD"), argsOnly = true, ordinal = 3)
    private static float pipinha$capAlphaToFade(float alpha) {
        float fade = AutoHideHUD.getAlpha();
        return fade < 1.0F ? Math.min(alpha, fade) : alpha;
    }

    @Inject(method = "disableBlend", at = @At("HEAD"), cancellable = true)
    private static void pipinha$keepBlendWhileFaded(CallbackInfo ci) {
        if (AutoHideHUD.getAlpha() < 1.0F) {
            ci.cancel();
        }
    }
}
