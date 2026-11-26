# Auditoria de preços: Pipinha's Village

Gerado por `tools/priceaudit/price_audit.py` (só lê o pack e a 1.20.1). Rodar de novo recria este arquivo; a saída é determinística. O arquivo gerado `kubejs/startup_scripts/globalRegistryMissingPrices.js` é escrito pelo mesmo script e não entra na leitura de PRICED, para a saída ser estável.

## Resumo

| Métrica | Valor |
|---|---|
| Ids existentes (jars, cliente, kubejs) | 27478 |
| PRICED (ids com preço no kubejs) | 3034 |
| PRICED com valor literal | 2954 |
| DEAD_PRICED restante | 284 |
|   DEAD_PRICED alta confiança (não corrigidos) | 27 |
|   DEAD_PRICED baixa confiança | 145 |
|   DEAD_PRICED sem sugestão | 112 |
| Correções de id aplicadas (dead_fixes.json) | 3 |
| Candidatos existentes (sem excluídos) | 1129 |
| Excluídos (não são produto) | 46 |
| MISSING (ids únicos) | 155 |
| MISSING com sugestão (gerados) | 155 |
|   gerados com fallback | 97 |
|   gerados por alias de preço | 13 |
|   gerados por classe food/machine/animal | 123/15/17 |
| UNRESOLVED (ficam sem preço) | 0 |
| MISSING após aplicar (UNRESOLVED + excluídos) | 46 |
| Excluídos (globalUnsellableItems.js) | 4 |

## Candidatos e faltantes por classe

| Classe | Candidatos | MISSING | Com sugestão | UNRESOLVED |
|---|---|---|---|---|
| machine | 117 | 15 | 15 | 0 |
| animal | 148 | 17 | 17 | 0 |
| food | 888 | 123 | 123 | 0 |

Um id com mais de uma classe aparece em cada uma delas nesta tabela; no missing.json ele sai uma vez, com a primeira classe em ordem machine, animal, food.

Maiores namespaces em MISSING: hearthandharvest (40), culturaldelights (24), farmersrespite (22), minecraft (19), crabbersdelight (6).

## Excluídos (não são produto)

| id | motivo |
|---|---|
| atmospheric:currant_seedling | seed |
| atmospheric:grimwood_sapling | sapling |
| beachparty:rubber_ring_axolotl | toy or decor |
| betterarcheology:growth_totem | totem |
| crittersandcompanions:jumping_spider_spawn_egg | spawn egg |
| culturaldelights:cucumber_seeds | seed |
| culturaldelights:eggplant_seeds | seed |
| etcetera:cotton_seeds | seed |
| farm_and_charm:barley_seeds | seed |
| farm_and_charm:fertilized_soil | soil or fertilizer |
| farm_and_charm:fertilizer | soil or fertilizer |
| farm_and_charm:lettuce_seeds | seed |
| farm_and_charm:oat_seeds | seed |
| farmersdelight:cabbage_seeds | seed |
| farmersdelight:tomato_seeds | seed |
| farmersrespite:tea_seeds | seed |
| kaleidoscope_cookery:chili_seed | seed |
| kaleidoscope_cookery:lettuce_seed | seed |
| minecraft:beetroot_seeds | seed |
| minecraft:melon_seeds | seed |
| minecraft:pumpkin_seeds | seed |
| minecraft:torchflower_seeds | seed |
| minecraft:wheat_seeds | seed |
| society:scavenged_food_bag | loot container |
| sunrisegardening:high_quality_fertilizer | soil or fertilizer |
| sunrisegardening:strong_fertilizer | soil or fertilizer |
| supplementaries:flax_seeds | seed |
| tanukidecor:brown_mushroom_log_stool | toy or decor |
| tanukidecor:brown_mushroom_stool | toy or decor |
| tanukidecor:red_mushroom_log_stool | toy or decor |
| tanukidecor:red_mushroom_stool | toy or decor |
| veggiesdelight:bellpepper_seeds | seed |
| veggiesdelight:broccoli_seeds | seed |
| veggiesdelight:cauliflower_seeds | seed |
| veggiesdelight:garlic_seed | seed |
| veggiesdelight:turnip_seeds | seed |
| veggiesdelight:zucchini_seeds | seed |
| vinery:red_grape_seeds | seed |
| vinery:white_grape_seeds | seed |
| vintagedelight:cucumber_seeds | seed |
| vintagedelight:ghost_pepper_seeds | seed |
| wildernature:bunny_stalker_banner | toy or decor |
| wildernature:loot_bag | loot container |
| youkaishomecoming:black_grape_seeds | seed |
| youkaishomecoming:cucumber_seeds | seed |
| youkaishomecoming:tea_seeds | seed |

## Correções de id aplicadas (DEAD_PRICED alta confiança)

| id antigo | id novo | arquivo |
|---|---|---|
| create_central_kitchen:cherry_pie_slice | hearthandharvest:cherry_pie_slice | globalRegistryFoodPrices.js |
| hearthandharvest:lemon | culturaldelights:lemon | globalRegistryFoodPrices.js |
| society:sea_biscuit | society:sea_biscut | globalRegistryFoodPrices.js |

## MISSING por namespace

### hearthandharvest (40)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| hearthandharvest:beer | food | alias of brewinandchewin:beer | 30 | crop | cooking |
| hearthandharvest:blueberry_pips | machine | machine seedMaker.js | 5 | crop | cooking |
| hearthandharvest:candy_corn | food | alias of hauntedharvest:candy_corn | 10 | crop | cooking |
| hearthandharvest:cheese_pizza | food | recipe minecraft:crafting_shaped | 143 | crop | cooking |
| hearthandharvest:cherry_pie | food | fallback: recipe minecraft:crafting_shaped | 102 | crop | cooking |
| hearthandharvest:chocolate_cake | food | alias of bakery:chocolate_cake | 142 | crop | cooking |
| hearthandharvest:chocolate_milk_bottle | food | fallback: recipe minecraft:crafting_shapeless | 28 | crop | cooking |
| hearthandharvest:cider_donut | food | fallback: recipe farmersdelight:cooking | 215 | crop | cooking |
| hearthandharvest:cooked_corn_on_the_cob | food | fallback: recipe minecraft:campfire_cooking | 10 | crop | cooking |
| hearthandharvest:corn | food | alias of farm_and_charm:corn x0.333 (globalPriceBalance list) | 9 | crop | cooking |
| hearthandharvest:corn_bread | food | fallback: recipe farmersdelight:cooking | 50 | crop | cooking |
| hearthandharvest:corn_stew | food | fallback: recipe farmersdelight:cooking | 88 | crop | cooking |
| hearthandharvest:croissant | food | alias of bakery:croissant | 2 | crop | cooking |
| hearthandharvest:glazed_carrots | food | recipe farmersdelight:cooking | 106 | crop | cooking |
| hearthandharvest:glow_berry_juice | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |
| hearthandharvest:glow_berry_wine | food | fallback: recipe hearthandharvest:aging | 5 | crop | cooking |
| hearthandharvest:goat_milk_bucket | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |
| hearthandharvest:hard_cider | food | fallback: recipe hearthandharvest:aging | 5 | crop | cooking |
| hearthandharvest:hops | food | alias of brewery:hops x0.333 (globalPriceBalance list) | 7 | crop | cooking |
| hearthandharvest:hot_dog | food | recipe minecraft:crafting_shapeless | 39 | crop | cooking |
| hearthandharvest:maple_cookie | food | recipe minecraft:crafting_shapeless | 13 | crop | cooking |
| hearthandharvest:meat_pizza | food | recipe minecraft:crafting_shaped | 151 | crop | cooking |
| hearthandharvest:melon_wine | food | fallback: recipe hearthandharvest:aging | 5 | crop | cooking |
| hearthandharvest:moonshine | food | fallback: recipe brewinandchewin:fermenting | 18 | crop | cooking |
| hearthandharvest:pancake | food | fallback: recipe farmersdelight:cooking | 64 | crop | cooking |
| hearthandharvest:pizza | food | recipe minecraft:crafting_shaped | 164 | crop | cooking |
| hearthandharvest:popcorn | food | recipe farmersdelight:cooking | 19 | crop | cooking |
| hearthandharvest:raisin_cookie | food | recipe minecraft:crafting_shapeless | 10 | crop | cooking |
| hearthandharvest:raspberry_pips | machine | machine seedMaker.js | 5 | crop | cooking |
| hearthandharvest:raspberry_scone | food | fallback: recipe minecraft:crafting_shaped | 120 | crop | cooking |
| hearthandharvest:raw_skewered_sausage | food | fallback: recipe minecraft:crafting_shapeless | 20 | crop | cooking |
| hearthandharvest:root_beer | food | fallback: recipe hearthandharvest:aging | 5 | crop | cooking |
| hearthandharvest:street_corn | food | fallback: recipe farmersdelight:cooking | 84 | crop | cooking |
| hearthandharvest:sweet_berry_juice | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |
| hearthandharvest:taco | food | recipe minecraft:crafting_shapeless | 141 | crop | cooking |
| hearthandharvest:tamale | food | recipe farmersdelight:cooking | 74 | crop | cooking |
| hearthandharvest:tortilla | food | recipe hearthandharvest:shapeless_remainder | 25 | crop | cooking |
| hearthandharvest:uncooked_corn_on_the_cob | food | fallback: recipe minecraft:crafting_shapeless | 7 | crop | cooking |
| hearthandharvest:unripe_cheese_wheel | food | recipe brewinandchewin:fermenting | 63 | crop | cooking |
| hearthandharvest:veggie_pizza | food | recipe minecraft:crafting_shaped | 155 | crop | cooking |

### culturaldelights (24)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| culturaldelights:apple_cider | food | fallback: recipe culturaldelights:aging | 44 | crop | cooking |
| culturaldelights:beans | food | fallback: recipe minecraft:crafting_shapeless | 5 | crop | cooking |
| culturaldelights:beer | food | alias of brewinandchewin:beer | 30 | crop | cooking |
| culturaldelights:bloody_mary | food | fallback: recipe culturaldelights:aging | 256 | crop | cooking |
| culturaldelights:brandy | food | alias of kaleidoscope_tavern:brandy | 8 | crop | cooking |
| culturaldelights:butterscotch_cinnamon_pie | food | fallback: recipe minecraft:crafting_shaped | 5 | crop | cooking |
| culturaldelights:cheese_wheel | food | fallback: recipe culturaldelights:aging | 54 | crop | cooking |
| culturaldelights:cinnamon_mint_curry | food | fallback: recipe farmersdelight:cooking | 100 | crop | cooking |
| culturaldelights:cooked_sausage | food | recipe minecraft:campfire_cooking | 18 | crop | cooking |
| culturaldelights:corn_dog | food | recipe farmersdelight:cooking | 82 | crop | cooking |
| culturaldelights:gin | food | fallback: recipe culturaldelights:aging | 148 | crop | cooking |
| culturaldelights:glow_wine | food | fallback: recipe culturaldelights:aging | 64 | crop | cooking |
| culturaldelights:ice_cream | food | fallback: recipe culturaldelights:aging | 36 | crop | cooking |
| culturaldelights:lemon_liqueur | food | fallback: recipe culturaldelights:aging | 164 | crop | cooking |
| culturaldelights:margarita | food | fallback: recipe culturaldelights:aging | 434 | crop | cooking |
| culturaldelights:marshmallow | food | fallback: recipe farmersdelight:cooking | 5 | crop | cooking |
| culturaldelights:mead | food | fallback: recipe culturaldelights:aging | 40 | crop | cooking |
| culturaldelights:mojito | food | alias of kaleidoscope_tavern:mojito | 44 | crop | cooking |
| culturaldelights:refried_beans | food | fallback: recipe farmersdelight:cooking | 34 | crop | cooking |
| culturaldelights:rum | food | alias of kaleidoscope_tavern:rum | 12 | crop | cooking |
| culturaldelights:tequila | food | fallback: recipe culturaldelights:aging | 32 | crop | cooking |
| culturaldelights:vodka | food | fallback: recipe culturaldelights:aging | 68 | crop | cooking |
| culturaldelights:whiskey | food | alias of kaleidoscope_tavern:whiskey | 46 | crop | cooking |
| culturaldelights:wine | food | alias of kaleidoscope_tavern:wine | 30 | crop | cooking |

### farmersrespite (22)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| farmersrespite:apple_cider_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:apple_cider_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:black_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:black_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:coffee_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:coffee_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:dandelion_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:dandelion_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:gamblers_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:gamblers_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:green_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:green_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:hot_cocoa_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:hot_cocoa_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:melon_juice_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:melon_juice_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:purulent_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:purulent_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:rose_hip_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:rose_hip_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:yellow_tea_with_milk | food | fallback: recipe create:filling | 5 | crop | cooking |
| farmersrespite:yellow_tea_with_sugar | food | fallback: recipe create:filling | 5 | crop | cooking |

### minecraft (19)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| minecraft:bamboo | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:bone | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:bone_meal | food | recipe farm_and_charm:drying | 36 | crop | cooking |
| minecraft:bowl | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:glass_bottle | machine | fallback: no usable recipe or 1.20.1 price | 5 | crop | cooking |
| minecraft:glow_ink_sac | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:green_dye | food | recipe minecraft:smoking | 30 | crop | cooking |
| minecraft:ink_sac | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:milk_bucket | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |
| minecraft:mycelium | food | fallback: recipe farm_and_charm:drying | 5 | crop | cooking |
| minecraft:ochre_froglight | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:pearlescent_froglight | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:pitcher_pod | machine | machine seedMaker.js | 14 | crop | cooking |
| minecraft:potion | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |
| minecraft:rotten_flesh | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |
| minecraft:seagrass | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:string | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:verdant_froglight | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| minecraft:water_bucket | food | recipe brewinandchewin:keg_pouring | 5 | crop | cooking |

### crabbersdelight (6)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| crabbersdelight:coconut_milk | food | fallback: recipe minecraft:crafting_shapeless | 14 | crop | cooking |
| crabbersdelight:coconut_pudding | food | fallback: recipe farmersdelight:cooking | 44 | crop | cooking |
| crabbersdelight:deluxe_crab_trap_bait | machine | fallback: no usable recipe or 1.20.1 price | 5 | crop | cooking |
| crabbersdelight:fish_sandwich | food | fallback: recipe minecraft:crafting_shapeless | 53 | crop | cooking |
| crabbersdelight:fried_fish | food | recipe farmersdelight:cooking | 20 | crop | cooking |
| crabbersdelight:turtle_stew | food | fallback: recipe farmersdelight:cooking | 148 | crop | cooking |

### farm_and_charm (4)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| farm_and_charm:cooked_bacon | food | recipe minecraft:campfire_cooking | 75 | crop | cooking |
| farm_and_charm:cooked_chicken_parts | food | recipe minecraft:campfire_cooking | 75 | crop | cooking |
| farm_and_charm:cooked_lamb_ham | food | recipe minecraft:campfire_cooking | 96 | crop | cooking |
| farm_and_charm:cooked_minced_beef | food | recipe minecraft:campfire_cooking | 75 | crop | cooking |

### pamhc2trees (4)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| pamhc2trees:roastedacornitem | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |
| pamhc2trees:roastedchestnutitem | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |
| pamhc2trees:roastedpecanitem | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |
| pamhc2trees:roastedpinenutitem | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |

### autumnity (3)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| autumnity:pancake | food | fallback: recipe minecraft:crafting_shapeless | 132 | crop | cooking |
| autumnity:snail_goo | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| autumnity:snail_shell_piece | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |

### bakery (3)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| bakery:baked_sweet_dough | food | recipe minecraft:campfire_cooking | 5 | crop | cooking |
| bakery:cornet_shell | food | fallback: recipe farm_and_charm:stove | 5 | crop | cooking |
| bakery:sponge_sheet | food | fallback: recipe farm_and_charm:stove | 126 | crop | cooking |

### create (3)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| create:crushed_raw_bismuth | machine | machine recyclingMachine.js | 22 | crop | cooking |
| create:crushed_raw_lead | machine | machine recyclingMachine.js | 32 | crop | cooking |
| create:crushed_raw_silver | machine | machine recyclingMachine.js | 43 | crop | cooking |

### society (3)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| society:artifact_trove | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |
| society:bouquet_bag | machine | machine recyclingMachine.js | 5 | crop | cooking |
| society:no_name_for_the_sheep | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |

### ftbstuff (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| ftbstuff:cast_iron_ingot | food | recipe minecraft:campfire_cooking | 16 | crop | cooking |
| ftbstuff:tempered_glass | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |

### herbalbrews (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| herbalbrews:flask | food | recipe herbalbrews:cauldron_brewing | 15 | crop | cooking |
| herbalbrews:tea_blossom | machine | machine seedMaker.js | 5 | crop | cooking |

### meadow (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| meadow:firewood | machine | fallback: no usable recipe or 1.20.1 price | 5 | crop | cooking |
| meadow:rennet | food | recipe meadow:cooking | 19 | crop | cooking |

### oceansdelight (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| oceansdelight:cooked_stuffed_squid | food | recipe minecraft:campfire_cooking | 116 | crop | cooking |
| oceansdelight:kelp_encrusted_cod | food | fallback: recipe farmersdelight:cooking | 32 | crop | cooking |

### paraglider (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| paraglider:enduring_elixir_1 | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |
| paraglider:energizing_elixir_1 | food | fallback: recipe minecraft:campfire_cooking | 5 | crop | cooking |

### vintagedelight (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| vintagedelight:oatmeal | food | fallback: recipe farmersdelight:cooking | 54 | crop | cooking |
| vintagedelight:organic_mash | machine | machine recyclingMachine.js | 43 | crop | cooking |

### wildernature (2)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| wildernature:cooked_turkey_meat | food | alias of autumnity:cooked_turkey | 32 | crop | cooking |
| wildernature:hazelnut | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |

### aquaculture (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| aquaculture:fish_bones | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |

### atmospheric (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| atmospheric:aloe_kernels | machine | machine seedMaker.js | 5 | crop | cooking |

### candlelight (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| candlelight:potroast | food | recipe farm_and_charm:pot_cooking | 150 | crop | cooking |

### farmersdelight (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| farmersdelight:gleaming_salad_block | food | fallback: recipe minecraft:crafting_shapeless | 406 | crop | cooking |

### rehooked (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| rehooked:diamond_hook | machine | fallback: no usable recipe or 1.20.1 price | 5 | crop | cooking |

### snowpig (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| snowpig:music_disc_frosty_snig | animal | fallback: no usable recipe or 1.20.1 price | 5 | crop | animalProducts |

### snowyspirit (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| snowyspirit:ginger_flower | machine | machine seedMaker.js | 5 | crop | cooking |

### supplementaries (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| supplementaries:pancake | food | fallback: recipe minecraft:crafting_shapeless | 10 | crop | cooking |

### veggiesdelight (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| veggiesdelight:lasagna_pan | food | fallback: recipe farmersdelight:cooking | 402 | crop | cooking |

### windswept (1)

| id | classe | fonte | sugestão | atributo | lista |
|---|---|---|---|---|---|
| windswept:frozen_flesh | food | fallback: recipe minecraft:crafting_shapeless | 5 | crop | cooking |

## PRICED (ids com preço no kubejs)

| id | valor | existe | arquivos |
|---|---|---|---|
| aquaculture:arapaima | 224 | sim | globalRegistry.js |
| aquaculture:arrau_turtle | 280 | sim | globalRegistry.js |
| aquaculture:atlantic_cod | 120 | sim | globalRegistry.js |
| aquaculture:atlantic_halibut | 232 | sim | globalRegistry.js |
| aquaculture:atlantic_herring | 16 | sim | globalRegistry.js |
| aquaculture:bayad | 208 | sim | globalRegistry.js |
| aquaculture:blackfish | 24 | sim | globalRegistry.js |
| aquaculture:bluegill | 16 | sim | globalRegistry.js |
| aquaculture:boulti | 128 | sim | globalRegistry.js |
| aquaculture:box | 32 | sim | globalRegistry.js |
| aquaculture:box_turtle | 320 | sim | globalRegistry.js |
| aquaculture:brown_shrooma | 264 | sim | globalRegistry.js |
| aquaculture:brown_trout | 40 | sim | globalRegistry.js |
| aquaculture:capitaine | 288 | sim | globalRegistry.js |
| aquaculture:carp | 40 | sim | globalRegistry.js |
| aquaculture:catfish | 144 | sim | globalRegistry.js |
| aquaculture:fish_fillet_cooked | 8 | sim | globalRegistry.js |
| aquaculture:fish_fillet_raw | 8 | sim | globalRegistry.js |
| aquaculture:gar | 88 | sim | globalRegistry.js |
| aquaculture:goldfish | 512 | sim | globalRegistry.js |
| aquaculture:jellyfish | 56 | sim | globalRegistry.js |
| aquaculture:leech | 136 | sim | globalRegistry.js |
| aquaculture:lockbox | 128 | sim | globalRegistry.js |
| aquaculture:minnow | 16 | sim | globalRegistry.js |
| aquaculture:muskellunge | 96 | sim | globalRegistry.js |
| aquaculture:neptunium_block | 23040 | sim | globalRegistry.js |
| aquaculture:neptunium_ingot | 2560 | sim | globalRegistry.js |
| aquaculture:pacific_halibut | 400 | sim | globalRegistry.js |
| aquaculture:perch | 16 | sim | globalRegistry.js |
| aquaculture:pink_salmon | 64 | sim | globalRegistry.js |
| aquaculture:piranha | 48 | sim | globalRegistry.js |
| aquaculture:pollock | 56 | sim | globalRegistry.js |
| aquaculture:rainbow_trout | 64 | sim | globalRegistry.js |
| aquaculture:red_grouper | 80 | sim | globalRegistry.js |
| aquaculture:red_shrooma | 264 | sim | globalRegistry.js |
| aquaculture:smallmouth_bass | 40 | sim | globalRegistry.js |
| aquaculture:starshell_turtle | 240 | sim | globalRegistry.js |
| aquaculture:sushi | 12 | sim | globalRegistry.js |
| aquaculture:synodontis | 112 | sim | globalRegistry.js |
| aquaculture:tambaqui | 112 | sim | globalRegistry.js |
| aquaculture:tin_can | 1 | sim | globalRegistry.js |
| aquaculture:treasure_chest | 512 | sim | globalRegistry.js |
| aquaculture:tuna | 192 | sim | globalRegistry.js |
| aquaculture:turtle_soup | 280 | sim | globalRegistry.js |
| atmospheric:aloe_bundle | 144 | sim | globalRegistry.js |
| atmospheric:aloe_gel_block | 512 | sim | globalRegistry.js |
| atmospheric:aloe_gel_bottle | 128 | sim | globalRegistry.js |
| atmospheric:aloe_leaves | 16 | sim | globalRegistry.js |
| atmospheric:annoying_orange | 12 | sim | globalRegistryFoodPrices.js |
| atmospheric:aspen_log | 3 | sim | globalRegistry.js |
| atmospheric:blood_orange | 112 | sim | globalRegistry.js |
| atmospheric:blood_orange_crate | 1008 | sim | globalRegistry.js |
| atmospheric:candied_orange_slices | 99 | sim | globalRegistry.js |
| atmospheric:carmine_block |  | sim | globalRegistryStorageBlockPrices.js |
| atmospheric:carmine_husk | 10 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| atmospheric:crustose_log | 4 | sim | globalRegistry.js |
| atmospheric:currant | 8 | sim | globalPriceBalance.js, globalRegistry.js |
| atmospheric:currant_crate | 72 | sim | globalPriceBalance.js, globalRegistry.js |
| atmospheric:currant_muffin | 32 | sim | globalRegistry.js |
| atmospheric:dragon_fruit | 30 | sim | globalRegistryFoodPrices.js |
| atmospheric:ender_dragon_fruit | 30 | sim | globalRegistryFoodPrices.js |
| atmospheric:golden_dragon_fruit | 30 | sim | globalRegistryFoodPrices.js |
| atmospheric:grimwood_log | 7 | sim | globalRegistry.js |
| atmospheric:kousa_log | 3 | sim | globalRegistry.js |
| atmospheric:laurel_log | 3 | sim | globalRegistry.js |
| atmospheric:morado_log | 3 | sim | globalRegistry.js |
| atmospheric:orange | 96 | sim | globalRegistry.js |
| atmospheric:orange_crate | 864 | sim | globalRegistry.js |
| atmospheric:orange_pudding | 164 | sim | globalRegistry.js |
| atmospheric:orange_sorbet | 107 | sim | globalRegistry.js |
| atmospheric:passion_fruit | 128 | sim | globalRegistry.js |
| atmospheric:passion_fruit_crate | 1152 | sim | globalRegistry.js |
| atmospheric:passion_fruit_sorbet | 139 | sim | globalRegistry.js |
| atmospheric:passion_fruit_tart | 128 | sim | globalRegistry.js |
| atmospheric:roasted_yucca_bundle | 72 | sim | globalRegistry.js |
| atmospheric:roasted_yucca_cask | 72 | sim | globalRegistry.js |
| atmospheric:roasted_yucca_fruit | 8 | sim | globalRegistry.js |
| atmospheric:rosewood_log | 3 | sim | globalRegistry.js |
| atmospheric:scythe_pottery_sherd | 512 | sim | globalRegistry.js |
| atmospheric:shimmering_passion_fruit | 160 | sim | globalRegistry.js |
| atmospheric:shimmering_passion_fruit_crate | 1440 | sim | globalRegistry.js |
| atmospheric:stripped_aspen_log | 3 | sim | globalRegistry.js |
| atmospheric:stripped_crustose_log | 4 | não | globalRegistry.js |
| atmospheric:stripped_grimwood_log | 7 | sim | globalRegistry.js |
| atmospheric:stripped_kousa_log | 3 | sim | globalRegistry.js |
| atmospheric:stripped_laurel_log | 3 | sim | globalRegistry.js |
| atmospheric:stripped_morado_log | 3 | sim | globalRegistry.js |
| atmospheric:stripped_rosewood_log | 3 | sim | globalRegistry.js |
| atmospheric:stripped_yucca_log | 3 | sim | globalRegistry.js |
| atmospheric:succulent_pottery_sherd | 512 | sim | globalRegistry.js |
| atmospheric:sun_pottery_sherd | 512 | sim | globalRegistry.js |
| atmospheric:watchful_aspen_log | 6 | sim | globalRegistry.js |
| atmospheric:yucca_bundle | 72 | sim | globalRegistry.js |
| atmospheric:yucca_cask | 72 | sim | globalRegistry.js |
| atmospheric:yucca_fruit | 8 | sim | globalRegistry.js |
| atmospheric:yucca_gateau | 369 | sim | globalRegistry.js |
| atmospheric:yucca_log | 3 | sim | globalRegistry.js |
| automobility:dash_panel | 60 | sim | globalRegistry.js |
| autumnity:cooked_turkey | 32 | sim | globalRegistry.js |
| autumnity:cooked_turkey_piece | 6 | sim | globalRegistry.js |
| autumnity:foul_berries | 4 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| autumnity:foul_berry_basket |  | sim | globalRegistryStorageBlockPrices.js |
| autumnity:foul_soup | 12 | sim | globalRegistry.js |
| autumnity:large_pumpkin_slice | 80 | sim | globalRegistry.js |
| autumnity:maple_log | 2 | sim | globalRegistry.js |
| autumnity:pumpkin | 12 | não | globalRegistryFoodPrices.js |
| autumnity:pumpkin_bread | 95 | sim | globalRegistry.js |
| autumnity:stripped_maple_log | 2 | sim | globalRegistry.js |
| autumnity:syrup_bottle | 30 | sim | globalRegistryFoodPrices.js |
| autumnity:turkey | 32 | sim | globalRegistry.js |
| autumnity:turkey_egg | 32 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| autumnity:turkey_egg_crate |  | sim | globalRegistryStorageBlockPrices.js |
| autumnity:turkey_piece | 6 | sim | globalRegistry.js |
| bakery:apple_cupcake | 8 | sim | globalRegistry.js |
| bakery:apple_jam | 11 | sim | globalRegistry.js |
| bakery:apple_pie | 88 | sim | globalCanonicalItems.js, globalRegistry.js |
| bakery:apple_pie_piece | 70 | não | globalRegistryFoodPrices.js |
| bakery:apple_pie_slice | 22 | sim | globalCanonicalItems.js, globalRegistry.js |
| bakery:baguette | 9 | sim | globalRegistry.js |
| bakery:braided_bread | 6 | sim | globalRegistry.js |
| bakery:bread | 8 | sim | globalRegistry.js |
| bakery:bread_crate | 64 | sim | globalRegistry.js |
| bakery:bread_with_jam | 32 | sim | globalRegistry.js |
| bakery:bun | 5 | sim | globalRegistry.js |
| bakery:bundt_cake | 104 | sim | globalRegistry.js |
| bakery:bundt_cake_slice | 26 | sim | globalRegistry.js |
| bakery:cake_dough | 40 | sim | globalRegistryExtraPrices.js |
| bakery:cake_tower | 70 | sim | globalRegistryFoodPrices.js |
| bakery:chocolate | 30 | não | globalRegistryFoodPrices.js |
| bakery:chocolate_box | 72 | sim | globalRegistry.js |
| bakery:chocolate_bread | 30 | sim | globalRegistryExtraPrices.js |
| bakery:chocolate_cake | 142 | sim | globalRegistry.js |
| bakery:chocolate_cake_slice | 36 | sim | globalRegistry.js, globalRegistryFoodPrices.js |
| bakery:chocolate_donut | 427 | sim | globalRegistry.js |
| bakery:chocolate_gateau | 25 | sim | globalRegistry.js |
| bakery:chocolate_gateau_slice | 6 | sim | globalRegistry.js |
| bakery:chocolate_glazed_cookie | 54 | sim | globalRegistry.js |
| bakery:chocolate_jam | 84 | sim | globalRegistry.js |
| bakery:chocolate_tart | 32 | sim | globalRegistry.js |
| bakery:chocolate_tart_slice | 8 | sim | globalRegistry.js |
| bakery:chocolate_truffle | 6 | sim | globalRegistry.js |
| bakery:cornet | 20 | sim | globalRegistry.js |
| bakery:croissant | 2 | sim | globalRegistry.js |
| bakery:crusty_bread | 8 | sim | globalRegistry.js |
| bakery:donut | 35 | sim | globalRegistryFoodPrices.js |
| bakery:dough |  | sim | globalCanonicalItems.js |
| bakery:glowberry_jam | 27 | sim | globalRegistry.js |
| bakery:glowberry_pie | 175 | não | globalRegistryFoodPrices.js |
| bakery:glowberry_pie_slice | 8 | sim | globalRegistry.js |
| bakery:glowberry_tart | 35 | sim | globalRegistry.js |
| bakery:grilled_bacon_sandwich | 56 | sim | globalRegistry.js |
| bakery:grilled_salmon_sandwich | 32 | sim | globalRegistry.js |
| bakery:hazelnut_ella | 1000 | sim | globalRegistry.js |
| bakery:jam_roll | 750 | sim | globalRegistry.js |
| bakery:jam_sandwich | 40 | sim | globalRegistryExtraPrices.js |
| bakery:linzer_tart | 1035 | sim | globalRegistry.js |
| bakery:linzer_tart_slice | 258 | sim | globalRegistry.js |
| bakery:milk_bread | 35 | sim | globalRegistryFoodPrices.js |
| bakery:misslilitu_biscuit | 4 | sim | globalRegistry.js |
| bakery:pudding | 100 | sim | globalRegistry.js |
| bakery:pudding_slice | 25 | sim | globalRegistry.js |
| bakery:sandwich | 56 | sim | globalRegistry.js |
| bakery:strawberry_cake | 48 | sim | globalRegistry.js |
| bakery:strawberry_cake_slice | 12 | sim | globalRegistry.js |
| bakery:strawberry_cupcake | 12 | sim | globalRegistry.js |
| bakery:strawberry_glazed_cookie | 16 | sim | globalRegistry.js |
| bakery:strawberry_jam | 21 | sim | globalRegistry.js |
| bakery:sweet_dough | 2 | sim | globalRegistryExternalItems.js |
| bakery:sweetberry_cake | 28 | sim | globalRegistry.js |
| bakery:sweetberry_cake_slice | 7 | sim | globalCanonicalItems.js, globalRegistry.js |
| bakery:sweetberry_cupcake | 7 | sim | globalRegistry.js |
| bakery:sweetberry_glazed_cookie | 12 | sim | globalRegistry.js |
| bakery:sweetberry_jam | 7 | sim | globalCanonicalItems.js, globalRegistry.js |
| bakery:toast | 16 | sim | globalRegistry.js |
| bakery:vegetable_sandwich | 42 | sim | globalRegistry.js |
| bakery:waffle | 18 | sim | globalRegistry.js |
| beachparty:beach_hat | 60 | sim | globalRegistryExtraPrices.js |
| beachparty:bikini | 90 | sim | globalRegistryExtraPrices.js |
| beachparty:chocolate_icecream | 12 | não | globalRegistry.js |
| beachparty:chocolate_milkshake | 80 | não | globalRegistry.js |
| beachparty:cocoa_cocktail | 28 | sim | globalRegistry.js |
| beachparty:coconut | 8 | sim | globalRegistry.js |
| beachparty:coconut_cocktail | 32 | sim | globalRegistry.js |
| beachparty:coconut_drink | 12 | não | globalRegistryFoodPrices.js |
| beachparty:coconut_icecream | 20 | não | globalRegistry.js |
| beachparty:coconut_milkshake | 112 | não | globalRegistry.js |
| beachparty:coconut_open | 12 | sim | globalRegistryFoodPrices.js |
| beachparty:cooked_mussel_meat | 16 | sim | globalRegistry.js |
| beachparty:crocs | 60 | sim | globalRegistryExtraPrices.js |
| beachparty:honey_cocktail | 416 | sim | globalRegistry.js |
| beachparty:icecream_cactus | 40 | não | globalRegistry.js |
| beachparty:icecream_chocolate | 12 | não | globalRegistry.js |
| beachparty:icecream_coconut | 20 | não | globalRegistry.js |
| beachparty:icecream_melon | 28 | não | globalRegistry.js |
| beachparty:icecream_sweetberries | 24 | não | globalRegistry.js |
| beachparty:melon_cocktail | 28 | sim | globalRegistry.js |
| beachparty:palm_log | 4 | sim | globalRegistry.js |
| beachparty:pumpkin_cocktail | 132 | sim | globalRegistry.js |
| beachparty:raw_mussel_meat | 16 | sim | globalRegistry.js |
| beachparty:refreshing_drink | 256 | não | globalRegistry.js |
| beachparty:stripped_palm_log | 4 | sim | globalRegistry.js |
| beachparty:sweetberries_cocktail | 48 | sim | globalRegistry.js |
| beachparty:sweetberry_icecream | 36 | não | globalRegistry.js |
| beachparty:sweetberry_milkshake | 144 | não | globalRegistry.js |
| beachparty:trunks | 80 | sim | globalRegistryExtraPrices.js |
| betterarcheology:artifact_shards | 64 | sim | globalRegistry.js |
| betterarcheology:chicken_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:chicken_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:chicken_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:creeper_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:creeper_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:creeper_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:guardian_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:guardian_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:guardian_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:ocelot_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:ocelot_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:ocelot_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:rotten_log | 12 | sim | globalRegistry.js |
| betterarcheology:sheep_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:sheep_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:sheep_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:unidentified_artifact | 576 | sim | globalRegistry.js |
| betterarcheology:vase | 128 | sim | globalRegistry.js |
| betterarcheology:vase_creeper | 144 | sim | globalRegistry.js |
| betterarcheology:vase_green | 112 | sim | globalRegistry.js |
| betterarcheology:villager_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:villager_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:villager_fossil_head | 192 | sim | globalRegistry.js |
| betterarcheology:wolf_fossil | 896 | sim | globalRegistry.js |
| betterarcheology:wolf_fossil_body | 256 | sim | globalRegistry.js |
| betterarcheology:wolf_fossil_head | 192 | sim | globalRegistry.js |
| botania:black_lotus | 128 | sim | globalRegistry.js |
| botania:black_mushroom | 24 | sim | globalRegistry.js |
| botania:blue_mushroom | 24 | sim | globalRegistry.js |
| botania:brown_mushroom | 24 | sim | globalRegistry.js |
| botania:cosmetic_puffy_scarf | 80 | sim | globalRegistryExtraPrices.js |
| botania:cyan_mushroom | 24 | sim | globalRegistry.js |
| botania:dragonstone | 1400 | sim | globalRegistry.js |
| botania:dragonstone_block | 12600 | sim | globalRegistry.js |
| botania:dreamwood_log | 32 | sim | globalRegistry.js |
| botania:elementium_block | 864 | sim | globalRegistry.js |
| botania:elementium_ingot | 96 | sim | globalRegistry.js |
| botania:gray_mushroom | 24 | sim | globalRegistry.js |
| botania:green_mushroom | 24 | sim | globalRegistry.js |
| botania:life_essence | 9999 | sim | globalRegistry.js |
| botania:light_blue_mushroom | 24 | sim | globalRegistry.js |
| botania:light_gray_mushroom | 24 | sim | globalRegistry.js |
| botania:lime_mushroom | 24 | sim | globalRegistry.js |
| botania:livingwood_log | 16 | sim | globalRegistry.js |
| botania:magenta_mushroom | 24 | sim | globalRegistry.js |
| botania:mana_diamond | 1128 | sim | globalRegistry.js |
| botania:mana_diamond_block | 10152 | sim | globalRegistry.js |
| botania:mana_pearl | 96 | sim | globalRegistry.js |
| botania:mana_string | 384 | sim | globalRegistry.js |
| botania:manasteel_block | 288 | sim | globalRegistry.js |
| botania:manasteel_ingot | 32 | sim | globalRegistry.js |
| botania:manaweave_cloth | 6144 | sim | globalRegistry.js |
| botania:orange_mushroom | 24 | sim | globalRegistry.js |
| botania:pink_mushroom | 24 | sim | globalRegistry.js |
| botania:pixie_dust | 120 | sim | globalRegistry.js |
| botania:purple_mushroom | 24 | sim | globalRegistry.js |
| botania:red_mushroom | 24 | sim | globalRegistry.js |
| botania:shimmering_mushrooms | 24 | não | globalRegistry.js |
| botania:stripped_dreamwood_log | 32 | sim | globalRegistry.js |
| botania:stripped_livingwood_log | 16 | sim | globalRegistry.js |
| botania:terrasteel_block | 396864 | sim | globalRegistry.js |
| botania:terrasteel_ingot | 44096 | sim | globalRegistry.js |
| botania:white_mushroom | 24 | sim | globalRegistry.js |
| botania:yellow_mushroom | 24 | sim | globalRegistry.js |
| brewery:beer_barley | 42 | sim | globalRegistry.js |
| brewery:beer_haley | 49 | sim | globalRegistry.js |
| brewery:beer_hops | 46 | sim | globalRegistry.js |
| brewery:beer_nettle | 49 | sim | globalRegistry.js |
| brewery:beer_oat | 76 | sim | globalRegistry.js |
| brewery:beer_standard | 40 | não | globalRegistryExtraPrices.js |
| brewery:beer_wheat | 94 | sim | globalRegistry.js |
| brewery:brewfest_blouse | 120 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_boots | 100 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_dress | 150 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_hat | 80 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_hat_red | 80 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_regalia | 150 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_shoes | 100 | sim | globalRegistryExtraPrices.js |
| brewery:brewfest_trousers | 120 | sim | globalRegistryExtraPrices.js |
| brewery:dark_brew | 810 | sim | globalRegistry.js |
| brewery:dried_barley | 11 | sim | globalRegistry.js, globalRegistryExternalItems.js |
| brewery:dried_corn | 28 | sim | globalRegistry.js, globalRegistryExternalItems.js |
| brewery:dried_oat | 34 | sim | globalRegistry.js, globalRegistryExternalItems.js |
| brewery:dried_wheat | 46 | sim | globalRegistry.js, globalRegistryExternalItems.js |
| brewery:dumplings | 60 | sim | globalCanonicalItems.js, globalRegistry.js |
| brewery:fried_chicken | 76 | sim | globalRegistry.js |
| brewery:gingerbread | 52 | sim | globalRegistry.js |
| brewery:half_chicken | 12 | sim | globalRegistry.js |
| brewery:hops | 21 | sim | globalPriceBalance.js, globalRegistry.js |
| brewery:mashed_potatoes | 30 | sim | globalRegistry.js |
| brewery:pork_knuckle | 160 | sim | globalRegistry.js |
| brewery:potato_salad | 82 | sim | globalRegistry.js |
| brewery:pretzel | 13 | sim | globalRegistry.js |
| brewery:sausage | 56 | sim | globalRegistry.js |
| brewery:whiskey_ak | 97 | sim | globalRegistry.js |
| brewery:whiskey_carrascon_label | 90 | não | globalRegistryFoodPrices.js |
| brewery:whiskey_carrasconlabel | 115 | sim | globalRegistry.js |
| brewery:whiskey_cristel_walker | 90 | não | globalRegistryFoodPrices.js |
| brewery:whiskey_cristelwalker | 88 | sim | globalRegistry.js |
| brewery:whiskey_highland_hearth | 124 | sim | globalRegistry.js |
| brewery:whiskey_jamesons_malt | 72 | sim | globalRegistry.js |
| brewery:whiskey_jo_jannik | 90 | não | globalRegistryFoodPrices.js |
| brewery:whiskey_jojannik | 38 | sim | globalRegistry.js |
| brewery:whiskey_lilitu_single_malt | 90 | não | globalRegistryFoodPrices.js |
| brewery:whiskey_lilitusinglemalt | 90 | sim | globalRegistry.js |
| brewery:whiskey_maggoallan | 142 | sim | globalRegistry.js |
| brewery:whiskey_smokey_reverie | 106 | sim | globalRegistry.js |
| brewery:whiskey_smoky_reverie | 90 | não | globalRegistryFoodPrices.js |
| brewinandchewin:apple_jelly | 34 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:beer | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:bloody_mary | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:cheesy_pasta | 70 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:cocoa_fudge | 18 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:creamy_onion_soup | 61 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:dread_nog | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:egg_grog | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:fiery_fondue | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| brewinandchewin:fiery_fondue_pot | 652 | sim | globalRegistryExternalItems.js |
| brewinandchewin:flaxen_cheese_wedge | 60 | sim | globalRegistryFoodPrices.js |
| brewinandchewin:flaxen_cheese_wheel | 240 | sim | globalRegistryExternalItems.js |
| brewinandchewin:glittering_grenadine | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:glow_berry_marmalade | 82 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:ham_and_cheese_sandwich | 75 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:horror_lasagna | 174 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:jerky | 35 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:kimchi | 16 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:kippers | 25 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:kombucha | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:mead | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:pale_jane | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:pickled_pickles | 22 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:pizza | 240 | sim | globalRegistryExternalItems.js |
| brewinandchewin:pizza_slice | 60 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:quiche | 280 | sim | globalRegistryExternalItems.js |
| brewinandchewin:quiche_slice | 70 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:red_rum | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:rice_wine | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:saccharine_rum | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:salty_folly | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:scarlet_cheese_wedge | 60 | sim | globalRegistryFoodPrices.js |
| brewinandchewin:scarlet_cheese_wheel | 240 | sim | globalRegistryExternalItems.js |
| brewinandchewin:scarlet_pierogi | 76 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:steel_toe_stout | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:strongroot_ale | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:sweet_berry_jam | 22 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:unripe_flaxen_cheese_wheel | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:unripe_scarlet_cheese_wheel | 30 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:vegetable_omelet | 68 | sim | globalRegistryAddonFoods.js |
| brewinandchewin:vodka | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| brewinandchewin:withering_dross | 30 | sim | globalRegistryAddonFoods.js |
| buzzier_bees:bee_bottle | 16 | sim | globalRegistry.js |
| buzzier_bees:crystallized_honey_block | 24 | sim | globalRegistry.js |
| buzzier_bees:glazed_porkchop | 144 | sim | globalRegistry.js |
| buzzier_bees:honey_apple | 152 | sim | globalRegistry.js |
| buzzier_bees:honey_bread | 24 | sim | globalRegistry.js |
| candlelight:beef_tartare | 14 | sim | globalRegistry.js |
| candlelight:beef_wellington | 1308 | sim | globalRegistry.js |
| candlelight:beef_with_mushroom_in_wine_and_potatoes | 528 | sim | globalRegistry.js |
| candlelight:beef_with_mushroom_in_wine_and_potatoes_1 | 80 | sim | globalRegistryFoodPrices.js |
| candlelight:beef_with_mushroom_in_wine_and_potatoes_2 | 80 | sim | globalRegistryFoodPrices.js |
| candlelight:beef_with_mushroom_in_wine_and_potatoes_3 | 80 | não | globalRegistryFoodPrices.js |
| candlelight:beetroot_salad | 36 | sim | globalRegistry.js |
| candlelight:bolognese | 190 | sim | globalRegistry.js |
| candlelight:chefs_boots | 100 | sim | globalRegistryExtraPrices.js |
| candlelight:chefs_jacket | 130 | sim | globalRegistryExtraPrices.js |
| candlelight:chefs_pants | 110 | sim | globalRegistryExtraPrices.js |
| candlelight:chicken_alfredo | 112 | sim | globalRegistry.js |
| candlelight:chicken_teriyaki | 32 | sim | globalRegistry.js |
| candlelight:chicken_with_vegetables | 144 | sim | globalRegistry.js |
| candlelight:chocolate_mousse | 13 | sim | globalRegistry.js |
| candlelight:cooking_hat | 80 | sim | globalRegistryExtraPrices.js |
| candlelight:dough |  | não | globalCanonicalItems.js |
| candlelight:dress | 150 | sim | globalRegistryExtraPrices.js |
| candlelight:fillet_steak | 272 | sim | globalRegistry.js |
| candlelight:fillet_steak_1 | 50 | sim | globalRegistryFoodPrices.js |
| candlelight:fillet_steak_2 | 50 | sim | globalRegistryFoodPrices.js |
| candlelight:fillet_steak_3 | 50 | não | globalRegistryFoodPrices.js |
| candlelight:flower_crown | 50 | sim | globalRegistryExtraPrices.js |
| candlelight:formal_shirt | 120 | sim | globalRegistryExtraPrices.js |
| candlelight:fresh_garden_salad | 37 | sim | globalRegistry.js |
| candlelight:harvest_plate | 24 | sim | globalRegistry.js |
| candlelight:khinkali | 8 | não | globalRegistry.js |
| candlelight:lasagne | 111 | sim | globalRegistry.js |
| candlelight:mozzarella | 12 | sim | globalRegistry.js |
| candlelight:mushroom_soup | 564 | sim | globalRegistry.js |
| candlelight:mushroom_soup_1 | 70 | sim | globalRegistryFoodPrices.js |
| candlelight:mushroom_soup_2 | 70 | não | globalRegistryFoodPrices.js |
| candlelight:necktie | 60 | sim | globalRegistryExtraPrices.js |
| candlelight:omelet | 22 | sim | globalRegistry.js |
| candlelight:pasta_with_bolognese | 254 | sim | globalRegistry.js |
| candlelight:pasta_with_lettuce | 88 | sim | globalRegistry.js |
| candlelight:pasta_with_mozzarella | 96 | sim | globalRegistry.js |
| candlelight:pork_ribs | 64 | sim | globalRegistry.js |
| candlelight:roastbeef_with_glazed_carrots | 72 | sim | globalRegistry.js |
| candlelight:roasted_lamb_with_lettuce | 128 | sim | globalRegistry.js |
| candlelight:roasted_lamb_with_lettuce_1 | 50 | sim | globalRegistryFoodPrices.js |
| candlelight:roasted_lamb_with_lettuce_2 | 50 | sim | globalRegistryFoodPrices.js |
| candlelight:roasted_lamb_with_lettuce_3 | 50 | não | globalRegistryFoodPrices.js |
| candlelight:salad | 25 | sim | globalRegistry.js |
| candlelight:salmon_on_white_wine | 144 | sim | globalRegistry.js |
| candlelight:salmon_on_white_wine_1 | 80 | sim | globalRegistryFoodPrices.js |
| candlelight:salmon_on_white_wine_2 | 80 | sim | globalRegistryFoodPrices.js |
| candlelight:salmon_on_white_wine_3 | 80 | não | globalRegistryFoodPrices.js |
| candlelight:shirt | 100 | sim | globalRegistryExtraPrices.js |
| candlelight:tomato_mozzarella_salad | 46 | sim | globalRegistry.js |
| candlelight:tomato_sauce | 25 | não | globalRegistryFoodPrices.js |
| candlelight:tomato_soup | 70 | sim | globalRegistry.js |
| candlelight:tomato_soup_1 | 70 | sim | globalRegistryFoodPrices.js |
| candlelight:tomato_soup_2 | 70 | não | globalRegistryFoodPrices.js |
| candlelight:tropical_fish_supreme | 368 | sim | globalRegistry.js |
| candlelight:trousers_and_vest | 140 | sim | globalRegistryExtraPrices.js |
| cluttered:blue_roundhead | 140 | sim | globalRegistry.js |
| cluttered:fly_agaric | 140 | sim | globalRegistry.js |
| crabbersdelight:bisque | 188 | sim | globalRegistry.js |
| crabbersdelight:clam | 4 | sim | globalRegistry.js |
| crabbersdelight:clam_bake | 116 | sim | globalRegistry.js |
| crabbersdelight:clam_barrel | 36 | sim | globalRegistry.js |
| crabbersdelight:clam_chowder | 168 | sim | globalRegistry.js |
| crabbersdelight:clawster | 16 | sim | globalRegistry.js |
| crabbersdelight:clawster_barrel | 144 | sim | globalRegistry.js |
| crabbersdelight:cod_barrel | 432 | sim | globalRegistry.js |
| crabbersdelight:cooked_clam_meat | 8 | sim | globalRegistry.js |
| crabbersdelight:cooked_clawster | 16 | sim | globalRegistry.js |
| crabbersdelight:cooked_crab | 8 | sim | globalRegistry.js |
| crabbersdelight:cooked_frog_leg | 40 | sim | globalRegistry.js |
| crabbersdelight:cooked_glow_squid_tentacles | 32 | sim | globalRegistry.js |
| crabbersdelight:cooked_pufferfish_slice | 12 | sim | globalRegistryExtraPrices.js |
| crabbersdelight:cooked_shrimp | 4 | sim | globalRegistry.js |
| crabbersdelight:cooked_squid_tentacles | 16 | sim | globalRegistry.js |
| crabbersdelight:cooked_tropical_fish | 72 | sim | globalRegistry.js |
| crabbersdelight:cooked_tropical_fish_slice | 24 | sim | globalRegistryExtraPrices.js |
| crabbersdelight:coral_crunch | 48 | sim | globalRegistry.js |
| crabbersdelight:crab | 8 | sim | globalCanonicalItems.js, globalRegistry.js |
| crabbersdelight:crab_barrel | 72 | sim | globalRegistry.js |
| crabbersdelight:crab_cakes | 123 | sim | globalRegistry.js |
| crabbersdelight:crab_claw | 30 | sim | globalRegistryFoodPrices.js |
| crabbersdelight:crab_legs | 30 | sim | globalRegistryFoodPrices.js |
| crabbersdelight:fish_stick | 128 | sim | globalRegistry.js |
| crabbersdelight:frog_leg_barrel | 360 | sim | globalRegistry.js |
| crabbersdelight:frog_leg_kebab | 149 | sim | globalRegistry.js |
| crabbersdelight:glow_squid_barrel | 288 | sim | globalRegistry.js |
| crabbersdelight:jar_of_pickles | 4 | sim | globalRegistry.js |
| crabbersdelight:kelp_shake | 8 | sim | globalRegistry.js |
| crabbersdelight:nautilus_shell_block | 640 | sim | globalRegistry.js |
| crabbersdelight:pearl | 64 | sim | globalRegistry.js |
| crabbersdelight:pearl_block | 512 | sim | globalRegistry.js |
| crabbersdelight:pufferfish_barrel | 144 | sim | globalRegistry.js |
| crabbersdelight:pufferfish_slice | 8 | sim | globalRegistryExtraPrices.js |
| crabbersdelight:raw_clam_meat | 8 | sim | globalRegistry.js |
| crabbersdelight:raw_frog_leg | 40 | sim | globalRegistry.js |
| crabbersdelight:raw_glow_squid_tentacles | 32 | sim | globalRegistry.js |
| crabbersdelight:raw_squid_tentacles | 16 | sim | globalRegistry.js |
| crabbersdelight:salmon_barrel | 216 | sim | globalRegistry.js |
| crabbersdelight:sea_pickle_juice | 8 | sim | globalRegistry.js |
| crabbersdelight:seafood_gumbo | 120 | sim | globalRegistry.js |
| crabbersdelight:shrimp | 4 | sim | globalRegistry.js |
| crabbersdelight:shrimp_barrel | 36 | sim | globalRegistry.js |
| crabbersdelight:shrimp_fried_rice | 95 | sim | globalRegistry.js |
| crabbersdelight:shrimp_skewer | 38 | sim | globalRegistry.js |
| crabbersdelight:squid_barrel | 144 | sim | globalRegistry.js |
| crabbersdelight:squid_kebab | 82 | sim | globalRegistry.js |
| crabbersdelight:stuffed_nautilus_shell | 192 | sim | globalRegistry.js |
| crabbersdelight:surf_and_turf | 72 | sim | globalRegistry.js |
| crabbersdelight:tropical_fish_barrel | 648 | sim | globalRegistry.js |
| crabbersdelight:tropical_fish_slice | 20 | sim | globalRegistryExtraPrices.js |
| create:bar_of_chocolate | 30 | sim | globalRegistry.js |
| create:builders_tea | 352 | sim | globalRegistry.js |
| create:chocolate_glazed_berries | 34 | sim | globalRegistry.js |
| create:cinder_flour | 20 | sim | globalRegistryFoodPrices.js |
| create:copper_nugget | 1 | sim | globalRegistryCreateMetals.js |
| create:crushed_raw_copper | 5 | sim | globalRegistryCreateMetals.js |
| create:crushed_raw_gold | 22 | sim | globalRegistryCreateMetals.js |
| create:crushed_raw_iron | 11 | sim | globalRegistryCreateMetals.js |
| create:crushed_raw_zinc | 11 | sim | globalRegistryCreateMetals.js |
| create:dough | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| create:experience_block | 18 | sim | globalRegistry.js |
| create:experience_nugget | 2 | sim | globalRegistry.js |
| create:honeyed_apple | 32 | sim | globalRegistry.js |
| create:raw_zinc | 8 | sim | globalRegistry.js |
| create:raw_zinc_block | 72 | sim | globalRegistry.js |
| create:sweet_roll | 64 | sim | globalRegistry.js |
| create:wheat_flour | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| create:zinc_block | 99 | sim | globalRegistryCreateMetals.js |
| create:zinc_ingot | 11 | sim | globalRegistryCreateMetals.js |
| create:zinc_nugget | 1 | sim | globalRegistryCreateMetals.js |
| create_central_kitchen:aloe_cake_slice | 70 | não | globalRegistryFoodPrices.js |
| create_central_kitchen:honey_cake_slice | 70 | não | globalRegistryFoodPrices.js |
| create_central_kitchen:mulberry_pie_slice | 70 | não | globalRegistryFoodPrices.js |
| create_central_kitchen:passion_fruit_cake_slice | 60 | não | globalRegistryExtraPrices.js |
| create_central_kitchen:pumpkin_cake_slice | 70 | não | globalRegistryFoodPrices.js |
| create_central_kitchen:sweet_berry_cake_slice | 70 | não | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| create_central_kitchen:truffle_pie_slice | 70 | não | globalRegistryFoodPrices.js |
| create_central_kitchen:yucca_cake_slice | 70 | não | globalRegistryFoodPrices.js |
| create_enchantment_industry:hyper_experience_bottle | 550 | não | globalRegistry.js |
| crittersandcompanions:clam | 512 | sim | globalRegistry.js |
| crittersandcompanions:dragonfly_wing | 3300 | sim | globalRegistry.js |
| crittersandcompanions:koi_fish | 340 | sim | globalRegistry.js |
| crittersandcompanions:silk | 128 | sim | globalRegistry.js |
| cuisinedelight:fried_egg | 50 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| cuisinedelight:fried_meat_and_melon | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:fried_mushroom | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:fried_pasta | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:fried_rice | 50 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| cuisinedelight:ham_fried_rice | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:meat_fried_rice | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:meat_pasta | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:meat_platter | 90 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:meat_with_seafood | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:meat_with_vegetables | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:mixed_fried_rice | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:mixed_pasta | 50 | sim | globalRegistryExternalItems.js |
| cuisinedelight:scrambled_egg_and_tomato | 12 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:seafood_fried_rice | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:seafood_pasta | 50 | sim | globalRegistryExternalItems.js |
| cuisinedelight:seafood_platter | 90 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:vegetable_fried_rice | 50 | sim | globalRegistryFoodPrices.js |
| cuisinedelight:vegetable_platter | 90 | sim | globalRegistryFoodPrices.js |
| culturaldelights:avocado | 24 | sim | globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:avocado_crate |  | sim | globalRegistryStorageBlockPrices.js |
| culturaldelights:avocado_toast | 6 | sim | globalRegistryAddonFoods.js |
| culturaldelights:beef_burrito | 58 | sim | globalRegistryAddonFoods.js |
| culturaldelights:calamari_roll | 41 | sim | globalRegistryAddonFoods.js |
| culturaldelights:chicken_roll | 138 | sim | globalRegistryAddonFoods.js |
| culturaldelights:chicken_roll_slice | 60 | sim | globalRegistryAddonFoods.js |
| culturaldelights:chicken_taco | 151 | sim | globalRegistryAddonFoods.js |
| culturaldelights:cooked_calamari | 28 | sim | globalRegistryAddonFoods.js |
| culturaldelights:cooked_squid | 28 | sim | globalRegistryAddonFoods.js |
| culturaldelights:corn_cob | 16 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:corn_cob_crate |  | sim | globalRegistryStorageBlockPrices.js |
| culturaldelights:corn_dough | 4 | sim | globalRegistryAddonFoods.js |
| culturaldelights:corn_kernels | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| culturaldelights:creamed_corn | 22 | sim | globalRegistryAddonFoods.js |
| culturaldelights:cucumber | 16 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:cucumber_crate |  | sim | globalRegistryStorageBlockPrices.js |
| culturaldelights:cucumber_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| culturaldelights:cut_avocado | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| culturaldelights:cut_cucumber | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| culturaldelights:cut_eggplant | 8 | sim | globalRegistryAddonFoods.js |
| culturaldelights:cut_pickle | 30 | sim | globalRegistryAddonFoods.js |
| culturaldelights:egg_roll | 14 | sim | globalRegistryAddonFoods.js |
| culturaldelights:eggplant | 24 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:eggplant_burger | 63 | sim | globalRegistryAddonFoods.js |
| culturaldelights:eggplant_crate |  | sim | globalRegistryStorageBlockPrices.js |
| culturaldelights:eggplant_parmesan | 30 | sim | globalRegistryAddonFoods.js |
| culturaldelights:eggplant_parmesan_block | 120 | sim | globalRegistryExternalItems.js |
| culturaldelights:elote | 21 | sim | globalRegistryAddonFoods.js |
| culturaldelights:empanada | 25 | sim | globalRegistryAddonFoods.js |
| culturaldelights:exotic_roll_medley | 888 | sim | globalRegistryExternalItems.js |
| culturaldelights:fish_taco | 64 | sim | globalRegistryAddonFoods.js |
| culturaldelights:fried_eggplant_pasta | 50 | sim | globalRegistryFoodPrices.js |
| culturaldelights:ginger | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| culturaldelights:glow_squid | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| culturaldelights:hearty_salad | 33 | sim | globalRegistryAddonFoods.js |
| culturaldelights:lemon | 12 | sim | globalRegistryFoodPrices.js |
| culturaldelights:midori_roll | 96 | sim | globalRegistryAddonFoods.js |
| culturaldelights:midori_roll_slice | 30 | sim | globalRegistryAddonFoods.js |
| culturaldelights:mutton_sandwich | 68 | sim | globalRegistryAddonFoods.js |
| culturaldelights:pickle | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:pickle_crate |  | sim | globalRegistryStorageBlockPrices.js |
| culturaldelights:poached_eggplants | 129 | sim | globalRegistryAddonFoods.js |
| culturaldelights:popcorn | 10 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| culturaldelights:pork_wrap | 52 | sim | globalRegistryAddonFoods.js |
| culturaldelights:pufferfish_roll | 32 | sim | globalRegistryAddonFoods.js |
| culturaldelights:raw_calamari | 18 | sim | globalRegistryAddonFoods.js |
| culturaldelights:rice_ball | 36 | sim | globalRegistryAddonFoods.js |
| culturaldelights:smoked_corn | 30 | sim | globalRegistryAddonFoods.js |
| culturaldelights:smoked_cut_eggplant | 28 | sim | globalRegistryAddonFoods.js |
| culturaldelights:smoked_eggplant | 1 | sim | globalRegistryAddonFoods.js |
| culturaldelights:smoked_tomato | 24 | sim | globalRegistryAddonFoods.js |
| culturaldelights:smoked_white_eggplant | 1 | sim | globalRegistryAddonFoods.js |
| culturaldelights:spicy_curry | 206 | sim | globalRegistryAddonFoods.js |
| culturaldelights:squid | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| culturaldelights:tortilla | 4 | sim | globalRegistryAddonFoods.js |
| culturaldelights:tortilla_chips | 2 | sim | globalRegistryAddonFoods.js |
| culturaldelights:tropical_roll | 93 | sim | globalRegistryAddonFoods.js |
| culturaldelights:white_eggplant | 24 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| culturaldelights:white_eggplant_crate |  | sim | globalRegistryStorageBlockPrices.js |
| etcetera:black_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:black_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:blue_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:blue_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:brown_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:brown_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:cotton_flower | 24 | sim | globalRegistry.js |
| etcetera:cyan_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:cyan_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:gray_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:gray_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:green_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:green_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:light_blue_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:light_blue_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:light_gray_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:light_gray_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:lime_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:lime_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:magenta_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:magenta_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:orange_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:orange_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:pink_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:pink_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:purple_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:purple_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:raw_bismuth | 32 | sim | globalRegistry.js |
| etcetera:raw_bismuth_block | 288 | sim | globalRegistry.js |
| etcetera:red_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:red_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:trader_hood | 100 | sim | globalRegistryExtraPrices.js |
| etcetera:white_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:white_sweater | 120 | sim | globalRegistryExtraPrices.js |
| etcetera:yellow_hat | 80 | sim | globalRegistryExtraPrices.js |
| etcetera:yellow_sweater | 120 | sim | globalRegistryExtraPrices.js |
| farm_and_charm:bacon | 50 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:bacon_with_eggs | 35 | sim | globalRegistry.js |
| farm_and_charm:baked_lamb_ham | 40 | sim | globalRegistry.js |
| farm_and_charm:barley | 11 | sim | globalPriceBalance.js, globalRegistry.js |
| farm_and_charm:barley_ball | 99 | sim | globalRegistry.js |
| farm_and_charm:barley_patties_with_potatoes | 80 | sim | globalRegistry.js |
| farm_and_charm:barley_seeds | 8 | sim | globalRegistryFoodPrices.js |
| farm_and_charm:barley_soup | 19 | sim | globalRegistry.js |
| farm_and_charm:beef_patty_with_vegetables | 108 | sim | globalRegistry.js |
| farm_and_charm:beetroot_bag | 216 | sim | globalRegistry.js |
| farm_and_charm:butter | 16 | sim | globalRegistry.js |
| farm_and_charm:carrot_bag | 207 | sim | globalRegistry.js |
| farm_and_charm:chicken_parts | 50 | sim | globalRegistryFoodPrices.js |
| farm_and_charm:chicken_wrapped_in_bacon | 132 | sim | globalRegistry.js |
| farm_and_charm:cooked_cod | 143 | sim | globalRegistry.js |
| farm_and_charm:cooked_salmon | 162 | sim | globalRegistry.js |
| farm_and_charm:corn | 28 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| farm_and_charm:corn_bag | 252 | sim | globalRegistry.js |
| farm_and_charm:corn_grits | 72 | sim | globalRegistry.js |
| farm_and_charm:dog_food |  | sim | globalCanonicalItems.js |
| farm_and_charm:dough | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:farmer_salad | 60 | sim | globalRegistry.js |
| farm_and_charm:farmers_bread | 12 | sim | globalRegistry.js |
| farm_and_charm:farmers_breakfast | 390 | sim | globalRegistry.js |
| farm_and_charm:flour | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:goulash | 309 | sim | globalRegistry.js |
| farm_and_charm:grandmothers_strawberry_cake | 18 | sim | globalRegistry.js |
| farm_and_charm:kernels | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:lamb_ham | 64 | sim | globalRegistryExtraPrices.js |
| farm_and_charm:lamb_with_corn | 148 | sim | globalRegistry.js |
| farm_and_charm:lettuce | 24 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| farm_and_charm:lettuce_bag | 216 | sim | globalRegistry.js |
| farm_and_charm:lettuce_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:minced_beef | 50 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:nettle_tea | 52 | sim | globalRegistry.js |
| farm_and_charm:nettle_tea_cup | 52 | sim | globalRegistryExtraPrices.js |
| farm_and_charm:oat | 36 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| farm_and_charm:oat_ball | 324 | sim | globalRegistry.js |
| farm_and_charm:oat_pancake | 84 | sim | globalRegistry.js |
| farm_and_charm:oat_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:oatmeal_with_strawberries | 58 | sim | globalRegistry.js |
| farm_and_charm:onion | 12 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| farm_and_charm:onion_bag | 108 | sim | globalRegistry.js |
| farm_and_charm:onion_soup | 32 | sim | globalCanonicalItems.js, globalRegistry.js |
| farm_and_charm:pasta_with_onion_sauce | 10 | sim | globalRegistry.js |
| farm_and_charm:potato_bag | 216 | sim | globalRegistry.js |
| farm_and_charm:potato_soup | 36 | sim | globalRegistry.js |
| farm_and_charm:potato_with_roast_meat | 24 | sim | globalRegistry.js |
| farm_and_charm:raw_pasta | 20 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| farm_and_charm:ribwort_tea | 52 | sim | globalRegistry.js |
| farm_and_charm:ribwort_tea_cup | 52 | sim | globalRegistryExtraPrices.js |
| farm_and_charm:roasted_chicken | 47 | sim | globalRegistry.js |
| farm_and_charm:roasted_corn | 88 | sim | globalRegistry.js |
| farm_and_charm:rotten_tomato | 12 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:sausage_with_oat_patty | 108 | sim | globalRegistry.js |
| farm_and_charm:simple_tomato_soup | 55 | sim | globalRegistry.js |
| farm_and_charm:strawberry | 18 | sim | globalPriceBalance.js, globalRegistry.js |
| farm_and_charm:strawberry_bag | 162 | sim | globalRegistry.js |
| farm_and_charm:strawberry_tea | 40 | sim | globalRegistry.js |
| farm_and_charm:strawberry_tea_cup | 40 | sim | globalRegistryExtraPrices.js |
| farm_and_charm:stuffed_chicken | 43 | sim | globalRegistry.js |
| farm_and_charm:stuffed_rabbit | 99 | sim | globalRegistry.js |
| farm_and_charm:tomato | 12 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:tomato_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farm_and_charm:wild_nettle | 24 | sim | globalRegistry.js |
| farm_and_charm:wild_ribwort | 24 | sim | globalRegistry.js |
| farm_and_charm:yeast | 2 | sim | globalRegistryExternalItems.js |
| farmersdelight:apple_cider | 179 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:apple_pie | 597 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:apple_pie_slice | 150 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:bacon | 12 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| farmersdelight:bacon_and_eggs | 50 | sim | globalRegistryFoodPrices.js |
| farmersdelight:bacon_sandwich | 171 | sim | globalRegistry.js |
| farmersdelight:baked_cod_stew | 255 | sim | globalRegistry.js |
| farmersdelight:barbecue_stick | 58 | sim | globalRegistry.js |
| farmersdelight:beef_patty | 16 | sim | globalRegistryExtraPrices.js |
| farmersdelight:beef_stew | 64 | sim | globalRegistry.js |
| farmersdelight:bone_broth | 70 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| farmersdelight:brown_mushroom_colony | 48 | sim | globalRegistry.js |
| farmersdelight:cabbage | 70 | sim | globalPriceBalance.js, globalRegistry.js |
| farmersdelight:cabbage_crate | 630 | sim | globalRegistry.js |
| farmersdelight:cabbage_leaf | 6 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| farmersdelight:cabbage_rolls | 102 | sim | globalRegistry.js |
| farmersdelight:cabbage_seeds | 8 | sim | globalRegistryFoodPrices.js |
| farmersdelight:cake_slice | 64 | sim | globalRegistry.js |
| farmersdelight:canvas | 12 | sim | globalRegistry.js |
| farmersdelight:chicken_cuts | 10 | sim | globalRegistryExtraPrices.js |
| farmersdelight:chicken_sandwich | 114 | sim | globalRegistry.js |
| farmersdelight:chicken_soup | 120 | sim | globalRegistry.js |
| farmersdelight:chocolate_pie | 660 | sim | globalRegistry.js |
| farmersdelight:chocolate_pie_slice | 165 | sim | globalRegistry.js |
| farmersdelight:cod_roll | 56 | sim | globalRegistry.js |
| farmersdelight:cod_slice | 10 | sim | globalRegistryExtraPrices.js |
| farmersdelight:cooked_bacon | 16 | sim | globalRegistryExtraPrices.js |
| farmersdelight:cooked_chicken_cuts | 14 | sim | globalRegistryExtraPrices.js |
| farmersdelight:cooked_cod_slice | 14 | sim | globalRegistryExtraPrices.js |
| farmersdelight:cooked_mutton_chops | 14 | sim | globalRegistryExtraPrices.js |
| farmersdelight:cooked_rice | 16 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:cooked_salmon_slice | 16 | sim | globalRegistryExtraPrices.js |
| farmersdelight:dog_food |  | sim | globalCanonicalItems.js |
| farmersdelight:dumplings | 102 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:egg_sandwich | 28 | sim | globalRegistry.js |
| farmersdelight:fish_stew | 154 | sim | globalRegistry.js |
| farmersdelight:fried_egg | 20 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| farmersdelight:fried_rice | 85 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:fruit_salad | 164 | sim | globalRegistry.js |
| farmersdelight:gleaming_salad | 100 | sim | globalRegistryExtraPrices.js |
| farmersdelight:glow_berry_custard | 215 | sim | globalRegistry.js |
| farmersdelight:grilled_salmon | 111 | sim | globalRegistry.js |
| farmersdelight:ham | 64 | sim | globalRegistry.js |
| farmersdelight:hamburger | 153 | sim | globalRegistry.js |
| farmersdelight:honey_cookie | 64 | sim | globalRegistry.js |
| farmersdelight:honey_glazed_ham | 60 | sim | globalRegistry.js |
| farmersdelight:honey_glazed_ham_block | 240 | sim | globalRegistry.js |
| farmersdelight:hot_cocoa | 27 | sim | globalRegistry.js |
| farmersdelight:kelp_roll | 73 | sim | globalRegistry.js |
| farmersdelight:kelp_roll_slice | 26 | sim | globalRegistry.js |
| farmersdelight:melon_juice | 66 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:melon_popsicle | 52 | sim | globalRegistry.js |
| farmersdelight:minced_beef | 12 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| farmersdelight:mixed_salad | 74 | sim | globalRegistry.js |
| farmersdelight:mushroom_rice | 72 | sim | globalRegistry.js |
| farmersdelight:mutton_chops | 10 | sim | globalRegistryExtraPrices.js |
| farmersdelight:mutton_wrap | 114 | sim | globalRegistry.js |
| farmersdelight:nether_salad | 288 | sim | globalRegistry.js |
| farmersdelight:noodle_soup | 87 | sim | globalRegistry.js |
| farmersdelight:onion | 12 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farmersdelight:onion_soup | 90 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| farmersdelight:pasta_with_meatballs | 84 | sim | globalRegistry.js |
| farmersdelight:pasta_with_mutton_chop | 110 | sim | globalRegistry.js |
| farmersdelight:pie_crust | 20 | sim | globalRegistryExtraPrices.js |
| farmersdelight:pumpkin_pie_slice | 21 | sim | globalRegistry.js, globalRegistryExtraPrices.js |
| farmersdelight:pumpkin_slice | 20 | sim | globalPriceBalance.js, globalRegistry.js |
| farmersdelight:pumpkin_soup | 140 | sim | globalRegistry.js |
| farmersdelight:ratatouille | 129 | sim | globalRegistry.js |
| farmersdelight:raw_pasta |  | sim | globalCanonicalItems.js |
| farmersdelight:red_mushroom_colony | 48 | sim | globalRegistry.js |
| farmersdelight:rice | 16 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| farmersdelight:rice_bag | 144 | sim | globalRegistry.js |
| farmersdelight:rice_panicle | 5 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farmersdelight:rice_roll_medley_block | 290 | sim | globalRegistry.js |
| farmersdelight:roast_chicken | 60 | sim | globalRegistry.js |
| farmersdelight:roast_chicken_block | 243 | sim | globalRegistry.js |
| farmersdelight:roasted_mutton_chops | 134 | sim | globalRegistry.js |
| farmersdelight:rotten_tomato | 1 | sim | globalCanonicalItems.js, globalRegistry.js |
| farmersdelight:salmon_roll | 36 | sim | globalRegistry.js |
| farmersdelight:salmon_slice | 12 | sim | globalRegistryExtraPrices.js |
| farmersdelight:shepherds_pie | 65 | sim | globalRegistry.js |
| farmersdelight:shepherds_pie_block | 261 | sim | globalRegistry.js |
| farmersdelight:smoked_ham | 64 | sim | globalRegistry.js |
| farmersdelight:squid_ink_pasta | 165 | sim | globalRegistry.js |
| farmersdelight:steak_and_potatoes | 144 | sim | globalRegistry.js |
| farmersdelight:straw | 3 | sim | globalRegistry.js |
| farmersdelight:straw_bale | 27 | sim | globalRegistry.js |
| farmersdelight:stuffed_potato | 92 | sim | globalRegistry.js |
| farmersdelight:stuffed_pumpkin | 75 | sim | globalRegistry.js |
| farmersdelight:stuffed_pumpkin_block | 300 | sim | globalRegistry.js |
| farmersdelight:sweet_berry_cheesecake | 454 | sim | globalRegistry.js |
| farmersdelight:sweet_berry_cheesecake_slice | 114 | sim | globalRegistry.js |
| farmersdelight:sweet_berry_cookie | 8 | sim | globalRegistry.js |
| farmersdelight:tomato | 24 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| farmersdelight:tomato_crate | 216 | sim | globalRegistry.js |
| farmersdelight:tomato_sauce | 52 | sim | globalRegistry.js |
| farmersdelight:tomato_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farmersdelight:vegetable_noodles | 136 | sim | globalRegistry.js |
| farmersdelight:vegetable_soup | 144 | sim | globalRegistry.js |
| farmersdelight:wheat_dough | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| farmersdelight:wild_beetroots | 12 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_cabbages | 12 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_carrots | 12 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_onions | 12 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_potatoes | 12 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_rice | 20 | sim | globalRegistryFoodPrices.js |
| farmersdelight:wild_tomatoes | 12 | sim | globalRegistryFoodPrices.js |
| farmersrespite:apple_cider | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:black_cod | 92 | sim | globalRegistryAddonFoods.js |
| farmersrespite:black_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| farmersrespite:black_tea_leaves | 10 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| farmersrespite:black_tea_leaves_sack | 90 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| farmersrespite:blazing_chili | 58 | sim | globalRegistryAddonFoods.js |
| farmersrespite:coffee | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| farmersrespite:coffee_beans | 20 | sim | globalCanonicalItems.js, globalRegistryDrinkPrices.js |
| farmersrespite:coffee_beans_sack | 90 | sim | globalRegistryAddonFoods.js |
| farmersrespite:coffee_berries | 12 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| farmersrespite:coffee_cake | 350 | sim | globalRegistryExternalItems.js |
| farmersrespite:coffee_cake_slice | 50 | sim | globalRegistryAddonFoods.js |
| farmersrespite:dandelion_tea | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:gamblers_tea | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:green_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| farmersrespite:green_tea_cookie | 13 | sim | globalRegistryAddonFoods.js |
| farmersrespite:green_tea_leaves | 10 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| farmersrespite:green_tea_leaves_sack | 90 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| farmersrespite:hot_cocoa | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:melon_juice | 80 | sim | globalRegistryExtraPrices.js |
| farmersrespite:nether_wart_sourdough | 28 | sim | globalRegistryAddonFoods.js |
| farmersrespite:purulent_tea | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:rose_hip_pie | 220 | sim | globalRegistryExternalItems.js |
| farmersrespite:rose_hip_pie_slice | 55 | sim | globalRegistryAddonFoods.js |
| farmersrespite:rose_hip_tea | 30 | sim | globalRegistryAddonFoods.js |
| farmersrespite:rose_hips | 8 | sim | globalRegistryExternalItems.js |
| farmersrespite:tea_curry | 88 | sim | globalRegistryAddonFoods.js |
| farmersrespite:tea_seeds | 8 | sim | globalRegistryFoodPrices.js |
| farmersrespite:yellow_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| farmersrespite:yellow_tea_leaves | 10 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| farmersrespite:yellow_tea_leaves_sack | 90 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| faunaandorchestra:baseball_cap | 80 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:baseball_jacket | 130 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:floral_boots | 100 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:fluffy_boots | 110 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:fortune_cookie | 20 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:propeller_hat | 90 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:santa_hat | 90 | sim | globalRegistryExtraPrices.js |
| faunaandorchestra:top_hat | 100 | sim | globalRegistryExtraPrices.js |
| furniture:trash_bag | 1 | sim | globalRegistry.js |
| gamediscs:game_disc_blocktris | 10000 | sim | globalRegistry.js |
| gamediscs:game_disc_flappy_bird | 490 | sim | globalRegistry.js |
| gamediscs:game_disc_froggie | 3200 | sim | globalRegistry.js |
| gamediscs:game_disc_pong | 4900 | sim | globalRegistry.js |
| gamediscs:game_disc_rabbit | 4096 | sim | globalRegistry.js |
| gamediscs:game_disc_slime | 999 | sim | globalRegistry.js |
| gamediscs:game_disc_tnt_sweeper | 2048 | sim | globalRegistry.js |
| golemoverhaul:honey_blob | 72 | sim | globalRegistry.js |
| hauntedharvest:candy_corn | 10 | sim | globalRegistryAddonFoods.js |
| hauntedharvest:corn | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| hauntedharvest:corn_crate | 10 | sim | globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| hauntedharvest:corn_on_the_cob | 1 | sim | globalRegistryAddonFoods.js |
| hauntedharvest:cornbread | 15 | sim | globalRegistryAddonFoods.js |
| hauntedharvest:grim_apple | 12 | sim | globalRegistryFoodPrices.js |
| hauntedharvest:kernels | 8 | sim | globalRegistryFoodPrices.js |
| hauntedharvest:popcorn | 28 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hauntedharvest:rotten_apple | 2 | sim | globalRegistryAddonFoods.js |
| hauntedharvest:succotash | 65 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:apple_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:apple_jam | 54 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:baked_apple | 50 | sim | globalRegistryFoodPrices.js |
| hearthandharvest:batter | 62 | sim | globalRegistryExternalItems.js |
| hearthandharvest:biscuits_and_gravy | 40 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:blueberries | 24 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_crate | 216 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_jam | 33 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_juice | 82 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_muffin | 59 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_pie | 220 | sim | globalRegistryExternalItems.js |
| hearthandharvest:blueberry_pie_slice | 55 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:blueberry_wine | 1 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| hearthandharvest:brown_mushroom_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:caramel | 25 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:caramel_apple | 83 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:carrot_cake |  | sim | globalCanonicalItems.js |
| hearthandharvest:carrot_cake_slice | 50 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:charred_marshmallow_stick | 28 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:cheddar_cheese_slice | 30 | não | globalRegistryAddonFoods.js |
| hearthandharvest:cheddar_cheese_wheel | 1152 | não | globalRegistry.js |
| hearthandharvest:cherry |  | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| hearthandharvest:cherry_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:cherry_jam | 33 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:cherry_juice | 82 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:cherry_pie_slice | 70 | sim | globalRegistryFoodPrices.js |
| hearthandharvest:cherry_wine | 1 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| hearthandharvest:chicken_pot_pie | 360 | sim | globalRegistryExternalItems.js |
| hearthandharvest:chicken_pot_pie_slice | 90 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:chocolate_bar | 38 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:cocoa_bean_bag |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:cooked_sausage | 12 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:cooking_oil | 25 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| hearthandharvest:cotton_candy | 50 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:crimson_fungus_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:egg_crate |  | não | globalRegistryStorageBlockPrices.js |
| hearthandharvest:glow_berry_crate | 216 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:glow_berry_jam | 102 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:goat_cheese_slice | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:goat_cheese_wheel | 1152 | sim | globalRegistryExternalItems.js |
| hearthandharvest:golden_apple_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:golden_carrot_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:grape_jam | 60 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:grape_pie | 220 | sim | globalRegistryExternalItems.js |
| hearthandharvest:grape_pie_slice | 55 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:green_grape_crate | 180 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:green_grape_juice | 72 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:green_grape_wine | 1 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| hearthandharvest:green_grapes | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:jerky | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:macaroni_and_cheese | 36 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:marshmallow_stick | 28 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:mashed_potatoes | 59 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:mead | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:melon_jam | 57 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:onion_soup | 41 | não | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:peanut | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| hearthandharvest:peanut_butter | 28 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:peanut_butter_and_jelly_sandwich | 84 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:peanut_butter_cookie | 15 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:peanut_butter_pie | 240 | sim | globalRegistryExternalItems.js |
| hearthandharvest:peanut_butter_pie_slice | 60 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:peanut_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:pickled_beetroots | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:pickled_cabbage | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:pickled_carrots | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:pickled_onions | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:pickled_potatoes | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:poisonous_potato_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:raisins | 10 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:raspberry | 20 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:raspberry_crate | 180 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:raspberry_jam | 33 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:raspberry_juice | 72 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:raspberry_pie | 220 | sim | globalRegistryExternalItems.js |
| hearthandharvest:raspberry_pie_slice | 55 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:raspberry_wine | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:raw_sausage | 12 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:red_grape_crate | 180 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:red_grape_juice | 72 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:red_grape_wine | 30 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:red_grapes | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:red_mushroom_crate |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:roasted_marshmallow_stick | 28 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:roasted_peanuts | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:salt | 5 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| hearthandharvest:salt_bag |  | sim | globalRegistryStorageBlockPrices.js |
| hearthandharvest:skewered_sausage | 22 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:smore | 90 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:sunflower_seeds | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| hearthandharvest:sweet_berry_crate | 36 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| hearthandharvest:sweet_berry_jam | 42 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:sweet_berry_wine | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| hearthandharvest:syrup_bottle | 30 | sim | globalRegistryFoodPrices.js |
| hearthandharvest:trail_mix | 16 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:turtle_egg_crate |  | não | globalRegistryStorageBlockPrices.js |
| hearthandharvest:unripe_cheddar_cheese_wheel | 30 | não | globalRegistryAddonFoods.js |
| hearthandharvest:unripe_goat_cheese_wheel | 12 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:waffle | 40 | sim | globalRegistryAddonFoods.js |
| hearthandharvest:warped_fungus_crate |  | sim | globalRegistryStorageBlockPrices.js |
| herbalbrews:black_tea | 1296 | sim | globalRegistry.js |
| herbalbrews:chai_tea | 2643 | sim | globalRegistry.js |
| herbalbrews:cinnamon_coffee | 138 | sim | globalRegistry.js |
| herbalbrews:coffee | 48 | sim | globalCanonicalItems.js, globalRegistry.js |
| herbalbrews:coffee_beans | 8 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| herbalbrews:coffee_beans_sack | 72 | sim | globalRegistry.js |
| herbalbrews:dried_black_tea | 1080 | sim | globalRegistry.js |
| herbalbrews:dried_green_tea | 120 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| herbalbrews:dried_green_tea_leaf_block |  | sim | globalRegistryStorageBlockPrices.js |
| herbalbrews:dried_oolong_tea | 3200 | sim | globalRegistry.js |
| herbalbrews:green_tea | 144 | sim | globalRegistry.js |
| herbalbrews:green_tea_leaf | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| herbalbrews:green_tea_leaf_block | 180 | sim | globalRegistry.js |
| herbalbrews:ground_coffee | 12 | sim | globalRegistry.js |
| herbalbrews:hazelnut_coffee | 90 | sim | globalRegistry.js |
| herbalbrews:herbal_infusion | 52 | sim | globalRegistryExtraPrices.js |
| herbalbrews:hibiscus | 16 | sim | globalRegistryDrinkPrices.js |
| herbalbrews:hibiscus_tea | 16 | sim | globalRegistry.js |
| herbalbrews:lavender_blossom | 16 | sim | globalRegistryDrinkPrices.js |
| herbalbrews:lavender_tea | 16 | sim | globalRegistry.js |
| herbalbrews:milk_coffee | 112 | sim | globalRegistry.js |
| herbalbrews:oolong_tea | 3840 | sim | globalCanonicalItems.js, globalRegistry.js |
| herbalbrews:rooibos_leaf | 8 | sim | globalPriceBalance.js, globalRegistry.js |
| herbalbrews:rooibos_leaf_block | 72 | sim | globalRegistry.js |
| herbalbrews:rooibos_tea | 20 | sim | globalRegistry.js |
| herbalbrews:tea_leaf_crate |  | sim | globalRegistryStorageBlockPrices.js |
| herbalbrews:top_hat | 100 | sim | globalRegistryExtraPrices.js |
| herbalbrews:witch_hat | 100 | sim | globalRegistryExtraPrices.js |
| herbalbrews:yerba_mate_leaf | 6 | sim | globalPriceBalance.js, globalRegistry.js |
| herbalbrews:yerba_mate_leaf_block | 54 | sim | globalRegistry.js |
| herbalbrews:yerba_mate_tea | 12 | sim | globalRegistry.js |
| kaleidoscope_cookery:apple_platter | 16 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:bamboo_tube_rice | 50 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:baozi | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:barley_tea | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:barley_tea_bag | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:beef_meatball_soup | 61 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:beef_noodle | 26 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:berry_platter | 49 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:biluochun | 224 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:biluochun_tea_bag | 224 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:blaze_lamb_chop | 26 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:borscht | 36 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:braised_beef | 36 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:braised_beef_rice_bowl | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:braised_beef_with_potatoes | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:braised_pork_ribs | 42 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:brown_mushroom_pot_soup | 70 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:buddha_jumps_over_the_wall | 80 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:butter_tea | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:butter_tea_bag | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:candied_potato | 34 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:caterpillar | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:chicken_and_mushroom_stew | 32 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:chili_ristra | 170 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:chili_seed | 8 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:chorus_fried_egg | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:chorus_fruit_platter | 108 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:clay_pot_milk_tea | 164 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cold_cut_ham_slices | 605 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:cold_roasted_meat | 50 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:cold_style_sashimi | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:cooked_cow_offal | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cooked_cut_small_meats | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cooked_lamb_chops | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cooked_meatball | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cooked_pork_belly | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:cooked_rice | 28 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:crimson_fungus_pot_soup | 70 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:crystal_lamb_chop | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:dark_cuisine | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:desert_style_sashimi | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:dongpo_pork | 42 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:donkey_burger | 60 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:dough_drop_soup | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:dried_tea_leaves | 20 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_cookery:dumpling | 41 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:egg | 12 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:egg_fried_rice | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:empty_cup | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:end_style_sashimi | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:farmer_boots | 90 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_cookery:farmer_leggings | 100 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_cookery:fearsome_thick_soup | 80 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fish_flavored_shredded_pork | 76 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fish_flavored_shredded_pork_rice_bowl | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:flour | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:flower_tea | 64 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fondant_pie | 131 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fondant_spider_eye | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:four_joy_meatball_soup | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fresh_tea_leaves | 14 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fried_caterpillar | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fried_egg | 4 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:fried_spring_roll | 66 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:frogspawn_jelly | 30 | não | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:frost_lamb_chop | 26 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:golden_salad | 200 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:green_chili | 32 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:honey | 30 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:hot_dry_noodles | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:hui_noodle | 26 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:laba_congee | 11 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:lamb_and_radish_soup | 39 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:lettuce | 24 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:lettuce_seed | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:mantou | 28 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:meat_pie | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:mystery_tea | 30 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_cookery:nether_style_sashimi | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:numbing_spicy_chicken | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:oil | 25 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:oil_splashed_fish | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:oolong | 164 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:oolong_tea_bag | 164 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:pan_seared_knight_steak | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:pork_bone_soup | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:pufferfish_soup | 36 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:qingtuan | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_bamboo_tube_rice | 50 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_cow_offal | 18 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_cut_small_meats | 16 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_dough | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_lamb_chops | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_meatball | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_noodles | 19 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:raw_pork_belly | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:raw_zongzi | 15 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:red_chili | 32 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:red_mushroom_pot_soup | 70 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:rice | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:rice_panicle | 16 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sakura_fubuki | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sakura_fubuki_tea_bag | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:samsa | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sashimi | 60 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:scramble_egg_with_tomatoes | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:scramble_egg_with_tomatoes_rice_bowl | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:seafood_miso_soup | 40 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:shengjian_mantou | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sickle | 60 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:slime_ball_meal | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:spicy_blood_stew | 62 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:spicy_chicken | 28 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:spicy_rabbit_head | 84 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:stargazy_pie | 141 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:steamer | 90 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sticky_candy | 18 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sticky_rice_cake | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:stir_fried_pork_with_peppers | 52 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:stir_fried_pork_with_peppers_rice_bowl | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:stove | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:straw_hat | 50 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_cookery:straw_hat_flower | 60 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_cookery:strung_mushrooms | 24 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:stuffed_dough_food | 41 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:stuffed_tiger_skin_pepper | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:suspicious_stir_fry | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:sweet_and_sour_ender_pearls | 40 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sweet_and_sour_pork | 42 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:sweet_and_sour_pork_rice_bowl | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tea_banner | 70 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tea_egg | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tea_seed | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_cookery:teapot | 130 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tieguanyin | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tieguanyin_tea_bag | 170 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tomato | 12 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_cookery:tomato_platter | 86 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:tomato_seed | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:tundra_style_sashimi | 80 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_cookery:udon_noodle | 34 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:warped_fungus_pot_soup | 70 | sim | globalRegistryExternalItems.js, globalRegistryFoodPrices.js |
| kaleidoscope_cookery:watermelon_platter | 24 | sim | globalRegistryExternalItems.js |
| kaleidoscope_cookery:wild_mushroom_rabbit_soup | 88 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:wild_rice | 16 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_cookery:zongzi | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_tavern:allium_garden | 12 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:barrel | 90 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:bloody_mary | 12 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:brandy | 8 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_tavern:brass_heart | 12 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:carignan | 4 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:champagne | 10 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:depth_charge | 26 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:emerald | 60 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:glowflower_brew | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:godfather | 12 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:gold_grape | 24 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:grape | 20 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:grasshopper | 52 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:green_grape | 20 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:honey_wine | 4 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_tavern:ice_grape | 24 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:ice_wine | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:luminous_bride | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:madame_shexiang | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:miners_star | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:mojito | 44 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:molotov | 30 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:mother_snow | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:mystery_cocktail | 40 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_tavern:nether_special | 34 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:plum_wine | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:polaris_sweet_white | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:red_queen | 8 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:riesling_dry_white | 20 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:rum | 12 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:sakura_wine | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_tavern:sauvignon_blanc_dry_white | 22 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:screwdriver | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:sculk_special | 24 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:sherry | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:signature_cocktail | 300 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_tavern:sunset_glow | 10 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:sweet_berry_wine | 4 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| kaleidoscope_tavern:vinegar | 30 | sim | globalRegistryExtraPrices.js |
| kaleidoscope_tavern:vodka | 24 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| kaleidoscope_tavern:water_bottle | 20 | sim | globalRegistryFoodPrices.js |
| kaleidoscope_tavern:watermelon_juice | 66 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| kaleidoscope_tavern:whiskey | 46 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:white_lady | 42 | sim | globalRegistryAddonFoods.js |
| kaleidoscope_tavern:wine | 30 | sim | globalRegistryAddonFoods.js |
| large_meals:chicken_curry | 152 | sim | globalRegistryAddonFoods.js |
| large_meals:cod_deluxe | 80 | sim | globalRegistryAddonFoods.js |
| large_meals:cooked_mutton_rack | 40 | sim | globalRegistryAddonFoods.js |
| large_meals:hearty_lunch | 103 | sim | globalRegistryAddonFoods.js |
| large_meals:mushroom_pot_pie | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| large_meals:mushroom_pot_pie_block | 200 | sim | globalRegistryExternalItems.js |
| large_meals:omurice | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| large_meals:omurice_block | 114 | sim | globalRegistryExternalItems.js |
| large_meals:pasta_with_mushroom_sauce | 76 | sim | globalRegistryAddonFoods.js |
| large_meals:potato_soup | 88 | sim | globalRegistryAddonFoods.js |
| large_meals:pufferfish_broth | 104 | sim | globalRegistryAddonFoods.js |
| large_meals:raw_mutton_rack | 40 | sim | globalRegistryAddonFoods.js |
| large_meals:red_soup | 64 | sim | globalRegistryAddonFoods.js |
| large_meals:rice_pudding | 50 | sim | globalRegistryAddonFoods.js |
| large_meals:roasted_mutton_rack | 30 | sim | globalRegistryAddonFoods.js |
| large_meals:roasted_mutton_rack_block | 120 | sim | globalRegistryExternalItems.js |
| large_meals:sweet_berry_custard | 38 | sim | globalRegistryAddonFoods.js |
| large_meals:tomato_egg_soup | 44 | sim | globalRegistryAddonFoods.js |
| legendarysurvivaloverhaul:apple_juice | 45 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:beetroot_juice | 115 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:cactus_juice | 60 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:carrot_juice | 110 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:chorus_fruit_juice | 75 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:glistering_melon_juice | 150 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:glow_berries_juice | 105 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:golden_apple_juice | 495 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:golden_carrot_juice | 580 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:melon_juice | 54 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:pumpkin_juice | 345 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:sweet_berries_juice | 33 | sim | globalRegistryExtraPrices.js |
| legendarysurvivaloverhaul:tonic | 70 | sim | globalRegistryFoodPrices.js |
| longwings:apple_butterfly_brew_bottle | 180 | sim | globalRegistryExtraPrices.js |
| longwings:apple_butterfly_brew_bowl | 90 | sim | globalRegistryDrinkPrices.js |
| longwings:berry_butterfly_brew_bottle | 180 | sim | globalRegistryExtraPrices.js |
| longwings:berry_butterfly_brew_bowl | 90 | sim | globalRegistryDrinkPrices.js |
| longwings:melon_butterfly_brew_bottle | 200 | sim | globalRegistryExtraPrices.js |
| longwings:melon_butterfly_brew_bowl | 100 | sim | globalRegistryDrinkPrices.js |
| meadow:alpine_salt | 15 | sim | globalRegistryFoodPrices.js |
| meadow:amethyst_cheese_slice | 160 | sim | globalRegistry.js |
| meadow:amethyst_cheese_wheel | 640 | sim | globalRegistry.js |
| meadow:buffalo_cheese_slice | 96 | sim | globalRegistry.js |
| meadow:buffalo_cheese_wheel | 384 | sim | globalRegistry.js |
| meadow:cheese_roll | 14 | sim | globalRegistry.js |
| meadow:cheese_sandwich | 13 | sim | globalRegistry.js |
| meadow:cheese_slice | 24 | sim | globalRegistry.js |
| meadow:cheese_stick | 40 | sim | globalRegistry.js |
| meadow:cheese_tart | 49 | sim | globalRegistry.js |
| meadow:cheese_tart_slice | 12 | sim | globalRegistry.js |
| meadow:cheese_wheel | 96 | sim | globalRegistry.js |
| meadow:cheesecake | 35 | sim | globalRegistry.js |
| meadow:cheesecake_slice | 8 | sim | globalRegistry.js |
| meadow:cooked_buffalo_meat | 32 | sim | globalRegistry.js |
| meadow:fur_boots | 180 | sim | globalRegistryExtraPrices.js |
| meadow:fur_chestplate | 250 | sim | globalRegistryExtraPrices.js |
| meadow:fur_helmet | 160 | sim | globalRegistryExtraPrices.js |
| meadow:fur_leggings | 220 | sim | globalRegistryExtraPrices.js |
| meadow:goat_cheese_slice | 144 | sim | globalRegistry.js |
| meadow:goat_cheese_wheel | 576 | sim | globalRegistry.js |
| meadow:grain_cheese_slice | 33 | sim | globalRegistry.js |
| meadow:grain_cheese_wheel | 132 | sim | globalRegistry.js |
| meadow:pine_log | 3 | sim | globalRegistry.js |
| meadow:raw_buffalo_meat | 32 | sim | globalRegistry.js |
| meadow:roasted_buffalo_ham | 108 | sim | globalRegistry.js |
| meadow:sausage_with_cheese | 168 | sim | globalRegistry.js |
| meadow:sheep_cheese_slice | 12 | sim | globalRegistry.js |
| meadow:sheep_cheese_wheel | 48 | sim | globalRegistry.js |
| meadow:slice_of_amethyst_cheese | 150 | não | globalRegistryFoodPrices.js |
| meadow:slice_of_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:slice_of_goat_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:slice_of_grain_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:slice_of_herb_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:slice_of_sheep_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:stripped_pine_log | 3 | sim | globalRegistry.js |
| meadow:warped_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:warped_cheese_slice | 144 | sim | globalRegistry.js, globalRegistryFoodPrices.js |
| meadow:warped_cheese_wheel | 576 | sim | globalRegistry.js |
| meadow:wheel_of_amethyst_cheese | 150 | não | globalRegistryFoodPrices.js |
| meadow:wheel_of_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:wheel_of_goat_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:wheel_of_grain_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:wheel_of_herb_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:wheel_of_sheep_cheese | 60 | não | globalRegistryFoodPrices.js |
| meadow:wooden_amethyst_milk_bucket | 100 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_buffalo_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_goat_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_grain_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_sheep_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| meadow:wooden_warped_milk_bucket | 40 | sim | globalRegistryFoodPrices.js |
| minecraft:acacia_log | 3 | sim | globalRegistry.js |
| minecraft:amethyst_block | 32 | sim | globalRegistry.js |
| minecraft:amethyst_shard | 8 | sim | globalRegistry.js |
| minecraft:angler_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:apple | 8 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:archer_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:arms_up_pottery_sherd | 128 | sim | globalRegistry.js |
| minecraft:baked_potato | 24 | sim | globalRegistry.js |
| minecraft:bamboo_block | 9 | sim | globalRegistry.js |
| minecraft:beef | 16 | sim | globalRegistry.js |
| minecraft:beetroot | 24 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:beetroot_soup | 72 | sim | globalRegistry.js |
| minecraft:birch_log | 2 | sim | globalRegistry.js |
| minecraft:blade_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:blue_egg | 4 | sim | globalRegistry.js |
| minecraft:bread | 16 | sim | globalRegistry.js |
| minecraft:brewer_pottery_sherd | 128 | sim | globalRegistry.js |
| minecraft:brown_egg | 4 | sim | globalRegistry.js |
| minecraft:brown_mushroom | 8 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:burn_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:cactus | 12 | sim | globalRegistry.js |
| minecraft:cake | 318 | sim | globalRegistry.js |
| minecraft:carrot | 23 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:cherry_log | 4 | sim | globalRegistry.js |
| minecraft:chicken | 8 | sim | globalRegistry.js |
| minecraft:chorus_fruit | 16 | sim | globalRegistry.js |
| minecraft:coal | 8 | sim | globalRegistry.js |
| minecraft:coal_block | 72 | sim | globalRegistry.js |
| minecraft:cocoa_beans | 4 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:cod | 16 | sim | globalRegistry.js |
| minecraft:cooked_beef | 16 | sim | globalRegistry.js |
| minecraft:cooked_chicken | 8 | sim | globalRegistry.js |
| minecraft:cooked_cod | 16 | sim | globalRegistry.js |
| minecraft:cooked_mutton | 16 | sim | globalRegistry.js |
| minecraft:cooked_porkchop | 32 | sim | globalRegistry.js |
| minecraft:cooked_rabbit | 64 | sim | globalRegistry.js |
| minecraft:cooked_salmon | 24 | sim | globalRegistry.js |
| minecraft:cookie | 12 | sim | globalRegistry.js |
| minecraft:copper_block | 45 | sim | globalRegistryCreateMetals.js |
| minecraft:copper_ingot | 5 | sim | globalRegistryCreateMetals.js |
| minecraft:crimson_fungus | 16 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:crimson_stem | 16 | sim | globalRegistry.js |
| minecraft:danger_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:dark_oak_log | 2 | sim | globalRegistry.js |
| minecraft:diamond | 256 | sim | globalRegistry.js |
| minecraft:diamond_block | 2304 | sim | globalRegistry.js |
| minecraft:dragon_breath | 4 | sim | globalRegistry.js |
| minecraft:dragon_egg | 3072 | sim | globalRegistry.js |
| minecraft:dragon_head | 4608 | sim | globalRegistry.js |
| minecraft:dried_kelp | 15 | sim | globalRegistryFoodPrices.js |
| minecraft:echo_shard | 192 | sim | globalRegistry.js |
| minecraft:egg | 4 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:emerald | 32 | sim | globalRegistry.js |
| minecraft:emerald_block | 288 | sim | globalRegistry.js |
| minecraft:enchanted_golden_apple | 4096 | sim | globalRegistry.js |
| minecraft:experience_bottle | 8 | sim | globalRegistry.js |
| minecraft:explorer_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:feather | 16 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:flow_pottery_sherd | 160 | sim | globalRegistry.js |
| minecraft:friend_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:glow_berries | 24 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:goat_horn | 512 | sim | globalRegistry.js |
| minecraft:gold_block | 198 | sim | globalRegistryCreateMetals.js |
| minecraft:gold_ingot | 22 | sim | globalRegistryCreateMetals.js |
| minecraft:gold_nugget | 2 | sim | globalRegistryCreateMetals.js |
| minecraft:golden_apple | 128 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:golden_carrot | 150 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:guster_pottery_sherd | 160 | sim | globalRegistry.js |
| minecraft:hay_block | 414 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:heart_of_the_sea | 256 | sim | globalRegistry.js |
| minecraft:heart_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:heartbreak_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:heavy_core | 6144 | sim | globalRegistry.js |
| minecraft:honey_block | 24 | sim | globalRegistry.js |
| minecraft:honey_bottle | 8 | sim | globalRegistry.js |
| minecraft:honeycomb | 4 | sim | globalRegistry.js |
| minecraft:honeycomb_block | 16 | sim | globalRegistry.js |
| minecraft:howl_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:iron_block | 99 | sim | globalRegistryCreateMetals.js |
| minecraft:iron_ingot | 11 | sim | globalRegistryCreateMetals.js |
| minecraft:iron_nugget | 1 | sim | globalRegistryCreateMetals.js |
| minecraft:jungle_log | 2 | sim | globalRegistry.js |
| minecraft:lapis_block | 64 | sim | globalRegistry.js |
| minecraft:lapis_lazuli | 6 | sim | globalRegistry.js |
| minecraft:leather | 8 | sim | globalRegistry.js |
| minecraft:mangrove_log | 4 | sim | globalRegistry.js |
| minecraft:melon | 81 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:melon_slice | 9 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:miner_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:mourner_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:mushroom_stew | 16 | sim | globalRegistry.js |
| minecraft:mutton | 16 | sim | globalRegistry.js |
| minecraft:nautilus_shell | 64 | sim | globalRegistry.js |
| minecraft:nether_star | 2048 | sim | globalRegistry.js |
| minecraft:nether_wart | 6 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:netherite_scrap | 1024 | sim | globalRegistry.js |
| minecraft:oak_log | 2 | sim | globalRegistry.js |
| minecraft:ominous_bottle | 64 | sim | globalRegistry.js |
| minecraft:ominous_trial_key | 224 | sim | globalRegistry.js |
| minecraft:pale_oak_log | 8 | sim | globalRegistry.js |
| minecraft:pitcher_plant | 64 | sim | globalRegistry.js |
| minecraft:plenty_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:poisonous_potato | 4 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:popped_chorus_fruit | 16 | sim | globalRegistry.js |
| minecraft:porkchop | 32 | sim | globalRegistry.js |
| minecraft:potato | 24 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:prismarine_crystals | 20 | sim | globalRegistry.js |
| minecraft:prize_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:pufferfish | 16 | sim | globalRegistry.js |
| minecraft:pumpkin | 80 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:pumpkin_pie | 87 | sim | globalRegistry.js |
| minecraft:quartz | 8 | sim | globalRegistry.js |
| minecraft:quartz_block | 32 | sim | globalRegistry.js |
| minecraft:rabbit | 64 | sim | globalRegistry.js |
| minecraft:rabbit_foot | 1024 | sim | globalRegistry.js |
| minecraft:rabbit_hide | 12 | sim | globalRegistry.js |
| minecraft:rabbit_stew | 239 | sim | globalRegistry.js |
| minecraft:raw_copper | 4 | sim | globalRegistry.js |
| minecraft:raw_copper_block | 36 | sim | globalRegistry.js |
| minecraft:raw_gold | 16 | sim | globalRegistry.js |
| minecraft:raw_gold_block | 144 | sim | globalRegistry.js |
| minecraft:raw_iron | 8 | sim | globalRegistry.js |
| minecraft:raw_iron_block | 72 | sim | globalRegistry.js |
| minecraft:red_mushroom | 8 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:redstone | 8 | sim | globalRegistry.js |
| minecraft:redstone_block | 72 | sim | globalRegistry.js |
| minecraft:saddle | 288 | sim | globalRegistry.js |
| minecraft:salmon | 24 | sim | globalRegistry.js |
| minecraft:scrape_pottery_sherd | 160 | sim | globalRegistry.js |
| minecraft:sheaf_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:shelter_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:skull_pottery_sherd | 80 | sim | globalRegistry.js |
| minecraft:sniffer_egg | 192 | sim | globalRegistry.js |
| minecraft:snort_pottery_sherd | 192 | sim | globalRegistry.js |
| minecraft:spruce_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_acacia_log | 3 | sim | globalRegistry.js |
| minecraft:stripped_birch_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_cherry_log | 4 | sim | globalRegistry.js |
| minecraft:stripped_crimson_stem | 16 | sim | globalRegistry.js |
| minecraft:stripped_dark_oak_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_jungle_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_mangrove_log | 4 | sim | globalRegistry.js |
| minecraft:stripped_oak_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_pale_oak_log | 8 | sim | globalRegistry.js |
| minecraft:stripped_spruce_log | 2 | sim | globalRegistry.js |
| minecraft:stripped_warped_stem | 16 | sim | globalRegistry.js |
| minecraft:sugar_cane | 12 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:sweet_berries | 4 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:torchflower | 128 | sim | globalRegistry.js |
| minecraft:totem_of_undying | 448 | sim | globalRegistry.js |
| minecraft:trial_key | 112 | sim | globalRegistry.js |
| minecraft:tropical_fish | 72 | sim | globalRegistry.js |
| minecraft:turtle_egg | 64 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:warped_fungus | 16 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| minecraft:warped_stem | 16 | sim | globalRegistry.js |
| minecraft:wheat | 46 | sim | globalPriceBalance.js, globalRegistry.js |
| minecraft:wither_rose | 128 | sim | globalRegistry.js |
| minersdelight:arthropod | 14 | sim | globalRegistryAddonFoods.js |
| minersdelight:baked_cave_carrot | 1 | sim | globalRegistryAddonFoods.js |
| minersdelight:baked_cod_stew_cup | 166 | sim | globalRegistryExtraPrices.js |
| minersdelight:baked_spider_leg | 28 | sim | globalRegistryAddonFoods.js |
| minersdelight:baked_squid | 28 | sim | globalRegistryAddonFoods.js |
| minersdelight:baked_tentacles | 28 | sim | globalRegistryAddonFoods.js |
| minersdelight:bat_cookie | 8 | sim | globalRegistryAddonFoods.js |
| minersdelight:bat_rolls | 21 | sim | globalRegistryAddonFoods.js |
| minersdelight:bat_soup | 40 | sim | globalRegistryAddonFoods.js |
| minersdelight:bat_soup_cup | 35 | sim | globalRegistryExtraPrices.js |
| minersdelight:bat_wing | 10 | sim | globalRegistryAddonFoods.js |
| minersdelight:beef_stew_cup | 42 | sim | globalRegistryExtraPrices.js |
| minersdelight:beetroot_soup_cup | 47 | sim | globalRegistryExtraPrices.js |
| minersdelight:bone_broth_cup | 70 | sim | globalRegistryFoodPrices.js |
| minersdelight:bowl_of_stuffed_squid | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| minersdelight:cave_carrot | 1 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| minersdelight:cave_carrot_crate |  | sim | globalPriceBalance.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| minersdelight:cave_hamburger | 76 | sim | globalRegistryAddonFoods.js |
| minersdelight:cave_soup | 25 | sim | globalRegistryAddonFoods.js |
| minersdelight:cave_soup_cup | 45 | sim | globalRegistryExtraPrices.js |
| minersdelight:chicken_soup_cup | 78 | sim | globalRegistryExtraPrices.js |
| minersdelight:cooked_arthropod | 28 | sim | globalRegistryAddonFoods.js |
| minersdelight:copper_carrot | 161 | sim | globalRegistryAddonFoods.js |
| minersdelight:crunchy_bar | 35 | sim | globalRegistryAddonFoods.js |
| minersdelight:fake_meatloaf | 23 | sim | globalRegistryAddonFoods.js |
| minersdelight:fish_stew_cup | 100 | sim | globalRegistryExtraPrices.js |
| minersdelight:glazed_arachnid_limbs | 373 | sim | globalRegistryExternalItems.js |
| minersdelight:glow_ink_pasta | 74 | sim | globalRegistryAddonFoods.js |
| minersdelight:glow_squid | 18 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| minersdelight:golden_nutritional_bar | 220 | sim | globalRegistryAddonFoods.js |
| minersdelight:hot_cocoa_cup | 40 | não | globalRegistryFoodPrices.js |
| minersdelight:improvised_barbecue_stick | 49 | sim | globalRegistryAddonFoods.js |
| minersdelight:insect_sandwich | 40 | sim | globalRegistryAddonFoods.js |
| minersdelight:insect_stew | 55 | sim | globalRegistryAddonFoods.js |
| minersdelight:insect_stew_cup | 35 | sim | globalRegistryExtraPrices.js |
| minersdelight:insect_wrap | 75 | sim | globalRegistryAddonFoods.js |
| minersdelight:milk_cup | 40 | sim | globalRegistryExtraPrices.js |
| minersdelight:moss | 30 | sim | globalRegistryAddonFoods.js |
| minersdelight:mushroom_stew_cup | 16 | sim | globalRegistryExtraPrices.js |
| minersdelight:noodle_soup_cup | 57 | sim | globalRegistryExtraPrices.js |
| minersdelight:nutritional_bar | 60 | sim | globalRegistryAddonFoods.js |
| minersdelight:onion_soup_cup | 60 | sim | globalRegistryExtraPrices.js |
| minersdelight:pasta_with_veggieballs | 125 | sim | globalRegistryAddonFoods.js |
| minersdelight:plate_of_fake_meatloaf | 50 | sim | globalRegistryFoodPrices.js |
| minersdelight:plate_of_glazed_arachnid_limbs | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| minersdelight:pumpkin_soup_cup | 91 | sim | globalRegistryExtraPrices.js |
| minersdelight:rabbit_stew_cup | 155 | sim | globalRegistryExtraPrices.js |
| minersdelight:seasoned_arthropods | 100 | sim | globalRegistryAddonFoods.js |
| minersdelight:silverfish_eggs | 10 | sim | globalRegistryAddonFoods.js |
| minersdelight:smoked_bat_wing | 28 | sim | globalRegistryAddonFoods.js |
| minersdelight:spider_leg | 10 | sim | globalRegistryAddonFoods.js |
| minersdelight:squid | 18 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| minersdelight:squid_sandwich | 40 | sim | globalRegistryAddonFoods.js |
| minersdelight:stuffed_squid | 77 | sim | globalRegistryAddonFoods.js |
| minersdelight:takoyaki | 80 | sim | globalRegistryAddonFoods.js |
| minersdelight:tentacles | 14 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| minersdelight:tentacles_on_a_stick | 60 | sim | globalRegistryAddonFoods.js |
| minersdelight:vegan_hamburger | 100 | sim | globalRegistryAddonFoods.js |
| minersdelight:vegan_patty | 24 | sim | globalRegistryAddonFoods.js |
| minersdelight:vegan_steak_and_potatoes | 99 | sim | globalRegistryAddonFoods.js |
| minersdelight:vegan_wrap | 41 | sim | globalRegistryAddonFoods.js |
| minersdelight:vegetable_soup_cup | 94 | sim | globalRegistryExtraPrices.js |
| minersdelight:water_cup | 30 | sim | globalRegistryAddonFoods.js |
| minersdelight:weird_caviar | 70 | sim | globalRegistryAddonFoods.js |
| moreminecarts:glass_cactus | 20 | não | globalRegistry.js |
| moreminecarts:glass_spines | 16 | não | globalRegistry.js |
| mynethersdelight:crimson_fungus_colony | 96 | não | globalRegistry.js |
| mynethersdelight:warped_fungus_colony | 96 | não | globalRegistry.js |
| mysticaloaktree:wise_oak | 1024 | sim | globalRegistry.js |
| netherdepthsupgrade:baked_blazefish_stew | 1512 | não | globalRegistry.js |
| netherdepthsupgrade:baked_glowdine_stew | 1632 | não | globalRegistry.js |
| netherdepthsupgrade:baked_lava_pufferfish_stew | 1080 | não | globalRegistry.js |
| netherdepthsupgrade:baked_magmacubefish_stew | 2148 | não | globalRegistry.js |
| netherdepthsupgrade:baked_obsidianfish_stew | 1824 | não | globalRegistry.js |
| netherdepthsupgrade:baked_searing_cod_stew | 1080 | não | globalRegistry.js |
| netherdepthsupgrade:baked_soulsucker_stew | 1224 | não | globalRegistry.js |
| netherdepthsupgrade:blazefish | 408 | sim | globalRegistry.js |
| netherdepthsupgrade:blazefish_roll | 840 | não | globalRegistry.js |
| netherdepthsupgrade:bonefish | 364 | sim | globalRegistry.js |
| netherdepthsupgrade:cooked_glowdine_slice | 125 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:cooked_lava_pufferfish_slice | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:cooked_magmacubefish_slice | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:cooked_obsidianfish_slice | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:cooked_soulsucker_slice | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:eyeball | 30 | sim | globalRegistryFoodPrices.js |
| netherdepthsupgrade:eyeball_fish | 408 | sim | globalRegistry.js |
| netherdepthsupgrade:fortress_grouper | 666 | sim | globalRegistry.js |
| netherdepthsupgrade:fortress_grouper_plate | 16 | sim | globalRegistry.js |
| netherdepthsupgrade:glowdine | 448 | sim | globalRegistry.js |
| netherdepthsupgrade:glowdine_roll | 920 | não | globalRegistry.js |
| netherdepthsupgrade:grilled_blazefish | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_glowdine | 125 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_lava_pufferfish | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_magmacubefish | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_obsidianfish | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_searing_cod | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:grilled_soulsucker | 50 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:lava_pufferfish | 264 | sim | globalRegistry.js |
| netherdepthsupgrade:lava_pufferfish_roll | 552 | não | globalRegistry.js |
| netherdepthsupgrade:magmacubefish | 620 | sim | globalRegistry.js |
| netherdepthsupgrade:magmacubefish_roll | 1264 | não | globalRegistry.js |
| netherdepthsupgrade:magmacubefish_slice | 30 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:nether_rice_roll_medley_block | 7252 | sim | globalRegistry.js |
| netherdepthsupgrade:obsidianfish | 512 | sim | globalRegistry.js |
| netherdepthsupgrade:obsidianfish_roll | 1048 | não | globalRegistry.js |
| netherdepthsupgrade:searing_cod | 264 | sim | globalRegistry.js |
| netherdepthsupgrade:searing_cod_roll | 552 | não | globalRegistry.js |
| netherdepthsupgrade:searing_cod_slice | 30 | não | globalRegistryFoodPrices.js |
| netherdepthsupgrade:soul_sucker_leather | 16 | sim | globalRegistry.js |
| netherdepthsupgrade:soulsucker | 312 | sim | globalRegistry.js |
| netherdepthsupgrade:soulsucker_roll | 648 | não | globalRegistry.js |
| netherdepthsupgrade:warped_kelp | 15 | sim | globalRegistryFoodPrices.js |
| netherdepthsupgrade:warped_kelp_roll | 96 | não | globalRegistry.js |
| netherdepthsupgrade:warped_kelp_roll_slice | 32 | não | globalRegistry.js |
| netherdepthsupgrade:warped_seagrass | 80 | sim | globalRegistryFoodPrices.js |
| netherdepthsupgrade:wither_bonefish | 412 | sim | globalRegistry.js |
| nethervinery:blazewine_pinot | 2208 | não | globalRegistry.js |
| nethervinery:crimson_grape | 24 | não | globalPriceBalance.js, globalRegistry.js |
| nethervinery:crimson_grape_crate | 216 | não | globalRegistry.js |
| nethervinery:crimson_grape_seeds | 8 | não | globalRegistryFoodPrices.js |
| nethervinery:crimson_grapejuice | 100 | não | globalRegistryDrinkPrices.js |
| nethervinery:ghastly_grenache | 480 | não | globalRegistry.js |
| nethervinery:improved_lava_fizz | 800 | não | globalRegistry.js |
| nethervinery:improved_nether_fizz | 1400 | não | globalRegistry.js |
| nethervinery:lava_fizz | 720 | não | globalRegistry.js |
| nethervinery:nether_fizz | 1248 | não | globalRegistry.js |
| nethervinery:netherite_nectar | 4384 | não | globalRegistry.js |
| nethervinery:warped_grape | 24 | não | globalPriceBalance.js, globalRegistry.js |
| nethervinery:warped_grape_crate | 216 | não | globalRegistry.js |
| nethervinery:warped_grape_seeds | 8 | não | globalRegistryFoodPrices.js |
| nethervinery:warped_grapejuice | 100 | não | globalRegistryDrinkPrices.js |
| numismatics:ancient_coin | 262144 | sim | globalRegistry.js |
| numismatics:bevel | 8 | sim | globalRegistry.js |
| numismatics:cog | 64 | sim | globalRegistry.js |
| numismatics:crown | 512 | sim | globalRegistry.js |
| numismatics:neptunium_coin | 32768 | sim | globalRegistry.js |
| numismatics:prismatic_coin | 16777216 | sim | globalRegistry.js |
| numismatics:sprocket | 16 | sim | globalRegistry.js |
| numismatics:spur | 1 | sim | globalRegistry.js |
| numismatics:sun | 4096 | sim | globalRegistry.js |
| oceansdelight:baked_tentacle_on_a_stick | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:bowl_of_guardian_soup | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| oceansdelight:braised_sea_pickle | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:cabbage_wrapped_elder_guardian | 80 | sim | globalRegistryAddonFoods.js |
| oceansdelight:cooked_elder_guardian_slice | 110 | sim | globalRegistryAddonFoods.js |
| oceansdelight:cooked_guardian_tail | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:cooked_stuffed_cod | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:cut_tentacles | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:elder_guardian_roll | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:elder_guardian_slab | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:elder_guardian_slice | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:fugu_roll | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:fugu_slice | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:guardian_soup | 70 | sim | globalRegistryFoodPrices.js |
| oceansdelight:guardian_tail | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:honey_fried_kelp | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:seagrass_salad | 74 | sim | globalRegistryAddonFoods.js |
| oceansdelight:squid_rings | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:stuffed_cod | 84 | sim | globalRegistryAddonFoods.js |
| oceansdelight:tentacle_on_a_stick | 30 | sim | globalRegistryAddonFoods.js |
| oceansdelight:tentacles | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| oreganized:raw_lead | 48 | não | globalRegistry.js |
| oreganized:raw_lead_block | 432 | não | globalRegistry.js |
| oreganized:raw_silver | 64 | não | globalRegistry.js |
| oreganized:raw_silver_block | 576 | não | globalRegistry.js |
| pamhc2trees:almonditem | 8 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:appleitem | 12 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:bananaitem | 16 | sim | globalRegistry.js |
| pamhc2trees:cashewitem | 8 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:cherryitem | 12 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:cinnamonitem | 160 | sim | globalRegistry.js |
| pamhc2trees:coconutitem | 12 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:dragonfruititem | 128 | sim | globalRegistry.js |
| pamhc2trees:hazelnutitem | 32 | sim | globalRegistry.js |
| pamhc2trees:lemonitem | 160 | sim | globalRegistry.js |
| pamhc2trees:limeitem | 12 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:lycheeitem | 16 | sim | globalRegistry.js |
| pamhc2trees:mangoitem | 64 | sim | globalRegistry.js |
| pamhc2trees:orangeitem | 96 | sim | globalRegistry.js |
| pamhc2trees:pawpawitem | 80 | sim | globalRegistry.js |
| pamhc2trees:peachitem | 64 | sim | globalRegistry.js |
| pamhc2trees:pearitem | 12 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:pistachioitem | 8 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:plumitem | 96 | sim | globalRegistry.js |
| pamhc2trees:roastedalmonditem | 50 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:roastedcashewitem | 50 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:roastedhazelnutitem | 32 | sim | globalRegistry.js |
| pamhc2trees:roastedpistachioitem | 50 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:roastedwalnutitem | 50 | sim | globalRegistryFoodPrices.js |
| pamhc2trees:starfruititem | 200 | sim | globalPriceBalance.js, globalRegistry.js |
| pamhc2trees:walnutitem | 8 | sim | globalRegistryFoodPrices.js |
| paraglider:spirit_orb | 64 | sim | globalRegistry.js |
| quark:ancient_fruit | 16 | sim | globalRegistry.js, globalRegistryStorageBlockPrices.js |
| quark:ancient_log | 8 | sim | globalRegistry.js |
| quark:apple_crate |  | sim | globalRegistryStorageBlockPrices.js |
| quark:azalea_log | 4 | sim | globalRegistry.js |
| quark:beetroot_crate |  | sim | globalRegistryStorageBlockPrices.js |
| quark:berry_sack | 36 | sim | globalPriceBalance.js, globalRegistry.js |
| quark:black_corundum | 32 | sim | globalRegistry.js |
| quark:black_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:blossom_log | 2 | sim | globalRegistry.js |
| quark:blue_corundum | 32 | sim | globalRegistry.js |
| quark:blue_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:bonded_leather | 72 | sim | globalRegistry.js |
| quark:bonded_rabbit_hide | 108 | sim | globalRegistry.js |
| quark:cactus_block | 108 | sim | globalRegistry.js |
| quark:carrot_crate |  | sim | globalRegistryStorageBlockPrices.js |
| quark:chorus_fruit_block | 144 | sim | globalRegistry.js |
| quark:cocoa_beans_sack | 36 | sim | globalRegistry.js |
| quark:cooked_crab_leg | 24 | sim | globalRegistry.js |
| quark:crab_leg | 24 | sim | globalRegistry.js |
| quark:crab_shell | 40 | sim | globalRegistry.js |
| quark:diamond_heart | 752 | sim | globalRegistry.js |
| quark:dragon_scale | 330 | sim | globalRegistry.js |
| quark:forgotten_hat | 112 | sim | globalRegistry.js |
| quark:glow_shroom | 24 | sim | globalPriceBalance.js, globalRegistry.js |
| quark:glowberry_sack | 216 | sim | globalPriceBalance.js, globalRegistry.js |
| quark:golden_apple_crate |  | sim | globalRegistryStorageBlockPrices.js |
| quark:golden_carrot_crate | 1350 | sim | globalRegistry.js |
| quark:green_corundum | 32 | sim | globalRegistry.js |
| quark:green_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:indigo_corundum | 32 | sim | globalRegistry.js |
| quark:indigo_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:nether_wart_sack | 54 | sim | globalRegistry.js |
| quark:orange_corundum | 32 | sim | globalRegistry.js |
| quark:orange_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:potato_crate |  | sim | globalRegistryStorageBlockPrices.js |
| quark:red_corundum | 32 | sim | globalRegistry.js |
| quark:red_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:stripped_ancient_log | 8 | sim | globalRegistry.js |
| quark:stripped_azalea_log | 4 | sim | globalRegistry.js |
| quark:stripped_blossom_log | 2 | sim | globalRegistry.js |
| quark:sugar_cane_block | 108 | sim | globalRegistry.js |
| quark:violet_corundum | 32 | sim | globalRegistry.js |
| quark:violet_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:white_corundum | 32 | sim | globalRegistry.js |
| quark:white_corundum_cluster | 16 | sim | globalRegistry.js |
| quark:yellow_corundum | 32 | sim | globalRegistry.js |
| quark:yellow_corundum_cluster | 16 | sim | globalRegistry.js |
| quarkdelight:ancient_fruit_crate |  | não | globalRegistryStorageBlockPrices.js |
| quarkdelight:bucket_of_sweet_gelatine | 66 | não | globalRegistryAddonFoods.js |
| quarkdelight:cavern_explorer_stew | 35 | não | globalRegistryAddonFoods.js |
| quarkdelight:cloud_latte | 38 | não | globalRegistryAddonFoods.js |
| quarkdelight:cooked_whole_crab | 114 | não | globalRegistryAddonFoods.js |
| quarkdelight:crab_bars | 30 | não | globalRegistryFoodPrices.js |
| quarkdelight:crab_pasta | 35 | não | globalRegistryAddonFoods.js |
| quarkdelight:lush_moss_salad | 60 | não | globalRegistryExtraPrices.js |
| quarkdelight:miso_with_bamboo_sprouts | 70 | não | globalRegistryAddonFoods.js |
| refurbished_furniture:bread_slice | 5 | sim | globalRegistry.js |
| refurbished_furniture:cheese | 60 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:cheese_sandwich | 60 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:cheese_toastie | 15 | sim | globalRegistry.js |
| refurbished_furniture:cooked_meatlovers_pizza | 40 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:cooked_vegetable_pizza | 414 | sim | globalRegistry.js |
| refurbished_furniture:dough | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| refurbished_furniture:glow_berry_jam | 112 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:glow_berry_jam_toast | 49 | sim | globalRegistry.js |
| refurbished_furniture:meatlovers_pizza_slice | 40 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:raw_meatlovers_pizza | 100 | sim | globalRegistryExtraPrices.js |
| refurbished_furniture:raw_vegetable_pizza | 80 | sim | globalRegistryExtraPrices.js |
| refurbished_furniture:sea_salt | 15 | sim | globalRegistryFoodPrices.js |
| refurbished_furniture:sweet_berry_jam | 45 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| refurbished_furniture:sweet_berry_jam_toast | 20 | sim | globalRegistry.js |
| refurbished_furniture:toast | 5 | sim | globalRegistry.js |
| refurbished_furniture:vegetable_pizza_slice | 414 | sim | globalRegistry.js |
| refurbished_furniture:wheat_flour | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| relics:amphibian_boot | 320 | sim | globalRegistry.js |
| relics:aqua_walker | 320 | sim | globalRegistry.js |
| relics:arrow_quiver | 4096 | sim | globalRegistry.js |
| relics:bastion_ring | 1024 | sim | globalRegistry.js |
| relics:blazing_flask | 8192 | sim | globalRegistry.js |
| relics:chorus_inhibitor | 3072 | sim | globalRegistry.js |
| relics:drowned_belt | 1024 | sim | globalRegistry.js |
| relics:elytra_booster | 1536 | sim | globalRegistry.js |
| relics:enders_hand | 1536 | sim | globalRegistry.js |
| relics:holy_locket | 4096 | sim | globalRegistry.js |
| relics:hunter_belt | 288 | sim | globalRegistry.js |
| relics:ice_breaker | 320 | sim | globalRegistry.js |
| relics:ice_skates | 304 | sim | globalRegistry.js |
| relics:infinity_ham | 8192 | sim | globalRegistry.js |
| relics:jellyfish_necklace | 320 | sim | globalRegistry.js |
| relics:leather_belt | 512 | sim | globalRegistry.js |
| relics:magma_walker | 1024 | sim | globalRegistry.js |
| relics:midnight_robe | 3072 | sim | globalRegistry.js |
| relics:rage_glove | 2560 | sim | globalRegistry.js |
| relics:reflection_necklace | 320 | sim | globalRegistry.js |
| relics:relic_experience_bottle | 80 | sim | globalRegistry.js |
| relics:roller_skates | 512 | sim | globalRegistry.js |
| relics:shadow_glaive | 1024 | sim | globalRegistry.js |
| relics:space_dissector | 16384 | sim | globalRegistry.js |
| relics:spatial_sign | 304 | sim | globalRegistry.js |
| relics:spore_sack | 2560 | sim | globalRegistry.js |
| relics:wool_mitten | 304 | sim | globalRegistry.js |
| ribbits:toadstool | 20 | sim | globalRegistry.js |
| rottencreatures:treasure_chest | 4096 | sim | globalRegistry.js |
| sewingkit:wool_hat | 80 | sim | globalRegistryExtraPrices.js |
| sewingkit:wool_pants | 120 | sim | globalRegistryExtraPrices.js |
| sewingkit:wool_shirt | 130 | sim | globalRegistryExtraPrices.js |
| simplehats:acornhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:aegishat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:alien_antennae | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:alienphil | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:amalgalichhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:angel_and_devil | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:angrymask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:antlers | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:apple | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:artsy | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:artsy_doll | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:astronaut | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:axolotl_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:azumanga_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baby_crewmate | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:babydolphin | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:babyturtle | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bandana | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bandanargb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baseballeaster | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baseballhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baseballhatfestive | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baseballhatjuly | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:baseballhatrgb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:batwinghat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beanie | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beanieeaster | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beaniefestive | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beaniejuly | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beaniergb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beaniespooky | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bee_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beehat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beehatpride | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beehattrans | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beetle_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:beret_ribbon | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bicorne | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bigbrain | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bigcrown | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bigeyes | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bigribbon | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bigstevehead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:binky | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bluefireeye | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bowler | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:breadhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:brownbrick | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bucket | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:bunnyhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:burgerhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:burning_m_bison | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:caddycap | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:camera | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:camerabeard | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:candleonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:candycane | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:capbackwards | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cardboard_box | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:carrotonstick | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cartoonegg | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cat_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cat_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:caterpillar_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chalk_stick | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cheeseslice | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chefshat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chi_ears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chickenhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chickenonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:chocolate_sauced | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:christmascakehat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:christmastree | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:circular_glasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:clockface | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cowboy | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cowboyrgb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:crabonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:crown | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:crystal_horns | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cucumbereyemask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cuphead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:cyclopseye | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dairyqueen | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dangereqsue | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dangeresquejuly | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dejiko | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:demoneyes | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:demonhorns | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:digger | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dimmahat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dipper | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:discoball | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:disguise | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:doctorhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dorkglassesandteeth | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:doubletake | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dragonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dragonskull | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dragonskullender | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:drinkinhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:druid_antlers | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:druid_antlers_rare | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dumhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dwarfbeard | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:dwarfminerbeard | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:easterhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eevee_ears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eggcracked | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:egghead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eggheadspots | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eggonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:elfhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:explorerhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyeholder_beeholder | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyeholder_dark | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyeholder_evil | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyeholder_warm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyeholder_xanath | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:eyepatch | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fakeblight | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fakefire | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:farmerbrim | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:festiveantlers | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:festiveribbon | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fez | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:finnhood | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fireworks | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fishing_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fishonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:flagjuly | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:flies | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:floatinghearts | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:floatingstar | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:flowercrown | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:floweronhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:foxhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fro | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fronthorns | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:frozenhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fulldiamondhelm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fullgoldhelm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fullironhelm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:fullsteelhelm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:ghostmask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:gnome | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:gnome_clover_wig | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:gnome_clover_wig_glasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:goggles | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:grandmadisguise | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:greaser | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:greenbirb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:greenstache | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:greyfoxhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:grinchhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:halo | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:hatbag_common | 1 | sim | globalRegistry.js |
| simplehats:hatbag_easter | 1 | sim | globalRegistry.js |
| simplehats:hatbag_epic | 1 | sim | globalRegistry.js |
| simplehats:hatbag_festive | 1 | sim | globalRegistry.js |
| simplehats:hatbag_halloween | 1 | sim | globalRegistry.js |
| simplehats:hatbag_rare | 1 | sim | globalRegistry.js |
| simplehats:hatbag_summer | 1 | sim | globalRegistry.js |
| simplehats:hatbag_uncommon | 1 | sim | globalRegistry.js |
| simplehats:headbolts | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:headphonesblue | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:headphonespink | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:headphonesred | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:headphonesreggae | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:headshot | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:hockeymask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:holyhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:horsemask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:hosthat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:icedragonskull | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:jackohat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:jesterhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:julydouble | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:julysunglasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:julytophat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:kirbymouthful | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:ladybug_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:largehorns | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:lightning_eyes | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:lil_bows | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:lil_termagant | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:lilbow | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:longfoxears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:madscientist | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:magikarp | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:medusa | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:megamanhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:milady_doll | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mimic_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mimic_head_dark | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mimic_head_gold | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mindflayer | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mindflayer_alhoon | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:minerhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mistletoe | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:mohawk | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:monkeyking | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:monocle | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:moreeyes | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:murdered | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:nekoears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:nyan_doll | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:octodad | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:orange_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:palmtree | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:paperbag | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:partyhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:paypay | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:peepo | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:penguinbaby | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:penguinhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:peppino | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pighead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pika_ears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pinhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:plaguedoctor | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pog | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pohatoe | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:policebucket | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:policesiren | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:pom_moog | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:poofballhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:poofballrgb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:popehat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:potionhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:presentsstack | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:propelhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:puchiko | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:questbook | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rabbitears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rabbitonhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rabi_en_rose | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rabi_en_rose_wig | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rainboworbiters | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:raincloud | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:ranahat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:redeyes | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rednose | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:redshroomcap | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:redstache | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbbigribbon | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbbowler | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbdragonskull | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbdrinkinhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbeasterhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbfullhelm | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbpartyhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbsmallbowler | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbsunglasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbtoptophathat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rgbushanka | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:right_hand_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:right_hand_hat_cyborg | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rimglasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rock | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:round_purple_wig | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:round_purple_wig_glasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:round_red_wig | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:round_red_wig_glasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:rubbernipple | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sandcastle | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:santaclaus | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:santahat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sausage | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:scouter | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:seaweedhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:shakehat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sheep | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:shinymagikarp | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:shrekears | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:shroomcap | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sidebow | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:simsgem | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sleepeyemask | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:slime_cube_dnd | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:slime_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:smokingpipe | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:snowmanbaby | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sombrero | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sonichood | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:spadesoldier | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:special | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:spiderweb | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sport_sunglasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:springer | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sprout | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:spyzombie | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:stackofeggs | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:stinkycheeseman | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:strawberry_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:stress | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:stuck_lollipop | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:summerhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sunglasses | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:sunglassesbig | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:supersandhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:swimmer | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tanuki_leaf | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_bee | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_ken | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_panda | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_rembo | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_ryu | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:teddy_bear_scary | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:the_noise | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:the_noisier | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:thumbnail | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tick_on_head | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tinkerhat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:toast | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:toilet | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tomato_splats | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:topcathat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tophat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:toptophathat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:toy_story_alien | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:traffic_cone | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:triangleshades | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tricorne | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tvhead | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tvheadrat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:tvheadstatic | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:twilight_doll | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:udder_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:unicornhorn | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:ushanka | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:vikinghat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:vikinghatbeard | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:villagernose | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:winghat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:worm_hat | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:worms_mine | 50 | sim | globalRegistryExtraPrices.js |
| simplehats:zigzagwitchhat | 50 | sim | globalRegistryExtraPrices.js |
| snowpig:frozen_ham | 128 | sim | globalRegistry.js |
| snowpig:frozen_porkchop | 64 | sim | globalRegistry.js |
| snowyspirit:candy_cane | 4 | sim | globalRegistry.js |
| snowyspirit:eggnog | 44 | sim | globalRegistry.js |
| snowyspirit:ginger | 24 | sim | globalPriceBalance.js, globalRegistry.js |
| snowyspirit:ginger_crate | 216 | sim | globalRegistry.js |
| snowyspirit:gingerbread | 35 | sim | globalRegistryFoodPrices.js |
| snowyspirit:gingerbread_cookie | 8 | sim | globalRegistry.js |
| snowyspirit:gingerbread_cookie_0 | 35 | não | globalRegistryFoodPrices.js |
| snowyspirit:gingerbread_cookie_1 | 35 | sim | globalRegistryFoodPrices.js |
| snowyspirit:gingerbread_cookie_2 | 35 | sim | globalRegistryFoodPrices.js |
| snowyspirit:gingerbread_cookie_3 | 35 | sim | globalRegistryFoodPrices.js |
| snowyspirit:gingerbread_frosted | 35 | sim | globalRegistryFoodPrices.js |
| snuffles:frosty_fluff | 64 | sim | globalRegistry.js |
| snuffles:snuffle_fluff | 16 | sim | globalRegistry.js |
| society:aerinite | 128 | sim | globalRegistry.js |
| society:aged_amethyst_cheese_block | 1920 | não | globalRegistry.js |
| society:aged_buffalo_cheese_block | 1152 | não | globalRegistry.js |
| society:aged_century_egg |  | não | globalRegistry.js |
| society:aged_cheese_block | 288 | não | globalRegistry.js |
| society:aged_energy_drink |  | não | globalRegistry.js |
| society:aged_espresso |  | não | globalRegistry.js |
| society:aged_goat_cheese_block | 1728 | não | globalRegistry.js |
| society:aged_grain_cheese_block | 396 | não | globalRegistry.js |
| society:aged_roe | 30 | não | globalRegistryFoodPrices.js |
| society:aged_sheep_cheese_block | 144 | não | globalRegistry.js |
| society:aged_tribull_cheese_wheel | 3456 | não | globalRegistry.js |
| society:aged_warped_cheese_block | 1728 | não | globalRegistry.js |
| society:allanite | 128 | sim | globalRegistry.js |
| society:aloe_preserves | 304 | não | globalRegistry.js |
| society:amethyst_chunk | 112 | sim | globalRegistry.js |
| society:amethyst_milk | 80 | sim | globalRegistry.js |
| society:amulet_of_light | 1282 | sim | globalRegistry.js |
| society:ancient_builders_tool | 612 | sim | globalRegistry.js |
| society:ancient_cider | 3424 | sim | globalRegistry.js |
| society:ancient_cookie | 728 | sim | globalRegistry.js |
| society:ancient_fruit | 128 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| society:ancient_fruit_crate | 1152 | não | globalRegistry.js |
| society:ancient_fruit_preserves | 112 | não | globalRegistryFoodPrices.js |
| society:ancient_juice | 180 | sim | globalPriceBalance.js, globalRegistryDrinkPrices.js |
| society:ancient_roe | 75 | sim | globalRegistryFoodPrices.js |
| society:ancient_vespertine | 1824 | sim | globalRegistry.js |
| society:aquamagical_dust | 512 | sim | globalRegistry.js |
| society:aquamarine | 184 | sim | globalRegistry.js |
| society:banana_karenina | 12 | sim | globalRegistryFoodPrices.js |
| society:banana_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:baryte | 48 | sim | globalRegistry.js |
| society:basalt_shard | 176 | sim | globalRegistry.js |
| society:battery | 400 | sim | globalRegistry.js |
| society:beemonican_seal | 2560 | sim | globalRegistry.js |
| society:beer_attunecore | 106 | sim | globalRegistry.js |
| society:beer_london | 300 | sim | globalRegistry.js |
| society:beetroot_preserves | 424 | não | globalRegistry.js |
| society:bell_pepper_preserves | 544 | não | globalRegistry.js |
| society:birt_mayonnaise | 24 | não | globalRegistry.js |
| society:bixbyite | 304 | sim | globalRegistry.js |
| society:blueberry | 24 | sim | globalPriceBalance.js, globalRegistry.js |
| society:blueberry_crate | 216 | não | globalPriceBalance.js, globalRegistry.js |
| society:blueberry_icecream | 64 | sim | globalRegistry.js |
| society:bowl_of_soul | 240 | sim | globalRegistry.js |
| society:boysenberry | 16 | sim | globalPriceBalance.js, globalRegistry.js |
| society:boysenberry_crate | 144 | não | globalRegistry.js |
| society:broccoli_preserves | 1080 | não | globalRegistry.js |
| society:buffalo_milk | 64 | sim | globalRegistry.js |
| society:butterfly_amber | 64 | sim | globalRegistry.js |
| society:calcite_gem | 64 | sim | globalRegistry.js |
| society:canvas | 80 | sim | globalRegistry.js |
| society:carrot_preserves | 409 | não | globalRegistry.js |
| society:caterpillar_eggs | 132 | sim | globalRegistry.js |
| society:cauliflower_preserves | 784 | não | globalRegistry.js |
| society:celestine | 112 | sim | globalRegistry.js |
| society:chai_blend | 40 | sim | globalRegistryFoodPrices.js |
| society:chai_tea | 40 | não | globalRegistryFoodPrices.js |
| society:cherry_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:chicken_tortilla_soup | 279 | sim | globalRegistry.js |
| society:chocolate_donut | 35 | não | globalRegistryFoodPrices.js |
| society:chorus_fruit_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:cinnamon_coffee | 45 | não | globalRegistryFoodPrices.js |
| society:coconut_oil | 64 | sim | globalRegistry.js |
| society:corn_preserves | 484 | não | globalRegistry.js |
| society:cranberry | 18 | sim | globalPriceBalance.js, globalRegistry.js |
| society:cranberry_crate | 162 | não | globalRegistry.js |
| society:cruncher_mayonnaise | 1024 | não | globalRegistry.js |
| society:crystalberry | 22 | sim | globalPriceBalance.js, globalRegistry.js |
| society:crystalberry_crate | 198 | não | globalRegistry.js |
| society:death_liquid | 930 | sim | globalRegistry.js |
| society:deep_a_mochi |  | sim | globalRegistry.js |
| society:dewy_star | 2688 | sim | globalRegistry.js |
| society:dirty_chai | 5574 | sim | globalRegistry.js |
| society:dolomite | 304 | sim | globalRegistry.js |
| society:double_aged_amethyst_cheese_block | 5760 | não | globalRegistry.js |
| society:double_aged_buffalo_cheese_block | 3456 | não | globalRegistry.js |
| society:double_aged_century_egg |  | não | globalRegistry.js |
| society:double_aged_cheese_block | 864 | não | globalRegistry.js |
| society:double_aged_energy_drink |  | não | globalRegistry.js |
| society:double_aged_espresso |  | não | globalRegistry.js |
| society:double_aged_goat_cheese_block | 5184 | não | globalRegistry.js |
| society:double_aged_grain_cheese_block | 1188 | não | globalRegistry.js |
| society:double_aged_sheep_cheese_block | 432 | não | globalRegistry.js |
| society:double_aged_tribull_cheese_wheel | 10368 | não | globalRegistry.js |
| society:double_aged_warped_cheese_block | 5184 | não | globalRegistry.js |
| society:dragon_mayonnaise | 6144 | não | globalRegistry.js |
| society:dried_alphacene_mushroom | 15 | não | globalRegistryFoodPrices.js |
| society:dried_ancient_fruit | 30 | não | globalRegistryFoodPrices.js |
| society:dried_apple | 12 | não | globalRegistryFoodPrices.js |
| society:dried_banana | 12 | não | globalRegistryFoodPrices.js |
| society:dried_bracket_mushroom | 15 | não | globalRegistryFoodPrices.js |
| society:dried_brown_mushroom | 15 | não | globalRegistryFoodPrices.js |
| society:dried_cherry | 12 | não | globalRegistryFoodPrices.js |
| society:dried_chorus_fruit | 12 | não | globalRegistryFoodPrices.js |
| society:dried_foul_berries | 12 | não | globalRegistryFoodPrices.js |
| society:dried_fruit | 12 | não | globalRegistryFoodPrices.js |
| society:dried_gearo_berry | 12 | não | globalRegistryFoodPrices.js |
| society:dried_glow_berries | 30 | não | globalRegistryFoodPrices.js |
| society:dried_lemon | 12 | não | globalRegistryFoodPrices.js |
| society:dried_mana_fruit | 30 | não | globalRegistryFoodPrices.js |
| society:dried_mango | 12 | não | globalRegistryFoodPrices.js |
| society:dried_melon_slice | 12 | não | globalRegistryFoodPrices.js |
| society:dried_orange | 12 | não | globalRegistryFoodPrices.js |
| society:dried_passion_fruit | 12 | não | globalRegistryFoodPrices.js |
| society:dried_peach | 12 | não | globalRegistryFoodPrices.js |
| society:dried_plum | 12 | não | globalRegistryFoodPrices.js |
| society:dried_red_mushroom | 15 | não | globalRegistryFoodPrices.js |
| society:dried_sweet_berries | 12 | não | globalRegistryFoodPrices.js |
| society:dried_tubabacco_leaf | 87 | sim | globalRegistry.js |
| society:dried_wild_berries | 12 | não | globalRegistryFoodPrices.js |
| society:dried_yucca_fruit | 12 | não | globalRegistryFoodPrices.js |
| society:duck_mayonnaise | 16 | não | globalRegistry.js |
| society:earth_crystal | 48 | sim | globalRegistry.js |
| society:eggplant | 42 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| society:eggplant_crate | 378 | não | globalRegistry.js |
| society:eggplant_preserves | 694 | não | globalRegistry.js |
| society:ember_crystal_cluster | 176 | sim | globalRegistry.js |
| society:energy_drink | 566 | sim | globalRegistry.js |
| society:esperite | 96 | sim | globalRegistry.js |
| society:espresso | 128 | sim | globalRegistry.js |
| society:fairy_stone | 256 | sim | globalRegistry.js |
| society:fine_wool | 256 | sim | globalRegistry.js |
| society:fire_opal | 352 | sim | globalRegistry.js |
| society:fire_quartz | 96 | sim | globalRegistry.js |
| society:flamingo_egg | 256 | sim | globalRegistry.js |
| society:flamingo_mayonnaise | 600 | não | globalRegistry.js |
| society:fluorapatite | 200 | sim | globalRegistry.js |
| society:forks_of_blue | 576 | sim | globalRegistry.js |
| society:foul_berries_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:froggy_helm | 256 | sim | globalRegistry.js |
| society:frozen_geode | 32 | sim | globalRegistry.js |
| society:frozen_tear | 64 | sim | globalRegistry.js |
| society:furniture_box | 64 | sim | globalRegistry.js |
| society:galliraptor_mayonnaise | 400 | não | globalRegistry.js |
| society:garlic_preserves | 469 | não | globalRegistry.js |
| society:geminite | 120 | sim | globalRegistry.js |
| society:geode | 16 | sim | globalRegistry.js |
| society:ghost_crystal | 200 | sim | globalRegistry.js |
| society:giant_bandolier_belt | 892 | sim | globalRegistry.js |
| society:ginger_preserves | 424 | não | globalRegistry.js |
| society:glitched_vhs | 256 | sim | globalRegistry.js |
| society:gnome | 360 | sim | globalRegistry.js |
| society:goat_milk | 96 | sim | globalRegistry.js |
| society:golden_mayonnaise | 6144 | não | globalRegistry.js |
| society:good_catawba | 504 | sim | globalRegistry.js |
| society:goose_mayonnaise | 32 | não | globalRegistry.js |
| society:grain_milk | 22 | sim | globalRegistry.js |
| society:granite_slate | 256 | sim | globalRegistry.js |
| society:green_tea_honeycomb | 329 | sim | globalRegistry.js |
| society:ground_cinnamon | 80 | sim | globalRegistry.js |
| society:ground_coffee | 45 | não | globalRegistryFoodPrices.js |
| society:hazelnut_coffee | 45 | não | globalRegistryFoodPrices.js |
| society:hazelnut_mash | 544 | não | globalRegistry.js |
| society:heart_of_neptunium | 4096 | sim | globalRegistry.js |
| society:helvite | 512 | sim | globalRegistry.js |
| society:hematite | 120 | sim | globalRegistry.js |
| society:holy_symbol | 160 | sim | globalRegistry.js |
| society:jade | 512 | sim | globalRegistry.js |
| society:jagoite | 272 | sim | globalRegistry.js |
| society:jamborite | 128 | sim | globalRegistry.js |
| society:jasper | 144 | sim | globalRegistry.js |
| society:kyanite | 256 | sim | globalRegistry.js |
| society:laputa_franc |  | sim | globalRegistry.js |
| society:large_amethyst_milk | 320 | sim | globalRegistry.js |
| society:large_buffalo_milk | 256 | sim | globalRegistry.js |
| society:large_duck_egg | 48 | sim | globalRegistry.js |
| society:large_duck_mayonnaise | 96 | não | globalRegistry.js |
| society:large_egg | 32 | sim | globalRegistry.js |
| society:large_galliraptor_egg | 600 | sim | globalRegistry.js |
| society:large_galliraptor_mayonnaise | 1200 | não | globalRegistry.js |
| society:large_goat_milk | 384 | sim | globalRegistry.js |
| society:large_goose_egg | 64 | sim | globalRegistry.js |
| society:large_goose_mayonnaise | 128 | não | globalRegistry.js |
| society:large_grain_milk | 88 | sim | globalRegistry.js |
| society:large_mayonnaise | 64 | sim | globalRegistry.js |
| society:large_milk | 64 | sim | globalRegistry.js |
| society:large_sheep_milk | 32 | sim | globalRegistry.js |
| society:large_tri_bull_milk | 768 | sim | globalRegistry.js |
| society:large_turkey_egg | 96 | sim | globalRegistry.js |
| society:large_turkey_mayonnaise | 192 | não | globalRegistry.js |
| society:large_warped_milk | 384 | sim | globalRegistry.js |
| society:latte | 576 | sim | globalRegistry.js |
| society:legendary_ink | 144 | sim | globalRegistry.js |
| society:lemon_beignets |  | sim | globalRegistry.js |
| society:lemon_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:lemon_stone | 192 | sim | globalRegistry.js |
| society:lime | 12 | não | globalRegistryFoodPrices.js |
| society:limestone_pebble | 15 | sim | globalRegistry.js |
| society:living_flesh | 192 | sim | globalRegistry.js |
| society:lunarite | 200 | sim | globalRegistry.js |
| society:magic_rock_candy | 30 | sim | globalRegistryFoodPrices.js |
| society:magma_geode | 48 | sim | globalRegistry.js |
| society:malachite | 256 | sim | globalRegistry.js |
| society:mana_energy_drink | 548 | sim | globalRegistry.js |
| society:mana_fruit | 256 | sim | globalPriceBalance.js, globalRegistry.js |
| society:mana_fruit_crate | 1024 | não | globalRegistry.js |
| society:mana_fruit_juice | 320 | não | globalPriceBalance.js, globalRegistryDrinkPrices.js |
| society:mana_fruit_preserves | 112 | não | globalRegistryFoodPrices.js |
| society:mana_king |  | sim | globalRegistry.js |
| society:mango_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:maple_syrup | 192 | não | globalRegistry.js |
| society:marble | 112 | sim | globalRegistry.js |
| society:mayonnaise | 16 | sim | globalRegistry.js |
| society:melon_preserves |  | não | globalRegistry.js |
| society:merino_wool | 4096 | sim | globalRegistry.js |
| society:mexican_street_corn | 162 | sim | globalRegistry.js |
| society:milk | 16 | não | globalRegistry.js |
| society:mini_oni_eye | 704 | sim | globalRegistry.js |
| society:mocha | 512 | sim | globalRegistry.js |
| society:mossberry | 96 | sim | globalRegistry.js |
| society:mossberry_stew | 288 | sim | globalRegistry.js |
| society:moth_pollen | 128 | sim | globalRegistry.js |
| society:mudstone | 24 | sim | globalRegistry.js |
| society:mystic_syrup | 1000 | não | globalRegistry.js |
| society:nekoite | 80 | sim | globalRegistry.js |
| society:neptuna | 384 | sim | globalRegistry.js |
| society:neptunite | 400 | sim | globalRegistry.js |
| society:nether_jelly | 512 | sim | globalRegistry.js |
| society:nether_raisins | 400 | não | globalRegistry.js |
| society:nutty_basil | 624 | sim | globalRegistry.js |
| society:oak_resin | 128 | não | globalRegistry.js |
| society:ocean_jelly | 256 | sim | globalRegistry.js |
| society:ocean_stone | 224 | sim | globalRegistry.js |
| society:oil | 112 | sim | globalRegistry.js |
| society:omni_geode | 128 | sim | globalRegistry.js |
| society:onion_preserves | 244 | não | globalRegistry.js |
| society:opal | 120 | sim | globalRegistry.js |
| society:orange | 12 | não | globalRegistryFoodPrices.js |
| society:orange_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:orpiment | 80 | sim | globalRegistry.js |
| society:parrot_mayonnaise | 128 | não | globalRegistry.js |
| society:passion_fruit_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:peach_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:penguin_egg | 128 | sim | globalRegistry.js |
| society:penguin_mayonnaise | 384 | não | globalRegistry.js |
| society:perfect_cherry | 777 | sim | globalRegistry.js |
| society:petrified_mayonnaise | 512 | não | globalRegistry.js |
| society:petrified_slime | 128 | sim | globalRegistry.js |
| society:pine_tar | 128 | não | globalRegistry.js |
| society:pink_energy_drink | 218 | sim | globalRegistry.js |
| society:plum_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:potato_preserves | 424 | não | globalRegistry.js |
| society:princess_hairbrush | 3584 | sim | globalRegistry.js |
| society:prismatic_shard | 2048 | sim | globalRegistry.js |
| society:prismatic_shard_block | 18432 | não | globalRegistry.js |
| society:production_science_pack | 1024 | sim | globalRegistry.js |
| society:pumpkin_preserves | 364 | não | globalRegistry.js |
| society:pure_obsidian | 192 | sim | globalRegistry.js |
| society:pyrite | 128 | sim | globalRegistry.js |
| society:raisins | 360 | não | globalRegistry.js |
| society:red_grape_preserves | 124 | não | globalRegistry.js |
| society:red_wrench | 233 | sim | globalRegistry.js |
| society:ribbit_drum | 96 | sim | globalRegistry.js |
| society:ribbit_gadget | 192 | sim | globalRegistry.js |
| society:river_jelly | 128 | sim | globalRegistry.js |
| society:roe | 30 | não | globalRegistryFoodPrices.js |
| society:rubber | 6 | sim | globalRegistry.js |
| society:ruby | 256 | sim | globalRegistry.js |
| society:salmonberry | 20 | sim | globalPriceBalance.js, globalRegistry.js |
| society:salmonberry_crate | 180 | não | globalRegistry.js |
| society:sandstone_slate | 64 | sim | globalRegistry.js |
| society:sap | 4 | sim | globalRegistry.js |
| society:sea_biscut | 30 | sim | globalRegistryFoodPrices.js |
| society:sheep_milk | 8 | sim | globalRegistry.js |
| society:slate | 80 | sim | globalRegistry.js |
| society:sniffer_mayonnaise | 384 | não | globalRegistry.js |
| society:soapstone | 128 | sim | globalRegistry.js |
| society:source_gem | 208 | sim | globalRegistry.js |
| society:sparkling_le_roy |  | sim | globalRegistry.js |
| society:sparkpod | 100 | sim | globalPriceBalance.js, globalRegistry.js |
| society:sparkpod_crate | 900 | não | globalRegistry.js |
| society:sparkpod_juice | 160 | não | globalPriceBalance.js, globalRegistryDrinkPrices.js |
| society:sparkstone | 16 | sim | globalRegistry.js |
| society:sparkstone_block | 144 | não | globalRegistry.js |
| society:spider_silk | 320 | sim | globalRegistry.js |
| society:spinel | 1024 | sim | globalRegistry.js |
| society:springling_mayonnaise | 256 | não | globalRegistry.js |
| society:star_coquito | 6000 | sim | globalRegistry.js |
| society:star_shards | 512 | sim | globalRegistry.js |
| society:starcardi | 228 | sim | globalRegistry.js |
| society:starfruit_juice | 240 | não | globalPriceBalance.js, globalRegistryDrinkPrices.js |
| society:steamed_milk | 64 | sim | globalRegistryDrinkPrices.js |
| society:steamy_gadget | 649 | sim | globalRegistry.js |
| society:sturdy_bamboo_block | 81 | sim | globalRegistry.js |
| society:sun_candy | 30 | sim | globalRegistryFoodPrices.js |
| society:sunlit_pearl | 1920 | sim | globalRegistry.js |
| society:supreme_mayonnaise | 9999 | sim | globalRegistry.js |
| society:suspicious_milk_tea | 2356 | sim | globalRegistry.js |
| society:sweet_potato_preserves | 364 | não | globalRegistry.js |
| society:thunder_egg | 256 | sim | globalRegistry.js |
| society:tigerseye | 272 | sim | globalRegistry.js |
| society:token_of_unity | 3 | sim | globalRegistry.js |
| society:tomato_preserves | 454 | não | globalRegistry.js |
| society:topaz | 192 | sim | globalRegistry.js |
| society:toy_train | 430 | sim | globalRegistry.js |
| society:tri_bull_milk | 192 | sim | globalRegistry.js |
| society:truffle | 512 | sim | globalRegistry.js |
| society:truffle_oil | 1536 | sim | globalRegistry.js |
| society:truffle_tea | 2061 | sim | globalRegistry.js |
| society:tubabacco_leaf | 87 | sim | globalRegistry.js |
| society:tubabacco_leaf_block | 783 | sim | globalRegistry.js |
| society:tubasmoke_carton | 1773 | sim | globalRegistry.js |
| society:tubasmoke_stick | 197 | sim | globalRegistry.js |
| society:turkey_mayonnaise | 64 | não | globalRegistry.js |
| society:turnip_preserves | 784 | não | globalRegistry.js |
| society:turtle_mayonnaise | 256 | não | globalRegistry.js |
| society:violet_moon |  | sim | globalRegistry.js |
| society:warped_milk | 96 | sim | globalRegistry.js |
| society:wheel_of_adaptation | 576 | sim | globalRegistry.js |
| society:white_energy_drink | 432 | sim | globalRegistry.js |
| society:white_grape_preserves | 123 | não | globalRegistry.js |
| society:wild_berries_preserves | 45 | não | globalRegistryFoodPrices.js |
| society:wraptor_mayonnaise | 80 | não | globalRegistry.js |
| society:yucca_preserves |  | não | globalRegistry.js |
| society:zucchini_preserves | 1440 | não | globalRegistry.js |
| species:alphacene_mushroom | 32 | não | globalRegistry.js |
| species:ancient_pinecone | 32 | não | globalRegistry.js |
| species:birt_egg | 12 | não | globalRegistry.js |
| species:birtday_cake | 1572 | não | globalRegistry.js |
| species:birtday_cake_slice | 196 | não | globalRegistry.js |
| species:ichor_bottle | 256 | não | globalRegistry.js |
| species:petrified_egg | 256 | não | globalRegistry.js |
| species:springling_egg | 128 | não | globalRegistry.js |
| species:wraptor_egg | 40 | não | globalRegistry.js |
| supplementaries:antique_ink | 32 | sim | globalRegistry.js |
| supplementaries:candy | 24 | sim | globalRegistry.js |
| supplementaries:feather_block |  | sim | globalRegistryStorageBlockPrices.js |
| supplementaries:flax | 68 | sim | globalRegistry.js |
| supplementaries:flax_block | 612 | sim | globalRegistry.js |
| supplementaries:flax_seeds | 8 | sim | globalRegistryFoodPrices.js |
| supplementaries:lumisene_bottle | 24 | sim | globalRegistry.js |
| twigs:bamboo_thatch | 3 | sim | globalRegistry.js |
| twigs:bronzed_seashell | 32 | sim | globalRegistry.js |
| twigs:opaline_seashell | 16 | sim | globalRegistry.js |
| twigs:roseate_seashell | 20 | sim | globalRegistry.js |
| twigs:tangerine_seashell | 24 | sim | globalRegistry.js |
| untitledduckmod:cooked_duck | 16 | sim | globalRegistry.js |
| untitledduckmod:cooked_goose | 16 | sim | globalRegistry.js |
| untitledduckmod:duck_egg | 8 | sim | globalRegistry.js |
| untitledduckmod:duck_feather | 64 | sim | globalRegistry.js |
| untitledduckmod:goose_egg | 16 | sim | globalRegistry.js |
| untitledduckmod:goose_foot | 96 | sim | globalRegistry.js |
| untitledduckmod:raw_duck | 16 | sim | globalRegistry.js |
| untitledduckmod:raw_goose | 16 | sim | globalRegistry.js |
| unusualfishmod:cooked_aero_mono_stick | 192 | sim | globalRegistry.js |
| unusualfishmod:cooked_blizzard_tuna | 24 | sim | globalRegistryExtraPrices.js |
| unusualfishmod:cooked_lobster | 50 | sim | globalRegistryFoodPrices.js |
| unusualfishmod:cooked_mono_stick | 50 | não | globalRegistryFoodPrices.js |
| unusualfishmod:cooked_mossthorn | 24 | sim | globalRegistryExtraPrices.js |
| unusualfishmod:cooked_shockcat | 24 | sim | globalRegistryExtraPrices.js |
| unusualfishmod:cooked_unusual_fillet | 64 | sim | globalRegistry.js |
| unusualfishmod:mana_jelly | 75 | não | globalRegistryFoodPrices.js |
| unusualfishmod:odd_fishsticks | 96 | sim | globalRegistry.js |
| unusualfishmod:pickledish | 128 | sim | globalRegistry.js |
| unusualfishmod:raw_aero_mono | 128 | sim | globalRegistry.js |
| unusualfishmod:raw_aero_mono_stick | 128 | sim | globalRegistry.js |
| unusualfishmod:raw_amber_goby | 288 | sim | globalRegistry.js |
| unusualfishmod:raw_bark_angelfish | 144 | sim | globalRegistry.js |
| unusualfishmod:raw_beaked_herring | 32 | sim | globalRegistry.js |
| unusualfishmod:raw_blind_sailfin | 224 | sim | globalRegistry.js |
| unusualfishmod:raw_blizzard_tuna | 30 | sim | globalRegistryFoodPrices.js |
| unusualfishmod:raw_circus_fish | 320 | sim | globalRegistry.js |
| unusualfishmod:raw_copperflame_anthias | 320 | sim | globalRegistry.js |
| unusualfishmod:raw_demon_herring | 192 | sim | globalRegistry.js |
| unusualfishmod:raw_drooping_gourami | 176 | sim | globalRegistry.js |
| unusualfishmod:raw_duality_damselfish | 448 | sim | globalRegistry.js |
| unusualfishmod:raw_eyelash | 480 | sim | globalRegistry.js |
| unusualfishmod:raw_eyelash_fish | 30 | não | globalRegistryFoodPrices.js |
| unusualfishmod:raw_forkfish | 96 | sim | globalRegistry.js |
| unusualfishmod:raw_frosty_fin | 96 | sim | globalRegistry.js |
| unusualfishmod:raw_hatchetfish | 352 | sim | globalRegistry.js |
| unusualfishmod:raw_picklefish | 48 | sim | globalRegistry.js |
| unusualfishmod:raw_sailor_barb | 112 | sim | globalRegistry.js |
| unusualfishmod:raw_shockcat | 30 | sim | globalRegistryFoodPrices.js |
| unusualfishmod:raw_sneep_snorp | 16 | sim | globalRegistry.js |
| unusualfishmod:raw_snowflake_tail_fish | 30 | não | globalRegistryFoodPrices.js |
| unusualfishmod:raw_spindlefish | 368 | sim | globalRegistry.js |
| unusualfishmod:raw_triple_twirl_pleco | 208 | sim | globalRegistry.js |
| unusualfishmod:raw_unusual_fillet | 30 | não | globalRegistryFoodPrices.js |
| unusualfishmod:strange_broth | 120 | sim | globalRegistry.js |
| unusualfishmod:unusual_fillet | 30 | sim | globalRegistryFoodPrices.js |
| unusualfishmod:unusual_sandwich | 132 | sim | globalRegistry.js |
| unusualfishmod:weird_goldfish | 64 | sim | globalRegistry.js |
| veggiesdelight:baked_sweet_potato | 20 | sim | globalRegistry.js, globalRegistryExternalItems.js |
| veggiesdelight:beetroot_brownie | 66 | sim | globalRegistryExternalItems.js |
| veggiesdelight:beetroot_brownie_tray | 141 | sim | globalRegistry.js |
| veggiesdelight:bellpepper | 32 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:bellpepper_crate | 288 | sim | globalRegistry.js |
| veggiesdelight:bellpepper_seeds | 8 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:broccoli | 54 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:broccoli_crate | 486 | sim | globalRegistry.js |
| veggiesdelight:broccoli_salad | 92 | sim | globalRegistry.js |
| veggiesdelight:broccoli_seeds | 8 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:broccoli_soup | 148 | sim | globalRegistry.js |
| veggiesdelight:cacciatore | 105 | sim | globalRegistry.js |
| veggiesdelight:carrot_cake | 256 | sim | globalCanonicalItems.js, globalRegistry.js |
| veggiesdelight:carrot_cake_slice | 37 | sim | globalCanonicalItems.js, globalRegistry.js |
| veggiesdelight:carrot_juice | 42 | sim | globalRegistry.js |
| veggiesdelight:cauliflower | 48 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:cauliflower_bread | 76 | sim | globalRegistry.js |
| veggiesdelight:cauliflower_burger | 162 | não | globalRegistry.js |
| veggiesdelight:cauliflower_crate | 432 | sim | globalRegistry.js |
| veggiesdelight:cauliflower_floret | 8 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| veggiesdelight:cauliflower_kuku | 174 | sim | globalRegistry.js |
| veggiesdelight:cauliflower_seeds | 8 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:cauliflower_soup | 84 | sim | globalRegistry.js |
| veggiesdelight:cesar_salad | 168 | sim | globalRegistry.js |
| veggiesdelight:chicken_fajitas_wrap | 90 | sim | globalRegistry.js |
| veggiesdelight:coleslaw | 170 | sim | globalRegistryExternalItems.js |
| veggiesdelight:cooked_vegetarian_patty | 50 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:dandelion_and_eggs | 58 | sim | globalRegistry.js |
| veggiesdelight:dandelion_juice | 60 | sim | globalRegistryDrinkPrices.js |
| veggiesdelight:dandelion_leaf | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:fermented_garlic_honey | 156 | sim | globalRegistry.js |
| veggiesdelight:fish_and_chips | 92 | sim | globalRegistry.js |
| veggiesdelight:garlic | 27 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:garlic_baked_cod | 57 | sim | globalRegistry.js |
| veggiesdelight:garlic_bread | 32 | sim | globalRegistry.js |
| veggiesdelight:garlic_chicken_stew | 137 | sim | globalRegistry.js |
| veggiesdelight:garlic_clove | 6 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| veggiesdelight:garlic_crate | 243 | sim | globalRegistry.js |
| veggiesdelight:garlic_rice_with_cauliflower | 148 | sim | globalRegistry.js |
| veggiesdelight:garlic_stuffed_mushrooms | 100 | sim | globalRegistry.js |
| veggiesdelight:lasagna_slice | 80 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:mashed_potatoes | 112 | sim | globalCanonicalItems.js, globalRegistry.js |
| veggiesdelight:mhadjeb | 93 | sim | globalRegistry.js |
| veggiesdelight:pasta_with_broccoli | 148 | sim | globalRegistry.js |
| veggiesdelight:potato_noodle | 70 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:potato_noodles | 44 | sim | globalRegistry.js |
| veggiesdelight:raw_vegetarian_patty | 147 | sim | globalRegistryExternalItems.js |
| veggiesdelight:rice_and_vegetables | 221 | sim | globalRegistry.js |
| veggiesdelight:roasted_cauliflower_floret | 50 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:roasted_garlic_clove | 14 | sim | globalRegistry.js |
| veggiesdelight:roasted_vegetables | 240 | sim | globalRegistry.js |
| veggiesdelight:roasted_zucchini | 72 | sim | globalRegistry.js |
| veggiesdelight:shakshouka | 165 | sim | globalRegistry.js |
| veggiesdelight:smoked_bellpepper | 32 | sim | globalRegistry.js |
| veggiesdelight:steak_and_broccoli | 165 | sim | globalRegistry.js |
| veggiesdelight:stuffed_bellpepper |  | sim | globalRegistry.js |
| veggiesdelight:stuffed_bellpeppers_block | 146 | sim | globalRegistry.js |
| veggiesdelight:stuffed_zucchini_boat | 270 | sim | globalRegistry.js |
| veggiesdelight:stuffed_zucchinis | 186 | sim | globalRegistry.js |
| veggiesdelight:sweet_potato | 20 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:sweet_potato_crate | 180 | sim | globalRegistry.js |
| veggiesdelight:sweet_potato_cupcake | 26 | sim | globalRegistry.js |
| veggiesdelight:sweet_potato_dough | 20 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:sweet_potato_pancakes | 336 | sim | globalRegistry.js |
| veggiesdelight:sweet_potato_pie | 489 | sim | globalRegistry.js |
| veggiesdelight:sweet_potato_pie_slice | 122 | sim | globalRegistry.js |
| veggiesdelight:turnip | 36 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:turnip_beef_stew | 75 | sim | globalRegistry.js |
| veggiesdelight:turnip_cake | 60 | sim | globalRegistry.js |
| veggiesdelight:turnip_crate | 324 | sim | globalRegistry.js |
| veggiesdelight:turnip_mutton_skewer | 60 | sim | globalRegistry.js |
| veggiesdelight:turnip_salad | 60 | sim | globalRegistry.js |
| veggiesdelight:turnip_seeds | 8 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:turnip_water | 76 | sim | globalRegistry.js |
| veggiesdelight:uncooked_mhadjeb | 109 | sim | globalRegistryExternalItems.js |
| veggiesdelight:vegan_pizza | 40 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:vegan_pizza_slice | 40 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:vegetables_wrap | 195 | sim | globalRegistry.js |
| veggiesdelight:vegetarian_burger | 188 | sim | globalRegistry.js |
| veggiesdelight:wild_bellpeppers | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_broccoli | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_cauliflowers | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_garlic | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_sweet_potatoes | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_turnips | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:wild_zucchinis | 12 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:zucchini | 72 | sim | globalPriceBalance.js, globalRegistry.js |
| veggiesdelight:zucchini_crate | 648 | sim | globalRegistry.js |
| veggiesdelight:zucchini_quiche | 939 | sim | globalRegistry.js |
| veggiesdelight:zucchini_quiche_slice | 234 | sim | globalRegistry.js |
| veggiesdelight:zucchini_sandwich | 134 | sim | globalRegistry.js |
| veggiesdelight:zucchini_seeds | 8 | sim | globalRegistryFoodPrices.js |
| veggiesdelight:zucchini_slice | 10 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| verdantvibes:bracket_mushroom | 32 | não | globalRegistry.js |
| vinery:aegis_wine | 1056 | sim | globalRegistry.js |
| vinery:apple_bag | 72 | sim | globalRegistry.js |
| vinery:apple_cider | 2592 | sim | globalCanonicalItems.js, globalRegistry.js |
| vinery:apple_juice | 20 | sim | globalRegistryExtraPrices.js |
| vinery:apple_log | 3 | sim | globalRegistry.js |
| vinery:apple_mash | 12 | sim | globalRegistryFoodPrices.js |
| vinery:apple_wine | 384 | sim | globalRegistry.js |
| vinery:bad_omen_wine | 180 | não | globalRegistryFoodPrices.js |
| vinery:bolvar_wine | 504 | sim | globalRegistry.js |
| vinery:bottle_mojang_noir | 480 | sim | globalRegistry.js |
| vinery:chenet_wine | 1056 | sim | globalRegistry.js |
| vinery:cherry | 12 | sim | globalPriceBalance.js, globalRegistry.js |
| vinery:cherry_bag | 108 | sim | globalRegistry.js |
| vinery:cherry_wine | 432 | sim | globalRegistry.js |
| vinery:chorus_wine | 480 | sim | globalRegistry.js |
| vinery:clark_wine | 480 | sim | globalRegistry.js |
| vinery:creeper_wine | 180 | não | globalRegistryFoodPrices.js |
| vinery:creepers_crush | 336 | sim | globalRegistry.js |
| vinery:cristel_wine | 576 | sim | globalRegistry.js |
| vinery:dark_cherry_log | 3 | sim | globalRegistry.js |
| vinery:eiswein | 1824 | sim | globalRegistry.js |
| vinery:glowing_wine | 1440 | sim | globalRegistry.js |
| vinery:jellie_wine | 6048 | sim | globalRegistry.js |
| vinery:jo_special_mixture | 1632 | sim | globalRegistry.js |
| vinery:jungle_grape_seeds_red | 8 | sim | globalRegistryFoodPrices.js |
| vinery:jungle_grape_seeds_white | 8 | sim | globalRegistryFoodPrices.js |
| vinery:jungle_grapes_red | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:jungle_grapes_white | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:kelp_cider | 1260 | sim | globalRegistry.js |
| vinery:lilitu_wine | 1824 | sim | globalRegistry.js |
| vinery:magnetic_wine | 384 | sim | globalRegistry.js |
| vinery:mead | 576 | sim | globalCanonicalItems.js, globalRegistry.js |
| vinery:mellohi_wine | 4384 | sim | globalRegistry.js |
| vinery:noir_wine | 1440 | sim | globalRegistry.js |
| vinery:red_grape | 20 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js |
| vinery:red_grape_bag | 180 | sim | globalRegistry.js |
| vinery:red_grape_seeds | 8 | sim | globalRegistryFoodPrices.js |
| vinery:red_grapejuice | 80 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| vinery:red_jungle_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:red_jungle_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:red_savanna_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:red_savanna_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:red_taiga_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:red_taiga_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:red_wine | 336 | sim | globalRegistry.js |
| vinery:rotten_cherry | 1 | sim | globalRegistry.js |
| vinery:savanna_grape_seeds_red | 8 | sim | globalRegistryFoodPrices.js |
| vinery:savanna_grape_seeds_white | 8 | sim | globalRegistryFoodPrices.js |
| vinery:savanna_grapes_red | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:savanna_grapes_white | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:savanne_grape_seeds_white | 8 | não | globalRegistryFoodPrices.js |
| vinery:solaris_wine | 576 | sim | globalRegistry.js |
| vinery:stal_wine | 600 | sim | globalRegistry.js |
| vinery:strad_wine | 336 | sim | globalRegistry.js |
| vinery:straw_hat | 50 | sim | globalRegistryExtraPrices.js |
| vinery:stripped_dark_cherry_log | 3 | sim | globalRegistry.js |
| vinery:taiga_grape_seeds_red | 8 | sim | globalRegistryFoodPrices.js |
| vinery:taiga_grape_seeds_white | 8 | sim | globalRegistryFoodPrices.js |
| vinery:taiga_grapes_red | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:taiga_grapes_white | 20 | sim | globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vinery:villagers_fright | 384 | sim | globalRegistry.js |
| vinery:white_grape | 20 | sim | globalPriceBalance.js, globalRegistry.js |
| vinery:white_grape_bag | 180 | sim | globalRegistry.js |
| vinery:white_grape_seeds | 8 | sim | globalRegistryFoodPrices.js |
| vinery:white_grapejuice | 80 | sim | globalRegistryExtraPrices.js |
| vinery:white_jungle_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:white_jungle_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:white_savanna_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:white_savanna_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:white_taiga_grape_bag |  | sim | globalRegistryStorageBlockPrices.js |
| vinery:white_taiga_grapejuice | 60 | sim | globalRegistryFoodPrices.js |
| vinery:winemaker_boots | 100 | sim | globalRegistryExtraPrices.js |
| vinery:winemaker_leggings | 110 | sim | globalRegistryExtraPrices.js |
| vintagedelight:apple_sauce_bottle | 25 | sim | globalRegistryFoodPrices.js |
| vintagedelight:apple_sauce_mason_jar |  | sim | globalRegistry.js |
| vintagedelight:blue_cheese_slice | 60 | não | globalRegistryFoodPrices.js |
| vintagedelight:blue_cheese_wheel | 60 | não | globalRegistryFoodPrices.js |
| vintagedelight:century_egg | 192 | sim | globalRegistry.js |
| vintagedelight:cheese_burger | 237 | sim | globalRegistry.js |
| vintagedelight:cheese_curds | 60 | sim | globalRegistryFoodPrices.js |
| vintagedelight:cheese_pasta | 112 | sim | globalRegistry.js |
| vintagedelight:cheese_pizza_slice | 40 | sim | globalRegistryFoodPrices.js |
| vintagedelight:cheese_slice | 60 | sim | globalRegistryFoodPrices.js |
| vintagedelight:cheese_wheel | 240 | sim | globalRegistryExternalItems.js |
| vintagedelight:chocolate_nut_granola_bar | 41 | sim | globalRegistry.js |
| vintagedelight:cucumber | 72 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vintagedelight:cucumber_crate | 648 | sim | globalRegistry.js |
| vintagedelight:cucumber_noodles | 70 | sim | globalRegistryFoodPrices.js |
| vintagedelight:cucumber_salad | 324 | sim | globalRegistry.js |
| vintagedelight:cucumber_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| vintagedelight:deluxe_burger | 321 | sim | globalRegistry.js |
| vintagedelight:deluxe_granola_bar | 42 | sim | globalRegistry.js |
| vintagedelight:fruity_granola_bar | 24 | sim | globalRegistry.js |
| vintagedelight:gearo_berry | 24 | sim | globalPriceBalance.js, globalRegistry.js |
| vintagedelight:gearo_berry_bag | 216 | sim | globalRegistry.js |
| vintagedelight:gearo_berry_jam_bottle | 45 | sim | globalRegistryFoodPrices.js |
| vintagedelight:gearo_berry_mason_jar |  | sim | globalRegistry.js |
| vintagedelight:ghost_charcoal | 36 | sim | globalRegistry.js |
| vintagedelight:ghost_pepper | 36 | sim | globalPriceBalance.js, globalRegistry.js |
| vintagedelight:ghost_pepper_crate | 324 | sim | globalRegistry.js |
| vintagedelight:ghost_pepper_seeds | 8 | sim | globalRegistryFoodPrices.js |
| vintagedelight:ghostly_chili | 204 | sim | globalRegistry.js |
| vintagedelight:glow_berry_jam_bottle | 112 | sim | globalRegistryFoodPrices.js |
| vintagedelight:glow_berry_mason_jar |  | sim | globalRegistry.js |
| vintagedelight:honey_jar | 30 | sim | globalRegistryFoodPrices.js |
| vintagedelight:honey_mason_jar | 24 | sim | globalRegistry.js |
| vintagedelight:honey_roasted_peanut | 40 | sim | globalRegistry.js |
| vintagedelight:kimchi | 71 | sim | globalCanonicalItems.js, globalRegistry.js |
| vintagedelight:magic_peanut | 1000 | sim | globalRegistry.js |
| vintagedelight:magic_vine | 32 | sim | globalRegistry.js |
| vintagedelight:meat_pizza | 522 | sim | globalRegistry.js |
| vintagedelight:meat_pizza_slice | 69 | sim | globalRegistry.js |
| vintagedelight:nut_mash_bottle | 8 | sim | globalRegistryFoodPrices.js |
| vintagedelight:nut_mash_mason_jar | 424 | sim | globalRegistry.js |
| vintagedelight:oat | 20 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| vintagedelight:oat_dough | 20 | sim | globalRegistryFoodPrices.js |
| vintagedelight:oat_seeds | 8 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| vintagedelight:oatmeal_cookie | 10 | sim | globalRegistry.js |
| vintagedelight:overnight_oats | 120 | sim | globalRegistry.js |
| vintagedelight:pad_thai | 372 | sim | globalRegistry.js |
| vintagedelight:pb_j | 208 | sim | globalRegistry.js |
| vintagedelight:peanut | 24 | sim | globalCanonicalItems.js, globalPriceBalance.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vintagedelight:peanut_crate | 216 | sim | globalRegistry.js |
| vintagedelight:pepper_jam_bottle | 45 | sim | globalRegistryFoodPrices.js |
| vintagedelight:pepper_jam_mason_jar | 604 | sim | globalRegistry.js |
| vintagedelight:pickle | 72 | sim | globalCanonicalItems.js, globalRegistry.js, globalRegistryStorageBlockPrices.js |
| vintagedelight:pickle_soup | 466 | sim | globalRegistry.js |
| vintagedelight:pickled_beetroot | 26 | sim | globalCanonicalItems.js, globalRegistry.js |
| vintagedelight:pickled_egg | 16 | sim | globalRegistry.js |
| vintagedelight:pickled_onion | 14 | sim | globalCanonicalItems.js, globalRegistry.js |
| vintagedelight:pickled_pepper | 38 | sim | globalRegistry.js |
| vintagedelight:pickled_pitcher_pod | 64 | sim | globalRegistry.js |
| vintagedelight:raw_oats | 20 | sim | globalRegistryFoodPrices.js |
| vintagedelight:relish_bottle | 45 | sim | globalRegistryFoodPrices.js |
| vintagedelight:relish_mason_jar | 1440 | sim | globalRegistry.js |
| vintagedelight:roasted_peanut | 24 | sim | globalCanonicalItems.js, globalRegistry.js |
| vintagedelight:salt |  | sim | globalCanonicalItems.js |
| vintagedelight:salted_cod | 18 | sim | globalRegistry.js |
| vintagedelight:salted_salmon | 26 | sim | globalRegistry.js |
| vintagedelight:stripped_magic_vine | 32 | sim | globalRegistry.js |
| vintagedelight:stuffed_burrito | 273 | sim | globalRegistry.js |
| vintagedelight:surstromming | 48 | sim | globalRegistry.js |
| vintagedelight:sweet_berry_jam_bottle | 60 | sim | globalRegistryExtraPrices.js |
| vintagedelight:sweet_berry_mason_jar | 80 | sim | globalRegistry.js, globalRegistryExtraPrices.js |
| vintagedelight:vinegar_bottle | 30 | sim | globalRegistryFoodPrices.js |
| vintagedelight:vinegar_mason_jar | 170 | sim | globalRegistry.js |
| wildernature:bison_horn | 3300 | sim | globalRegistry.js |
| wildernature:bison_meat | 64 | sim | globalRegistry.js |
| wildernature:cassowary_meat | 90 | sim | globalRegistry.js |
| wildernature:cooked_bison_meat | 64 | sim | globalRegistry.js |
| wildernature:cooked_cassowary_meat | 90 | sim | globalRegistry.js |
| wildernature:cooked_pelican_meat | 32 | não | globalRegistry.js |
| wildernature:cooked_venison | 48 | sim | globalRegistry.js |
| wildernature:fur_cloak | 220 | sim | globalRegistryExtraPrices.js |
| wildernature:pelican_meat | 32 | não | globalRegistry.js |
| wildernature:stylin_purple_hat | 90 | sim | globalRegistryExtraPrices.js |
| wildernature:venison | 48 | sim | globalRegistry.js |
| windswept:candy_cane | 30 | sim | globalRegistryFoodPrices.js |
| windswept:candy_cane_block | 36 | sim | globalRegistry.js |
| windswept:chestnut_crate | 18 | sim | globalRegistry.js |
| windswept:chestnut_log | 3 | sim | globalRegistry.js |
| windswept:chestnut_soup | 80 | sim | globalRegistry.js |
| windswept:chestnuts | 2 | sim | globalRegistry.js |
| windswept:christmas_pudding | 160 | sim | globalRegistry.js |
| windswept:cooked_goat | 40 | sim | globalRegistry.js |
| windswept:drupes_pottery_sherd | 256 | sim | globalRegistry.js |
| windswept:elder_feather | 128 | sim | globalRegistry.js |
| windswept:feather_cloak | 150 | sim | globalRegistryExtraPrices.js |
| windswept:flake_pottery_sherd | 256 | sim | globalRegistry.js |
| windswept:frozen_branch | 200 | sim | globalRegistry.js |
| windswept:ginger_root | 15 | sim | globalRegistryFoodPrices.js |
| windswept:ginger_tea | 128 | sim | globalRegistry.js |
| windswept:gingerbread_cookie | 35 | sim | globalRegistryFoodPrices.js |
| windswept:goat | 40 | sim | globalRegistry.js |
| windswept:goat_stew | 190 | sim | globalRegistry.js |
| windswept:holly_berries | 3 | sim | globalPriceBalance.js, globalRegistry.js |
| windswept:holly_berries_on_a_stick | 12 | sim | globalRegistryFoodPrices.js |
| windswept:holly_berry_basket | 27 | sim | globalPriceBalance.js, globalRegistry.js |
| windswept:holly_log | 3 | sim | globalRegistry.js |
| windswept:hoot_pottery_sherd | 182 | sim | globalRegistry.js |
| windswept:lavender_crown | 50 | sim | globalRegistryExtraPrices.js |
| windswept:lavender_tea | 80 | sim | globalRegistry.js |
| windswept:minty_snow_cone | 27 | sim | globalRegistry.js |
| windswept:mutton_pie | 116 | sim | globalRegistry.js |
| windswept:offshoot_pottery_sherd | 256 | sim | globalRegistry.js |
| windswept:pine_log | 3 | sim | globalRegistry.js |
| windswept:pinecone_jam_bottle | 212 | sim | globalRegistry.js |
| windswept:plumage_pottery_sherd | 182 | sim | globalRegistry.js |
| windswept:roasted_chestnut_crate | 18 | sim | globalRegistry.js |
| windswept:roasted_chestnuts | 2 | sim | globalRegistry.js |
| windswept:snow_boots | 150 | sim | globalRegistryExtraPrices.js |
| windswept:spicy_snow_cone | 64 | sim | globalRegistry.js |
| windswept:stripped_chestnut_log | 3 | sim | globalRegistry.js |
| windswept:stripped_holly_log | 3 | sim | globalRegistry.js |
| windswept:stripped_pine_log | 3 | sim | globalRegistry.js |
| windswept:sweet_snow_cone | 34 | sim | globalRegistry.js |
| windswept:weathered_pine_log | 6 | sim | globalRegistry.js |
| windswept:wild_berries | 8 | sim | globalPriceBalance.js, globalRegistry.js |
| windswept:wild_berry_basket | 72 | sim | globalPriceBalance.js, globalRegistry.js |
| youkaishomecoming:affogato | 43 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:americano | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:apaki | 74 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:assorted_dango | 20 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:avgolemono | 52 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:bamboo_mizuyokan | 31 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:big_popsicle | 15 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:black_grape | 20 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:black_grape_crate |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:black_grape_juice | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:black_grape_seeds | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:black_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:black_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:black_tea_leaves | 20 | sim | globalCanonicalItems.js, globalRegistryDrinkPrices.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:blazing_red_curry | 74 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:blood_curd | 41 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:bloody_flesh | 80 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:borscht | 70 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| youkaishomecoming:bowl_of_cream | 3 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:bowl_of_flesh_feast | 90 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:bowl_of_heart_throbbing_surprise | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:bun | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:burgundy | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:butter | 7 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:california_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:california_roll_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:camellia | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:can | 12 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:candy_apple | 38 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:canned_flesh | 25 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cappuccino | 24 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:champagne | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:champagne_bottle | 180 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:chest_of_heart_throbbing_surprise | 57 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cirno_hairband | 60 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:coffee_bean_bag |  | sim | globalPriceBalance.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:coffee_beans | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:coffee_berries | 12 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:coffee_mochi | 15 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:coffee_powder | 20 | sim | globalRegistryDrinkPrices.js |
| youkaishomecoming:cold_tofu | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:con_panna | 33 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cooked_flesh | 24 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cooked_flesh_slice | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cooked_mandrake_root | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:cornflower_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:crab | 20 | sim | globalCanonicalItems.js, globalRegistryExtraPrices.js |
| youkaishomecoming:crab_meat | 50 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:crab_roe | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:cucumber | 16 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:cucumber_crate |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:cucumber_seeds | 10 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:cucumber_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:cumberland_loin | 174 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:daiginjo | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:dark_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:dark_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:dark_tea_leaves | 20 | sim | globalRegistryDrinkPrices.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:dassai | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:doughnut | 35 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:dried_fish | 80 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:dried_mandrake_flower | 20 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:egg_futomaki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:egg_futomaki_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:egg_nigiri | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:espresso | 36 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:fairy_candy | 9 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:flesh | 8 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:flesh_chocolate_mousse | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:flesh_dumplings | 21 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:flesh_feast | 60 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:flesh_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:flesh_slice | 80 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:flesh_stew | 72 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:full_moons_eve | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:genmai_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:green_coffee_bean | 20 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js |
| youkaishomecoming:green_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:green_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:green_tea_leaves | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:green_water | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:grilled_boarchop | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:grilled_boarchop_bits | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:grilled_eel_over_rice | 70 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:grilled_venison | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:grilled_venison_slice | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:hakutsuru | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:han_palace | 30 | sim | globalRegistryDrinkPrices.js |
| youkaishomecoming:higan_soup | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:higi_chocolate | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:higi_doughnut | 35 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:hokkaido_salmon_hotpot | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:honey_glazed_cucumber | 31 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:imitation_bear_paw | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:imitation_crab | 34 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kabayaki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kaguya_hime | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kappa_maki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kappa_maki_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:kappa_village | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kiku | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:kinako_dango | 20 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:koishi_hat | 90 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:koishi_mousse | 51 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:komeiji_ice_cream | 30 | não | globalRegistryFoodPrices.js |
| youkaishomecoming:lamprey_skewer | 50 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:latte | 21 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:lemon_black_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:lime | 12 | não | globalRegistryFoodPrices.js |
| youkaishomecoming:lions_head | 114 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:longevity_noodles | 61 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:lorelei_nigiri | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:macchiato | 23 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mandrake_flower | 16 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mandrake_root | 20 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mantou | 28 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:mapo_tofu | 49 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:matcha | 40 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:matcha_mochi | 40 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mayonnaise_bottle | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mead | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:milk_popsicle | 30 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:mio | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:miso_soup | 70 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:mitarashi_dango | 53 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mocha | 25 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mochi | 11 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:moon_rocket | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:mushroom_soup | 70 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:nattou | 50 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:nattou_gunkan | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:oily_bean_curd | 2 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:onigili | 16 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:oolong_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:oolong_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:oolong_tea_leaves | 1 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:orange | 12 | não | globalRegistryFoodPrices.js |
| youkaishomecoming:otoro | 50 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:otoro_nigiri | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:oyaki | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:pastitsio | 167 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:peach_tapioca | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:peach_yatsuhashi | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:pod_crate |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:pods | 8 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:poor_god_soup | 32 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:pork_rice_ball | 52 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:pot_of_borscht | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_cod_stew | 61 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_han_palace | 120 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_miso_soup | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_mushroom_soup | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_potato_soup | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_power_soup | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_seafood_miso_soup | 280 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_shirayuki | 120 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:pot_of_tofu_crab_stew | 480 | sim | globalRegistryExternalItems.js |
| youkaishomecoming:potato_soup | 70 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:power_soup | 70 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:rainbow_futomaki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:rainbow_futomaki_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:rainbow_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:rainbow_roll_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:raisin | 1 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:raw_boarchop | 16 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_boarchop_bits | 8 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_bun | 35 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:raw_flesh_feast | 90 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:raw_imitation_bear_paw | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:raw_kaguya_hime | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:raw_lamprey | 16 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_lamprey_fillet | 8 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_rice_powder_pork | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:raw_scholar_ginkgo | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:raw_tuna | 16 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_tuna_slice | 8 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_tutu_congee | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:raw_venison | 16 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:raw_venison_slice | 8 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:red_grape | 20 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:red_grape_crate |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:red_grape_juice | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:red_grape_seeds | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:red_velvet_cake_slice | 70 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:red_wine | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:red_wine_bottle | 240 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| youkaishomecoming:redbean | 8 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:redbean_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:reimu_hairband | 60 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:rice_powder_pork | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:ristretto | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:roasted_lamprey | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:roasted_lamprey_fillet | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:roe | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:roe_california_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:roe_california_roll_slice | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:rumia_hairband | 60 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:saidi_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:sake_bottle | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:sakura_honey_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:sakura_mochi | 16 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:salmon_futomaki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:salmon_futomaki_slice | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:salmon_lover_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:salmon_lover_roll_slice | 30 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:sauce_grilled_fish | 52 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:saucer | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:scarlet_devil_cake | 300 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:scarlet_mist | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:scarlet_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:scholar_ginkgo | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:seafood_miso_soup | 70 | sim | globalCanonicalItems.js, globalRegistryFoodPrices.js |
| youkaishomecoming:seagrass_gunkan | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:seared_tuna | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:seared_tuna_slice | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:sekibankiyaki | 14 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:senbei | 12 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:seven_colored_yokan | 68 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:shaved_ice_over_rice | 20 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:shinnko_maki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:shinnko_maki_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:shirayuki | 30 | sim | globalRegistryDrinkPrices.js |
| youkaishomecoming:signature_mushroom_stew | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:soy_sauce_bottle | 25 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:soybean | 8 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:soybean_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:sparrow_sake | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:steamed_crab | 10 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:steamed_egg_in_bamboo | 14 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:steamer_lid | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:steamer_pot | 70 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:steamer_rack | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:stinky_tofu | 32 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:straw_hat | 50 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:suigei | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:suwako_hat | 90 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:sweet_ormosia_mochi_mixed_boiled | 35 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tamagoyaki | 12 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tamagoyaki_slice | 50 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:tea_leaf_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:tea_leaves | 12 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:tea_mocha | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tea_seeds | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:tekka_maki | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tekka_maki_slice | 20 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:tengu_tango | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tobiko_gunkan | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tofu | 2 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tofu_burger | 33 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tofu_crab_stew | 120 | sim | globalRegistryExtraPrices.js |
| youkaishomecoming:tomato_sauce_cod | 146 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tsukimi_dango | 11 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tuna_nigiri | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tuscan_salmon | 67 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:tutu_congee | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:udumbara_cake | 40 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:udumbara_flower | 24 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:udumbara_seeds | 30 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js |
| youkaishomecoming:van_allen | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:volcano_roll | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:volcano_roll_slice | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:white_grape | 20 | sim | globalPriceBalance.js, globalRegistryAddonFoods.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:white_grape_crate |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:white_grape_juice | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:white_grape_seeds | 10 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:white_tea | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:white_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:white_tea_leaves | 1 | sim | globalRegistryAddonFoods.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |
| youkaishomecoming:white_wine | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:white_wine_bottle | 240 | sim | globalRegistryExternalItems.js, globalRegistryExtraPrices.js |
| youkaishomecoming:wild_black_grape | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_coffea | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_cucumber | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_mandrake | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_red_grape | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_redbean | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_soybean | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_udumbara | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wild_white_grape | 12 | sim | globalRegistryFoodPrices.js |
| youkaishomecoming:wind_priestesses | 30 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:yakumo_inari | 18 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:yashouma_dango | 40 | sim | globalRegistryAddonFoods.js |
| youkaishomecoming:yellow_tea | 30 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js |
| youkaishomecoming:yellow_tea_bag |  | sim | globalRegistryStorageBlockPrices.js |
| youkaishomecoming:yellow_tea_leaves | 1 | sim | globalCanonicalItems.js, globalRegistryAddonFoods.js, globalRegistryExternalItems.js, globalRegistryStorageBlockPrices.js |

## DEAD_PRICED (preço para id que não existe)

| id | sugestão | confiança | evidência |
|---|---|---|---|
| atmospheric:stripped_crustose_log | atmospheric:stripped_rosewood_log | low | fuzzy name match (0.81) |
| autumnity:pumpkin | minecraft:pumpkin | high | same path under another namespace |
| bakery:apple_pie_piece | bakery:apple_pie_slice | low | fuzzy name match (0.87) |
| bakery:chocolate | create:chocolate | high | same path under another namespace |
| bakery:glowberry_pie | bakery:glowberry_pie_slice | low | fuzzy name match (0.81) |
| beachparty:chocolate_icecream |  | none | no candidate |
| beachparty:chocolate_milkshake |  | none | no candidate |
| beachparty:coconut_drink | beachparty:coconut_open | low | fuzzy name match (0.72) |
| beachparty:coconut_icecream | beachparty:coconut_cocktail | low | fuzzy name match (0.56) |
| beachparty:coconut_milkshake | beachparty:coconut_block | low | fuzzy name match (0.67) |
| beachparty:icecream_cactus |  | none | no candidate |
| beachparty:icecream_chocolate |  | none | no candidate |
| beachparty:icecream_coconut | beachparty:coconut | low | fuzzy name match (0.61) |
| beachparty:icecream_melon |  | none | no candidate |
| beachparty:icecream_sweetberries |  | none | no candidate |
| beachparty:refreshing_drink | beachparty:rubber_ring_pink | low | fuzzy name match (0.62) |
| beachparty:sweetberry_icecream | beachparty:sweetberries_cocktail | low | fuzzy name match (0.55) |
| beachparty:sweetberry_milkshake |  | none | no candidate |
| botania:shimmering_mushrooms | botania:lime_mushroom | low | fuzzy name match (0.73) |
| brewery:beer_standard |  | none | no candidate |
| brewery:whiskey_carrascon_label | brewery:whiskey_carrasconlabel | high | fuzzy name match (0.98) |
| brewery:whiskey_cristel_walker | brewery:whiskey_cristelwalker | high | fuzzy name match (0.98) |
| brewery:whiskey_jo_jannik | brewery:whiskey_jojannik | high | fuzzy name match (0.97) |
| brewery:whiskey_lilitu_single_malt | brewery:whiskey_lilitusinglemalt | high | fuzzy name match (0.96) |
| brewery:whiskey_smoky_reverie | brewery:whiskey_smokey_reverie | high | fuzzy name match (0.98) |
| candlelight:beef_with_mushroom_in_wine_and_potatoes_3 | candlelight:beef_with_mushroom_in_wine_and_potatoes_2 | high | fuzzy name match (0.98) |
| candlelight:dough | bakery:dough | low | same path under another namespace |
| candlelight:fillet_steak_3 | candlelight:fillet_steak_2 | high | fuzzy name match (0.93) |
| candlelight:khinkali |  | none | no candidate |
| candlelight:mushroom_soup_2 | candlelight:mushroom_soup_1 | high | fuzzy name match (0.93) |
| candlelight:roasted_lamb_with_lettuce_3 | candlelight:roasted_lamb_with_lettuce_2 | high | fuzzy name match (0.96) |
| candlelight:salmon_on_white_wine_3 | candlelight:salmon_on_white_wine_2 | high | fuzzy name match (0.95) |
| candlelight:tomato_sauce | farmersdelight:tomato_sauce | high | same path under another namespace |
| candlelight:tomato_soup_2 | candlelight:tomato_soup_1 | high | fuzzy name match (0.92) |
| create_central_kitchen:aloe_cake_slice |  | none | no candidate |
| create_central_kitchen:honey_cake_slice |  | none | no candidate |
| create_central_kitchen:mulberry_pie_slice |  | none | no candidate |
| create_central_kitchen:passion_fruit_cake_slice |  | none | no candidate |
| create_central_kitchen:pumpkin_cake_slice |  | none | no candidate |
| create_central_kitchen:sweet_berry_cake_slice |  | none | no candidate |
| create_central_kitchen:truffle_pie_slice |  | none | no candidate |
| create_central_kitchen:yucca_cake_slice |  | none | no candidate |
| create_enchantment_industry:hyper_experience_bottle | create_enchantment_industry:super_experience_block | low | fuzzy name match (0.76) |
| hearthandharvest:cheddar_cheese_slice | hearthandharvest:goat_cheese_slice | low | fuzzy name match (0.76) |
| hearthandharvest:cheddar_cheese_wheel | hearthandharvest:goat_cheese_wheel | low | fuzzy name match (0.76) |
| hearthandharvest:egg_crate | hearthandharvest:crate | low | fuzzy name match (0.71) |
| hearthandharvest:onion_soup | displaydelight:onion_soup | low | same path under another namespace |
| hearthandharvest:turtle_egg_crate | hearthandharvest:red_grape_crate | low | fuzzy name match (0.65) |
| hearthandharvest:unripe_cheddar_cheese_wheel | hearthandharvest:unripe_cheese_wheel | low | fuzzy name match (0.83) |
| kaleidoscope_cookery:frogspawn_jelly |  | none | no candidate |
| meadow:slice_of_amethyst_cheese | meadow:amethyst_cheese_wheel | low | fuzzy name match (0.67) |
| meadow:slice_of_cheese |  | none | no candidate |
| meadow:slice_of_goat_cheese |  | none | no candidate |
| meadow:slice_of_grain_cheese | meadow:grain_cheese_wheel | low | fuzzy name match (0.62) |
| meadow:slice_of_herb_cheese |  | none | no candidate |
| meadow:slice_of_sheep_cheese | meadow:sheep_cheese_wheel | low | fuzzy name match (0.62) |
| meadow:warped_cheese | meadow:warped_cheese_wheel | low | fuzzy name match (0.81) |
| meadow:wheel_of_amethyst_cheese | meadow:amethyst_cheese_wheel | low | fuzzy name match (0.67) |
| meadow:wheel_of_cheese | meadow:sheep_cheese_wheel | low | fuzzy name match (0.61) |
| meadow:wheel_of_goat_cheese |  | none | no candidate |
| meadow:wheel_of_grain_cheese | meadow:grain_cheese_wheel | low | fuzzy name match (0.62) |
| meadow:wheel_of_herb_cheese |  | none | no candidate |
| meadow:wheel_of_sheep_cheese | meadow:sheep_cheese_wheel | low | fuzzy name match (0.62) |
| minersdelight:hot_cocoa_cup |  | none | no candidate |
| moreminecarts:glass_cactus |  | none | no candidate |
| moreminecarts:glass_spines |  | none | no candidate |
| mynethersdelight:crimson_fungus_colony |  | none | no candidate |
| mynethersdelight:warped_fungus_colony |  | none | no candidate |
| netherdepthsupgrade:baked_blazefish_stew | netherdepthsupgrade:blazefish | low | fuzzy name match (0.62) |
| netherdepthsupgrade:baked_glowdine_stew |  | none | no candidate |
| netherdepthsupgrade:baked_lava_pufferfish_stew | netherdepthsupgrade:lava_pufferfish | low | fuzzy name match (0.73) |
| netherdepthsupgrade:baked_magmacubefish_stew | netherdepthsupgrade:magmacubefish | low | fuzzy name match (0.70) |
| netherdepthsupgrade:baked_obsidianfish_stew | netherdepthsupgrade:obsidianfish | low | fuzzy name match (0.69) |
| netherdepthsupgrade:baked_searing_cod_stew | netherdepthsupgrade:searing_cod | low | fuzzy name match (0.67) |
| netherdepthsupgrade:baked_soulsucker_stew | netherdepthsupgrade:soulsucker | low | fuzzy name match (0.65) |
| netherdepthsupgrade:blazefish_roll | netherdepthsupgrade:blazefish | low | fuzzy name match (0.78) |
| netherdepthsupgrade:cooked_glowdine_slice | netherdepthsupgrade:glowdine_bucket | low | fuzzy name match (0.61) |
| netherdepthsupgrade:cooked_lava_pufferfish_slice | netherdepthsupgrade:lava_pufferfish_bucket | low | fuzzy name match (0.72) |
| netherdepthsupgrade:cooked_magmacubefish_slice | netherdepthsupgrade:magmacubefish_bucket | low | fuzzy name match (0.70) |
| netherdepthsupgrade:cooked_obsidianfish_slice | netherdepthsupgrade:obsidianfish_bucket | low | fuzzy name match (0.68) |
| netherdepthsupgrade:cooked_soulsucker_slice | netherdepthsupgrade:soulsucker_bucket | low | fuzzy name match (0.65) |
| netherdepthsupgrade:glowdine_roll | netherdepthsupgrade:glowdine | low | fuzzy name match (0.76) |
| netherdepthsupgrade:grilled_blazefish | netherdepthsupgrade:blazefish | low | fuzzy name match (0.69) |
| netherdepthsupgrade:grilled_glowdine | netherdepthsupgrade:glowdine | low | fuzzy name match (0.67) |
| netherdepthsupgrade:grilled_lava_pufferfish | netherdepthsupgrade:lava_pufferfish | low | fuzzy name match (0.79) |
| netherdepthsupgrade:grilled_magmacubefish | netherdepthsupgrade:magmacubefish | low | fuzzy name match (0.76) |
| netherdepthsupgrade:grilled_obsidianfish | netherdepthsupgrade:obsidianfish | low | fuzzy name match (0.75) |
| netherdepthsupgrade:grilled_searing_cod | netherdepthsupgrade:searing_cod | low | fuzzy name match (0.73) |
| netherdepthsupgrade:grilled_soulsucker | netherdepthsupgrade:soulsucker | low | fuzzy name match (0.71) |
| netherdepthsupgrade:lava_pufferfish_roll | netherdepthsupgrade:lava_pufferfish | low | fuzzy name match (0.86) |
| netherdepthsupgrade:magmacubefish_roll | netherdepthsupgrade:magmacubefish | low | fuzzy name match (0.84) |
| netherdepthsupgrade:magmacubefish_slice | netherdepthsupgrade:magmacubefish_bucket | low | fuzzy name match (0.82) |
| netherdepthsupgrade:obsidianfish_roll | netherdepthsupgrade:obsidianfish | low | fuzzy name match (0.83) |
| netherdepthsupgrade:searing_cod_roll | netherdepthsupgrade:searing_cod | low | fuzzy name match (0.81) |
| netherdepthsupgrade:searing_cod_slice | netherdepthsupgrade:searing_cod_bucket | low | fuzzy name match (0.80) |
| netherdepthsupgrade:soulsucker_roll | netherdepthsupgrade:soulsucker | low | fuzzy name match (0.80) |
| netherdepthsupgrade:warped_kelp_roll | netherdepthsupgrade:warped_kelp | low | fuzzy name match (0.81) |
| netherdepthsupgrade:warped_kelp_roll_slice | netherdepthsupgrade:warped_kelp_block | low | fuzzy name match (0.72) |
| nethervinery:blazewine_pinot |  | none | no candidate |
| nethervinery:crimson_grape |  | none | no candidate |
| nethervinery:crimson_grape_crate |  | none | no candidate |
| nethervinery:crimson_grape_seeds |  | none | no candidate |
| nethervinery:crimson_grapejuice |  | none | no candidate |
| nethervinery:ghastly_grenache |  | none | no candidate |
| nethervinery:improved_lava_fizz |  | none | no candidate |
| nethervinery:improved_nether_fizz |  | none | no candidate |
| nethervinery:lava_fizz |  | none | no candidate |
| nethervinery:nether_fizz |  | none | no candidate |
| nethervinery:netherite_nectar |  | none | no candidate |
| nethervinery:warped_grape |  | none | no candidate |
| nethervinery:warped_grape_crate |  | none | no candidate |
| nethervinery:warped_grape_seeds |  | none | no candidate |
| nethervinery:warped_grapejuice |  | none | no candidate |
| oreganized:raw_lead |  | none | no candidate |
| oreganized:raw_lead_block |  | none | no candidate |
| oreganized:raw_silver |  | none | no candidate |
| oreganized:raw_silver_block |  | none | no candidate |
| quarkdelight:ancient_fruit_crate |  | none | no candidate |
| quarkdelight:bucket_of_sweet_gelatine |  | none | no candidate |
| quarkdelight:cavern_explorer_stew |  | none | no candidate |
| quarkdelight:cloud_latte |  | none | no candidate |
| quarkdelight:cooked_whole_crab |  | none | no candidate |
| quarkdelight:crab_bars |  | none | no candidate |
| quarkdelight:crab_pasta |  | none | no candidate |
| quarkdelight:lush_moss_salad |  | none | no candidate |
| quarkdelight:miso_with_bamboo_sprouts |  | none | no candidate |
| snowyspirit:gingerbread_cookie_0 | snowyspirit:gingerbread_cookie_3 | high | fuzzy name match (0.95) |
| society:aged_amethyst_cheese_block | society:large_amethyst_milk | low | fuzzy name match (0.67) |
| society:aged_buffalo_cheese_block | society:large_buffalo_milk | low | fuzzy name match (0.65) |
| society:aged_century_egg | society:large_turkey_egg | low | fuzzy name match (0.75) |
| society:aged_cheese_block | society:large_sheep_milk | low | fuzzy name match (0.61) |
| society:aged_energy_drink | society:energy_drink | low | fuzzy name match (0.83) |
| society:aged_espresso | society:espresso | low | fuzzy name match (0.76) |
| society:aged_goat_cheese_block |  | none | no candidate |
| society:aged_grain_cheese_block | society:large_grain_milk | low | fuzzy name match (0.62) |
| society:aged_roe | society:ancient_roe | low | fuzzy name match (0.63) |
| society:aged_sheep_cheese_block | society:large_sheep_milk | low | fuzzy name match (0.62) |
| society:aged_tribull_cheese_wheel |  | none | no candidate |
| society:aged_warped_cheese_block | society:large_warped_milk | low | fuzzy name match (0.63) |
| society:aloe_preserves | society:preserves_jar | low | fuzzy name match (0.67) |
| society:ancient_fruit_crate | society:ancient_fruit | low | fuzzy name match (0.81) |
| society:ancient_fruit_preserves | society:ancient_fruit | low | fuzzy name match (0.72) |
| society:banana_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:beetroot_preserves |  | none | no candidate |
| society:bell_pepper_preserves |  | none | no candidate |
| society:birt_mayonnaise | society:mayonnaise | low | fuzzy name match (0.80) |
| society:blueberry_crate | hearthandharvest:blueberry_crate | high | same path under another namespace |
| society:boysenberry_crate | society:boysenberry | low | fuzzy name match (0.79) |
| society:broccoli_preserves |  | none | no candidate |
| society:carrot_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:cauliflower_preserves |  | none | no candidate |
| society:chai_tea | herbalbrews:chai_tea | high | same path under another namespace |
| society:cherry_preserves | society:cheese_press | low | fuzzy name match (0.64) |
| society:chocolate_donut | bakery:chocolate_donut | high | same path under another namespace |
| society:chorus_fruit_preserves |  | none | no candidate |
| society:cinnamon_coffee | herbalbrews:cinnamon_coffee | high | same path under another namespace |
| society:corn_preserves | society:preserves_jar | low | fuzzy name match (0.67) |
| society:cranberry_crate | society:cranberry | low | fuzzy name match (0.75) |
| society:cruncher_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.74) |
| society:crystalberry_crate | society:crystalberry | low | fuzzy name match (0.80) |
| society:double_aged_amethyst_cheese_block | society:large_amethyst_milk | low | fuzzy name match (0.62) |
| society:double_aged_buffalo_cheese_block | society:large_buffalo_milk | low | fuzzy name match (0.60) |
| society:double_aged_century_egg | society:large_turkey_egg | low | fuzzy name match (0.56) |
| society:double_aged_cheese_block |  | none | no candidate |
| society:double_aged_energy_drink | society:mana_energy_drink | low | fuzzy name match (0.68) |
| society:double_aged_espresso |  | none | no candidate |
| society:double_aged_goat_cheese_block |  | none | no candidate |
| society:double_aged_grain_cheese_block |  | none | no candidate |
| society:double_aged_sheep_cheese_block |  | none | no candidate |
| society:double_aged_tribull_cheese_wheel |  | none | no candidate |
| society:double_aged_warped_cheese_block |  | none | no candidate |
| society:dragon_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.79) |
| society:dried_alphacene_mushroom |  | none | no candidate |
| society:dried_ancient_fruit | society:ancient_fruit | low | fuzzy name match (0.81) |
| society:dried_apple |  | none | no candidate |
| society:dried_banana | society:dried_tubabacco_leaf | low | fuzzy name match (0.62) |
| society:dried_bracket_mushroom |  | none | no candidate |
| society:dried_brown_mushroom |  | none | no candidate |
| society:dried_cherry | society:perfect_cherry | low | fuzzy name match (0.69) |
| society:dried_chorus_fruit |  | none | no candidate |
| society:dried_foul_berries |  | none | no candidate |
| society:dried_fruit | society:ancient_fruit | low | fuzzy name match (0.67) |
| society:dried_gearo_berry |  | none | no candidate |
| society:dried_glow_berries |  | none | no candidate |
| society:dried_lemon |  | none | no candidate |
| society:dried_mana_fruit | society:mana_fruit | low | fuzzy name match (0.77) |
| society:dried_mango |  | none | no candidate |
| society:dried_melon_slice |  | none | no candidate |
| society:dried_orange | society:iridium_ore | low | fuzzy name match (0.61) |
| society:dried_passion_fruit |  | none | no candidate |
| society:dried_peach | society:red_wrench | low | fuzzy name match (0.67) |
| society:dried_plum |  | none | no candidate |
| society:dried_red_mushroom |  | none | no candidate |
| society:dried_sweet_berries |  | none | no candidate |
| society:dried_wild_berries |  | none | no candidate |
| society:dried_yucca_fruit |  | none | no candidate |
| society:duck_mayonnaise | society:mayonnaise | low | fuzzy name match (0.80) |
| society:eggplant_crate | culturaldelights:eggplant_crate | high | same path under another namespace |
| society:eggplant_preserves | society:eggplant | low | fuzzy name match (0.62) |
| society:flamingo_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.80) |
| society:foul_berries_preserves |  | none | no candidate |
| society:galliraptor_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.63) |
| society:garlic_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:ginger_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:golden_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.79) |
| society:goose_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.81) |
| society:ground_coffee | herbalbrews:ground_coffee | high | same path under another namespace |
| society:hazelnut_coffee | herbalbrews:hazelnut_coffee | high | same path under another namespace |
| society:hazelnut_mash |  | none | no candidate |
| society:large_duck_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.86) |
| society:large_galliraptor_mayonnaise | society:large_galliraptor_egg | low | fuzzy name match (0.78) |
| society:large_goose_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.84) |
| society:large_turkey_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.82) |
| society:lemon_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:lime |  | none | no candidate |
| society:mana_fruit_crate | society:mana_fruit_crop | low | fuzzy name match (0.84) |
| society:mana_fruit_juice | society:mana_fruit_crop | low | fuzzy name match (0.77) |
| society:mana_fruit_preserves | society:mana_fruit_crop | low | fuzzy name match (0.69) |
| society:mango_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:maple_syrup |  | none | no candidate |
| society:melon_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:milk | society:milk_pail | low | fuzzy name match (0.62) |
| society:mystic_syrup |  | none | no candidate |
| society:nether_raisins |  | none | no candidate |
| society:oak_resin |  | none | no candidate |
| society:onion_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:orange | atmospheric:orange | high | same path under another namespace |
| society:orange_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:parrot_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.79) |
| society:passion_fruit_preserves |  | none | no candidate |
| society:peach_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:penguin_mayonnaise | society:mayonnaise | low | fuzzy name match (0.71) |
| society:petrified_mayonnaise | society:supreme_mayonnaise | low | fuzzy name match (0.74) |
| society:pine_tar | society:pink_matter | low | fuzzy name match (0.53) |
| society:plum_preserves | society:preserves_jar | low | fuzzy name match (0.67) |
| society:potato_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:prismatic_shard_block | society:prismatic_shard | low | fuzzy name match (0.83) |
| society:pumpkin_preserves | society:preserves_jar | low | fuzzy name match (0.60) |
| society:raisins | hearthandharvest:raisins | high | same path under another namespace |
| society:red_grape_preserves | society:red_glasses | low | fuzzy name match (0.53) |
| society:roe | youkaishomecoming:roe | high | same path under another namespace |
| society:salmonberry_crate | society:salmonberry | low | fuzzy name match (0.79) |
| society:sniffer_mayonnaise | society:supreme_mayonnaise | low | fuzzy name match (0.72) |
| society:sparkpod_crate | society:sparkpod | low | fuzzy name match (0.73) |
| society:sparkpod_juice | society:sparkpod | low | fuzzy name match (0.73) |
| society:sparkstone_block | society:sparkstone_ore | low | fuzzy name match (0.80) |
| society:springling_mayonnaise | society:supreme_mayonnaise | low | fuzzy name match (0.72) |
| society:starfruit_juice | society:ancient_juice | low | fuzzy name match (0.64) |
| society:sweet_potato_preserves | society:sweet_potato | low | fuzzy name match (0.71) |
| society:tomato_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:turkey_mayonnaise | society:supreme_mayonnaise | low | fuzzy name match (0.80) |
| society:turnip_preserves | society:preserves_jar | low | fuzzy name match (0.62) |
| society:turtle_mayonnaise | society:supreme_mayonnaise | low | fuzzy name match (0.80) |
| society:white_grape_preserves |  | none | no candidate |
| society:wild_berries_preserves |  | none | no candidate |
| society:wraptor_mayonnaise | society:large_mayonnaise | low | fuzzy name match (0.71) |
| society:yucca_preserves | society:preserves_jar | low | fuzzy name match (0.64) |
| society:zucchini_preserves |  | none | no candidate |
| species:alphacene_mushroom |  | none | no candidate |
| species:ancient_pinecone |  | none | no candidate |
| species:birt_egg |  | none | no candidate |
| species:birtday_cake |  | none | no candidate |
| species:birtday_cake_slice |  | none | no candidate |
| species:ichor_bottle |  | none | no candidate |
| species:petrified_egg |  | none | no candidate |
| species:springling_egg |  | none | no candidate |
| species:wraptor_egg |  | none | no candidate |
| unusualfishmod:cooked_mono_stick | unusualfishmod:cooked_aero_mono_stick | low | fuzzy name match (0.87) |
| unusualfishmod:mana_jelly |  | none | no candidate |
| unusualfishmod:raw_eyelash_fish | unusualfishmod:raw_eyelash | low | fuzzy name match (0.81) |
| unusualfishmod:raw_snowflake_tail_fish | unusualfishmod:raw_bark_angelfish | low | fuzzy name match (0.49) |
| unusualfishmod:raw_unusual_fillet | unusualfishmod:unusual_fillet | low | fuzzy name match (0.88) |
| veggiesdelight:cauliflower_burger | veggiesdelight:cauliflower_bread | low | fuzzy name match (0.86) |
| verdantvibes:bracket_mushroom |  | none | no candidate |
| vinery:bad_omen_wine | vinery:strad_wine | low | fuzzy name match (0.61) |
| vinery:creeper_wine | vinery:red_wine | low | fuzzy name match (0.70) |
| vinery:savanne_grape_seeds_white | vinery:savanna_grape_seeds_white | high | fuzzy name match (0.96) |
| vintagedelight:blue_cheese_slice | vintagedelight:cheese_slice | low | fuzzy name match (0.83) |
| vintagedelight:blue_cheese_wheel | vintagedelight:cheese_wheel | low | fuzzy name match (0.83) |
| wildernature:cooked_pelican_meat | wildernature:cooked_bison_meat | low | fuzzy name match (0.78) |
| wildernature:pelican_meat | wildernature:bison_meat | low | fuzzy name match (0.64) |
| youkaishomecoming:komeiji_ice_cream |  | none | no candidate |
| youkaishomecoming:lime |  | none | no candidate |
| youkaishomecoming:orange | atmospheric:orange | high | same path under another namespace |

## UNRESOLVED

Nenhum: todo MISSING tem preço (alias, receita ou fallback).

## Fallback de 5 moedas (sem receita útil nem preço 1.20.1)

| id | classe | bloqueio (insumo sem preço) |
|---|---|---|
| aquaculture:fish_bones | animal | nenhum |
| autumnity:snail_goo | animal | nenhum |
| autumnity:snail_shell_piece | animal | nenhum |
| crabbersdelight:deluxe_crab_trap_bait | machine | crabbersdelight:crab_trap_bait |
| meadow:firewood | machine | aquaculture:driftwood |
| minecraft:bamboo | animal | nenhum |
| minecraft:bone | animal | nenhum |
| minecraft:bowl | animal | nenhum |
| minecraft:glass_bottle | machine | farmersdelight:milk_bottle, vintagedelight:nut_milk_bottle |
| minecraft:glow_ink_sac | animal | nenhum |
| minecraft:ink_sac | animal | nenhum |
| minecraft:ochre_froglight | animal | nenhum |
| minecraft:pearlescent_froglight | animal | nenhum |
| minecraft:seagrass | animal | nenhum |
| minecraft:string | animal | nenhum |
| minecraft:verdant_froglight | animal | nenhum |
| rehooked:diamond_hook | machine | rehooked:blaze_hook, rehooked:red_hook |
| snowpig:music_disc_frosty_snig | animal | nenhum |
| society:artifact_trove | animal | nenhum |
| society:no_name_for_the_sheep | animal | nenhum |
| wildernature:hazelnut | animal | nenhum |

## Aliases de preço aplicados

| id sem preço | alias para (já priced) |
|---|---|
| cookscollection:cooking_oil | hearthandharvest:cooking_oil |
| cookscollection:lemon | culturaldelights:lemon |
| cookscollection:salt | hearthandharvest:salt |
| corn_delight:tortilla | culturaldelights:tortilla |
| crabbersdelight:coconut | beachparty:coconut |
| culturaldelights:cooking_oil | hearthandharvest:cooking_oil |
| culturaldelights:cucumber_crate | vintagedelight:cucumber_crate |
| culturaldelights:eggplant_crate | society:eggplant_crate |
| culturaldelights:raw_sausage | hearthandharvest:raw_sausage |
| culturaldelights:salt | hearthandharvest:salt |
| culturaldelights:tofu | youkaishomecoming:tofu |
| culturaldelights:vinegar | kaleidoscope_tavern:vinegar |
| farm_and_charm:wild_beetroots | farmersdelight:wild_beetroots |
| farm_and_charm:wild_carrots | farmersdelight:wild_carrots |
| farm_and_charm:wild_onions | farmersdelight:wild_onions |
| farm_and_charm:wild_potatoes | farmersdelight:wild_potatoes |
| farm_and_charm:wild_tomatoes | farmersdelight:wild_tomatoes |
| hearthandharvest:cheese_pizza_slice | vintagedelight:cheese_pizza_slice |
| hearthandharvest:chocolate_cake_slice | bakery:chocolate_cake_slice |
| hearthandharvest:corn_crate | hauntedharvest:corn_crate |
| hearthandharvest:corn_kernels | culturaldelights:corn_kernels |
| hearthandharvest:goat_milk | society:goat_milk |
| hearthandharvest:meat_pizza_slice | vintagedelight:meat_pizza_slice |
| hearthandharvest:peanut_crate | vintagedelight:peanut_crate |
| hearthandharvest:pizza_slice | brewinandchewin:pizza_slice |
| minecraft:bucket | simplehats:bucket |
| minecraft:milk | society:milk |
| oceansdelight:stuffed_squid | minersdelight:stuffed_squid |
| simplefarming:barley | farm_and_charm:barley |
| snowyspirit:candy_cane_block | windswept:candy_cane_block |
| ubesdelight:garlic | veggiesdelight:garlic |
| wildernature:turkey_egg | autumnity:turkey_egg |
| youkaishomecoming:sushi | aquaculture:sushi |

## Insumos sem preço próprio (fallback de 2 moedas por unidade)

`atmospheric:dragon_fruit_crate`, `atmospheric:golden_dragon_fruit_crate`, `atmospheric:yucca_flower`, `autumnity:sap_bottle`, `crabbersdelight:coconut_halve`, `crabbersdelight:coral_fragments`, `culturaldelights:agave`, `culturaldelights:avocado_crate`, `culturaldelights:bean_bag`, `culturaldelights:bean_pod`, `culturaldelights:butter`, `culturaldelights:butterscotch_cinnamon_pie_slice`, `culturaldelights:cinnamon`, `culturaldelights:corn_cob_crate`, `culturaldelights:mint`, `culturaldelights:pickle_crate`, `culturaldelights:wafer`, `culturaldelights:white_eggplant_crate`, `farm_and_charm:tomato_bag`, `farm_and_charm:wild_barley`, `farm_and_charm:wild_corn`, `farm_and_charm:wild_emmer`, `farm_and_charm:wild_lettuce`, `farm_and_charm:wild_oat`, `farm_and_charm:wild_strawberries`, `farmersdelight:milk_bottle`, `farmersdelight:onion_crate`, `farmersdelight:tree_bark`, `hearthandharvest:butter`, `hearthandharvest:cherry_crate`, `hearthandharvest:corn_meal`, `hearthandharvest:flour`, `hearthandharvest:hops_bag`, `hearthandharvest:veggie_pizza_slice`, `legendarysurvivaloverhaul:purified_water_bottle`, `meadow:limestone`, `minecraft:allium`, `minecraft:amethyst_cluster`, `minecraft:bamboo`, `minecraft:blaze_powder`, `minecraft:blue_ice`, `minecraft:bone`, `minecraft:bowl`, `minecraft:calcite`, `minecraft:cherry_leaves`, `minecraft:cornflower`, `minecraft:dandelion`, `minecraft:dirt`, `minecraft:ender_eye`, `minecraft:ender_pearl`, `minecraft:fermented_spider_eye`, `minecraft:flower_pot`, `minecraft:glass_bottle`, `minecraft:glow_ink_sac`, `minecraft:glow_lichen`, `minecraft:glowstone_dust`, `minecraft:hanging_roots`, `minecraft:ice`, `minecraft:ink_sac`, `minecraft:kelp`, `minecraft:lily_of_the_valley`, `minecraft:netherrack`, `minecraft:orange_dye`, `minecraft:paper`, `minecraft:phantom_membrane`, `minecraft:pink_dye`, `minecraft:pink_petals`, `minecraft:podzol`, `minecraft:purple_banner`, `minecraft:red_dye`, `minecraft:sculk`, `minecraft:sea_pickle`, `minecraft:seagrass`, `minecraft:shroomlight`, `minecraft:slime_ball`, `minecraft:soul_sand`, `minecraft:spider_eye`, `minecraft:stick`, `minecraft:sugar`, `minecraft:white_dye`, `minecraft:wind_charge`, `minersdelight:cave_carrot_crate`, `moredelight:diced_potatoes`, `moredelight:toast`, `oceansdelight:guardian`, `pamhc2trees:acornitem`, `pamhc2trees:chestnutitem`, `pamhc2trees:pecanitem`, `pamhc2trees:pinenutitem`, `paraglider:enduring_mixture`, `paraglider:energizing_mixture`, `rottencreatures:frozen_rotten_flesh`, `simplefarming:oat`, `simplefarming:rice`, `simplefarming:rye`, `society:blueberry_preserves`, `society:dragonfruit_preserves`, `sunrisegardening:weak_fertilizer`, `unusualfishmod:raw_lobster`, `unusualfishmod:raw_mossthorn`, `veggiesdelight:mature_dandelion`, `vintagedelight:oat_bag`, `vintagedelight:wild_oats`, `wildernature:turkey_meat`, `windswept:frozen_flesh_block`, `windswept:ginger_root_crate`, `windswept:gingerbread_cookie_block`, `windswept:lavender`, `youkaishomecoming:blood_bottle`, `youkaishomecoming:hosomaki`, `youkaishomecoming:stripped_mandrake_root`

## Tipos de receita contados (candidatos de food)

| tipo | receitas que geraram candidato | multiplicador |
|---|---|---|
| bakery:jam_cooking | 5 | x2 |
| botania:elven_trade | 1 | x2 (padrão, sem regra) |
| botania:mana_infusion | 5 | x2 (padrão, sem regra) |
| brewinandchewin:create_potion_pouring | 1 | x2 |
| brewinandchewin:fermenting | 37 | x3 |
| brewinandchewin:keg_pouring | 47 | x2 (padrão, sem regra) |
| crafting_shapeless | 2 | x1.4 |
| create:compacting | 11 | x2 (padrão, sem regra) |
| create:crushing | 8 | x2 (padrão, sem regra) |
| create:filling | 61 | x2 (padrão, sem regra) |
| create:haunting | 2 | x2 (padrão, sem regra) |
| create:milling | 8 | x2 (padrão, sem regra) |
| create:mixing | 34 | x3 |
| create:splashing | 1 | x2 (padrão, sem regra) |
| culturaldelights:aging | 21 | x2 (padrão, sem regra) |
| culturaldelights:baking | 15 | x2 (padrão, sem regra) |
| farm_and_charm:crafting_bowl | 9 | x1.4 |
| farm_and_charm:cutting_board | 5 | x2 (padrão, sem regra) |
| farm_and_charm:drying | 26 | x1.5 |
| farm_and_charm:mincer | 7 | x2 (padrão, sem regra) |
| farm_and_charm:pot_cooking | 23 | x2 |
| farm_and_charm:roaster | 11 | x2 (padrão, sem regra) |
| farm_and_charm:stove | 59 | x3 |
| farmersdelight:cooking | 299 | x2 |
| farmingforblockheads:market | 2 | x2 (padrão, sem regra) |
| hearthandharvest:aging | 55 | x2 (padrão, sem regra) |
| hearthandharvest:shapeless_remainder | 1 | x2 (padrão, sem regra) |
| herbalbrews:cauldron_brewing | 1 | x3 |
| herbalbrews:kettle_brewing | 23 | x3 |
| immersiveengineering:cloche | 14 | x2 (padrão, sem regra) |
| immersiveengineering:crusher | 2 | x2 (padrão, sem regra) |
| immersiveengineering:metal_press | 1 | x2 (padrão, sem regra) |
| kaleidoscope_cookery:chopping_board | 9 | x2 (padrão, sem regra) |
| kaleidoscope_cookery:flex_pot | 27 | x2 |
| kaleidoscope_cookery:flex_stockpot | 28 | x2 |
| kaleidoscope_cookery:pot | 198 | x2 |
| kaleidoscope_cookery:stockpot | 77 | x2 |
| kaleidoscope_cookery:teapot | 7 | x2 |
| meadow:cooking | 29 | x2 |
| minecraft:campfire_cooking | 127 | x1.5 |
| minecraft:crafting_shaped | 89 | x1.4 |
| minecraft:crafting_shapeless | 243 | x1.4 |
| minecraft:smelting | 64 | x2 (padrão, sem regra) |
| minecraft:smoking | 129 | x1.5 |
| refurbished_furniture:cutting_board_combining | 10 | x2 (padrão, sem regra) |
| refurbished_furniture:cutting_board_slicing | 3 | x2 (padrão, sem regra) |
| refurbished_furniture:frying_pan_cooking | 4 | x2 |
| refurbished_furniture:oven_baking | 3 | x2 (padrão, sem regra) |
| refurbished_furniture:toaster_heating | 3 | x2 (padrão, sem regra) |
| vinery:apple_fermenting | 3 | x3 |
| youkaishomecoming:cuisine_ordered | 3 | x2 (padrão, sem regra) |
| youkaishomecoming:steaming | 3 | x2 (padrão, sem regra) |

Tipos de estação sem regra própria de multiplicador usam x2: `botania:elven_trade`, `botania:mana_infusion`, `brewinandchewin:keg_pouring`, `create:compacting`, `create:crushing`, `create:filling`, `create:haunting`, `create:milling`, `create:splashing`, `culturaldelights:aging`, `culturaldelights:baking`, `farm_and_charm:cutting_board`, `farm_and_charm:mincer`, `farm_and_charm:roaster`, `farmingforblockheads:market`, `hearthandharvest:aging`, `hearthandharvest:shapeless_remainder`, `immersiveengineering:cloche`, `immersiveengineering:crusher`, `immersiveengineering:metal_press`, `kaleidoscope_cookery:chopping_board`, `minecraft:smelting`, `refurbished_furniture:cutting_board_combining`, `refurbished_furniture:cutting_board_slicing`, `refurbished_furniture:oven_baking`, `refurbished_furniture:toaster_heating`, `youkaishomecoming:cuisine_ordered`, `youkaishomecoming:steaming`.

## Padrões de template

Ids expandidos a partir de listas no mesmo arquivo: 6.

| padrão | motivo | ocorrências |
|---|---|---|
| `longwings:variant/${variant}` | no forEach over variant before it | 1 |
| `society:${fishId}_roe` | no forEach over fishId before it | 1 |
| `society:${itemId}_preserves` | no forEach over itemId before it | 1 |
| `society:aged_${brew.item.path}` | list global.brews not defined in this file | 1 |
| `society:aged_${fishId}_roe` | no forEach over fishId before it | 1 |
| `society:aged_${wine.item.path}` | list global.wines not defined in this file | 1 |
| `society:double_aged_${brew.item.path}` | list global.brews not defined in this file | 1 |
| `society:double_aged_${wine.item.path}` | list global.wines not defined in this file | 1 |
| `society:dried_${itemId}` | no forEach over itemId before it | 2 |
| `society:pickled_${recipe.item.path}` | list global.picklableVegetables not defined in this file | 1 |
| `society:pristine_${mineral.item.path}` | list global.frozenGeodeList not defined in this file | 1 |
| `society:pristine_${mineral.item.path}` | list global.gems not defined in this file | 1 |
| `society:pristine_${mineral.item.path}` | list global.geodeList not defined in this file | 1 |
| `society:pristine_${mineral.item.path}` | list global.magmaGeodeList not defined in this file | 1 |
| `society:pristine_${mineral.item.path}` | no forEach over mineral before it | 1 |
| `society:smoked_${fishId}` | no forEach over fishId before it | 1 |

## Método

- PRICED: ids literais em `globalRegistry*.js`, `globalPriceBalance.js` e `globalCanonicalItems.js`. Valor só quando aparece como `{ item, value }`, `[id, N]` ou `getConfiguredValue(N, ...)` na mesma linha.
- Exclusão: spawn eggs, saplings, totens, brinquedos/decoração e solo/fertilizante. Blocos `*_block` (e `*_salad_block`) só são excluídos quando existe fatia/porção priced com o mesmo radical.
- Receitas: saída de receitas em `c:foods`/`c:drinks` ou de tipos de estação (lista acima). Preço = soma dos insumos / quantidade de saída x multiplicador da estação, limitado a [5, 1000]. Tag de insumo usa o membro mais barato com preço.
- Fallback de insumo sem preço e sem receita: 2 moedas por unidade para `minecraft:*`, tags `c:*` e garrafas, leite, açúcar, gelo, tigelas e varas. Marcado como `fallback`.
- Máquinas: preço da entrada x 1.35 / quantidade de saída, quando a entrada tem preço.
- Animal sem receita e sem preço 1.20.1: 5 moedas (mínimo), marcado como `fallback`.
- Ordem do preço: receita; depois alias de preço: primeiro a tabela `PRICE_ALIASES` (hearthandharvest:corn, hearthandharvest:hops, wildernature:cooked_turkey_meat), depois o par de `global.canonicalItems` (nos dois sentidos), depois o mesmo caminho em um único outro namespace. O alvo tem que ser PRICED.
- Sem preço até aqui: valor de 1.20.1 do mesmo id, se existir; senão fallback de 5 moedas, marcado como `fallback`.
- Ids de fluido criados em `registerFluids.js` não contam como itens; os templates de geode/gema/artefato/relíquia entram pelas listas de `globalRegistry.js`.
- Atributo: o da entrada 1.20.1 quando existe, senão `crop`. Lista: `cooking` para food e máquina, `animalProducts` para animal.
- Saídas de máquina contadas por arquivo: wineKeg.js (60), seedMaker.js (53), mushroomLog.js (48), recyclingMachine.js (43), espressoMachine.js (17), cheesePress.js (14), preservesJar.js (11), oilMaker.js (5), loom.js (4), mayonnaiseMachine.js (4), deluxeWormFarm.js (1).
- Gerado: `kubejs/startup_scripts/globalRegistryMissingPrices.js` com 155 entradas.

