package com.pipinha.deerfix.mixin;

import com.pipinha.deerfix.DeerTame;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.satisfy.wildernature.core.entity.animal.neutral.DeerEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Tamed deer: no awareness build-up near players, no waking up in a panic when a player
 * walks by, and no joining herd alarms (shared panic or hurt calls). Wild deer are unchanged.
 */
@Mixin(DeerEntity.class)
public abstract class DeerEntityMixin {
    @Shadow
    private float awareness;

    @Inject(method = "updateAwareness", at = @At("HEAD"), cancellable = true)
    private void pipinha$tameStaysCalm(CallbackInfo ci) {
        if (DeerTame.isTame((Entity) (Object) this)) {
            this.awareness = 0.0F;
            ci.cancel();
        }
    }

    @Inject(method = "hasWakeUpTriggerNearby", at = @At("HEAD"), cancellable = true)
    private void pipinha$tameKeepsSleeping(CallbackInfoReturnable<Boolean> cir) {
        if (DeerTame.isTame((Entity) (Object) this)) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "onHeardCall", at = @At("HEAD"), cancellable = true)
    private void pipinha$tameIgnoresCalls(DeerEntity source, Entity threat, CallbackInfo ci) {
        if (DeerTame.isTame((Entity) (Object) this)) {
            ci.cancel();
        }
    }

    @Redirect(
        method = "triggerPanic",
        at = @At(
            value = "INVOKE",
            target = "Lnet/minecraft/world/level/Level;getEntitiesOfClass(Ljava/lang/Class;Lnet/minecraft/world/phys/AABB;)Ljava/util/List;"
        )
    )
    private <T extends Entity> List<T> pipinha$skipTameInHerdPanic(Level level, Class<T> type, AABB area) {
        List<T> deer = new ArrayList<>(level.getEntitiesOfClass(type, area));
        deer.removeIf(DeerTame::isTame);
        return deer;
    }

    @Inject(
        method = "getBreedOffspring(Lnet/minecraft/server/level/ServerLevel;Lnet/minecraft/world/entity/AgeableMob;)Lnet/satisfy/wildernature/core/entity/animal/neutral/DeerEntity;",
        at = @At("RETURN")
    )
    private void pipinha$inheritTame(ServerLevel level, AgeableMob otherParent, CallbackInfoReturnable<DeerEntity> cir) {
        DeerEntity child = cir.getReturnValue();
        if (child != null && (DeerTame.isTame((Entity) (Object) this) || DeerTame.isTame(otherParent))) {
            DeerTame.markBredTame(child);
        }
    }
}
