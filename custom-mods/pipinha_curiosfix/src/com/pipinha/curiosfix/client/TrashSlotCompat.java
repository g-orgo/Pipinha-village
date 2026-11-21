package com.pipinha.curiosfix.client;

import net.blay09.mods.trashslot.api.TrashSlotAPI;
import top.theillusivec4.curios.client.gui.CuriosScreen;

/**
 * Enables the TrashSlot trash slot by default on the Curios inventory screen.
 * Only referenced when trashslot and curios are both loaded.
 */
public final class TrashSlotCompat {

    private TrashSlotCompat() {
    }

    public static void register() {
        TrashSlotAPI.registerSimpleLayout(CuriosScreen.class)
                .setEnabledByDefault()
                .enableDefaultCollision()
                .enableDefaultSnaps();
    }
}
