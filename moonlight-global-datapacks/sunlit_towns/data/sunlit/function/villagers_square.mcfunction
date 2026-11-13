# Praca viva: villagers + golem + gatos. Rode numa praca: /function sunlit:villagers_square
summon minecraft:villager ~2 ~ ~ {VillagerData:{profession:nitwit,level:1,type:plains}}
summon minecraft:villager ~-2 ~ ~ {VillagerData:{profession:shepherd,level:1,type:plains}}
summon minecraft:villager ~ ~ ~2 {VillagerData:{profession:cartographer,level:1,type:plains}}
summon minecraft:iron_golem ~ ~1 ~
summon minecraft:cat ~3 ~ ~3
tellraw @s {"text":"[Pipinha] Praca animada: moradores + golem + gato.","color":"green"}
