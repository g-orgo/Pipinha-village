console.info("[SOCIETY] farmingLoot.js loaded");

// TODO: "vintagedelight:gearo_berry_bush"
const cropCollectorDenied = [
  "pamhc2trees:pamapple",
  "pamhc2trees:pamcherry",
  "pamhc2trees:pamorange",
  "pamhc2trees:pampeach",
  "pamhc2trees:pamplum",
  "pamhc2trees:pamhazelnut",
  "pamhc2trees:pampawpaw",
  "pamhc2trees:pambanana",
  "pamhc2trees:pamcinnamon",
  "pamhc2trees:pamdragonfruit",
  "pamhc2trees:pammango",
  "pamhc2trees:pamstarfruit",
  "pamhc2trees:pamlychee",
  "pamhc2trees:pamlemon",
  "pamhc2trees:pampassionfruit",
];

const farmLootParams = Java.loadClass("net.minecraft.world.level.storage.loot.parameters.LootContextParams");
const farmCropBlock = Java.loadClass("net.minecraft.world.level.block.CropBlock");
const farmBlockPos = Java.loadClass("net.minecraft.core.BlockPos");
const farmBlockRegistry = Java.loadClass("net.minecraft.core.registries.BuiltInRegistries");

const cropState = (context) => context.getParamOrNull(farmLootParams.BLOCK_STATE);

// Crop is fully grown: CropBlock.isMaxAge for crops, otherwise the "age" property at its maximum.
const isCropMaxGrown = (state) => {
  const block = state.block;
  if (block instanceof farmCropBlock) return block.isMaxAge(state);
  const ageProp = block.getStateDefinition().getProperty("age");
  if (!ageProp) return false;
  const maxAge = Math.max.apply(null, Java.from(ageProp.getPossibleValues()));
  return Number(state.getValue(ageProp)) === maxAge;
};

const checkMaxGrownWithChance = (state, chance) => {
  return chance > Math.random() && isCropMaxGrown(state);
};

// Adds an item by id only when the mod providing it is loaded.
const addLootId = (loot, id) => {
  if (Item.exists(id)) loot.addItem(Item.of(id));
};

// global.getCropQuality expects a block-like object (id, level, pos). The crop is already
// removed when loot runs, so it is rebuilt from the loot context.
const destroyedCrop = (context, state) => {
  const pos = farmBlockPos.containing(context.getPosition());
  return {
    id: String(farmBlockRegistry.BLOCK.getKey(state.block)),
    blockState: state,
    getLevel: () => context.getLevel(),
    getPos: () => pos,
  };
};

LootJS.modifiers((e) => {
  e.addBlockModifier(global.cropList).customAction((context, loot) => {
    const state = cropState(context);
    loot.modifyItems((item) => {
      const quality = global.getCropQuality(destroyedCrop(context, state));
      if (quality > 0) global.setQualityLevel(item, quality);
      return item;
    });
  });
  e.addBlockModifier(global.cropList)
    .hasAnyStage("sticky_crops")
    .customAction((context, loot) => {
      if (checkMaxGrownWithChance(cropState(context), 0.02)) {
        addLootId(loot, "society:pine_tar");
      }
    });
  e.addBlockModifier(global.cropList)
    .hasAnyStage("soil_inspector")
    .customAction((context, loot) => {
      if (checkMaxGrownWithChance(cropState(context), 0.05)) {
        addLootId(loot, "farm_and_charm:fertilizer");
      }
    });
  e.addBlockModifier(global.cropList)
    .randomChance(0.25)
    .matchCustomCondition({
      condition: "minecraft:location_check",
      offsetY: -1,
      predicate: {
        block: {
          blocks: ["sunrisegardening:bountiful_fertilized_farmland"],
        },
      },
    })
    .modifyLoot(ItemFilter.ANY, (itemStack) => {
      itemStack.setCount(itemStack.getCount() + 1);
      return itemStack;
    });

  e.addBlockModifier(global.cropList)
    .hasAnyStage("paradise_crop")
    .modifyLoot(ItemFilter.ANY, (itemStack) => {
      if (!cropCollectorDenied.includes(itemStack.id))
        itemStack.setCount(itemStack.getCount() + 1);
      return itemStack;
    });
  e.addBlockModifier(global.cropList)
    .hasAnyStage("crop_collector")
    .modifyLoot(ItemFilter.ANY, (itemStack) => {
      if (!cropCollectorDenied.includes(itemStack.id))
        itemStack.setCount(itemStack.getCount() * 2);
      return itemStack;
    });

  // Mastery
  e.addBlockModifier(global.cropList)
    .hasAnyStage("husbandry_mastery")
    .customAction((context, loot) => {
      if (checkMaxGrownWithChance(cropState(context), 0.005)) {
        addLootId(loot, "society:plushie_capsule");
      }
    });
  e.addBlockModifier(global.cropList)
    .hasAnyStage("husbandry_mastery")
    .customAction((context, loot) => {
      if (checkMaxGrownWithChance(cropState(context), 0.003)) {
        addLootId(loot, "society:animal_cracker");
      }
    });
  e.addBlockModifier(global.cropList)
    .hasAnyStage("farming_mastery")
    .customAction((context, loot) => {
      if (checkMaxGrownWithChance(cropState(context), 0.005)) {
        addLootId(loot, "atmospheric:grimwood_sapling");
      }
    });
});
