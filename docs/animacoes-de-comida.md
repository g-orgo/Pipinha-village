# Animações de comida: terceira pessoa e comidas sem animação

Este arquivo tem duas funções: explicar para o dono como o sistema funciona e o que dá para fazer, e servir de prompt para uma sessão futura executar o trabalho (seção [Prompt pronto](#prompt-pronto), no fim).

Tudo em "Como funciona hoje" foi lido do bytecode dos jars em 2026-11-03.

## Estado (2026-11-04)

Todas as 1.610 comidas e bebidas ativas têm animação completa nas duas câmeras, e isto substitui o que as seções abaixo dizem sobre lista curta e caminho C opcional.

- **Primeira pessoa**: `sunlit_tools/gen_ie_foods_all.py` gera 1.584 por tipo, a partir do ícone de cada item. Comidas de mão viram voxels com 3 grupos de mordida; tigelas, pratos, copos e garrafas têm recipiente e conteúdo.
- **Terceira pessoa**: `ThirdPersonFood` desenha o osso `food` do modelo na mão. Uma parte some quando o progresso do uso alcança o momento em que a animação `eat` reduz a escala dela a zero, sem dados por comida.
- **Custo medido**: carregamento de cerca de 170 s para 186 s e memória sem aumento, numa cópia sem janela com renderização por software.
- **Bloqueio corrigido**: `ImmersiveEatingGuard` limpa a animação de troca presa e a trava sem animação de comer.

## Estado anterior (2026-11-03)

As fases 1 a 5 foram executadas e verificadas no jogo real, sem janela, numa cópia isolada da instância (`sunlit_tools/headless_client/`).

- **Terceira pessoa**: `mods/sunlit_eating-1.0.0.jar` (fonte em `custom-mods/sunlit_eating/`). Fora da primeira pessoa, o clique direito mantém o comer normal, e toda comida ou bebida toca uma das 7 poses, escolhidas por dados em `FoodPose`.
- **Fresh Moves**: não impede o caminho B. Ele reescreve corpo e pernas, mas lê a rotação de braços e cabeça do modelo, então as poses só giram essas partes. O PlayerAnimator também ganha do NotEnoughAnimations. Veja `docs/context/decisions.md`.
- **Inventário**: `docs/animacoes-inventario.md`, gerado do registro do jogo.
- **Mordidas**: 1.251 comidas ganharam frames com `sunlit_tools/gen_bite_frames.py`. Bebidas ficam sem frames, como as poções.
- **Animação completa em primeira pessoa**: 6 comidas novas, de 4 a 6,5 s, escritas em `sunlit_tools/gen_ie_foods.py`: `farm_and_charm:potato_soup`, `crabbersdelight:clam_chowder`, `candlelight:harvest_plate`, `vintagedelight:pad_thai`, `candlelight:salad` e `minecraft:bread`. O critério foi serem os pratos prontos mais citados nas receitas, quests e lojas do pack, mais o pão. Fruta e vegetal cru ficaram de fora mesmo sendo mais citados: são ingrediente, e travar a hotbar por segundos para comer uma cenoura cansa rápido.

As seções abaixo guardam a análise original. O que ela marcava como **Confirmar no jogo** foi confirmado: em F5 a comida do Immersive Eating não era consumida, e definições em `kubejs/assets/food` funcionam.

## Resumo

- As animações vêm de um único addon: **Kaleidoscope: ImmersiveEating** (`kaleidoscope_immersiveEating-forge1.20.1-1.4.3.jar`, modId `food`). São **19 comidas, todas do Kaleidoscope Cookery**. O Tavern não tem nenhuma.
- Elas não aparecem em terceira pessoa porque são um **modelo de primeira pessoa**: mãos, talheres e comida são desenhados presos à câmera, no lugar da mão do jogador. Não dá para só "ligar" isso em terceira pessoa.
- Além de não aparecer, o F5 **cancela** a animação. Pelo código, essas 19 comidas nem devem conseguir ser comidas em terceira pessoa ou com o Shoulder Surfing. **Confirmar no jogo**, porque é o primeiro bug a resolver.
- Recomendação: um mini mod `sunlit_eating` que deixa a terceira pessoa usar o comer normal do jogo, com animações de corpo novas por **tipo de comida** (prato, tigela, bebida...). Em paralelo, comidas sem animação ganham duas camadas: mordidas no ícone para todas e animação completa de primeira pessoa só para as mais especiais.

## Como funciona hoje

**Início.** O clique direito (`GameplayEvents.onRightClickItem`) ou a tecla "Play Animations" (`InputEvents.onKey`) cancelam o uso normal do item, travam a hotbar e mandam um `AnimationPacket` ao servidor. O servidor dispara a animação `eat` só para quem está comendo (`PacketDistributor.PLAYER`). Os outros jogadores não recebem nada.

**Desenho.** `ItemRendererMixin` só age em `ItemDisplayContext.FIRST_PERSON_RIGHT_HAND`, trocando o item por um `GeoItemRenderer` do GeckoLib. Em terceira pessoa o jogo usa outro contexto, então aparece o item comum. Isso vale também para segurar a comida parada em primeira pessoa: quem tem definição sempre mostra o modelo 3D.

**Fim da comida.** Quem termina é a própria animação: a keyframe `"timeline": {"12.0": "finished;"}` manda um `FinishUsePacket`, e o servidor chama `finishUsingItem`. O GeckoLib só avança a animação quando ela é desenhada (`handleAnimations` em `GeoItemRenderer`). Sem desenho, não há `finished`, som nem comida consumida.

**Câmera.** `InputEvents.onClientTick` para a animação se a câmera não estiver em primeira pessoa e houver trava ativa. Como o clique direito não testa a câmera, em F5 ele cancela o uso normal e a animação morre no tick seguinte.

**Comidas sem definição** usam o comer normal, e aí os outros mods já cuidam da terceira pessoa:
- **NotEnoughAnimations** leva o braço à boca quando há uso de item com `UseAnim.EAT` ou `DRINK` (`enableEatDrinkAnimation: true` no config).
- **Eating Animation** troca o ícone por frames mordidos via item model. A propriedade é genérica para todos os itens, mas cada item precisa de model e frames. Hoje há vanilla e Farmer's Delight, mais o pack `EatAnimation Farmer's Delight's Compat`, que cobre também Ender's Delight e Mineral Delight (a lista de mods do pack não foi conferida até o fim).

## Caminhos para a terceira pessoa

| Caminho | O que faz | Avaliação |
| --- | --- | --- |
| **A. Comer normal em F5** | Mixin faz `onRightClickItem` não agir fora da primeira pessoa | Barato. Corrige o bug. Braço à boca e mordidas já funcionam |
| **B. Corpo por tipo de comida** | PlayerAnimator toca uma animação enquanto `isUsingItem()` for verdadeiro | **Recomendado sobre o A.** Só cliente, e o uso de item já é sincronizado, então outros jogadores também veem |
| **C. Comida 3D na mão em F5** | Desenha os ossos da comida no contexto de terceira pessoa, com mordidas | Opcional, para as comidas especiais. Caro por comida |
| **D. Repassar o IE em F5** | Espelha a sessão do IE, com clock próprio, pacote para outros jogadores e braços refeitos | Não recomendado. Os braços foram animados relativos à câmera e não reaproveitam. Se o modelo sai da tela, a animação não avança e a comida trava |
| **E. Só resource pack (EMF/CEM)** | Animar via `player.jem` | Descartado até prova em contrário: o pedido exige saber qual item está na mão, e o que já vi do EMF não mostra isso. **Não verifiquei** as variáveis dele |

Por que não só mudar `enableRightClickAnimation = false` em `config/immersive_eating.toml`: isso devolve o comer normal em todas as câmeras, mas a animação de primeira pessoa passa a depender da tecla. Serve como quebra-galho se a correção demorar, e a decisão é do dono.

Peças já disponíveis para B: `player-animation-lib-forge-1.0.2-rc1+1.20.jar` traz `PlayerAnimationRegistry` (lê `assets/<ns>/player_animation/*.json`), `PlayerAnimationAccess`, `PlayerAnimationFactory`, `ModifierLayer`, `KeyframeAnimationPlayer` e `SpeedModifier` (para casar com a duração da comida). Ele tem também `FirstPersonMode`, para não interferir na primeira pessoa. O formato exato do JSON e a assinatura das chamadas ainda precisam ser conferidos no jar.

## Como criar uma animação nova (primeira pessoa)

O IE lê tudo por dados, então não precisa de código por comida. Para o item `meumod:minha_comida`, o nome base é só o `minha_comida`:

```
kubejs/assets/food/definitions/minha_comida.json          liga o item à animação
kubejs/assets/food/geo/minha_comida.geo.json              modelo
kubejs/assets/food/animations/minha_comida.animation.json animações
kubejs/assets/food/textures/item/minha_comida.png         textura
kubejs/assets/food/sounds/novo_som.ogg                    só se o som for novo
```

```json
{
  "item": "meumod:minha_comida",
  "invisible": ["kuaizi"],
  "sounds": { "eating": "food:eat", "soup": "food:soup" }
}
```

Regras que saem do código:
- O namespace `food` é fixo para geo, textura e animação. O gerador de sons (`SoundJson`) também só lê `assets/food/definitions/`, por isso a definição vai lá.
- `kubejs/assets` é o lugar certo porque não mexe na lista de resource packs. **Confirmar no jogo** com uma comida antes de produzir em volume.
- O modelo é escolhido pelo **path do item, sem namespace**. Dois itens com o mesmo nome em mods diferentes dividiriam modelo. O gerador precisa acusar colisão.
- Ossos: `rightArm` e `leftArm` são trocados pelo braço do jogador, com a skin dele. `camera` é opcional (10 das 19) e gira a visão. O padrão de `spicy_chicken` é `root > bone > food > eat > 1..6` para os pedaços, que somem por `scale`.
- `invisible` esconde ossos fora da animação, como talheres.
- Animações: `eat` é obrigatória e precisa da keyframe `finished;` no `timeline`, senão a comida nunca é consumida. `switchin` (13 das 19) e `switchout` são opcionais.
- `sound_effects` usa nomes livres (`"1.85": {"effect": "eating"}`), traduzidos em `sounds` na definição. Sons do namespace `food` entram sozinhos no `sounds.json` dinâmico. Disponíveis: `eat`, `eating1` a `eating6`, `cake`, `cherry`, `cherry_1`, `cut_1`, `fall`, `soup`, `soup_1`, `xigua`.
- O comportamento de um pedaço por vez de `baozi_plate` e `qingtuan_plate` é fixo em código (`UniqueItem`) e não dá para repetir só com dados.
- Ferramenta: Blockbench com o plugin GeckoLib. Formato `1.8.0`, GeckoLib do pack `4.8.4`.

**Licença, atenção:** o `mods.toml` do addon declara `GPL-3.0-only (code); CC BY-NC-ND 4.0 (assets)`. O ND proíbe obra derivada dos assets, e o pack é distribuído. Copie a **estrutura** (hierarquia, nomes, ritmo), nunca geo, textura ou animação dele editados. Vale pedir autorização ao autor (XianYue) antes de publicar qualquer coisa inspirada de perto. Não sou advogado, então a decisão fica com o dono, junto do `docs/PUBLICAR.md`.

**Duração:** as atuais vão de 6,25 s a 16 s (mediana 11,25 s), com hotbar travada. Em comida comum isso cansa rápido. Sugestão para as novas: 4 a 8 s. Decisão do dono.

## Quais comidas e com qual esforço

Só **itens canônicos** recebem animação: nada que esteja em `global.removedItems` ou como duplicado em `kubejs/startup_scripts/globalCanonicalItems.js` (103 duplicados), porque esses somem do jogo. Quem ainda sobra de outros mods (Youkai's Homecoming, Bakery, Vinery, Brewery etc.) entra normalmente.

A lista real só sai com o jogo aberto, porque ser comida é definido em código. Um dump temporário com `Item.getList()` e `isEdible()` do KubeJS resolve (os dois nomes existem no jar e nos scripts do pack; a forma exata de usar ainda precisa ser conferida). O dump também deve pegar bebidas com `UseAnim.DRINK` que não sejam comida.

| Camada | O que a comida ganha | Para quem | Como |
| --- | --- | --- | --- |
| 1 | Mordidas no ícone, em primeira e terceira pessoa | Todas sem frames | Script gera 3 frames e o model com `eatinganimation:eat` em 0.35, 0.7 e 0.9 e `eatinganimation:eating` 1.0, preservando o model original do item |
| 2 | Corpo em terceira pessoa por tipo | Todas | Uma animação por tipo, mapeada por tag ou tabela: prato com talher, tigela, na mão, espeto, fatia, garrafa, xícara |
| 3 | Animação completa em primeira pessoa | Lista curta escolhida pelo dono (pratos especiais, receitas finais) | Autoria manual em Blockbench |
| 4 | Comida 3D na mão em F5 | Subconjunto da camada 3, se valer a pena | Caminho C |

Gerar a camada 3 em massa a partir do ícone (extrudar o sprite) é possível, mas o resultado não chega perto dos modelos à mão e fere a regra de cara de conteúdo original. Só faça depois de comparar um protótipo com o dono.

## Riscos para testar cedo

- **Fresh Moves** está ativo e traz `optifine/cem/player.jem`, então o EMF mexe no modelo do jogador. PlayerAnimator e NotEnoughAnimations podem disputar ou perder para ele. É o maior risco técnico do caminho B, então vem antes de qualquer autoria.
- **Servidor dedicado:** `FoodDefinitionManager` só é registrado no cliente, mas `AnimationPacket` consulta a mesma lista no servidor. Em dedicado a lista pode ficar vazia. Solo e LAN do anfitrião compartilham a JVM, portanto não sofrem disso.
- **Compilação:** `custom-mods/sunlit_sortfix/build.sh` é o modelo, sem Gradle, e precisa de JDK 17. Esta máquina não tem `javac` no PATH: a Java do CurseForge é só JRE. Mixin sem Gradle não gera refmap, então os alvos usam nomes SRG (`m_xxxxx_`).
- **Interações a conferir:** `canonicalItemSwap.js` durante a animação; comida com estrela de qualidade (Quality Food, NBT no item); comer de barriga cheia, porque não vi teste de `canEat` no fluxo do IE; soltar o mouse ou trocar de câmera no meio.

## Prompt pronto

Cole em uma sessão nova (troque o que estiver entre colchetes):

```
Leia docs/animacoes-de-comida.md e AGENTS.md. Objetivo: animações de comida em terceira
pessoa e cobertura das comidas sem animação, seguindo o documento. Decisões do dono:
duração das novas = [4 a 8 s]; lista da camada 3 = [a definir depois da fase 2];
quebra-galho enableRightClickAnimation = [não usar].

Regras: save alvo saves/Solito solamente, nunca saves/Nosso mapa; não mexer em options.txt
nem na lista de resource packs; assets novos em kubejs/assets; cara de conteúdo original;
não editar assets do ImmersiveEating (CC BY-NC-ND); tudo no Modpack.zip no fim; toda fase
só termina com teste no jogo (pedir ao dono para abrir pelo CurseForge, acompanhar logs com
tail/grep, passar checklist curto). Conferir APIs no jar antes de usar, sem chutar.

Fase 0, diagnóstico no jogo, sem mudar nada: em F5 e no Shoulder Surfing, testar
spicy_chicken (com IE) e uma comida sem IE. Registrar se a comida com IE é consumida e se o
braço vai à boca na sem IE, com Fresh Moves ativo.
Fase 1, inventário: dump temporário das comidas e bebidas; cruzar com globalCanonicalItems,
globalRemovedItems, definições do IE e frames existentes; apagar o dump do pack. Entregar
uma tabela item, mod, tipo, tem frames, tem IE, em docs/ e acusar colisões de path.
Fase 2, mini mod custom-mods/sunlit_eating, jar em mods/: caminho A (mixin em
GameplayEvents.onRightClickItem) e depois caminho B com uma única animação de corpo, como
prova contra o Fresh Moves. Pedir o JDK 17 ao dono se ainda não houver. Se o Fresh Moves
impedir, parar e trazer opções ao dono.
Fase 3, corpo por tipo: as demais animações em assets/<ns>/player_animation, tabela
item ou tag -> tipo, SpeedModifier para casar com a duração da comida.
Fase 4, mordidas: gerador em sunlit_tools/ para a camada 1, preservando os models originais.
Fase 5, autoria: uma comida completa de ponta a ponta em kubejs/assets/food, validar com o
dono e depois seguir a lista da camada 3. Caminho C só se o dono pedir.

No fim de cada fase: atualizar docs/context/state.md, uma linha em history.md, HANDOFF.md, e
dizer o que foi verificado no jogo e o que não foi.
```
