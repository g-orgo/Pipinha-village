package com.pipinha.hudfade.mixin;

import neoforge.com.krookedlilly.autohidehud.AutoHideHUD;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Colorful Hearts draws the hearts inside RenderGuiLayerEvent.Pre (LOWEST) and cancels the vanilla
 * health layer, so Auto Hide HUD's Post never ends the fade. It is ended here right away, so the
 * layers drawn next are not faded by mistake.
 */
@Mixin(targets = "terrails.colorfulhearts.neoforge.render.RenderEventHandler", remap = false)
public abstract class RenderEventHandlerMixin {

    @Inject(method = "renderHearts", at = @At("RETURN"))
    private void pipinha$endFade(RenderGuiLayerEvent.Pre event, CallbackInfo ci) {
        if (event.isCanceled()) {
            AutoHideHUD.endLayer();
        }
    }
}
