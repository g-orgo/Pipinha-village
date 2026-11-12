console.info("[SOCIETY] npcInvite.js loaded");

ItemEvents.rightClicked("society:invitation", (e) => {
  const { server, player, item } = e;
  if (player.isFake()) e.cancel();
  // 1.21.1: the invitation type lives in the minecraft:custom_data component, not item NBT.
  const inviteCustom = player.getHeldItem("main_hand").get(Java.loadClass("net.minecraft.core.component.DataComponents").CUSTOM_DATA);
  const inviteData = inviteCustom ? inviteCustom.copyTag() : null;

  if (inviteData && inviteData.contains("type")) {
    let id = inviteData.getString("type");
    let baseId = id.substring(8, id.length);
    server.scheduleInTicks(0, () => {
      server.scheduleInTicks(1, () => {
        player.give(Item.of(`society:villager_home[minecraft:custom_data={type:"${baseId}"}]`))
      });
    });
    if (!player.stages.has(`invited_${baseId}`)) {
      player.stages.add(`invited_${baseId}`)
      player.tell(Text.translatable("society.invitation.place_home").green());
      if (baseId === "market") {
        player.tell(Text.translatable("society.new_villager.message").green());
      }
    }
    if (!player.isCreative()) item.count--;
    server.runCommandSilent(
      `playsound stardew_fishing:complete block @a ${player.x} ${player.y} ${player.z}`
    );
  } else {
    player.tell("Something went wrong! Tell Chakyl")
  }
  global.addItemCooldown(player, item, 4);
});
