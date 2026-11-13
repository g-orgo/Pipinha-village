"""Temas de loot para os containers das cidades Sunlit.

Cada tema: (rolls_min, rolls_max, [(item, peso, min, max), ...]). Itens inexistentes ou
removidos pelo modpack sao descartados na geracao (validados contra registry.json).
"""
import collections, glob, json, os, re, zipfile
from mapping import item_ok, ITEMS, REG
from itemcheck import bad_item, save_cache, CROP_BLACKLIST

FOOD_SNACK = [('minecraft:bread', 10, 1, 3), ('minecraft:apple', 8, 1, 3), ('minecraft:cookie', 6, 2, 6),
              ('farmersdelight:egg_sandwich', 4, 1, 2), ('bakery:toast', 4, 1, 2), ('bakery:croissant', 3, 1, 2),
              ('farmersdelight:sweet_berry_cookie', 4, 2, 5), ('farmersdelight:honey_cookie', 4, 2, 5),
              ('veggiesdelight:carrot_juice', 3, 1, 2), ('kaleidoscope_tavern:watermelon_juice', 3, 1, 2),
              ('farmersdelight:apple_cider', 2, 1, 1), ('herbalbrews:green_tea', 2, 1, 2), ('farmersrespite:coffee', 3, 1, 2)]
RAW_INGREDIENTS = [('minecraft:egg', 8, 1, 4), ('minecraft:sugar', 6, 1, 4), ('hearthandharvest:goat_milk_bottle', 2, 1, 1),
                   ('farmersdelight:milk_bottle', 5, 1, 3), ('kaleidoscope_cookery:tomato', 6, 1, 4), ('farmersdelight:cabbage', 5, 1, 3),
                   ('minecraft:beetroot', 4, 1, 4),
                   ('kaleidoscope_cookery:flour', 5, 1, 4), ('farm_and_charm:butter', 3, 1, 2), ('farm_and_charm:yeast', 2, 1, 2),
                   ('veggiesdelight:garlic', 3, 1, 3), ('kaleidoscope_cookery:rice', 3, 1, 4), ('kaleidoscope_cookery:oil', 2, 1, 2),
                   ('meadow:piece_of_cheese', 4, 1, 3), ('farmersdelight:minced_beef', 3, 1, 3), ('farmersdelight:bacon', 3, 1, 3),
                   ('farmersdelight:chicken_cuts', 3, 1, 3), ('minecraft:cocoa_beans', 2, 1, 3), ('minecraft:honey_bottle', 2, 1, 2),
                   ('farmersdelight:tomato_sauce', 2, 1, 1), ('minecraft:apple', 2, 1, 3), ('pamhc2trees:lemonitem', 2, 1, 3)]
MEALS = [('farmersdelight:beef_stew', 4, 1, 2), ('farmersdelight:chicken_soup', 4, 1, 2), ('farmersdelight:vegetable_soup', 4, 1, 2),
         ('farmersdelight:pasta_with_meatballs', 3, 1, 1), ('farmersdelight:fried_rice', 3, 1, 2), ('farmersdelight:hamburger', 4, 1, 2),
         ('farmersdelight:bacon_sandwich', 4, 1, 2), ('farmersdelight:mixed_salad', 3, 1, 2), ('farmersdelight:shepherds_pie', 2, 1, 1),
         ('candlelight:lasagne', 2, 1, 1), ('candlelight:bolognese', 2, 1, 1), ('candlelight:omelet', 3, 1, 2), ('candlelight:salad', 3, 1, 2),
         ('candlelight:tomato_soup', 3, 1, 2), ('veggiesdelight:fish_and_chips', 3, 1, 2), ('veggiesdelight:garlic_bread', 3, 1, 2),
          ('veggiesdelight:mashed_potatoes', 3, 1, 2), ('vintagedelight:cheese_burger', 3, 1, 2), ('minecraft:cooked_beef', 3, 1, 2),
         ('vintagedelight:meat_pizza_slice', 3, 1, 3), ('kaleidoscope_cookery:egg_fried_rice', 2, 1, 2), ('farm_and_charm:potato_soup', 3, 1, 2),
         ('farm_and_charm:farmers_breakfast', 2, 1, 1), ('farm_and_charm:goulash', 2, 1, 1)]
BAKERY = [('minecraft:bread', 10, 2, 5), ('bakery:baguette', 6, 1, 3), ('bakery:croissant', 6, 1, 4), ('bakery:braided_bread', 5, 1, 3),
          ('bakery:crusty_bread', 5, 1, 3), ('bakery:bun', 6, 2, 4), ('bakery:waffle', 4, 1, 3),
          ('bakery:strawberry_cupcake', 4, 1, 3), ('bakery:apple_cupcake', 4, 1, 3), ('bakery:chocolate_cake_slice', 3, 1, 2),
          ('bakery:strawberry_cake_slice', 3, 1, 2), ('bakery:jam_roll', 3, 1, 2), ('bakery:pancake', 3, 1, 3),
          ('farm_and_charm:farmers_bread', 4, 1, 2), ('veggiesdelight:carrot_cake_slice', 3, 1, 2), ('minecraft:pumpkin_pie', 3, 1, 2),
          ('minecraft:cake', 1, 1, 1), ('bakery:rolling_pin', 1, 1, 1), ('bakery:bread_knife', 1, 1, 1)]
DRINKS = [('vinery:apple_juice', 4, 1, 3), ('kaleidoscope_tavern:grape_juice', 4, 1, 3), ('veggiesdelight:carrot_juice', 4, 1, 2),
          ('kaleidoscope_tavern:watermelon_juice', 4, 1, 3), ('farmersdelight:apple_cider', 3, 1, 2), ('farmersrespite:coffee', 5, 1, 3),
          ('herbalbrews:milk_coffee', 4, 1, 2), ('herbalbrews:green_tea', 4, 1, 2), ('herbalbrews:black_tea', 4, 1, 2),
          ('herbalbrews:hibiscus_tea', 3, 1, 2), ('farmersdelight:hot_cocoa', 4, 1, 2), ('crabbersdelight:kelp_shake', 2, 1, 2),
          ('farm_and_charm:strawberry_tea_cup', 3, 1, 2), ('minecraft:honey_bottle', 3, 1, 2), ('kaleidoscope_tavern:watermelon_juice', 2, 1, 2)]
CREATE_PARTS = [('create:andesite_alloy', 10, 2, 8), ('create:shaft', 8, 2, 6), ('create:cogwheel', 8, 1, 4), ('create:large_cogwheel', 4, 1, 2),
                ('create:zinc_ingot', 6, 1, 4), ('create:zinc_nugget', 6, 3, 9), ('create:copper_nugget', 5, 3, 9), ('create:brass_ingot', 3, 1, 3),
                ('create:iron_sheet', 5, 1, 4), ('create:copper_sheet', 4, 1, 4), ('create:brass_sheet', 2, 1, 2), ('create:belt_connector', 4, 1, 3),
                ('create:andesite_casing', 4, 1, 3),
                ('create:wrench', 2, 1, 1), ('create:goggles', 1, 1, 1), ('create:electron_tube', 2, 1, 2), ('create:fluid_pipe', 3, 2, 6),
                ('create:precision_mechanism', 1, 1, 1),
                ('create:super_glue', 1, 1, 1), ('create:propeller', 1, 1, 1), ('create:whisk', 1, 1, 1)]
TOOLS = [('minecraft:iron_ingot', 6, 1, 4), ('minecraft:copper_ingot', 6, 2, 6), ('minecraft:iron_nugget', 6, 3, 9), ('minecraft:coal', 6, 2, 6),
         ('minecraft:stone_pickaxe', 1, 1, 1), ('minecraft:iron_axe', 1, 1, 1), ('minecraft:iron_shovel', 1, 1, 1), ('minecraft:shears', 2, 1, 1),
         ('minecraft:flint_and_steel', 1, 1, 1), ('minecraft:chain', 3, 1, 4), ('minecraft:lantern', 3, 1, 2), ('minecraft:torch', 6, 4, 12),
         ('supplementaries:rope', 4, 2, 8), ('minecraft:string', 4, 2, 6), ('minecraft:redstone', 3, 2, 6), ('minecraft:bucket', 1, 1, 1),
         ('etcetera:hammer', 1, 1, 1), ('etcetera:chisel', 1, 1, 1), ('minecraft:leather', 2, 1, 3), ('minecraft:oak_planks', 3, 4, 12)]
# sementes que plantam o ANO TODO (regra 2026-10-06: Serene Seasons nao deixa crescer fora de
# estacao) + os classicos vanilla abobora/melancia (sazonais de proposito no modpack). Fora: trigo,
# beterraba, repolho, tomate, cevada, aveia, morango, alface, abobrinha, pimentao, pepino, amendoim,
# uvas, algodao (semente que planta e nao nasce nao entra em bau).
SEEDS = [('veggiesdelight:turnip_seeds', 3, 2, 5), ('veggiesdelight:broccoli_seeds', 3, 2, 5),
         ('veggiesdelight:cauliflower_seeds', 3, 2, 5), ('veggiesdelight:garlic_clove', 3, 2, 5),
         ('veggiesdelight:sweet_potato', 3, 1, 4), ('kaleidoscope_cookery:lettuce_seed', 2, 1, 3),
         ('kaleidoscope_cookery:chili_seed', 2, 1, 3), ('kaleidoscope_cookery:tomato_seed', 2, 1, 3),
         ('culturaldelights:eggplant_seeds', 2, 1, 3),
         ('minecraft:pumpkin_seeds', 4, 1, 4), ('minecraft:melon_seeds', 4, 1, 4)]
FARM = SEEDS + [('minecraft:bone_meal', 8, 2, 8), ('minecraft:wheat', 6, 2, 8), ('minecraft:hay_block', 3, 1, 2), ('minecraft:lead', 3, 1, 2),
                 ('minecraft:shears', 2, 1, 1), ('minecraft:iron_hoe', 2, 1, 1), ('minecraft:bucket', 1, 1, 1), ('minecraft:egg', 4, 2, 6),
                ('minecraft:oak_sapling', 3, 1, 3), ('minecraft:birch_sapling', 2, 1, 3), ('farm_and_charm:fertilizer', 3, 1, 4),
                ('farm_and_charm:chicken_feed', 3, 1, 4), ('farm_and_charm:horse_fodder', 2, 1, 3), ('farmersdelight:straw', 4, 2, 6),
                ('farmersdelight:flint_knife', 1, 1, 1), ('dew_drop_watering_cans:copper_watering_can', 1, 1, 1),
                ('minecraft:name_tag', 1, 1, 1), ('minecraft:saddle', 1, 1, 1)]
FLOWERS = [('minecraft:poppy', 6, 1, 4), ('minecraft:dandelion', 6, 1, 4), ('minecraft:cornflower', 5, 1, 4), ('minecraft:allium', 4, 1, 3),
           ('minecraft:azure_bluet', 4, 1, 3), ('minecraft:oxeye_daisy', 4, 1, 3), ('minecraft:lily_of_the_valley', 3, 1, 3),
           ('minecraft:red_tulip', 4, 1, 3), ('minecraft:pink_tulip', 4, 1, 3), ('minecraft:white_tulip', 4, 1, 3), ('minecraft:orange_tulip', 4, 1, 3),
           ('minecraft:sunflower', 2, 1, 2), ('minecraft:rose_bush', 2, 1, 2), ('minecraft:peony', 2, 1, 2), ('minecraft:lilac', 2, 1, 2),
           ('minecraft:flower_pot', 5, 1, 4), ('minecraft:bone_meal', 6, 2, 8), ('minecraft:oak_sapling', 3, 1, 2), ('minecraft:cherry_sapling', 2, 1, 2),
           ('minecraft:azalea', 2, 1, 2), ('minecraft:flowering_azalea', 2, 1, 2), ('herbalbrews:lavender_blossom', 2, 1, 3),
           ('minecraft:moss_block', 2, 1, 3), ('candlelight:rose', 3, 1, 3)]
HOME = [('minecraft:candle', 5, 1, 3), ('minecraft:white_candle', 3, 1, 2), ('minecraft:book', 5, 1, 3), ('minecraft:paper', 5, 2, 6),
        ('minecraft:torch', 6, 2, 8), ('minecraft:string', 4, 1, 4), ('minecraft:white_wool', 3, 1, 3), ('minecraft:stick', 4, 2, 6),
        ('minecraft:flower_pot', 2, 1, 2), ('minecraft:clock', 1, 1, 1), ('minecraft:compass', 1, 1, 1), ('minecraft:writable_book', 2, 1, 1),
        ('minecraft:glass_bottle', 3, 1, 3), ('minecraft:bowl', 3, 1, 3), ('minecraft:emerald', 1, 1, 2), ('supplementaries:soap', 2, 1, 2),
        ('supplementaries:candy', 2, 1, 3), ('minecraft:name_tag', 1, 1, 1), ('minecraft:painting', 1, 1, 1), ('minecraft:item_frame', 2, 1, 2)]
BEDROOM = [('minecraft:white_wool', 6, 1, 4), ('minecraft:light_gray_wool', 3, 1, 3), ('minecraft:string', 5, 1, 4), ('minecraft:leather', 3, 1, 2),
           ('minecraft:book', 6, 1, 3), ('minecraft:writable_book', 3, 1, 1), ('minecraft:paper', 4, 1, 4), ('minecraft:candle', 4, 1, 2),
           ('minecraft:feather', 3, 1, 4), ('minecraft:pink_dye', 2, 1, 2), ('minecraft:light_blue_dye', 2, 1, 2), ('minecraft:yellow_dye', 2, 1, 2),
           ('minecraft:clock', 1, 1, 1), ('minecraft:music_disc_cat', 1, 1, 1), ('minecraft:music_disc_mellohi', 1, 1, 1),
           ('etcetera:white_sweater', 2, 1, 1), ('etcetera:red_sweater', 1, 1, 1), ('etcetera:blue_hat', 1, 1, 1),
           ('simplehats:beanie', 1, 1, 1), ('simplehats:hatbag_common', 1, 1, 1), ('candlelight:love_letter', 1, 1, 1),
           ('minecraft:leather_boots', 1, 1, 1), ('minecraft:leather_helmet', 1, 1, 1), ('supplementaries:candy', 2, 1, 3),
           ('exposure:photograph', 1, 1, 1), ('minecraft:emerald', 1, 1, 2)]
BATHROOM = [('supplementaries:soap', 8, 1, 3), ('minecraft:sponge', 2, 1, 1), ('minecraft:white_wool', 4, 1, 2), ('minecraft:glass_bottle', 5, 1, 3),
            ('minecraft:water_bucket', 1, 1, 1), ('minecraft:honey_bottle', 2, 1, 1), ('minecraft:paper', 4, 2, 6), ('minecraft:white_dye', 2, 1, 2),
            ('minecraft:bone_meal', 1, 1, 2)]
CLOTHING = [('minecraft:white_wool', 6, 2, 6), ('minecraft:red_wool', 3, 1, 4), ('minecraft:blue_wool', 3, 1, 4), ('minecraft:yellow_wool', 3, 1, 4),
            ('minecraft:string', 6, 2, 8), ('minecraft:leather', 5, 1, 4), ('minecraft:leather_boots', 2, 1, 1), ('minecraft:leather_chestplate', 2, 1, 1),
            ('minecraft:leather_leggings', 2, 1, 1), ('minecraft:leather_helmet', 2, 1, 1), ('etcetera:white_sweater', 3, 1, 1),
            ('etcetera:blue_sweater', 2, 1, 1), ('etcetera:green_sweater', 2, 1, 1), ('etcetera:red_hat', 2, 1, 1), ('etcetera:yellow_hat', 2, 1, 1),
            ('candlelight:shirt', 2, 1, 1), ('candlelight:dress', 2, 1, 1), ('candlelight:trousers_and_vest', 2, 1, 1), ('candlelight:necktie', 2, 1, 1),
            ('candlelight:formal_shirt', 2, 1, 1), ('simplehats:hatbag_common', 2, 1, 1), ('simplehats:hatbag_uncommon', 1, 1, 1),
            ('beachparty:sunglasses', 2, 1, 1), ('beachparty:beach_hat', 1, 1, 1), ('minecraft:pink_dye', 3, 1, 3), ('minecraft:blue_dye', 3, 1, 3)]
OFFICE = [('minecraft:paper', 10, 3, 12), ('minecraft:book', 6, 1, 4), ('minecraft:writable_book', 4, 1, 2), ('minecraft:ink_sac', 4, 1, 3),
          ('minecraft:feather', 4, 1, 4), ('minecraft:map', 3, 1, 2), ('minecraft:compass', 2, 1, 1), ('minecraft:clock', 2, 1, 1),
          ('minecraft:name_tag', 1, 1, 1), ('minecraft:emerald', 2, 1, 3), ('minecraft:gold_nugget', 3, 2, 6), ('create:clipboard', 2, 1, 1),
          ('candlelight:note_paper_writeable', 3, 1, 2), ('candlelight:letter_closed', 2, 1, 2), ('farmersrespite:coffee', 4, 1, 2),
          ('minecraft:cookie', 3, 1, 4), ('numismatics:spur', 3, 2, 8), ('numismatics:bevel', 1, 1, 3), ('minecraft:redstone', 2, 1, 4),
          ('minecraft:glass_pane', 2, 1, 3), ('quark:abacus', 1, 1, 1)]
BANK = [('minecraft:gold_nugget', 8, 3, 12), ('minecraft:gold_ingot', 4, 1, 3), ('minecraft:emerald', 6, 1, 5), ('minecraft:diamond', 1, 1, 1),
        ('numismatics:spur', 8, 4, 16), ('numismatics:bevel', 5, 1, 6), ('numismatics:sprocket', 3, 1, 3), ('numismatics:cog', 2, 1, 2),
        ('minecraft:paper', 6, 2, 8), ('minecraft:book', 3, 1, 2), ('minecraft:writable_book', 2, 1, 1), ('minecraft:clock', 1, 1, 1),
        ('numismatics:banking_guide', 1, 1, 1)]
SCHOOL = [('minecraft:book', 10, 1, 4), ('minecraft:writable_book', 6, 1, 2), ('minecraft:paper', 8, 2, 10), ('minecraft:feather', 4, 1, 4),
          ('minecraft:ink_sac', 4, 1, 3), ('minecraft:map', 3, 1, 1), ('minecraft:compass', 2, 1, 1), ('minecraft:clock', 2, 1, 1),
          ('minecraft:spyglass', 1, 1, 1), ('minecraft:white_dye', 2, 1, 3), ('minecraft:red_dye', 2, 1, 3), ('minecraft:blue_dye', 2, 1, 3),
          ('minecraft:apple', 4, 1, 3), ('minecraft:cookie', 3, 1, 4), ('zetter:paints', 1, 1, 1), ('zetter:canvas', 2, 1, 2),
          ('quark:abacus', 1, 1, 1), ('minecraft:bookshelf', 1, 1, 1), ('minecraft:lectern', 1, 1, 1)]
CLINIC = [('minecraft:honey_bottle', 6, 1, 3), ('farmersdelight:milk_bottle', 3, 1, 2), ('minecraft:glass_bottle', 6, 1, 4),
          ('minecraft:golden_carrot', 3, 1, 2), ('minecraft:golden_apple', 1, 1, 1), ('minecraft:glistering_melon_slice', 2, 1, 2),
          ('minecraft:white_wool', 4, 1, 3), ('minecraft:paper', 4, 1, 4), ('supplementaries:soap', 4, 1, 2), ('farmersdelight:chicken_soup', 4, 1, 2),
          ('farmersdelight:bone_broth', 3, 1, 2), ('herbalbrews:green_tea', 4, 1, 2), ('herbalbrews:lavender_tea', 3, 1, 2),
          ('herbalbrews:rooibos_tea', 2, 1, 2), ('minecraft:sugar', 2, 1, 3), ('minecraft:apple', 3, 1, 3),
          ('legendarysurvivaloverhaul:healing_herbs', 6, 1, 3), ('legendarysurvivaloverhaul:plaster', 5, 1, 2)]
GROCERY = RAW_INGREDIENTS + FOOD_SNACK + [('minecraft:melon_slice', 4, 2, 6), ('minecraft:sweet_berries', 4, 2, 6), ('minecraft:pumpkin', 2, 1, 1),
                                          ('kaleidoscope_tavern:grape', 3, 2, 5),
                                          ('veggiesdelight:sweet_potato', 3, 1, 4), ('vintagedelight:cucumber', 3, 1, 4), ('vintagedelight:peanut', 3, 2, 6),
                                          ('minecraft:cooked_cod', 3, 1, 3), ('minecraft:cooked_salmon', 3, 1, 3)]
CAFE = DRINKS + BAKERY[:12] + [('farmersrespite:coffee_beans', 5, 2, 6), ('minecraft:sugar', 4, 1, 4), ('farmersdelight:milk_bottle', 4, 1, 3)]
RESTAURANT = MEALS + RAW_INGREDIENTS[:12] + [('farmersdelight:iron_knife', 1, 1, 1), ('farmersdelight:cooking_pot', 1, 1, 1),
                                             ('farmersdelight:skillet', 1, 1, 1), ('minecraft:bowl', 4, 1, 4)]
SUSHI = [('minecraft:cod', 6, 1, 4), ('minecraft:salmon', 6, 1, 4), ('farmersdelight:salmon_slice', 5, 1, 4), ('farmersdelight:cod_slice', 5, 1, 4),
         ('kaleidoscope_cookery:rice', 6, 2, 6), ('kaleidoscope_cookery:cooked_rice', 4, 1, 3), ('farmersdelight:kelp_roll', 4, 1, 2), ('farmersdelight:salmon_roll', 4, 1, 3),
         ('farmersdelight:cod_roll', 4, 1, 3), ('minecraft:dried_kelp', 6, 2, 8), ('kaleidoscope_cookery:sashimi', 3, 1, 2),
         ('crabbersdelight:shrimp', 3, 1, 4), ('crabbersdelight:cooked_shrimp', 3, 1, 3), ('crabbersdelight:clam_chowder', 2, 1, 1),
         ('herbalbrews:green_tea', 4, 1, 2), ('kaleidoscope_cookery:oolong_tea_bag', 2, 1, 2)]
WORKSHOP = CREATE_PARTS + TOOLS
LUXURY = [('minecraft:gold_nugget', 6, 2, 8), ('minecraft:emerald', 5, 1, 4), ('minecraft:gold_ingot', 2, 1, 2), ('minecraft:amethyst_shard', 3, 1, 4),
          ('minecraft:music_disc_13', 1, 1, 1), ('minecraft:music_disc_blocks', 1, 1, 1), ('minecraft:music_disc_chirp', 1, 1, 1),
          ('minecraft:music_disc_far', 1, 1, 1), ('minecraft:music_disc_strad', 1, 1, 1), ('minecraft:painting', 2, 1, 1),
          ('minecraft:candle', 3, 1, 3),            ('candlelight:wine_glass', 2, 1, 2), ('minecraft:diamond', 1, 1, 1), ('numismatics:bevel', 3, 1, 4),
          ('numismatics:sprocket', 2, 1, 2), ('kaleidoscope_tavern:champagne', 2, 1, 1), ('kaleidoscope_tavern:wine', 2, 1, 1),
          ('farmersdelight:apple_cider', 3, 1, 2), ('minecraft:cake', 1, 1, 1), ('minecraft:white_wool', 3, 1, 2), ('supplementaries:soap', 2, 1, 2),
          ('exposure:photograph', 1, 1, 1), ('simplehats:hatbag_uncommon', 1, 1, 1)]
GARAGE = [('create:andesite_alloy', 6, 2, 6), ('create:iron_sheet', 4, 1, 4), ('minecraft:iron_ingot', 4, 1, 3), ('minecraft:coal', 6, 2, 8),
           ('minecraft:charcoal', 4, 2, 6), ('minecraft:bucket', 1, 1, 1), ('minecraft:lava_bucket', 1, 1, 1), ('minecraft:chain', 3, 1, 3),
          ('create:wrench', 2, 1, 1), ('create:belt_connector', 3, 1, 2), ('create:fluid_pipe', 3, 2, 6), ('create:copper_sheet', 3, 1, 3),
          ('minecraft:minecart', 1, 1, 1), ('minecraft:rail', 3, 4, 12), ('minecraft:torch', 4, 4, 10), ('farmersdelight:hamburger', 2, 1, 1),
          ('farmersrespite:coffee', 3, 1, 2), ('minecraft:cookie', 2, 1, 3)]
CAMP = FOOD_SNACK + [('minecraft:torch', 8, 4, 12), ('minecraft:campfire', 2, 1, 1), ('minecraft:string', 4, 2, 6), ('minecraft:stick', 5, 2, 8),
                     ('minecraft:fishing_rod', 2, 1, 1), ('minecraft:cooked_cod', 3, 1, 3), ('minecraft:cooked_salmon', 3, 1, 3),
                     ('minecraft:oak_log', 4, 2, 6), ('minecraft:map', 1, 1, 1), ('minecraft:compass', 1, 1, 1), ('minecraft:bowl', 2, 1, 2),
                     ('farmersdelight:flint_knife', 1, 1, 1), ('minecraft:leather', 2, 1, 3), ('minecraft:white_bed', 1, 1, 1)]
CELLAR = [('kaleidoscope_tavern:grape', 6, 2, 5), ('vinery:white_grape', 6, 2, 5), ('kaleidoscope_tavern:grape_juice', 5, 1, 3),
          ('vinery:white_grapejuice', 5, 1, 3), ('vinery:apple_juice', 4, 1, 3), ('farmersdelight:apple_cider', 3, 1, 2),
          ('vinery:cherry_wine', 3, 1, 2), ('vinery:apple_wine', 3, 1, 2), ('vinery:aegis_wine', 2, 1, 1),
          ('vinery:chenet_wine', 2, 1, 1), ('vinery:bolvar_wine', 2, 1, 1), ('vinery:clark_wine', 2, 1, 1),
          ('vinery:cristel_wine', 1, 1, 1), ('vinery:red_grape_seeds', 4, 1, 3), ('vinery:white_grape_seeds', 4, 1, 3),
          ('kaleidoscope_tavern:wine', 3, 1, 2), ('kaleidoscope_tavern:champagne', 2, 1, 1), ('kaleidoscope_tavern:honey_wine', 2, 1, 2),
          ('kaleidoscope_tavern:ice_wine', 1, 1, 1), ('kaleidoscope_tavern:watermelon_juice', 3, 1, 2),
          ('candlelight:wine_glass', 2, 1, 2), ('farmersdelight:apple_cider', 3, 1, 2), ('minecraft:glass_bottle', 4, 1, 3),
          ('minecraft:barrel', 1, 1, 1)]
DOCK = [('minecraft:cod', 6, 1, 4), ('minecraft:salmon', 6, 1, 4), ('minecraft:cooked_cod', 4, 1, 3), ('minecraft:cooked_salmon', 4, 1, 3),
        ('farmersdelight:salmon_slice', 4, 1, 3), ('farmersdelight:cod_slice', 4, 1, 3), ('farmersdelight:kelp_roll', 3, 1, 2),
        ('crabbersdelight:shrimp', 3, 1, 4), ('crabbersdelight:cooked_shrimp', 3, 1, 3), ('minecraft:fishing_rod', 2, 1, 1),
        ('supplementaries:rope', 5, 2, 6), ('minecraft:lead', 3, 1, 2), ('minecraft:lantern', 3, 1, 2), ('minecraft:torch', 5, 2, 8),
        ('minecraft:barrel', 2, 1, 1), ('minecraft:oak_boat', 1, 1, 1), ('minecraft:water_bucket', 2, 1, 1),
        ('minecraft:oak_planks', 3, 2, 6), ('minecraft:stick', 4, 2, 6), ('kaleidoscope_cookery:sashimi', 2, 1, 2),
        ('farmersdelight:apple_cider', 2, 1, 2), ('minecraft:map', 1, 1, 1)]

# deposito: equipamento bom (encantado), materiais de nether/end e pecas de mods que dao trabalho.
# 5o campo True = sai encantado (enchant_with_levels 20-35, inclui encantamentos de tesouro).
DEP_GEAR = [(f'minecraft:diamond_{p}', 4, 1, 1, True) for p in ('sword', 'pickaxe', 'axe', 'shovel', 'helmet', 'chestplate', 'leggings', 'boots')] + \
    [(f'minecraft:netherite_{p}', 1, 1, 1, True) for p in ('sword', 'pickaxe', 'axe', 'helmet', 'chestplate', 'leggings', 'boots')] + \
    [(f'minecraft:iron_{p}', 3, 1, 1, True) for p in ('sword', 'helmet', 'chestplate', 'leggings', 'boots')] + \
    [('minecraft:chainmail_chestplate', 2, 1, 1, True), ('minecraft:trident', 1, 1, 1, True), ('minecraft:crossbow', 3, 1, 1, True),
     ('minecraft:bow', 3, 1, 1, True), ('minecraft:shield', 3, 1, 1), ('minecraft:elytra', 1, 1, 1)] + \
    [(f'aquaculture:neptunium_{p}', 2, 1, 1, True) for p in ('sword', 'pickaxe', 'axe', 'helmet', 'chestplate', 'leggings', 'boots', 'fishing_rod')] + \
    [('botania:manasteel_sword', 2, 1, 1, True), ('botania:manasteel_pick', 2, 1, 1, True), ('botania:manasteel_chestplate', 2, 1, 1, True),
     ('botania:terrasteel_helmet', 1, 1, 1, True), ('botania:terrasteel_chestplate', 1, 1, 1, True), ('botania:elementium_sword', 1, 1, 1, True),
     ('botania:elementium_pickaxe', 1, 1, 1, True), ('farmersdelight:diamond_knife', 3, 1, 1, True), ('farmersdelight:netherite_knife', 1, 1, 1, True),
     ('hearthandharvest:netherite_cleaver', 1, 1, 1, True), ('justhammers:diamond_hammer', 2, 1, 1, True), ('justhammers:netherite_hammer', 1, 1, 1, True),
     ('create:netherite_diving_helmet', 1, 1, 1, True), ('create:netherite_diving_boots', 1, 1, 1, True), ('create:netherite_backtank', 1, 1, 1),
     ('create:copper_diving_helmet', 2, 1, 1), ('create:copper_backtank', 2, 1, 1), ('minecraft:diamond_horse_armor', 2, 1, 1)]
DEP_MATERIALS = [('minecraft:diamond', 6, 1, 4), ('minecraft:emerald', 6, 2, 8), ('minecraft:netherite_scrap', 3, 1, 2), ('minecraft:netherite_ingot', 1, 1, 1),
                 ('minecraft:netherite_scrap', 2, 1, 2), ('minecraft:blaze_rod', 6, 2, 6), ('minecraft:ghast_tear', 4, 1, 3), ('minecraft:magma_cream', 4, 2, 5),
                 ('minecraft:quartz', 6, 4, 16), ('minecraft:glowstone_dust', 5, 4, 12), ('minecraft:nether_wart', 5, 3, 9), ('minecraft:crying_obsidian', 3, 2, 6),
                 ('minecraft:ender_pearl', 6, 2, 6), ('minecraft:ender_eye', 3, 1, 3), ('minecraft:shulker_shell', 3, 1, 2), ('minecraft:chorus_fruit', 4, 3, 8),
                 ('minecraft:popped_chorus_fruit', 3, 2, 6), ('minecraft:dragon_breath', 2, 1, 3), ('minecraft:end_rod', 3, 2, 6), ('minecraft:purpur_block', 3, 4, 12),
                 ('minecraft:echo_shard', 2, 1, 3), ('minecraft:amethyst_shard', 4, 3, 9), ('minecraft:nautilus_shell', 2, 1, 2), ('minecraft:experience_bottle', 5, 4, 16),
                 ('create:precision_mechanism', 4, 1, 3), ('create:brass_hand', 3, 1, 2), ('create:sturdy_sheet', 3, 1, 4), ('create:electron_tube', 4, 2, 6),
                 ('create:rose_quartz', 4, 2, 6), ('create:polished_rose_quartz', 3, 2, 4), ('create:brass_ingot', 5, 3, 8), ('create:chromatic_compound', 1, 1, 1),
                 ('create:refined_radiance', 1, 1, 2), ('create:shadow_steel', 1, 1, 2), ('create:track', 3, 8, 24), ('create:brass_casing', 3, 2, 6),
                 ('aquaculture:neptunium_ingot', 3, 1, 3), ('botania:manasteel_ingot', 4, 2, 5), ('botania:terrasteel_ingot', 2, 1, 2),
                 ('botania:elementium_ingot', 2, 1, 3), ('botania:mana_diamond', 2, 1, 2), ('botania:dragonstone', 2, 1, 2), ('botania:pixie_dust', 2, 1, 3),
                 ('botania:mana_pearl', 3, 1, 3), ('createdeco:netherite_sheet', 1, 1, 2), ('waystones:warp_stone', 2, 1, 1), ('waystones:warp_scroll', 4, 1, 3),
                 ('waystones:bound_scroll', 3, 1, 2), ('waystones:attuned_shard', 2, 1, 1), ('paraglider:spirit_orb', 2, 1, 2)]
# 2026-10-10 (pedido do dono): NENHUMA backpack em bau de cidade (nem base, nem tiers, nem upgrades).
DEP_DEVICES = [('create:blaze_burner', 3, 1, 1), ('create:mechanical_arm', 2, 1, 1), ('create:wand_of_symmetry', 1, 1, 1), ('create:extendo_grip', 2, 1, 1),
               ('create:potato_cannon', 2, 1, 1), ('create:linked_controller', 2, 1, 1), ('create:schematicannon', 1, 1, 1), ('create:mechanical_crafter', 2, 1, 4),
               ('create:rotation_speed_controller', 2, 1, 1), ('create:sequenced_gearshift', 2, 1, 2), ('create:display_board', 2, 2, 6), ('create:redstone_link', 3, 2, 4),
               ('create:package_frogport', 2, 1, 2), ('create:stock_link', 2, 1, 1),
               ('functionalstorage:diamond_upgrade', 2, 1, 2), ('functionalstorage:netherite_upgrade', 1, 1, 1), ('constructionstick:diamond_stick', 2, 1, 1),
               ('constructionstick:netherite_stick', 1, 1, 1), ('dew_drop_watering_cans:diamond_watering_can', 2, 1, 1),
               ('dew_drop_watering_cans:netherite_watering_can', 1, 1, 1), ('botania:mana_tablet', 2, 1, 1), ('botania:rune_mana', 2, 1, 2),
               ('botania:flight_tiara', 1, 1, 1), ('buildinggadgets2:gadget_building', 1, 1, 1), ('toolbelt:belt', 2, 1, 1), ('toolbelt:pouch', 3, 1, 2),
                ('paraglider:paraglider', 1, 1, 1), ('minecraft:spyglass', 1, 1, 1), ('minecraft:name_tag', 3, 1, 2), ('minecraft:saddle', 3, 1, 1)]
DEP_RARE = [('minecraft:enchanted_golden_apple', 2, 1, 1), ('minecraft:golden_apple', 8, 1, 3), ('minecraft:totem_of_undying', 2, 1, 1),
            ('minecraft:nether_star', 1, 1, 1), ('minecraft:wither_skeleton_skull', 2, 1, 1), ('minecraft:heart_of_the_sea', 2, 1, 1),
            ('minecraft:netherite_upgrade_smithing_template', 2, 1, 1), ('minecraft:end_crystal', 2, 1, 2), ('minecraft:shulker_box', 2, 1, 1),
            ('minecraft:beacon', 1, 1, 1), ('minecraft:dragon_head', 1, 1, 1), ('minecraft:music_disc_pigstep', 1, 1, 1), ('minecraft:music_disc_otherside', 1, 1, 1),
            ('minecraft:recovery_compass', 2, 1, 1), ('minecraft:respawn_anchor', 1, 1, 1), ('minecraft:lodestone', 2, 1, 1), ('minecraft:netherite_block', 1, 1, 1),
            ('botania:gaia_ingot', 1, 1, 1), ('aquaculture:nether_star_hook', 1, 1, 1), ('minecraft:enchanted_book', 6, 1, 1, True)]

# temas com varias pools (rolls_min, rolls_max, entradas) por pool
MULTI = {
    'deposito': [(2, 4, DEP_GEAR), (3, 6, DEP_MATERIALS), (1, 3, DEP_DEVICES), (0, 1, DEP_RARE)],
}

THEMES = {
    'kitchen': (2, 5, RAW_INGREDIENTS + FOOD_SNACK + [('farmersdelight:cooking_pot', 2, 1, 1), ('farmersdelight:skillet', 2, 1, 1),
                                                     ('farmersdelight:cutting_board', 2, 1, 1), ('farmersdelight:iron_knife', 1, 1, 1),
                                                     ('minecraft:bowl', 3, 1, 4)]),
    'fridge': (3, 6, RAW_INGREDIENTS[:12] + [('minecraft:cooked_chicken', 4, 1, 2), ('minecraft:cooked_beef', 3, 1, 2)] + DRINKS[:6] + MEALS[:8]),
    'home': (2, 5, HOME + SEEDS[:6]),
    'bedroom': (2, 4, BEDROOM),
    'bathroom': (1, 3, BATHROOM),
    'workshop': (3, 6, WORKSHOP),
    'garage': (2, 5, GARAGE),
    'grocery': (3, 7, GROCERY),
    'cafe': (3, 6, CAFE),
    'restaurant': (3, 6, RESTAURANT),
    'sushi': (3, 6, SUSHI),
    'bakery': (3, 6, BAKERY),
    'flowers': (3, 6, FLOWERS),
    'floricultura': (3, 6, FLOWERS[:4] + SEEDS[:4] + [('dew_drop_farmland_growth:weak_fertilizer', 5, 1, 3),
                     ('dew_drop_farmland_growth:hydrating_fertilizer', 3, 1, 2), ('quark:seed_pouch', 2, 1, 1),
                     ('dew_drop_watering_cans:copper_watering_can', 1, 1, 1), ('dew_drop_farmland_growth:iron_sprinkler', 1, 1, 1)]),
    'adega': (3, 6, CELLAR + [('minecraft:glass_bottle', 8, 2, 6), ('minecraft:honey_bottle', 3, 1, 2)]),
    'torre_raio': (2, 5, [('minecraft:blaze_rod', 4, 1, 3), ('minecraft:copper_ingot', 8, 2, 6), ('minecraft:copper_block', 3, 1, 2),
                          ('minecraft:lightning_rod', 4, 1, 2), ('minecraft:redstone', 6, 2, 6), ('minecraft:iron_nugget', 4, 3, 9)]),
    'laticinio': (1, 3, [('society:animal_feed_sack', 3, 1, 2), ('society:steamed_milk', 1, 1, 1), ('minecraft:cake', 1, 1, 1)]),
    'vinicola': (2, 4, CELLAR[:4] + [('minecraft:glass_bottle', 6, 1, 4)]),
    'celeiro_neve': (1, 3, [('legendarysurvivaloverhaul:heating_coat_1', 2, 1, 1), ('legendarysurvivaloverhaul:heating_coat_2', 1, 1, 1)]),
    'cabana_pescador': (1, 3, [('crabbersdelight:crab_trap_bait', 3, 1, 3), ('minecraft:cod', 2, 1, 2)]),
    'alfaiataria': (1, 3, [('legendarysurvivaloverhaul:heating_coat_1', 2, 1, 1), ('legendarysurvivaloverhaul:cooling_coat_1', 2, 1, 1),
                           ('legendarysurvivaloverhaul:thermometer', 2, 1, 1)]),
    'seringueiro': (2, 4, [('society:maple_syrup', 3, 1, 2), ('society:pine_tar', 2, 1, 2), ('meadow:wooden_bucket', 1, 1, 1),
                           ('minecraft:copper_block', 2, 1, 2), ('meadow:fire_log', 2, 1, 3), ('society:earth_crystal', 1, 1, 1)]),
    'clothing': (2, 5, CLOTHING),
    'office': (2, 5, OFFICE),
    'bank': (3, 6, BANK),
    'school': (2, 5, SCHOOL),
    'clinic': (2, 5, CLINIC),
    'farm': (3, 6, FARM),
    'camp': (2, 5, CAMP),
    'luxury': (2, 5, LUXURY),
    'cellar': (2, 5, CELLAR),
    'dock': (2, 5, DOCK),
    'deposito': (0, 0, []),  # pools reais em MULTI
}


# ---------------------------------------------------------------- pools extras (2026-10-04)
# Comida fica nos containers de cozinha/mercado/padaria. O resto (casa, quarto, banheiro, oficina, escritorio...)
# ganha, alem do proprio tema: equipamento (ferramentas e armaduras gastas, as vezes encantadas), bebidas de
# todo tipo (o modpack tem sede: agua purificada, sucos, chas, cafes, vinhos, cervejas e pocoes), coisas para
# FAZER comida (utensilios e ingredientes crus) e itens aleatorios dos mods.
LANG_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lang_items.json')
MODS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'mods')


def _lang_ids():
    """ids com nome traduzido (item.ns.x / block.ns.x) nos en_us.json dos jars: o registry.json vem dos modelos e tem
    variantes que nao sao itens (naturescompass_09, camera_active); item inexistente invalida a loot table inteira"""
    jars = sorted(glob.glob(os.path.join(MODS, '*.jar')))
    # 'v2' marks the BOM-tolerant parser; bumping it rebuilds caches written by the old parser
    stamp = ['v2'] + [os.path.basename(j) for j in jars]
    if os.path.exists(LANG_CACHE):
        d = json.load(open(LANG_CACHE))
        if d.get('jars') == stamp:
            return set(d['ids'])
    ids = set()
    for j in jars:
        try:
            z = zipfile.ZipFile(j)
        except zipfile.BadZipFile:
            continue
        for n in z.namelist():
            if not re.match(r'^assets/[^/]+/lang/en_us\.json$', n):
                continue
            try:
                keys = json.loads(z.read(n).decode('utf-8-sig', 'replace'))
            except ValueError:
                continue
            for k in keys:
                m = re.match(r'^(item|block)\.([a-z0-9_.-]+)\.([a-z0-9_./-]+)$', k)
                if m:
                    ids.add(f'{m.group(2)}:{m.group(3)}')
    json.dump({'jars': stamp, 'ids': sorted(ids)}, open(LANG_CACHE, 'w'))
    return ids


LANG = _lang_ids()


GAME_REG = os.path.join(os.path.dirname(MODS), 'kubejs', 'exported', 'sunlit_registry.json')
GAME_ITEMS = set(json.load(open(GAME_REG))['items']) if os.path.exists(GAME_REG) else None


KJS_CREATE_RX = re.compile(r'''create\(\s*['"]([a-z0-9_.-]+:[a-z0-9_./-]+)['"]''')


def _kjs_ids():
    """ids registrados por KubeJS (e.create('ns:id') em kubejs/startup_scripts): itens sem modelo no jar"""
    ids = set()
    for f in glob.glob(os.path.join(os.path.dirname(MODS), 'kubejs', 'startup_scripts', '**', '*.js'), recursive=True):
        try:
            ids.update(KJS_CREATE_RX.findall(open(f, encoding='utf-8', errors='replace').read()))
        except OSError:
            continue
    return ids


KJS_ITEMS = _kjs_ids()


def real_item(i):
    """registro do jogo (exportado pelo sunlitTownsCheck.js) quando existe; senao modelo/KubeJS + nome traduzido"""
    if GAME_ITEMS is not None:
        return i in GAME_ITEMS or i in KJS_ITEMS
    return (item_ok(i) or i in KJS_ITEMS) and (i.startswith('minecraft:') or i in LANG or i in KJS_ITEMS)


GEAR_RX = re.compile(r'_(pickaxe|axe|shovel|hoe|sword|knife|machete|helmet|chestplate|leggings|boots|fishing_rod|shears|'
                     r'watering_can|net|bow|crossbow|shield|spear|scythe|sickle|hammer|chisel|cap|hat)$|^minecraft:(bow|crossbow|shield|'
                     r'fishing_rod|shears|flint_and_steel|spyglass|compass|clock|lead|brush)$')
GEAR_SKIP = re.compile(r'netherite|_trim$|2d|3d|/|blocking|creative|spawn_egg|_\d+$|^gecko|^botania:|^relics:|^railways:|^simplehats:|'
                       r'^buildinggadgets2:|^constructionstick:|^refinedstorage:|^create:cardboard|^splendid_slimes:|^species:')
DAMAGEABLE = re.compile(r'_(pickaxe|axe|shovel|hoe|sword|knife|machete|helmet|chestplate|leggings|boots|fishing_rod|shears|bow|'
                        r'crossbow|shield|spear|scythe|sickle|hammer|chisel)$|^minecraft:(bow|crossbow|shield|fishing_rod|shears|'
                        r'flint_and_steel|brush)$')


def _gear():
    out = []
    for i in sorted(ITEMS):
        if i in REG['blocks'] or not real_item(i) or not GEAR_RX.search(i) or GEAR_SKIP.search(i):
            continue
        w = 1 if re.search(r'diamond|electrum|neptunium|golden_|gold_', i) else (2 if re.search(r'iron|copper|chainmail', i) else 3)
        out.append((i, w, 1, 1, {'damage': bool(DAMAGEABLE.search(i)), 'ench': bool(DAMAGEABLE.search(i))}))
    return out


GEAR = _gear()

POTIONS = ['water', 'healing', 'regeneration', 'swiftness', 'night_vision', 'fire_resistance', 'water_breathing',
           'strength', 'leaping', 'slow_falling', 'invisibility', 'long_regeneration', 'strong_healing']
DRINKS_ALL = [('legendarysurvivaloverhaul:purified_water_bottle', 12, 1, 3), ('legendarysurvivaloverhaul:canteen_purified', 2, 1, 1),
              ('legendarysurvivaloverhaul:apple_juice', 4, 1, 2), ('legendarysurvivaloverhaul:carrot_juice', 3, 1, 2),
              ('legendarysurvivaloverhaul:beetroot_juice', 3, 1, 2), ('legendarysurvivaloverhaul:melon_juice', 4, 1, 2),
              ('legendarysurvivaloverhaul:pumpkin_juice', 3, 1, 2), ('legendarysurvivaloverhaul:sweet_berries_juice', 3, 1, 2),
              ('legendarysurvivaloverhaul:glow_berries_juice', 2, 1, 2), ('legendarysurvivaloverhaul:cactus_juice', 2, 1, 2),
              ('legendarysurvivaloverhaul:chorus_fruit_juice', 1, 1, 1), ('legendarysurvivaloverhaul:golden_apple_juice', 1, 1, 1),
              ('legendarysurvivaloverhaul:golden_carrot_juice', 1, 1, 1),
              ('farmersdelight:milk_bottle', 4, 1, 2), ('farmersdelight:hot_cocoa', 3, 1, 2), ('farmersdelight:apple_cider', 3, 1, 2),
              ('kaleidoscope_tavern:watermelon_juice', 3, 1, 2), ('farmersrespite:green_tea', 3, 1, 2), ('farmersrespite:yellow_tea', 2, 1, 2),
              ('farmersrespite:black_tea', 3, 1, 2), ('farmersrespite:rose_hip_tea', 2, 1, 2), ('farmersrespite:dandelion_tea', 2, 1, 2),
              ('farmersrespite:coffee', 3, 1, 2), ('farmersrespite:long_coffee', 1, 1, 1), ('farmersrespite:strong_black_tea', 1, 1, 1),
              ('farmersrespite:coffee', 3, 1, 2), ('herbalbrews:milk_coffee', 2, 1, 2), ('herbalbrews:green_tea', 2, 1, 2),
              ('herbalbrews:black_tea', 2, 1, 2), ('herbalbrews:hibiscus_tea', 2, 1, 2), ('herbalbrews:lavender_tea', 2, 1, 2),
              ('kaleidoscope_cookery:oolong', 2, 1, 2), ('herbalbrews:rooibos_tea', 2, 1, 2), ('herbalbrews:yerba_mate_tea', 2, 1, 2),
              ('herbalbrews:herbal_infusion', 2, 1, 1), ('farmersrespite:green_tea', 2, 1, 2), ('kaleidoscope_cookery:oolong', 2, 1, 2),
              ('youkaishomecoming:white_tea', 2, 1, 2), ('youkaishomecoming:latte', 2, 1, 2), ('youkaishomecoming:sakura_honey_tea', 2, 1, 2),
              ('youkaishomecoming:lemon_black_tea', 2, 1, 2), ('kaleidoscope_tavern:grape_juice', 2, 1, 2),
              ('youkaishomecoming:white_grape_juice', 2, 1, 2), ('youkaishomecoming:sake_bottle', 1, 1, 1), ('youkaishomecoming:red_wine', 1, 1, 1),
              ('youkaishomecoming:white_wine', 1, 1, 1), ('kaleidoscope_tavern:honey_wine', 1, 1, 1),
              ('hearthandharvest:blueberry_juice', 2, 1, 2), ('hearthandharvest:cherry_juice', 2, 1, 2), ('hearthandharvest:raspberry_juice', 2, 1, 2),
              ('kaleidoscope_tavern:grape_juice', 2, 1, 2), ('kaleidoscope_tavern:green_grape_juice', 2, 1, 2), ('hearthandharvest:goat_milk_bottle', 2, 1, 2),
              ('kaleidoscope_tavern:honey_wine', 1, 1, 1), ('hearthandharvest:cherry_wine', 1, 1, 1), ('hearthandharvest:blueberry_wine', 1, 1, 1),
              ('vinery:apple_juice', 2, 1, 2), ('kaleidoscope_tavern:grape_juice', 2, 1, 2), ('vinery:white_grapejuice', 2, 1, 2), ('farmersdelight:apple_cider', 2, 1, 1),
              ('vinery:red_wine', 1, 1, 1), ('vinery:cherry_wine', 1, 1, 1), ('vinery:apple_wine', 1, 1, 1), ('vinery:noir_wine', 1, 1, 1),
              ('kaleidoscope_tavern:honey_wine', 1, 1, 1), ('nethervinery:crimson_grapejuice', 1, 1, 1), ('nethervinery:warped_grapejuice', 1, 1, 1),
              ('brewinandchewin:beer', 1, 1, 1), ('kaleidoscope_tavern:honey_wine', 1, 1, 1), ('brewinandchewin:rice_wine', 1, 1, 1),
              ('brewinandchewin:egg_grog', 1, 1, 1), ('brewinandchewin:kombucha', 1, 1, 1), ('brewery:beer_wheat', 1, 1, 1),
              ('brewery:beer_barley', 1, 1, 1), ('brewery:beer_hops', 1, 1, 1), ('veggiesdelight:carrot_juice', 2, 1, 2),
              ('crabbersdelight:kelp_shake', 1, 1, 1), ('farm_and_charm:strawberry_tea', 2, 1, 2), ('farm_and_charm:nettle_tea', 1, 1, 2),
              ('windswept:ginger_tea', 1, 1, 2), ('windswept:lavender_tea', 1, 1, 2), ('miners_delight:milk_cup', 1, 1, 2),
               ('miners_delight:water_cup', 2, 1, 2), ('minecraft:honey_bottle', 3, 1, 2), ('farmersdelight:milk_bottle', 1, 1, 1),
              ('kaleidoscope_tavern:watermelon_juice', 1, 1, 2), ('quarkdelight:cloud_latte', 1, 1, 1)] + \
             [('minecraft:potion', 4 if p == 'water' else 2, 1, 2, {'potion': p}) for p in POTIONS] + \
             [('minecraft:splash_potion', 1, 1, 1, {'potion': p}) for p in ('healing', 'regeneration', 'swiftness')]

COOK_SUPPLY = [('farmersdelight:cooking_pot', 2, 1, 1), ('farmersdelight:skillet', 2, 1, 1), ('farmersdelight:cutting_board', 2, 1, 1),
               ('farmersdelight:flint_knife', 2, 1, 1), ('farmersdelight:iron_knife', 1, 1, 1), ('bakery:rolling_pin', 1, 1, 1),
               ('bakery:bread_knife', 1, 1, 1), ('farm_and_charm:cooking_saucepan', 1, 1, 1), ('candlelight:cooking_pot', 1, 1, 1),
               ('minecraft:bowl', 3, 1, 4), ('minecraft:glass_bottle', 3, 1, 4), ('minecraft:bucket', 1, 1, 1),
                ('kaleidoscope_cookery:flour', 4, 1, 4), ('kaleidoscope_cookery:flour', 2, 1, 4), ('kaleidoscope_cookery:raw_dough', 3, 1, 3),
                ('farm_and_charm:yeast', 2, 1, 3), ('farm_and_charm:butter', 2, 1, 2), ('vintagedelight:salt', 3, 1, 4),
               ('meadow:alpine_salt', 2, 1, 4), ('meadow:rennet', 1, 1, 2), ('minecraft:sugar', 4, 1, 4), ('minecraft:egg', 4, 1, 4),
               ('kaleidoscope_cookery:oil', 2, 1, 2), ('vintagedelight:vinegar_bottle', 1, 1, 2), ('youkaishomecoming:soy_sauce_bottle', 1, 1, 2),
               ('youkaishomecoming:mayonnaise_bottle', 1, 1, 2), ('farmersdelight:tomato_sauce', 1, 1, 2), ('hearthandharvest:peanut_butter', 1, 1, 2),
               ('kaleidoscope_cookery:rice', 3, 1, 4), ('kaleidoscope_cookery:tomato', 3, 1, 4), ('farmersdelight:cabbage', 3, 1, 3), 
               ('veggiesdelight:garlic', 2, 1, 3), ('minecraft:wheat', 3, 2, 6), ('minecraft:beef', 2, 1, 3), ('minecraft:porkchop', 2, 1, 3), ('minecraft:chicken', 2, 1, 3),
               ('minecraft:mutton', 2, 1, 3), ('minecraft:cod', 2, 1, 3), ('minecraft:salmon', 2, 1, 3), ('minecraft:cocoa_beans', 2, 1, 3),
               ('farmersrespite:coffee_beans', 2, 1, 4), ('farmersrespite:green_tea_leaves', 2, 1, 4), ('farmersrespite:coffee_beans', 1, 1, 3),
               ('kaleidoscope_cookery:chili_seed', 1, 1, 2)]

# ---------------------------------------------------------------- niveis de bau (2026-10-05, rev. 2026-10-06)
# Cada bau sorteia um nivel em jogo (sunlitTownsLoot.js, gerado abaixo). Regra do projeto (AGENTS.md):
# todo bau comum tem 1 drop de mob, 1 comida OU 1 bebida, warm/cold strings, 1 equipamento e 1 material:
# - comum (a maioria): 1 a 3 itens "de verdade" (o tema do container primeiro, depois o proprio tema,
#   por ultimo BASIC), 1 equipamento (MACHINE_COMMON: ferramenta e miudeza vanilla, nunca Create e nunca
#   a bancada que ja existe como mobilia no mapa), 1 material (BASIC_MATERIALS, sem Create), 1 comida OU
#   1 bebida (nunca os dois), warm/cold strings (1 a 3) e pouco preenchimento de mob (1 a 3 drops), sem
#   repetir item;
# - rico (raro, e o deposito sempre): 4 a 6 itens de qualquer nivel (RICH, aleatorio), no maximo 3
#   strings e sem comida/bebida, mesmo preenchimento pequeno de mob.
# O preenchimento e so ESPACO VAZIO com drops de mobs (MOB_DROPS, com blaze_rod raro): nao e loot de
# verdade, so faz o bau parecer habitado. Itens removidos/escondidos pelo modpack, guias e itens com icone
# quebrado nunca entram (itemcheck.bad_item aqui e o registro do jogo + global.removedItems em jogo).
TIER_OK = re.compile(r'(^|:|_)(wood|wooden|stone|leather|chainmail|copper|iron|gold|golden|flint|bone|bamboo|steel|bronze|'
                     r'silver|rose_gold)_|^minecraft:(bow|crossbow|shield|fishing_rod|shears|flint_and_steel|spyglass|'
                     r'compass|clock|lead|brush)$')
TIER_HIGH = re.compile(r'diamond|netherite|neptunium|electrum|manasteel|terrasteel|elementium|obsidian|emerald|amethyst|'
                       r'enderite|dragon|warden|crystal')

BASIC_MACHINES = [('minecraft:crafting_table', 3, 1, 1), ('minecraft:furnace', 4, 1, 1), ('minecraft:smoker', 2, 1, 1),
                  ('minecraft:blast_furnace', 1, 1, 1), ('minecraft:chest', 3, 1, 1), ('minecraft:barrel', 3, 1, 1),
                  ('minecraft:composter', 2, 1, 1), ('minecraft:grindstone', 2, 1, 1), ('minecraft:stonecutter', 2, 1, 1),
                   ('minecraft:smithing_table', 1, 1, 1), ('minecraft:cauldron', 1, 1, 1), ('minecraft:hopper', 1, 1, 1),
                   ('minecraft:chipped_anvil', 1, 1, 1),
                  ('create:hand_crank', 3, 1, 1), ('create:water_wheel', 2, 1, 2), ('create:shaft', 4, 2, 8),
                  ('create:cogwheel', 4, 1, 4), ('create:large_cogwheel', 3, 1, 2), ('create:andesite_casing', 3, 1, 4),
                  ('create:gearbox', 2, 1, 2), ('create:millstone', 2, 1, 1), ('create:encased_fan', 2, 1, 1),
                  ('create:mechanical_press', 2, 1, 1), ('create:mechanical_mixer', 1, 1, 1), ('create:basin', 2, 1, 1),
                  ('create:depot', 2, 1, 1), ('create:belt_connector', 2, 1, 4), ('create:wrench', 2, 1, 1),
                  ('create:goggles', 2, 1, 1), ('create:chute', 1, 1, 2), ('create:andesite_funnel', 1, 1, 2),
                  ('create:windmill_bearing', 1, 1, 1), ('create:mechanical_saw', 1, 1, 1), ('create:mechanical_drill', 1, 1, 1),
                  ('create:mechanical_harvester', 1, 1, 1), ('create:mechanical_plough', 1, 1, 1),
                  ('create:fluid_pipe', 1, 2, 6), ('create:mechanical_pump', 1, 1, 1), ('create:fluid_tank', 1, 1, 1),
                   ('farmersdelight:cooking_pot', 2, 1, 1), ('farmersdelight:stove', 1, 1, 1), ('farmersdelight:skillet', 2, 1, 1),
                   ('farmersdelight:cutting_board', 2, 1, 1), ('farmersdelight:basket', 1, 1, 1),
                   ('minecraft:loom', 2, 1, 1), ('minecraft:fletching_table', 2, 1, 1), ('minecraft:cartography_table', 2, 1, 1),
                   ('minecraft:enchanting_table', 1, 1, 1),
                   ('toolbelt:pouch', 1, 1, 1)]
BASIC_MATERIALS = [('minecraft:iron_ingot', 6, 1, 4), ('minecraft:iron_nugget', 6, 3, 9), ('minecraft:raw_iron', 4, 1, 4),
                   ('minecraft:copper_ingot', 6, 2, 6), ('minecraft:raw_copper', 4, 1, 4), ('minecraft:gold_nugget', 3, 2, 6),
                   ('minecraft:gold_ingot', 1, 1, 2), ('minecraft:coal', 7, 2, 8), ('minecraft:charcoal', 4, 2, 6),
                   ('minecraft:string', 4, 2, 6), ('minecraft:leather', 4, 1, 4), ('minecraft:flint', 4, 1, 4),
                   ('minecraft:stick', 4, 4, 12), ('minecraft:oak_planks', 3, 4, 12), ('minecraft:spruce_planks', 3, 4, 12),
                   ('minecraft:oak_log', 3, 2, 6), ('minecraft:cobblestone', 3, 8, 24), ('minecraft:glass', 3, 2, 8),
                   ('minecraft:clay_ball', 3, 2, 8), ('minecraft:brick', 2, 2, 8), ('minecraft:paper', 3, 2, 8),
                   ('minecraft:book', 2, 1, 2), ('minecraft:white_wool', 3, 1, 4), ('minecraft:redstone', 3, 2, 8),
                   ('minecraft:lapis_lazuli', 2, 1, 6), ('minecraft:quartz', 2, 1, 6), ('minecraft:torch', 5, 4, 16),
                   ('minecraft:ladder', 2, 2, 8), ('minecraft:slime_ball', 1, 1, 3), ('minecraft:bone_meal', 3, 2, 8),
                   ('minecraft:oak_sapling', 2, 1, 3), ('minecraft:birch_sapling', 2, 1, 3), ('minecraft:wheat_seeds', 3, 2, 8),
                   ('minecraft:gunpowder', 1, 1, 3), ('minecraft:arrow', 2, 4, 12), ('minecraft:name_tag', 1, 1, 1),
                   ('supplementaries:rope', 2, 4, 12)]


WEAPON_RX = re.compile(r'_(sword|knife|machete|helmet|chestplate|leggings|boots|bow|crossbow|shield|spear|scythe|sickle)$'
                       r'|^minecraft:(bow|crossbow|shield)$')


def _basic_gear():
    out = []
    for i, w, a, b, opt in GEAR:
        if TIER_HIGH.search(i) or not TIER_OK.search(i):
            continue
        # 2026-10-10: picareta de bau comum e nivel pedra (madeira/pedra); ferro/dourado
        # pra cima nao sai no comum (fica para bau rico/deposito)
        if '_pickaxe' in i and not re.search(r'(wooden|stone)_pickaxe', i):
            continue
        # 2026-10-10: spyglass quase nao spawna (so no deposito raro e na escola)
        if i == 'minecraft:spyglass':
            continue
        # arma/armadura pronta quase nao sai em bau comum (peso 1): o grosso e ferramenta e material;
        # o acabado (encantado forte, endgame) fica para bau rico/deposito
        if WEAPON_RX.search(i):
            w = 1
        out.append((i, w, a, b, dict(opt)))
    return out


# cura basica em todo bau comum + livro encantado leve e frasco de XP (pocoes ja vem pela pool de bebidas)
HEALING = [('legendarysurvivaloverhaul:healing_herbs', 6, 1, 3), ('legendarysurvivaloverhaul:plaster', 5, 1, 2),
           ('minecraft:enchanted_book', 2, 1, 1, {'ench': True}), ('minecraft:experience_bottle', 2, 2, 6)]


# blocos que as towns colocam como mobilia (clutter, vanilla_furni, remodel, parques): nao saem em
# bau comum (o jogador ja encontra de graca pelo mapa; ex. o blast_furnace da oficina). Utensilio
# nativo do tema continua saindo pela loot table do proprio tema no datapack (panela na cozinha);
# o deposito (RICH, sempre aleatorio) continua podendo guardar qualquer coisa.
FURNITURE_DENY = {
    'minecraft:crafting_table', 'minecraft:furnace', 'minecraft:smoker', 'minecraft:blast_furnace',
    'minecraft:chest', 'minecraft:trapped_chest', 'minecraft:barrel', 'minecraft:composter',
    'minecraft:grindstone', 'minecraft:stonecutter', 'minecraft:smithing_table', 'minecraft:cauldron',
    'minecraft:hopper', 'minecraft:loom', 'minecraft:fletching_table', 'minecraft:cartography_table',
    'minecraft:enchanting_table', 'minecraft:anvil', 'minecraft:chipped_anvil', 'minecraft:damaged_anvil',
    'minecraft:bookshelf', 'minecraft:lectern',
    'farmersdelight:stove', 'farmersdelight:cooking_pot', 'farmersdelight:skillet',
    'farmersdelight:cutting_board', 'farmersdelight:basket',
    'create:gearbox', 'create:millstone', 'create:encased_fan', 'create:mechanical_press',
    'create:mechanical_mixer', 'create:basin', 'create:depot', 'create:windmill_bearing',
}
MACHINE_COMMON = [e for e in BASIC_MACHINES if e[0] not in FURNITURE_DENY]
# Create so sai em oficina (tema workshop) e deposito: nada com namespace create em bau comum
MACHINE_COMMON = [e for e in MACHINE_COMMON if not e[0].startswith('create:')] + \
    [('minecraft:shears', 2, 1, 1), ('minecraft:flint_and_steel', 1, 1, 1), ('minecraft:fishing_rod', 2, 1, 1),
     ('minecraft:compass', 1, 1, 1), ('minecraft:clock', 1, 1, 1),
     ('minecraft:lead', 2, 1, 1), ('minecraft:chain', 2, 1, 4), ('minecraft:lantern', 2, 1, 2)]


BASIC = _basic_gear() + BASIC_MACHINES + BASIC_MATERIALS + HEALING + [e for e in COOK_SUPPLY if e[1] > 1]
BASIC_COMMON = [e for e in BASIC if e[0] not in FURNITURE_DENY and not e[0].startswith('create:')]
RICH = [e if len(e) < 5 or not isinstance(e[4], bool) else (*e[:4], {'treasure': e[4], 'damage': False})
        for e in DEP_GEAR + DEP_MATERIALS + DEP_DEVICES + DEP_RARE] + \
    [e for e in GEAR if not re.search(r'_(hat|cap)$', e[0]) and e[0] != 'minecraft:spyglass'] + BASIC_MACHINES  # chapeus sao enfeite, nao premio
FOOD = FOOD_SNACK + MEALS + BAKERY
MOB_DROPS = [('minecraft:rotten_flesh', 12, 1, 3), ('minecraft:bone', 10, 1, 3), ('minecraft:string', 6, 1, 2),
             ('minecraft:spider_eye', 5, 1, 2), ('minecraft:gunpowder', 5, 1, 2), ('minecraft:arrow', 6, 1, 4),
             ('minecraft:leather', 5, 1, 2), ('minecraft:feather', 6, 1, 3), ('minecraft:rabbit_hide', 3, 1, 2),
             ('minecraft:ink_sac', 3, 1, 2), ('minecraft:glow_ink_sac', 1, 1, 1), ('minecraft:slime_ball', 2, 1, 2),
             ('minecraft:phantom_membrane', 1, 1, 1), ('minecraft:ender_pearl', 1, 1, 1), ('minecraft:rabbit_foot', 1, 1, 1),
             ('minecraft:blaze_rod', 2, 1, 2), ('minecraft:prismarine_shard', 1, 1, 2), ('minecraft:magma_cream', 1, 1, 1),
             ('minecraft:white_wool', 3, 1, 2),
             ('minecraft:beef', 2, 1, 2), ('minecraft:porkchop', 2, 1, 2), ('minecraft:chicken', 2, 1, 2),
             ('minecraft:mutton', 2, 1, 2), ('minecraft:rabbit', 1, 1, 1), ('minecraft:cod', 1, 1, 1)]
TEMP_STRINGS = ('legendarysurvivaloverhaul:warm_string', 'legendarysurvivaloverhaul:cold_string')

RICH_CHANCE = 0.12  # chance de um bau comum virar rico
ALWAYS_RICH = ('deposito',)

EXTRA_JS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        'kubejs', 'server_scripts', 'sunlitTownsLoot.js')


def _js_entries(ents, why):
    """[id, peso, min, max, pocao, gasto(0/1), encanto(0 nao, 1 as vezes leve, 2 tesouro)]"""
    lst, seen = [], set()
    for item, w, a, b, *extra in ents:
        opt = extra[0] if extra and isinstance(extra[0], dict) else {}
        key = (item, opt.get('potion'))
        if item.startswith('sophisticatedbackpacks:'):
            why['backpack_ban'] += 1
            continue
        if key in seen or not real_item(item):
            continue
        r = bad_item(item)
        if r:
            why[r] += 1
            continue
        seen.add(key)
        ench = 2 if opt.get('treasure') else (1 if opt.get('ench') else 0)
        lst.append([item, w, a, b, opt.get('potion') or '', 1 if opt.get('damage') else 0, ench])
    return lst


def write_extra_js():
    """Gera o sunlitTownsLoot.js: niveis de bau, preenchimento e filtro em jogo (item desligado por config quebraria
    a loot table inteira se estivesse no datapack, por isso tudo que nao e do tema passa por aqui)."""
    why = collections.Counter()
    pools = {'basic': _js_entries(BASIC_COMMON, why), 'rich': _js_entries(RICH, why), 'food': _js_entries(FOOD, why),
             'drink': _js_entries(DRINKS_ALL, why), 'mob': _js_entries(MOB_DROPS, why),
             'machine': _js_entries(MACHINE_COMMON, why), 'material': _js_entries(BASIC_MATERIALS, why)}
    for t, (_lo, _hi, entries) in THEMES.items():
        if t in ALWAYS_RICH:
            continue  # deposito usa as pools ricas aleatorias
        pools['theme_' + t] = _js_entries(entries, why)
    cfg = {'themes': sorted(set(THEMES) | set(MULTI)), 'richChance': RICH_CHANCE, 'alwaysRich': list(ALWAYS_RICH),
           'strings': list(TEMP_STRINGS)}
    save_cache()
    print('loot: pools', {k: len(v) for k, v in pools.items()}, 'descartados', dict(why))
    js = f"""// GERADO por sunlit_tools/towns/loot.py (nao editar a mao).
// Baus das cidades Sunlit. O datapack sorteia so os itens do tema do container; aqui cada bau ganha um nivel.
// Regra do projeto (AGENTS.md): todo bau comum tem 1 drop de mob, 1 comida OU 1 bebida, warm/cold strings,
// 1 equipamento e 1 material (a pool "machine" so tem ferramenta/componente miudo: nenhuma bancada que
// ja exista como mobilia no mapa sai em bau comum; panela so sai no tema da cozinha):
// - comum (a maioria): 1 a 3 itens de verdade (o tema do container primeiro, depois o proprio tema, por
//   ultimo basicos), 1 equipamento, 1 material, 1 comida OU 1 bebida, warm/cold strings (1 a 3) e so 1 a 3
//   drops de mobs de preenchimento; sem repetir o mesmo item dentro do bau;
// - rico (raro; deposito sempre): 4 a 6 itens de qualquer nivel, no maximo 3 strings, sem comida/bebida,
//   mesmo preenchimento pequeno. So o deposito (e o raro bau rico) dropa itens aleatorios.
// Itens do Create so saem em oficina (tema workshop) e deposito: nada com esse namespace em bau comum.
// O preenchimento e so ESPACO VAZIO com drops de mobs (pool "mob", com blaze_rod raro): nao e loot de verdade,
// so ocupa slots. Itens fora do registro, removidos/escondidos pelo modpack (global.removedItems/hiddenItems) nunca saem.
const $SunlitLootItems = Java.loadClass("net.minecraftforge.registries.ForgeRegistries").ITEMS;
const $SunlitLootRL = Java.loadClass("net.minecraft.resources.ResourceLocation");
const $SunlitLootEnch = Java.loadClass("net.minecraft.world.item.enchantment.EnchantmentHelper");
const SUNLIT_LOOT_POOLS = {json.dumps(pools)};
const SUNLIT_LOOT_CFG = {json.dumps(cfg)};

let sunlitLootBanned = null;
let sunlitLootReady = null;

const sunlitLootBan = (id) => {{
  if (sunlitLootBanned == null) {{
    sunlitLootBanned = {{}};
    try {{
      (global.removedItems || []).forEach((i) => (sunlitLootBanned[String(i)] = true));
      (global.hiddenItems || []).forEach((i) => (sunlitLootBanned[String(i)] = true));
    }} catch (err) {{
      console.warn(`[Sunlit Towns] loot: lista de itens removidos ilegivel: ${{err}}`);
    }}
  }}
  return !!sunlitLootBanned[id] || !$SunlitLootItems.containsKey(new $SunlitLootRL(id));
}};

// pools filtrados pelo registro real, com o peso acumulado para o sorteio
const sunlitLootPools = () => {{
  if (sunlitLootReady) return sunlitLootReady;
  let out = {{}};
  Object.keys(SUNLIT_LOOT_POOLS).forEach((k) => {{
    let list = SUNLIT_LOOT_POOLS[k].filter((it) => !sunlitLootBan(it[0]));
    let total = 0;
    list.forEach((it) => (total += it[1]));
    out[k] = {{ list: list, total: total }};
    let skipped = SUNLIT_LOOT_POOLS[k].length - list.length;
    if (skipped) console.info(`[Sunlit Towns] loot ${{k}}: ${{skipped}} itens fora do registro/removidos ignorados`);
  }});
  sunlitLootReady = out;
  return out;
}};

const sunlitLootInt = (rnd, lo, hi) => (hi <= lo ? lo : lo + rnd.nextInt(hi - lo + 1));

const sunlitLootStack = (it, rnd, maxCount) => {{
  let count = Math.min(sunlitLootInt(rnd, it[2], it[3]), maxCount || 64);
  let stack = it[4] ? Item.of(it[0], count, `{{Potion:"minecraft:${{it[4]}}"}}`) : Item.of(it[0], count);
  if (it[5] && stack.isDamageableItem()) stack.setDamageValue(Math.floor(stack.getMaxDamage() * (0.35 + rnd.nextFloat() * 0.55)));
  if (it[6] == 2) stack = $SunlitLootEnch.enchantItem(rnd, stack, sunlitLootInt(rnd, 20, 35), true);
  else if (it[6] == 1 && rnd.nextFloat() < 0.2) stack = $SunlitLootEnch.enchantItem(rnd, stack, sunlitLootInt(rnd, 5, 15), false);
  return stack;
}};

const sunlitLootPick = (pool, rnd, maxCount) => {{
  if (!pool.list.length) return null;
  let r = rnd.nextInt(pool.total);
  for (let i = 0; i < pool.list.length; i++) {{
    r -= pool.list[i][1];
    if (r < 0) return sunlitLootStack(pool.list[i], rnd, maxCount);
  }}
  return sunlitLootStack(pool.list[0], rnd, maxCount);
}};

// sorteio sem repetir item que ja saiu neste bau (4 tentativas; se tudo repetir, aceita o ultimo)
const sunlitLootDistinct = (pool, rnd, maxCount, used) => {{
  let s = null;
  for (let t = 0; t < 4; t++) {{
    s = sunlitLootPick(pool, rnd, maxCount);
    if (!s || s.isEmpty() || !used[String(s.getId())]) break;
  }}
  return s;
}};

const sunlitLootShuffle = (arr, rnd) => {{
  for (let i = arr.length - 1; i > 0; i--) {{
    let j = rnd.nextInt(i + 1);
    let t = arr[i];
    arr[i] = arr[j];
    arr[j] = t;
  }}
  return arr;
}};

const sunlitLootFill = (ctx, theme) => {{
  let pools = sunlitLootPools();
  let rnd = ctx.getVanillaContext().getRandom();
  let size = 27;
  try {{
    let be = ctx.getLevel().getBlockEntity(ctx.getBlockPos());
    if (be && be.getContainerSize) size = be.getContainerSize();
  }} catch (err) {{}}
  let rich = SUNLIT_LOOT_CFG.alwaysRich.indexOf(theme) >= 0 || rnd.nextFloat() < SUNLIT_LOOT_CFG.richChance;

  // itens do tema que o datapack sorteou (ja sem nada removido pelo modpack)
  let themed = [];
  ctx.forEachLoot((s) => {{
    if (!s.isEmpty() && !sunlitLootBan(String(s.getId()))) themed.push(s.copy());
  }});
  sunlitLootShuffle(themed, rnd);

  // itens de verdade: primeiro os do tema, depois o proprio tema, por ultimo basicos
  // (bau rico/deposito: qualquer nivel, como antes). Nada de repetir item dentro do bau.
  let want = rich ? sunlitLootInt(rnd, 4, 6) : [1, 1, 2, 2, 2, 3][rnd.nextInt(6)];
  want = Math.max(1, Math.min(want, size - 6));
  let real = themed.slice(0, want);
  let used = {{}};
  real.forEach((s) => (used[String(s.getId())] = true));
  let guard = 0;
  while (real.length < want && guard++ < 60) {{
    let src;
    if (rich) {{
      src = rnd.nextFloat() < 0.7 ? pools.rich : pools.basic;
    }} else {{
      let tp = pools['theme_' + theme];
      src = tp && tp.list.length && rnd.nextFloat() < 0.8 ? tp : pools.basic;
    }}
    let s = sunlitLootDistinct(src, rnd, 0, used);
    if (s && !s.isEmpty()) {{
      real.push(s);
      used[String(s.getId())] = true;
    }}
  }}

  // 1 equipamento + 1 material em todo bau (comum e rico): a regra do projeto garante essas categorias
  // (sem repetir o que ja saiu como item de verdade)
  let extra = [];
  if (pools.machine && pools.machine.list.length) {{
    let m = sunlitLootDistinct(pools.machine, rnd, 0, used);
    if (m && !m.isEmpty()) {{
      extra.push(m);
      used[String(m.getId())] = true;
    }}
  }}
  if (pools.material && pools.material.list.length) {{
    let m = sunlitLootDistinct(pools.material, rnd, 0, used);
    if (m && !m.isEmpty()) {{
      extra.push(m);
      used[String(m.getId())] = true;
    }}
  }}

  // 1 comida OU 1 bebida no bau comum (nunca os dois)
  if (!rich) {{
    let snack = sunlitLootPick(rnd.nextFloat() < 0.5 ? pools.food : pools.drink, rnd, 2);
    if (snack) extra.push(snack);
  }}
  let warm = rich ? 1 : sunlitLootInt(rnd, 1, 3);
  let cold = Math.max(1, warm + sunlitLootInt(rnd, -1, 1));
  if (rich && warm + cold > 3) cold = 3 - warm;
  [[SUNLIT_LOOT_CFG.strings[0], warm], [SUNLIT_LOOT_CFG.strings[1], cold]].forEach((p) => {{
    if (!sunlitLootBan(p[0])) extra.push(Item.of(p[0], p[1]));
  }});

  // PREENCHIMENTO pequeno: 1 a 3 drops de mobs (o vanilla espalha pilhas com mais de 1 item pelos
  // slots livres, entao a conta e por quantidade de itens, nao por pilha)
  let target = sunlitLootInt(rnd, 1, 3);
  let filler = [];
  guard = 0;
  while (filler.length < target && real.length + extra.length + filler.length < size && guard++ < 16) {{
    let s = sunlitLootPick(pools.mob, rnd, 2);
    if (!s || s.isEmpty()) break;
    filler.push(s);
  }}

  // so mexe no loot depois de tudo calculado: um erro acima deixa o bau com os itens do tema
  ctx.removeLoot(Ingredient.all);
  real.concat(extra, filler).slice(0, size).forEach((s) => ctx.addLoot(s));
}};

// LootJS 3.7 (1.21): customAction gives the vanilla LootContext and a LootBucket instead of the old
// LootContextJS; this adapter keeps the old ctx API used by sunlitLootFill.
const $SunlitLootParams = Java.loadClass("net.minecraft.world.level.storage.loot.parameters.LootContextParams");
const $SunlitBlockPos = Java.loadClass("net.minecraft.core.BlockPos");
const sunlitLootCtx = (context, loot) => ({{
  getVanillaContext: () => context,
  getLevel: () => context.getLevel(),
  getBlockPos: () => $SunlitBlockPos.containing(context.getParamOrNull($SunlitLootParams.ORIGIN)),
  forEachLoot: (fn) => {{
    for (let i = 0; i < loot.size(); i++) fn(loot.get(i));
  }},
  removeLoot: () => loot.clear(),
  addLoot: (s) => loot.addItem(s),
}});

LootJS.modifiers((e) => {{
  SUNLIT_LOOT_CFG.themes.forEach((theme) => {{
    e.addTableModifier(`sunlit:chests/${{theme}}`).customAction((context, loot) => {{
      try {{
        sunlitLootFill(sunlitLootCtx(context, loot), theme);
      }} catch (err) {{
        console.error(`[Sunlit Towns] loot ${{theme}}: ${{err}}`);
      }}
    }});
  }});
  console.info("[Sunlit Towns] niveis de loot registrados");
}});
"""
    open(EXTRA_JS, 'w', encoding='utf-8').write(js)


def loot_table(theme):
    """so os pools do tema; o resto (nivel do bau, comida/bebida, equipamento, material, strings, preenchimento)
    vai pelo LootJS (write_extra_js). O tema sorteia no maximo 3 e o JS usa no maximo 3 de verdade no comum."""
    if theme in MULTI:
        pools = [_pool(lo, hi, ents) for lo, hi, ents in MULTI[theme]]
    else:
        lo, hi, entries = THEMES[theme]
        pools = [_pool(1, min(hi, 3), entries)]
    return {'type': 'minecraft:chest', 'pools': pools}


# temas com predio proprio (clutter.SPECIAL_THEMES): so aparecem em um predio do schematics.py
SPECIAL_THEMES = ('floricultura', 'adega', 'torre_raio', 'laticinio', 'vinicola', 'celeiro_neve', 'cabana_pescador',
                  'alfaiataria', 'seringueiro')
PACK_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                         'moonlight-global-datapacks', 'sunlit_towns', 'data', 'sunlit')


def write_theme_files(themes=SPECIAL_THEMES):
    """condicao (lostcities/conditions) e loot table (loot_tables/chests) de cada tema, no formato do cozy_expansion.py.
    Chamado pelo schematics.py depois de gerar os predios."""
    for t in themes:
        with open(os.path.join(PACK_DATA, 'lostcities', 'conditions', t + '.json'), 'w', encoding='utf-8') as f:
            json.dump({'values': [{'factor': 1, 'value': f'sunlit:chests/{t}'}]}, f)
        with open(os.path.join(PACK_DATA, 'loot_tables', 'chests', t + '.json'), 'w', encoding='utf-8') as f:
            json.dump(loot_table(t), f)


def _pool(lo, hi, entries):
    seen, ents = set(), []
    for item, w, a, b, *extra in entries:
        opt = extra[0] if extra else None
        if isinstance(opt, bool):
            opt = {'treasure': opt}
        opt = opt or {}
        key = (item, opt.get('potion'))
        if key in seen or not real_item(item) or bad_item(item) or item in CROP_BLACKLIST:
            continue
        seen.add(key)
        e = {'type': 'minecraft:item', 'name': item, 'weight': w}
        fns = []
        if b > 1:
            fns.append({'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': a, 'max': b}})
        if opt.get('potion'):
            fns.append({'function': 'minecraft:set_potion', 'id': f"minecraft:{opt['potion']}"})
        if opt.get('damage'):
            fns.append({'function': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': 0.35, 'max': 0.9}})
        if opt.get('ench'):
            fns.append({'function': 'minecraft:enchant_randomly',
                        'conditions': [{'condition': 'minecraft:random_chance', 'chance': 0.2}]})
        if opt.get('treasure'):
            fns.append({'function': 'minecraft:enchant_with_levels', 'treasure': True,
                        'levels': {'type': 'minecraft:uniform', 'min': 20, 'max': 35}})
        if fns:
            e['functions'] = fns
        ents.append(e)
    return {'rolls': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}, 'bonus_rolls': 0, 'entries': ents}


# ---------------------------------------------------------------- escolha do tema por predio + container
BUILDING_THEME = [
    (r'fastfood|restaurant(?!sushi)', 'restaurant'), (r'sushi', 'sushi'), (r'cafe|foodtruck', 'cafe'),
    (r'convenientstore|gasstation', 'grocery'), (r'flowershop', 'flowers'), (r'clothstore', 'clothing'),
    (r'hardwarestore|workshop', 'workshop'), (r'officebank', 'bank'), (r'office|filmworks|courtyard|police', 'office'),
    (r'verticalschool|communitycenter', 'school'), (r'hospital|polyclinic', 'clinic'),
    (r'farmhouse|villager', 'farm'), (r'cabin|campsite|treehouse', 'camp'),
    (r'hotel|casino|gallery|sunkenclub|thering', 'luxury'),
    (r'adega|cellar|vineyard|vinhedo', 'cellar'), (r'porto|dock|pier|harbor|trapiche|fishery', 'dock'),
]


def building_theme(bname):
    for rx, t in BUILDING_THEME:
        if re.search(rx, bname):
            return t
    return None


def theme_for(bname, container, part=''):
    """bname = nome do predio DC, container = id do bloco final (ja convertido)"""
    c = container.split(':')[-1]
    bt = building_theme(bname)
    if re.search(r'fridge|freezer|cooler', c):
        return 'fridge' if bt in (None, 'luxury', 'office', 'school', 'clinic', 'camp', 'farm') else bt
    if re.search(r'kitchen|stove|cutting_board', c):
        return 'kitchen' if bt in (None, 'luxury', 'office', 'school', 'clinic') else bt
    if bt:
        if bt in ('office', 'school', 'bank') and re.search(r'drawer|desk', c):
            return bt
        if bt == 'luxury' and re.search(r'drawer', c):
            return 'bedroom'
        return bt
    if re.search(r'basin|bath|toilet', c):
        return 'bathroom'
    if re.search(r'drawer|dresser|wardrobe', c):
        return 'bedroom'
    if re.search(r'toolbox|tool_box', c) or 'garage' in part:
        return 'garage'
    return 'home'
