package com.pipinha.cinematictoms.client;

import com.mojang.logging.LogUtils;
import net.neoforged.fml.loading.FMLPaths;
import org.slf4j.Logger;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Client-side visibility flag for the TrashSlot shown in the Cinematic terminal scene.
 * Stored in a small file of its own; does not reference TrashSlot classes.
 */
public final class TrashSlotToggle {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static final Path FILE = FMLPaths.CONFIGDIR.get().resolve("pipinha_cinematic_toms_trashslot.txt");
    private static boolean visible = true;
    private static boolean loaded;

    private TrashSlotToggle() {
    }

    public static boolean isVisible() {
        load();
        return visible;
    }

    public static void toggle() {
        load();
        visible = !visible;
        save();
    }

    private static void load() {
        if (loaded) {
            return;
        }
        loaded = true;
        try {
            if (Files.exists(FILE)) {
                visible = !"false".equalsIgnoreCase(Files.readString(FILE).trim());
            }
        } catch (IOException e) {
            LOGGER.warn("[CinematicToms] Could not read TrashSlot toggle state from {}", FILE, e);
        }
    }

    private static void save() {
        try {
            Files.writeString(FILE, Boolean.toString(visible));
        } catch (IOException e) {
            LOGGER.warn("[CinematicToms] Could not save TrashSlot toggle state to {}", FILE, e);
        }
    }
}
