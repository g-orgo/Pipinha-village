package com.pipinha.skilltoast.mixin;

import com.github.spacemex.client.XpToast;
import net.minecraft.client.resources.language.I18n;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * SkillExpNotifier builds the XP toast title from the raw category path (for example "catador")
 * with formatCategoryName, which only capitalizes the words. This injection returns the translated
 * Puffish skill tree title from the society_skills.<id>.category.title lang key when it exists,
 * and leaves the original result for any other category.
 */
@Mixin(value = XpToast.class, remap = false)
public abstract class XpToastMixin {

    @Inject(method = "formatCategoryName(Ljava/lang/String;)Ljava/lang/String;", at = @At("HEAD"), cancellable = true)
    private static void pipinha$translateCategoryName(String categoryId, CallbackInfoReturnable<String> cir) {
        if (categoryId == null) {
            return;
        }
        String path = categoryId.substring(categoryId.lastIndexOf(':') + 1);
        String key = "society_skills." + path + ".category.title";
        if (I18n.exists(key)) {
            cir.setReturnValue(I18n.get(key));
        }
    }
}
