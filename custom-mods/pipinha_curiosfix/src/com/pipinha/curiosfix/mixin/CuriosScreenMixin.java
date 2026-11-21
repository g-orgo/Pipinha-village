package com.pipinha.curiosfix.mixin;

import java.util.List;
import java.util.Optional;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.inventory.tooltip.TooltipComponent;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;
import top.theillusivec4.curios.client.gui.CuriosScreen;

/**
 * Curios draws its slot tooltip with the 4-argument GuiGraphics.renderTooltip overload (no ItemStack),
 * so NeoForge's RenderTooltipEvent.GatherComponents receives an empty stack and stack-based tooltip
 * components (Quark attributes, LSO hydration) are skipped. This redirect swaps that call for the
 * 6-argument overload, passing the stack of the hovered slot.
 */
@Mixin(value = CuriosScreen.class, remap = false)
public abstract class CuriosScreenMixin {

    @Redirect(
            method = "renderTooltip(Lnet/minecraft/client/gui/GuiGraphics;II)V",
            at = @At(
                    value = "INVOKE",
                    target = "Lnet/minecraft/client/gui/GuiGraphics;renderTooltip(Lnet/minecraft/client/gui/Font;Ljava/util/List;Ljava/util/Optional;II)V"))
    private void pipinha$renderTooltipWithStack(GuiGraphics graphics, Font font, List<Component> lines,
            Optional<TooltipComponent> image, int mouseX, int mouseY) {
        // hoveredSlot is declared in AbstractContainerScreen, so it cannot be shadowed here; use the public getter.
        Slot hovered = ((AbstractContainerScreen<?>) (Object) this).getSlotUnderMouse();
        ItemStack stack = hovered != null ? hovered.getItem() : ItemStack.EMPTY;
        graphics.renderTooltip(font, lines, image, stack, mouseX, mouseY);
    }
}
