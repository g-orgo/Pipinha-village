package com.pipinha.qualityfix.bnc;

import com.pipinha.qualityfix.KegBatchAccess;
import de.cadentem.quality_food.core.codecs.Quality;
import de.cadentem.quality_food.core.codecs.QualityType;
import de.cadentem.quality_food.registry.QFComponents;
import de.cadentem.quality_food.util.QualityUtils;
import de.cadentem.quality_food.util.Utils;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import umpaz.brewinandchewin.common.block.entity.KegBlockEntity;
import umpaz.brewinandchewin.common.container.AbstractedFluidTank;
import umpaz.brewinandchewin.common.container.AbstractedItemHandler;
import umpaz.brewinandchewin.common.crafting.KegFermentingRecipe;

// The keg has no quality support: its fermenting consumes the ingredients without looking at
// them. The batch quality is rolled from the ingredients when a fermentation finishes, kept on
// the block entity while the tank holds fluid, and handed to every drink taken from the keg.
@Mixin(value = KegBlockEntity.class, remap = false)
public abstract class KegBlockEntityMixin implements KegBatchAccess {
    @Unique
    private static final String PIPINHA_QUALITY_KEY = "SunlitQuality";
    // Ingredient slots of the keg; slot 4 is the container slot and slot 5 the item output.
    @Unique
    private static final int PIPINHA_INPUT_SLOTS = 4;

    @Shadow
    @Final
    private AbstractedItemHandler inventory;
    @Shadow
    @Final
    private AbstractedFluidTank fluidTank;

    @Unique
    private Holder<QualityType> pipinha$batch = null;

    // Runs before any branch of processFermenting, so the roll is ready before the item result
    // is modified (a @ModifyArg on the same call would otherwise read the old value).
    @Inject(
            method = "processFermenting(Lumpaz/brewinandchewin/common/crafting/KegFermentingRecipe;Lumpaz/brewinandchewin/common/block/entity/KegBlockEntity;)Z",
            at = @At(value = "INVOKE", ordinal = 0, target = "Lumpaz/brewinandchewin/common/crafting/KegFermentingRecipe;getResult()Lcom/mojang/datafixers/util/Either;")
    )
    private void pipinha$rollBatch(KegFermentingRecipe recipe, KegBlockEntity keg, CallbackInfo callback) {
        BlockEntity owner = (BlockEntity) (Object) this;
        List<ItemStack> ingredients = new ArrayList<>();
        for (int slot = 0; slot < PIPINHA_INPUT_SLOTS; slot++) {
            ItemStack stack = this.inventory.getStackInSlot(slot);
            if (!stack.isEmpty() && Utils.isValidItem(stack)) {
                ingredients.add(stack.copy());
            }
        }
        // A fluid ingredient carries the batch quality of the keg into the next step of a chain.
        if (this.pipinha$batch != null && !this.fluidTank.isEmpty() && recipe.getFluidIngredient().isPresent()) {
            ItemStack chained = new ItemStack(Items.APPLE);
            QualityUtils.applyQuality(chained, this.pipinha$batch);
            ingredients.add(chained);
        }
        // Food is needed for Quality Food to roll; the probe only carries the rolled quality.
        ItemStack probe = new ItemStack(Items.APPLE);
        Utils.incrementQuality(owner, ingredients, probe);
        Quality quality = QualityUtils.getQuality(probe);
        this.pipinha$batch = quality != null && quality.level() > 0 ? quality.getType() : null;
    }

    @ModifyArg(
            method = "processFermenting(Lumpaz/brewinandchewin/common/crafting/KegFermentingRecipe;Lumpaz/brewinandchewin/common/block/entity/KegBlockEntity;)Z",
            at = @At(value = "INVOKE", target = "Lumpaz/brewinandchewin/common/container/AbstractedItemHandler;insertItem(ILnet/minecraft/world/item/ItemStack;Z)Lnet/minecraft/world/item/ItemStack;"),
            index = 1
    )
    private ItemStack pipinha$applyToItemResult(ItemStack result) {
        if (this.pipinha$batch != null && !result.isEmpty()) {
            QualityUtils.applyQuality(result, this.pipinha$batch);
        }
        return result;
    }

    @Inject(
            method = "fluidExtract(Lnet/minecraft/world/item/ItemStack;IZZ)Ljava/util/List;",
            at = @At("RETURN")
    )
    private void pipinha$applyToPoured(ItemStack held, int maxTakeAmount, boolean inGui, boolean isCreative, CallbackInfoReturnable<List<ItemStack>> callback) {
        List<ItemStack> poured = callback.getReturnValue();
        if (this.pipinha$batch == null || poured == null) {
            return;
        }
        for (ItemStack stack : poured) {
            if (!stack.isEmpty() && !stack.has(QFComponents.QUALITY_DATA_COMPONENT.get())) {
                QualityUtils.applyQuality(stack, this.pipinha$batch);
            }
        }
        if (this.fluidTank.isEmpty()) {
            this.pipinha$batch = null;
        }
    }

    // A tank drained by pipes never passes through fluidExtract, so the tick clears the batch too.
    @Inject(
            method = "fermentingTick(Lnet/minecraft/world/level/Level;Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;Lumpaz/brewinandchewin/common/block/entity/KegBlockEntity;)V",
            at = @At("TAIL"))
    private static void pipinha$clearOnTick(Level level, BlockPos pos, BlockState state, KegBlockEntity keg, CallbackInfo callback) {
        ((KegBatchAccess) keg).pipinha$clearBatchIfEmpty();
    }

    @Override
    public void pipinha$clearBatchIfEmpty() {
        if (this.pipinha$batch != null && this.fluidTank.isEmpty()) {
            this.pipinha$batch = null;
        }
    }

    @Inject(
            method = "loadAdditional(Lnet/minecraft/nbt/CompoundTag;Lnet/minecraft/core/HolderLookup$Provider;)V",
            at = @At("TAIL")
    )
    private void pipinha$load(CompoundTag tag, HolderLookup.Provider provider, CallbackInfo callback) {
        this.pipinha$batch = null;
        ResourceLocation id = null;
        if (tag.contains(PIPINHA_QUALITY_KEY, Tag.TAG_STRING)) {
            id = ResourceLocation.tryParse(tag.getString(PIPINHA_QUALITY_KEY));
        } else if (tag.contains(PIPINHA_QUALITY_KEY, Tag.TAG_INT)) {
            id = pipinha$legacyId(tag.getInt(PIPINHA_QUALITY_KEY));
        }
        if (id != null) {
            ResourceLocation typeId = id;
            this.pipinha$batch = provider.<QualityType>lookup(QFComponents.QUALITY_TYPE_REGISTRY)
                    .flatMap(lookup -> lookup.get(QFComponents.key(typeId)))
                    .orElse(null);
        }
    }

    @Inject(
            method = "saveAdditional(Lnet/minecraft/nbt/CompoundTag;Lnet/minecraft/core/HolderLookup$Provider;)V",
            at = @At("TAIL")
    )
    private void pipinha$save(CompoundTag tag, HolderLookup.Provider provider, CallbackInfo callback) {
        this.pipinha$writeBatch(tag);
    }

    // Used when the keg is broken and keeps its drink as an item.
    @Inject(
            method = "writeDrink(Lnet/minecraft/nbt/CompoundTag;Lnet/minecraft/core/HolderLookup$Provider;)Lnet/minecraft/nbt/CompoundTag;",
            at = @At("RETURN")
    )
    private void pipinha$saveToItem(CompoundTag tag, HolderLookup.Provider provider, CallbackInfoReturnable<CompoundTag> callback) {
        this.pipinha$writeBatch(callback.getReturnValue());
    }

    @Unique
    private void pipinha$writeBatch(CompoundTag tag) {
        if (tag != null && this.pipinha$batch != null) {
            this.pipinha$batch.unwrapKey().ifPresent(key -> tag.putString(PIPINHA_QUALITY_KEY, key.location().toString()));
        }
    }

    // Converted 1.20.1 worlds stored the level as an int: 1 iron, 2 gold, 3 diamond.
    @Unique
    private static ResourceLocation pipinha$legacyId(int level) {
        return switch (level) {
            case 1 -> ResourceLocation.fromNamespaceAndPath("quality_food", "iron");
            case 2 -> ResourceLocation.fromNamespaceAndPath("quality_food", "gold");
            case 3 -> ResourceLocation.fromNamespaceAndPath("quality_food", "diamond");
            default -> null;
        };
    }
}
