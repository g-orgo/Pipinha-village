console.info("[SOCIETY] checkAttributes.js loaded");

const shippingBinThrottle = ((temp) => (entity, tick, identifier) => {
  const { age, uuid } = entity;
  const key = `${uuid}${identifier}`;
  const now = temp[key];
  if (!now || age - now >= tick) {
    temp[key] = age;
    return false;
  }
  return true;
})({});

BlockEvents.leftClicked(
  ["shippingbin:shipping_bin", "shippingbin:basic_shipping_bin", "shippingbin:smart_shipping_bin"],
  (e) => {
    const { player, block, level } = e;
    let binPlayer;
    if (shippingBinThrottle(player, 30, "shipping-bin-throttle")) return;
    level.getServer().players.forEach((p) => {
      if (p.getUuid().toString() === global.nbtStr(block.getEntityData().data.owner)) {
        binPlayer = p;
      }
    });
    // Base value of a sell multiplier, 1 when the owner lacks the attribute (as the old list lookup did)
    const baseOrOne = (attributeId) => {
      const value = global.getAttributeBaseValue(binPlayer, attributeId);
      return Number.isNaN(value) ? 1 : value;
    };
    if (binPlayer) {
        player.tell(
          Text.translatable(
            "society.shipping_bin.owner", 
            Text.of(`${binPlayer.username}`).gold()
          )
        );
        player.tell(Text.translatable("society.shipping_bin.sell_multipliers").gray());
        player.tell(
          Text.translatable(
            "society.shipping_bin.multiplier", 
            Text.translatable("tooltip.society.farmer_product"), 
            Text.green(`${baseOrOne("shippingbin:crop_sell_multiplier")}`)
          )
        );
        player.tell(
          Text.translatable(
            "society.shipping_bin.multiplier",
            Text.translatable("tooltip.society.artisan_product"),
            Text.green(`${baseOrOne("shippingbin:wood_sell_multiplier")}`)
          )
        );
        player.tell(
          Text.translatable(
            "society.shipping_bin.multiplier",
            Text.translatable("tooltip.society.geologist_product"),
            Text.green(`${baseOrOne("shippingbin:gem_sell_multiplier")}`)
          )
        );
        player.tell(
          Text.translatable(
            "society.shipping_bin.multiplier",
            Text.translatable("tooltip.society.adventurer_product"),
            Text.green(`${baseOrOne("shippingbin:meat_sell_multiplier")}`)
          )
        );
    } else {
      player.tell(
        Text.translatable("society.shipping_bin.offline").gray()
      );
    }
  }
);
