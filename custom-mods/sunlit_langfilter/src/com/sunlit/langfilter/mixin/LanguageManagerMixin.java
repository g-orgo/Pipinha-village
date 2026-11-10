package com.sunlit.langfilter.mixin;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import net.minecraft.client.resources.language.LanguageInfo;
import net.minecraft.client.resources.language.LanguageManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

// The language list is rebuilt from every resource pack's metadata on each reload
// (extractLanguages). Dropping everything except en_us and pt_br there removes the other
// languages from the selection screen; a saved selection outside the list falls back to en_us.
@Mixin(value = LanguageManager.class, remap = false)
public abstract class LanguageManagerMixin {
    @Unique
    private static final Set<String> SUNLIT_ALLOWED = Set.of("en_us", "pt_br");

    @Inject(method = "m_118981_", at = @At("RETURN"), cancellable = true, remap = false)
    private static void sunlit_langfilter$keepAllowed(CallbackInfoReturnable<Map<String, LanguageInfo>> cir) {
        Map<String, LanguageInfo> filtered = new LinkedHashMap<>();
        cir.getReturnValue().forEach((code, info) -> {
            if (SUNLIT_ALLOWED.contains(code)) {
                filtered.put(code, info);
            }
        });
        cir.setReturnValue(filtered);
    }
}
