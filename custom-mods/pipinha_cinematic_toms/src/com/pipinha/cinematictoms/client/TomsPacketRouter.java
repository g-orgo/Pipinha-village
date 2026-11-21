package com.pipinha.cinematictoms.client;

import com.mojang.logging.LogUtils;
import com.tom.storagemod.menu.StorageTerminalMenu;
import com.tom.storagemod.util.IDataReceiver;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.nbt.CompoundTag;
import org.slf4j.Logger;

public final class TomsPacketRouter {
    private static final Logger LOGGER = LogUtils.getLogger();

    private TomsPacketRouter() {
    }

    // Runs on the client main thread, queued before Tom's own handler.
    // When the open screen is an IDataReceiver, Tom's handler delivers the packet itself.
    public static void route(CompoundTag tag) {
        Minecraft mc = Minecraft.getInstance();
        Screen screen = mc.screen;
        if (screen instanceof IDataReceiver) {
            return;
        }
        LocalPlayer player = mc.player;
        if (player == null || !(player.containerMenu instanceof StorageTerminalMenu menu)) {
            return;
        }
        // The only Tom's screen that set onPacket is an orphan, since the current screen is not Tom's.
        menu.onPacket = null;
        menu.receiveClientNBTPacket(tag);
        LOGGER.info("[CinematicToms] routed terminal packet (screen={}, items={})",
                screen == null ? "-" : screen.getClass().getSimpleName(), menu.sync.getAsList().size());
    }
}
