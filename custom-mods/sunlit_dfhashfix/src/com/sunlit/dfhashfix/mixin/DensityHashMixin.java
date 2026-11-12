package com.sunlit.dfhashfix.mixin;

import java.util.concurrent.ConcurrentMap;

import com.google.common.collect.MapMaker;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Density functions are immutable records whose hashCode walks the whole function graph on every call.
 * Lithosphere's graph is huge and heavily shared, so the hash maps that wire a NoiseChunk spend minutes
 * re-hashing the same subtrees (seen in a thread dump: Worker-Main stuck in DensityFunctions hashCode).
 * The hash of an immutable record never changes, so it is memoized per instance (weak identity keys).
 */
@Mixin(targets = {
    "net.minecraft.world.level.levelgen.DensityFunctions$Ap2",
    "net.minecraft.world.level.levelgen.DensityFunctions$BlendDensity",
    "net.minecraft.world.level.levelgen.DensityFunctions$Clamp",
    "net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder",
    "net.minecraft.world.level.levelgen.DensityFunctions$Mapped",
    "net.minecraft.world.level.levelgen.DensityFunctions$Marker",
    "net.minecraft.world.level.levelgen.DensityFunctions$MulOrAdd",
    "net.minecraft.world.level.levelgen.DensityFunctions$Noise",
    "net.minecraft.world.level.levelgen.DensityFunctions$RangeChoice",
    "net.minecraft.world.level.levelgen.DensityFunctions$ShiftA",
    "net.minecraft.world.level.levelgen.DensityFunctions$ShiftB",
    "net.minecraft.world.level.levelgen.DensityFunctions$Shift",
    "net.minecraft.world.level.levelgen.DensityFunctions$ShiftedNoise",
    "net.minecraft.world.level.levelgen.DensityFunctions$Spline",
    "net.minecraft.world.level.levelgen.DensityFunctions$WeirdScaledSampler",
    "net.minecraft.world.level.levelgen.DensityFunction$NoiseHolder",
    "net.minecraft.util.CubicSpline$Multipoint",
    "net.minecraft.core.Holder$Direct"
}, remap = false)
public abstract class DensityHashMixin {
    @Unique
    private static final ConcurrentMap<Object, Integer> SUNLIT$HASHES = new MapMaker().weakKeys().concurrencyLevel(16).makeMap();

    @Inject(method = "hashCode", at = @At("HEAD"), cancellable = true, remap = false)
    private void sunlit$cachedHash(CallbackInfoReturnable<Integer> cir) {
        Integer h = SUNLIT$HASHES.get(this);
        if (h != null) cir.setReturnValue(h);
    }

    @Inject(method = "hashCode", at = @At("RETURN"), remap = false)
    private void sunlit$storeHash(CallbackInfoReturnable<Integer> cir) {
        SUNLIT$HASHES.putIfAbsent(this, cir.getReturnValue());
    }
}
