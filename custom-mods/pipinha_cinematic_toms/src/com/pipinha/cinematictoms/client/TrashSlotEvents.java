package com.pipinha.cinematictoms.client;

import dev.dyslexic.cinematic.client.SceneScreen;
import com.pipinha.cinematictoms.CinematicToms;
import com.pipinha.cinematictoms.mixin.SceneScreenAccessor;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.EventBusSubscriber;
import org.lwjgl.glfw.GLFW;

/**
 * Shows a TrashSlot next to the panel of the Cinematic terminal scene.
 * Soft dependency: every handler returns early when "trashslot" is not loaded,
 * and TrashSlotBridge (the only class that touches TrashSlot) is never reached.
 */
@EventBusSubscriber(modid = CinematicToms.MOD_ID, bus = EventBusSubscriber.Bus.GAME, value = Dist.CLIENT)
public final class TrashSlotEvents {
    private static final String TRASHSLOT_MOD_ID = "trashslot";
    private static final String TOGGLE_KEY_NAME = "key.trashslot.toggle";
    private static final int GAP = 4;

    private TrashSlotEvents() {
    }

    private static boolean installed() {
        return ModList.get().isLoaded(TRASHSLOT_MOD_ID);
    }

    /** Returns the scene screen when the terminal scene is active and the slot is visible, otherwise null. */
    private static SceneScreen activeScreen() {
        if (!installed() || !TrashSlotToggle.isVisible() || TerminalStripEvents.station() == null) {
            return null;
        }
        return Minecraft.getInstance().screen instanceof SceneScreen s ? s : null;
    }

    /** The mixin interface is applied to SceneScreen at runtime, so the compiler needs an explicit cast through Object. */
    private static SceneScreenAccessor accessor(SceneScreen screen) {
        return (SceneScreenAccessor) (Object) screen;
    }

    /** Slot rectangle in screen space, left of the scene panel and aligned with its top. */
    private static int[] slotRect(SceneScreen screen) {
        SceneScreenAccessor a = accessor(screen);
        // The drawn frame reaches FRAME_INSET - 1 px past the slot on every side.
        int overhang = TrashSlotBridge.FRAME_INSET - 1;
        int x = a.cinematicToms$getPanelX() - GAP - overhang - TrashSlotBridge.SIZE;
        int y = a.cinematicToms$getPanelY() + overhang;
        return new int[] {x, y, TrashSlotBridge.SIZE, TrashSlotBridge.SIZE};
    }

    private static boolean inside(int[] r, double mx, double my) {
        return mx >= r[0] && mx < r[0] + r[2] && my >= r[1] && my < r[1] + r[3];
    }

    private static KeyMapping toggleMapping(Minecraft mc) {
        for (KeyMapping k : mc.options.keyMappings) {
            if (TOGGLE_KEY_NAME.equals(k.getName())) {
                return k;
            }
        }
        return null;
    }

    @SubscribeEvent
    public static void onKeyPressed(ScreenEvent.KeyPressed.Pre event) {
        if (!installed() || TerminalStripEvents.station() == null || !(Minecraft.getInstance().screen instanceof SceneScreen screen)) {
            return;
        }
        var field = accessor(screen).cinematicToms$getField();
        if (field != null && field.isFocused()) {
            return;
        }
        // Typing in the terminal's search bar must not toggle the trash slot.
        if (TerminalStripEvents.station().strip().isSearchFocused()) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        KeyMapping toggle = toggleMapping(mc);
        boolean match = toggle != null
                ? toggle.matches(event.getKeyCode(), event.getScanCode())
                : event.getKeyCode() == GLFW.GLFW_KEY_T;
        if (match) {
            TrashSlotToggle.toggle();
            event.setCanceled(true);
        }
    }

    @SubscribeEvent
    public static void onMouseButton(ScreenEvent.MouseButtonPressed.Pre event) {
        int button = event.getButton();
        if (button != 0 && button != 1) {
            return;
        }
        SceneScreen screen = activeScreen();
        LocalPlayer player = Minecraft.getInstance().player;
        if (screen == null || player == null || !inside(slotRect(screen), event.getMouseX(), event.getMouseY())) {
            return;
        }
        boolean right = button == 1;
        if (player.containerMenu.getCarried().isEmpty()) {
            TrashSlotBridge.undeleteLast(player, right);
        } else if (!TrashSlotBridge.isDenied(player.containerMenu.getCarried())) {
            TrashSlotBridge.deleteCarried(player, right);
        }
        event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onRender(ScreenEvent.Render.Post event) {
        SceneScreen screen = activeScreen();
        if (screen == null) {
            return;
        }
        int[] r = slotRect(screen);
        var graphics = event.getGuiGraphics();
        TrashSlotBridge.renderSlot(graphics, r[0], r[1]);
        if (inside(r, event.getMouseX(), event.getMouseY())) {
            ItemStack shown = TrashSlotBridge.shownItem();
            if (!shown.isEmpty()) {
                graphics.renderTooltip(Minecraft.getInstance().font, shown, event.getMouseX(), event.getMouseY());
            }
        }
    }
}
