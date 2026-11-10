package com.sunlit.qualityfix.mixin;

import com.sunlit.qualityfix.QualityFix;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import vectorwing.farmersdelight.common.block.entity.CookingPotBlockEntity;

// Serving a meal by right-clicking the pot with its container skips the result slot,
// the only place Quality Food reads the pot's quality queue.
@Mixin(value = CookingPotBlockEntity.class, remap = false)
public abstract class CookingPotBlockEntityMixin {
    @Inject(method = "useHeldItemOnMeal", at = @At("RETURN"))
    private void sunlit_qualityfix$applyToServing(ItemStack container, CallbackInfoReturnable<ItemStack> callback) {
        QualityFix.applyQueuedQuality((BlockEntity) (Object) this, callback.getReturnValue());
    }
}
