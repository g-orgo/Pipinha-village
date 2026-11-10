package com.sunlit.eating;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLEnvironment;

// Client only behaviour. The class stays loadable on a dedicated server, where it does nothing.
@Mod("sunlit_eating")
public class SunlitEating {
    public SunlitEating() {
        if (FMLEnvironment.dist == Dist.CLIENT) {
            EatingAnimations.init();
            ImmersiveEatingGuard.init();
            HotbarSwitchGuard.init();
        }
    }
}
