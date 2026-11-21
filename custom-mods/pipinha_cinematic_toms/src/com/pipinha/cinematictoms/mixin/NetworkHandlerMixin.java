package com.pipinha.cinematictoms.mixin;

import com.tom.storagemod.network.DataPacket;
import com.tom.storagemod.network.NetworkHandler;
import com.pipinha.cinematictoms.client.TomsPacketRouter;
import net.minecraft.network.protocol.PacketFlow;
import net.neoforged.neoforge.network.handling.IPayloadContext;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(value = NetworkHandler.class, remap = false)
public abstract class NetworkHandlerMixin {
    // Tom's client handler only delivers the packet when the open screen is an IDataReceiver.
    // Enqueued before Tom's own work, so the terminal menu gets the packet even when another screen is open.
    @Inject(method = "handleDataClient(Lcom/tom/storagemod/network/DataPacket;Lnet/neoforged/neoforge/network/handling/IPayloadContext;)V", at = @At("HEAD"))
    private static void routeTerminalPacket(DataPacket packet, IPayloadContext ctx, CallbackInfo ci) {
        if (ctx.flow() != PacketFlow.CLIENTBOUND) {
            return;
        }
        var tag = packet.tag();
        ctx.enqueueWork(() -> TomsPacketRouter.route(tag));
    }
}
