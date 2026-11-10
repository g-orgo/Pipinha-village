package com.sunlit.eating.mixin;

import net.minecraft.client.Minecraft;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.toame.food.events.GameplayEvents;
import org.toame.food.utils.AnimationUtils;

// Immersive Eating cancels the right click and starts its first person animation, which only
// runs while drawn and is stopped outside first person on the next tick. In third person or with
// Shoulder Surfing the food could not be eaten at all. Outside first person the click now keeps
// the normal item use. A lock already running still goes through the original handler.
@Mixin(value = GameplayEvents.class, remap = false)
public abstract class GameplayEventsMixin {
    @Inject(method = "onRightClickItem", at = @At("HEAD"), cancellable = true, remap = false)
    private static void sunlit_eating$keepNormalUseOutsideFirstPerson(PlayerInteractEvent.RightClickItem event, CallbackInfo ci) {
        Minecraft minecraft = Minecraft.m_91087_();
        if (!AnimationUtils.isAnimationLocked() && !minecraft.f_91066_.m_92176_().m_90612_()) {
            ci.cancel();
        }
    }
}
