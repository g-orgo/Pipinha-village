package com.pipinha.qualityfix.fd;

import com.pipinha.qualityfix.OwnerAware;
import com.pipinha.qualityfix.Quality;
import net.minecraft.core.BlockPos;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.items.IItemHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import vectorwing.farmersdelight.common.block.entity.CookingPotBlockEntity;

@Mixin(CookingPotBlockEntity.class)
public abstract class CookingPotBlockEntityMixin {
    @Shadow
    private IItemHandler inputHandler;

    @Shadow
    private IItemHandler outputHandler;

    /** Links both item handlers back to this pot, so their extract path can reach the quality data. */
    @Inject(method = "<init>", at = @At("TAIL"))
    private void pipinha$linkHandlers(BlockPos pos, BlockState state, CallbackInfo ci) {
        BlockEntity self = (BlockEntity) (Object) this;
        ((OwnerAware) this.inputHandler).setOwner(self);
        ((OwnerAware) this.outputHandler).setOwner(self);
    }

    /** Hand-held bowl path: the meal returned to the player gets quality. */
    @Inject(method = "useHeldItemOnMeal", at = @At("RETURN"))
    private void pipinha$qualityOnHeldMeal(ItemStack held, CallbackInfoReturnable<ItemStack> cir) {
        Quality.apply((BlockEntity) (Object) this, cir.getReturnValue());
    }
}
