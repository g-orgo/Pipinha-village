package com.pipinha.curiosfix.mixin;

import com.pipinha.curiosfix.client.CuriosArmorLayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Simple Hats' HumanoidArmorLayer mixin cancels the helmet whenever getVisibleHat returns a hat, so a
 * hat in a Curios slot replaced the helmet look. During the armor layer pass this reports no hat;
 * the hat layer itself still sees the hat and draws it on top of the helmet.
 */
@Mixin(targets = "fonnymunkey.simplehats.compat.curios.CuriosCompat", remap = false)
public abstract class SimpleHatsCuriosCompatMixin {

    @Inject(method = "getVisibleHat(Lnet/minecraft/world/entity/LivingEntity;)Lnet/minecraft/world/item/ItemStack;",
            at = @At("HEAD"), cancellable = true)
    private void pipinha$keepHelmet(LivingEntity entity, CallbackInfoReturnable<ItemStack> cir) {
        if (CuriosArmorLayer.hideHatFromArmorLayer(entity)) {
            cir.setReturnValue(ItemStack.EMPTY);
        }
    }
}
