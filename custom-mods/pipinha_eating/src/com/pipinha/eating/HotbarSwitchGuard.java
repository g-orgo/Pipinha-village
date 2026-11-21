package com.pipinha.eating;

import io.github.memorytoame.immersiveeating.neoforge.utils.AnimationUtils;
import net.minecraft.client.Minecraft;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.common.NeoForge;

// Immersive Eating locks the hotbar while its eat animation plays, so a scroll is swallowed.
// A left click cancels that animation through the addon, so a scroll does the same. The event is
// not cancelled: the addon's own handler then sees the unlocked state and vanilla scrolls the hotbar.
final class HotbarSwitchGuard {
    private HotbarSwitchGuard() {
    }

    static void init() {
        NeoForge.EVENT_BUS.addListener(EventPriority.HIGHEST, false, InputEvent.MouseScrollingEvent.class,
                HotbarSwitchGuard::onMouseScroll);
    }

    private static void onMouseScroll(InputEvent.MouseScrollingEvent event) {
        if (Minecraft.getInstance().screen == null && AnimationUtils.isAnimationLocked()) {
            AnimationUtils.stopAnimationControl();
        }
    }
}
