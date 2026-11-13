# Limpa teias dos interiores antigos (chunks ja gerados) num raio de 96 blocos.
# Rode parado dentro de uma casa: /function sunlit:clean_cobwebs
# So limpa, nao remove loot nem moveis. Depois decore manualmente ou rode sunlit:decorate_room.
fill ~-96 ~-12 ~-96 ~96 ~12 ~96 minecraft:air replace minecraft:cobweb
tellraw @s {"text":"[Sunlit] Teias removidas num raio de 96 blocos. Interiores antigos limpos.","color":"green"}
