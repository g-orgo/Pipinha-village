console.info("[SOCIETY] autoTapper.js loaded");

StartupEvents.registry("block", (event) => {
  event
    .create("society:auto_tapper", "cardinal")
    .displayName("Auto-Tapper")
    .tagBlock("minecraft:mineable/pickaxe")
    .tagBlock("minecraft:needs_stone_tool")
    .property(booleanProperty.create("error"))
    .defaultState((state) => {
      state.set(booleanProperty.create("error"), false);
    })
    .placementState((state) => {
      state.set(booleanProperty.create("error"), false);
    })
    .box(0, 0, 0, 16, 18, 16)
    .defaultCutout()
    .item((item) => {
      item.tooltip(Text.translatable("block.society.auto_tapper.description").gray());
      item.parentModel("society:block/kubejs/auto_tapper");
    })
    .blockEntity((blockInfo) => {
      blockInfo.initialData({ Fluid: 0, FluidType: "" });
      blockInfo.serverTicking();
      blockInfo.tickFrequency(200);
      blockInfo.tickOffset(0);
      global.portBeTicks["society:auto_tapper"] = (entity) => {
        global.runAutoTapper(entity);
      };
      blockInfo.fluidTank("fluid", Direction.ALL_SET, 10000);
    });
});
global.runAutoTapper = (blockInfo) => {
  const { block, level } = blockInfo;

  const fluidTank = blockInfo.attachments.fluid;
  const fluidData = global.handleTapperRandomTick(
    { block: block, level: level, server: level.getServer() },
    true
  );
  if (global.susFunctionLogging) console.log("[SOCIETY-SUSFN] autoTapper.js");
  if (fluidData && fluidTank && block.properties.get("error") == "false") {
    fluidTank.fill(Fluid.of(fluidData.fluid, Math.round(10 / fluidData.time)), "execute");
  }
};
