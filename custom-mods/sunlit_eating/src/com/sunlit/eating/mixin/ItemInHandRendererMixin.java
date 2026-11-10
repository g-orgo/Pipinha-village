package com.sunlit.eating.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sunlit.eating.ThirdPersonFoodHook;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// Replaces the flat held item with the food model while it is being eaten in third person.
@Mixin(value = ItemInHandRenderer.class, remap = false)
public abstract class ItemInHandRendererMixin {
    @Inject(method = "m_269530_", at = @At("HEAD"), cancellable = true, remap = false)
    private void sunlit_eating$drawFoodModel(LivingEntity entity, ItemStack stack, ItemDisplayContext context,
            boolean leftHand, PoseStack pose, MultiBufferSource buffers, int light, CallbackInfo ci) {
        if (ThirdPersonFoodHook.render(entity, stack, context, pose, buffers, light)) {
            ci.cancel();
        }
    }
}
