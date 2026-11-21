package com.pipinha.freelook.compat;

import com.github.exopandora.shouldersurfing.client.ShoulderSurfing;
import net.neoforged.fml.ModList;

/**
 * The only class that touches Shoulder Surfing types. Callers must only reach these methods
 * when the mod is loaded, which every method here checks first.
 */
public final class SsCompat {

    private static final String MOD_ID = "shouldersurfing";

    private SsCompat() {
    }

    public static boolean isLoaded() {
        return ModList.get().isLoaded(MOD_ID);
    }

    public static boolean isShoulderSurfing() {
        return isLoaded() && ShoulderSurfing.getInstance().isShoulderSurfing();
    }

    public static boolean isFreeLooking() {
        return isLoaded() && ShoulderSurfing.getInstance().isFreeLooking();
    }
}
