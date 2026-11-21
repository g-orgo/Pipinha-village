package com.pipinha.curiosfix.client;

import com.mojang.logging.LogUtils;
import net.blay09.mods.trashslot.TrashSlot;
import net.blay09.mods.trashslot.TrashSlotSaveState;
import net.blay09.mods.trashslot.api.IGuiContainerLayout;
import net.blay09.mods.trashslot.client.ContainerSettings;
import net.blay09.mods.trashslot.client.LayoutManager;
import net.blay09.mods.trashslot.client.TrashSlotGuiHandler;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ScreenEvent;
import org.slf4j.Logger;
import top.theillusivec4.curios.client.gui.CuriosScreen;

/**
 * Temporary diagnostics: the TrashSlot toggle key did nothing on the Curios screen.
 * Logs, only for the Curios screen and only for the toggle key, what TrashSlot sees.
 * Remove after the owner's test session.
 */
public final class TrashSlotDiagnostics {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String PREFIX = "[CuriosFix/TrashSlot] ";
    private static final String TOGGLE_KEY = "key.trashslot.toggle";

    private TrashSlotDiagnostics() {
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onInit(ScreenEvent.Init.Post event) {
        if (!(event.getScreen() instanceof CuriosScreen screen)) {
            return;
        }
        IGuiContainerLayout layout = LayoutManager.getLayout(screen);
        ContainerSettings settings = TrashSlotSaveState.getSettings(screen, layout);
        LOGGER.info(PREFIX + "init: serverInstalled={} component={} enabled={} enabledByDefault={} slot=({}, {}) gui=({}, {}, {}x{})",
                TrashSlot.isServerSideInstalled, TrashSlotGuiHandler.getTrashSlotComponent() != null,
                settings.isEnabled(), layout.isEnabledByDefault(), settings.getSlotX(), settings.getSlotY(),
                screen.getGuiLeft(), screen.getGuiTop(), screen.getXSize(), screen.getYSize());
    }

    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void onKeyFirst(ScreenEvent.KeyPressed.Pre event) {
        if (isToggle(event)) {
            LOGGER.info(PREFIX + "toggle key arrived (HIGHEST): canceled={}", event.isCanceled());
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void onKeyLast(ScreenEvent.KeyPressed.Pre event) {
        if (isToggle(event)) {
            LOGGER.info(PREFIX + "toggle key (LOWEST): canceled={} enabled={}", event.isCanceled(), currentEnabled(event));
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onKeyPost(ScreenEvent.KeyPressed.Post event) {
        if (isToggle(event)) {
            LOGGER.info(PREFIX + "toggle key (Post): enabled={}", currentEnabled(event));
        }
    }

    private static boolean isToggle(ScreenEvent.KeyPressed event) {
        if (!(event.getScreen() instanceof CuriosScreen)) {
            return false;
        }
        for (KeyMapping mapping : Minecraft.getInstance().options.keyMappings) {
            if (TOGGLE_KEY.equals(mapping.getName())) {
                return mapping.matches(event.getKeyCode(), event.getScanCode());
            }
        }
        LOGGER.info(PREFIX + "key mapping {} not found in options", TOGGLE_KEY);
        return false;
    }

    private static boolean currentEnabled(ScreenEvent.KeyPressed event) {
        CuriosScreen screen = (CuriosScreen) event.getScreen();
        return TrashSlotSaveState.getSettings(screen, LayoutManager.getLayout(screen)).isEnabled();
    }
}
