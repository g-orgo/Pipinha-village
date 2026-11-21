package com.pipinha.freelook;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.settings.KeyConflictContext;
import org.lwjgl.glfw.GLFW;

/** The hold-to-use Free Look key mapping. */
public final class FreeLookKeys {

    public static final KeyMapping FREE_LOOK = new KeyMapping(
            "key.pipinha_freelook.free_look",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_LEFT_ALT,
            "key.categories.pipinha");

    private FreeLookKeys() {
    }

    static void register(RegisterKeyMappingsEvent event) {
        event.register(FREE_LOOK);
    }
}
