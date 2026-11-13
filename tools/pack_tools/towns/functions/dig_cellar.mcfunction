# Escava um porao 5x3x5 embaixo de voce (para casas ANTIGAS sem porao).
# ATENCAO: fique no TERREO da casa, com 4 blocos livres abaixo. Rode: /function sunlit:dig_cellar
# 1) esvazia
fill ~-2 ~-4 ~-2 ~2 ~-1 ~2 minecraft:air
# 2) piso
fill ~-2 ~-4 ~-2 ~2 ~-4 ~2 minecraft:stone_bricks
# 3) escada de acesso no canto
setblock ~2 ~-1 ~2 minecraft:ladder[facing=north]
setblock ~2 ~-2 ~2 minecraft:ladder[facing=north]
setblock ~2 ~-3 ~2 minecraft:ladder[facing=north]
# 4) abre o buraco de descida no terreo
setblock ~2 ~ ~2 minecraft:air
# 5) mobilia do porao: bancada Create + baus + fornalha + tocha
setblock ~-2 ~-3 ~-2 create:basin
setblock ~-1 ~-3 ~-2 create:andesite_casing
setblock ~-2 ~-3 ~2 minecraft:chest[facing=north]
setblock ~-1 ~-3 ~2 minecraft:chest[facing=north]
setblock ~2 ~-3 ~-2 minecraft:furnace[facing=north]
setblock ~1 ~-3 ~-1 minecraft:wall_torch[facing=north]
setblock ~-1 ~-3 ~1 minecraft:wall_torch[facing=south]
tellraw @s {"text":"[Sunlit] Porao escavado! Desca pela escada no canto. Recoloque o alcapao se quiser.","color":"gold"}
