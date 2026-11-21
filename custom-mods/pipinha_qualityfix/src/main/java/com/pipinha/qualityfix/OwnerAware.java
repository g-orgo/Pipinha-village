package com.pipinha.qualityfix;

import net.minecraft.world.level.block.entity.BlockEntity;

/**
 * Added to the cooking pot item handlers by mixin, so the owning block entity can link itself to them.
 */
public interface OwnerAware {
    void setOwner(BlockEntity owner);
}
