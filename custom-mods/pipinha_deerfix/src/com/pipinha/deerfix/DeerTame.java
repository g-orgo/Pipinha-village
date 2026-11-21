package com.pipinha.deerfix;

import dev.latvian.mods.kubejs.core.WithPersistentData;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;

/**
 * A deer counts as tamed when the pack's husbandry scripts gave it affection
 * (KubeJS persistentData "affection" > 0, set on the first pet), or when it was
 * born from a tamed parent (marker written by DeerEntityMixin on breeding).
 */
public final class DeerTame {
    public static final String BRED_TAME_KEY = "pipinha_tame_deer";

    private DeerTame() {
    }

    public static boolean isTame(Entity entity) {
        if (!(entity instanceof WithPersistentData holder)) {
            return false;
        }
        CompoundTag data = holder.kjs$getPersistentData();
        return data.getDouble("affection") > 0.0D || data.getBoolean(BRED_TAME_KEY);
    }

    public static void markBredTame(Entity entity) {
        if (entity instanceof WithPersistentData holder) {
            holder.kjs$getPersistentData().putBoolean(BRED_TAME_KEY, true);
        }
    }
}
