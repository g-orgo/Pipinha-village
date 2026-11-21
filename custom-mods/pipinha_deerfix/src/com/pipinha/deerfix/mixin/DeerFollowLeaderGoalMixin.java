package com.pipinha.deerfix.mixin;

import com.pipinha.deerfix.DeerTame;
import net.satisfy.wildernature.core.entity.ai.goal.animal.DeerGoals;
import net.satisfy.wildernature.core.entity.animal.neutral.DeerEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A tamed deer does not chase its herd leader while that leader is running away in a panic. */
@Mixin(DeerGoals.DeerFollowLeaderGoal.class)
public abstract class DeerFollowLeaderGoalMixin {
    @Shadow
    @Final
    private DeerEntity deer;

    @Inject(method = {"canUse", "canContinueToUse"}, at = @At("HEAD"), cancellable = true)
    private void pipinha$tameStaysWhenLeaderFlees(CallbackInfoReturnable<Boolean> cir) {
        DeerEntity leader = this.deer.getLeader();
        if (leader != null && leader != this.deer && leader.isDeerRunning() && DeerTame.isTame(this.deer)) {
            cir.setReturnValue(false);
        }
    }
}
