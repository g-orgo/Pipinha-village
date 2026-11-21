package com.pipinha.cinematictoms.mixin;

import com.mojang.blaze3d.systems.RenderSystem;
import com.pipinha.cinematictoms.client.emi.SceneLookupScreen;
import com.tom.storagemod.emi.EmiTransferHandler;
import com.tom.storagemod.inventory.TerminalItemStack;
import com.tom.storagemod.menu.CraftingTerminalMenu;
import dev.emi.emi.api.recipe.EmiPlayerInventory;
import dev.emi.emi.api.recipe.EmiRecipe;
import dev.emi.emi.api.recipe.handler.EmiCraftContext;
import dev.emi.emi.api.stack.EmiIngredient;
import dev.emi.emi.api.stack.EmiStack;
import dev.emi.emi.api.widget.Bounds;
import dev.emi.emi.api.widget.SlotWidget;
import dev.emi.emi.api.widget.Widget;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.world.inventory.Slot;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

// Tom's 2.4.2 only counts the terminal's stored items for EMI when the window is Tom's own terminal
// screen with "smart features" on (1.7.1 on 1.20.1 always counted them). A scene opens EMI's recipe
// page over SceneLookupScreen, which has no such toggle, so the fill button only saw the player's
// inventory and stayed off for recipes whose ingredients sit in the storage. On the scene's stand-in
// window both checks behave as if smart features were on; Tom's own screen keeps its toggle.
@Mixin(value = EmiTransferHandler.class, remap = false)
public abstract class TomsEmiTransferHandlerMixin {
    private static final int MISSING_COLOR = 0x44FF0000;

    @Shadow
    private static List<Integer> handleRecipe(EmiRecipe recipe, AbstractContainerScreen<CraftingTerminalMenu> screen, boolean simulate) {
        throw new AssertionError();
    }

    @Inject(method = "getInventory", at = @At("HEAD"), cancellable = true)
    private void cinematicToms$countStoredItems(AbstractContainerScreen<CraftingTerminalMenu> screen,
            CallbackInfoReturnable<EmiPlayerInventory> cir) {
        Object window = screen;
        if (!(window instanceof SceneLookupScreen lookup) || !(lookup.getMenu() instanceof CraftingTerminalMenu menu)) {
            return;
        }
        List<EmiStack> stacks = new ArrayList<>();
        // Slot 0 is the crafting result; the rest are the crafting grid and the player's inventory.
        for (Slot slot : menu.slots.subList(1, menu.slots.size())) {
            stacks.add(EmiStack.of(slot.getItem()));
        }
        for (TerminalItemStack stored : menu.getStoredItems()) {
            stacks.add(EmiStack.of(stored.getStack(), stored.getQuantity()));
        }
        cir.setReturnValue(new EmiPlayerInventory(stacks));
    }

    // Same red marks Tom's draws on the recipe's missing ingredients, now also on the scene's window.
    @Inject(method = "render", at = @At("HEAD"), cancellable = true)
    private void cinematicToms$markMissing(EmiRecipe recipe, EmiCraftContext<CraftingTerminalMenu> context,
            List<Widget> widgets, GuiGraphics graphics, CallbackInfo ci) {
        Object window = context.getScreen();
        if (!(window instanceof SceneLookupScreen lookup) || !(lookup.getMenu() instanceof CraftingTerminalMenu)) {
            return;
        }
        ci.cancel();
        RenderSystem.enableDepthTest();
        List<Integer> missing = handleRecipe(recipe, context.getScreen(), true);
        int index = 0;
        for (Widget widget : widgets) {
            if (!(widget instanceof SlotWidget slot)) {
                continue;
            }
            int current = index++;
            EmiIngredient stack = slot.getStack();
            Bounds bounds = slot.getBounds();
            if (slot.getRecipe() == null && !stack.isEmpty() && missing.contains(current)) {
                graphics.fill(bounds.x(), bounds.y(), bounds.x() + bounds.width(), bounds.y() + bounds.height(), MISSING_COLOR);
            }
        }
    }
}
