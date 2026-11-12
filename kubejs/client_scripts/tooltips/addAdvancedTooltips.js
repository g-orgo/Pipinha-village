// Item tooltips (KubeJS 7, NeoForge 1.21.1).
// Each old addAdvanced block is now a modifyTooltips hook that attaches a dynamic tooltip id,
// and the lines are built in the matching ItemEvents.dynamicTooltips handler.
// Item NBT is read from stack.customData (CompoundTag); the keys are the same as before.

// Inserts lines starting at index, keeping the old text.add(index, lines) positions.
const insertTooltipLines = (e, index, lines) => {
    let list = Array.isArray(lines) ? lines : [lines];
    list.forEach((line, offset) => {
        e.lines.add(index + offset, Text.of(line));
    });
};

const itemData = (e) => {
    const data = e.item.customData;
    return data && !data.isEmpty() ? data : null;
};

// Plushies: one shared dynamic id for every plush item.
ItemEvents.dynamicTooltips("pipinha:plushie", (e) => {
    const data = itemData(e);
    if (data) {
        let type = global.plushieTraits[Number(data.getInt("type"))];
        if (e.shift) {
            insertTooltipLines(e, 1, [
                Text.translatable("tooltip.society.plushies.trait"),
                global.getTranslatedTextWithColorCode(
                    type.color,
                    `society.item.plushie.${type.trait}`
                ),
            ]);
            insertTooltipLines(e, 2, [
                Text.translate(`society.item.plushie.trait.description`).darkGray(),
            ]);
            let description = Text.translate(
                `society.item.plushie.${type.trait}.description`
            )
                .getString()
                .split("\n");
            insertTooltipLines(e, 3, [Text.gray(description[0])]);
            insertTooltipLines(e, 4, [description[1]]);
        } else {
            {
                const quality = global.getQualityLevel(e.item);
                if (quality)
                    insertTooltipLines(e, 1, [
                        Text.translatable("tooltip.society.plushies.rarity"),
                        Text.gold("★".repeat(quality + 1)),
                        Text.gray("☆".repeat(3 - quality)),
                    ]);
                else insertTooltipLines(e, 1, [Text.gray("☆".repeat(4))]);
            }
            let affection = data.getInt("affection");
            insertTooltipLines(e, 2, [
                Text.translatable("tooltip.society.plushies.affection"),
                `§c${affection > 0 ? `❤`.repeat(affection) : ""}§7${affection < 4 ? `❤`.repeat(4 - affection) : ""
                }`,
            ]);
            insertTooltipLines(e, 3, [
                Text.translatable("tooltip.society.plushies.trait"),
                global.getTranslatedTextWithColorCode(
                    type.color,
                    `society.item.plushie.${type.trait}`
                ),
                Text.of(" "),
                Text.translatable(
                    "tooltip.society.hold_key",
                    global.getTranslatedTextWithColorCode(
                        type.color,
                        "key.keyboard.shift"
                    )
                ).gray(),
            ]);
            if (data.contains("animal")) {
                let animal = data.getCompound("animal");
                insertTooltipLines(e, 4, [
                    Text.translatable("tooltip.society.plushies.animal_type"),
                    global.getTranslatedEntityName(animal.getString("type")).gold(),
                ]);
                if (animal.contains("name")) {
                    insertTooltipLines(e, 5, [
                        Text.translatable("tooltip.society.plushies.animal_name"),
                        `§6${animal.getString("name")}`,
                    ]);
                }
            } else {
                insertTooltipLines(e, 4, [Text.translatable("tooltip.society.plushies")]);
            }
        }
    } else {
        insertTooltipLines(e, 1, [Text.translatable("tooltip.society.plushies")]);
    }
});

ItemEvents.dynamicTooltips("pipinha:villager_invitation", (e) => {
    const data = itemData(e);
    if (data) {
        insertTooltipLines(e, 1,
            Text.translatable(
                "block.society.fish_pond.fish.type",
                `${data.get("type")}`
            ).aqua()
        );
        insertTooltipLines(e, 2,
            Text.translatable("block.society.fish_pond.description").gray()
        );
    } else {
        insertTooltipLines(e, 1,
            Text.translatable("block.society.fish_pond.description").gray()
        );
    }
});

ItemEvents.dynamicTooltips("pipinha:villager_home", (e) => {
    const data = itemData(e);
    if (data) {
        insertTooltipLines(e, 1,
            Text.translatable(
                "block.society.villager_home.type",
                `${data.getString("type")}`
            ).green()
        );
        insertTooltipLines(e, 2,
            Text.translatable("block.society.villager_home.description").gray()
        );
    } else {
        insertTooltipLines(e, 1,
            Text.translatable("block.society.villager_home.description").gray()
        );
    }
});

ItemEvents.dynamicTooltips("pipinha:fish_pond", (e) => {
    const data = itemData(e);
    if (data) {
        insertTooltipLines(e, 1,
            Text.translatable(
                "block.society.fish_pond.fish.type",
                `${Item.of(data.getString("type")).id}`
            ).aqua()
        );
        insertTooltipLines(e, 2,
            Text.translatable(
                "block.society.fish_pond.fish.population",
                `${data.get("population")}`,
                `${data.get("max_population")}`
            ).aqua()
        );
    } else {
        insertTooltipLines(e, 1,
            Text.translatable("block.society.fish_pond.description").gray()
        );
        insertTooltipLines(e, 2,
            Text.translatable(
                "block.society.fish_pond.description.place"
            ).darkAqua()
        );
    }
});

ItemEvents.dynamicTooltips("pipinha:caterpillar_eggs", (e) => {
    const data = itemData(e);
    if (data) {
        insertTooltipLines(e, 1,
            Text.translatable("item.society.caterpillar_eggs.description").darkGray()
        );
        insertTooltipLines(e, 2,
            Text.translatable(
                "item.society.caterpillar_eggs.longwing.type",
                Text.translatable(`item.longwings.${data.getString("child")}`).gray()
            ).green()
        );
        insertTooltipLines(e, 3,
            Text.translatable(
                "item.society.caterpillar_eggs.longwing.parents",
                Text.translatable(`item.longwings.${data.getString("parent")}`).gray(),
                Text.translatable(`item.longwings.${data.getString("coparent")}`).gray()
            ).lightPurple()
        );
        insertTooltipLines(e, 4,
            Text.translatable(
                "item.society.caterpillar_eggs.longwing.size",
                `${data.getDouble("size")}`
            ).darkGray()
        );
    } else {
        insertTooltipLines(e, 1,
            Text.translatable("item.society.caterpillar_eggs.description").gray()
        );
    }
});

// Sometimes season just breaks for the tooltip and I have no idea why
ItemEvents.dynamicTooltips("pipinha:tomato_seed", (e) => {
    if (e.shift) {
        insertTooltipLines(e, 1, [
            Text.white("")
                .append(Text.translatable("desc.sereneseasons.fertile_seasons"))
                .append(":"),
            Text.of(" "),
            Text.translatable("desc.sereneseasons.spring").green().append(","),
            Text.of(" "),
            Text.translatable("desc.sereneseasons.summer").yellow().append(","),
            Text.of(" "),
            Text.translatable("desc.sereneseasons.autumn").gold(),
        ]);
    } else {
        insertTooltipLines(e, 1, [
            Text.translatable(
                "tooltip.society.hold_key",
                Text.translatable("key.keyboard.shift").gray()
            ).darkGray(),
        ]);
    }
});

ItemEvents.dynamicTooltips("pipinha:strawberry_seed", (e) => {
    if (e.shift) {
        insertTooltipLines(e, 1, [
            Text.white("")
                .append(Text.translatable("desc.sereneseasons.fertile_seasons"))
                .append(":"),
            Text.of(" "),
            Text.translatable("desc.sereneseasons.spring").green(),
        ]);
    } else {
        insertTooltipLines(e, 1, [
            Text.translatable(
                "tooltip.society.hold_key",
                Text.translatable("key.keyboard.shift").gray()
            ).darkGray(),
        ]);
    }
});

const magnifyingBlocks = [
    Text.translatable("block.society.auto_grabber"),
    Text.translatable("block.society.artisan_hopper"),
    Text.translatable("block.farmingforblockheads.chicken_nest"),
    Text.translatable("block.society.feeding_trough"),
    Text.translatable("block.society.snow_melter"),
    Text.translatable("block.society.fish_pond_basket"),
    Text.translatable("block.society.fish_pond_hatchery"),
    Text.translatable("block.society.golden_clock"),
    Text.translatable("block.society.mana_clock"),
    Text.translatable("block.society.mana_milker"),
    Text.translatable("item.society.magnifying_glass.description.view_block.sprinklers"),
    Text.translatable("block.society.growth_obelisk"),
    Text.translatable("block.society.ribbit_hut"),
    Text.translatable("block.society.fish_pond_manager"),
];
ItemEvents.dynamicTooltips("pipinha:magnifying_glass", (e) => {
    if (e.shift) {
        magnifyingBlocks.forEach((block, index) => {
            insertTooltipLines(e, index + 1, Text.gold(block));
        });
    } else {
        insertTooltipLines(e, 1,
            Text.translatable("item.society.magnifying_glass.description").green()
        );
        insertTooltipLines(e, 2, [
            Text.translatable(
                "item.society.magnifying_glass.description.view_block",
                Text.translatable("key.keyboard.shift").gray()
            ).darkGray(),
        ]);
    }
});

ItemEvents.dynamicTooltips("pipinha:car_key", (e) => {
    const data = itemData(e);
    insertTooltipLines(e, 1, [Text.translatable("item.society.car_key.description").gray()]);
    if (data) {
        insertTooltipLines(e, 2, [
            Text.translatable("item.society.car_key.description.parked").green(),
        ]);
    } else {
        insertTooltipLines(e, 2, [
            Text.translatable("item.society.car_key.description.empty").red(),
        ]);
    }
});

const getPigColoredName = (pig) => {
    switch (pig) {
        case "Red":
            return Text.translatable("society.pig_race.red_pig").red();
        case "Blue":
            return Text.translatable("society.pig_race.blue_pig").blue();
        case "Yellow":
            return Text.translatable("society.pig_race.yellow_pig").yellow();
        case "Green":
            return Text.translatable("society.pig_race.green_pig").green();
        default:
            console.log(`Invalid pig color`);
    }
    return Text.of(`${pig}`);
};
ItemEvents.dynamicTooltips("pipinha:pig_race_ticket", (e) => {
    insertTooltipLines(e, 1, [
        Text.translatable("item.society.pig_race_ticket.description").gray(),
    ]);
    const data = itemData(e);
    if (data) {
        insertTooltipLines(e, 2, [
            Text.translatable(
                "item.society.pig_race_ticket.description.bet",
                getPigColoredName(data.getString("bet"))
            ).gray(),
        ]);
    } else {
        insertTooltipLines(e, 2, [
            Text.translatable(
                "item.society.pig_race_ticket.description.no_pig"
            ).gray(),
        ]);
    }
});

// Aged and double-aged products recolor the name line (index 0).
global.ageableProductInputs.forEach((product) => {
    const splitProduct = product.item.split(":");
    const isWhiskeyGold =
        product.item === "brewery:whiskey_maggoallan" || product.item === "brewery:whiskey_smokey_reverie";
    ItemEvents.dynamicTooltips(`pipinha:aged_${splitProduct[1]}`, (e) => {
        if (isWhiskeyGold)
            e.lines.set(0, e.lines.get(0).copy().gold());
        else
            e.lines.set(0, e.lines.get(0).copy().aqua());
    });
    ItemEvents.dynamicTooltips(`pipinha:double_aged_${splitProduct[1]}`, (e) => {
        if (isWhiskeyGold)
            e.lines.set(0, e.lines.get(0).copy().gold());
        else
            e.lines.set(0, e.lines.get(0).copy().darkAqua());
    });
});

ItemEvents.modifyTooltips((tooltip) => {
    global.plushies.forEach((plush) => {
        tooltip.add(plush, (text) => text.dynamic("pipinha:plushie"));
    });
    tooltip.add("society:villager_invitation", (text) => text.dynamic("pipinha:villager_invitation"));
    tooltip.add("society:villager_home", (text) => text.dynamic("pipinha:villager_home"));
    tooltip.add("society:fish_pond", (text) => text.dynamic("pipinha:fish_pond"));
    tooltip.add("society:caterpillar_eggs", (text) => text.dynamic("pipinha:caterpillar_eggs"));
    tooltip.add("kaleidoscope_cookery:tomato_seed", (text) => text.dynamic("pipinha:tomato_seed"));
    tooltip.add("farm_and_charm:strawberry_seed", (text) => text.dynamic("pipinha:strawberry_seed"));
    tooltip.add("society:magnifying_glass", (text) => text.dynamic("pipinha:magnifying_glass"));
    tooltip.add("society:car_key", (text) => text.dynamic("pipinha:car_key"));
    tooltip.add(["society:pig_race_ticket", "society:multiplayer_pig_race_ticket"], (text) =>
        text.dynamic("pipinha:pig_race_ticket")
    );
    global.ageableProductInputs.forEach((product) => {
        const splitProduct = product.item.split(":");
        tooltip.add(`society:aged_${splitProduct[1]}`, (text) => text.dynamic(`pipinha:aged_${splitProduct[1]}`));
        tooltip.add(`society:double_aged_${splitProduct[1]}`, (text) =>
            text.dynamic(`pipinha:double_aged_${splitProduct[1]}`)
        );
    });
});
