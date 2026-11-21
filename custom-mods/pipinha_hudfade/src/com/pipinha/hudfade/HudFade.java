package com.pipinha.hudfade;

import com.mojang.blaze3d.systems.RenderSystem;
import neoforge.com.krookedlilly.autohidehud.AutoHideHUD;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Makes every HUD layer that Auto Hide HUD hides really follow its fade.
 *
 * Auto Hide HUD fades a layer by calling setShaderColor(1, 1, 1, alpha) in its Pre handler (NORMAL)
 * and resets it in Post. Mod layers broke that in three ways: they call setShaderColor(..., 1) while
 * drawing (Legendary Survival Overhaul thirst, Colorful Hearts), they draw with blending disabled
 * (Create toolbox hotbar marks), or they cancel the layer so Post never resets the fade.
 * - Pre HIGHEST: a fade left over from a layer whose Post never fired is ended first.
 * - Pre LOW (after Auto Hide HUD): while the layer is faded, blending is turned on.
 * - RenderSystemMixin caps every setShaderColor alpha at the current fade and keeps blending on
 *   while a layer is faded. Outside hidden layers the fade is 1, so nothing changes.
 */
@Mod(value = "pipinha_hudfade", dist = Dist.CLIENT)
public class HudFade {

    public HudFade() {
        NeoForge.EVENT_BUS.addListener(EventPriority.HIGHEST, true, RenderGuiLayerEvent.Pre.class, HudFade::clearStaleFade);
        NeoForge.EVENT_BUS.addListener(EventPriority.LOW, false, RenderGuiLayerEvent.Pre.class, HudFade::enableBlendWhileFaded);
    }

    private static void clearStaleFade(RenderGuiLayerEvent.Pre event) {
        if (AutoHideHUD.getAlpha() < 1.0F) {
            AutoHideHUD.endLayer();
        }
    }

    private static void enableBlendWhileFaded(RenderGuiLayerEvent.Pre event) {
        if (AutoHideHUD.getAlpha() < 1.0F) {
            RenderSystem.enableBlend();
            RenderSystem.defaultBlendFunc();
        }
    }
}
