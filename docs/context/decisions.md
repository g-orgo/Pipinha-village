# Decisões

Um registro por decisão, em ordem cronológica. As regras em vigor estão em `conventions.md` (ou em `AGENTS.md` para as regras obrigatórias); aqui fica o porquê. As datas são as originais da 1.20.1, mantidas de propósito. Os registros de 2026-11-11 em diante são da migração 1.21.1.

## Herdadas da 1.20.1

#### 2026-10-02: arquivo de opções protegido
Uma alteração anterior removeu as configurações de resource packs e opções do usuário. O arquivo atual é o estado correto e deve ser preservado. Nenhum agente altera `options.txt` sem pedido do dono. Ver `AGENTS.md`.

#### 2026-10-03: saves ativos regenerados quando a geração muda
Quando a geração muda, os chunks antigos do save são regenerados, preservando claims, jogadores e chunks com armazenamento do jogador. Procedimento e critérios em `conventions.md`, seção Saves e regen.

#### 2026-10-06: Backup.zip substituído por Modpack.zip
O pacote de distribuição passou a ser `Modpack.zip` na raiz da instância. Não se recria mais o `Backup.zip`.

#### 2026-10-06: hortas só com plantas do ano todo
Culturas sazonais ficavam como "Cannot grow" fora de estação e deixavam vãos nas hortas. Só entram culturas que crescem em qualquer estação e nada bloqueado no pack. Detalhes em `conventions.md`, seção Cidades.

#### 2026-10-09: pouco loot por andar
Muitos baús em cada andar deixavam as cidades cheias de loot sem sentido. No máximo 2 containers com loot por andar (3 em andar grande), baú ou barril primeiro.

#### 2026-10-09: terracota e concreto em pó fora das cidades
Terracota criava um "mar de rosa" sem variação, e o concreto em pó faz a casa desmoronar ao gerar. Toda terracota vira concreto com cor sorteada, e o concreto em pó nunca entra nas cidades.

#### 2026-10-09: baú bônus com conteúdo fixo
O kit inicial precisa ser sempre o mesmo, e o cantil novo já nasce vazio.

#### 2026-10-10: mochilas fora dos baús das cidades
Mochila em baú de cidade distorcia o loot. Ela entra só no baú bônus.

#### 2026-10-10: fauna e moradores espaçados
Muitos animais e moradores juntos deixavam as cidades lotadas, e o coelho comia a plantação de cenoura. Um único ponto de spawn por cidade, com distância mínima entre grupos e quantidades reduzidas.

#### 2026-10-10: backups mantidos em uma cópia
Cópias acumuladas ocupavam espaço sem uso. Só o backup mais recente fica guardado.

#### 2026-10-14: coletor de lixo avançado removido
O coletor avançado exigia RAM demais, então voltou ao coletor padrão. Decisão do dono.

#### 2026-10-14: V-Minus desativado
O mod recarregava os recursos uma vez por dimensão ao entrar no mundo, deixando o carregamento em 0% por cerca de 5 minutos. O Botania também avisava que ele quebra receitas customizadas. Reativar exige nova decisão.

#### 2026-10-18: durabilidade infinita com perda na morte
Ferramentas e armaduras não gastam com o uso e perdem durabilidade só ao morrer, para o jogo ser menos punitivo no dia a dia.

#### 2026-10-18: velocidades de Puffish Skills reduzidas
Os bônus de velocidade de parkour, aventura e farming estavam altos demais. Os valores reduzidos não devem voltar a subir.

#### 2026-10-18: botões de baú do Quark com 9 slots e correção do sort
Os botões precisam funcionar nos armários do Refurbished, que têm 9 ou 18 slots, e o sort falhava em silêncio com eles. Decisão: slot target em 9 e um mini mod próprio (`sunlit_sortfix`) que corrige a aceitação de itens. **A portar.**

#### 2026-10-18: villagers com iron golem e chaminés maciças
Villagers só nascem em profissões que abrem loja do pack, sempre com um iron golem e com espaço livre de 3 blocos de altura. Lareiras viraram chaminés maciças de tijolo, sem duto aberto nos andares.

#### 2026-10-24: mapas e integrações desativados
Havia mais de um mapa ativo e integrações que dependiam deles. Decisão: manter só o mapa do FTB Chunks e desativar JourneyMap, JMI, Xaero's World Map, ConstructionSticks e animal_pen (este último pelo dono em 2026-10). Lista completa em `conventions.md`, seção Mods fora do pack.

#### 2026-10-24: conteúdo com cara de original
Conteúdo novo que destoava do resto do pack (textos, ícones, layout) confundia o jogador. Todo conteúdo novo copia o padrão de um item equivalente que já existe no pack. Regra vigente em `AGENTS.md`.

#### 2026-10-25: cada etapa de processamento soma valor
Processar um insumo precisa compensar o trabalho de cada etapa, e insumo sazonal é mais difícil de conseguir. Cada etapa adiciona um acréscimo sobre o custo dos ingredientes (referência x1,25, depois x1,35 desde 2026-10-29), maior quando o insumo é sazonal (+10% extra, depois +8% extra). O bônus sazonal da caixa de envio vale só para colheitas cruas. Produtos artesanais das máquinas da Society mantêm a fórmula original do pack.

Exemplo da época: ovo cru 4 para ovo frito 5; Bacon com Ovos 34 para 35 e Arroz Frito 84 para 85 em cascata.
**Ainda em aberto:** `farmersdelight:fried_egg` vende por 20 em `globalRegistryExtraPrices.js`, mas pela regra seria 5.

#### 2026-10-26: profissão única e Especialidades por profissão
- O jogador segue uma profissão só (limite padrão 1, em `global.professionLimit(player)`). Vagas extras são vendidas pela Guilda via `global.addProfessionSlots(player, n)`, guardadas em `persistentData.sunlitProfessionSlots`. Quem já tinha várias profissões antes do rework fica com elas; o cristal de reset é o caminho para escolher de novo.
- As 5 árvores de profissão (farming, husbandry, fishing, vinicultura, culinaria) ficam desbloqueadas para todos. O login desbloqueia de novo as que saves antigos tinham travado. A Maestria volta a exigir uma skill de maestria em cada árvore.
- A profissão continua dando +50% de XP na árvore dela. O que muda por profissão são dois nós por árvore, Especialidade I e II (stages `specialty_<árvore>_1/2`); a II substitui os valores da I. Com mais de uma profissão vale a maior chance entre elas.
- Tabela (chance I / II), fonte da verdade em `global.SPECIALTY_PERKS`:
  - Lavoura: Fazendeiro +1 colheita 20/35%, semente extra 10/15%, na II terra arada fica molhada +1 dia e replantio por clique com 25% de começar um estágio adiantado; Cozinheiro qualidade +1 15/30% (25/45% em plantas de ciclo longo); Dono de Vinícola +1 uva ao colher parreira 20/35%; Rancheiro ração 10/20%; Pescador minhoca 10/20% (2 na II).
  - Criação: Rancheiro +1 produto 20/30% e gêmeos 20% na II; Cozinheiro qualidade +1 20/35% e gêmeos 10% na II; Fazendeiro fertilizante 10/20%; Pescador e Dono de Vinícola +1 produto 5/10%.
  - Pesca: Pescador +1 peixe 20/35%; Cozinheiro qualidade +1 15/30%; Fazendeiro fertilizante 10/20%; Rancheiro e Dono de Vinícola +1 peixe 5/10%.
  - Vinicultura (barril, cuba e cuba antiga): Dono de Vinícola qualidade +1 20/35% e +1 garrafa 10/20%; Cozinheiro qualidade +1 10/20%; demais +1 garrafa 5/10%.
  - Culinária (panela): Cozinheiro +1 prato 15/25%; demais 5/10%.
- Motivo: árvores compartilhadas com benefícios de classe, sem nada quebrado. A especialidade da casa ganha os números maiores; combinações sem ligação natural ganham um bônus genérico pequeno. Mineração, aventura, parkour, maestria e livros não têm Especialidade.
**Ainda em aberto:** "colheitas que demorem mais para nascer" do Cozinheiro foi lido como bônus maior em plantas de ciclo longo, não como crescimento mais lento; confirmar com o dono.

#### 2026-10-26: Árvore Mercantil, comum a todas as profissões
- Nova categoria Puffish `society:mercantil` (Noções de Comércio, Pechincha I/II/III, Livro-Caixa em Dia e Balanço Fechado; 6 níveis, limite de 6 pontos). **A portar.**
- XP: vender na Caixa de Envio dá ao dono `round(2 * sqrt(valor))`, no máximo 1500 por venda. Não alimenta a Maestria e não recebe o bônus de profissão.
- Desconto: Pechincha I/II/III = 10/15/25% nas lojas, só nos itens do ofício (grupos em `global.MERCANTIL_GROUPS`, itens em `tools/mercantil_discounts.py`). Os grupos cobrem sementes caras, mudas, fertilizantes, ração, cocho, tesoura, varas, anzóis, minhoca, sementes de uva, sal, açúcar e garrafas, entre outros, de acordo com a profissão.
- Como: o society_trading não tem preço por jogador, então cada troca ganha 3 cópias com desconto logo depois dela, liberadas por stage (`mercantil_<grupo>_<n>`, mantidos por `global.syncMercantilStages` no login e a cada 100 ticks). A troca original fica intacta, porque o Auto Trader descarta trocas com stage. Quem tem desconto vê o preço normal e o preço com desconto lado a lado.
- Fora do desconto: trocas com stage_required/stage_removed/limit, trocas abaixo de 10 spurs e tudo da Guilda.
**Ainda em aberto:** confirmar com o dono se ver os dois preços lado a lado é aceitável e se 10/15/25% está no tom certo.

#### 2026-10-26: cristais de profissão na Guilda
- **Cristal do Arrependimento: Profissões** (`society:crystal_of_regret_professions`), vendido por 16000. Ao usar: tira todas as profissões, reabre as missões de contrato, ressincroniza o scoreboard do bônus de XP e os stages do desconto Mercantil. As vagas extras compradas ficam.
- **Cristal da Ambição: Profissões** (`society:crystal_of_ambition_professions`): +1 vaga de profissão. O preço sobe a cada compra: 8, 16, 32 e 64 sóis; depois da 4ª compra a troca some.
- O cristal conta como comprado na primeira vez que entra no inventário (NBT `sunlit_slot_bought`, soma em `persistentData.sunlitProfessionSlotsBought`). Código em `kubejs/server_scripts/itemEvents/professionCrystals.js`. **A portar.**
**Ainda em aberto:** confirmar com o dono os preços das vagas.

#### 2026-10-26: XP Mercantil por relação com os NPCs
- Presente entregue (shift + clique): amado 40 XP, gostou 25, neutro 10; não gostou e odiou não dão XP.
- Primeira interação do dia com cada NPC (conversa, presente, loja ou apresentação): 10 XP, controlado por `persistentData.npcData.<npc>.dayLastMercantil`.
- Sem bônus de profissão e sem Mastery. Valores em `global.MERCANTIL_GIFT_XP` e `global.MERCANTIL_GREETING_XP` (`mercantilGlobals.js`).
**Ainda em aberto:** confirmar se 10 XP por NPC/dia e 40/25/10 por presente estão no ritmo certo.

#### 2026-10-26: Kaleidoscope e Farmer's Delight como conteúdo central de comida
- Item duplicado entre mods vira um item canônico em todo lugar onde o jogador o obtém (inventário, saída de receita, loot). Prioridade: Kaleidoscope (Cookery, depois Tavern), Farmer's Delight, `society:` (item do próprio pack), addons do FD, resto.
- Item que o pack já remove (`global.removedItems`) nunca é canônico: o grupo cai para o próximo.
- Não convertidos, só unificados por tag: sementes de chá, sementes de uva, sucos do Legendary Survival Overhaul e grupos sem membro Kaleidoscope/FD. Nenhum mod foi removido.
- Mapa em `kubejs/startup_scripts/globalCanonicalItems.js`; grupos e receitas em `server_scripts/recipes/normalizeDuplicateItems.js`. **A portar.**
**Ainda em aberto:** esconder os duplicados no JEI (hoje aparecem e viram o canônico ao pegar).

#### 2026-10-29: botão do Replay Viewer no menu inicial
- **Problema**: o ReplayMod injeta um botão 20x20 na `TitleScreen` e calcula a posição dele antes de o FancyMenu reposicionar os botões vanilla. O botão ficava em cima do "Multiplayer".
- **Não resolve no FancyMenu nem no `config/replaymod.json`**: o botão do ReplayMod não tem identificador universal, e `mainMenuButton` também usa a posição do init.
- **Solução**: `kubejs/startup_scripts/replayViewerButton.js` registra `ForgeEvents` em `ScreenEvent$Render$Pre`. Antes de cada frame, cola o botão na coluna dos ícones, na linha do "Multiplayer". Só `ForgeEvents` roda na tela inicial; `ClientEvents.tick` não roda.
- **Armadilha do Rhino**: `const`/`let` dentro de bloco estoura `redeclaration of var`, então o script usa `var`.
- **Rótulo vazio**: o botão tem mensagem vazia, então a comparação é por conteúdo, nunca por `label.length`.
- **Conferência no jogo**: o script loga uma vez a posição antes e depois no `latest.log`.
**Ainda em aberto:** teste no jogo (o botão precisa aparecer à direita do "Multiplayer", sem sobrepor nada). Pelas regras, o teste é do dono.

#### 2026-10-30: cliques do inventário, do EMI e do Cinematic
- **JEI**: o clique esquerdo abria a receita e o direito abria os usos, porque os atalhos `jei.showRecipe2` e `jei.showUses2` estavam no mouse. Decisão: os dois atalhos de mouse ficam sem tecla; o lookup continua só em `R`/`U`. **A portar** o padrão em `options_canonical.txt`. Não mexido: `cheatOneItem2`/`cheatItemStack2`, que só valem no modo cheat.
- **EMI na cena do terminal**: o provider de `SceneScreen` devolvia interação clicável para o painel inteiro. Decisão: interação não clicável, e o roteamento de mouse para o EMI fica só nas colunas laterais (`SceneEmi.overSides`). **A portar** em `sunlit_cinematic_toms`.
- **Receita na sidebar cancelada**: o Cinematic cancelava a tela substituta do EMI, porque o `StorageTerminalMenu` era o menu do jogador. Decisão: mixin `CinematicEventsMixin` que cancela o handler só para `SceneLookupScreen`. **A portar.**
- **Shift+clique na cena**: o `quickMove` do Tom's mandava o item para a rede e o Cinematic desfazia a parte do jogador. Decisão: usar o clique vanilla `QUICK_MOVE` no slot do menu. **A portar.**
- **Slot de lixo na cena**: o TrashSlot só conhece `AbstractContainerScreen`. Decisão: o addon desenha o slot e reaproveita a tecla `key.trashslot.toggle`. TrashSlot é dependência opcional. **A portar.**
**Ainda em aberto:** testes no jogo destes cliques são do dono.

#### 2026-10-30: formato de distribuição em zip do CurseForge
A distribuição sai como zip de CurseForge (manifest e overrides), gerado por `tools/export_curseforge.py`. O `Modpack.zip` embarca os jars de terceiros e serve só para instalação manual. `local/`, mapas, caches e saves ficam fora. **A portar** o script para `tools/`.

#### 2026-11-03: XP Mercantil por contratos do Quadro de Recompensas
Entregar um contrato no quadro também sobe a árvore Mercantil. XP por raridade do papel: comum 40, incomum 60, raro 80, épico 100, lendário 150, em `global.MERCANTIL_BOUNTY_XP`. A entrega só acontece com clique direito no quadro segurando o papel completo e não vencido. O listener em `server_scripts/playerEvents/mercantil.js` dá a XP um tick depois, só se a mão estiver vazia. **A portar.**

#### 2026-11-03: dia mais longo via KubeJS, não Better Days
O Better Days não estava instalado: `config/betterdays-*.toml` eram resíduos. `kubejs/server_scripts/sunlitLongerDay.js` segura o relógio entre os ticks 1300 e 12000. Não desacelerar antes do tick 1300, porque máquinas, caixa de envio e contador de dias usam janelas de `dayTime`. **A portar.**

#### 2026-11-03: dia mais longo lê o tempo pelo level data
`overworld.getGameTime()` não existe para o Rhino, e o script dava erro a cada 5 ticks. Decisão: usar `overworld.getLevelData().getGameTime()`, testado no jogo real.

#### 2026-11-03: replay de mundo solo carrega os IDs do save (`sunlit_replayfix`)
- **Sintoma**: replay gravado em singleplayer abria com blocos e entidades trocados e dezenas de erros no log.
- **Causa**: cada mundo guarda seus IDs numéricos no `level.dat`. O Forge só envia esse mapa a clientes remotos, então a gravação solo não o contém.
- **Decisão**: `ReplayHandlerMixin` chama `GameData.injectSnapshot(...)` com o mapa do `level.dat` no início de `ReplayHandler.setup()`, e `GameData.revertToFrozen()` ao fechar. **A portar.**
- **Limite**: o mundo gravado precisa existir em `saves/`. Replays de servidor não mudam.

#### 2026-11-03: herança de qualidade em panelas por automação e no keg (`sunlit_qualityfix`)
O Quality Food guarda a qualidade numa fila do bloco e só a lê no slot de resultado do jogador. O mini mod lê a fila também no funil, no braço do Central Kitchen e na tigela na mão. O keg recebe o nível do lote no bloco, não no `FluidStack`, para não impedir o empilhamento de fluido igual. Fluido em cano continua sem qualidade. **A portar.**

#### 2026-11-03: animações de comida em terceira pessoa (`sunlit_eating`)
- **Fresh Moves**: a pack reescreve posições, corpo e pernas, então as poses só giram braços e cabeça, sem `bend`.
- **NotEnoughAnimations**: nos eixos que a animação define, o PlayerAnimator vence. Config não alterado. Essa mod saiu depois (ver 2026-11-11).
- **Poses por dados**: `FoodPose` decide pelo item que sobra, pela classe e pelo nome. Item novo já entra sem tabela.
- **Mordidas só em comida**: bebida fica sem frames, como as poções.
- **Janela de 0,25 s** entre `finished;` e o fim da animação é obrigatória. Com 0,05 s a trava do addon fica presa.
- **`ModifierLayer`**: o construtor com modificadores não encadeia a lista. Usar `addModifierLast`.
- **Primeira pessoa**: lista curta de comidas com modelo próprio gerado em código, sem derivar dos assets do Immersive Eating (CC BY-NC-ND).

#### 2026-11-03: bônus sazonal das colheitas externas sem mudar o crescimento
- O crescimento lê só a tag de **bloco**. A tag de item do Serene Seasons só alimenta o tooltip e o bônus do pack (`global.getSeasonalMultiplier`).
- Planta já sazonal no próprio mod (Kaleidoscope, Tavern, Youkai): o fruto recebe `sereneseasons:<estação>_crops`.
- Planta do ano todo ou árvore: o fruto recebe `society:<estação>_bonus_crops`, lida só pelo bônus. Marcar o bloco quebraria as hortas.
- Duplicado conta as estações do item canônico, além das próprias.
- Tomate: `kaleidoscope_cookery:tomato_crop` ganhou primavera no bloco, porque a planta não crescia nela. É a única mudança de crescimento.
- Estações sem equivalente direto foram escolhidas pelo agente e podem ser editadas em `bonusSeasonCrops` (`handleSeasonTags.js`). **A portar.**
- Trigo (verão e outono) e castanha (outono) entraram em `bonusSeasonCrops`.
- Preço de processados não muda: a tag própria não conta como insumo sazonal para o fator de etapa.

#### 2026-11-03: registro de textura fora da thread de render (`sunlit_texturefix`)
O Puffish Skills registra texturas de fundo na thread de rede. O `TextureManager` não é thread safe, e isso gera `ConcurrentModificationException` cerca de 3 s depois de entrar no mundo. Decisão: mixin em `TextureManager.register` que agenda o registro com `Minecraft.execute` quando chamado fora da thread de render. Verificado sem janela: 2 crashes em 3 rodadas sem a correção, 0 em 3 com ela. **A portar.**

#### 2026-11-03: Seed Maker não dá lucro na venda
- **Causa**: a máquina consome 3 colheitas e devolve 6 sementes, e as sementes valiam 8 mesmo depois do corte nas colheitas. 26 de 46 receitas davam lucro.
- **Decisão**: manter a quantidade e baixar o preço da semente. O limite é calculado em `globalPriceBalance.js` e acompanha mudança de preço da colheita.
- **Arroz é a exceção**: manteve o preço e passou de 6 para 3 por operação.
- **Fator de etapas**: não se aplica à semente, que saiu do bônus de subprocesso do tooltip.
- **Sem mudança**: saídas sem preço continuam sem preço, e as sparkstones continuam abaixo das sparkpods.
**Ainda em aberto:** com a perk de mineração de x1,5 e sem perk de fazendeiro, as sparkstones valem mais que as sparkpods.

#### 2026-11-03: qualidade de comida e bônus sazonal na caixa
Comida ganhou qualidade, e a caixa ganhou bônus sazonal de 20%, reduzido para 8% em 2026-10-29. Vale só para colheita crua.

#### 2026-11-03: `farmersdelight:rice_panicle` com o preço da canônica
Passou de 20 para 5, igual a `kaleidoscope_cookery:rice_panicle`, para a qual ela é convertida.

#### 2026-11-04: animação completa em todas as comidas e nas duas câmeras
- O pedido do dono já era a mesma animação nas duas câmeras e em todas as comidas. A entrega de 2026-11-03 ficou aquém e foi corrigida.
- Modelo por item: o Immersive Eating escolhe o modelo pelo path, então 8 itens com nome repetido mostravam o modelo de outro item. Em terceira pessoa cada um usa o próprio modelo (`<path>__<namespace>`).
- Estado preso do addon: uma animação `switchin` iniciada fora da primeira pessoa nunca termina. É preciso limpar `triggeredAnimation`.

#### 2026-11-06: pose das comidas de mão e troca de item durante a animação
- **Cabo**: espetinho segura pela ponta de baixo do palito. Osso só em itens com nome de carne com osso (`BONE_WORDS`, por termo inteiro).
- **Rotação**: no jogo, rotação z positiva leva +y para +x; a fórmula é `phi - 90 + inclinação`.
- **Braço esquerdo**: o osso nasce abaixado no modelo, porque o addon mostra a pose parada antes da transição.
- **Troca de item**: teclas 1-9 e a roda chamam `AnimationUtils.stopAnimationControl()`, o mesmo cancelamento do clique esquerdo.

#### 2026-11-07: potes, tigelas com ingredientes e colher visível
- **Potes**: maionese, conserva, geleia e similares viraram o tipo `jar`: a tampa sobe e sai antes do primeiro gole, depois quatro goles em 6 s.
- **Tigela e prato**: o conteúdo vem dos ingredientes da receita (cache `tools/eating/dish_ingredients.json`) e do nome, por palavra inteira. Sem ingrediente conhecido, usa as cores da comida no ícone.
- **Colher**: fica inclinada 30° na mão, aparece no repouso e na boca, e no mergulho gira para baixo com a cabeça no meio do caldo.
- **Colher na pose parada**: o addon esconde os ossos de `utensil` antes da animação. Uma cópia da colher fica apoiada no prato com `utensil_rest`.
- **Escopo do gerador**: `--sample` reescreve o mapa só com a amostra. Para testar um item, usar a geração completa.

#### 2026-11-08: dia claro de 15 minutos
O dono pediu dia claro de 15 min. `sunlitLongerDay.js` segura o relógio em 9 de cada 25 ticks (0,64x), espalhados para nunca cair em dois ticks seguidos. A janela continua de 1300 a 12000. A noite segue com 10 min. **A portar** junto com o script de 2026-11-03.

#### 2026-11-09: slot de lixo invisível por causa do Replay Mod
A jGui do Replay Mod dispara um `ScreenEvent.Init.Post` logo depois de cada tela, e o TrashSlot tratava isso como tela sem contêiner. Decisão: mixin em `TrashSlotGuiHandler.onScreenInit` no `sunlit_replayfix`, cancelando para classes `de.johni0702.minecraft.gui`. Config de mixin opcional. **A portar.**

#### 2026-11-09: limite de pontos acompanha os nós de Especialidade
Cada árvore com Especialidade ganhou um ponto (limite e nível) por nó novo. Farming, husbandry e fishing: 14 pontos. Culinaria: limite 15, 14 níveis mais 1 ponto da missão do Welcome. Vinicultura: limite 15 e 15 níveis. Mining, adventuring, parkour, mastery, mercantil e books não mudaram.
**Ainda em aberto:** confirmar com o dono se o ritmo de XP dos níveis novos (+4000 por nível) está bom.

#### 2026-11-09: colher e tigela cheia
- **Colher**: a colher nunca gira na pegada, só o braço tem keyframes. Num passo de arrasto a mão puxa a colher pelo caldo e só então o pedaço aparece na colher.
- **Ordem de desenho**: a mão fica fora da borda e acima dela, e a cabeça da colher fica à esquerda do punho, para nada esconder o outro sem querer.
- **Tigela cheia**: caldo mais alto, 16 pedaços espalhados até a parede, com gola de molho em carne, cubo e cogumelo.

#### 2026-11-09: carvão, carvão vegetal e gelo intercambiáveis nas receitas
Carvão e carvão vegetal servem um no lugar do outro em toda receita que pede um deles, e o mesmo vale para os blocos. Gelo e cubo de gelo valem um pelo outro só em comidas e bebidas. Construção, congeladores e compactação continuam como estavam. Saídas não mudam. Carvão vegetal continua sem preço de venda, para não dar lucro fácil com tronco.

Grupos e tags em `kubejs/server_scripts/recipes/normalizeEquivalentItems.js`. Receitas sem schema no KubeJS 6 têm o JSON reescrito, porque `replaceInput` não age nelas. **A portar.**
**Ainda em aberto:** `normalizeDuplicateItems.js` usa só `replaceInput`, então os grupos não valem nas receitas de mods sem schema.

#### 2026-11-10: só inglês (EUA) e português (Brasil) na lista de idiomas (`sunlit_langfilter`)
A tela de idiomas mostra só `en_us` e `pt_br`. O mixin `LanguageManagerMixin` filtra o retorno de `LanguageManager.extractLanguages`. Os arquivos de tradução dos mods ficam nos jars. Mixin só no cliente. **A portar.**

#### 2026-11-10: dificuldade sempre Difícil e botão de mobs hostis (pedido do dono)
- Ninguém troca a dificuldade. Mundo novo nasce Difícil e travado; todo mundo volta para Difícil se algo mudar (`server_scripts/worldCreationLock.js`). Saves antigos só ficam com o botão cinza.
- No lugar da escolha de dificuldade, um botão 20x20 liga ou desliga o nascimento de mobs hostis, nas Opções dentro do mundo e na aba Jogo de Criar Mundo.
- A escolha fica em `server.persistentData.sunlitHostileSpawnsOff`. Desligado, mobs da categoria MONSTER são cancelados no `MobSpawnEvent$FinalizeSpawn` para spawns naturais. Ovo, comando e raid continuam. Mobs que já existem não somem. **A portar.**

#### 2026-11-10: EMI sumia depois do Hands-On Delight (`sunlit_handsonfix`)
- **Causa**: o plugin EMI do Hands-On Delight usa um `Set` imutável com `contains(null)`, que lança NPE e derruba a recarga do EMI, então a sidebar não aparece.
- **Decisão**: mixin `@Redirect` null-safe no plugin. `@Pseudo` e `"required": false`: sem o Hands-On Delight o mod não faz nada. **A portar.**
- **Junto**: um `const` em bloco em `addPriceTooltips.js` dava `redeclaration of var`, virou `let`.
- **Log escondido**: `config/logbegone.toml` filtra toda linha com "EMI". Para diagnosticar, tirar o filtro só na cópia de teste.

#### 2026-11-11: portar o próprio pack para 1.21.1 por causa do Create Aeronautics
O pack passa a existir em 1.21.1 porque queremos o **Create Aeronautics**, que não existe para 1.20.1. A migração é um porte do próprio pack, não um pack novo: conteúdo da 1.20.1 é copiado e convertido, e a instância de origem fica só para leitura. Itens marcados **a portar** ainda não têm código na 1.21.1.

#### 2026-11-11: Artesã vende as máquinas do Create (pedido do dono)
- A Bibliotecária passou a se chamar Artesã. Os ids internos não mudaram, para não quebrar saves, quests e diálogos.
- Preço de cada máquina = custo dos ingredientes pela receita ativa, x1,35 por etapa em cascata, arredondado para uma moeda. Script: `tools/artisan_shop/create_prices.py`. **A portar.**
- Itens com Kinetic Blueprint só liberam com `boiler_room_complete`. Broca, serra e colheitadeira mecânicas custam 2 moedas ancestrais.
- Ficam de fora: variantes de cor, blocos decorativos, itens criativos e ferramentas que outras lojas já vendem.

#### 2026-11-11: regen só preserva claims; claim automático ao construir
- **Problema**: no modo antigo, todo baú de loot aberto contava como armazenamento do jogador e segurava o chunk para sempre.
- **Decisão**: `regen_chunks.py --so-claims-estrito` vira o padrão: só claim FTB (forceload incluso), animais do jogador e prédio que cruza a borda. Nada de jogador, cama, baú ou InhabitedTime.
- **Claim automático**: `kubejs/server_scripts/blockEvents/autoClaimChunk.js` faz o claim quando um jogador real coloca bloco com block entity ou cama. Placas, estandartes e abrir baú ficam de fora. **A portar.** Teste em `tools/js_harness/run_auto_claim.sh`.
- **Limites**: `max_claimed_chunks` e `max_force_loaded_chunks` = 1000000000, porque o FTB soma os extras do time.

#### 2026-11-11: contato de profissão no telefone
Quem segue uma profissão ganha uma loja a mais no telefone que facilita o ofício (cozinheiro: fornecedor de insumos que acompanha a estação). Lojas só de telefone, escondidas pelo `stage_required` `profession_<id>`. Insumo vendável custa `ceil(1,5 * valor de venda * quantidade)`. Itens não vendáveis usam o preço unitário das lojas que já os vendem, em lotes maiores. O Grocer segue o calendário das sementes do Market. **A portar.**

#### 2026-11-11: o que conta como prato no bônus de primeiro preparo
- Fazer um prato pela primeira vez dá XP ao Cozinheiro: `15 + valor/10`, teto 120, sem qualidade nem estação.
- Conta como prato: item de `global.cooking` com preço, fora caixas, insumos, fatias `*_slice` e bebidas alcoólicas. Chás, cafés, sucos e chocolate quente contam.
- Antiexploit: uma vez por prato por jogador; compra em loja não paga; prato posto numa estação e retirado não paga; pratos feitos antes da mudança não pagam retroativo.
- **A portar** em `global.cooking`.

#### 2026-11-11: carnes e peixes por espécie
- Pato não tinha receita (só caía em `forge:raw_meat`), e qualquer carne servia de recheio para rolinhos de repolho e de asa de morcego.
- Decisão: tag por espécie em vez de grupo genérico. Pato entra onde entra frango, bisão onde entra boi. Transformações de um insumo ficam por item, para o pato assado continuar sendo pato assado.
- `replaceInput` só é chamado quando a receita cita o item exato, porque ele também troca tags largas.
- Perna de caranguejo de mod e as do Quark valem nos pratos de caranguejo do Quark Delight. Perna de aranha continua nas receitas do Miner's Delight.
- **A portar** em `harmonizeMeatTags.js`.

#### 2026-11-11: Lithosphere, Punchy Moves e Spatial GUI; regen manda o jogador para a cama
- Lithosphere sobe a overworld para 576 blocos (`min_y` -64, altura lógica 512). Chunks já gerados mantêm o terreno antigo. O aviso "Ignoring heightmap data" é esperado.
- O regen termina mandando cada jogador para a cama com `tools/send_to_bed.py`, para acordar dentro de chunks mantidos. O primeiro login depois de um regen pode demorar.
- Punchy Moves entra no lugar da Not Enough Animations, que foi desativada pelo dono (animação em terceira pessoa duplicada).
- Spatial GUI é só cliente.

#### 2026-11-11: testes no jogo são do dono
Os agentes não rodam o jogo nem cliente headless. Verificação fica restrita a checagens leves sem o jogo, e o teste no jogo é feito pelo dono. Regra em `AGENTS.md`.

#### 2026-11-11: seed nova no Solito solamente por causa do Lithosphere
- Depois do regen estrito, o entorno da base nasceu todo oceano profundo. O Lithosphere troca o mapa de continentes, e com a seed antiga a base caiu no meio de um oceano. Regenerar daria o mesmo oceano, porque a geração é determinística.
- Decisão do dono: manter o Lithosphere e trocar a seed. Seed antiga `-2365142878615750770`, nova `3306540390856787928` (`level.dat` e `level.dat_old`), escolhida pelo avaliador `tools/seed_finder/find_land_seed.py` sem rodar o jogo.

#### 2026-11-11: mod de diagnóstico `sunlit_hangdump`
Se o servidor ficar 90 s sem completar um tick, grava a pilha de todas as threads em `logs/`. Só diagnóstico. A causa achada: o ALI cria entidades no start, o nó de corda do Brewery lê o bloco de (0,0), e o chunk de origem, apagado pelo regen, é gerado de forma síncrona. A geração ficava presa em `hashCode` recursivo dos records de função de densidade do Lithosphere. Correções: `regen_chunks.py` sempre mantém o 5x5 em volta da origem (motivo `origem_ali`); `tools/restore_origin_chunk.py` devolve o 5x5 de um backup; mod `sunlit_dfhashfix` memoriza o hash desses records e reutiliza o resultado de `HolderMapAllMixin`. **A portar.**

#### 2026-11-14: câmera própria do Punchy Moves desligada e sem tecla
- A câmera de terceira pessoa do Punchy Moves vem ligada por padrão e assume a posição quando o Shoulder Surfing entra no modo ombro pelo botão 5 do mouse. Teclas e mouse continuam guiados pela câmera do Shoulder Surfing, que fica invisível.
- `config/punchy_moves/camera.json` grava `enabled: false`.
- O atalho "Toggle Custom Camera" (tecla V) ficou sem tecla em `options.txt` e em `tools/pack_tools/options_canonical.txt`, com autorização do dono. Apertar o atalho religa a câmera e grava `enabled: true`.
- A câmera em terceira pessoa do pack é só a do Shoulder Surfing.

#### 2026-11-14: estações das plantações iguais às da 1.20.1 depois da troca de jars
- **Causa**: o Hearth & Harvest 1.4 passou a trazer tags próprias do Serene Seasons (mirtilo e framboesa na primavera e verão, algodão e milho no verão e outono, amendoim e treliça). Na 1.20.1 o jar não tinha tags e essas plantas cresciam o ano todo; no inverno o Jade mostrava "Cannot grow". O Youkai's Homecoming 4.x só gera as tags no datagen e o jar veio sem elas, então chá, pepino, café, uva vermelha, soja e feijão vermelho cresciam o ano todo.
- **Decisão**: `jarSeasonStrip` e `jarSeasonRestore` em `handleSeasonTags.js` tiram as tags do Hearth & Harvest (bloco e item) e devolvem as do Youkai com os valores do jar 1.20.1. O milho e a treliça de uva e lúpulo são novos na 1.21.1 e seguem o resto do mod, o ano todo.
- **Verificação**: tag efetiva calculada fora do jogo (jars, `kubejs/data` e o script) nas duas instâncias; nenhum bloco ou item ficou com estação diferente da 1.20.1.

## Anotações

> Registros de 2026-10-02 a 2026-11-03 foram resumidos. O texto completo continua na 1.20.1 de origem, somente para leitura.
**Dropadas por dependerem de mod que saiu do pack:**

- Decisão de mapa duplo (JourneyMap, JMI, Xaero's World Map): o FTB Chunks é o único mapa.
- ConstructionSticks e animal_pen.
- V-Minus e a recarga por dimensão.
- Botania, Splendid Slimes e Splendid Cogs (saíram em 2026-11-12, com registro próprio).
- Better Days, que nunca foi instalado.
- Not Enough Animations, trocada por Punchy Moves.
**Ainda em aberto:**

- Preços das vagas do Cristal da Ambição e o ritmo de XP da Mercantil e das Especialidades.
- Lista de mods "fora" da migração pode mudar conforme a checagem avança.
- Os registros com **a portar** precisam de porta na 1.21.1 antes de valer.
