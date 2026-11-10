# Mini-cozinha modelo para interiores ANTIGOS (que nao ganham a paleta nova sozinhos).
# Fique olhando para o chao da cozinha e rode: /function sunlit:decorate_room
# Coloca cozinha Farmer's Delight + moveis + Create em volta de voce.
setblock ~1 ~ ~ farmersdelight:stove
setblock ~2 ~ ~ farmersdelight:cooking_pot
setblock ~1 ~ ~1 refurbished_furniture:oak_kitchen_sink
setblock ~2 ~ ~1 refurbished_furniture:oak_kitchen_cabinetry
setblock ~ ~ ~1 refurbished_furniture:oak_table
setblock ~ ~ ~2 refurbished_furniture:oak_chair
setblock ~-1 ~ ~ furniture:oak_cabinet
setblock ~-1 ~ ~1 minecraft:bookshelf
setblock ~3 ~ ~ create:basin
setblock ~3 ~ ~1 create:andesite_casing
setblock ~2 ~ ~2 minecraft:lantern
tellraw @s {"text":"[Sunlit] Cozinha modelo colocada. Gire/ajuste com a chave inglesa do Create se precisar.","color":"gold"}
