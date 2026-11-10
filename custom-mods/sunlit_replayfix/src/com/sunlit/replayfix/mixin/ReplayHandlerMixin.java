package com.sunlit.replayfix.mixin;

import com.replaymod.replay.ReplayHandler;
import com.replaymod.replaystudio.replay.ReplayFile;
import com.sunlit.replayfix.ReplayRegistryLoader;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

// setup() runs when a replay opens and again after every restart (jumping back in time).
// A restart clears the level first, which makes Forge revert the registries, so the world
// IDs have to be loaded on each setup and not only once.
@Mixin(value = ReplayHandler.class, remap = false)
public abstract class ReplayHandlerMixin {
    @Shadow(remap = false)
    @Final
    private ReplayFile replayFile;

    @Inject(method = "setup", at = @At("HEAD"), remap = false)
    private void sunlit_replayfix$loadWorldRegistries(CallbackInfo ci) {
        ReplayRegistryLoader.loadFor(this.replayFile);
    }

    @Inject(method = "endReplay", at = @At("RETURN"), remap = false)
    private void sunlit_replayfix$restoreRegistries(CallbackInfo ci) {
        ReplayRegistryLoader.restore();
    }
}
