console.info("[SOCIETY] seedMessage.js loaded");

const seedMessageThrottle = ((temp) => (entity, tick, identifier) => {
  // KubeJS 7: entity.age is undefined, so the throttle never held. Use the tick count.
  const { uuid } = entity;
  const age = global.playerTicks(entity);
  const key = `${uuid}${identifier}`;
  const now = temp[key];
  if (!now || age - now >= tick) {
    temp[key] = age;
    return false;
  }
  return true;
})({});

BlockEvents.rightClicked(
  [
    "minecraft:farmland",
    "sunrisegardening:tilled_soil",
    "sunrisegardening:weak_fertilized_farmland",
    "sunrisegardening:strong_fertilized_farmland",
    "sunrisegardening:hyper_fertilized_farmland",
    "sunrisegardening:hydrating_farmland",
    "sunrisegardening:bountiful_fertilized_farmland",
    "sunrisegardening:low_quality_fertilized_farmland",
    "sunrisegardening:high_quality_fertilized_farmland",
    "sunrisegardening:pristine_quality_fertilized_farmland",
  ],
  (e) => {
    const { player, level, block, server } = e;
    if (!player.getHeldItem("main_hand").hasTag("c:seeds")) return;
    let errorText;
    const biomeTags = level
      .getBiome(block.pos)
      .tags()
      .map((tagkey) => tagkey.location())
      .toList();
    if (biomeTags.toString().includes("sereneseasons:infertile_biomes")) {
      errorText = Text.translatable("society.planting_crop.infertile_biome").toJson();
    }
    if (!seedMessageThrottle(player, 1200, "seed_message_throttle") && errorText) {
      global.renderUiText(
        player,
        server,
        {
          seedBiomeMessage: {
            type: "text",
            x: 0,
            y: -90,
            text: `${errorText}`,
            color: "#FF5555",
            alignX: "center",
            alignY: "bottom",
          },
          seedBiomeMessageShadow: {
            type: "text",
            x: 1,
            z: -1,
            y: -89,
            text: `${errorText}`,
            color: "#000000",
            alignX: "center",
            alignY: "bottom",
          },
        },
        global.mainUiElementIds
      );
    }
  }
);
// BlockEvents.placed(
//   ([
//     "minecraft:cactus",
//     "moreminecarts:glass_cactus",
//     "minecraft:sugar_cane",
//     "nethervinery:crimson_grape_bush",
//     "nethervinery:warped_grape_bush",
//     "vinery:jungle_grape_bush_red",
//     "vinery:jungle_grape_bush_white",
//     "vinery:taiga_grape_bush_white",
//     "vinery:taiga_grape_bush_red",
//     "vinery:savanna_grape_bush_white",
//     "vinery:savanna_grape_bush_red",
//     "vinery:white_grape_bush",
//     "vinery:red_grape_bush",
//     "windswept:wild_berry_bush",
//     "minecraft:sweet_berry_bush",
//   ],
//   (e) => {
//     const { player, block, server } = e;
//     let errorText;
//     if (
//       ["minecraft:cactus", "moreminecarts:glass_cactus", "minecraft:sugar_cane"].includes(block.id)
//     ) {
//       errorText = "This must be planted on Tilled Sand to grow";
//     }
//     if (block.id.includes("jungle")) {
//       errorText = "This Seed must be planted on a Vinery Lattice to grow";
//     } else if (block.id.includes("grape")) {
//       errorText = "This must be planted on a Grapevine Stem to grow";
//     }
//     if (block.id.includes("berry")) {
//       errorText = "This berry must be planted on farmland to grow";
//     }

//     if (errorText) {
//       global.renderUiText(
//         player,
//         server,
//         {
//           seedBiomeMessage: {
//             type: "text",
//             x: 0,
//             y: -90,
//             text: errorText,
//             color: "#FF5555",
//             alignX: "center",
//             alignY: "bottom",
//           },
//           seedBiomeMessageShadow: {
//             type: "text",
//             x: 1,
//             z: -1,
//             y: -89,
//             text: errorText,
//             color: "#000000",
//             alignX: "center",
//             alignY: "bottom",
//           },
//         },
//         global.mainUiElementIds
//       );
//     }
//   })
// );
