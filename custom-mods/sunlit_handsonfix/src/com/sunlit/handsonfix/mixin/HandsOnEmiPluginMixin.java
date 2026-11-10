package com.sunlit.handsonfix.mixin;

import java.util.Set;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

// HandsOnEmiPlugin hides the crafting recipes of its board dishes with
// removeRecipes(r -> r.getCategory() == CRAFTING && ids.contains(r.getId())).
// ids is an immutable Set, whose contains(null) throws, and other mods register crafting
// recipes without an id. The throw aborted the whole EMI reload, so EMI showed nothing
// anywhere (inventory, Tom's terminal scene). A null id is simply not one of the dishes.
@Pseudo
@Mixin(targets = "com.pockyl.handson_delight.compat.emi.HandsOnEmiPlugin", remap = false)
public abstract class HandsOnEmiPluginMixin {
    @Redirect(method = "lambda$register$0", at = @At(value = "INVOKE", target = "Ljava/util/Set;contains(Ljava/lang/Object;)Z"))
    private static boolean sunlit$containsNullSafe(Set<?> ids, Object id) {
        return id != null && ids.contains(id);
    }
}
