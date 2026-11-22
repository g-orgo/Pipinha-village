package com.pipinha.cinematictoms.mixin;

import com.tom.storagemod.block.entity.CraftingTerminalBlockEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.inventory.ResultContainer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(value = CraftingTerminalBlockEntity.class, remap = false)
public abstract class TomsCraftingResultMixin {
    @ModifyArg(
            method = "onCraftingMatrixChanged",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/world/inventory/ResultContainer;setItem(ILnet/minecraft/world/item/ItemStack;)V"),
            index = 1)
    private ItemStack pipinha$useEmptyStackForMissingRecipe(ItemStack result) {
        return result == null ? ItemStack.EMPTY : result;
    }
}
