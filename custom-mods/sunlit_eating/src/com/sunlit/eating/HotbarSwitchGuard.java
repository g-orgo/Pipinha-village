package com.sunlit.eating;

import net.minecraft.client.Minecraft;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.EventPriority;
import org.toame.food.utils.AnimationUtils;

// Immersive Eating locks the hotbar while its eat animation plays, so a scroll is swallowed.
// A left click cancels that animation through the addon, so a scroll does the same. The event is
// not cancelled: the addon's own handler then sees the unlocked state and vanilla scrolls the hotbar.
final class HotbarSwitchGuard {
    private HotbarSwitchGuard() {
    }

    static void init() {
        MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGHEST, false, InputEvent.MouseScrollingEvent.class,
                HotbarSwitchGuard::onMouseScroll);
    }

    private static void onMouseScroll(InputEvent.MouseScrollingEvent event) {
        if (Minecraft.m_91087_().f_91080_ == null && AnimationUtils.isAnimationLocked()) {
            AnimationUtils.stopAnimationControl();
        }
    }
}
