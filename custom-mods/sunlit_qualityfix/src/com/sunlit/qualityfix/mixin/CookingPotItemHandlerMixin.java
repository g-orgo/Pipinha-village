package com.sunlit.qualityfix.mixin;

import com.sunlit.qualityfix.QualityFix;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.IItemHandler;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import vectorwing.farmersdelight.common.block.entity.inventory.CookingPotItemHandler;

// Hoppers, funnels and Central Kitchen's mechanical arms take meals through this handler,
// which left them without quality and the pot's quality queue out of step.
@Mixin(value = CookingPotItemHandler.class, remap = false)
public abstract class CookingPotItemHandlerMixin {
    private static final int SUNLIT_MEAL_OUTPUT_SLOT = 8;

    @Shadow
    @Final
    private IItemHandler itemHandler;

    @Inject(method = "extractItem", at = @At("RETURN"))
    private void sunlit_qualityfix$applyToExtracted(int slot, int amount, boolean simulate, CallbackInfoReturnable<ItemStack> callback) {
        if (!simulate && slot == SUNLIT_MEAL_OUTPUT_SLOT) {
            QualityFix.applyQueuedQuality(QualityFix.ownerOf(this.itemHandler), callback.getReturnValue());
        }
    }
}
