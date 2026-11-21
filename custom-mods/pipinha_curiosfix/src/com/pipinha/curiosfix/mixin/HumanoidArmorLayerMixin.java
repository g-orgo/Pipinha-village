package com.pipinha.curiosfix.mixin;

import java.util.List;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.mojang.blaze3d.vertex.PoseStack;
import com.pipinha.curiosfix.client.CuriosArmorLayer;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Draws Curios clothing (head, body, feet) as an extra layer after the regular armor, and marks the
 * armor pass so Simple Hats stops hiding the helmet (see CuriosArmorLayer).
 */
@Mixin(HumanoidArmorLayer.class)
public abstract class HumanoidArmorLayerMixin {

    private static final String RENDER =
            "render(Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;ILnet/minecraft/world/entity/LivingEntity;FFFFFF)V";
    private static final String RENDER_PIECE =
            "renderArmorPiece(Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/entity/EquipmentSlot;ILnet/minecraft/client/model/HumanoidModel;FFFFFF)V";

    @Shadow
    @SuppressWarnings("rawtypes")
    private void renderArmorPiece(PoseStack poseStack, MultiBufferSource buffer, LivingEntity entity,
            EquipmentSlot slot, int light, HumanoidModel model, float limbSwing, float limbSwingAmount,
            float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
    }

    @Shadow
    @SuppressWarnings("rawtypes")
    private HumanoidModel getArmorModel(EquipmentSlot slot) {
        return null;
    }

    @Inject(method = RENDER, at = @At("HEAD"))
    private void pipinha$beginArmorPass(PoseStack poseStack, MultiBufferSource buffer, int light,
            LivingEntity entity, float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks,
            float netHeadYaw, float headPitch, CallbackInfo ci) {
        CuriosArmorLayer.beginArmorPass(entity);
    }

    @Inject(method = RENDER, at = @At("RETURN"))
    @SuppressWarnings("rawtypes")
    private void pipinha$renderCuriosClothing(PoseStack poseStack, MultiBufferSource buffer, int light,
            LivingEntity entity, float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks,
            float netHeadYaw, float headPitch, CallbackInfo ci) {
        try {
            for (int s = 0; s < CuriosArmorLayer.CURIO_SLOTS.length; s++) {
                EquipmentSlot slot = CuriosArmorLayer.ARMOR_SLOTS[s];
                List<ItemStack> pieces = CuriosArmorLayer.visiblePieces(entity, CuriosArmorLayer.CURIO_SLOTS[s], slot);
                // The piece worn in the regular slot (or its Cosmetic Armor look) keeps the vanilla model.
                int layer = entity.getItemBySlot(slot).isEmpty() ? 0 : 1;
                for (ItemStack piece : pieces) {
                    HumanoidModel model = layer == 0 ? getArmorModel(slot) : CuriosArmorLayer.layerModel(layer);
                    CuriosArmorLayer.setOverride(entity, slot, piece);
                    renderArmorPiece(poseStack, buffer, entity, slot, light, model, limbSwing, limbSwingAmount,
                            partialTick, ageInTicks, netHeadYaw, headPitch);
                    CuriosArmorLayer.clearOverride();
                    layer++;
                }
            }
        } finally {
            CuriosArmorLayer.endArmorPass();
        }
    }

    @WrapOperation(method = RENDER_PIECE, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/LivingEntity;getItemBySlot(Lnet/minecraft/world/entity/EquipmentSlot;)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack pipinha$curiosPiece(LivingEntity entity, EquipmentSlot slot, Operation<ItemStack> original) {
        ItemStack piece = CuriosArmorLayer.overrideFor(entity, slot);
        return piece != null ? piece : original.call(entity, slot);
    }
}
