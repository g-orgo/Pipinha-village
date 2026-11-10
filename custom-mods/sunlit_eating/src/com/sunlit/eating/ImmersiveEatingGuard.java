package com.sunlit.eating;

import java.lang.reflect.Field;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import org.toame.food.additions.Empty;
import org.toame.food.init.ModItems;
import org.toame.food.utils.AnimationUtils;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

// Immersive Eating refuses every right click while a switch animation is playing, and only advances
// those animations while its first person model is drawn. One started in third person, or left
// behind by a model without that animation, stays "playing" forever and no food can be eaten in
// first person until the game restarts. The same goes for a lock left without an eat animation.
final class ImmersiveEatingGuard {
    private static final String[] SWITCH_CONTROLLERS = {"switchin", "switchout"};
    // The longest switch animation of the addon takes 1.5 s.
    private static final int SWITCH_LIMIT_TICKS = 40;
    private static final int LOCK_LIMIT_TICKS = 40;

    private static final Map<String, Integer> SWITCH_TICKS = new HashMap<>();
    private static int lockTicks;

    private ImmersiveEatingGuard() {
    }

    static void init() {
        MinecraftForge.EVENT_BUS.addListener(ImmersiveEatingGuard::onClientTick);
    }

    private static void onClientTick(TickEvent.ClientTickEvent event) {
        Minecraft minecraft = Minecraft.m_91087_();
        if (event.phase != TickEvent.Phase.END || minecraft.f_91074_ == null) {
            return;
        }
        boolean locked = AnimationUtils.isAnimationLocked();
        lockTicks = locked && !Empty.isEatAnimationPlaying() ? lockTicks + 1 : 0;
        if (lockTicks > LOCK_LIMIT_TICKS) {
            AnimationUtils.clearAnimationState();
            lockTicks = 0;
        }
        if (locked) {
            return;
        }
        boolean firstPerson = minecraft.f_91066_.m_92176_().m_90612_();
        AnimatableManager<?> manager = ModItems.EMPTY.get().getAnimatableInstanceCache()
                .getManagerForId(AnimationUtils.getAnimationControllerId(minecraft));
        for (String name : SWITCH_CONTROLLERS) {
            AnimationController<?> controller = manager.getAnimationControllers().get(name);
            boolean playing = controller != null && controller.isPlayingTriggeredAnimation();
            int ticks = playing ? SWITCH_TICKS.getOrDefault(name, 0) + 1 : 0;
            if (playing && (!firstPerson || ticks > SWITCH_LIMIT_TICKS)) {
                clear(controller);
                ticks = 0;
            }
            SWITCH_TICKS.put(name, ticks);
        }
    }

    // stop() alone keeps the triggered animation, which a later switch then fails to replace.
    private static void clear(AnimationController<?> controller) {
        controller.stop();
        controller.forceAnimationReset();
        try {
            Field triggered = AnimationController.class.getDeclaredField("triggeredAnimation");
            triggered.setAccessible(true);
            triggered.set(controller, (RawAnimation) null);
        } catch (ReflectiveOperationException | RuntimeException ignored) {
            // The stop above is still the best that can be done on another GeckoLib version.
        }
    }
}
