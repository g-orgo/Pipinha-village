package com.pipinha.cinematictoms.client;

import com.mojang.logging.LogUtils;
import com.tom.storagemod.screen.AbstractStorageTerminalScreen;
import dev.dyslexic.cinematic.client.Scene;
import dev.dyslexic.cinematic.client.SceneScreen;
import com.pipinha.cinematictoms.CinematicToms;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.player.LocalPlayer;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import org.slf4j.Logger;

@EventBusSubscriber(modid = CinematicToms.MOD_ID, bus = EventBusSubscriber.Bus.GAME, value = Dist.CLIENT)
public final class TerminalStripEvents {
    private static final Logger LOGGER = LogUtils.getLogger();
    private static Screen lastLoggedTomsScreen;

    private TerminalStripEvents() {
    }

    @SubscribeEvent
    public static void onScreenInit(ScreenEvent.Init.Post event) {
        if (!(event.getScreen() instanceof AbstractStorageTerminalScreen<?> screen) || screen == lastLoggedTomsScreen) {
            return;
        }
        lastLoggedTomsScreen = screen;
        LOGGER.info("[CinematicToms] Tom's screen opened: {} items={}", screen.getClass().getSimpleName(), screen.getMenu().sync.getAsList().size());
    }

    static TerminalStation station() {
        if (!(Minecraft.getInstance().screen instanceof SceneScreen)) {
            return null;
        }
        if (Scene.phase != Scene.Phase.ACTIVE || !(Scene.station instanceof TerminalStation t)) {
            return null;
        }
        return t;
    }

    private static TerminalStation overStrip(double mx, double my) {
        TerminalStation t = station();
        return t != null && t.strip().over(mx, my) ? t : null;
    }

    @SubscribeEvent
    public static void onMouseButton(ScreenEvent.MouseButtonPressed.Pre event) {
        int button = event.getButton();
        if (button != 0 && button != 1) {
            return;
        }
        TerminalStation t = station();
        if (t == null) {
            return;
        }
        if (!t.strip().over(event.getMouseX(), event.getMouseY())) {
            t.strip().unfocus();
            return;
        }
        t.stripClick(button, Screen.hasShiftDown());
        event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onMouseScrolled(ScreenEvent.MouseScrolled.Pre event) {
        TerminalStation t = overStrip(event.getMouseX(), event.getMouseY());
        if (t != null) {
            t.strip().scroll(event.getScrollDeltaY());
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onCharTyped(ScreenEvent.CharacterTyped.Pre event) {
        TerminalStation t = station();
        if (t != null && t.strip().charTyped(event.getCodePoint(), event.getModifiers())) {
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onRender(ScreenEvent.Render.Post event) {
        TerminalStation t = overStrip(event.getMouseX(), event.getMouseY());
        LocalPlayer player = Minecraft.getInstance().player;
        if (t != null && player != null) {
            t.strip().renderTooltip(event.getGuiGraphics(), Minecraft.getInstance().font, event.getMouseX(), event.getMouseY(), player.containerMenu.getCarried());
        }
    }
}
