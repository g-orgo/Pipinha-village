console.info("[SOCIETY] parkourExerciseHeat.js loaded");

// Exercise heat: sprinting without stopping, or hanging with ParCool (ledge or bar),
// slowly warms the player up to a cap through a Legendary Survival Overhaul
// heating_temperature modifier. Staying at the cap for a while makes the player
// sweat, which adds LSO wetness (the same "wet" status that rain and water give).
// LSO's flat "Player Sprint Modifier" is 0 in its common config, so sprint heat
// comes only from here and builds up gradually.
(function () {
  // 1.21.1: attribute modifiers are keyed by ResourceLocation and have no display name.
  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  const $AttributeModifier = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier");
  const $Operation = Java.loadClass("net.minecraft.world.entity.ai.attributes.AttributeModifier$Operation");
  const $AttributeRegistry = Java.loadClass("sfiomn.legendarysurvivaloverhaul.registry.AttributeRegistry");
  const $WetnessUtil = Java.loadClass("sfiomn.legendarysurvivaloverhaul.api.wetness.WetnessUtil");
  const $Parkourability = Java.loadClass("com.alrex.parcool.common.Parkourability");

  const HEAT_ID = $ResourceLocation.fromNamespaceAndPath("kubejs", "sunlit_exercise_heat");
  // Everything below runs once per second (20 ticks).
  const STEP_TICKS = 20;
  // Temperature added at the cap (LSO scale: 10 to 30 is normal, 20 is neutral).
  const HEAT_MAX = 4.0;
  // Heat gained per second of exercise (40 s from rest to the cap).
  const HEAT_RISE = 0.1;
  // Heat lost per second of rest (20 s from the cap back to nothing).
  const HEAT_DECAY = 0.2;
  // Horizontal blocks per second needed to count as running (sprint is about 5.6).
  const RUN_MIN_DIST = 3.0;
  // Larger jumps in one second are teleports and do not count.
  const RUN_MAX_DIST = 50.0;
  // Seconds at the cap before sweating starts.
  const SWEAT_DELAY = 20;
  // Wetness added per second while sweating (LSO dries 6 per second out of water).
  const SWEAT_PER_STEP = 12;
  // Sweat never soaks past this wetness (LSO limit is 400; 120 shows the wet icon).
  const SWEAT_CAP = 120;
  // ParCool actions that count as hanging.
  const HANG_ACTIONS = { ClingToCliff: true, HangDown: true };

  const state = {};

  // Simple names of the ParCool actions the player is doing right now.
  const doingActions = (player) => {
    const doing = {};
    const pk = $Parkourability.get(player);
    if (!pk) return doing;
    // 1.21.1: ParCool exposes its actions as an ActionSet (Parkourability.getActions()).
    const list = pk.getActions().listForIteration();
    for (let i = 0; i < list.size(); i++) {
      let action = list.get(i);
      if (action.isDoing()) doing[String(action).split("@")[0].split(".").pop()] = true;
    }
    return doing;
  };

  const setHeat = (player, value) => {
    // 1.21.1: LivingEntity.getAttribute takes the DeferredHolder directly (no .get()).
    const inst = player.getAttribute($AttributeRegistry.HEATING_TEMPERATURE);
    if (!inst) return;
    const current = inst.getModifier(HEAT_ID);
    if (current && Math.abs(current.getAmount() - value) < 0.001) return;
    if (current) inst.removeModifier(HEAT_ID);
    if (value > 0.001) {
      inst.addTransientModifier(new $AttributeModifier(HEAT_ID, value, $Operation.ADD_VALUE));
    }
  };

  // 1.21.1: LSO has no public wetness getter, so the sweat cap is counted here per hot spell.
  const sweat = (player, s) => {
    const amount = Math.min(SWEAT_PER_STEP, SWEAT_CAP - s.sweated);
    if (amount > 0) {
      $WetnessUtil.addWetness(player, amount);
      s.sweated += amount;
    }
  };

  PlayerEvents.tick((e) => {
    const { player } = e;
    if (player.level.isClientSide() || player.isFake()) return;
    if (player.age % STEP_TICKS !== 0) return;

    const id = String(player.uuid);
    const s = state[id] || (state[id] = { heat: 0, atCap: 0, sweated: 0, x: player.getX(), z: player.getZ() });
    const dx = player.getX() - s.x;
    const dz = player.getZ() - s.z;
    const dist = Math.sqrt(dx * dx + dz * dz);
    s.x = player.getX();
    s.z = player.getZ();

    if (player.isCreative() || player.isSpectator()) {
      s.heat = 0;
      s.atCap = 0;
      setHeat(player, 0);
      return;
    }

    const doing = doingActions(player);
    let hanging = false;
    let otherAction = false;
    const names = Object.keys(doing);
    for (let i = 0; i < names.length; i++) {
      let name = names[i];
      if (HANG_ACTIONS[name]) hanging = true;
      else if (name !== "FastRun") otherAction = true;
    }
    const sprinting = player.isSprinting() || doing.FastRun === true;
    const running =
      sprinting && !player.isInWater() && !player.isPassenger() && dist >= RUN_MIN_DIST && dist <= RUN_MAX_DIST;

    if (hanging || running) {
      s.heat = Math.min(HEAT_MAX, s.heat + HEAT_RISE);
    } else if (!otherAction) {
      // Other ParCool moves (vault, wall run, roll...) keep the heat without adding.
      s.heat = Math.max(0, s.heat - HEAT_DECAY);
    }
    setHeat(player, s.heat);

    s.atCap = s.heat >= HEAT_MAX - 0.001 ? s.atCap + 1 : 0;
    if (s.atCap === 0) s.sweated = 0;
    if (s.atCap > SWEAT_DELAY) sweat(player, s);
  });

  // The modifier is transient, so a new body or a new login starts cool.
  PlayerEvents.respawned((e) => {
    delete state[String(e.player.uuid)];
  });
  PlayerEvents.loggedOut((e) => {
    delete state[String(e.player.uuid)];
  });
})();
