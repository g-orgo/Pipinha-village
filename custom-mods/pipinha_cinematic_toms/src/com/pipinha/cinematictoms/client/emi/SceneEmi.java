package com.pipinha.cinematictoms.client.emi;

import dev.dyslexic.cinematic.client.ClientStation;
import dev.dyslexic.cinematic.client.Picking;
import dev.dyslexic.cinematic.client.Scene;
import dev.dyslexic.cinematic.client.SceneScreen;
import dev.dyslexic.cinematic.client.TableStation;
import com.tom.storagemod.menu.StorageTerminalMenu;
import com.pipinha.cinematictoms.client.TerminalStation;
import com.pipinha.cinematictoms.mixin.SceneScreenAccessor;
import java.lang.reflect.Field;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.Rect2i;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

// EMI's usual sidebar on a Cinematic scene, in place of the field guide book.
// Holds no EMI types, so the scene mixins can ask about it when EMI is absent.
public final class SceneEmi {
    // Seconds into the work before the overlay comes in, once the camera has settled.
    private static final double SETTLE = 0.4;
    private static final int INVENTORY_W = 176;
    private static final int INVENTORY_H = 166;
    // Columns EMI keeps on each side even when the work spreads wide.
    private static final int MIN_SIDE = 90;

    private static boolean active;
    @Nullable
    private static Rect2i area;
    @Nullable
    private static ClientStation areaFor;
    private static int areaW;
    private static int areaH;

    @Nullable
    private static final Field BOOK = field(TableStation.class, "recipeBook");
    @Nullable
    private static final Class<?> BOOK_CLASS = BOOK == null ? null : BOOK.getType();
    @Nullable
    private static final Field BOOK_SHOWN = field(BOOK_CLASS, "shown");
    @Nullable
    private static final Field BOOK_SCALE = field(BOOK_CLASS, "scale");
    @Nullable
    private static final Field BOOK_X = field(BOOK_CLASS, "x");
    @Nullable
    private static final Field BOOK_Y = field(BOOK_CLASS, "y");
    @Nullable
    private static final Field BOOK_TOGGLE_Y = field(BOOK_CLASS, "toggleY");

    private SceneEmi() {
    }

    public static boolean active() {
        return active;
    }

    static void setActive(boolean on) {
        active = on;
        area = null;
    }

    // The terminal menu the scene has open, when the station at hand is a storage terminal.
    @Nullable
    static StorageTerminalMenu terminalMenu() {
        return Scene.station instanceof TerminalStation terminal ? terminal.sceneMenu() : null;
    }

    static boolean inScene() {
        return active && Minecraft.getInstance().screen instanceof SceneScreen;
    }

    // The rectangle EMI treats as the open window: centred like the inventory screen,
    // widened to the scene's inventory drawer and the work. Fixed for the stay, so EMI does not relayout every frame.
    @Nullable
    static Rect2i area(int width, int height) {
        ClientStation station = Scene.station;
        if (!active || Scene.phase != Scene.Phase.ACTIVE || station == null || Scene.time < SETTLE) {
            area = null;
            return null;
        }
        if (area != null && areaFor == station && areaW == width && areaH == height) {
            return area;
        }
        // Same scale as SceneScreen's drawer.
        float scale = Mth.clamp(height * 0.068f / 18.0f, 0.6f, 1.25f);
        double centre = width / 2.0;
        double half = Math.max(INVENTORY_W / 2.0, Math.round(172.0f * scale) / 2.0 + 4.0);
        for (Vec3 sample : station.workSamples()) {
            double[] at = Picking.toGui(sample);
            if (at != null) {
                half = Math.max(half, Math.abs(at[0] - centre) + 12.0);
            }
        }
        half = Math.min(half, Math.max(INVENTORY_W / 2.0, centre - MIN_SIDE));
        int h = (int) Math.ceil(half);
        area = new Rect2i(width / 2 - h, (height - INVENTORY_H) / 2, h * 2, INVENTORY_H);
        areaFor = station;
        areaW = width;
        areaH = height;
        return area;
    }

    static boolean overSides(double mx) {
        Rect2i at = area;
        return at != null && (mx < at.getX() || mx >= at.getX() + at.getWidth());
    }

    @Nullable
    static ItemStack hoveredPanelItem() {
        if (!inScene() || Scene.phase != Scene.Phase.ACTIVE) {
            return null;
        }
        ItemStack stack = ((SceneScreenAccessor) Minecraft.getInstance().screen).cinematicToms$hoveredPanelItem();
        return stack == null || stack.isEmpty() ? null : stack;
    }

    // The table's recipe book sits on the left, where EMI's favorites go.
    static List<Rect2i> extraAreas() {
        if (!inScene() || !(Scene.station instanceof TableStation table) || BOOK == null || BOOK_SHOWN == null
                || BOOK_SCALE == null || BOOK_X == null || BOOK_Y == null || BOOK_TOGGLE_Y == null) {
            return List.of();
        }
        try {
            Object book = BOOK.get(table);
            float scale = BOOK_SCALE.getFloat(book);
            if (BOOK_SHOWN.getDouble(book) > 0.02) {
                return List.of(new Rect2i(BOOK_X.getInt(book), BOOK_Y.getInt(book),
                        Mth.ceil(128.0f * scale), Mth.ceil(226.0f * scale)));
            }
            return List.of(new Rect2i(8, BOOK_TOGGLE_Y.getInt(book), Mth.ceil(32.0f * scale), Mth.ceil(28.0f * scale)));
        } catch (ReflectiveOperationException | RuntimeException e) {
            return List.of();
        }
    }

    @Nullable
    private static Field field(@Nullable Class<?> owner, String name) {
        if (owner == null) {
            return null;
        }
        try {
            Field f = owner.getDeclaredField(name);
            f.setAccessible(true);
            return f;
        } catch (ReflectiveOperationException | RuntimeException e) {
            return null;
        }
    }
}
