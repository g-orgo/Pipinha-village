package com.pipinha.freelook.mixin;

import com.pipinha.freelook.FreeLookState;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Diverts the local player's mouse turn into the free look offsets while free looking. */
@Mixin(Entity.class)
public abstract class EntityTurnMixin {

    @Inject(method = "turn(DD)V", at = @At("HEAD"), cancellable = true)
    private void pipinha$freeLookTurn(double yRot, double xRot, CallbackInfo ci) {
        if ((Object) this != Minecraft.getInstance().player) {
            return;
        }
        if (!FreeLookState.refresh()) {
            return;
        }
        FreeLookState.turn(yRot, xRot);
        ci.cancel();
    }
}
