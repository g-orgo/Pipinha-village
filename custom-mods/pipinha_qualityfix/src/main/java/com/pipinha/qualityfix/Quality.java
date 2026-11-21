package com.pipinha.qualityfix;

import de.cadentem.quality_food.util.Utils;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

/**
 * Shared entry point that gives a cooking pot meal its Quality Food quality.
 */
public final class Quality {
    private Quality() {
    }

    /**
     * Applies quality to the meal using the pot's own quality data. The player is null, so luck is NONE.
     */
    public static void apply(BlockEntity owner, ItemStack meal) {
        if (owner == null || meal == null || meal.isEmpty()) {
            return;
        }
        Utils.useQuality(owner, meal, null);
    }
}
