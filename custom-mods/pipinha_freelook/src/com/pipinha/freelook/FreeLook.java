package com.pipinha.freelook;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.common.NeoForge;

/** Client-only mod entry: wires the key mapping and the client event listeners. */
@Mod(value = "pipinha_freelook", dist = Dist.CLIENT)
public class FreeLook {

    public FreeLook(IEventBus modBus) {
        modBus.addListener(RegisterKeyMappingsEvent.class, FreeLookKeys::register);
        NeoForge.EVENT_BUS.register(new FreeLookEvents());
    }
}
