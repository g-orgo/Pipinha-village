package com.pipinha.freelook;

import com.pipinha.freelook.compat.SsCompat;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;

/**
 * Shared free look state. The player's real rotation is never changed while free looking;
 * the difference between the camera and the real aim is kept in offsetYaw and offsetPitch.
 */
public final class FreeLookState {

    /** Mouse delta to degrees factor used by Entity.turn. */
    private static final float TURN_FACTOR = 0.15F;
    private static final float MAX_YAW = 150F;
    private static final float MAX_PITCH = 90F;

    private static float offsetYaw;
    private static float offsetPitch;

    private FreeLookState() {
    }

    /** True when the local player is riding a living entity (horses, camels, pigs, striders, modded mounts). */
    public static boolean isMounted() {
        LocalPlayer player = Minecraft.getInstance().player;
        return player != null && player.getVehicle() instanceof LivingEntity;
    }

    /** True when our free look is active: key held, mounted, no screen, and not in Shoulder Surfing shoulder view. */
    public static boolean isActive() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.screen != null) {
            return false;
        }
        if (!isMounted() || !FreeLookKeys.FREE_LOOK.isDown()) {
            return false;
        }
        return !SsCompat.isShoulderSurfing();
    }

    /** Resets the offsets when free look is not active, so the camera snaps back in the same frame. */
    public static boolean refresh() {
        boolean active = isActive();
        if (!active) {
            reset();
        }
        return active;
    }

    /** Applies a mouse turn to the offsets instead of the player's real rotation. */
    public static void turn(double yRot, double xRot) {
        LocalPlayer player = Minecraft.getInstance().player;
        offsetYaw = Mth.clamp(offsetYaw + (float) yRot * TURN_FACTOR, -MAX_YAW, MAX_YAW);
        float realPitch = player.getXRot();
        float targetPitch = Mth.clamp(realPitch + offsetPitch + (float) xRot * TURN_FACTOR, -MAX_PITCH, MAX_PITCH);
        offsetPitch = targetPitch - realPitch;
    }

    public static float getOffsetYaw() {
        return offsetYaw;
    }

    public static float getOffsetPitch() {
        return offsetPitch;
    }

    public static boolean hasOffset() {
        return offsetYaw != 0F || offsetPitch != 0F;
    }

    public static void reset() {
        offsetYaw = 0F;
        offsetPitch = 0F;
    }
}
