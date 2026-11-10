package com.sunlit.eating;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

// Public entry for the mixin, so ThirdPersonFood can stay package private.
public final class ThirdPersonFoodHook {
    private ThirdPersonFoodHook() {
    }

    public static boolean render(LivingEntity entity, ItemStack stack, ItemDisplayContext context, PoseStack pose,
            MultiBufferSource buffers, int light) {
        return ThirdPersonFood.render(entity, stack, context, pose, buffers, light);
    }
}
