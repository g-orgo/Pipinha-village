console.info("[SOCIETY] nerfHero.js loaded");

const applicableResult = Java.loadClass("net.neoforged.neoforge.event.entity.living.MobEffectEvent$Applicable$Result");
const $Player = Java.loadClass("net.minecraft.world.entity.player.Player");

// 1.21.1: MobEffectInstance.getEffect() returns Holder<MobEffect>, so unwrap it first.
const effectDescriptionId = (event) => String(event.getEffectInstance().getEffect().value().getDescriptionId());

global.runFixGrandma = (e) => {
  if (
    [
      "effect.farm_and_charm.grandmas_blessing",
      "effect.farm_and_charm.farmers_blessing",
      "effect.brewery.pintcharisma",
    ].includes(effectDescriptionId(e)) &&
    e.getEntity() instanceof $Player
  ) {
    // e.setResult(applicableResult.DO_NOT_APPLY);
    if (e.getEntity().potionEffects.getActiveEffects().toString().includes("stunning")) {
      console.log("removing");
      e.getEntity().potionEffects.add("oreganized:stunning", 1, 1, true, false);
      e.setResult(applicableResult.DO_NOT_APPLY);
    }
  }
};

NativeEvents.onEvent("net.neoforged.neoforge.event.entity.living.MobEffectEvent$Applicable", (event) => {
  // Any exception here propagates into LivingEntity.addEffect and can block the player from joining.
  try {
    global.runFixGrandma(event);

    if (
      [
        "effect.minecraft.hero_of_the_village",
        "effect.vinery.trading",
        "effect.brewery.pintcharisma",
        "effect.nethervinery.gravedigger",
        "effect.nethervinery.improved_gravedigger",
      ].includes(effectDescriptionId(event)) &&
      event.getEntity() instanceof $Player
    ) {
      event.setResult(applicableResult.DO_NOT_APPLY);
      console.log("No cheese in industrial capitalism...");
    }
  } catch (err) {
    console.error("[SOCIETY] nerfHero.js failed: " + err);
  }
});
