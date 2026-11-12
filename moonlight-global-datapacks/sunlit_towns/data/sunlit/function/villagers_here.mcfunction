# Espalha vida na cidade atual: 4 villagers com profissoes + chance de golem.
# Rode no centro da cidade: /function sunlit:villagers_here
summon minecraft:villager ~3 ~ ~2 {VillagerData:{profession:farmer,level:2,type:plains}}
summon minecraft:villager ~-3 ~ ~1 {VillagerData:{profession:butcher,level:2,type:plains}}
summon minecraft:villager ~1 ~ ~-3 {VillagerData:{profession:librarian,level:2,type:plains}}
summon minecraft:villager ~-2 ~ ~-2 {VillagerData:{profession:weaponsmith,level:1,type:plains}}
summon minecraft:villager ~ ~ ~5 {VillagerData:{profession:fisherman,level:1,type:plains}}
tellraw @s {"text":"[Sunlit] 5 moradores chegaram na vila. Repita em outros bairros/pracas.","color":"green"}
