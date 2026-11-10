package com.sunlit.qualityfix;

import de.cadentem.quality_food.config.QualityConfig;
import de.cadentem.quality_food.core.Quality;
import de.cadentem.quality_food.util.QualityUtils;
import de.cadentem.quality_food.util.Utils;
import java.lang.reflect.Field;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;

public final class QualityFix {
    private QualityFix() {
    }

    // Same result as Quality Food's BlockData.useQuality for cooking pots: the lowest
    // ingredient quality is guaranteed and the averaged cooking bonus can roll it higher.
    // Ingredients Quality Food does not track (salt, blacklisted items) are ignored.
    public static Quality resolveBatch(List<ItemStack> ingredients) {
        int counted = 0;
        double bonus = 0.0;
        Quality floor = null;
        for (ItemStack ingredient : ingredients) {
            if (!Utils.isValidItem(ingredient)) {
                continue;
            }
            Quality quality = QualityUtils.getQuality(ingredient);
            if (quality != Quality.NONE) {
                bonus += QualityUtils.getCookingBonus(quality);
            }
            if (floor == null || quality.level() < floor.level()) {
                floor = quality;
            }
            counted++;
        }
        if (counted == 0) {
            return Quality.NONE;
        }
        Quality selected = floor;
        double averageBonus = bonus / counted;
        for (Quality quality : List.of(Quality.IRON, Quality.GOLD, Quality.DIAMOND)) {
            double roll = ThreadLocalRandom.current().nextDouble() + averageBonus / (quality.level() * quality.level());
            if (roll > 1.0 - QualityConfig.getChance(quality) && quality.level() > selected.level()) {
                selected = quality;
            }
        }
        return selected;
    }

    public static Quality fromLevel(int level) {
        return switch (level) {
            case 1 -> Quality.IRON;
            case 2 -> Quality.GOLD;
            case 3 -> Quality.DIAMOND;
            default -> Quality.NONE;
        };
    }

    // Hands an item taken out of a pot its queued quality, as the pot's result slot does.
    public static void applyQueuedQuality(BlockEntity pot, ItemStack stack) {
        if (pot == null || stack.m_41619_() || pot.m_58904_() == null || pot.m_58904_().m_5776_()) {
            return;
        }
        Utils.useQuality(pot, stack, null);
    }

    // A pot's capability handler only holds the pot's inner inventory, an anonymous class
    // whose synthetic outer field points back to the block entity.
    public static BlockEntity ownerOf(Object innerInventory) {
        for (Field field : innerInventory.getClass().getDeclaredFields()) {
            if (BlockEntity.class.isAssignableFrom(field.getType())) {
                try {
                    field.setAccessible(true);
                    return (BlockEntity) field.get(innerInventory);
                } catch (ReflectiveOperationException | RuntimeException exception) {
                    return null;
                }
            }
        }
        return null;
    }
}
