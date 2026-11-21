package com.pipinha.curiosfix.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.mojang.logging.LogUtils;
import net.minecraft.client.model.HumanoidArmorModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.core.NonNullList;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.slf4j.Logger;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.client.CuriosRendererRegistry;
import top.theillusivec4.curios.api.type.capability.ICuriosItemHandler;
import top.theillusivec4.curios.api.type.inventory.ICurioStacksHandler;
import top.theillusivec4.curios.api.type.inventory.IDynamicStackHandler;

/**
 * Makes Curios wearables an extra layer on top of the regular armor instead of a replacement.
 * <ul>
 * <li>Simple Hats cancels the helmet render while a hat is visible in a Curios slot. During the armor
 * layer pass this class reports "no hat" to Simple Hats, so the helmet is drawn and the hat layer still
 * draws the hat on top.</li>
 * <li>Clothing (ArmorItem) in the Curios head, body and feet slots has no Curios renderer, so it was
 * invisible. The armor layer now draws it after the regular pieces, with a slightly larger model when a
 * piece is already worn in that slot, so both show without z-fighting.</li>
 * </ul>
 * Rendering runs on the render thread only, so plain static state is enough.
 */
public final class CuriosArmorLayer {

    private static final Logger LOGGER = LogUtils.getLogger();
    private static final String PREFIX = "[CuriosFix/Armor] ";

    /** Curios slot id and the armor slot whose model and texture its clothing uses. */
    public static final String[] CURIO_SLOTS = {"head", "body", "feet"};
    public static final EquipmentSlot[] ARMOR_SLOTS = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.FEET};

    /** Vanilla outer armor uses 1.0; every extra layer grows by this much. */
    private static final float LAYER_STEP = 0.25F;

    private static LivingEntity armorPassEntity;
    private static LivingEntity overrideEntity;
    private static EquipmentSlot overrideSlot;
    private static ItemStack overrideStack;

    private static final Map<Integer, HumanoidModel<LivingEntity>> LAYER_MODELS = new HashMap<>();
    private static final Set<Item> LOGGED_PIECES = new HashSet<>();
    private static boolean loggedHat;

    private CuriosArmorLayer() {
    }

    public static void beginArmorPass(LivingEntity entity) {
        armorPassEntity = entity;
    }

    public static void endArmorPass() {
        armorPassEntity = null;
        clearOverride();
    }

    /** True while the armor layer of this entity is rendering: Simple Hats must not hide the helmet. */
    public static boolean hideHatFromArmorLayer(LivingEntity entity) {
        boolean hide = entity != null && entity == armorPassEntity;
        if (hide && !loggedHat) {
            loggedHat = true;
            LOGGER.info(PREFIX + "Simple Hats helmet hiding bypassed during the armor layer (first time)");
        }
        return hide;
    }

    public static void setOverride(LivingEntity entity, EquipmentSlot slot, ItemStack stack) {
        overrideEntity = entity;
        overrideSlot = slot;
        overrideStack = stack;
    }

    public static void clearOverride() {
        overrideEntity = null;
        overrideSlot = null;
        overrideStack = null;
    }

    /** The Curios piece being drawn in place of the equipped item, or null outside the extra pass. */
    public static ItemStack overrideFor(LivingEntity entity, EquipmentSlot slot) {
        if (overrideStack != null && entity == overrideEntity && slot == overrideSlot) {
            return overrideStack;
        }
        return null;
    }

    /**
     * Visible clothing in one Curios slot, in slot order. Mirrors Curios' own layer: the cosmetic stack
     * always shows, the regular stack only when its render toggle is on. Items with their own Curios
     * renderer (Beachparty, Simple Hats and others) are left to that renderer.
     */
    public static List<ItemStack> visiblePieces(LivingEntity entity, String curioSlot, EquipmentSlot armorSlot) {
        List<ItemStack> pieces = new ArrayList<>();
        Optional<ICuriosItemHandler> inventory = CuriosApi.getCuriosInventory(entity);
        if (inventory.isEmpty()) {
            return pieces;
        }
        Optional<ICurioStacksHandler> handler = inventory.get().getStacksHandler(curioSlot);
        if (handler.isEmpty()) {
            return pieces;
        }
        IDynamicStackHandler stacks = handler.get().getStacks();
        IDynamicStackHandler cosmetics = handler.get().getCosmeticStacks();
        NonNullList<Boolean> renders = handler.get().getRenders();
        for (int i = 0; i < stacks.getSlots(); i++) {
            ItemStack stack = i < cosmetics.getSlots() ? cosmetics.getStackInSlot(i) : ItemStack.EMPTY;
            if (stack.isEmpty() && (i >= renders.size() || renders.get(i))) {
                stack = stacks.getStackInSlot(i);
            }
            if (stack.isEmpty() || !(stack.getItem() instanceof ArmorItem armor)
                    || armor.getEquipmentSlot() != armorSlot
                    || CuriosRendererRegistry.getRenderer(stack.getItem()).isPresent()) {
                continue;
            }
            pieces.add(stack);
            if (LOGGED_PIECES.add(stack.getItem())) {
                LOGGER.info(PREFIX + "drawing {} from Curios slot {} as an extra {} layer (first time)",
                        BuiltInRegistries.ITEM.getKey(stack.getItem()), curioSlot, armorSlot.getName());
            }
        }
        return pieces;
    }

    /** Armor model one step larger per layer above the vanilla outer armor (layer 1 = 1.25). */
    public static HumanoidModel<LivingEntity> layerModel(int layer) {
        return LAYER_MODELS.computeIfAbsent(layer, l -> new HumanoidArmorModel<>(LayerDefinition
                .create(HumanoidArmorModel.createBodyLayer(new CubeDeformation(1.0F + LAYER_STEP * l)), 64, 32)
                .bakeRoot()));
    }
}
