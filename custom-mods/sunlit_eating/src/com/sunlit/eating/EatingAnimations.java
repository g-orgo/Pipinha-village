package com.sunlit.eating;

import dev.kosmx.playerAnim.api.layered.IAnimation;
import dev.kosmx.playerAnim.api.layered.KeyframeAnimationPlayer;
import dev.kosmx.playerAnim.api.layered.ModifierLayer;
import dev.kosmx.playerAnim.api.layered.modifier.AbstractFadeModifier;
import dev.kosmx.playerAnim.api.layered.modifier.AdjustmentModifier;
import dev.kosmx.playerAnim.api.layered.modifier.MirrorModifier;
import dev.kosmx.playerAnim.api.layered.modifier.SpeedModifier;
import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import dev.kosmx.playerAnim.core.util.Ease;
import dev.kosmx.playerAnim.core.util.Vec3f;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationFactory;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;
import java.util.Map;
import java.util.Optional;
import java.util.WeakHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.BowlFoodItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.registries.ForgeRegistries;

// Plays a body animation while a player eats or drinks. Item use is already synced, so the same
// code covers the local player and the others around, with nothing sent over the network.
//
// Fresh Moves animates the player through EMF and rewrites body and legs, but keeps reading the
// rotation of arms and head from the model, so the animations only rotate those parts.
final class EatingAnimations {
    private static final ResourceLocation LAYER = new ResourceLocation("sunlit_eating", "eating");
    private static final int LAYER_PRIORITY = 1000;
    private static final int FADE_TICKS = 4;
    // Use time of a regular food in this pack. A faster food plays the same motion faster.
    private static final float REFERENCE_USE_TICKS = 38.0F;
    private static final float DEGREES = (float) (Math.PI / 180.0);

    private static final Map<AbstractClientPlayer, Item> ACTIVE = new WeakHashMap<>();

    private EatingAnimations() {
    }

    static void init() {
        PlayerAnimationFactory.ANIMATION_DATA_FACTORY.registerFactory(LAYER, LAYER_PRIORITY,
                player -> new ModifierLayer<IAnimation>());
        MinecraftForge.EVENT_BUS.addListener(EatingAnimations::onClientTick);
    }

    private static void onClientTick(TickEvent.ClientTickEvent event) {
        Minecraft minecraft = Minecraft.m_91087_();
        if (event.phase != TickEvent.Phase.END || minecraft.f_91073_ == null) {
            return;
        }
        for (AbstractClientPlayer player : minecraft.f_91073_.m_6907_()) {
            update(player);
        }
    }

    private static void update(AbstractClientPlayer player) {
        ItemStack stack = player.m_6117_() ? player.m_21211_() : ItemStack.f_41583_;
        boolean consuming = !stack.m_41619_()
                && (stack.m_41780_() == UseAnim.EAT || stack.m_41780_() == UseAnim.DRINK);
        Item current = ACTIVE.get(player);
        if (consuming && current != stack.m_41720_()) {
            if (start(player, stack)) {
                ACTIVE.put(player, stack.m_41720_());
            }
        } else if (!consuming && current != null) {
            stop(player);
            ACTIVE.remove(player);
        }
    }

    private static FoodPose poseOf(ItemStack stack) {
        Item item = stack.m_41720_();
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(item);
        Item left = item.m_41469_();
        ResourceLocation leftId = left == null ? null : ForgeRegistries.ITEMS.getKey(left);
        return FoodPose.classify(id == null ? "" : id.m_135815_(), leftId == null ? "" : leftId.toString(),
                stack.m_41780_() == UseAnim.DRINK, item instanceof BowlFoodItem
                        || item.getClass().getSimpleName().startsWith("BowlFood"));
    }

    private static boolean start(AbstractClientPlayer player, ItemStack stack) {
        FoodPose pose = poseOf(stack);
        KeyframeAnimation data = PlayerAnimationRegistry.getAnimation(
                new ResourceLocation("sunlit_eating", pose.animationName()));
        ModifierLayer<IAnimation> layer = layerOf(player);
        if (data == null || layer == null) {
            return false;
        }
        int useTicks = stack.m_41779_();
        float speed = useTicks <= 0 ? 1.0F : Math.max(0.5F, Math.min(3.0F, REFERENCE_USE_TICKS / useTicks));
        boolean offhandSide = (player.m_7655_() == InteractionHand.MAIN_HAND)
                == (player.m_5737_() == HumanoidArm.LEFT);
        // Added one by one: the varargs constructor of this library version does not link the chain.
        ModifierLayer<IAnimation> motion = new ModifierLayer<>(new KeyframeAnimationPlayer(data));
        motion.addModifierLast(new SpeedModifier(speed));
        motion.addModifierLast(new AdjustmentModifier(part -> adjust(player, pose, part)));
        if (offhandSide) {
            motion.addModifierLast(new MirrorModifier(true));
        }
        layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(FADE_TICKS, Ease.INOUTSINE), motion, true);
        return true;
    }

    private static void stop(AbstractClientPlayer player) {
        ModifierLayer<IAnimation> layer = layerOf(player);
        if (layer != null) {
            layer.replaceAnimationWithFade(AbstractFadeModifier.standardFadeIn(FADE_TICKS, Ease.INOUTSINE), null);
        }
    }

    @SuppressWarnings("unchecked")
    private static ModifierLayer<IAnimation> layerOf(AbstractClientPlayer player) {
        IAnimation layer = PlayerAnimationAccess.getPlayerAssociatedData(player).get(LAYER);
        return layer instanceof ModifierLayer<?> ? (ModifierLayer<IAnimation>) layer : null;
    }

    // Arms follow where the player is looking, so the food stays near the mouth. The head keeps
    // its own direction and only gets a small motion on top: chewing, or tilting back to drink.
    private static Optional<AdjustmentModifier.PartModifier> adjust(AbstractClientPlayer player, FoodPose pose, String part) {
        float partial = Minecraft.m_91087_().m_91296_();
        float look = player.m_5686_(partial) * DEGREES;
        if (part.equals("rightArm") || part.equals("leftArm")) {
            return Optional.of(new AdjustmentModifier.PartModifier(new Vec3f(look * 0.8F, 0.0F, 0.0F), new Vec3f(0.0F, 0.0F, 0.0F)));
        }
        if (part.equals("head")) {
            float pitch = pose.isDrink() ? -14.0F * DEGREES
                    : (float) Math.sin((player.f_19797_ + partial) * 1.1F) * 3.5F * DEGREES;
            return Optional.of(new AdjustmentModifier.PartModifier(new Vec3f(pitch, 0.0F, 0.0F), new Vec3f(0.0F, 0.0F, 0.0F)));
        }
        return Optional.empty();
    }
}
