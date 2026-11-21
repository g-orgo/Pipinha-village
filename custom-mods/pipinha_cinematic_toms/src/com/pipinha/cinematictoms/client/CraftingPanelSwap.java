package com.pipinha.cinematictoms.client;

import dev.dyslexic.cinematic.client.SceneScreen;
import com.pipinha.cinematictoms.mixin.SceneScreenAccessor;
import net.minecraft.client.Minecraft;

// Crafting terminal scene only: the Cinematic inventory panel moves to the bottom centre and the
// terminal contents strip takes the top centre spot. Called at the end of SceneScreen.layout().
public final class CraftingPanelSwap {
    // Same bottom gap StorageStrip uses for its own bottom-centre placement.
    private static final int BOTTOM_GAP = 26;

    private CraftingPanelSwap() {
    }

    public static void apply(SceneScreen screen) {
        SceneScreenAccessor accessor = (SceneScreenAccessor) (Object) screen;
        TerminalStation station = TerminalStripEvents.station();
        if (station == null || !station.crafting()) {
            if (station != null) {
                station.strip().resetSwap();
            }
            return;
        }
        int guiHeight = Minecraft.getInstance().getWindow().getGuiScaledHeight();
        int stripTop = accessor.cinematicToms$getPanelY();
        int inventoryTop = guiHeight - BOTTOM_GAP - accessor.cinematicToms$getPanelH();
        accessor.cinematicToms$setPanelY(inventoryTop);
        station.strip().swapTo(stripTop, inventoryTop);
    }

    // Whether the swap is in effect, under the same condition apply() moves the panel.
    public static boolean active() {
        TerminalStation station = TerminalStripEvents.station();
        return station != null && station.crafting();
    }

    // SceneScreen.overPanel assumes a panel hanging from the top edge and spans from y=0 down to it. With the
    // panel at the bottom that span would cover the whole centre column, grid included, so anchor it to the bottom edge.
    public static boolean overPanel(SceneScreen screen, double mx, double my) {
        SceneScreenAccessor accessor = (SceneScreenAccessor) (Object) screen;
        int panelX = accessor.cinematicToms$getPanelX();
        return mx >= panelX - 4 && mx <= panelX + accessor.cinematicToms$getPanelW() + 4
                && my >= accessor.cinematicToms$getPanelY() - 4
                && my <= Minecraft.getInstance().getWindow().getGuiScaledHeight();
    }
}
