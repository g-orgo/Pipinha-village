package com.sunlit.qualityfix.mixin;

import com.sunlit.qualityfix.QualityFix;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import com.sammy.minersdelight.content.block.copper_pot.CopperPotBlockEntity;

// Same gap as the Farmer's Delight pot: a serving by right-click skips the result slot,
// the only place Quality Food reads the pot's quality queue.
@Mixin(value = CopperPotBlockEntity.class, remap = false)
public abstract class CopperPotBlockEntityMixin {
    @Inject(method = "useHeldItemOnMeal", at = @At("RETURN"))
    private void sunlit_qualityfix$applyToServing(ItemStack container, CallbackInfoReturnable<ItemStack> callback) {
        QualityFix.applyQueuedQuality((BlockEntity) (Object) this, callback.getReturnValue());
    }
}
