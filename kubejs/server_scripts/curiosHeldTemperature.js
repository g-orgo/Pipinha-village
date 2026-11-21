console.info("[SOCIETY] curiosHeldTemperature.js loaded");

// Warm and cold items (LSO "temperature" in kubejs/data/*/legendarysurvivaloverhaul/temperature/items/)
// count in the Curios slots and in the hands.
//
// 1) Curios resync after login. In singleplayer LSO asks Curios for the item's valid slots on the
//    client-side slot list (CuriosApi.getItemStackSlots(stack, true), because the physical side is
//    the client). That list is only filled by Curios' sync packet, and Curios computes the attribute
//    modifiers of already equipped items on the player's first tick and only again when the stack
//    changes. When that first tick wins the race against the packet, a lantern in the charm slot
//    (or a hat in the head slot) stays without its LSO modifier for the whole session. A few
//    seconds after login this script asks Curios (and so LSO) for the modifiers again and adds the
//    LSO ones that are missing, with the same ids LSO uses, so nothing is counted twice.
// 2) Held items. LSO skips any Curios item in the hand (a lantern is a charm) and, in 1.21.1, never
//    counts the off hand. Here a warm or cold item counts in the off hand, and a Curios item counts
//    in the main hand too. A non-Curios item in the main hand is left to LSO, which already counts it.
(function () {
  // Diagnostic logs "[curiostemp]" in logs/latest.log; turn off after the owner confirms in game.
  const TEMP_DEBUG = true;

  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  const $AttributeModifier = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier");
  const $Operation = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation");
  const $BuiltInRegistries = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");
  const $CuriosApi = Java.loadClass("top.theillusivec4.curios.api.CuriosApi");
  const $SlotContext = Java.loadClass("top.theillusivec4.curios.api.SlotContext");
  const $AttributeRegistry = Java.loadClass("sfiomn.legendarysurvivaloverhaul.registry.AttributeRegistry");
  const $TemperatureDataManager = Java.loadClass("sfiomn.legendarysurvivaloverhaul.api.data.manager.TemperatureDataManager");

  const HELD_HEAT_ID = $ResourceLocation.fromNamespaceAndPath("kubejs", "held_item_heating");
  const HELD_COOL_ID = $ResourceLocation.fromNamespaceAndPath("kubejs", "held_item_cooling");
  // Held items are checked once per second.
  const STEP_TICKS = 20;
  // Curios resync runs at these player ages (ticks since login or respawn).
  const RESYNC_AT = [60, 200];
  // LSO attributes that a Curios item can carry.
  const LSO_ATTRIBUTES = {
    "legendarysurvivaloverhaul:heating_temperature": true,
    "legendarysurvivaloverhaul:cooling_temperature": true,
    "legendarysurvivaloverhaul:heat_resistance": true,
    "legendarysurvivaloverhaul:cold_resistance": true,
    "legendarysurvivaloverhaul:thermal_resistance": true,
  };

  const state = {};

  const debug = (msg) => {
    if (!TEMP_DEBUG) return;
    try {
      console.info("[curiostemp] " + msg());
    } catch (err) {
      console.warn("[curiostemp] debug log failed: " + err);
    }
  };

  // LSO temperature of an item stack (0 when the item has no LSO data).
  const itemTemperature = (stack) => {
    let data = null;
    data = $TemperatureDataManager.getItem($BuiltInRegistries.ITEM.getKey(stack.getItem()));
    if (!data) return 0;
    return Number(data.temperature) || 0;
  };

  const isCurioItem = (stack, player) =>
    !$CuriosApi["getItemStackSlots(net.minecraft.world.item.ItemStack,net.minecraft.world.entity.LivingEntity)"](
      stack,
      player
    ).isEmpty();

  const setModifier = (player, holder, id, value) => {
    // 1.21.1: LivingEntity.getAttribute takes the DeferredHolder directly (no .get()).
    const inst = player.getAttribute(holder);
    if (!inst) return;
    const current = inst.getModifier(id);
    if (current && Math.abs(current.amount() - value) < 0.001) return;
    if (current) inst["removeModifier(net.minecraft.resources.ResourceLocation)"](id);
    if (Math.abs(value) > 0.001) inst.addTransientModifier(new $AttributeModifier(id, value, $Operation.ADD_VALUE));
  };

  // Re-asks Curios for the modifiers of every equipped item that has LSO data and adds the
  // LSO ones that are missing. addOrUpdateTransientModifier is what Curios itself uses, so a
  // modifier that is already there is only refreshed.
  const resyncCurios = (player, label) => {
    let inv = null;
    let handlers = null;
    let it = null;
    let entry = null;
    let slotId = "";
    let handler = null;
    let stacks = null;
    let renders = null;
    let active = null;
    let i = 0;
    let stack = null;
    let ctx = null;
    let mods = null;
    let mit = null;
    let me = null;
    let name = "";
    let inst = null;
    let mod = null;
    let found = 0;
    let missing = 0;
    let fromLso = 0;
    let item = "";
    inv = $CuriosApi.getCuriosInventory(player);
    if (!inv.isPresent()) return;
    handlers = inv.get().getCurios();
    it = handlers.entrySet().iterator();
    while (it.hasNext()) {
      entry = it.next();
      slotId = String(entry.getKey());
      handler = entry.getValue();
      stacks = handler.getStacks();
      renders = handler.getRenders();
      active = handler.getActiveStates();
      for (i = 0; i < stacks.getSlots(); i++) {
        stack = stacks.getStackInSlot(i);
        if (stack.isEmpty()) continue;
        // NonNullList<Boolean> hands back java.lang.Boolean; String() avoids Rhino wrapper surprises.
        if (active && i < active.size() && String(active.get(i)) === "false") continue;
        item = String($BuiltInRegistries.ITEM.getKey(stack.getItem()));
        if (!$TemperatureDataManager.getItem($BuiltInRegistries.ITEM.getKey(stack.getItem()))) continue;
        found++;
        ctx = new $SlotContext(slotId, player, i, false, i < renders.size() ? String(renders.get(i)) === "true" : true);
        mods = $CuriosApi.getAttributeModifiers(ctx, $CuriosApi.getSlotId(ctx), stack);
        fromLso = 0;
        mit = mods.entries().iterator();
        while (mit.hasNext()) {
          me = mit.next();
          name = String(me.getKey().getRegisteredName());
          if (!LSO_ATTRIBUTES[name]) continue;
          fromLso++;
          inst = player.getAttribute(me.getKey());
          if (!inst) continue;
          mod = me.getValue();
          if (!inst.getModifier(mod.id())) missing++;
          inst.addOrUpdateTransientModifier(mod);
        }
        debug(() => label + " " + slotId + "[" + i + "] " + item + ": " + fromLso + " LSO modifiers from Curios");
      }
    }
    debug(
      () =>
        label +
        " " +
        player.getName().getString() +
        ": " +
        found +
        " Curios items with LSO data, " +
        missing +
        " modifiers were missing and were added, heating=" +
        player.getAttributeValue($AttributeRegistry.HEATING_TEMPERATURE) +
        " cooling=" +
        player.getAttributeValue($AttributeRegistry.COOLING_TEMPERATURE)
    );
  };

  // Warmth of the held items that LSO does not count by itself.
  const updateHeld = (player, s) => {
    let heat = 0;
    let cool = 0;
    let hands = [];
    let h = 0;
    let stack = null;
    let isMain = false;
    let t = 0;
    let key = "";
    hands = [player.getMainHandItem(), player.getOffhandItem()];
    for (h = 0; h < hands.length; h++) {
      stack = hands[h];
      isMain = h === 0;
      if (!stack || stack.isEmpty()) continue;
      // Armor and shields are LSO's own business (worn or blocking), not "holding something warm".
      if (String(player.getEquipmentSlotForItem(stack).getName()) !== "mainhand") continue;
      t = itemTemperature(stack);
      if (t === 0) continue;
      if (isMain && !isCurioItem(stack, player)) continue;
      if (t > 0) heat += t;
      else cool += t;
    }
    setModifier(player, $AttributeRegistry.HEATING_TEMPERATURE, HELD_HEAT_ID, heat);
    setModifier(player, $AttributeRegistry.COOLING_TEMPERATURE, HELD_COOL_ID, cool);
    key = heat.toFixed(2) + "/" + cool.toFixed(2);
    if (key !== s.held) {
      s.held = key;
      debug(() => "held " + player.getName().getString() + ": heating +" + heat + " cooling " + cool);
    }
  };

  PlayerEvents.tick((e) => {
    const { player } = e;
    let ticks = 0;
    let id = "";
    let s = null;
    let r = 0;
    try {
      if (player.level.isClientSide() || player.isFake()) return;
      ticks = global.playerTicks(player);
      if (ticks % STEP_TICKS !== 0) return;
      id = String(player.uuid);
      s = state[id] || (state[id] = { resynced: {}, held: "" });
      for (r = 0; r < RESYNC_AT.length; r++) {
        if (ticks >= RESYNC_AT[r] && !s.resynced[r]) {
          s.resynced[r] = true;
          resyncCurios(player, "resync@" + RESYNC_AT[r]);
        }
      }
      updateHeld(player, s);
    } catch (err) {
      if (!s || !s.failed) console.error("[curiostemp] tick failed: " + err);
      if (s) s.failed = true;
    }
  });

  // Transient modifiers die with the body; a new body or a new login starts over.
  PlayerEvents.respawned((e) => {
    delete state[String(e.player.uuid)];
  });
  PlayerEvents.loggedOut((e) => {
    delete state[String(e.player.uuid)];
  });
})();
