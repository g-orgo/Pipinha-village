package com.pipinha.cinematictoms.mixin;

import dev.dyslexic.cinematic.client.Scene;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(value = Scene.class, remap = false)
public interface SceneAccessor {
    // Marks the next screen as a consultation, so the scene holds while EMI's recipe page is open.
    @Accessor("consulting")
    static void cinematicToms$setConsulting(boolean consulting) {
        throw new AssertionError();
    }
}
