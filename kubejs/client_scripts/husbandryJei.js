const husbandryJeiItemAliases = {
  "minecraft:scute": "minecraft:turtle_scute",
  "trials:breeze_rod": "minecraft:breeze_rod",
};

// Returns "Nx id" (or "id") when the item exists in the registry, null otherwise.
// Strings with NBT or component data are passed through unchanged.
const husbandryJeiItem = (raw) => {
  const text = String(raw);
  if (text.includes("{") || text.includes("[")) return text;
  const match = text.match(/^(\d+x )?(.+)$/);
  if (!match) return null;
  const count = match[1] || "";
  const id = husbandryJeiItemAliases[match[2]] || match[2];
  return Item.exists(id) ? `${count}${id}` : null;
};

const registerMilkingCategory = (event, equipment, title) => {
  event.custom("society:milking", (category) => {
    const {
      jeiHelpers: { guiHelper },
    } = category;
    category
      .title(title)
      .background(guiHelper.createDrawable("society:textures/gui/milking.png", 1, 1, 148, 40))
      .icon(guiHelper.createDrawableItemStack(Item.of(husbandryJeiItem(equipment) || "minecraft:air")))
      .isRecipeHandled((recipe) => {
        return !!(recipe?.data?.animal !== undefined);
      })
      .setDrawHandler((recipe, recipeSlotsView, guiGraphics) => {
        guiGraphics.drawWordWrap(
          Client.font,
          Text.translatable(
            "jei.society.husbandry.cooldown",
            Text.translatable(
              `jei.society.working_block_entity.day${recipe.getRecipeData().cooldown > 1 ? "s" : ""}`,
              `${recipe.getRecipeData().cooldown}`
            )
          ),
          2,
          26,
          177,
          0
        );
      })
      .handleLookup((builder, recipe) => {
        const { animal, milk } = recipe.data;
        const outputs = [
          {
            item: milk.sm,
            count: 1,
          },
          {
            item: milk.lg,
            count: 1,
          },
        ];
        const slotSize = 21;
        builder
          .addSlot("CATALYST", 48, 2)
          .addItemStack(husbandryJeiItem(equipment) || "minecraft:air")
          .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        builder
          .addSlot("INPUT", 2, 2)
          .addItemStack(husbandryJeiItem(`${animal}_spawn_egg`) || "minecraft:air")
          .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        outputs.forEach((reward, index) => {
          builder
            .addSlot("OUTPUT", 104 + index * slotSize, 2)
            .addItemStack(husbandryJeiItem(`${reward.count}x ${reward.item}`) || "minecraft:air")
            .addTooltipCallback((slotView, tooltip) => {
              if (index == 0) {
                tooltip.add(1, Text.translatable("jei.society.husbandry.affection.range", `1-5`).lightPurple());
              } else {
                tooltip.add(1, Text.translatable("jei.society.husbandry.affection.over", `6`).lightPurple());
              }
            })
            .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        });
      });
  });
};

const registerForagingCategory = (event, title) => {
  event.custom("society:foraging", (category) => {
    const {
      jeiHelpers: { guiHelper },
    } = category;
    category
      .title(title)
      .background(guiHelper.createDrawable("society:textures/gui/foraging.png", 1, 1, 174, 40))
      .icon(guiHelper.createDrawableItemStack(Item.of("society:truffle")))
      .isRecipeHandled((recipe) => {
        return !!(recipe?.data?.animal !== undefined);
      })
      .setDrawHandler((recipe, recipeSlotsView, guiGraphics, mouseX, mouseY) => {
        global.runtime["textDrawHandler"](
          category.jeiHelpers,
          recipe,
          recipeSlotsView,
          guiGraphics,
          mouseX,
          mouseY
        );
      })
      .handleLookup((builder, recipe) => {
        const { animal, forages } = recipe.data;
        const slotSize = 21;
        builder
          .addSlot("INPUT", 2, 2)
          .addItemStack(husbandryJeiItem(`${animal}_spawn_egg`) || "minecraft:air")
          .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        global.runtime["textDrawHandler"] = (jeiHelpers, recipe, recipeSlotsView, guiGraphics) => {
          guiGraphics.drawWordWrap(
            Client.font,
            Text.translatable("jei.society.working_block_entity.item"),
            2,
            28,
            177,
            0
          );
        };
        forages.forEach((forage, index) => {
          if (forage.itemPool) {
            forage.itemPool.forEach((poolItem, poolIndex) => {
              // Keep itemPool forages at end of pool to ensure calculation correct
              builder
                .addSlot("OUTPUT", 50 + (index + poolIndex) * slotSize, 2)
                .addItemStack(husbandryJeiItem(`${forage.countMult}x ${poolItem}`) || "minecraft:air")
                .addTooltipCallback((slotView, tooltip) => {
                  tooltip.add(1, Text.translatable("jei.society.husbandry.affection.over", `${forage.minHearts}`).lightPurple());
                  tooltip.add(2, Text.translatable("jei.society.husbandry.pool").gold());
                  tooltip.add(
                    3,
                    Text.translatable("jei.society.husbandry.pool.roll", `${Math.round(forage.chance * 100)}`).gold()
                  );
                  tooltip.add(
                    4,
                    Text.translatable(
                      "jei.society.husbandry.pool.select", `${Math.round((1 / forage.itemPool.length) * 100)}`
                    ).gold()
                  );
                  if (forage.hasQuality) {
                    tooltip.add(5, Text.translatable("jei.society.husbandry.affection.quality").green());
                  }
                })
                .setBackground(guiHelper.getSlotDrawable(), -1, -1);
            });
          } else {
            builder
              .addSlot("OUTPUT", 50 + index * slotSize, 2)
              .addItemStack(husbandryJeiItem(`${forage.countMult}x ${forage.item}`) || "minecraft:air")
              .addTooltipCallback((slotView, tooltip) => {
                tooltip.add(1, Text.translatable("jei.society.husbandry.affection.over", `${forage.minHearts}`).lightPurple());
                tooltip.add(2, Text.translatable("jei.society.husbandry.chance", `${Math.round(forage.chance * 100)}`).gold());
                if (forage.hasQuality) {
                  tooltip.add(3, Text.translatable("jei.society.husbandry.affection.quality").green());
                }
              })
              .setBackground(guiHelper.getSlotDrawable(), -1, -1);
          }
        });
      });
  });
};

const registerGiftCategory = (event, title) => {
  event.custom("society:pet_gifts", (category) => {
    const {
      jeiHelpers: { guiHelper },
    } = category;
    category
      .title(title)
      .background(guiHelper.createDrawable("society:textures/gui/gifting.png", 1, 1, 174, 40))
      .icon(guiHelper.createDrawableItemStack(Item.of("supplementaries:present_magenta")))
      .isRecipeHandled((recipe) => {
        return !!(recipe?.data?.animal !== undefined);
      })
      .setDrawHandler((recipe, recipeSlotsView, guiGraphics, mouseX, mouseY) => {
        global.runtime["textDrawHandler"](
          category.jeiHelpers,
          recipe,
          recipeSlotsView,
          guiGraphics,
          mouseX,
          mouseY
        );
      })
      .handleLookup((builder, recipe) => {
        const { animal, gifts } = recipe.data;
        const slotSize = 21;
        builder
          .addSlot("INPUT", 2, 2)
          .addItemStack(husbandryJeiItem(`${animal}_spawn_egg`) || "minecraft:air")
          .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        global.runtime["textDrawHandler"] = (jeiHelpers, recipe, recipeSlotsView, guiGraphics) => {
          guiGraphics.drawWordWrap(
            Client.font,
            Text.translatable("jei.society.working_block_entity.item"),
            2,
            28,
            177,
            0
          );
        };
        gifts.forEach((item, index) => {
          builder
            .addSlot("OUTPUT", 50 + index * slotSize, 2)
            .addItemStack(husbandryJeiItem(`1x ${item}`) || "minecraft:air")
            .addTooltipCallback((slotView, tooltip) => {
              tooltip.add(1, Text.translatable("jei.society.husbandry.affection.at", `10`).lightPurple());
              tooltip.add(
                2,
                Text.translatable("jei.society.husbandry.pool.select", `${Math.round((1 / gifts.length) * 100)}`).gold()
              );
            })
            .setBackground(guiHelper.getSlotDrawable(), -1, -1);
        });
      });
  });
};

JEIAddedEvents.registerCategories((e) => {
  registerMilkingCategory(e, "society:milk_pail", Text.translatable("jei.society.category.milking"));
  registerForagingCategory(e, Text.translatable("jei.society.category.foraging"));
  registerGiftCategory(e, Text.translatable("jei.society.category.pet_gifts"));
});

JEIAddedEvents.registerRecipes((e) => {
  global.husbandryMilkingDefinitions.forEach((element) => {
    e.custom("society:milking").add(element);
  });
  global.husbandryForagingDefinitions.forEach((element) => {
    e.custom("society:foraging").add(element);
  });
  global.petGifts.forEach((element) => {
    e.custom("society:pet_gifts").add(element);
  });
});
