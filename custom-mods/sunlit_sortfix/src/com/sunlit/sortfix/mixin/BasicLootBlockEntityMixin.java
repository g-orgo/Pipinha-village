package com.sunlit.sortfix.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

// Refurbished's canPlaceItem rejects any slot holding a full stack, so Quark's sort
// (which checks isItemValid on every slot before moving items) aborts silently.
// Accept any item like a vanilla chest; stack limits are still enforced on insertion.
@Mixin(targets = "com.mrcrayfish.furniture.refurbished.blockentity.BasicLootBlockEntity", remap = false)
public abstract class BasicLootBlockEntityMixin {
    @Inject(method = "m_7013_", at = @At("HEAD"), cancellable = true, remap = false)
    private void sunlit_sortfix$allowAnyItem(CallbackInfoReturnable<Boolean> cir) {
        cir.setReturnValue(true);
    }
}
