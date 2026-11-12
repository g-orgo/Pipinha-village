console.info("[SOCIETY] addFishBaits.js loaded");

ServerEvents.generateData("after_mods", (e) => {
  const $ResourceLocation = Java.loadClass("net.minecraft.resources.ResourceLocation");
  global.fish.forEach((fish) => {
    const splitFish = fish.item.split(":");
    let fishId = splitFish[1];
    if (
      ["barrel", "roe", "meat"].some((denied) => splitFish[1].includes(denied))
    )
      return;
    if (fishId.includes("raw_")) {
      if (fishId === "raw_snowflake") fishId = "frosty_fin";
      else fishId = fishId.substring(4, fishId.length);
    }
    e.json(
      $ResourceLocation.parse(`crabbersdelight:loot_table/gameplay/crab_trap_loot/${fishId}_bait.json`),
      {
        type: "minecraft:fishing",
        pools: [
          {
            rolls: 1,
            bonus_rolls: 0,
            entries: [
              {
                type: "minecraft:item",
                weight: 1,
                name: fish.item,
              },
            ],
          },
        ],
      }
    );
  });
});
