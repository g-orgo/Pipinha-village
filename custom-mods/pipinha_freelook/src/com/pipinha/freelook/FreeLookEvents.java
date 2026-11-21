package com.pipinha.freelook;

import com.pipinha.freelook.compat.SsCompat;
import net.minecraft.client.Camera;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.event.RenderLivingEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Game event listeners for the free look camera, crosshair and head turn. Client only. */
public class FreeLookEvents {

    private static final float DEFAULT_FOV = 70F;
    private static final float HEAD_YAW_LIMIT = 70F;
    private static final float HEAD_PITCH_LIMIT = 60F;
    private static final float MIN_DEPTH = 0.1F;

    private float lastFov = DEFAULT_FOV;
    private boolean crosshairPushed;

    private boolean headSaved;
    private LivingEntity headEntity;
    private float savedYHeadRot;
    private float savedYHeadRotO;
    private float savedXRot;
    private float savedXRotO;

    /** Moves the camera by the free look offsets, or snaps them back to zero when inactive. */
    @SubscribeEvent
    public void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        if (!FreeLookState.refresh()) {
            return;
        }
        event.setYaw(event.getYaw() + FreeLookState.getOffsetYaw());
        event.setPitch(Mth.clamp(event.getPitch() + FreeLookState.getOffsetPitch(), -90F, 90F));
    }

    /** Remembers the FOV used by the world projection, so the crosshair can be placed with it. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onComputeFov(ViewportEvent.ComputeFov event) {
        if (event.usedConfiguredFov()) {
            lastFov = (float) event.getFOV();
        }
    }

    /** Moves the crosshair to the original aim while the camera is offset. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onGuiLayerPre(RenderGuiLayerEvent.Pre event) {
        crosshairPushed = false;
        if (!VanillaGuiLayers.CROSSHAIR.equals(event.getName())) {
            return;
        }
        if (!FreeLookState.isActive() || !FreeLookState.hasOffset()) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null) {
            return;
        }
        float partialTick = event.getPartialTick().getGameTimeDeltaPartialTick(false);
        Vec3 view = player.getViewVector(partialTick);
        Vector3f aim = new Vector3f((float) view.x, (float) view.y, (float) view.z);
        Camera camera = mc.gameRenderer.getMainCamera();
        Vector3f local = new Quaternionf(camera.rotation()).conjugate().transform(aim);

        float depth = -local.z;
        if (depth < MIN_DEPTH) {
            event.setCanceled(true);
            return;
        }
        GuiGraphics guiGraphics = event.getGuiGraphics();
        float scale = (guiGraphics.guiHeight() / 2F) / (float) Math.tan(Math.toRadians(lastFov) / 2D);
        float dx = local.x / depth * scale;
        float dy = -local.y / depth * scale;
        guiGraphics.pose().pushPose();
        guiGraphics.pose().translate(dx, dy, 0F);
        crosshairPushed = true;
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onGuiLayerPost(RenderGuiLayerEvent.Post event) {
        if (crosshairPushed && VanillaGuiLayers.CROSSHAIR.equals(event.getName())) {
            event.getGuiGraphics().pose().popPose();
        }
        crosshairPushed = false;
    }

    /** Turns the player model's head toward the camera in third person while free looking. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onLivingPre(RenderLivingEvent.Pre<?, ?> event) {
        restoreHead();
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || event.getEntity() != player) {
            return;
        }
        boolean shoulderFreeLook = SsCompat.isLoaded() && SsCompat.isFreeLooking() && FreeLookState.isMounted();
        if (!FreeLookState.isActive() && !shoulderFreeLook) {
            return;
        }
        Camera camera = mc.gameRenderer.getMainCamera();
        float headYaw = player.getYRot()
                + Mth.clamp(Mth.wrapDegrees(camera.getYRot() - player.getYRot()), -HEAD_YAW_LIMIT, HEAD_YAW_LIMIT);
        float headPitch = Mth.clamp(camera.getXRot(), -HEAD_PITCH_LIMIT, HEAD_PITCH_LIMIT);

        headEntity = player;
        savedYHeadRot = player.yHeadRot;
        savedYHeadRotO = player.yHeadRotO;
        savedXRot = player.getXRot();
        savedXRotO = player.xRotO;
        headSaved = true;

        player.yHeadRot = headYaw;
        player.yHeadRotO = headYaw;
        player.setXRot(headPitch);
        player.xRotO = headPitch;
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onLivingPost(RenderLivingEvent.Post<?, ?> event) {
        restoreHead();
    }

    /** Safety net: the player's real head and pitch must never stay changed across a tick. */
    @SubscribeEvent
    public void onClientTickPre(ClientTickEvent.Pre event) {
        restoreHead();
    }

    /** Restores the player's real head and pitch values saved by onLivingPre. */
    private void restoreHead() {
        if (!headSaved) {
            return;
        }
        headEntity.yHeadRot = savedYHeadRot;
        headEntity.yHeadRotO = savedYHeadRotO;
        headEntity.setXRot(savedXRot);
        headEntity.xRotO = savedXRotO;
        headSaved = false;
        headEntity = null;
    }
}
