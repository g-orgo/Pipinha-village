# Inventário de comidas e bebidas

Este documento resume o inventário de comidas e bebidas do Pipinha's Village 1.21.1: quantas são, de que tipo, quais têm mordidas e animação completa, e onde estão as colisões de path que podem quebrar o modelo. A lista item a item (mais de 1700 linhas) não fica mais aqui. Ela sai do gerador, que lê o registro do jogo.

Esta versão só existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1. O pack é baseado no Society: Sunlit Valley (1.20.1), e o inventário foi convertido a partir dele.

## Alto nível

O inventário é a base para decidir **quais comidas recebem animação** e **quais ficam só com mordidas**. Ele parte de um registro do jogo, não de uma lista escrita à mão, então pega também itens de mods que não estão no nosso catálogo. Cada item cai em um **tipo**: comida ou bebida, e "outro" para o que usa a animação de comer ou beber mas não tem dados de comida (como garrafas e copos de itens de mods diversos).

Cada item também tem uma **pose** de terceira pessoa, que diz como a mão segura o item enquanto ele é consumido. A maior parte é `hand` (segurar na mão), seguida de `bowl` (tigela), `cup` (copo), `slice` (fatia), `plate` (prato), `bottle` (garrafa) e `skewer` (espeto). A pose é o que a camada de corpo usa para escolher a animação (ver [[animacoes-de-comida]]).

Os itens com mais peso no pack vêm de **society**, **youkaishomecoming**, **kaleidoscope_cookery**, **farmersdelight**, **veggiesdelight**, **miners_delight** e **vintagedelight**, nessa ordem de quantidade. A lista de quem entra em cada tipo muda sempre que um mod é trocado, então o número precisa ser refeito a cada fase.

## Baixo nível

```py title:InventarioItem
# Um registro do inventário (gerado, não editar à mão)
item = "society:espresso"        # id completo, com namespace
mod = "society"                  # mod de origem
tipo = "bebida"                  # comida | bebida | outro
pose = "cup"                     # hand | bowl | cup | slice | plate | bottle | skewer
mordidas = True                  # tem frames de mordida
icone = "plano"                  # plano (sprite) ou 3D (model)
animacao_completa = True         # tem definição do Immersive Eating
```

```py title:Colisao
# Colisão de path: o Immersive Eating escolhe o modelo pelo path do item, sem o namespace
path = "espresso"
itens = ["youkaishomecoming:espresso", "society:espresso"]
# Só há problema se dois itens com o mesmo path tiverem definição.
```

```py title:ResumoDoInventario
# Números de referência, da última geração feita na 1.20.1 (refazer na 1.21.1)
itens_com_uso_de_comer_ou_beber = 1920
itens_ativos = 1740              # sem removidos nem duplicados
ativos_por_tipo = { comida: 1381, bebida: 229, outro: 130 }
com_frames_de_mordida = 1378
sem_frames_e_com_icone_3d = 3    # sem como gerar hoje
com_animacao_completa = 1610
colisoes_entre_ativos = 25
```

Regras que saem do código:
- Itens sem frames de mordida e com ícone 3D não têm como gerar frames sozinhos. Entram numa lista própria para decisão manual.
- Itens removidos ou duplicados nunca entram no inventário ativo.
- A pose vem do tipo do item, e não de uma tabela manual por comida.
- O gerador é `tools/pack_tools/food_inventory.py`. Ele hoje lê o registro, mas os números acima foram tirados da 1.20.1. Na 1.21.1 eles mudam, e a lista precisa ser refeita antes de qualquer decisão.

### Colisões de path

O Immersive Eating escolhe o modelo pelo path do item, sem o namespace. Antes disso ele confere o id completo na lista de definições. Por isso só há problema quando dois itens com o mesmo path têm definição.

- Colisões entre itens ativos: 25.
- Colisões que afetam a animação completa (dois itens com o mesmo path e ambos com definição):
  - `ancient_fruit`: `society:ancient_fruit`, `quark:ancient_fruit`
  - `black_tea`: `farmersrespite:black_tea`, `herbalbrews:black_tea`
  - `bread`: `minecraft:bread`, `bakery:bread`
  - `bun`: `youkaishomecoming:bun`, `bakery:bun`
  - `butter`: `youkaishomecoming:butter`, `farm_and_charm:butter`
  - `cherry`: `hearthandharvest:cherry`, `vinery:cherry`
  - `cherry_wine`: `hearthandharvest:cherry_wine`, `vinery:cherry_wine`
  - `cooked_cod`: `minecraft:cooked_cod`, `farm_and_charm:cooked_cod`
  - `cooked_salmon`: `minecraft:cooked_salmon`, `farm_and_charm:cooked_salmon`
  - `espresso`: `youkaishomecoming:espresso`, `society:espresso`
  - `green_tea`: `farmersrespite:green_tea`, `herbalbrews:green_tea`
  - `lavender_tea`: `windswept:lavender_tea`, `herbalbrews:lavender_tea`
  - `mashed_potatoes`: `veggiesdelight:mashed_potatoes`, `brewery:mashed_potatoes`
  - `mocha`: `youkaishomecoming:mocha`, `society:mocha`
  - `mushroom_soup`: `youkaishomecoming:mushroom_soup`, `candlelight:mushroom_soup`
  - `potato_soup`: `youkaishomecoming:potato_soup`, `largemeals:potato_soup`, `farm_and_charm:potato_soup`
  - `raisins`: `hearthandharvest:raisins`, `society:raisins`
  - `red_wine`: `youkaishomecoming:red_wine`, `vinery:red_wine`
  - `rotten_apple`: `domesticationinnovation:rotten_apple`, `hauntedharvest:rotten_apple`
  - `toast`: `refurbished_furniture:toast`, `bakery:toast`
  - `waffle`: `hearthandharvest:waffle`, `bakery:waffle`
  - `white_grape`: `youkaishomecoming:white_grape`, `vinery:white_grape`

Essas colisões precisam ser resolvidas antes da lista de animação completa ser usada na 1.21.1. A saída mais simples é o script de remap de ids (`largemeals -> large_meals` e similares) ou um item canônico escolhido pelo dono.

## Estado na 1.21.1

- **Gerador do inventário:** `tools/pack_tools/food_inventory.py` existe na instância, mas ainda precisa ser conferido contra o registro 1.21.1. **A portar** junto dos scripts do KubeJS, que já estão na instância em modo estático e em correção pelos logs.
- **Números de referência:** ainda são os da 1.20.1. **Não refeitos** para a 1.21.1.
- **Colisões de path:** a lista acima vem da 1.20.1. Na 1.21.1 ela precisa ser gerada de novo. Pode mudar, porque mods foram trocados e alguns itens somem.
- **Assets de animação completa:** `kubejs/assets/food/` já tem 1593 definições e 1577 modelos, animações e texturas. A lista de quem ganhou definição precisa ser refeita com o inventário novo. **A portar** o resto.
- **Mods que saíram do pack:** Splendid Slimes, Splendid Cogs e Species não estão em `mods/`. Itens desses mods saem do inventário. O Botania voltou em 2026-11-13 (Botania Revived, mesmo mod id), então os itens dele contam de novo.

## Regras de negócio

- Só itens ativos (não removidos e não duplicados) entram no inventário.
- Cada item tem exatamente um tipo e uma pose.
- Colisões de path entre itens com definição precisam ser resolvidas antes de publicar a animação completa.
- Os números do inventário só valem para a geração em que foram tirados. Antes de decidir algo com eles, refazer o inventário.
- Itens sem frames e com ícone 3D são revisados à mão, sem geração automática.

## Anotações

> Por que o inventário não tem a lista item a item? Porque ela tem mais de 1700 linhas, muda a cada geração, e o gerador sempre pode refazê-la a partir do registro. Manter a lista no documento só envelhece.

> De onde sai a pose de cada item? Do tipo (comida, bebida ou outro) e do formato do item (prato, tigela, copo, garrafa, espeto e assim por diante), ambos lidos do registro.

**Ainda em aberto:** os números de referência e as colisões de path precisam ser refeitos no registro da 1.21.1. Também falta decidir a resolução das colisões (remap de ids ou item canônico) e confirmar o gerador do inventário na fase F5.
