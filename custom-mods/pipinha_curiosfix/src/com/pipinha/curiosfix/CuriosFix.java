package com.pipinha.curiosfix;

import com.pipinha.curiosfix.client.TrashSlotCompat;
import com.pipinha.curiosfix.client.TrashSlotDiagnostics;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;

@Mod("pipinha_curiosfix")
public class CuriosFix {

    public CuriosFix(IEventBus modBus) {
        if (FMLEnvironment.dist == Dist.CLIENT) {
            modBus.addListener(this::onClientSetup);
        }
    }

    private void onClientSetup(FMLClientSetupEvent event) {
        // TrashSlot classes are only loaded when both mods are present.
        if (ModList.get().isLoaded("trashslot") && ModList.get().isLoaded("curios")) {
            event.enqueueWork(TrashSlotCompat::register);
            // Temporary: remove with TrashSlotDiagnostics after the owner's test.
            NeoForge.EVENT_BUS.register(TrashSlotDiagnostics.class);
        }
    }
}
