# Mini-apartamento para interiores ANTIGOS (chunks ja gerados nao ganham a paleta nova).
# Fique no chao do comodo e rode: /function sunlit:decorate_apartment
setblock ~1 ~ ~ furniture:oak_desk
setblock ~1 ~ ~1 furniture:oak_desk_chair
setblock ~2 ~ ~ minecraft:bookshelf
setblock ~2 ~ ~1 furniture:oak_dresser
setblock ~ ~ ~1 refurbished_furniture:oak_table
setblock ~ ~ ~2 refurbished_furniture:oak_chair
setblock ~-1 ~ ~ refurbished_furniture:white_lamp
setblock ~-1 ~ ~1 furniture:lamp_white
setblock ~3 ~ ~ create:black_seat
setblock ~3 ~ ~1 create:depot
tellraw @s {"text":"[Pipinha] Apartamento mobiliado. Use a chave do Create para girar o que ficar torto.","color":"gold"}
