package com.pipinha.skinfix.mixin;

import java.util.UUID;

import com.mojang.authlib.minecraft.MinecraftSessionService;
import com.mojang.authlib.yggdrasil.ProfileResult;
import com.pipinha.skinfix.SkinFix;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * lambda$new$1 is the supplier given to profileFuture in the Minecraft constructor (runtime is Mojang-named;
 * the name was checked in the 1.21.1 client jar and in a runtime stack trace). Its only call is
 * MinecraftSessionService.fetchProfile(UUID, true), redirected here to the retrying fetch.
 */
@Mixin(value = Minecraft.class, remap = false)
public abstract class MinecraftProfileRetryMixin {
    @Redirect(method = "lambda$new$1", at = @At(value = "INVOKE",
            target = "Lcom/mojang/authlib/minecraft/MinecraftSessionService;fetchProfile(Ljava/util/UUID;Z)Lcom/mojang/authlib/yggdrasil/ProfileResult;"))
    private ProfileResult pipinha$fetchProfileWithRetry(MinecraftSessionService service, UUID id, boolean requireSecure) {
        return SkinFix.fetchWithRetry(service, id, requireSecure);
    }
}
