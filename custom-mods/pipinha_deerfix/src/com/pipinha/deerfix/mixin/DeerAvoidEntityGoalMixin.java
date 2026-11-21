package com.pipinha.deerfix.mixin;

import com.pipinha.deerfix.DeerTame;
import net.minecraft.world.entity.player.Player;
import net.satisfy.wildernature.core.entity.ai.goal.animal.DeerGoals;
import net.satisfy.wildernature.core.entity.animal.neutral.DeerEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The "flee from players" goal never starts for a tamed deer. Pillager/villager goals are untouched. */
@Mixin(DeerGoals.DeerAvoidEntityGoal.class)
public abstract class DeerAvoidEntityGoalMixin {
    @Shadow
    @Final
    private DeerEntity deer;

    @Inject(method = "canUse", at = @At("HEAD"), cancellable = true)
    private void pipinha$tameIgnoresPlayers(CallbackInfoReturnable<Boolean> cir) {
        Class<?> avoided = ((AvoidEntityGoalAccessor) (Object) this).pipinha$getAvoidClass();
        if (avoided == Player.class && DeerTame.isTame(this.deer)) {
            cir.setReturnValue(false);
        }
    }
}
