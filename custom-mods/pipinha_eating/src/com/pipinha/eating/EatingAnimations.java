package com.pipinha.eating;

import net.minecraft.core.component.DataComponents;
import net.minecraft.world.food.FoodProperties;
import dev.kosmx.playerAnim.api.IPlayable;
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
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.common.NeoForge;

// Plays a body animation while a player eats or drinks. Item use is already synced, so the same
// code covers the local player and the others around, with nothing sent over the network.
//
// Fresh Moves animates the player through EMF and rewrites body and legs, but keeps reading the
// rotation of arms and head from the model, so the animations only rotate those parts.
final class EatingAnimations {
    private static final ResourceLocation LAYER = ResourceLocation.fromNamespaceAndPath("pipinha_eating", "eating");
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
        NeoForge.EVENT_BUS.addListener(EatingAnimations::onClientTick);
    }

    private static void onClientTick(ClientTickEvent.Post event) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.level == null) {
            return;
        }
        for (AbstractClientPlayer player : minecraft.level.players()) {
            update(player);
        }
    }

    private static void update(AbstractClientPlayer player) {
        ItemStack stack = player.isUsingItem() ? player.getUseItem() : ItemStack.EMPTY;
        boolean consuming = !stack.isEmpty()
                && (stack.getUseAnimation() == UseAnim.EAT || stack.getUseAnimation() == UseAnim.DRINK);
        Item current = ACTIVE.get(player);
        if (consuming && current != stack.getItem()) {
            if (start(player, stack)) {
                ACTIVE.put(player, stack.getItem());
            }
        } else if (!consuming && current != null) {
            stop(player);
            ACTIVE.remove(player);
        }
    }

    private static FoodPose poseOf(ItemStack stack) {
        Item item = stack.getItem();
        ResourceLocation id = BuiltInRegistries.ITEM.getKey(item);
        Item left = item.getCraftingRemainingItem();
        // Since 1.21 vanilla stews and soups no longer use a crafting remainder or BowlFoodItem: the
        // bowl comes back through the food component, so that item counts as the remainder too.
        if (left == null) {
            FoodProperties food = stack.get(DataComponents.FOOD);
            if (food != null && food.usingConvertsTo().isPresent()) {
                left = food.usingConvertsTo().get().getItem();
            }
        }
        ResourceLocation leftId = left == null ? null : BuiltInRegistries.ITEM.getKey(left);
        return FoodPose.classify(id == null ? "" : id.getPath(), leftId == null ? "" : leftId.toString(),
                stack.getUseAnimation() == UseAnim.DRINK, item.getClass().getSimpleName().startsWith("BowlFood"));
    }

    private static boolean start(AbstractClientPlayer player, ItemStack stack) {
        FoodPose pose = poseOf(stack);
        IPlayable playable = PlayerAnimationRegistry.getAnimation(
                ResourceLocation.fromNamespaceAndPath("pipinha_eating", pose.animationName()));
        KeyframeAnimation data = playable instanceof KeyframeAnimation keyframes ? keyframes : null;
        ModifierLayer<IAnimation> layer = layerOf(player);
        if (data == null || layer == null) {
            return false;
        }
        int useTicks = stack.getUseDuration(player);
        float speed = useTicks <= 0 ? 1.0F : Math.max(0.5F, Math.min(3.0F, REFERENCE_USE_TICKS / useTicks));
        boolean offhandSide = (player.getUsedItemHand() == InteractionHand.MAIN_HAND)
                == (player.getMainArm() == HumanoidArm.LEFT);
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
        float partial = Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(false);
        float look = player.getViewXRot(partial) * DEGREES;
        if (part.equals("rightArm") || part.equals("leftArm")) {
            return Optional.of(new AdjustmentModifier.PartModifier(new Vec3f(look * 0.8F, 0.0F, 0.0F), new Vec3f(0.0F, 0.0F, 0.0F)));
        }
        if (part.equals("head")) {
            float pitch = pose.isDrink() ? -14.0F * DEGREES
                    : (float) Math.sin((player.tickCount + partial) * 1.1F) * 3.5F * DEGREES;
            return Optional.of(new AdjustmentModifier.PartModifier(new Vec3f(pitch, 0.0F, 0.0F), new Vec3f(0.0F, 0.0F, 0.0F)));
        }
        return Optional.empty();
    }
}
