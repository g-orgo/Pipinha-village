# Registro de decisões

Uma decisão por entrada, em ordem cronológica. As regras em vigor estão em `conventions.md` (ou em `AGENTS.md` para as regras obrigatórias); aqui fica o porquê.

## 2026-10-02: arquivo de opções do jogo protegido

- Uma alteração anterior removeu as configurações de resourcepacks e opções do usuário.
- O arquivo de opções atual (com `sunlit_overrides.zip`, Excalibur, FreshAnimations, Create Style etc.) é o estado correto e deve ser preservado.
- Decisão: nenhum agente altera esse arquivo sem autorização do dono. A regra vigente está em `AGENTS.md`.
- Autor: pedido do dono da instância.

## 2026-10-03: saves ativos regenerados quando a geração muda

- Mudanças de geração pedem a regeneração dos chunks antigos do save solo, preservando claims, jogadores e chunks com armazenamento do jogador.
- Procedimento e critérios em `conventions.md#regen-dos-saves-ativos`.

## 2026-10-06: Backup.zip substituído por Modpack.zip

- O pacote de distribuição passou a ser `Modpack.zip` na raiz da instância. Não se recria mais o `Backup.zip`.
- Regra vigente e nota de substituição em `AGENTS.md`.

## 2026-10-06: horta só com plantas do ano todo

- Culturas sazonais ficavam como "Cannot grow" fora de estação e deixavam vãos nas hortas.
- Decisão: só culturas que crescem em qualquer estação, e nada que esteja bloqueado no pack.
- Detalhes em `conventions.md#hortas`.

## 2026-10-09: pouco loot por andar

- Muitos baús em cada andar deixavam as cidades cheias de loot sem sentido.
- Decisão: no máximo 2 containers com loot por andar (3 em andar grande), baú ou barril primeiro.
- Detalhes em `conventions.md#baús-das-cidades`.

## 2026-10-09: terracota e concreto powder fora das cidades

- Terracota criava um "mar de rosa" sem variação, e o concreto em pó faz a casa desmoronar ao gerar.
- Decisão: toda terracota vira concreto com cor sorteada, e o concreto em pó nunca entra nas cidades.
- Detalhes em `conventions.md#casas-variação-de-material` e `conventions.md#nada-bloqueado-nasce-nas-cidades`.

## 2026-10-09: baú bônus com conteúdo fixo

- O kit inicial precisava ser o mesmo sempre, e o cantil novo já nasce vazio.
- Detalhes em `conventions.md#baú-bônus-e-kit-inicial`.

## 2026-10-10: mochilas fora dos baús das cidades

- Mochilas em baú de cidade distorciam o loot, e a mochila entra só no baú bônus.
- Detalhes em `conventions.md#baús-das-cidades`.

## 2026-10-10: fauna e moradores espaçados

- Muitos animais e moradores juntos deixavam as cidades lotadas e o coelho comia a plantação de cenoura.
- Decisão: um único ponto de spawn, com distância mínima entre grupos e quantidades reduzidas.
- Detalhes em `conventions.md#fauna-e-moradores-espaçados`.

## 2026-10-10: backups mantidos em uma cópia

- Cópias acumuladas ocupavam espaço sem uso.
- Decisão: só o backup mais recente fica em `backups/` e em `options.txt.bak-*`.
- Detalhes em `conventions.md#backups-manter-apenas-um`.

## 2026-10-14: coletor de lixo avançado removido do modpack

- O coletor avançado exigia RAM demais, então voltou ao coletor padrão do CurseForge.
- Decisão do dono. A regra vigente, com os arquivos de configuração, está em `AGENTS.md` (seção Modpack.zip).

## 2026-10-14: V-Minus desativado

- O mod recarregava os recursos uma vez por dimensão ao entrar no mundo, deixando o carregamento em 0% por cerca de 5 minutos. O Botania também avisa que ele quebra receitas customizadas.
- Decisão: desativar. Motivo completo em `conventions.md#mods-desativados`.

## 2026-10-18: durabilidade infinita com perda na morte

- Ferramentas e armaduras não gastavam com o uso e perdiam durabilidade só ao morrer, para o jogo ficar menos punitivo no dia a dia.
- Detalhes em `conventions.md#ajustes-de-gameplay`.

## 2026-10-18: velocidades de Puffish Skills reduzidas

- Os bônus de velocidade de parkour, aventura e farming estavam altos demais.
- Decisão: valores reduzidos e não devem voltar a subir.
- Detalhes em `conventions.md#ajustes-de-gameplay`.

## 2026-10-18: botões de baú do Quark com 9 slots e correção do sort

- Os botões precisam funcionar nos armários do Refurbished, que têm 9 ou 18 slots, e o sort falhava em silêncio com eles.
- Decisão: slot target em 9 e um mini mod próprio que corrige a aceitação de itens.
- Detalhes em `conventions.md#ajustes-de-gameplay`.

## 2026-10-18: villagers com iron golem e lareiras maciças

- Villagers só nascem em profissões que abrem loja do Sunlit, sempre com um iron golem e com espaço livre de 3 blocos de altura.
- Lareiras viraram chaminés maciças de tijolo, sem duto aberto nos andares.
- Detalhes em `conventions.md#fauna-e-moradores-espaçados` e `conventions.md#interiores-e-mobília`.

## 2026-10-24: mods de mapa e integrações desativados

- Havia mais de um mapa ativo e integrações que dependiam deles.
- Decisão: manter só o mapa do FTB Chunks e desativar JourneyMap, JMI, Xaero's World Map, ConstructionSticks e animal_pen (este último pelo dono em 2026-10).
- Lista completa em `conventions.md#mods-desativados`.

## 2026-10-24: conteúdo com cara de original

- Conteúdo novo que destoava do resto do pack (textos, ícones, layout) confundia o jogador.
- Decisão: todo conteúdo novo copia o padrão de um item equivalente que já existe no pack. Regra vigente em `AGENTS.md`.

## 2026-10-25: cada etapa de processamento soma valor

- Processar um insumo precisa compensar o trabalho de cada etapa, e insumo sazonal é mais difícil de conseguir.
- Decisão: cada etapa adiciona um acréscimo sobre o custo dos ingredientes (referência x1,25), maior quando o insumo é sazonal (+10% extra). O bônus sazonal de +20% da caixa de envio continua só para colheitas cruas. Produtos artesanais das máquinas da Society mantêm a fórmula original do pack.
- Exemplo: ovo cru 4 -> ovo frito 5; Bacon com Ovos 34 -> 35 e Arroz Frito 84 -> 85 em cascata.
- Ainda em aberto: `farmersdelight:fried_egg` vende por 20 em `globalRegistryExtraPrices.js`, mas pela regra seria 5.
- Detalhes em `conventions.md#preços-e-etapas-de-processamento`.

## 2026-10-26: profissão única e Especialidades por profissão

- O jogador segue uma profissão só (limite padrão 1, em `global.professionLimit(player)`); a Guilda vai vender vagas extras via `global.addProfessionSlots(player, n)` (guardadas em `persistentData.sunlitProfessionSlots`). Quem já tinha várias profissões antes do rework fica com elas; o cristal de reset é o caminho para escolher de novo.
- As 5 árvores de profissão (farming, husbandry, fishing, vinicultura, culinaria) ficam sempre desbloqueadas para todos; o login desbloqueia de novo as que saves antigos tinham travado. A Maestria volta a exigir uma skill de maestria em cada árvore, como no pack original.
- A profissão continua dando +50% de XP na árvore dela. O que muda por profissão são dois nós novos por árvore, Especialidade I e II (stages `specialty_<árvore>_1/2`); a II substitui os valores da I. Com mais de uma profissão vale a maior chance entre elas.
- Tabela (chance I / II), fonte da verdade em `global.SPECIALTY_PERKS`:
  - Lavoura: Fazendeiro +1 colheita 20/35%, semente extra 10/15%, na II terra arada por ele fica molhada +1 dia e replantio por clique com 25% de começar um estágio adiantado; Cozinheiro qualidade +1 15/30% (25/45% em plantas de ciclo longo, idade máxima >= 7); Dono de Vinícola +1 uva ao colher parreira 20/35%; Rancheiro ração 10/20%; Pescador minhoca 10/20% (2 na II).
  - Criação: Rancheiro +1 produto 20/30% e gêmeos 20% na II; Cozinheiro qualidade +1 20/35% e gêmeos 10% na II; Fazendeiro fertilizante 10/20%; Pescador e Dono de Vinícola +1 produto 5/10%.
  - Pesca: Pescador +1 peixe 20/35%; Cozinheiro qualidade +1 15/30%; Fazendeiro fertilizante 10/20%; Rancheiro e Dono de Vinícola +1 peixe 5/10%.
  - Vinicultura (barril, cuba e cuba antiga): Dono de Vinícola qualidade +1 20/35% e +1 garrafa 10/20%; Cozinheiro qualidade +1 10/20%; demais +1 garrafa 5/10%.
  - Culinária (panela): Cozinheiro +1 prato 15/25%; demais 5/10%.
- Motivo: o dono quer árvores compartilhadas com benefícios de classe, sem nada quebrado. A especialidade da casa ganha os números maiores; combinações sem ligação natural ganham um bônus genérico pequeno.
- Ainda em aberto: "colheitas que demorem mais para nascer" do Cozinheiro foi lido como bônus maior em plantas de ciclo longo, não como crescimento mais lento; confirmar com o dono. Mineração, aventura, parkour, maestria e livros não têm Especialidade.

## 2026-10-26: Árvore Mercantil (comum a todas as profissões)
- Nova categoria Puffish `society:mercantil` (Noções de Comércio, Pechincha I/II/III, Livro-Caixa em Dia e Balanço Fechado; 6 níveis, limite de 6 pontos).
- XP: vender na Caixa de Envio (básica ou inteligente) dá ao dono `round(2 * sqrt(valor))`, no máximo 1500 por venda; não alimenta a Maestria e não recebe o bônus de profissão.
- Desconto: Pechincha I/II/III = 10/15/25% nas lojas, só nos itens do ofício (grupos em `global.MERCANTIL_GROUPS`, itens em `sunlit_tools/mercantil_discounts.py`): Fazendeiro sementes caras, mudas, fertilizantes, forcado e desidratador; Rancheiro ração, cocho, balde, tesoura, scanner, ovos de spawn e saco de pato; Rancheiro e Cozinheiro Poção Milagrosa; Pescador varas, anzóis, boias, minhoca, radar, viveiro, defumador, caixa de pesca e minhocário; Dono de Vinícola sementes de uva do Vinicultor Errante; Cozinheiro açúcar, sal, garrafa, livro de receitas e marmitas.
- Como: o society_trading não tem evento nem preço por jogador, então cada troca ganha 3 cópias com desconto logo depois dela, liberadas por stage (`mercantil_<grupo>_<n>`, mantidos por `global.syncMercantilStages` no login e a cada 100 ticks). A troca original fica intacta, porque o Auto Trader descarta trocas com stage; quem tem desconto vê o preço normal e o preço com desconto lado a lado. Trocas com `stage_override` ganham um override exato por nível.
- Fora do desconto: trocas com stage_required/stage_removed/limit (não cabem dois stages), trocas abaixo de 10 spurs (arredondariam para o mesmo preço) e tudo da Guilda.
- Ainda em aberto: confirmar com o dono se ver os dois preços lado a lado é aceitável e se 10/15/25% está no tom certo.

## 2026-10-26: Cristais de profissão na Guilda

- **Cristal do Arrependimento: Profissões** (`society:crystal_of_regret_professions`) volta, vendido na Guilda por 16000. Ao usar: tira todas as profissões, reabre as missões de contrato (`ftbquests change_progress <p> reset <missão>`), ressincroniza o scoreboard do bônus de XP e os stages do desconto Mercantil. As vagas extras compradas ficam.
- **Cristal da Ambição: Profissões** (`society:crystal_of_ambition_professions`, o mesmo cristal em dourado): +1 vaga de profissão (`global.addProfessionSlots`). Preço sobe a cada compra: 8, 16, 32 e 64 sóis (32768/65536/131072/262144); depois da 4ª compra a troca some.
- Como o preço sobe: o society_trading não tem evento de compra, então o cristal conta como comprado na primeira vez que entra no inventário de um jogador (ganha a NBT `sunlit_slot_bought` e soma em `persistentData.sunlitProfessionSlotsBought`). A Guilda só mostra a troca com o stage `profession_slot_offer_<n>` da próxima compra; cada troca tem `limit: 1` para não comprar duas na mesma faixa com a loja aberta. Código em `kubejs/server_scripts/itemEvents/professionCrystals.js`.
- Ainda em aberto: confirmar com o dono os preços das vagas.

## 2026-10-26: XP Mercantil por relação com os NPCs

- A árvore Mercantil também sobe pela relação com os moradores, não só pela Caixa de Envio (pedido do dono).
- Presente entregue (shift + clique): amado 40 XP, gostou 25, neutro 10; não gostou e odiou não dão XP. Vale a mesma janela de presentes que já existia.
- Primeira interação do dia com cada NPC (conversa, presente, loja ou apresentação): 10 XP, controlado por jogador + NPC + dia em `persistentData.npcData.<npc>.dayLastMercantil`.
- Sem bônus de profissão e sem Mastery, igual ao XP de venda. Valores em `global.MERCANTIL_GIFT_XP` e `global.MERCANTIL_GREETING_XP` (`mercantilGlobals.js`).
- Ainda em aberto: confirmar com o dono se 10 XP por NPC/dia e 40/25/10 por presente estão no ritmo certo (nível 1 da árvore pede 400).

## 2026-10-26: Kaleidoscope e Farmer's Delight como conteúdo central de comida

- Item duplicado entre mods vira um item canônico em todo lugar onde o jogador o obtém (inventário, saída de receita, loot de bloco/baú/mob). Prioridade: Kaleidoscope (Cookery, depois Tavern), Farmer's Delight, `society:` (item do próprio pack), addons do FD (Respite, Brewin', Vintage, Cultural, Veggies, Miner's, Crabber's, Ocean's, Cuisine, Create Central Kitchen), resto.
- Item que o pack já remove (`global.removedItems`, ex.: cebola, massa crua e ração do FD, aveia do Vintage, fatias do CCK) nunca é canônico: o grupo cai para o próximo.
- Não convertidos, só unificados por tag: sementes de chá (cada uma planta um arbusto com cadeia própria), sementes de uva, sucos do Legendary Survival Overhaul (sede) e grupos sem membro Kaleidoscope/FD (geleias da Bakery, vinho tinto, manteiga etc.). Nenhum mod foi removido.
- Mapa em `kubejs/startup_scripts/globalCanonicalItems.js`; grupos e receitas em `server_scripts/recipes/normalizeDuplicateItems.js`.
- Ainda em aberto: esconder os duplicados no JEI (hoje aparecem e viram o canônico ao pegar).

## 2026-10-29: Botão do Replay Viewer no menu inicial

- **Problema**: o ReplayMod (jar `reforgedplaymod-1.20.1-0.3.1.jar`) injeta um botão de 20x20 (`GuiHandler$1`, texto `replaymod.gui.replayviewer`) na `TitleScreen` e calcula a posição dele na inicialização da tela, quando os botões vanilla ainda estão no lugar original. O FancyMenu reposiciona os botões depois (layout `title_screen`), então o botão ficava no meio, em cima do "Multiplayer".
- **Por que não dá para resolver no FancyMenu**: o FancyMenu 3.7.0 só reconhece botões vanilla por chave de tradução conhecida (`TitleScreenWidgetIdentificationContext`); o botão do ReplayMod não tem identificador universal, então não vira elemento `vanilla_button` do layout.
- **Por que não dá para resolver só no `config/replaymod.json`**: `mainMenuButton` (inclusive `RIGHT_OF_MULTIPLAYER`) também usa a posição dos widgets no init, antes do layout do FancyMenu. E o `GuiHandler$1` desenha lendo o próprio `getX()`/`getY()` a cada frame, sem se reposicionar.
- **Primeira tentativa (não funcionou)**: `kubejs/client_scripts/replayViewerButton.js` reposicionava a cada `ClientEvents.tick`. Esse evento não roda na tela inicial: `MinecraftClientMixin.kjs$postTickClient` sai antes quando `Minecraft.level`/`player` é nulo, e `ClientEvents.paintScreen` tem a mesma trava (`Painter.guiScreenDraw`). `ForgeEvents` só é registrado nos scripts de startup (`BuiltinKubeJSForgePlugin`, `ScriptType.isStartup()`).
- **Solução**: `kubejs/startup_scripts/replayViewerButton.js` registra `ForgeEvents.onEvent("net.minecraftforge.client.event.ScreenEvent$Render$Pre", ...)`. Antes de cada frame, ele procura o botão do ReplayMod em `screen.children()` (prefixo de classe `com.replaymod.replay.handler.GuiHandler$` ou o texto; o botão sem texto é o do menu, o "Sair do replay" da pausa tem texto e é ignorado) e o cola na coluna dos ícones do pack — `x` do botão de acessibilidade (202 à direita dos botões de 200) — na linha do "Multiplayer", centralizado na altura. Sem o botão de acessibilidade, usa `Multiplayer.x + 202`. Sem âncora, não faz nada.
- **Posição do FancyMenu**: o mixin `MixinAbstractWidget` guarda a posição em `customX/customY` e o `getX()`/`getY()` devolve esses campos quando não são nulos; `setPosition` só mexe no `x`/`y` vanilla. Por isso o script grava com `setPosition` e, se `getX()`/`getY()` ainda não baterem, também em `setCustomXFancyMenu`/`setCustomYFancyMenu`.
- **Rótulo vazio**: o botão de 20x20 da tela inicial tem mensagem vazia (`""`), então a comparação é por conteúdo (`label == ""`), nunca por `label.length`, porque o texto pode chegar como texto do Java ou do Rhino.
- **Conferência no jogo**: o script loga uma vez `[Sunlit] Botão do Replay Viewer: antes -> depois (tela ..., âncora ...)` no `latest.log`; se a linha não aparecer, o evento de render não chegou na tela.
- **Por que o `getX()` do FancyMenu serve de âncora**: o mixin `MixinAbstractWidget` guarda `customXFancyMenu`/`customYFancyMenu` e sobrescreve `getX()`/`getY()` com a posição do layout; `setPosition` não é sobrescrito. `VanillaWidgetElement.updateWidget()` só roda no init/resize da tela, então nada desfaz o reposicionamento a cada frame.
- **Armadilha do Rhino do KubeJS**: `const`/`let` dentro de bloco (principalmente dentro de `try`) estoura `redeclaration of var <nome>` em tempo de execução. Por isso o script usa `var` dentro da função do tick e de `widgetLabel`.
- **Teste fora do jogo**: `sunlit_tools/js_harness/run_replay_button.sh` roda o script com o Rhino do próprio mod contra uma tela inicial falsa com as posições do layout e dispara o evento de render (14 cenários: nome do evento, layout completo, sem acessibilidade, sem Multiplayer, resize, tela de pausa com o botão de sair do replay, tela nula, botão com outra classe, widget problemático, erro logado uma vez só, posição customizada do FancyMenu e log de confirmação).
- Ainda em aberto: teste no jogo (o botão precisa aparecer à direita do "Multiplayer", sem sobrepor nada).

## 2026-10-30: Clique no inventário abria a receita do JEI

- **Sintoma**: clicar com o botão esquerdo num item do inventário (ou da tabela de trabalho) abria a receita do JEI em vez de mover o item; o botão direito abria "mostrar usos" em vez de dividir o stack.
- **Causa**: os atalhos da categoria `jei.key.category.mouse.hover` ("JEI (Hovering With Mouse)") estavam no mouse — `key_key.jei.showRecipe2:key.mouse.left` e `key_key.jei.showUses2:key.mouse.right` (`options.txt` linhas 242 e 244). `InternalKeyMappings.<init>` monta um `JeiMultiKeyMapping` para `getShowRecipe`/`getShowUses` (o `R`/`U` **mais** esse segundo atalho), e `FocusInputHandler` dispara o lookup com o ingrediente sob o mouse — o que inclui o item de qualquer slot de GUI, não só a lista do JEI. O clique era consumido antes do slot, então o item não saía do lugar.
- **Decisão**: os dois atalhos de mouse ficam sem tecla (`key.keyboard.unknown`); o lookup continua só em `R`/`U` (`jei.showRecipe`/`jei.showUses`, categoria "JEI (Recipes)"). Novo padrão gravado em `sunlit_tools/options_canonical.txt` (`--save`) e refletido em `atalhos.md` (`--md`).
- **Não mexido**: `jei.cheatOneItem2`/`cheatItemStack2` também estão no mouse, mas só valem no modo cheat do JEI (desligado em survival).
- **Pendente**: teste no jogo (clique esquerdo move o item, botão direito divide o stack, `R`/`U` seguem abrindo receita/usos).

## 2026-10-30: Clique no inventário da cena abria a receita do EMI

- **Sintoma**: nas cenas do Cinematic (terminal de crafting), clicar com o botão esquerdo num item do inventário da cena abria a receita no EMI em vez de pegar o item; os cliques na lista do EMI continuavam corretos, e nada mudou ao tirar os atalhos de mouse do JEI.
- **Onde é**: o `latest.log` mostra `menu=CraftingTerminalMenu ... screen=SceneScreen` — é a cena do addon `sunlit_cinematic_toms`, não o inventário vanilla. Quem exibe receita ali é o **EMI** (a cena troca o livro Field Guide pela sidebar do EMI).
- **Diagnóstico**: `SceneEmiPlugin` registra `registry.addStackProvider(SceneScreen.class, ...)` — necessário para `R`/`U` sobre os itens do painel — devolvendo `new EmiStackInteraction(EmiStack.of(stack))`. No bytecode do EMI 1.1.24 esse construtor é `this(stack, null, true)`, isto é **`clickable = true`**, e `EmiScreenManager.mouseClicked` → `stackInteraction(...)` → `EmiApi.displayRecipes` **não consulta** `isClickable`. Como o provider reporta o painel inteiro, todo clique esquerdo sobre um item do inventário da cena virava "ver receita" e o evento era cancelado antes de chegar no slot.
- **Decisão**: (1) o provider passa a entregar interação **não-clicável** (`new EmiStackInteraction(stack, null, false)`) — o painel não é uma fonte clicável de receita; (2) o roteamento de mouse para o EMI fica restrito às colunas laterais (`SceneEmi.overSides(event.getMouseX())`), onde ficam índice, busca, favoritos e botões de página; o centro (gaveta/inventário e área de trabalho) volta a ser da cena. Teclado (`R`/`U`, busca) continua roteado como antes.
- **Build**: não há JDK na máquina; o jar é compilado no container `docker run --rm -v "$PWD":/mod -v sunlit-gradle:/root/.gradle -w /mod eclipse-temurin:17-jdk ./gradlew build --offline`.
- **Pendente**: teste no jogo (clique pega/coloca item na cena; `R`/`U` no item do painel segue abrindo receita/usos; cliques na lista/busca do EMI seguem funcionando).

## 2026-10-30: Cinematic cancelava a página de receita do EMI na cena

- **Sintoma**: na cena do terminal, clicar num item da sidebar do EMI não abria a receita; sem a página, o botão de preencher crafting com itens do terminal também não ficava acessível.
- **Diagnóstico**: `EmiApi.setPages` abre um `InventoryScreen` quando não há janela de contêiner; o addon troca por `SceneLookupScreen` carregando o `StorageTerminalMenu`. Esse menu é o `containerMenu` do jogador e a estação o aceita, então `Scene.answer` devolve `OURS` e o handler de abertura do Cinematic cancela a tela. O EMI segue sem `AbstractContainerScreen` e não abre nada.
- **Decisão**: mixin `CinematicEventsMixin` (HEAD de `CinematicClient$Events.onScreenOpening`, cancela o handler só para `SceneLookupScreen`). A janela substituta é consulta da cena, não a janela da estação; o resto do comportamento do Cinematic fica igual.
- **Pendente**: teste no jogo (clique esquerdo na sidebar abre receita; botão `+` da receita preenche o grid 3x3 da cena com itens do terminal; fechar a receita volta para a cena).

## 2026-10-30: Shift+clique do inventário da cena do terminal vai para a rede

- **Sintoma**: na cena do terminal de crafting, Shift+clique num item do inventário da cena não guardava o item no terminal.
- **Diagnóstico**: o `TerminalStation.quickMove` chamava o `quickMove` do Cinematic, que manda a ação `QUICK`; no servidor `MenuActions.quickMove` faz o QUICK_MOVE e, se nenhum slot da estação mudou, devolve o item ao slot do jogador. O `quickMoveStack` do Tom's empurra o item para a rede (`te.pushStack`), que não é slot, então o Cinematic sempre desfazia a parte do jogador (com risco de duplicar o item na rede).
- **Decisão**: o `TerminalStation.quickMove` usa o clique vanilla `QUICK_MOVE` no slot do menu (`slotClick(menuSlot, 0, true)`), o mesmo caminho da janela do próprio Tom's, e mantém a animação do item voando para a tela.
- **Pendente**: teste no jogo (Shift+clique no inventário da cena guarda a pilha inteira no terminal, item some do inventário e aparece no painel uma vez só, sem duplicar).

## 2026-10-30: slot de lixo na cena do terminal
- **Sintoma**: T não abria o slot de lixo; o E abre o terminal como cena do Cinematic e o TrashSlot só conhece `AbstractContainerScreen`.
- **Decisão**: o addon sunlit_cinematic_toms desenha o slot (textura `trashslot:textures/gui/slot.png`) e reaproveita a tecla `key.trashslot.toggle` e o `MessageTrashSlotClick`; estado de visível salvo em `config/sunlit_cinematic_toms_trashslot.txt`. TrashSlot é dependência opcional (referências isoladas em `TrashSlotBridge`).

## 2026-10-30: formato de distribuição
- **Decisão**: publicar pelo zip padrão do CurseForge (manifest + overrides) gerado por `sunlit_tools/export_curseforge.py`, não pelo `Modpack.zip` (que embarca os jars de terceiros e serve só para instalação manual). `local/`, mapas, caches e saves ficam fora; `dist/` não entra no `Modpack.zip`.

## 2026-11-03: XP Mercantil por contratos do Quadro de Recompensas
- Entregar um contrato (papel do Bountiful) no quadro também sobe a árvore Mercantil (pedido do dono).
- XP por raridade do papel: comum 40, incomum 60, raro 80, épico 100, lendário 150, em `global.MERCANTIL_BOUNTY_XP` (`mercantilGlobals.js`). Sem bônus de profissão e sem Mastery, igual às outras fontes da árvore.
- Como: o Bountiful não tem evento de conclusão. A entrega só acontece com clique direito no quadro segurando o papel, e esvazia a pilha; papel incompleto ou vencido fica intacto (conferido no bytecode de `BoardBlock.use` e `BountyData.tryCashIn`). O listener em `server_scripts/playerEvents/mercantil.js` guarda a pilha da mão e dá a XP um tick depois, só se ela estiver vazia.

## 2026-11-03: Dia mais longo via KubeJS, não Better Days
- O Better Days não está instalado (nem no manifest do pack): `config/betterdays-*.toml` são resíduos e editá-los não faz nada.
- `kubejs/server_scripts/sunlitLongerDay.js` segura o relógio 1 tick a cada 5 (0,8x) só entre os ticks 1300 e 12000: o dia claro passa de 10 min para cerca de 12 min 14 s. A noite não muda.
- Não desacelerar antes do tick 1300: máquinas, caixa de envio e contador de dias usam janelas de `dayTime` do tamanho do tick rate (até o tick 1200), e rodariam duas vezes.

## 2026-11-03: Replay de mundo solo carrega os IDs do save (mini mod `sunlit_replayfix`)
- **Sintoma**: replay gravado em singleplayer abria com blocos e entidades trocados (pato virava ovo de pato, barco com nome de morador) e dezenas de `Error executing task on Client` no log.
- **Causa**: cada mundo guarda seus IDs numéricos no `level.dat` (`fml.Registries`; pato é 448 no solo e 417 no `Nosso mapa`). O Forge só envia esse mapa a clientes remotos (`RegistryManager.generateRegistryPackets` devolve lista vazia em conexão local), então a gravação solo não o contém e o replay decodificava os pacotes com os IDs padrão do jogo.
- **Decisão**: `ReplayHandlerMixin` chama `GameData.injectSnapshot(snapshot, true, true)` com o mapa do `level.dat` no início de `ReplayHandler.setup()`, igual ao que o Forge faz ao abrir o mundo. Precisa ser em `setup()` porque voltar no tempo no replay limpa o level e o Forge reverte os registros. Ao fechar o replay, `GameData.revertToFrozen()`.
- **Limite**: o mundo gravado precisa existir em `saves/` (procura pelo nome da pasta e depois por `LevelName`); sem ele o replay continua quebrado e o log avisa. Replays de servidor não mudam.
- **Junto**: `showReplayWarningOnStartup = false` no `config/DistantHorizons.toml` (aviso informativo no chat) e removido `Distant_Horizons_server_data/REPLAY`, cache de LOD gerado pela tentativa quebrada.
- **Build**: `JDK=/caminho/jdk17 custom-mods/sunlit_replayfix/build.sh`, sem JDK na máquina usar o container `eclipse-temurin:17-jdk`.
- **Pendente**: teste no jogo.

## 2026-11-03: Herança de qualidade em panelas por automação e no keg (mini mod `sunlit_qualityfix`)

- O Quality Food guarda a qualidade dos pratos numa fila do bloco e só a lê no slot de resultado do jogador. Funil, braço do Central Kitchen e tigela na mão recebiam o prato sem qualidade e deixavam a fila atrasada. O mini mod lê a fila nesses caminhos, igual ao slot.
- O keg não tem suporte nenhum no Quality Food. O nível do lote usa a mesma conta da panela (o menor ingrediente é garantido, e o bônus médio pode subir) e fica no bloco, não no `FluidStack`: uma tag no fluido impediria juntar fluido igual e faria a bebida devolvida ao keg sumir.
- Fluido em cano continua sem qualidade (sopas do Central Kitchen em fluido, Create enchendo e esvaziando bebida): não há onde guardar sem mexer em cada receita.
- Bebida devolvida ao keg só abaixa o nível dele, para não virar forma de subir a qualidade de bebida comum.

## 2026-11-03: Animações de comida em terceira pessoa (mini mod `sunlit_eating`)

- **Fresh Moves**: a pack mantém `right_arm.rx = wraprad(right_arm.rx)`, então a rotação de braços e cabeça passa, mas posições, corpo e pernas são reescritos. **Decisão**: as poses só giram braços e cabeça, sem `bend`. Confirmado no jogo real: `rightArm.xRot` segue a animação e o braço aparece nas capturas.
- **NotEnoughAnimations continua ativo**: nos eixos que a animação define, o PlayerAnimator vence. Nada no config foi alterado.
- **Poses por dados, sem tabela por item**: `FoodPose` decide pelo item que sobra, pela classe e pelo nome. Item novo já entra sem manutenção.
- **Mordidas só em comida**: bebida fica sem frames, como as poções. Três itens com modelo 3D ficaram sem frames (`hearthandharvest:*marshmallow_stick`).
- **Primeira pessoa**: lista curta de 6 comidas, de 4 a 6,5 s, com modelo e animação próprios gerados em código, sem derivar dos assets do Immersive Eating (CC BY-NC-ND). Só o formato e os nomes de ossos seguem o addon.
- **A janela de 0,25 s entre `finished;` e o fim da animação é obrigatória**: com 0,05 s, a trava do addon ficou presa num teste em que a comida seguinte foi colocada na mão logo depois. As animações originais do addon também usam 0,25 s.
- **`ModifierLayer` nesta versão**: o construtor com modificadores não encadeia a lista e a camada fica inativa. Usar `addModifierLast`.
- **Verificação**: `sunlit_tools/headless_client/` roda o jogo real sem janela numa cópia isolada, então o crivo final não depende do dono.

## 2026-11-03: Dia mais longo lê o tempo pelo level data

- **Causa**: `overworld.getGameTime()` não existe para o Rhino, então o script dava erro a cada 5 ticks, logo depois do `setDayTime` e antes de enviar o pacote de sincronia.
- **Decisão**: usar `overworld.getLevelData().getGameTime()`, testado no jogo real. Relógio medido: 800 ticks de dia em 1000 ticks de servidor.

## 2026-11-03: Seed Maker não dá lucro na venda

- **Causa**: a máquina consome 3 colheitas e devolve 6 sementes, e as sementes valiam 8 mesmo depois do corte de preço das colheitas. 26 das 46 receitas com preço davam lucro (3 uvas valem 21, 6 sementes valiam 48), 31 contando o arredondamento de qualidade e estação.
- **Decisão**: manter a quantidade e baixar o preço da semente, porque quem planta não perde nada e quem só vende deixa de lucrar. O limite é calculado em `globalPriceBalance.js` para valer em receita nova e acompanhar mudança de preço da colheita.
- **Arroz é a exceção**: ele também é comida e vale o mesmo que a panícula, então manteve o preço e passou de 6 para 3 por operação.
- **Fator de etapas**: não se aplica. A semente não é produto processado, então saiu também do bônus de subprocesso do tooltip.
- **Pior caso no cálculo**: o bônus sazonal de 8% conta só na semente, porque as tags de estação das duas pontas nem sempre coincidem. Por isso várias sementes ficam 1 ou 2 moedas abaixo do limite simples (cevada vale 1).
- **Sem mudança**: saídas sem preço continuam sem preço (framboesa, berinjela branca e outras), e as 16 sparkstones (256) continuam abaixo das 3 sparkpods (300).
- **Ainda em aberto**: com a perk de mineração de x1,5 e sem perk de fazendeiro, as sparkstones valem 384 contra 300. A reciclagem já dá 6 sparkstones por sparkpod, então cortar só aqui não fecha esse caminho.

## 2026-11-03: Bônus sazonal das colheitas externas sem mudar o crescimento

- **Quem lê a tag**: o crescimento (`ModFertility.isCropFertile`) lê só a tag de **bloco**. A tag de **item** do Serene Seasons só alimenta a linha "Fertile Seasons" do tooltip e o bônus do pack (`global.getSeasonalMultiplier`). Conferido no bytecode do jar.
- **Planta já sazonal no próprio mod** (Kaleidoscope, Tavern, Youkai): o fruto recebe `sereneseasons:<estação>_crops` com a estação do bloco. O jar só marcava semente e bloco. Nada muda no crescimento e o tooltip diz a verdade.
- **Planta do ano todo ou árvore** (Hearth and Harvest, Cultural Delights, Farmer's Respite, mandrágora e udumbara do Youkai): o fruto recebe a tag própria `society:<estação>_bonus_crops`, lida só pelo bônus, com a estação da equivalente do pack. Marcar o bloco quebraria `conventions.md#hortas`, porque `parks.py` usa `culturaldelights:eggplants`, `hearthandharvest:blueberry_bush`, `raspberry_bush` e `farmersrespite:tea_bush`. A tag de item do Serene Seasons mostraria uma estação fértil falsa.
- **Duplicado conta as estações do item canônico**, além das próprias. Trocar uma pela outra tirava o bônus de `snowyspirit:ginger`, cujo canônico não tem tag.
- **Tomate**: `kaleidoscope_cookery:tomato_crop` ganhou primavera no bloco, porque o item e a semente canônicos já diziam primavera (herdado do Farmer's Delight) e a planta não crescia nela. É a única mudança de crescimento.
- **Estações sem equivalente direto, por escolha do agente**: framboesa e semente de girassol no verão, abacate no verão (como manga e banana), cereja na primavera (como `vinery:cherry`), rose hips e mandrágora no outono, udumbara na primavera. Para mudar, basta editar `bonusSeasonCrops` em `handleSeasonTags.js`.
- **Preço de processados não muda**: a tag própria não conta como insumo sazonal para o x1,46, porque a planta segue fácil de obter o ano todo. Processados e caixas seguem sem bônus de venda, como os do pack.

## 2026-11-03: Registro de textura fora da thread de render vai para a fila dela (`sunlit_texturefix`)

- **Causa**: o Puffish Skills registra 15 texturas de fundo das árvores (`ClientBackgroundTexture`, que é `Tickable`) na thread de rede, ao ler o pacote da categoria. O `TextureManager` não é thread safe, e isso corre com o tick dele na thread de render: `ConcurrentModificationException` cerca de 3 s depois de entrar no mundo.
- **Decisão**: mixin em `TextureManager.register` que, fora da thread de render, agenda o registro com `Minecraft.execute`. Vale para qualquer mod, sem depender do Puffish.
- **Verificação**: cliente sem janela, sem a correção: 2 crashes em 3 rodadas; com ela: 0 em 3, com as 15 texturas registradas pela fila. Corrida de threads: 3 rodadas reduzem o risco, mas não provam ausência absoluta.

## 2026-11-03: Trigo e castanha no bônus sazonal; panícula do FD com o preço da canônica

- `minecraft:wheat` (verão e outono, as estações do bloco) e `windswept:chestnuts` (outono) entraram em `bonusSeasonCrops`. Frutas do Pam e `atmospheric:dragon_fruit` estão em `globalRemovedItems`, então não precisam de tag.
- `farmersdelight:rice_panicle` passou de 20 para 5, igual à `kaleidoscope_cookery:rice_panicle`, para a qual ela é convertida.

## 2026-11-04: Animação completa em todas as comidas e nas duas câmeras

- **Decisão**: o pedido original do dono já era a mesma animação nas duas câmeras e em todas as comidas. A entrega de 2026-11-03 (poses de corpo e lista curta de 6) ficou aquém disso e foi corrigida. O caminho C de `docs/animacoes-de-comida.md` era marcado como caro sem medição; medido, custa cerca de 16 s de carregamento e nenhuma memória a mais, e a terceira pessoa é uma classe genérica.
- **Modelo por item**: o Immersive Eating escolhe o modelo pelo path, então 8 itens com nome repetido e tipo diferente mostram em primeira pessoa o modelo do dono do nome: `herbalbrews:black_tea`, `herbalbrews:green_tea`, `veggiesdelight:mashed_potatoes`, `windswept:lavender_tea`, `youkaishomecoming:espresso`, `youkaishomecoming:latte`, `youkaishomecoming:mocha` e `youkaishomecoming:mushroom_soup`. Em terceira pessoa cada um usa o próprio modelo (`<path>__<namespace>`).
- **Duração**: a primeira pessoa dura de 3 a 4,5 s nas geradas; a terceira pessoa segue o tempo de uso normal do item (cerca de 1,9 s).
- **Estado preso do addon**: uma animação `switchin` iniciada fora da primeira pessoa nunca termina e o addon recusa todo clique direito. `controller.stop()` sozinho não resolve: é preciso limpar `triggeredAnimation` (`ImmersiveEatingGuard`).

## 2026-11-06: Pose das comidas de mão e troca de item durante a animação

- **Cabo**: espetinho segura pela ponta de baixo à esquerda do palito (convenção dos ícones), o quinto final fica na mão. Osso por cor (claro e pouco saturado) só em itens com nome de carne com osso (`BONE_WORDS`, por termo inteiro): o teste só por cor pegava creme, arroz e pratos e virava a comida de ponta-cabeça. Sem cabo, a comida fica em pé com a mão no quarto de baixo.
- **Rotação**: no jogo, rotação z positiva leva +y para +x; a fórmula é `phi - 90 + inclinação`. Carne com eixo quase vertical não mostra o erro de sinal, espetinho diagonal mostra (sumia da tela).
- **Braço esquerdo**: além de escala 0 na animação, o osso nasce abaixado no modelo, porque o addon mostra a pose parada antes e durante a transição para a animação.
- **Troca de item**: o addon trava a hotbar; roda (listener HIGHEST) e teclas 1-9 (mixin em `KeyboardHandler`, prioridade 500) chamam `AnimationUtils.stopAnimationControl()`, o mesmo cancelamento do clique esquerdo. Com prioridade 1500 o bloqueio do addon rodava antes (testado).
- **Escopo do gerador**: itens já no mapa continuam no escopo, porque o inventário passou a marcá-los como completos.

## 2026-11-07: Potes, tigelas com ingredientes e colher visível (pedido do dono)

- **Potes**: maionese, conserva (`_preserves`), geleia (`_jam`, `_jelly`) têm ícone de pote com tampa e viraram o tipo `jar` (`jar_kind` em `gen_ie_foods_all.py`, 79 itens): a tampa sobe e sai antes do primeiro gole, depois quatro goles em 6 s. Antes eram mordidos como pão (`hand`) ou bebidos como caneca (`cup`). `mayonnaise_flask` virou garrafa. Conserva e geleia também são tomadas em goles, pelo mesmo pote; trocar por colher seria outra animação.
- **Pote na frente do punho**: centrado na mão, o antebraço aparecia dentro do pote vazio; o pote fica 4,5 unidades à frente.
- **Tigela e prato**: o conteúdo vinha das 3 cores mais comuns do ícone, que são a madeira da tigela e o contorno preto; daí o "monte de nada". Agora (`gen_ie_dishes.py`) a tigela é redonda em degraus, o caldo tem a cor do topo do ícone sem contorno nem tigela, e os pedaços vêm dos ingredientes da receita (cache `sunlit_tools/eating/dish_ingredients.json`, refeito com `python3 -I sunlit_tools/gen_ie_dishes.py --ingredients`) e do nome, por palavra inteira: carne em cubos com gordura, rodela de cenoura, cubo de batata, cogumelo com chapéu, macarrão em fios etc. Sem ingrediente conhecido, os pedaços usam as cores da comida no ícone. Os 5 pratos antigos de `gen_ie_foods.py` usam o mesmo modelo; o hash de referência foi atualizado (pão sem mudança).
- **Colher**: no repouso ela ficava atrás da parede da tigela e no mergulho atravessava o fundo (cabeça 10 unidades além da borda de trás). Agora a colher fica inclinada 30° na mão (como o garfo), aparece no repouso e na boca, e no mergulho gira para baixo e recua um pouco na mão (`UTENSIL_DIP`, `UTENSIL_DIP_POS`), com a cabeça pousando no meio do caldo. Pose achada por busca medindo a posição dos ossos.
- **Colher na pose parada**: o Immersive Eating esconde os ossos de `invisible` (`utensil`) no estágio de modelo parado, antes da animação (`hiddenInModelStage`); era a tigela sem colher do print do dono. Uma cópia da colher (garfo no prato, hashis no macarrão) fica apoiada no prato com o cabo sobre a borda (`utensil_rest`) e a animação a esconde desde o primeiro quadro, quando a mão pega a colher.
- **Escopo do gerador**: `--sample` reescreve o mapa só com a amostra e tira do escopo os itens marcados como completos no inventário. Para testar um item, use a geração completa (8 s).

## 2026-11-08: Dia claro de 15 minutos

- O dono pediu dia claro de 15 min (estava em cerca de 12 min 14 s com 0,8x).
- `sunlitLongerDay.js` agora segura o relógio em 9 de cada 25 ticks (0,64x), espalhados para nunca cair em dois ticks seguidos. A janela continua de 1300 a 12000, então máquinas, caixa de envio e contador de dias não mudam, e cada valor de `dayTime` continua aparecendo no máximo duas vezes, como antes.
- Conta: 1300 + 10700 / 0,64 = cerca de 18019 ticks de servidor, 15 min 1 s, conferido por simulação da mesma lógica. A noite continua com 10 min e o Serene Seasons segue em 24000 ticks por dia.

## 2026-11-09: slot de lixo invisível por causa do Replay Mod

- **Sintoma**: o slot do TrashSlot não aparecia em nenhuma tela (inventário, Curios), mesmo com a tela habilitada em `TrashSlotSaveState.json` e sem erro no log.
- **Causa**: a jGui do Replay Mod (`de.johni0702.minecraft.gui...MinecraftGuiScreen`) dispara um `ScreenEvent.Init.Post` logo depois de cada tela. O TrashSlot trata isso como tela sem contêiner e põe `currentContainerSettings = NONE`; ele só ignora classes `com.replaymod`.
- **Decisão**: mixin em `TrashSlotGuiHandler.onScreenInit` no `sunlit_replayfix` (já é o mod de convivência com o Replay Mod), cancelando para classes `de.johni0702.minecraft.gui`. Config de mixin separada e opcional, para o mod não quebrar sem o TrashSlot.
- **Build**: `build.sh` agora inclui eventbus 6.0.5, TrashSlot e Balm no classpath; sem JDK na máquina, rodar no container `eclipse-temurin:17-jdk` com `docker run -d`.

## 2026-11-09: limite de pontos acompanha os nós de Especialidade

- **Sintoma**: depois do rework de profissões, as árvores com Especialidade I/II tinham 2 nós a mais e o mesmo limite (`spent_points_limit`) e a mesma quantidade de níveis de antes; o dono notou ponto faltando em Criação.
- **Decisão**: cada árvore ganha um ponto (limite e nível) por nó novo. Farming, husbandry e fishing: 14 pontos (as 24 skills originais continuam sendo escolha de 12, como no pack original; os 2 extras são das Especialidades). Culinaria: limite 15, 14 níveis + 1 ponto da missão do Welcome = todas as 15 skills. Vinicultura: limite 15 e 15 níveis = todas as 15 skills (antes eram 12 níveis para 13 skills).
- Mining, adventuring, parkour, mastery, mercantil e books não ganharam nós e não mudaram.
- **Ainda em aberto**: XP dos níveis novos segue a curva de cada árvore (+4000 por nível); confirmar com o dono se o ritmo está bom.

## 2026-11-09: Colher levada pela mão e tigela cheia (pedido do dono)

- **Colher**: no mergulho a colher girava sozinha na mão (`UTENSIL_DIP`, -60° de rolagem) enquanto o braço quase parava; parecia a colher se mexendo e não a mão. Agora a colher nunca gira na pegada: só o braço tem keyframes. No mergulho o antebraço vira para dentro e o punho fica na borda direita, à vista; num passo de arrasto (`SCOOP_POS/ROT`) a mão puxa a colher pelo caldo e só então o pedaço aparece na colher e some da tigela. Garfo do prato e hashis mantêm a pose antiga (`FORK_DIP_*`). Uma pose com a mão à frente da tigela foi descartada: no jogo a mão saía da tela por baixo.
- **Ordem de desenho**: o GeckoLib desenha com profundidade, então quem esconde quem é geometria. A mão fica fora da borda e acima dela, e a cabeça da colher fica à esquerda do punho. Conferido no cliente sem janela, sem a mão cobrir a colher nem a colher atravessar a parede.
- **Tigela cheia**: caldo 0,8 mais alto (topo -3,1, 0,3 abaixo da parede), 16 pedaços espalhados até a parede (padrão girassol), 30% maiores, inclinados e afundados mais da metade (`SINK` por corte). Carne, cubo e cogumelo ganham uma gola de molho em volta, para o caldo parecer grosso. Uma versão com 27 pedaços e outra com 21 cobriam o caldo inteiro e foram descartadas. Pratos não mudaram (hash de referência igual); o hash de `clam_chowder`, `potato_soup` e `pad_thai` foi atualizado.

## 2026-11-09: carvão, carvão vegetal e gelo intercambiáveis nas receitas (pedido do dono)

- **Decisão**: carvão e carvão vegetal servem um no lugar do outro em toda receita que pede um deles; o mesmo vale para bloco de carvão e bloco de carvão vegetal (Quark). Gelo e cubo de gelo (Youkai's Homecoming) valem um pelo outro só em comidas e bebidas (sorvetes, picolés, coquetéis do Palm Bar, Mother Snow, affogato, creme, tofu gelado, raspadinha); construção, congeladores, compactação e o corte de gelo em cubos continuam como estavam.
- Saídas não mudam. Compactar e descompactar bloco de carvão/carvão vegetal e a moagem do Create de cada um ficam separados, para não haver receita em conflito.
- Não existe pó de carvão no pack. Carvão vegetal continua sem preço de venda (carvão é minério, 8; carvão vegetal sai de tronco e daria lucro fácil).
- Grupos e tags em `kubejs/server_scripts/recipes/normalizeEquivalentItems.js` e `kubejs/data/sunlit/tags/items/compat/{coal,coal_block,ice}.json`. Receitas sem schema no KubeJS 6 (Create, Botania, Let's Do, Youkai etc.) têm o JSON reescrito, porque `replaceInput` não age nelas.
- **Ainda em aberto**: `normalizeDuplicateItems.js` usa só `replaceInput`, então os grupos de duplicados não valem nas receitas de mods sem schema (panela do FD, Create, Kaleidoscope...).

## 2026-11-10: Só inglês (EUA) e português (Brasil) na lista de idiomas (mini mod `sunlit_langfilter`, pedido do dono)
- **Decisão**: a tela de idiomas mostra só `en_us` e `pt_br`. O mixin `LanguageManagerMixin` filtra o retorno de `LanguageManager.extractLanguages` (`m_118981_`), que monta a lista a partir do `pack.mcmeta` de todo pack a cada reload, então idiomas vindos de mods e resource packs também somem.
- Os arquivos de tradução dos mods ficam nos jars (só não aparecem nem carregam). Um `lang:` salvo fora da lista cai para `en_us` pelo próprio jogo.
- Mixin só no cliente (`"client"` no mixins.json), `displayTest="IGNORE_ALL_VERSION"`: servidor não precisa do mod.
- **Build**: `JDK=/caminho/jdk17 custom-mods/sunlit_langfilter/build.sh`, sem JDK na máquina usar o container `eclipse-temurin:17-jdk` com `docker run -d`.

## 2026-11-10: Dificuldade sempre Difícil e botão de mobs hostis ao lado dela (pedido do dono)
- **Decisão**: ninguém troca a dificuldade. Mundo novo nasce Difícil e travado (como antes); todo mundo, novo ou antigo, volta para Difícil a cada segundo se algo mudar (o `/difficulty` ignora a trava). Saves antigos não são travados no `level.dat`: o botão de dificuldade só fica cinza (`server_scripts/worldCreationLock.js`).
- No lugar da escolha de dificuldade, um botão 20x20 ao lado dela liga ou desliga o nascimento de mobs hostis: nas Opções dentro do mundo (dificuldade 110 + cadeado + botão, mesma largura da linha) e na aba Jogo de Criar Mundo (escolha gravada no mundo novo no primeiro load).
- A escolha fica em `server.persistentData.sunlitHostileSpawnsOff` (ausente = nascem). Desligado, mobs da categoria MONSTER são cancelados no `MobSpawnEvent$FinalizeSpawn` para NATURAL, CHUNK_GENERATION, SPAWNER, STRUCTURE, PATROL, REINFORCEMENT, JOCKEY e MOB_SUMMONED; ovo, comando, balde, dispenser, conversão e raid continuam. Mobs que já existem não somem.
- Textura com versão vanilla e Excalibur (autorizada pelo dono) em `kubejs/assets/kubejs/textures/gui/`, escolhida pelo pack selecionado; geradas por `sunlit_tools/gen_hostile_toggle_icons.py`. Teste fora do jogo: `sunlit_tools/js_harness/run_hostile_toggle.sh`.

## 2026-11-10: EMI sumia em todas as telas (terminal de crafting inclusive) depois do Hands-On Delight (mini mod `sunlit_handsonfix`)
- **Sintoma**: a sidebar do EMI não aparecia na cena do terminal de crafting do Tom's (nem em outras telas).
- **Causa**: o plugin EMI do Hands-On Delight 1.1.0 esconde as receitas de crafting dos pratos de tábua com `removeRecipes(r -> r.getCategory() == CRAFTING && ids.contains(r.getId()))`; `ids` é um `Set` imutável, cujo `contains(null)` lança NPE, e há receitas de crafting sem id. O NPE derrubava a recarga do EMI ("Critical error occured during reload" em `HandsOnEmiPlugin.java:45`), e com o EMI não carregado (`EmiScreenManager.isDisabled()`) a cena não desenha a sidebar.
- **Log escondido**: `config/logbegone.toml` filtra toda linha com "EMI", por isso nada aparecia no `latest.log`. Para diagnosticar, tirar "EMI" da lista só na cópia do cliente sem janela.
- **Decisão**: mixin `@Redirect` no `lambda$register$0` (static) do plugin troca o `Set.contains` por versão null-safe (id nulo não é prato da tábua). `@Pseudo` e `"required": false`: sem o Hands-On Delight o mod não faz nada.
- **Verificado**: cliente sem janela com o filtro de log desligado: antes, `EmiReloadManager.isLoaded()` ficava `false` por 10 min com o NPE; depois, `loaded=true disabled=false` e sem erro crítico.
- **Junto**: `kubejs/client_scripts/tooltips/addPriceTooltips.js#100` dava "redeclaration of var before" (Rhino, `const` em bloco) ao mostrar tooltip com bônus sazonal; virou `let`.
- **Build**: `JDK=/caminho/jdk17 custom-mods/sunlit_handsonfix/build.sh`, sem JDK na máquina usar o container `eclipse-temurin:17-jdk` com `docker run -d`.
