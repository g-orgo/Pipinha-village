package com.sunlit.dfhashfix.mixin;

import java.util.IdentityHashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentMap;

import com.google.common.collect.MapMaker;
import net.minecraft.world.level.levelgen.DensityFunction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * DensityFunctions.HolderHolder.mapAll re-maps the referenced function on every occurrence. A graph that
 * references the same functions many times (Lithosphere) turns every NoiseChunk into an exponential walk;
 * jigsaw structures ask for terrain height piece by piece, so structure starts on land took minutes.
 * Within one visitor pass the same reference always maps to an equal result (the visitors memoize by
 * equality), so the first result is reused for that reference: same values, linear time.
 */
@Mixin(targets = "net.minecraft.world.level.levelgen.DensityFunctions$HolderHolder", remap = false)
public abstract class HolderMapAllMixin {
    @Unique
    private static final ConcurrentMap<Object, Map<Object, DensityFunction>> SUNLIT$PASSES = new MapMaker().weakKeys().concurrencyLevel(16).makeMap();

    @Unique
    private static Map<Object, DensityFunction> sunlit$pass(DensityFunction.Visitor visitor) {
        return SUNLIT$PASSES.computeIfAbsent(visitor, v -> new IdentityHashMap<>());
    }

    @Inject(method = "m_207456_(Lnet/minecraft/world/level/levelgen/DensityFunction$Visitor;)Lnet/minecraft/world/level/levelgen/DensityFunction;",
            at = @At("HEAD"), cancellable = true, remap = false)
    private void sunlit$reuse(DensityFunction.Visitor visitor, CallbackInfoReturnable<DensityFunction> cir) {
        Map<Object, DensityFunction> pass = sunlit$pass(visitor);
        DensityFunction done;
        synchronized (pass) {
            done = pass.get(this);
        }
        if (done != null) cir.setReturnValue(done);
    }

    @Inject(method = "m_207456_(Lnet/minecraft/world/level/levelgen/DensityFunction$Visitor;)Lnet/minecraft/world/level/levelgen/DensityFunction;",
            at = @At("RETURN"), remap = false)
    private void sunlit$remember(DensityFunction.Visitor visitor, CallbackInfoReturnable<DensityFunction> cir) {
        Map<Object, DensityFunction> pass = sunlit$pass(visitor);
        synchronized (pass) {
            pass.putIfAbsent(this, cir.getReturnValue());
        }
    }
}
