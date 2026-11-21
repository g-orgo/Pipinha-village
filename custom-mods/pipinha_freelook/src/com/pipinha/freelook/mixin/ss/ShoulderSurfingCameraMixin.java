package com.pipinha.freelook.mixin.ss;

import com.github.exopandora.shouldersurfing.api.math.Vec2f;
import com.github.exopandora.shouldersurfing.client.ShoulderSurfing;
import com.pipinha.freelook.FreeLookState;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Optional mixin: while mounted and not free looking in Shoulder Surfing, drops its smooth
 * return of the free look offset and resets it at once. On foot nothing changes.
 */
@Mixin(targets = "com.github.exopandora.shouldersurfing.client.ShoulderSurfingCamera", remap = false)
public abstract class ShoulderSurfingCameraMixin {

    @Shadow
    private Vec2f rotationOffset;

    @Shadow
    private Vec2f rotationOffsetO;

    @Shadow
    @Final
    private ShoulderSurfing instance;

    @Inject(method = "renderTick(Lnet/minecraft/world/entity/Entity;F)V", at = @At("HEAD"), remap = false)
    private void pipinha$snapOffsetOnRender(Entity entity, float partialTick, CallbackInfo ci) {
        pipinha$snapIfMountedAndNotFreeLooking();
    }

    @Inject(method = "tick()V", at = @At("TAIL"), remap = false)
    private void pipinha$snapOffsetOnTick(CallbackInfo ci) {
        pipinha$snapIfMountedAndNotFreeLooking();
    }

    private void pipinha$snapIfMountedAndNotFreeLooking() {
        if (FreeLookState.isMounted() && !this.instance.isFreeLooking()) {
            this.rotationOffset = Vec2f.ZERO;
            this.rotationOffsetO = Vec2f.ZERO;
        }
    }
}
