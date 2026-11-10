package com.sunlit.clockfix.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

// GameTimeComponent passes (dayTime % 24000) / 1000 + 6 as the hour, which never wraps,
// so from midnight to 6 AM the 12-hour clock reads 12 PM to 17 PM. The real-time clock
// shares this formatter with hours 0-23, so wrapping here only changes the game clock.
@Mixin(targets = "dev.ftb.mods.ftbchunks.client.minimap.components.RealTimeComponent", remap = false)
public abstract class RealTimeComponentMixin {
    @ModifyVariable(method = "createTimeString(IIZ)Ljava/lang/String;", at = @At("HEAD"), argsOnly = true, ordinal = 0, remap = false)
    private static int sunlit_clockfix$wrapHour(int hour) {
        return hour % 24;
    }
}
