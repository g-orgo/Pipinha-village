package com.pipinha.cinematictoms.client;

import com.pipinha.cinematictoms.CinematicToms;
import com.tom.storagemod.menu.StorageTerminalMenu;
import dev.dyslexic.cinematic.api.client.AddonScenes;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;

@EventBusSubscriber(modid = CinematicToms.MOD_ID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class TerminalClientSetup {
    private TerminalClientSetup() {
    }

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            AddonScenes.register(CinematicToms.STORAGE_TERMINAL,
                    (pos, state, player, side) -> new TerminalStation(pos, side, StorageTerminalMenu.class));
            AddonScenes.register(CinematicToms.CRAFTING_TERMINAL,
                    (pos, state, player, side) -> new TerminalStation(pos, side, StorageTerminalMenu.class));
        });
    }
}
