package com.pipinha.eating;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;

// Client-only mod: third-person eating poses and the hotbar unlock while eating.
@Mod("pipinha_eating")
public final class PipinhaEating {
    public PipinhaEating() {
        if (FMLEnvironment.dist == Dist.CLIENT) {
            EatingAnimations.init();
            HotbarSwitchGuard.init();
        }
    }
}
