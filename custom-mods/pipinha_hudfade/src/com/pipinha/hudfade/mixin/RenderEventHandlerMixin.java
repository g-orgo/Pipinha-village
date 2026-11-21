package com.pipinha.hudfade.mixin;

import com.mojang.blaze3d.systems.RenderSystem;
import neoforge.com.krookedlilly.autohidehud.AutoHideHUD;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Colorful Hearts replaces the vanilla health layer from RenderGuiLayerEvent.Pre (LOWEST priority) and
 * cancels it. Auto Hide HUD already ran its Pre handler (NORMAL) and set the fade with setShaderColor,
 * but a cancelled Pre skips the Post event, so Auto Hide HUD never ends the layer.
 * HEAD: when the HUD is faded, enable default blending so the plain heart sprites honor the fade.
 * RETURN: when Colorful Hearts drew and cancelled the layer, restore the blend state and end the
 * Auto Hide HUD layer exactly as its Post handler would.
 */
@Mixin(targets = "terrails.colorfulhearts.neoforge.render.RenderEventHandler", remap = false)
public abstract class RenderEventHandlerMixin {

    @Unique
    private boolean pipinha$blendForced;

    @Inject(method = "renderHearts", at = @At("HEAD"))
    private void pipinha$beginFade(RenderGuiLayerEvent.Pre event, CallbackInfo ci) {
        pipinha$blendForced = false;
        if (!event.isCanceled() && AutoHideHUD.getAlpha() < 1.0F) {
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
            pipinha$blendForced = true;
        }
    }

    @Inject(method = "renderHearts", at = @At("RETURN"))
    private void pipinha$endFade(RenderGuiLayerEvent.Pre event, CallbackInfo ci) {
        if (pipinha$blendForced) {
            RenderSystem.disableBlend();
            pipinha$blendForced = false;
        }
        if (event.isCanceled()) {
            AutoHideHUD.endLayer();
        }
    }
}
