package com.pipinha.hudfade.mixin;

import neoforge.com.krookedlilly.autohidehud.AutoHideHUD;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Colorful Hearts draws colored hearts through HeartDrawing.colorBlend (anonymous class HeartDrawing$1):
 * a base sprite pass, then a tinted pass with setShaderColor(r, g, b, a), then setShaderColor(1, 1, 1, 1)
 * and disableBlend. That reset wipes the fade Auto Hide HUD set for the health layer, so every heart
 * after the first colored one was drawn fully opaque. Both setShaderColor alphas are scaled by the
 * Auto Hide HUD alpha (1 when the HUD is visible), and blending stays on while the HUD is faded so the
 * next heart's base sprite keeps the fade too. RenderEventHandlerMixin restores the blend state afterwards.
 */
@Mixin(targets = "terrails.colorfulhearts.api.heart.drawing.HeartDrawing$1", remap = false)
public abstract class HeartDrawingMixin {

    @ModifyArg(
            method = "draw",
            at = @At(value = "INVOKE", target = "Lcom/mojang/blaze3d/systems/RenderSystem;setShaderColor(FFFF)V"),
            index = 3,
            require = 2,
            allow = 2)
    private float pipinha$fadeShaderAlpha(float alpha) {
        return alpha * AutoHideHUD.getAlpha();
    }

    @Redirect(
            method = "draw",
            at = @At(value = "INVOKE", target = "Lcom/mojang/blaze3d/systems/RenderSystem;disableBlend()V"),
            require = 1)
    private void pipinha$keepBlendWhileFaded() {
        if (AutoHideHUD.getAlpha() >= 1.0F) {
            com.mojang.blaze3d.systems.RenderSystem.disableBlend();
        }
    }
}
