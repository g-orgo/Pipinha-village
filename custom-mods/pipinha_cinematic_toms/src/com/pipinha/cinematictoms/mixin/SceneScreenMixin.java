package com.pipinha.cinematictoms.mixin;

import dev.dyslexic.cinematic.client.SceneScreen;
import com.pipinha.cinematictoms.client.CraftingPanelSwap;
import com.pipinha.cinematictoms.client.emi.SceneEmi;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(value = SceneScreen.class, remap = false)
public abstract class SceneScreenMixin {
    // With EMI's own sidebar on the scene, Cinematic's field guide book stays closed and out of the way.
    @Inject(method = "guideShown()Z", at = @At("HEAD"), cancellable = true)
    private void hideFieldGuide(CallbackInfoReturnable<Boolean> cir) {
        if (SceneEmi.active()) {
            cir.setReturnValue(false);
        }
    }

    // Cinematic recomputes its panel position at the end of every layout pass; the crafting swap runs after it.
    @Inject(method = "layout()V", at = @At("TAIL"))
    private void swapCraftingPanels(CallbackInfo ci) {
        if (Minecraft.getInstance().screen instanceof SceneScreen screen) {
            CraftingPanelSwap.apply(screen);
        }
    }

    // Keeps the panel's hover and click area on the panel itself once the crafting swap moves it to the bottom.
    @Inject(method = "overPanel(DD)Z", at = @At("HEAD"), cancellable = true)
    private void craftingOverPanel(double mx, double my, CallbackInfoReturnable<Boolean> cir) {
        if (Minecraft.getInstance().screen instanceof SceneScreen screen && CraftingPanelSwap.active()) {
            cir.setReturnValue(CraftingPanelSwap.overPanel(screen, mx, my));
        }
    }
}
