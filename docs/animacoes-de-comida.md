# Animações de comida: terceira pessoa e comidas sem animação

Este documento explica como as animações de comer funcionam no Pipinha's Village 1.21.1, o que já existe na instância e o que ainda falta portar. Ele também serve de roteiro para a próxima sessão de trabalho nisso.

Esta versão só existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1. O pack é baseado no Society: Sunlit Valley (1.20.1), e o conteúdo é convertido aqui.

## Alto nível

Comer no pack tem duas camadas. A primeira é a **animação completa de primeira pessoa**, feita pelo **Immersive Eating** (`kaleidoscope_ImmersiveEating`, versão 1.5.6 na 1.21.1). Ele desenha a mão, o talher e a comida presos à câmera, com um **modelo GeckoLib** por comida. A segunda são as **mordidas no ícone**, feitas pelo **Eating Animation** (`eatinganimation`, versão 6.0.1), que troca o ícone do item por frames mordidos e vale para qualquer comida que tenha frames.

O problema de fundo é que a animação completa é um modelo de primeira pessoa. Ela não aparece em **terceira pessoa** (vista de fora ou com o **Shoulder Surfing**), porque o jogo usa outro contexto de desenho para a mão. Pior: em terceira pessoa a animação é cancelada, e a comida nem chega a ser consumida. Por isso a proposta é um mini mod, `sunlit_eating` (ainda não existe na instância), que deixa a terceira pessoa usar o comer normal do jogo e acrescenta uma **animação de corpo** por **tipo de comida** (prato, tigela, bebida e assim por diante), tocada pelo **Player Animation Lib** (`player-animation-lib`, 2.0.4 na 1.21.1).

Sobre o que falta com comidas sem animação: a camada de mordidas cobre quase todas as comidas ativas, e a animação completa só vale para uma lista curta de pratos especiais, escolhida pelo dono.

## Baixo nível

Cada comida com animação completa é ligada por dados. Nenhum código é necessário por comida.

```py title:AnimacaoDeComida
# Caminhos para o item meumod:minha_comida (só o nome base "minha_comida" conta)
definitions/minha_comida.json           # liga o item à animação
geo/minha_comida.geo.json               # modelo
animations/minha_comida.animation.json  # animações
textures/item/minha_comida.png          # textura
sounds/novo_som.ogg                     # só se o som for novo, no namespace food
```

```py title:DefinicaoDeComida
# kubejs/assets/food/definitions/minha_comida.json
item = "meumod:minha_comida"
invisible = ["kuaizi"]                  # ossos escondidos fora da animação, como talheres
sounds = { eating = "food:eat", soup = "food:soup" }
```

```py title:AnimacaoEat
# Animação "eat": obrigatória
timeline = { "12.0": "finished;" }      # sem a keyframe finished, a comida nunca é consumida
sound_effects = { "1.85": { effect = "eating" } }  # nomes livres, traduzidos em sounds
switchin = opcional                     # presente em 13 das 19 comidas de referência
switchout = opcional
root > bone > food > eat > 1..6         # padrão para pedaços que somem por scale
camera = opcional                       # gira a visão, presente em 10 das 19
```

```py title:Terceira Pessoa
# Camada de corpo, a ser criada em assets/<ns>/player_animation
FoodPose                                 # tabela de dados: item ou tag -> tipo -> animação
SpeedModifier                            # casa a duração da animação com a da comida
rightArm, leftArm                        # trocados pelo braço do jogador, com a skin dele
```

Regras que saem do código:
- O namespace `food` é fixo para geo, textura e animação. O gerador de sons só lê `assets/food/definitions/`, então a definição vai lá.
- `kubejs/assets` é o lugar certo para isso, porque não mexe na lista de resource packs.
- O modelo é escolhido pelo **path do item, sem namespace**. Dois itens com o mesmo path em mods diferentes dividiriam modelo, e o gerador precisa acusar essa colisão.
- Sons do namespace `food` entram sozinhos no `sounds.json` dinâmico. Os disponíveis são `eat`, `eating1` a `eating6`, `cake`, `cherry`, `cherry_1`, `cut_1`, `fall`, `soup`, `soup_1` e `xigua`.
- O comportamento de um pedaço por vez de `baozi_plate` e `qingtuan_plate` é fixo em código (`UniqueItem`) e não dá para repetir só com dados.
- Ferramenta de autoria: Blockbench com o plugin GeckoLib. Formato `1.8.0`. A GeckoLib do pack é a 4.9.3 na 1.21.1 (a 1.20.1 usava 4.8.4).

**Licença, atenção:** o `mods.toml` do addon da 1.20.1 declarava `GPL-3.0-only (code); CC BY-NC-ND 4.0 (assets)`. O ND proíbe obra derivada dos assets, e o pack é distribuído. Copie só a **estrutura** (hierarquia, nomes, ritmo), nunca geo, textura ou animação editados a partir dele. Conferir o `mods.toml` do jar 1.21.1 antes de publicar, e pedir autorização ao autor se algo for inspirado de perto. A decisão final é do dono, junto do `docs/PUBLICAR.md`.

**Duração:** as animações de referência vão de 6,25 s a 16 s (mediana 11,25 s), com a hotbar travada. Em comida comum isso cansa rápido. Sugestão para as novas: 4 a 8 s. Decisão do dono.

### Quais comidas recebem o quê

Só **itens canônicos** recebem animação. Nada que esteja em `global.removedItems` ou seja duplicado em `kubejs/startup_scripts/globalCanonicalItems.js` entra, porque esses itens somem do jogo. O resto (Youkai's Homecoming, Bakery, Vinery, Brewery e outros) entra normalmente.

A lista real só sai com o jogo aberto, porque ser comida é definido em código. Um dump temporário com `Item.getList()` e `isEdible()` do KubeJS resolve, e deve pegar também bebidas com `UseAnim.DRINK` que não sejam comida. O dump é temporário e não fica no pack.

| Camada | O que a comida ganha | Para quem | Como |
| --- | --- | --- | --- |
| 1 | Mordidas no ícone, em primeira e terceira pessoa | Todas as comidas sem frames | Gerador escreve 3 frames e o model com `eatinganimation:eat` em 0.35, 0.7 e 0.9, e `eatinganimation:eating` em 1.0, preservando o model original |
| 2 | Corpo em terceira pessoa, por tipo | Todas | Uma animação por tipo, mapeada por tag ou tabela |
| 3 | Animação completa em primeira pessoa | Lista curta escolhida pelo dono (pratos especiais, receitas finais) | Autoria manual em Blockbench |
| 4 | Comida 3D na mão em terceira pessoa | Subconjunto da camada 3, se valer a pena | Caminho C, abaixo |

Gerar a camada 3 em massa, extrudando o sprite do ícone, é possível, mas o resultado não chega perto dos modelos feitos à mão e fere a regra de cara de conteúdo original. Só fazer depois de comparar um protótipo com o dono.

### Caminhos para a terceira pessoa

| Caminho | O que faz | Avaliação |
| --- | --- | --- |
| **A. Comer normal em F5** | Mixin faz o `onRightClickItem` não agir fora da primeira pessoa | Barato. Corrige o cancelamento. Mordidas já funcionam |
| **B. Corpo por tipo** | Player Animation Lib toca uma animação enquanto `isUsingItem()` for verdadeiro | **Recomendado sobre o A.** Só cliente, e o uso de item já é sincronizado, então outros jogadores também veem |
| **C. Comida 3D na mão em terceira pessoa** | Desenha os ossos da comida no contexto de terceira pessoa, com mordidas | Opcional, para as comidas especiais. Caro por comida |
| **D. Repassar o Immersive Eating em terceira pessoa** | Espelha a sessão, com clock próprio e pacote para outros jogadores | Não recomendado. Os braços são animados relativos à câmera e não reaproveitam; se o modelo sai da tela, a animação trava |
| **E. Só resource pack (EMF)** | Animar via `player.jem` | Descartado até prova em contrário. Não verificado nas variáveis do EMF |

Trocar só `enableRightClickAnimation = false` no config do Immersive Eating devolve o comer normal em todas as câmeras, mas a animação de primeira pessoa passa a depender da tecla. Serve de quebra-galho, e a decisão é do dono.

Peças para o caminho B já estão na instância: `player-animation-lib` 2.0.4 e `geckolib` 4.9.3. O formato exato do JSON em `assets/<ns>/player_animation` e as assinaturas das chamadas ainda precisam ser conferidos no jar da versão 2.0.4, antes de escrever código.

### Riscos para testar cedo

- **Fresh Moves** (resource pack, `-1.21.2 Fresh Moves v3.1`) e **EMF** (`entity_model_features`) mexem no modelo do jogador. O Player Animation Lib pode disputar com eles. É o maior risco técnico do caminho B, então vem antes de qualquer autoria.
- **Servidor dedicado:** o registro de definições é feito no cliente, mas o pacote de animação consulta a mesma lista no servidor. Em dedicado a lista pode ficar vazia. Solo e LAN do anfitrião não sofrem disso.
- **Compilação do mini mod:** o modelo é `custom-mods/sunlit_sortfix/build.sh`, sem Gradle. Ele precisa do JDK certo para a 1.21.1 (conferir antes de compilar). Mixin sem Gradle não gera refmap, então os alvos usam nomes SRG.
- **Interações a conferir:** `canonicalItemSwap.js` durante a animação; comida com estrela de qualidade (`quality_food`, NBT no item); comer com a barriga cheia; soltar o mouse ou trocar de câmera no meio da animação.

## Estado na 1.21.1

- **Assets da animação completa:** já copiados para `kubejs/assets/food/` (1593 definições, 1577 geo, 1577 animações e 1577 texturas). Os scripts que consomem isso (fase F5, `kubejs/`) já foram portados em modo estático (379 de 379 com sintaxe válida) e seguem em correção a partir dos logs do dono. **A conferir no jogo.**
- **Immersive Eating:** `kaleidoscope_ImmersiveEating-neoforge1.21.1-1.5.6.jar` está em `mods/`. A versão de referência da 1.20.1 era a 1.4.3. **Existe**, mas o comportamento em terceira pessoa ainda não foi testado na 1.21.1. **Confirmar no jogo**, sem rodar o jogo pelo agente.
- **Mordidas (Eating Animation):** `eatinganimation-1.21.0-6.0.1.jar` está em `mods/`. Os frames das comidas ainda dependem do gerador de `tools/pack_tools/gen_bite_frames.py`, que precisa ser conferido para a 1.21.1. **A portar** para o restante das comidas.
- **Resource packs de comida:** `EatAnimation Farmer's Delight's Compat` e `FreshAnimations_v1.10.4` estão em `resourcepacks/` como zip, sem ativação. A ativação é da fase F10 e exige a decisão do dono (regra de resource packs do AGENTS.md). **A portar** na F10.
- **Animação de braço (NotEnoughAnimations):** não há o jar na `mods/`. O caminho de "braço à boca" por ele não existe na 1.21.1 até ser portado. **A portar** ou substituir pelo caminho B.
- **Mini mod `sunlit_eating`:** não existe na instância. **A portar** (caminhos A e B). Depende da triagem dos mods próprios e do JDK de compilação.
- **Shoulder Surfing** (`ShoulderSurfing-NeoForge-1.21.1-5.3.1.jar`) está em `mods/`, então o teste de terceira pessoa já tem a câmera necessária.
- **Duração e lista da camada 3:** decisões do dono, em aberto.

## Regras de negócio

- Toda comida com animação completa precisa ter a keyframe `finished;` na animação `eat`. Sem ela, a comida não é consumida.
- Só itens canônicos recebem animação. Itens removidos ou duplicados nunca entram na lista.
- Assets novos de comida ficam em `kubejs/assets/food/`, nunca na lista de resource packs.
- Não se copia geo, textura ou animação de assets com licença ND. Só a estrutura pode ser usada como referência.
- Comidas novas de animação completa seguem a duração definida pelo dono (sugestão de 4 a 8 s).
- Cada fase só termina com teste feito pelo dono no jogo. O agente não roda o jogo nem cliente headless.

## Anotações

> Por que a terceira pessoa não funciona hoje? A animação completa é um modelo de primeira pessoa, preso à câmera. Em terceira pessoa o jogo desenha outro contexto de mão, e a animação é cancelada antes da comida ser consumida.

> Por que não só desligar a tecla? Isso devolve o comer normal em todas as câmeras, mas a primeira pessoa deixa de ter animação completa. Serve de quebra-galho, e a decisão é do dono.

**Ainda em aberto:** a lista de comidas da camada 3, a duração das animações novas, o JDK de compilação do mini mod para a 1.21.1, o formato exato do JSON do Player Animation Lib 2.0.4 e a substituição do NotEnoughAnimations. Também falta confirmar no jogo o comportamento do Immersive Eating 1.5.6 em terceira pessoa.
