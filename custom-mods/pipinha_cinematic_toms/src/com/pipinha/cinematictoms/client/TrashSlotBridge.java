package com.pipinha.cinematictoms.client;

import net.blay09.mods.balm.api.Balm;
import net.blay09.mods.trashslot.client.TrashSlotGuiHandler;
import net.blay09.mods.trashslot.config.TrashSlotConfig;
import net.blay09.mods.trashslot.network.MessageTrashSlotClick;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.core.registries.BuiltInRegistries;

/**
 * All direct references to TrashSlot classes live here. Only load this class when
 * ModList reports "trashslot" as loaded, so the addon still runs without TrashSlot.
 */
final class TrashSlotBridge {
    static final int SIZE = 18;
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath("trashslot", "textures/gui/slot.png");
    private static final int TEXTURE_V = 56;
    /** TrashSlot's LONE style: a 28x28 frame with the 16x16 item area inset by 6. */
    static final int FRAME = 28;
    static final int FRAME_INSET = 6;

    private TrashSlotBridge() {
    }

    static ItemStack shownItem() {
        return TrashSlotGuiHandler.getTrashSlot().getItem();
    }

    static boolean isDenied(ItemStack stack) {
        ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
        return id != null && TrashSlotConfig.getActive().deletionDenyList.contains(id.toString());
    }

    /** Mirrors TrashSlot's DefaultDeletionProvider.deleteMouseItem: right click trashes one item. */
    static void deleteCarried(Player player, boolean right) {
        AbstractContainerMenu menu = player.containerMenu;
        ItemStack original = menu.getCarried();
        ItemStack remaining = original.copy();
        ItemStack trash = right ? remaining.split(1) : remaining;
        menu.setCarried(right ? remaining : ItemStack.EMPTY);
        TrashSlotGuiHandler.getTrashSlot().set(trash);
        Balm.getNetworking().sendToServer(new MessageTrashSlotClick(original, right));
    }

    /** Mirrors TrashSlot's DefaultDeletionProvider.undeleteLast: takes the trashed item back to the hand. */
    static void undeleteLast(Player player, boolean right) {
        ItemStack trash = shownItem().copy();
        if (trash.isEmpty()) {
            return;
        }
        ItemStack taken = right ? trash.split(1) : trash;
        player.containerMenu.setCarried(taken);
        TrashSlotGuiHandler.getTrashSlot().set(right ? trash : ItemStack.EMPTY);
        Balm.getNetworking().sendToServer(new MessageTrashSlotClick(ItemStack.EMPTY, right));
    }

    static void renderSlot(GuiGraphics graphics, int x, int y) {
        int u = TrashSlotConfig.getDeletionProvider().canUndeleteLast() ? 0 : 64;
        graphics.blit(TEXTURE, x + 1 - FRAME_INSET, y + 1 - FRAME_INSET, u, TEXTURE_V, FRAME, FRAME);
        ItemStack shown = shownItem();
        if (!shown.isEmpty()) {
            graphics.renderItem(shown, x + 1, y + 1);
            graphics.renderItemDecorations(net.minecraft.client.Minecraft.getInstance().font, shown, x + 1, y + 1);
        }
    }
}
