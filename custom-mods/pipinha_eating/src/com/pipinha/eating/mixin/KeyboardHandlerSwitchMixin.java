package com.pipinha.eating.mixin;

import io.github.memorytoame.immersiveeating.neoforge.utils.AnimationUtils;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.KeyboardHandler;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Options;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// The addon locks the hotbar while its eat animation plays and swallows the number keys. Pressing
// a number key for another slot now cancels the animation like a left click does. Priority 500
// makes this mixin apply before the addon, so its HEAD callback runs first.
@Mixin(value = KeyboardHandler.class, priority = 500)
public abstract class KeyboardHandlerSwitchMixin {
    private static final int GLFW_PRESS = 1;

    @Inject(method = "keyPress", at = @At("HEAD"), remap = false)
    private void pipinha_eating$stopAnimationOnHotbarKey(long window, int key, int scancode, int action, int modifiers, CallbackInfo ci) {
        Minecraft minecraft = Minecraft.getInstance();
        if (action != GLFW_PRESS || minecraft.screen != null || AnimationUtils.lockedHotbarSlot < 0
                || minecraft.player == null) {
            return;
        }
        int selected = minecraft.player.getInventory().selected;
        Options options = minecraft.options;
        KeyMapping[] slots = options.keyHotbarSlots;
        for (int slot = 0; slot < slots.length; slot++) {
            if (slots[slot].matches(key, scancode) && slot != selected) {
                AnimationUtils.stopAnimationControl();
                return;
            }
        }
    }
}
