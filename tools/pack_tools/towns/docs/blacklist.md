# Blacklist de plantio

Este documento lista as culturas, frutas, sementes e mudas que nao podem aparecer no mapa Sunlit Valley. A lista vive em `itemcheck.py` (`CROP_BLACKLIST`) e entra na variavel `BANNED`, que e checada pelos geradores de hortas, lotes e loot. Quem nao cabe no pack nao entra no mapa, mesmo que o mod continue instalado.

## Alto nível

A blacklist existe porque o modpack desliga ou esconde parte das culturas, e o mapa nao pode plantar algo que o jogador nao consegue colher ou que nao cresce. Ela junta tres fontes: os itens removidos ou escondidos pelo **KubeJS** (`globalRemovedItems.js`), a cadeia quebrada que o `stripTags` de `handleItemBlockFluidTags.js` desliga, e a decisao de edicao para batata e cenoura vanilla, que saem das hortas e do loot.

A blacklist vale para tudo que o gerador produz: os predios de [[casas]], as hortas e os lotes dos bairros, e os baus com comida. O [[estudo_do_modpack]] explica por que cada mod entrou no pacote, e a lista aqui so guarda o resultado dessa decisao.

O `validate.py` e a rede de seguranca: se qualquer palette, parque, lote ou tabela de loot citar um id da lista, o pipeline falha e aponta o arquivo e o bloco.

## Baixo nível

```py title:CulturasBloqueadas
# grupo 1: globalRemovedItems.js (removedItems e hiddenItems: colheitas, caixotes, sementes, mudas)
atmospheric:golden_dragon_fruit, atmospheric:golden_dragon_fruit_crate
windswept:ginger_root_crate
farmersdelight:carrot_crate, farmersdelight:potato_crate, farmersdelight:onion_crate
farmersdelight:beetroot_crate, farmersdelight:onion
farmersdelight:wild_beetroots, farmersdelight:wild_cabbages, farmersdelight:wild_potatoes
farmersdelight:wild_carrots, farmersdelight:wild_rice, farmersdelight:wild_onions
farm_and_charm:tomato_seeds, farm_and_charm:rotten_tomato, farm_and_charm:tomato, farm_and_charm:tomato_bag
vintagedelight:oat_seeds
pamhc2trees:gooseberry_sapling, pamhc2trees:chestnut_sapling, pamhc2trees:avocado_sapling
pamhc2trees:candlenut_sapling, pamhc2trees:acorn_sapling, pamhc2trees:soursop_sapling
pamhc2trees:spiderweb_sapling, pamhc2trees:walnut_sapling, pamhc2trees:pear_sapling
pamhc2trees:nutmeg_sapling

# grupo 2: handleItemBlockFluidTags.js (stripTags: cadeia de semente, caixote e planta selvagem quebrada)
vintagedelight:oat, vintagedelight:wild_oats, vintagedelight:raw_oats
farmersdelight:cabbage_crate, farmersdelight:tomato_crate, farmersdelight:tomato_seeds
farmersdelight:wild_onions
brewery:hops_seeds
farm_and_charm:strawberry_seed, farm_and_charm:strawberry, farm_and_charm:lettuce, farm_and_charm:corn
society:eggplant
pamhc2trees:grapefruit_sapling, pamhc2trees:pomegranate_sapling, pamhc2trees:guava_sapling
pamhc2trees:jackfruit_sapling, pamhc2trees:tamarind_sapling, pamhc2trees:papaya_sapling
pamhc2trees:durian_sapling, pamhc2trees:rambutan_sapling, pamhc2trees:lime_sapling
pamhc2trees:fig_sapling, pamhc2trees:date_sapling, pamhc2trees:coconut_sapling
pamhc2trees:apricot_sapling, pamhc2trees:almond_sapling, pamhc2trees:cashew_sapling
pamhc2trees:persimmon_sapling, pamhc2trees:pistachio_sapling, pamhc2trees:breadfruit_sapling
pamhc2trees:vanillabean_sapling, pamhc2trees:peppercorn_sapling, pamhc2trees:olive_sapling
pamhc2trees:pecan_sapling, pamhc2trees:pinenut_sapling, pamhc2trees:paperbark_sapling
pamhc2trees:maple_sapling, pamhc2trees:spiderweb_sapling

# grupo 3: decisao de edicao (vanilla, sem tag sazonal; quark-common.toml desliga os caixotes de batata e cenoura, sem id no registro)
minecraft:potato, minecraft:carrot, minecraft:potatoes, minecraft:carrots
```

#### Regras de negócio

- Um id na lista nunca entra em palette, parque, lote, predio ou tabela de loot.
- Batata e cenoura vanilla saem das hortas e do loot, porque nao tem tag sazonal e o mapa usa so plantas do ano inteiro.
- Hortas usam beetroots e pimentao no lugar de batata e cenoura.
- A lojinha do posto troca o caixote de batata por um caixote de brocolis, na mesma posicao.
- O `validate.py` falha com `cultura proibida (CROP_BLACKLIST)`, citando o arquivo e o id, se algum id da lista aparecer.
- Mods que continuam no pack, como `farm_and_charm:potato_bag` e `veggiesdelight:carrot_juice`, nao sao culturas e ficam fora da lista.

## Anotações

> **Por que a vinicola (vinery) fica de fora?** As folhas e os troncos de macieira e cereja escura continuam permitidos porque o pomar precisa de arvores de maca. A lista pega so os itens de cultura.

**Ainda em aberto:** confirmar se `veggiesdelight:carrot_juice` (bebida) deve sair do loot de bebidas. Hoje fica, porque nao e planta.

**Ainda em aberto:** `quark` e `zeta` estao na lista de namespaces desligaveis de `itemcheck.py`, mas o registro de caixotes de batata e cenoura do Quark nao aparece em `registry.json`. Se o Quark voltar a ser ativado, a lista precisa ser revista.
