package com.pipinha.eating.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import com.pipinha.eating.ThirdPersonFoodHook;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// Replaces the default item drawing for food eaten in third person with the bitten food model.
@Mixin(ItemInHandRenderer.class)
abstract class ItemInHandRendererMixin {
    @Inject(method = "renderItem", at = @At("HEAD"), cancellable = true)
    private void pipinha_eating$drawFoodModel(LivingEntity entity, ItemStack stack, ItemDisplayContext context,
            boolean leftHand, PoseStack pose, MultiBufferSource buffers, int light, CallbackInfo ci) {
        if (ThirdPersonFoodHook.render(entity, stack, context, pose, buffers, light)) {
            ci.cancel();
        }
    }
}
