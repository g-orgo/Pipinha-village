global.updateBerryBush = (level, block) => {
  let type = 0;
  switch (global.getSeasonFromLevel(level)) {
    case "spring":
      type = 1;
      break;
    case "summer":
      type = 2;
      break;
    case "autumn":
      type = 3;
      break;
    default:
    case "winter":
      type = 4;
  }
  block.set(block.id, {
    type: String(type),
  });
};

StartupEvents.registry("block", (e) => {
  e
    .create("society:ancient_fruit", "crop")
    .age(10, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 3, 16)
        .shape(1, 0, 0, 0, 16, 4, 16)
        .shape(2, 0, 0, 0, 16, 4, 16)
        .shape(3, 0, 0, 0, 16, 8, 16)
        .shape(4, 0, 0, 0, 16, 8, 16)
        .shape(5, 0, 0, 0, 16, 16, 16)
        .shape(6, 0, 0, 0, 16, 16, 16)
        .shape(7, 0, 0, 0, 16, 16, 16)
        .shape(8, 0, 0, 0, 16, 16, 16)
        .shape(9, 0, 0, 0, 16, 16, 16)
        .shape(10, 0, 0, 0, 16, 24, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:ancient_fruit", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/ancient_seed");
    });
  e
    .create("society:tubabacco_leaf", "crop")
    .age(9, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 4, 16)
        .shape(2, 0, 0, 0, 16, 5, 16)
        .shape(3, 0, 0, 0, 16, 5, 16)
        .shape(4, 0, 0, 0, 16, 10, 16)
        .shape(5, 0, 0, 0, 16, 10, 16)
        .shape(6, 0, 0, 0, 16, 10, 16)
        .shape(7, 0, 0, 0, 16, 10, 16)
        .shape(8, 0, 0, 0, 16, 16, 16)
        .shape(9, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:tubabacco_leaf", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/tubabacco_seed");
    });

  e
    .create("brewery:hop_trellis", "crop")
    .age(6, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 16, 16)
        .shape(1, 0, 0, 0, 16, 16, 16)
        .shape(2, 0, 0, 0, 16, 16, 16)
        .shape(3, 0, 0, 0, 16, 16, 16)
        .shape(4, 0, 0, 0, 16, 16, 16)
        .shape(5, 0, 0, 0, 16, 16, 16)
        .shape(6, 0, 0, 0, 16, 22, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("brewery:hops", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("brewery:item/hops_seeds");
    });

  e
    .create("society:blueberry", "crop")
    .age(7, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 6, 16)
        .shape(3, 0, 0, 0, 16, 12, 16)
        .shape(4, 0, 0, 0, 16, 12, 16)
        .shape(5, 0, 0, 0, 16, 16, 16)
        .shape(6, 0, 0, 0, 16, 16, 16)
        .shape(7, 0, 0, 0, 16, 20, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:blueberry", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/blueberry_seeds");
    });
  e
    .create("society:cranberry", "crop")
    .age(5, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 6, 16)
        .shape(3, 0, 0, 0, 16, 12, 16)
        .shape(4, 0, 0, 0, 16, 12, 16)
        .shape(5, 0, 0, 0, 16, 16, 16)
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:cranberry", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/cranberry_seeds");
    });
  e
    .create("society:eggplant", "crop")
    .age(6, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 7, 16)
        .shape(4, 0, 0, 0, 16, 13, 16)
        .shape(5, 0, 0, 0, 16, 13, 16)
        .shape(6, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:eggplant", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/eggplant_seeds");
    });

  e
    .create("society:carrot", "crop")
    .age(7, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 7, 16)
        .shape(4, 0, 0, 0, 16, 13, 16)
        .shape(5, 0, 0, 0, 16, 13, 16)
        .shape(6, 0, 0, 0, 16, 16, 16)
        .shape(7, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("minecraft:carrot", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/carrot_seed");
    });

  e
    .create("society:potato", "crop")
    .age(7, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 7, 16)
        .shape(4, 0, 0, 0, 16, 13, 16)
        .shape(5, 0, 0, 0, 16, 13, 16)
        .shape(6, 0, 0, 0, 16, 16, 16)
        .shape(7, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("minecraft:potato", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/potato_seed");
    });

  e
    .create("society:onion", "crop")
    .age(4, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 13, 16)
        .shape(4, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("farm_and_charm:onion", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/onion_seed");
    });

  e
    .create("society:sweet_potato", "crop")
    .age(5, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 3, 16)
        .shape(4, 0, 0, 0, 16, 13, 16)
        .shape(5, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("veggiesdelight:sweet_potato", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/sweet_potato_seed");
    });

  e
    .create("society:peanut", "crop")
    .age(7, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 4, 16)
        .shape(1, 0, 0, 0, 16, 6, 16)
        .shape(2, 0, 0, 0, 16, 7, 16)
        .shape(3, 0, 0, 0, 16, 7, 16)
        .shape(4, 0, 0, 0, 16, 13, 16)
        .shape(5, 0, 0, 0, 16, 13, 16)
        .shape(6, 0, 0, 0, 16, 16, 16)
        .shape(7, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("vintagedelight:peanut", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/peanut_seed");
    });

  e
    .create("society:berry_bush")
    .defaultCutout()
    .hardness(0)
    .resistance(0)
    .mapColor("grass")
    .noCollision()
    .soundType("azalea_leaves")
    .property(integerProperty.create("type", 0, 4))
    .defaultCutout()
    .item((item) => {
      item.parentModel("society:block/kubejs/berry_bush/base");
    })
    .defaultState((state) => {
      state.set(integerProperty.create("type", 0, 4), 0);
    })
    .placementState((state) => {
      state.set(integerProperty.create("type", 0, 4), 0);
    })
    .rightClick((click) => {
      const { block, level, hand } = click;

      if (hand == "OFF_HAND") return;
      if (hand == "MAIN_HAND") {
        global.updateBerryBush(level, block);
      }
    })
    .randomTick((tick) => {
      const { block, level } = tick;
      global.updateBerryBush(level, block);
    });

  e
    .create("society:sparkpod", "crop")
    .age(8, (builder) => {
      builder
        .shape(0, 0, 0, 0, 16, 3, 16)
        .shape(1, 0, 0, 0, 16, 3, 16)
        .shape(2, 0, 0, 0, 16, 5, 16)
        .shape(3, 0, 0, 0, 16, 5, 16)
        .shape(4, 0, 0, 0, 16, 8, 16)
        .shape(5, 0, 0, 0, 16, 8, 16)
        .shape(6, 0, 0, 0, 16, 11, 16)
        .shape(7, 0, 0, 0, 16, 11, 16)
        .shape(8, 0, 0, 0, 16, 16, 16);
    })
    .survive((state, level, pos) => global.surviveCheck(level, pos))
    .noSeeds()
    .crop("society:sparkpod", 1)
    .tagBlock("minecraft:mineable/hoe")
    .tagBlock("minecraft:crops")
    .randomTick((tick) => {})
    .item((seedItem) => {
      seedItem.texture("society:item/sparkpod_spores");
    });
});
