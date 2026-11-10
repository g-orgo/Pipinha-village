package com.sunlit.texturefix.mixin;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.resources.ResourceLocation;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// Puffish Skills registers its skill tree backgrounds on the Netty thread while reading the
// category packet. TextureManager is not thread safe, so this races with its tick on the
// render thread and crashes the client with a ConcurrentModificationException right after
// joining a world. Registrations from any other thread now run on the render thread.
@Mixin(value = TextureManager.class, remap = false)
public abstract class TextureManagerMixin {
    @Unique
    private static final Logger SUNLIT_LOGGER = LogManager.getLogger("sunlit_texturefix");

    @Inject(method = "m_118495_", at = @At("HEAD"), cancellable = true, remap = false)
    private void sunlit_texturefix$deferToRenderThread(ResourceLocation id, AbstractTexture texture, CallbackInfo ci) {
        Minecraft minecraft = Minecraft.m_91087_();
        if (minecraft == null || RenderSystem.isOnRenderThread()) {
            return;
        }
        TextureManager self = (TextureManager) (Object) this;
        minecraft.execute(() -> {
            SUNLIT_LOGGER.debug("Registering deferred texture {}", id);
            self.m_118495_(id, texture);
        });
        ci.cancel();
    }
}
