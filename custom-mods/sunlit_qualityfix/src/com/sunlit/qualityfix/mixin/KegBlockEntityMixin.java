package com.sunlit.qualityfix.mixin;

import com.sunlit.qualityfix.QualityFix;
import de.cadentem.quality_food.core.Quality;
import de.cadentem.quality_food.util.QualityUtils;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.RegistryAccess;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.fluids.capability.templates.FluidTank;
import net.minecraftforge.items.ItemStackHandler;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import umpaz.brewinandchewin.common.block.entity.KegBlockEntity;
import umpaz.brewinandchewin.common.crafting.KegFermentingRecipe;
import umpaz.brewinandchewin.common.crafting.KegPouringRecipe;
import umpaz.brewinandchewin.common.utility.KegRecipeWrapper;

// The keg has no quality support: its fermenting consumes the ingredients without looking at
// them. A fermented fluid keeps the batch quality on the block entity (a FluidStack tag would
// stop plain fluid of the same type from merging) and hands it to every drink poured from it.
@Mixin(value = KegBlockEntity.class, remap = false)
public abstract class KegBlockEntityMixin {
    @Unique
    private static final String SUNLIT_QUALITY_KEY = "SunlitQuality";
    @Unique
    private static final String SUNLIT_FERMENTED_KEY = "SunlitFermented";
    @Unique
    private static final int SUNLIT_INPUT_SLOTS = 5;
    @Unique
    private static final int SUNLIT_ITEM_OUTPUT_SLOT = 5;

    @Shadow
    @Final
    private ItemStackHandler inventory;
    @Shadow
    @Final
    private FluidTank fluidTank;

    // Level of the fluid in the tank, and whether that fluid came out of a fermentation (only
    // then does it count as an ingredient of the next step of a chain such as beer to ale).
    @Unique
    private int sunlit_qualityfix$quality = 0;
    @Unique
    private boolean sunlit_qualityfix$fermented = false;
    @Unique
    private int sunlit_qualityfix$batch = 0;

    @Inject(
            method = "processFermenting",
            at = @At(value = "INVOKE", ordinal = 0, target = "Lumpaz/brewinandchewin/common/crafting/KegFermentingRecipe;getResultFluid()Lnet/minecraft/world/level/material/Fluid;")
    )
    private void sunlit_qualityfix$rollBatch(KegFermentingRecipe recipe, KegBlockEntity keg, CallbackInfoReturnable<Boolean> callback) {
        List<ItemStack> ingredients = new ArrayList<>();
        for (int slot = 0; slot < SUNLIT_INPUT_SLOTS; slot++) {
            ingredients.add(this.inventory.getStackInSlot(slot));
        }
        int batch = QualityFix.resolveBatch(ingredients).level();
        if (this.sunlit_qualityfix$fermented && !this.fluidTank.isEmpty() && recipe.getFluidIngredient() != null) {
            batch = Math.min(batch, this.sunlit_qualityfix$quality);
        }
        this.sunlit_qualityfix$batch = batch;
        if (recipe.getResultFluid() != null) {
            this.sunlit_qualityfix$quality = batch;
            this.sunlit_qualityfix$fermented = true;
        }
    }

    // The output slot drops what does not stack, so a result that differs from what the slot
    // holds takes the tag of the slot instead of being lost.
    @ModifyArg(
            method = "processFermenting",
            at = @At(value = "INVOKE", target = "Lnet/minecraftforge/items/ItemStackHandler;insertItem(ILnet/minecraft/world/item/ItemStack;Z)Lnet/minecraft/world/item/ItemStack;"),
            index = 1
    )
    private ItemStack sunlit_qualityfix$applyToItemResult(ItemStack result) {
        ItemStack held = this.inventory.getStackInSlot(SUNLIT_ITEM_OUTPUT_SLOT);
        if (!held.m_41619_() && ItemStack.m_41656_(held, result)) {
            result.m_41751_(held.m_41782_() ? held.m_41783_().m_6426_() : null);
            return result;
        }
        QualityUtils.applyQuality(result, QualityFix.fromLevel(this.sunlit_qualityfix$batch));
        return result;
    }

    @Redirect(
            method = "fluidExtract",
            at = @At(value = "INVOKE", target = "Lumpaz/brewinandchewin/common/crafting/KegPouringRecipe;assemble(Lumpaz/brewinandchewin/common/utility/KegRecipeWrapper;Lnet/minecraft/core/RegistryAccess;)Lnet/minecraft/world/item/ItemStack;")
    )
    private ItemStack sunlit_qualityfix$applyToPoured(KegPouringRecipe recipe, KegRecipeWrapper wrapper, RegistryAccess access) {
        ItemStack poured = recipe.assemble(wrapper, access).m_41777_();
        QualityUtils.applyQuality(poured, QualityFix.fromLevel(this.sunlit_qualityfix$quality));
        return poured;
    }

    // Fluid coming back from a held drink or container cannot raise the quality of the tank.
    @Inject(
            method = "fluidExtract",
            at = @At(value = "INVOKE", target = "Lnet/minecraftforge/fluids/capability/templates/FluidTank;fill(Lnet/minecraftforge/fluids/FluidStack;Lnet/minecraftforge/fluids/capability/IFluidHandler$FluidAction;)I")
    )
    private void sunlit_qualityfix$mergeFilled(ItemStack held, int maxTakeAmount, boolean inGui, boolean isCreative, CallbackInfoReturnable<List<ItemStack>> callback) {
        int level = QualityUtils.getQuality(held).level();
        if (this.fluidTank.isEmpty()) {
            this.sunlit_qualityfix$quality = level;
            this.sunlit_qualityfix$fermented = level > 0;
        } else {
            this.sunlit_qualityfix$quality = Math.min(this.sunlit_qualityfix$quality, level);
        }
    }

    // Covers a tank drained by pipes, which never passes through fluidExtract.
    @Inject(method = "fermentingTick", at = @At("HEAD"))
    private static void sunlit_qualityfix$clearWhenEmpty(Level level, BlockPos pos, BlockState state, KegBlockEntity keg, CallbackInfo callback) {
        KegBlockEntityMixin self = (KegBlockEntityMixin) (Object) keg;
        if (self.fluidTank.isEmpty()) {
            self.sunlit_qualityfix$quality = 0;
            self.sunlit_qualityfix$fermented = false;
        }
    }

    @Inject(method = "m_142466_(Lnet/minecraft/nbt/CompoundTag;)V", at = @At("TAIL"))
    private void sunlit_qualityfix$load(CompoundTag compound, CallbackInfo callback) {
        this.sunlit_qualityfix$quality = compound.m_128451_(SUNLIT_QUALITY_KEY);
        this.sunlit_qualityfix$fermented = compound.m_128471_(SUNLIT_FERMENTED_KEY);
    }

    @Inject(method = "m_183515_(Lnet/minecraft/nbt/CompoundTag;)V", at = @At("TAIL"))
    private void sunlit_qualityfix$save(CompoundTag compound, CallbackInfo callback) {
        sunlit_qualityfix$writeQuality(compound);
    }

    // Used when the keg is broken and keeps its drink as an item.
    @Inject(method = "writeDrink", at = @At("RETURN"))
    private void sunlit_qualityfix$saveToItem(CompoundTag compound, CallbackInfoReturnable<CompoundTag> callback) {
        sunlit_qualityfix$writeQuality(compound);
    }

    @Unique
    private void sunlit_qualityfix$writeQuality(CompoundTag compound) {
        compound.m_128405_(SUNLIT_QUALITY_KEY, this.sunlit_qualityfix$quality);
        compound.m_128379_(SUNLIT_FERMENTED_KEY, this.sunlit_qualityfix$fermented);
    }
}
