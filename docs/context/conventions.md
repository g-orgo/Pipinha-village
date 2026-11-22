# Convenções do pack

Regras que valem para o Pipinha's Village 1.21.1. Vieram da 1.20.1 e foram adaptadas. Quando a regra depende de mod ou formato que mudou, a nota diz como ficou. Item marcado **a portar** ainda não existe no código da 1.21.1 e precisa ser portado antes de a regra valer.

## Alto nível

O pack é de fazenda, comércio e vida na cidade. O jogador mexe em **saves** que já têm mundo gerado, então a primeira preocupação é não estragar o que ele construiu. Depois vêm as **cidades** (baús, casas, moradores, hortas), a **economia** (preços, etapas de processamento, lojas e profissões) e a **harmonização** entre mods, para que itens equivalentes entrem nas mesmas receitas, tags e lojas.

O código é em inglês, comentários incluídos. O texto para o jogador é em pt-BR e segue o tom original do pack. A 1.20.1 de origem só aparece na linha de crédito "baseado no Society: Sunlit Valley".

## Baixo nível

```py title:Ambiente
minecraft = "1.21.1"
neoforge = "21.1.265"
kubejs = "2101"                # scripts KubeJS para 1.21
render = ["Sodium", "Iris"]    # Embeddium e Oculus ficaram de fora
menu = "FancyMenu 3.9.1"
```

```py title:Formato de dados 1.21
recipe_folder = "recipe/"      # antes era "recipes/"
tag_folder = "tags/item/"      # tags de item
result_key = "id"              # resultado de receita; antes era "item"
item_extra = "components"      # antes era nbt (data components)
```

```py title:Caminhos e arquivos protegidos
tools_dir = "tools/"           # antes era `sunlit_tools/` (a porta ainda é a-portar)
tools = ["modcheck", "configport", "dataport", "kjsport", "lcport", "pack_tools"]
options_file = "options.txt"   # nunca alterar sem pedido do dono
server_files = ["servers.dat", "usernamecache.json", "usercache.json"]  # intocáveis
```

```py title:Modos de regen
modo_padrao = "--so-claims-estrito"      # desde 2026-11-11 (a portar na 1.21.1)
modos_antigos = ["--so-claims", "--apenas-forceload --so-predio", "--politica-solo"]
claim_max = 1000000000                   # max_claimed_chunks e max_force_loaded_chunks
```

```py title:Bônus sazonal
seasonal_tag = "sereneseasons:<estacao>_crops"   # planta sazonal no próprio mod
bonus_tag = "society:<estacao>_bonus_crops"      # colheita do ano todo ou de árvore
seasonal_bonus_crate = 0.08                      # caixa de envio, só colheita crua
```

```py title:Preços e etapas
step_factor = 1.35             # x1,35 por etapa desde 2026-10-29 (era x1,25)
seasonal_extra = 0.08          # acréscimo sazonal extra desde 2026-10-29 (era 10%)
```

```py title:Rhino (KubeJS)
forbidden_in_block = ["const", "let"]   # "redeclaration of var" em qualquer bloco aninhado, inclusive dentro de função
use_instead = "let no topo da função, atribuído dentro do bloco"   # detalhes em erros-comuns.md
time_call = "overworld.getLevelData().getGameTime()"   # getGameTime() não existe
```

## Regras de negócio

#### Saves e regen

- Regen de chunk de save ativo só roda com o jogo fechado, e sempre com backup antes. O backup vai para `saves/` com o nome do save, a versão e a data.
- Só o save `Solito solamente` é regenerado. O save `Nosso mapa` não entra nessa regra.
- Mantém-se sempre o chunk de cada jogador e o chunk da cama e do spawn dele.
- Mantém-se todo chunk com claim do FTB Chunks, com forceload incluso.
- Mantém-se o chunk que tem animal do jogador: carinho do Society, dono ou domado, golem feito pelo jogador, animal na guia, nome dado com name tag ou passageiro de um desses. NPC de cidade e nome gerado não contam.
- Jogador, cama, baú e tempo de chunk habitado não seguram nada no modo atual.
- Casa não pode ficar cortada. Quando um chunk é mantido, o prédio que cruza a borda também é mantido.
- O regen começa com `--dry` para conferir os números. Depois, é preciso informar quantos chunks foram preservados e apagados em cada save e onde ficou o backup.
- Nether e End não são tocados.
- Antes de apagar, o regen leva cada animal domado que está fora dos claims do dono para dentro deles (`move_pets.py`), num lugar seguro, com a âncora do Horseman junto. Animal do jogador sem dono vai para o claim mais próximo. Dono sem claim: o animal fica e o relatório diz.
- O regen termina mandando cada jogador para a cama com `send_to_bed.py`. Quem não tem cama fica onde está. Os animais não vão para a cama.
- A primeira entrada depois de um regen espera a geração em volta dos chunks com forceload, então pode demorar.
- O mapa de LOD do Distant Horizons (`data/DistantHorizons.sqlite`) sai do save antes do regen, senão mostra as cidades antigas de longe.
- Claim automático: quando um jogador real coloca bloco com block entity ou cama, o chunk ganha claim sozinho. Placa e estandarte não fazem claim, e abrir baú nunca faz (**a portar** em `kubejs/server_scripts/blockEvents/autoClaimChunk.js`).
- Casa cortada na borda de um claim se resolve depois, com jogo fechado, por `fix_cut_houses.py`, que vira o pedaço de fora em lote de grama no nível da rua. Restaurar o vizinho do backup não serve, porque o chão antigo fica em outra altura. Todo regen apaga de novo esses lotes (não têm claim) e a seed volta a gerar a meia casa, por isso o `clear` registra cada lote em `tools/pack_tools/lotes_limpos.tsv` e o `regen_chunks.py` mantém esses lotes em qualquer modo (2026-11-18: a meia casa do -642,522, limpa na 1.20.1, voltou após o regen de 13/11). Mesmo assim o `scan` roda depois que o dono jogar perto da base, para pegar casas cortadas novas.
- Backups são mantidos em uma cópia só. O anterior é substituído. Backups e caches de save nunca entram no `Modpack.zip`.
- Save convertido da 1.20.1 ou editado por ferramenta passa por `tools/saveport/sunrise_soil.py` com o jogo fechado e backup antes, senão a lavoura do Sunrise não cresce.

#### Cidades

- Todo baú comum de cidade tem um drop de mob, uma comida ou uma bebida (nunca as duas), `warm_string` e `cold_string`, um equipamento vanilla, um material e de 1 a 3 itens temáticos. O baú rico tem de 4 a 6 itens de qualquer nível, sem comida nem bebida.
- Create só aparece em baú de oficina e de depósito. Nenhum item sem uso prático entra no baú.
- Baú de cidade não repete item dentro do mesmo baú.
- No máximo 2 containers com loot por andar de cada construção, 3 se o andar tiver mais de 6 candidatos. Baú ou barril de verdade vem primeiro. Vale para todas as estruturas (**a portar** em `polish.py`, `rule_loot_cap`).
- Mochila nunca sai de baú de cidade. Ela entra só no baú bônus.
- Hortas usam só plantas que dão o ano todo no Serene Seasons: nabo, brócolis, couve-flor, alho, batata-doce e berinjela. Abóbora e melancia só como semente no baú. Batata e cenoura estão na blacklist. Alface e pimenta do Kaleidoscope só aparecem nas estações em que o jar as libera.
- Casas variam o material, para não repetir a mesma fachada. Terracota vira concreto com cor sorteada, e a tinta e o tema do bloco seguem o mesmo sorteio. Concreto em pó nunca entra nas cidades, porque faz a casa desmoronar ao gerar.
- Casas têm três variações de cor (`_c1` e `_c2`) além da original, trocadas por `recolor` ou `swap_material` (**a portar** em `houses.py` e `remodel.py`).
- Interiores: chaminé e lareira são maciças de tijolo, sem duto aberto nos andares. Escada tem bocas de alçapão. Móvel solto cai no chão (`lift_onto_ground`) e não flutua.
- Fauna e moradores são espaçados. Cada cidade tem um ponto de spawn, com distância mínima entre grupos e quantidades reduzidas. Villager só nasce em profissão que abre loja do pack, sempre com um iron golem e 3 blocos livres de altura acima dele.
- Coelho não pode ter acesso livre à horta de cenoura.
- Baú bônus tem conteúdo fixo: copper backpack, iron pickaxe e axe, 3 pães e cantil vazio. O kit inicial só é entregue se não houver baú bônus perto do spawn (**a portar** em `spawn_bonus_chest.json` e `addQuestbook.js`).
- Nada bloqueado nasce nas cidades. Itens em `global.removedItems`, `hiddenItems` e `stripTags` são limpos dos baús, e `itemcheck.BANNED` e `bad_item` / `bad_crop` valem na geração (**a portar**).
- Lost Cities roda com `generateSpawners` falso.
- Lost Cities roda com `streetGenerationMode = LEGACY` no `sunlit_cozy` (o traçado da 1.20.1: rua em volta de todo prédio). O `HIERARCHICAL_GRID_V1`, padrão do 8.4, não volta: deixa lote aberto 1 bloco acima da rua, quadra sem estrada e casa virada para o nada. O modo fica gravado no save (`data/LostCityWorldGenData.dat`); trocar num save jogado é com `tools/pack_tools/lc_street_mode.py`, jogo fechado e junto com o regen das cidades.
- Estrutura de mod de superfície não nasce dentro da cidade: ela entra em `avoidStructures` do `lostcities-server.toml` (gerado por `tools/pack_tools/lc_avoid_structures.py`, com `avoidFlattening = true`), e a cidade deixa a área dela no terreno natural. Depois de um regen, `fix_floating_structures.py scan` confere se sobrou estrutura flutuando nos chunks mantidos.

#### Gameplay e economia

- Durabilidade é infinita, e a morte custa durabilidade. A conta da durabilidade fica no script de ajuste de gameplay. Ferramenta da tag `SunlitWear` segue a mesma regra.
- Config `unbreakable` órfã não é usada.
- Todo animal é domável. Quem não tem doma própria usa a doma universal do Redomesticate: definição em `kubejs/data/society/redomesticate/taming/` e tag `#society:tameable/<grupo>` com entradas opcionais, gerados pelo `build_pet_guide.py` a partir do `content.json` do guia. O item de doma nunca é comida de cruza do animal, item da lista do `animalBreeding.js` nem item de uso do Society, porque a doma gasta o item e cancela o clique. Ficam fora peixes, monstros, NPCs, golens e o allay. Cada animal domável tem caixa no capítulo "Companheiros".
- Pegar galinha com a mão vazia e carregá-la na cabeça fica desligado: `chickenGliding = false` em `config/hearthandharvest-common.toml`. O `Grab Chickens` do Quark também segue desligado.
- ParCool 4.x tranca as ações numa árvore própria; no pack ela fica desligada (`enable_skill_tree = false` em `config/parcool-server.toml` e no `serverconfig` de cada save), porque a progressão de parkour é a árvore do Puffish, como na 1.20.1 (ParCool 3.4, sem árvore).
- ParCool: as opções da 1.20.1 (3.4) que não existem no 4.x ficam em `kubejs/startup_scripts/forgeEvents/parcoolBreakfallGuard.js`: rolagem só em queda de 3 blocos ou mais (`lowest_fall_distance_for_breakfall = 3.0`) e vault só no chão (`enable_vault_in_air = false`). As que têm equivalente: corrida rápida automática ao correr (`fast_run` input `ALWAYS` = `Auto`), cambalhota desligada (`trick_jump` available = false = `can_Flipping = false`), breakfall perfeito com janela de 5 ticks (`breakfall_just_time_input_tick = 5`). A animação em primeira pessoa fica ligada (`enable_first_person_view_animation = true` em `config/parcool-animation.toml`): no 4.x é ela que libera o giro de câmera do rolamento e do hang down, que a 1.20.1 tinha (`enable_camera_rotation_roll = true`). Config de servidor muda em `config/parcool-server.toml` e no `serverconfig` do Solito juntos.
- ParCool: o FOV não reage à corrida rápida (`kubejs/startup_scripts/forgeEvents/parcoolFastRunFov.js` tira o modificador `parcool:modi.fast_run` da conta do FOV). Sprint, poções e o resto da velocidade continuam abrindo o FOV como no vanilla.
- ParCool: no ar, clicar com o botão direito num bloco não usa o bloco (porta, alçapão, botão, alavanca, baú), porque o mesmo botão é o agarrar do ParCool (`kubejs/startup_scripts/forgeEvents/parcoolAirborneUse.js`). O item na mão continua funcionando (pôr bloco pulando, balde na queda), e escada, trepadeira, andaime, água, montaria, voo e elytra seguem como no vanilla.
- Velocidades de Puffish Skills foram reduzidas e não voltam a subir: `fast_feet` de 0,25 para 0,075, `quick_feet` de 0,2 para 0,1, `farming` de 0,05 para 0,03.
- Quark: o botão de chest tem slot target 9. O sort falhava em armário de 9 e 18 slots, então `sunlit_sortfix` corrige a aceitação de itens (**a portar**).
- Preço de colheita crua vem da etapa de processamento, não do item cru. Colheita crua recebe fator `/3` ou `/1,5`, e item raro segue sem mudança.
- Cada etapa de processamento soma valor sobre o custo dos ingredientes. A etapa usa x1,35 desde 2026-10-29 e o insumo sazonal leva acréscimo extra.
- Bônus sazonal da caixa de envio é de 8% desde 2026-10-29 (era 20%). Vale só para colheita crua com tag do Serene Seasons, na estação dela. Colheita do ano todo não recebe bônus.
- Produto processado não recebe bônus sazonal na venda, porque o peso sazonal já entra no preço pela etapa.
- Colheita de planta que cresce o ano todo usa a tag `society:<estação>_bonus_crops` (`bonusSeasonCrops` em `handleSeasonTags.js`). Ela dá o bônus, não muda o crescimento e não conta como insumo sazonal.
- Itens de mods externos entram na economia pela mesma regra dos itens do pack, com as exceções do arquivo de preços. Colheita externa entra em `EASY_CROPS`/`NORMAL_CROPS` de `globalPriceBalance.js`, e o item canônico recebe o preço do duplicado que substitui.
- Produto artesanal das máquinas da Society (conserva, barril, chá e sidra envelhecidos) segue a fórmula original do pack. Não recalcular esses preços pela regra das etapas.
- Saída do Seed Maker não é etapa de processamento. A venda de uma operação (3 colheitas) nunca passa do valor das colheitas. Conferir com `seed_maker_audit.py` ao mexer em receita ou preço (**a portar**).
- Preço de processado e de caixa segue sem bônus de venda. Tooltip mostra o bônus sazonal e o bônus de subprocesso só para item que tem esse bônus, sem texto genérico.
- Insumo vendável em loja do Mercantil custa `ceil(1,5 * valor de venda * quantidade)`. Insumo sem venda usa o preço unitário das lojas que já o vendem, em lotes maiores.
- Profissão é uma só por jogador, salvo vagas compradas. As árvores de profissão ficam desbloqueadas para todos. Árvore Mercantil vale para todas as profissões (ver `decisions.md`).
- Culinária, Vinicultura e demais árvores têm um ponto e um nível a mais por nó de Especialidade. Mining, adventuring, parkour, mastery, mercantil e books não mudaram.
- Preparo culinário gera XP repetível: `4` por item de comida/bebida produzido, `3` por corte confirmado na tábua e `1` por ação que coloca insumo numa estação culinária. O primeiro preparo de cada prato ainda paga ao Cozinheiro o bônus `15 + valor/10` (teto 120) e moedas, uma vez por prato por jogador; compras em loja não contam.
- Dificuldade fica travada em Difícil. Ninguém troca. Mobs hostis podem ser desligados pelo botão ao lado da dificuldade, sem apagar mobs que já existem.
- Mob hostil só nasce em caverna (overworld abaixo de y 50, afogado abaixo de y 30) ou em outra dimensão (`surfaceHostileSpawns.js`). Raid, ovo e comando continuam. Drop de mob que só aparecia na superfície sai de baú de loot.
- Dia claro é de 15 minutos: o relógio segura 9 de cada 25 ticks entre os ticks 1300 e 12000 (**a portar** em `sunlitLongerDay.js`, com o tempo lido por `getLevelData().getGameTime()`).

#### Harmonização e KubeJS

- Ao portar ou corrigir uma funcionalidade que já existia na 1.20.1, consultar primeiro o código correspondente da instância `../Society: Sunlit Valley/kubejs/` e preservar seu comportamento na 1.21.1, salvo decisão explícita do dono. Registrar nos docs as diferenças de API e as adaptações feitas; a origem é somente leitura.
- Itens equivalentes de mods diferentes entram nas mesmas receitas, tags e lojas. Todo insumo novo precisa de uso prático.
- Carne e peixe entram na tag da espécie real (`harmonizeMeatTags.js`): pato, ganso, peru, pelicano e casuar em `c:foods/raw_chicken`; búfalo, bisão e veado em `c:foods/raw_beef`; javali em `c:foods/raw_pork`; cabra e carré de cordeiro em `c:foods/raw_mutton`; peixe branco em `c:foods/raw_cod`, salmão e truta em `c:foods/raw_salmon`, atum inteiro em `c:foods/raw_tuna`. O mesmo vale para os cozidos (`c:foods/cooked_*`).
- Cada ingrediente tem uma família de tags sinônimas na 1.21.1 (`c:foods/x`, `c:x`, `farm_and_charm:x`, `forge:x` que sobrou da 1.20.1, tag do próprio mod), e todas recebem os mesmos itens (`harmonizeFoodTags.js`). Famílias: ovo cru (qualquer ovo de ave, inclusive os grandes e os da Society), ovo frito, cada carne crua e cozida, bacon, carne genérica, cada peixe, peixe genérico, leite pequeno (`society:small_milk`, garrafa), leite grande (`society:large_milk`, balde), qualquer leite (`c:drinks/milk` e afins), queijo, manteiga, e tags que só existiam na 1.20.1 (pão, pimenta, soja, morango, trigo). A família só ganha itens, nunca referência de tag, para não formar ciclo.
- Mod novo de comida: conferir se as carnes, peixes, ovos e leites dele estão em alguma família, e se as tags que as receitas dele pedem estão na lista de sinônimos.
- Prato que pede o item vanilla (`minecraft:chicken`, `minecraft:cod`, `minecraft:egg`, `minecraft:milk_bucket`, `farmersdelight:milk_bottle` etc.) passa a pedir a tag da família, só em receita com pelo menos dois insumos distintos (`normalizeEquivalentItems.js`). Assar, cortar ou moer um frango continuam dando produto de frango. Ovo de pata e de gansa nomeados no bolo de pata e de gansa continuam pedindo o próprio ovo.
- Tag genérica (`c:foods/raw_meat`, `c:raw_meat`) só tem carne de verdade. Inseto, perna de aranha, carne podre, hambúrguer vegano e pratos compostos saem dela.
- Recheio de rolinho de repolho e de asa de morcego é carne vermelha moída, vegetal ou cogumelo, nunca peixe.
- Perna de caranguejo de mod (`crabbersdelight:crab_legs`) e as do Quark valem nos pratos de caranguejo do Quark Delight.
- Mula do Vinery fica fora. No lugar entra a mula vanilla. `spawnWithMules` fica falso, e um `vinery:mule` que entrar no mundo vira mula vanilla com os mesmos dados. Não reaplicar patch no jar da Vinery.
- Carvão, carvão vegetal e blocos deles valem um pelo outro em toda receita. Gelo e cubo de gelo valem um pelo outro só em comida e bebida.
- Receita sem schema no KubeJS 6 (Create, Botania, Let's Do, Youkai etc.) tem o JSON reescrito, porque `replaceInput` não age nela. `replaceInput` só é chamado quando a receita cita o item exato.
- Idioma: a lista só mostra `en_us` e `pt_br`, filtrada por mixin no cliente. Os arquivos de tradução dos mods continuam nos jars.
- Rhino: `const` e `let` dentro de qualquer bloco aninhado (`if`, `try`, `for`), em qualquer função e tipo de script, dão `redeclaration of var`. Declarar no topo da função. Lista completa de armadilhas em [[erros-comuns]].
- `Map` e `Set` guardados em `global` podem chegar como lista em outro script. Testar `Array.isArray()` antes de chamar `.get()`. Dado que atravessa scripts vai como texto (`"moedas|porcentagem"`).
- Script de startup roda duas vezes por sessão (cliente e servidor). Script que multiplica preço precisa de flag de idempotência (`global.priceBalanceApplied`).
- `global.extractinatorRecipes` é lista de `{ input, output }`, não `Map`.
- Roupa vestível (armadura de pano, chapéu, Curios de vestir) de qualquer mod tem valor de temperatura do LSO em `kubejs/data/<mod>/legendarysurvivaloverhaul/temperature/items/`, na escala do próprio LSO (peça de 0,5 a 3,5; peito maior, bota menor). Lã, suéter, gorro e pele vão em `cold_resistance` (protege do frio); palha, boné, óculos escuros e roupa leve de trabalho vão em `heat_resistance`. Peças equivalentes de mods diferentes têm o mesmo valor (chapéu de palha 3,0, chapéu de chef 1,0). Mod novo com roupa entra nessa tabela na mesma entrega. Fantasia e máscara ficam neutras.
- A temperatura das peças conta na armadura vestida e nos slots do Curios (o próprio LSO soma os dois). O slot do Cosmetic Armor é só aparência e não protege (decisão do dono, 2026-11-20).
- Item quente ou frio (lanterna +1,5, lanterna de alma -1,5, qualquer item com `temperature` no LSO) conta pendurado no slot do Curios e segurado em qualquer mão, uma vez por pilha. O LSO sozinho não conta item de Curios na mão nem a mão secundária; `kubejs/server_scripts/curiosHeldTemperature.js` completa isso e reaplica os modificadores do Curios depois de entrar no mundo (2026-11-21).
- Roupa de qualquer mod veste também no slot equivalente do Curios: cabeça em `curios:head`, peito em `curios:body`, pés em `curios:feet` (`harmonizeClothingCurios.js`, regra automática sobre todo item vestível). Armadura de verdade fica fora: todo item `minecraft:` (couro, cota, ferro, ouro, diamante, netherite, tartaruga, cobre do VanillaBackport), Botania, Create, Aquaculture, Mapperbase e as peças avulsas da lista do script (casca de caracol, bota do Soul Sucker, elmo das marés, mochila do Quark, baldes de madeira). Mod novo com armadura entra nessa lista na mesma entrega. No Curios a peça não dá pontos de armadura, mas conta a temperatura do LSO. Calça não tem slot no Curios.
- Item vestido no Curios é peça a mais, nunca troca o visual da armadura: o `pipinha_curiosfix` desenha a roupa do Curios por cima da peça do slot normal (modelo um pouco maior quando o slot normal está ocupado) e impede o Simple Hats de esconder o capacete quando há chapéu ou chifre no Curios. Só o Cosmetic Armor troca o visual.
- Itens de mesma origem são unificados: canônico Kaleidoscope, depois Farmer's Delight, depois `society:`, depois addons do FD, depois o resto. Item que o pack remove nunca é canônico.
- Botões de mouse do JEI ficam sem tecla. Os lookups de receita e uso ficam só em R e U.

#### Mods fora do pack

- Mod desativado não volta sem registro em `decisions.md`.
- Saíram em 2026-11-12: Botania, Splendid Slimes e Splendid Cogs.
- Ficam na lista "fora" da migração: Radium, Sodium Options API, Create: Extra Gauges, Redecorate, Farmer's Cutting: Quark e PowerfulJS.
- Os mods da 1.20.1 que saíram antes (V-Minus, JourneyMap, JMI, Xaero's World Map, ConstructionSticks, animal_pen, Better Days) e as regras que dependem deles estão em `## Anotações`.
- Not Enough Animations saiu e foi trocada por Punchy Moves (2026-11-11).

## Anotações

> Adaptação do arquivo de convenções da 1.20.1 (553 linhas). Regras que dependiam de mods que não existem na 1.21.1 foram removidas, como listado abaixo.

**Dropadas por dependerem de mod que saiu do pack:**

- Regra de mapa duplo (JourneyMap, JMI, Xaero's World Map), dependente de mapa ativo; o FTB Chunks é o único mapa.
- Regra de `animal_pen` e de `ConstructionSticks`.
- Regra do V-Minus (recarga por dimensão): a causa era o próprio mod.
- Regra de Botania (receitas e Cluttered) e de Splendid Slimes e Splendid Cogs.
- Regra de Better Days: o mod não estava instalado, e `config/betterdays-*.toml` era só resíduo.
- Regra de Not Enough Animations em terceira pessoa, trocada por Punchy Moves.

**Ainda em aberto:**

- As regras de regen para o save convertido (F9) ainda não foram revalidadas na 1.21.1.
- Os itens **a portar** precisam de porta antes de valer, e a lista está em `state.md`.
- `farmersdelight:fried_egg` vende por 20 em `globalRegistryExtraPrices.js`, mas pela regra seria 5.
- `normalizeDuplicateItems.js` usa só `replaceInput`, então os grupos de duplicados não valem nas receitas de mods sem schema.
- Immersive Eating: confirmar se continua no pack antes de portar as animações de comida.

Data da regra: 2026-10-03 (regen), 2026-10-06 (baús, hortas), 2026-11-11 (claims e regen estrito), 2026-11-18 (animais para dentro dos claims).
