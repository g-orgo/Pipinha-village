console.info("[SOCIETY] lostCityCreatePalette.js loaded");

// Paleta cozy Sunlit: cozinhas/fazendas (Farmer's Delight, Refurbished, Let's Do, Create)
// So afeta pecas padrao do Lost Cities (rodovias/pontes/trilhos). As cidades Sunlit usam o datapack
// moonlight-global-datapacks/sunlit_towns, gerado por sunlit_tools/towns/convert.py.
// Nunca colocar cobweb com peso 1000 aqui (vira predio abandonado).
ServerEvents.generateData("after_mods", (e) => {
  e.json(
    "lostcities:lostcities/palettes/common.json",
    {
      "palette": [
        {
          "char": "1",
          "block": "minecraft:spawner",
          "mob": "easymobs"
        },
        {
          "char": "4",
          "block": "minecraft:spawner",
          "mob": "hardmobs"
        },
        {
          "char": "T",
          "block": "minecraft:wall_torch[facing=north]",
          "torch": true
        },
        {
          "char": "h",
          "block": "minecraft:glowstone"
        },
        {
          "char": "g",
          "block": "minecraft:redstone_torch[lit=true]"
        },
        {
          "char": "9",
          "blocks": [
            {
              "random": 32,
              "block": "minecraft:cyan_terracotta"
            },
            {
              "random": 32,
              "block": "minecraft:gray_terracotta"
            },
            {
              "random": 32,
              "block": "minecraft:cyan_concrete"
            },
            {
              "random": 1000,
              "block": "minecraft:gray_concrete"
            }
          ]
        },
        {
          "char": "Y",
          "block": "minecraft:white_stained_glass"
        },
        {
          "char": "Z",
          "blocks": [
            {
              "random": 32,
              "block": "minecraft:glass"
            },
            {
              "random": 32,
              "block": "minecraft:gray_stained_glass"
            },
            {
              "random": 32,
              "block": "minecraft:blue_stained_glass"
            },
            {
              "random": 1000,
              "block": "minecraft:light_blue_stained_glass"
            }
          ]
        },
        {
          "char": "p",
          "blocks": [
            {
              "random": 30,
              "block": "minecraft:poppy"
            },
            {
              "random": 30,
              "block": "minecraft:dandelion"
            },
            {
              "random": 15,
              "block": "minecraft:oak_sapling[stage=1]"
            },
            {
              "random": 15,
              "block": "minecraft:spruce_sapling[stage=1]"
            },
            {
              "random": 15,
              "block": "minecraft:birch_sapling[stage=1]"
            },
            {
              "random": 1000,
              "block": "minecraft:acacia_sapling[stage=1]"
            }
          ]
        },
        {
          "char": "K",
          "blocks": [
            {
              "random": 64,
              "block": "minecraft:poppy"
            },
            {
              "random": 1000,
              "block": "minecraft:dandelion"
            }
          ]
        },
        {
          "char": "!",
          "blocks": [
            {
              "random": 15,
              "block": "minecraft:diamond_block"
            },
            {
              "random": 20,
              "block": "minecraft:gold_block"
            },
            {
              "random": 15,
              "block": "minecraft:emerald_block"
            },
            {
              "random": 1000,
              "block": "minecraft:iron_block"
            }
          ]
        },
        {
          "char": "F",
          "blocks": [
            {
              "random": 20,
              "block": "farmersdelight:stove"
            },
            {
              "random": 18,
              "block": "farmersdelight:cooking_pot"
            },
            {
              "random": 18,
              "block": "farmersdelight:oak_cabinet"
            },
            {
              "random": 16,
              "block": "farmersdelight:cutting_board"
            },
            {
              "random": 16,
              "block": "refurbished_furniture:oak_kitchen_sink"
            },
            {
              "random": 16,
              "block": "refurbished_furniture:oak_kitchen_cabinetry"
            },
            {
              "random": 14,
              "block": "refurbished_furniture:oak_kitchen_drawer"
            },
            {
              "random": 12,
              "block": "refurbished_furniture:light_stove"
            },
            {
              "random": 12,
              "block": "create:basin"
            },
            {
              "random": 12,
              "block": "create:depot"
            },
            {
              "random": 10,
              "block": "create:andesite_casing"
            },
            {
              "random": 10,
              "block": "furniture:oak_cabinet"
            },
            {
              "random": 8,
              "block": "minecraft:crafting_table"
            },
            {
              "random": 8,
              "block": "minecraft:furnace[facing=north]"
            },
            {
              "random": 4,
              "block": "minecraft:brewing_stand"
            },
            {
              "random": 3,
              "block": "minecraft:cauldron"
            }
          ]
        },
        {
          "char": "%",
          "blocks": [
            {
              "random": 15,
              "block": "minecraft:cobweb"
            },
            {
              "random": 1000,
              "block": "minecraft:air"
            }
          ]
        },
        {
          "char": "\\",
          "blocks": [
            {
              "random": 40,
              "block": "refurbished_furniture:oak_table"
            },
            {
              "random": 1000,
              "block": "minecraft:oak_planks"
            }
          ]
        },
        {
          "char": "{",
          "block": "minecraft:chain"
        },
        {
          "char": "*",
          "blocks": [
            {
              "random": 25,
              "block": "minecraft:potted_poppy"
            },
            {
              "random": 25,
              "block": "minecraft:potted_dandelion"
            },
            {
              "random": 20,
              "block": "minecraft:lantern"
            },
            {
              "random": 15,
              "block": "furniture:lamp_white"
            },
            {
              "random": 15,
              "block": "refurbished_furniture:white_lamp"
            },
            {
              "random": 1000,
              "block": "minecraft:potted_oak_sapling"
            }
          ]
        },
        {
          "char": "l",
          "block": "minecraft:ladder[facing=north]"
        },
        {
          "char": "-",
          "block": "minecraft:oak_pressure_plate"
        },
        {
          "char": ".",
          "blocks": [
            {
              "random": 40,
              "block": "refurbished_furniture:oak_chair"
            },
            {
              "random": 30,
              "block": "furniture:oak_desk_chair"
            },
            {
              "random": 1000,
              "block": "minecraft:oak_fence"
            }
          ]
        },
        {
          "char": "L",
          "blocks": [
            {
              "random": 30,
              "block": "minecraft:bookshelf"
            },
            {
              "random": 25,
              "block": "farmersdelight:oak_cabinet"
            },
            {
              "random": 25,
              "block": "furniture:oak_cabinet"
            },
            {
              "random": 20,
              "block": "furniture:oak_dresser"
            },
            {
              "random": 20,
              "block": "furniture:oak_desk"
            },
            {
              "random": 15,
              "block": "refurbished_furniture:oak_table"
            },
            {
              "random": 12,
              "block": "farmersdelight:carrot_crate"
            },
            {
              "random": 12,
              "block": "farmersdelight:potato_crate"
            }
          ]
        },
        {
          "char": "W",
          "block": "minecraft:water"
        },
        {
          "char": "C",
          "block": "minecraft:chest[facing=north]",
          "loot": "chestloot"
        },
        {
          "char": "G",
          "block": "minecraft:grass_block"
        },
        {
          "char": "D",
          "block": "minecraft:dirt"
        },
        {
          "char": " ",
          "block": "minecraft:air"
        },
        {
          "char": "~",
          "block": "minecraft:structure_void"
        }
      ]
    }
  );
});
