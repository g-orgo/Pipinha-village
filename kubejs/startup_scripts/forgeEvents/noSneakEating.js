// Sneaking + right click gives gifts to NPCs, so it must never start eating or
// drinking (vanilla use and Immersive Eating's own animation). Covers every food, drink, potion and thirst item (canteens, bottles)
// on both sides, plus Legendary Survival Overhaul's empty hand drinking from fluids.
console.info("[SOCIETY] noSneakEating.js loaded");

global.isSneakingPlayer = (entity) =>
  entity && entity.isPlayer() && (entity.isShiftKeyDown() || entity.isCrouching());

global.isConsumableStack = (stack) => {
  if (!stack || stack.isEmpty()) return false;
  // 1.21.1 has no edible check on ItemStack; food is the minecraft:food data component.
  if (stack.get(Java.loadClass("net.minecraft.core.component.DataComponents").FOOD) != null) return true;
  var anim = String(stack.getUseAnimation());
  return anim === "EAT" || anim === "DRINK";
};

global.handleNoSneakEating = (e) => {
  if (global.isSneakingPlayer(e.getEntity()) && global.isConsumableStack(e.getItem())) e.setCanceled(true);
};

NativeEvents.onEvent("net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent$Start", (e) => {
  global.handleNoSneakEating(e);
});

// Immersive Eating starts its own eating animation from RightClickItem (NORMAL
// priority, ignores cancelled events) without ever calling startUsingItem, so
// the click itself is cancelled first, at HIGH priority, on both sides.
global.handleNoSneakRightClick = (e) => {
  if (global.isSneakingPlayer(e.getEntity()) && global.isConsumableStack(e.getItemStack())) {
    e.setCancellationResult(Java.loadClass("net.minecraft.world.InteractionResult").PASS);
    e.setCanceled(true);
  }
};

if (!global.noSneakRightClickRegistered) {
  global.noSneakRightClickRegistered = true;
  Java.loadClass("net.neoforged.neoforge.common.NeoForge").EVENT_BUS.addListener(
    Java.loadClass("net.neoforged.bus.api.EventPriority").HIGH,
    false,
    Java.loadClass("net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$RightClickItem"),
    (e) => global.handleNoSneakRightClick(e)
  );
}

// Mirrors LSO's ClientForgeEvents.onRightClickEmpty and the fluid branch of
// CommonForgeEvents.onRightClickBlock (LSO already skips block drinking while
// crouching). Cancelling the use key on the client stops both the drink effect
// and the packet; it only fires when LSO would actually drink.
global.wouldDrinkFluid = (player, hit) => {
  if (player.isCreative() || player.isSpectator()) return false;
  if (!player.getMainHandItem().isEmpty()) return false;
  var type = hit ? String(hit.getType()) : "MISS";
  if (type === "ENTITY") return false;
  // 1.21.1: LSO keeps thirst in a data attachment (AttachmentUtil) instead of a capability,
  // and the reach is the vanilla block interaction range attribute.
  var thirst = Java.loadClass("sfiomn.legendarysurvivaloverhaul.util.AttachmentUtil").getThirstAttachment(player);
  if (!thirst || thirst.isHydrationLevelAtMax()) return false;
  var Attributes = Java.loadClass("net.minecraft.world.entity.ai.attributes.Attributes");
  var reach = player.getAttributeValue(Attributes.BLOCK_INTERACTION_RANGE) / 2.0;
  if (type === "BLOCK") {
    if (player.level().getBlockEntity(hit.getBlockPos()) instanceof Java.loadClass("net.minecraft.world.MenuProvider")) return false;
  } else {
    reach = Math.max(3.0, reach);
  }
  var ThirstUtil = Java.loadClass("sfiomn.legendarysurvivaloverhaul.api.thirst.ThirstUtil");
  var drink = ThirstUtil.getFluidThirstLookedAt(player, reach);
  return drink != null && (drink.hydration != 0 || drink.saturation != 0);
};

global.handleNoSneakHandDrink = (e) => {
  if (!e.isUseItem() || String(e.getHand()) !== "MAIN_HAND") return;
  var mc = Java.loadClass("net.minecraft.client.Minecraft").getInstance();
  var player = mc.player;
  if (!player || !global.isSneakingPlayer(player)) return;
  try {
    if (global.wouldDrinkFluid(player, mc.hitResult)) {
      if (global.noSneakEatingDebug) console.info("[SOCIETY] noSneakEating blocked hand drink");
      e.setSwingHand(false);
      e.setCanceled(true);
    }
  } catch (err) {
    console.warn("[SOCIETY] noSneakEating hand drink check failed: " + err);
  }
};

if (Platform.isClientEnvironment()) {
  NativeEvents.onEvent("net.neoforged.neoforge.client.event.InputEvent$InteractionKeyMappingTriggered", (e) => {
    global.handleNoSneakHandDrink(e);
  });
}
