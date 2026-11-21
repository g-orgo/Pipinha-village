package com.pipinha.qualityfix.fd;

import com.pipinha.qualityfix.OwnerAware;
import com.pipinha.qualityfix.Quality;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.Implements;
import org.spongepowered.asm.mixin.Interface;
import vectorwing.farmersdelight.common.block.entity.inventory.CookingPotItemHandler;

@Mixin(CookingPotItemHandler.class)
@Implements(@Interface(iface = OwnerAware.class, prefix = "ownerAware$", unique = true))
public abstract class CookingPotItemHandlerMixin {
    /** Slot of the meal output in Farmer's Delight 1.3.4 (SLOT_MEAL_OUTPUT). */
    @Unique
    private static final int PIPINHA_MEAL_OUTPUT = 8;

    @Unique
    private BlockEntity pipinha$owner;

    // Soft-implements OwnerAware.setOwner; the prefix must not be shared with any other method.
    public void ownerAware$setOwner(BlockEntity owner) {
        this.pipinha$owner = owner;
    }

    /** Hopper, funnel and mechanical arm path: the meal leaving the output slot gets quality. */
    @Inject(method = "extractItem", at = @At("RETURN"))
    private void pipinha$qualityOnExtract(int slot, int amount, boolean simulate, CallbackInfoReturnable<ItemStack> cir) {
        if (!simulate && slot == PIPINHA_MEAL_OUTPUT) {
            Quality.apply(this.pipinha$owner, cir.getReturnValue());
        }
    }
}
