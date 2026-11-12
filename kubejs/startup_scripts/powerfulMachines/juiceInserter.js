console.info("[SOCIETY] juiceInserter.js loaded");

StartupEvents.registry("block", (event) => {
  event
    .create("society:juice_inserter", "cardinal")
    .tagBlock("minecraft:mineable/axe")
    .box(1, 0, 1, 15, 16, 15)
    .defaultCutout()
    .item((item) => {
      item.tooltip(Text.translatable("block.society.juice_inserter.description").gray());
      item.parentModel("society:block/kubejs/juice_inserter");
    })
    .blockEntity((blockInfo) => {
      blockInfo.initialData({ Fluid: 0, FluidType: "" });
      blockInfo.serverTicking();
      blockInfo.tickFrequency(10);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:juice_inserter"] = (entity) => {
        global.runJuiceInserter(entity);
      };
      blockInfo.fluidTank("fluid", Direction.ALL_SET, 10000);
    });
});

const juiceMap = [
  { fluid: "vinery:white_grape_juice", barrelFluidId: "white_general" },
  { fluid: "vinery:white_savanna_grape_juice", barrelFluidId: "white_savanna" },
  { fluid: "vinery:white_taiga_grape_juice", barrelFluidId: "white_taiga" },
  { fluid: "vinery:white_jungle_grape_juice", barrelFluidId: "white_jungle" },
  { fluid: "nethervinery:warped_grape_juice", barrelFluidId: "white_warped" },
  { fluid: "vinery:red_grape_juice", barrelFluidId: "red_general" },
  { fluid: "vinery:red_savanna_grape_juice", barrelFluidId: "red_savanna" },
  { fluid: "vinery:red_taiga_grape_juice", barrelFluidId: "red_taiga" },
  { fluid: "vinery:red_jungle_grape_juice", barrelFluidId: "red_jungle" },
  { fluid: "nethervinery:crimson_grape_juice", barrelFluidId: "red_crimson" },
  { fluid: "vinery:apple_juice", barrelFluidId: "apple" },
];
global.runJuiceInserter = (blockInfo) => {
  const { block, level } = blockInfo;
  const fluidTank = blockInfo.attachments.fluid;
  const fermentationBarrel = global.getFermentingBarrel(level, level.getBlock(block.getPos()));
  if (String(fermentationBarrel.id) !== "vinery:fermentation_barrel") return;
  // Vinery's barrel block entity exposes typed getters and setters for its juice state.
  const barrelEntity = fermentationBarrel.getEntity();
  if (!barrelEntity || !fluidTank) return;
  if (Number(barrelEntity.getFluidLevel()) + 25 > 100) return;
  const storedFluid = fluidTank.getFluid();
  if (storedFluid.getAmount() < 250) return;
  const storedFluidId = String(storedFluid.getId());
  juiceMap.forEach((juice) => {
    if (storedFluidId === juice.fluid) {
      if (Number(barrelEntity.getFluidLevel()) === 0) {
        barrelEntity.setJuiceType(juice.barrelFluidId);
      }
      if (String(barrelEntity.getJuiceType()) === juice.barrelFluidId) {
        fluidTank.drain(Fluid.of(storedFluidId, 250), "execute");
        barrelEntity.setFluidLevel(Number(barrelEntity.getFluidLevel()) + 25.0);
        barrelEntity.setChanged();
        level
          .getServer()
          .runCommandSilent(`playsound create:spout block @a ${block.x} ${block.y} ${block.z}`);
      }
    }
  });
};
