package com.pipinha.cinematictoms.client.emi;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;

// Stands in for the window EMI keeps behind its recipe page when a lookup starts on a scene.
// Never drawn: the recipe page replaces it at once, and returning to it goes back to the scene.
// It carries the menu the scene has open (the terminal's, when there is one), so EMI finds the
// terminal's own fill handler: the craft button then counts the stored items and fills the
// scene's crafting grid from them, instead of only the player's inventory.
public final class SceneLookupScreen extends AbstractContainerScreen<AbstractContainerMenu> {
    SceneLookupScreen(AbstractContainerMenu menu, Player player) {
        super(menu, player.getInventory(), player.getDisplayName());
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
    }

    // The window's menu stays in use by the scene.
    @Override
    public void removed() {
    }
}
