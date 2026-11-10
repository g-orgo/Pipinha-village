package com.sunlit.eating.mixin;

import net.minecraft.client.KeyMapping;
import net.minecraft.client.KeyboardHandler;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Options;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.toame.food.utils.AnimationUtils;

// The addon locks the hotbar while its eat animation plays and swallows the number keys. Pressing
// a number key for another slot now cancels the animation like a left click does. Priority 500
// makes this mixin apply before the addon, so its HEAD callback runs first (checked in the headless client).
@Mixin(value = KeyboardHandler.class, priority = 500)
public abstract class KeyboardHandlerSwitchMixin {
    private static final int GLFW_PRESS = 1;

    @Inject(method = "m_90893_", at = @At("HEAD"), remap = false)
    private void sunlit_eating$stopAnimationOnHotbarKey(long window, int key, int scancode, int action, int modifiers, CallbackInfo ci) {
        Minecraft minecraft = Minecraft.m_91087_();
        if (action != GLFW_PRESS || minecraft.f_91080_ != null || AnimationUtils.lockedHotbarSlot < 0
                || minecraft.f_91074_ == null) {
            return;
        }
        int selected = minecraft.f_91074_.m_150109_().f_35977_;
        Options options = minecraft.f_91066_;
        KeyMapping[] slots = options.f_92056_;
        for (int slot = 0; slot < slots.length; slot++) {
            if (slots[slot].m_90832_(key, scancode) && slot != selected) {
                AnimationUtils.stopAnimationControl();
                return;
            }
        }
    }
}
