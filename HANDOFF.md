# HANDOFF: migração para 1.21.1

Fonte única de progresso da migração. Plano completo: `docs/migracao/PLANO.md`.
Origem (só leitura): `../Society: Sunlit Valley`.

## Decisões do dono (2026-11-12)

- Botania, Botania Seeds, Splendid Slimes e Create: Splendid Cogs saem do pack:
  quests, ofertas de loja e receitas ligadas a eles são removidas.
- O save "Solito solamente" vai ser convertido numa CÓPIA (F9); o original não é tocado.
- Versionamento: branch `1.21.1` do Pipinha-village (worktree `/var/home/Orgo/Documentos/Pipinha-village-1.21.1`).

## Decisões do dono (2026-11-13)

- Motivo da migração: a 1.21.1 existe porque o dono quer o **Create Aeronautics**, que não existe para 1.20.1.
  Todas as docs reescritas citam isso. ATENÇÃO: o Aeronautics ainda NÃO está em `mods/` (só aparece como
  nome de modpack em `modpacks_comparados.tsv`); instalar, conferindo compatibilidade com Create 6.0.10.
  FEITO (2026-11-13): Create Aeronautics bundled 1.3.2 (traz aeronautics, simulated, offroad), Aeronautics
  Camera Sync 1.4.0 e Sable 2.0.6 (Modrinth, sha512 conferido); High Seas 0.2.2 (CurseForge, baixado pelo dono).
  ranges.py sem problema novo. mixscan: mixins de compat do Sable miram ShoulderSurfingImpl/client.ObjectPicker,
  que o Shoulder Surfing 5.3.1 renomeou; olhar no latest.log se só viram WARN ou se quebram a câmera.
- Mods próprios (custom-mods/ + sunlit_cinematic_toms): triar um por um. Se o bug ainda existe na 1.21.1,
  portar para NeoForge ou refazer em KubeJS; senão fica de fora. Mostrar a lista ao dono antes de portar.
- Docs: trazer todas reescritas como Pipinha's Village 1.21.1 (atalhos.md, README/READ_FIRST/LEIA-ME,
  REGRA_NAO_MODIFICAR_OPTIONS.md, docs/animacoes-*.md, docs/PUBLICAR.md, docs/context como índice novo).
- `keybinding presets`: trazer e conferir se os atalhos existem na 1.21.1; não ativar preset nem tocar options.txt.
- Changelog do menu: reescrever para o Pipinha's Village 1.21.1, com a linha de crédito.
- Funções desligadas no port do KubeJS (cabeças no minimapa, noSneakEating, fertilizante do golem de feno,
  status de 21 itens em modifyItems.js): recriar o que tiver caminho; listar ao dono o que não tiver.
- Tapper da wise oak: passa a dar um item equivalente de mod instalado; receitas e lojas da lótus negra mudam junto.
- Mod `society` (F7): reimplementar loot das vilas e textos (EmbersTextAPI) em KubeJS/datapack; o patch de
  serialização só se o bug ainda existir.
- Página do pinguim no almanaque: remover de vez, junto com os links para ela.
- Tela de créditos: barra de rolagem transparente, igual ao changelog do menu.
- Resource packs (autorizado): no options.txt, trocar cada zip 1.20.1 pela versão 1.21.1/equivalente na mesma
  posição e tirar os que não existem. Remover da pasta os packs copiados e não ativados (Quark Programmer Art.zip,
  longwing_nuker.zip).
- Mundo principal: a cópia convertida do "Solito solamente" (F9). "Mapa solo" é só mundo de teste
  (regenerado em 2026-11-13; backup em `backups/Mapa solo - antes do regen 2026-11-13.tar.gz`).
- Entrega (F11): ao terminar e testar, a 1.21.1 vai para a `main` e sai um Modpack.zip novo; a 1.20.1 fica
  guardada numa branch própria. Exige confirmação do dono no momento de mexer na main.

## Feito

- F0/F1: instância criada, 364 mods, boot limpo confirmado pelo dono (2026-11-12).
- Checagens leves: `tools/modcheck/` (ranges.py, mixscan.py, modids.txt).
- F4 dados (2026-11-12): `tools/dataport/port_data.py` (idempotente) gera `kubejs/data` e os 3 packs
  da Moonlight no formato 1.21; tags forge->c por tipo; referências a mods que saíram podadas de
  tags/receitas/loot. Relatório: `tools/dataport/REPORT.md`. Sobra para a F8: 988 JSON (quase todos
  paletas do Lost Cities em sunlit_towns) com blocos cfm/redeco/botania/splendid_slimes.

- F3 configs (2026-11-12): `tools/configport/port_configs.py` (idempotente) mescla valores antigos nos
  configs gerados da 1.21.1, copia conteúdo do pack (portable_blueprints, easy_npc skins/presets, jei, xaero).
  Relatório `tools/configport/REPORT.md`. Pendente: `config/relics/**` (formato pode ter mudado) e ~100
  arquivos "manual" listados no relatório (logs, png, mixins do modernfix: ignorados de propósito).

## Em andamento

- F5 recon pronto: `tools/kjsport/API_DIFF.md` (8 eventos e 13 classes Java ausentes; 252 usos de NBT;
  2048 ids de namespaces ausentes). Renames comprovados nos jars: ForgeEvents.onEvent->NativeEvents.onEvent,
  EntityEvents.hurt->beforeHurt, ItemEvents.tooltip->modifyTooltips, JEIEvents.addItems/hideItems/
  removeCategories->RecipeViewerEvents.addEntries/removeEntries/removeCategories, highPriorityData->generateData.
- F5a pronto: scripts copiados para `kubejs/`, renames mecânicos, sintaxe Rhino 2101 OK (374/374).
  NÃO rodar de novo `tools/kjsport/mechanical.py` (regenera do OLD e apaga o port manual).
- API verificada (javap/strings): `tools/kjsport/API_NOTES.md`.
- mechanical2 pronto (370 linhas de mods removidos, hunger->nutrition). Lotes em `tools/kjsport/batches.json`
  com ordem comum `tools/kjsport/BATCH_ORDER.md`. Em curso: startup-01..03, server-globals;
  a seguir server-01..06. Também em curso: C1 (addAdvancedTooltips + minimapIcons); C2 (addPriceTooltips +
  helper `global.getAttributeMultiplier(entity, id)` em 4 arquivos).
- Lotes fechados (2026-11-12, sintaxe OK em cada um): startup-01, startup-03, server-globals A e B, C1.
  Parciais com resto já despachado: startup-02 -> startup-02b/02c; C2 -> client-c2b.
  Em curso: server-globals C, server-01(+06), server-02..05.
  Decisões novas: `000_port_runtime.js` (priority 10000) e `000_port_quality.js` (qualidade do Quality Food
  2.x é o componente `quality_food:quality`; helpers `global.getQualityLevel/setQualityLevel`).
  Funções desligadas até agora (avisar o dono): ícone padrão do minimapa sem cabeças (FTB Chunks sem
  EntityIcons), bloqueio de beber fluido agachado (noSneakEating), fertilizante do golem de feno (mod ausente),
  alcance de bloco do NeoForgeMod (no-op). Sono na Skull Cavern usa setProblem.
  Relatórios que os operadores não puderam gravar: o resumo está aqui e no histórico da sessão.
- Fechados depois (sintaxe OK): startup-02b, startup-02c, client-c2b, client-tooltips, server-01(+06),
  server-02, server-03. server-04 refeito como 04a (npcs/player) e 04b (receitas); server-05 refeito como
  05x e 05y (o primeiro analisou a instância antiga por engano; a antiga foi conferida e está intacta).
  Mais funções desligadas: tag nos papéis do Bountiful (Bountiful 8 usa componentes), escrita na prancheta
  do fish pond (create clipboard), fertilizante Dew Drop. Itens a olhar no jogo: tooltips de preço/moeda,
  textos flutuantes (placar, monitor), chave do carro, plushies, aposta da corrida de porcos, anzol na
  caixa de pesca, nome do taco de fumaça, `hasBobber` lendo customData da vara.
- A fazer depois do 1º log: limpar dados ainda ligados a mods que saíram (ex.: `kubejs/data/cozycafe/menu/farmlife/*.json`,
  pools do Bountiful, processos com ids de splendid_slimes/farmlife/botania): `grep -rl` em `kubejs/data` e packs.
- Mods que mudaram de id na 1.21.1: `numismatics_utils` -> `numismaticsutils` (já trocado em banker.json e
  addTooltips.js; falta `config/gnetum.json`), `largemeals` -> `large_meals` (dados já mapeados pelo port_data),
  `bonsaitrees3` -> `bonsaitrees4` (formato a conferir). `kubejs/assets/` ainda tem pastas com os ids antigos
  (largemeals, numismatics_utils, bonsaitrees3, forge) e de mods que saíram (botania, farmlife, splendid_slimes,
  hamsters, liltractor, croptania, legendarycreatures...): renomear/remover na F10.
- Regra nova no BATCH_ORDER: o shell dos operadores abre na instância antiga; toda ordem usa a raiz nova.
- Depois: resto do client_scripts, um operador por lote do batches.json (startup e server), resto do client, e o dono abre
  o jogo para o agente ler `logs/kubejs/*.log`.

- Options (2026-11-12, autorizado pelo dono): `options.txt` recebeu o padrão do Sunlit
  (`../Society: Sunlit Valley/sunlit_tools/options_canonical.txt`), inclusive os packs; `version` mantido (3955).
  Os 31 packs `file/` foram copiados para `resourcepacks/`; os 18 de formato antigo estão em
  `incompatibleResourcePacks` para carregarem na 1.21.1. Backup do anterior só na sessão (era o padrão do jogo).

- 1º launch do dono (2026-11-12): correções em curso a partir de `logs/kubejs/startup.log` e `client.log`.
  Feito: JEIEvents -> JEIAddedEvents; globals do client -> `global.runtime`; fragmentos quebrados pelo
  mechanical2 (casks, husbandry galliraptor, fisher `liked`, seedMaker, manaClock, skullCavernBroken);
  registro: fastToEat -> eatSeconds(0.8), dropSeed(false) -> noSeeds(), tiers sem `level`
  (setIncorrectBlocksForDropsTag), Ingredient.custom -> prismatic_shard, craftingRemainder.
  Desligado em modifyItems.js (sem API no KJS 7): maxDamage/digSpeed/attackDamage de 21 itens (dono avaliar).
  Assets do jar `society-1.22` (mod que não existe na 1.21.1) copiados para `kubejs/assets` sem sobrescrever:
  1546 arquivos (lista em `tools/kjsport/society_jar_assets.txt`), som `the_box` no sounds.json.
  Commit 6f678ad8 (branch 1.21.1): tudo abaixo pronto, Rhino 380/380; dados podados por
  `tools/dataport/prune_removed.py`. Removido sem substituto (dono decidir): tapper da wise oak (dava lótus negra).
  Depois: 1507e134 (2º launch: itemitem, cache de propriedades, morango nativo, getClass) e acb72cd2
  (3º launch: inventário/fluido via attachments do KJS 7 no lugar do PowerfulJS; sementes recriadas com o
  id antigo `<crop>_seed` porque o KJS 7 força `_seeds`; renomes revisados em `tools/kjsport/IDSCAN.md`).
  Sobra: ~1400 refs a mods ausentes (fantasyfurniture, nethervinery, species, trials, youkai...) em tabelas;
  corrigir só o que aparecer no log. Texturas sem par: 221 (IDSCAN). Esperando o 4º launch (com mundo). Pronto: `tools/kjsport/port_models.py` (modelJson/model -> parentModel/modelGenerator, blockstateJson ->
  arquivos estáticos em `kubejs/assets`, serverTick -> serverTicking + `global.portBeTicks` +
  `server_scripts/zz_port_be_ticks.js` com BlockEvents.blockEntityTick, fluidos thick/thin, sons botania).
  Erros de cascata esperados a sumir com o registro: `numismatics:neptunium_coin`, `society:neptuna`, `froggy_helm`.
  Sobra: biomas `kubejs/data/society/worldgen/biome/*.json` ainda spawnam `splendid_slimes:splendid_slime`.

- 4º launch (2026-11-12, crash ao criar mundo: "Duplicate data file ignored with ID meadow:firewood").
  Causa NÃO provada: só existe um arquivo meadow:firewood em disco (jar do Meadow); listagem vanilla,
  collective, bookshelf, blueprint, moonlight (FastSearch), modernfix e KubeJS conferidas no bytecode, sem
  achar a cópia. Correção candidata: o Meadow 1.21.1 renomeou `fire_log` -> `firewood` (mesmas
  propriedades facing/stage); rename aplicado em 29 arquivos (74 refs) e `meadow:firewood` (2 pinheiros -> 5)
  removido por id em removeRecipes.js, já que o pack usa 6 troncos (kubejs/data/meadow/recipe/fire_log.json).
  Se o crash voltar: próximo suspeito é um pack em memória; testar desligando mods de pack dinâmico.
  Também: generateData -> alvo "after_mods" + e.json (addFishBaits com caminho 1.21 `loot_table/gameplay/
  crab_trap_loot/<isca>`, lostCityCreatePalette), npcInteraction com presentes montados no 1º uso
  (encantamento precisa do registro), disableDispenser com DispenseItemBehavior.NOOP, 131 dicas no formato
  `tipsmod:simple`. Menu: engrenagem do Create desligada (mainMenuConfigButtonRow=0, na 1.20.1 o layout a
  escondia pelo id 376322) e botão de configs do Supplementaries desligado (chave renomeada configs_button).
  Chaves de config renomeadas entre versões: operador aplicando a partir de scratch renamed_keys.txt.

- 5º-7º launch (2026-11-13): mesmo crash. Causa PROVADA: o Meadow 1.21.1 tem `DataFixerMixin` no construtor de
  `ResourceLocation` que troca ids antigos (lista em `DataFixerEntries`, ex. `meadow:fire_log` -> `meadow:firewood`).
  O arquivo `kubejs/data/meadow/recipe/fire_log.json` ganhava o id `meadow:firewood` e duplicava a receita do Meadow.
  Renomeado para `firewood_from_raw_logs.json` (+ `fire_log_unpack` -> `firewood_unpack`); `port_data.py` ganhou
  `FILE_RENAMES` para não recriar o nome antigo. Regra: nenhum arquivo de dados `meadow:` pode ter id da lista antiga.
  Confirmado no 8º launch (mundo criou); `zzDebugDuplicateData.js` removido.
  Create: todos os addons declaram faixas que aceitam 6.0.10; nenhum feito para Create 5 nos jars.

- 8º launch (2026-11-13): mundo criou. Erros do log em 3 unidades paralelas (operadores):
  R) 1478 receitas no formato 1.20 (301 em kubejs/data, 1177 de e.custom em server_scripts/recipes) -> formato 1.21.
  P) Lost Cities: 4561 de 19031 paletas em moonlight-global-datapacks/sunlit_towns com 243 blocos inexistentes
     (redeco, cfm, youkaishomecoming, meadow...) -> tools/lcport/block_map.tsv + port_palettes.py; + 51 loot tables do pack.
  S) sunlitTownsLife.js (.is ambíguo, 47 chunks sem povoar), husbandryJei 'global', itens ausentes no JEI,
     jadeClient getTooltip, hostileSpawnToggle getCategory, incontrol com splendid_slimes.
  R FEITO (2026-11-13): tanukidecor diy (683) item->id no brain; sewing (script + toolbelt: pouch_upgrade_N virou
     belt_upgrade_N na 1.21, overrides recriados com agulha de ferro; belt/pouch mantêm materiais do pack);
     kubejs/data via tools/dataport/fix_recipe_format.py (268 fixed, 45 removidos por itens ausentes, 27 left;
     status em tools/dataport/work/recipe_status.tsv; forge:conditional desembrulhado); scripts lote 1
     (misc/stripping/pickling) e lote 2 (mixer/bottle/grape/milk/milling/pressing/crushing/harmonize com
     conversor toRecipe121 em runtime). S FEITO: sunlitTownsLife getBlock()===, husbandryJei global.runtime,
     guards de itens no JEI, jadeClient appendTooltip, hostileSpawnToggle, incontrol sem splendid_slimes.
  P FEITO: 4561 paletas reescritas (tools/lcport/block_map.tsv, 243 blocos; regras a=157 b=6493 c=342), loot do pack
     com 72 trocas em 36 arquivos (tools/lcport/loot_map.tsv). lc_ids.py reconhece itens registrados pelo KubeJS
     (create() e society:*): a 1ª passada tinha trocado 73 itens society válidos e foi refeita a partir da branch.
  Ruído de mods (ignorar): railways (267 loot de compat), bonsaitrees4 (794 avisos de compat), quark spawn category.

- Auditoria do que faltou da 1.20.1 (2026-11-13, pedido do dono):
  FEITO: patchouli_books (almanac 155 entradas, fish_finder 68; sem slimes e sem animais de mods ausentes;
  variantes SNBT de wooly_cow/chapple mantidas), config/remi/stack_groups (130), 8 defaultconfigs FTB/gag,
  2 shaderpacks, 2 resource packs (sem ativar), sunlit_tools -> tools/pack_tools; regen_chunks.py portado
  (claims FTB 2101 em chunks/time/force_loaded; testado em cópia do save, incluindo claim sintético).
  Barra de rolagem do changelog transparente nos 12 layouts do menu (pedido do dono).
  A decidir com o dono: 11 mods próprios (custom-mods/ + sunlit_cinematic_toms) para portar a NeoForge 1.21.1
  (clockfix, dfhashfix, eating, handsonfix, hangdump, langfilter, qualityfix, replayfix, sortfix, texturefix,
  cinematic_toms); "keybinding presets" (atalhos: precisa autorização); docs da raiz (READ_FIRST, LEIA-ME,
  atalhos.md) com identidade Pipinha. Ignorado de propósito: journeymap/xaero (mapa agora é FTB Chunks),
  caches (emojiful, mod_data, local/), dist/, saves, Distant_Horizons_server_data, .bobby, screenshots.

- 9º launch (2026-11-13, "Mapa solo" regenerado; mundo criou, erros de script). Em curso, sem commit ainda:
  FEITO: ciclo de tag de item c:crops/corn -> forge:grain/corn -> farm_and_charm:corn (jar) -> c:crops/corn
  derrubava TODO o ServerEvents.tags de item (StackOverflow); corn.json não inclui mais #forge:grain/corn.
  Regra: tags do pack nunca incluem #forge:x quando o jar faz forge/mod -> #c:x (scanner:
  `python3 tools/dataport/tag_cycles.py .`). toRecipe121 e helpers em `000_recipe121.js`
  (global.toRecipe121; antes era const em 8 arquivos). isEdible -> componente minecraft:food (3 arquivos).
  LootJS 3.7: addLootTableModifier->addTableModifier, addLootTypeModifier->addTypeModifier,
  addBlockLootModifier->addBlockModifier. Guards Item.exists em receitas/JEI. LMFT: 61 ids mortos tirados de
  17 tags. incontrol sem mobs de mods ausentes. Jade: tooltip.tooltip() antes de CropProgressProvider.
  Almanaque: entrada nether_grapes removida (o livro não compilava), flauta do cavalo -> sela.
  EM CURSO: troca society:milk no lugar do leite fluido (era replaceInput {fluid} na 1.20.1); ids do Vinery
  1.21 (*_crate -> *_bag, cherries -> cherry) em todo o pack; efeito nethervinery:netherite; varredura de ids
  do almanaque. Deixado: aloe_preserves sem receita de Create (fluido aloe_gel não existe); erro do Small Ships
  2.0.2 ao fechar o mundo (bug do mod, depois do save); JEMI/create_factory_logistics chemical (bug do mod).

- 10º launch (2026-11-13, "10º launch: KubeJS loot/ids"): bakery:dough removido (não existe no jar 2.1.11) de canonical/normalize; create:toolbox -> create:brown_toolbox; entrada vazia de splendid_slimes removida (generalLoot); addTypeModifier -> addTableModifier(LootType) em 3 arquivos. Pendente: sunlitTownsLoot (apply não existe em addTableModifier) e ImageButton 1.21.1 (precisa de sprites).
- 10º launch: KubeJS receitas (2026-11-13): addMiscRecipes.js, 37 blocos com resultado/ingrediente ausente trocados por comentário "dropped in 1.21.1"; car_key: relics:horse_flute -> minecraft:saddle; meadow wool: só warped_wool mantido; create:filling honey como neoforge:tag; cutting FD e tuna corrigidos; helper em startup_scripts/recipe121Helper.js. Não testado no jogo.
- 10º launch (2026-11-13, brain): Shoulder Surfing 5.3.1 renomeou player_x/y_rot_follows_camera para player.turning.turn_player_x/y_rot_with_camera; voltaram a false como na 1.20.1 (corpo não gira com a câmera). FOV 60 já estava certo. Punchy Moves tem câmera de ombro própria (tecla V, junto com Toolbelt/Supplementaries/Curios/Replay), desligada por padrão; camera.json não existe, então nunca foi ligada. InControl: 3=vinery:basket -> farmersdelight:wooden_basket, regra do wildernature:flamingo removida. sunlitTownsLoot.js (e o gerador tools/pack_tools/towns/loot.py): apply -> customAction com adaptador do ctx (LootJS 3.7). hostileSpawnToggle.js: ImageButton com WidgetSprites, sprites recortados em kubejs/assets/kubejs/textures/gui/sprites/hostile_spawns*/. Pendente do dono: Sturdy Farmland (aspersores/fertilizantes) sem 1.21.1; itens sem receita: gnome, quality_washer, mana_sprinkler, relics:blazing_flask, quark:slime_in_a_bucket, conchas do unusualfishmod.

## Pendente, em ordem

1. F5 KubeJS: port estático PRONTO (379/379 sintaxe OK, commit 10f2eb5e na branch 1.21.1). Falta: o dono abre
   o jogo uma vez e o agente corrige o que aparecer em `logs/kubejs/*.log` e `logs/latest.log`.
2. F6 FTB Quests (30 capítulos), tirando conteúdo de Botania/Slimes.
3. F7 o que o mod `society` (Society Tweaks) fazia: VillageLootModifier, EmbersTextAPI, serializer patch.
4. F8 Lost Cities: profiles, estruturas e trocar nas paletas os blocos de mods que saíram
   (cfm -> refurbished_furniture, redeco/botania/slimes -> equivalentes instalados).
5. F9 conversão da cópia do save.
6. F10 resource packs, FancyMenu (sem menções ao Sunlit), atalhos (options.txt só com autorização).
7. F11 sincronizar a branch a cada unidade fechada.

- 2026-11-13 (sessão Redecorate/F9): RAM: `minecraftinstance.json` allocatedMemory 8096 -> 6880 (igual à 1.20.1;
  PC tem 15 GB e o processo passava de 95%). Redecorate 1.1.0 instalado pelo dono como sucessor do Re:Deco:
  mapa redeco->redecorate (cadeira/banco upholstery->fabric, mesa short=false, drawers, drawer_counter->drawer_table,
  light_bulb->lightbulb, lâmpada colorida -> oak_lamp[shade=cor,lightbulb=glowstone], fluffy_carpet->rug).
  F9 em curso: `tools/saveport/convert_save.py` copia "Solito solamente" para `saves/` e remapeia ids antes do upgrade.
  Repositório: branch `1.20.1` criada da main (c849da451) para a 1.20.1; `sync_repo.py` e AGENTS.md do Sunlit apontam para ela.
  Sucessores achados e a decidir com o dono: Fantasy's Furniture (port não oficial 1.21.1), Youkai's Homecoming
  (port não oficial completo), Domestication Innovation -> Redomesticate, Refined Storage Addons -> Quartz Arsenal,
  Botania -> Botania Revived (dono já tinha tirado o Botania).
  FEITO: block_map.tsv com 90 linhas redecorate; port_palettes.py renomeia upholstery->fabric; 343 paletas corrigidas
  via tools/saveport/fix_redeco_palettes.py (check_palettes/check_states limpos, 0 "redeco:" restante).
  Dono escolheu instalar (2026-11-13): Youkai's Homecoming (port não oficial), Fantasy's Furniture (port não oficial),
  Redomesticate, Quartz Arsenal. PENDENTE em ordem: (1) instalar e conferir os 4 jars; (2) voltar nas paletas as linhas
  youkaishomecoming/fantasyfurniture/domesticationinnovation se os ports mantêm os ids; (3) F9 convert_save.py
  (scan+dry-run, depois cópia real), id do vinery cherries->cherry conferir no jar.
  FEITO: youkaishomecoming-4.2.17 (mesmos 209 ids), redomesticate-2.0.2 (namespace domesticationinnovation -> redomesticate,
  mesmos nomes), refinedstorage-quartz-arsenal-1.0.8 (toml sem faixa de mc/neoforge; Modrinth lista 1.21.1 NeoForge, aceito).
  Fantasy's Furniture: DONO BAIXA no CurseForge (fantasys-furniture-1-21-1-neoforge-unofficial-port, Core + sets).
  Em curso: paletas voltam aos blocos youkai (fix_namespace_palettes.py); convert_save.py scan/dry-run.
  A fazer no id_map: domesticationinnovation:* -> redomesticate:*; youkai sem remap; refinedstorageaddons -> quartz arsenal (conferir ids).
  FEITO: paletas voltaram aos blocos youkai (643 valores, 305 arquivos). convert_save.py scan ok (97 regiões, 2646 chunks,
  0 erros, md5 da origem igual). Caso novo achado: Miner's Delight mudou namespace miners_delight -> minersdelight
  (290 arquivos do pack ainda usavam o antigo). Em curso: auditoria de namespaces renomeados (tools/modcheck/namespace_renames.tsv)
  + troca no pack; rodada 1 do conversor (upholstery>fabric, namespaces, pet_bed->rug, BE de crate/pedestal, itens perdidos).
  Depois: cópia real do save (convert_save.py run) e validator.
  FEITO: namespaces renomeados (tools/modcheck/namespace_renames.tsv): miners_delight->minersdelight, largemeals->large_meals,
  domesticationinnovation->redomesticate, numismatics_utils->numismaticsutils, bonsaitrees3->bonsaitrees4 (pareamento fraco),
  sunlit_eating->pipinha_eating. 376 arquivos reescritos, kubejs/assets e kubejs/data movidos. ATENÇÃO: port_data.py não
  conhece esses renames de pasta; se rodar de novo, recria kubejs/data/miners_delight e domesticationinnovation.
  Ids sem par no jar novo (ficaram): miners_delight:cooking, numismatics_utils:numismatics_utils, bonsaitrees3:* (5).
  FEITO (F9): saves/Solito solamente convertido (cópia; origem intacta por md5): 697 blocos, 22 itens, 46 BE remapeados,
  181 BE descartados sem itens; terra arada do Sturdy Farmland -> farmland vanilla, aspersores -> ar. Renomes dentro de mods:
  toms_storage ts.* -> sem prefixo, supplementaries sign_post -> way_sign (também em config/via_romana-common.toml),
  quark lootr trapped chest -> trapped_chest. Ficam sem par (somem): verdantvibes (103 plantas), splendid_slimes, species,
  balloonbox, botania:lexicon, meadow sheep_cheese_block/inky_wool. fantasyfurniture (5 blocos) aguarda o dono instalar o port
  ANTES de abrir o mundo. tools/pack_tools/sync_repo.py da 1.21.1 aponta para a worktree e a branch 1.21.1.
  Em curso: validator; depois commit na branch 1.21.1.
  FECHADO: validator PASS (6/6); commit 4ab7a1782 na branch 1.21.1, enviado. Pendente do dono: baixar o port 1.21.1 do
  Fantasy's Furniture (CurseForge) antes de abrir o "Solito solamente"; depois o agente remapeia as linhas fantasyfurniture
  das paletas como foi feito com o youkai.

## 2026-11-13 18:00: Botania de volta + erros do 11º launch
- Decisão do dono: Botania volta "exatamente como na 1.20.1" (a remoção foi baseada em "não há port"; existe o
  Botania Revived, port não oficial com mod id `botania`, só no CurseForge, projeto 1725641). Botania Seeds não tem
  port: recriar as 16 sementes em KubeJS. Splendid Slimes/Cogs seguem sem port (busca 2026-11-13).
- 11º launch (17:53, "Mapa solo"): mundo abriu; erros: society_trading 43 lojas (formato item/nbt 1.20), cozycafe 47
  cardápios (nethervinery, duplicados, itens), loot ~50 fora o ruído do railways (looting_enchant, entry name->value,
  set_nbt...), receitas KubeJS com nethervinery/species/fluido create_central_kitchen, youkai cucumber_crate e
  red_velvet_cake não registrados pelo port (blockstate existe, bloco não), advancements.
- Ordem: U1 baixar Botania Revived + Fantasy's Furniture port; U2 corrigir erros do log; U3 restaurar Botania
  (scripts, dados, quests, lojas, almanaque, paletas) + sementes em KubeJS; U4 refazer cópia do save sem as linhas
  botania/fantasyfurniture no id_map; validator; commit.
- 18:05: Botania-Revived-1.21.1-2.0.2-NeoForge.jar colocado pelo dono (mod id botania, todos os ids da 1.20.1 existem).
  fantasyfurniture-1.21.1-9.0.0-port.1.jar já estava (dono, 17:52; 304 blockstates iguais à 1.20.1). Em curso: U2 erros
  do log; U3a quests+configs do Botania. Depois: U3b kubejs do Botania + sementes + paletas (botania e fantasyfurniture
  voltam ao original); U4 refazer save.
- 18:20: lojas: 5994 stacks item->id, 132 blueprints com custom_data (classe WornBlueprint), villager -> villager_home.
  cozycafe: 31 cardápios de itens que não existem mais removidos, 4 duplicados. Renome achado: crabbersdelight *_kebob -> *_kebab.
  questport (port.py/convert.py) não descarta mais botania. Em curso (5 operadores): Botania kubejs+sementes+paletas
  (frontend-operator), quests do Botania, configs do Botania, sobras das lojas + kebab + check_ids, loot/receitas/
  advancements/youkai não registrados. Depois: U4 refazer save (tirar linhas botania/fantasyfurniture do id_map), validator, commit.
- 18:40: FEITO: Botania Seeds recriado (registerBotaniaSeeds.js, 16 sementes, ids originais, assets em kubejs/assets/botania_seeds),
  addMysticalFlowerSeedRecipes.js, paletas botania (84) e fantasyfurniture (5) de volta ao original, prune_removed sem botania,
  configs do Botania (toml + supplementaries + solonion + 3 stack groups remi). Convites: formato custom_data {type:"society:X"}
  (npcInvite lê string); receitas que criavam {type:{id}} sendo corrigidas. kebob->kebab feito em dados e scripts.
  Gap do Botania por arquivo: scratchpad botania_gaps.txt (startup 16, client 1, assets 10, server 21, data ~105).
  Em curso: 3 operadores (startup/client/assets, server_scripts, kubejs/data) + quests do Botania + loot/receitas/youkai.
  Pendente: lc_ids.py indexa blockstates só pelo nome-base (ids com subpasta, ex. fantasyfurniture:decorations/x, dão
  falso "desconhecido" em check_palettes); U4 save; validator; commit.
- 19:10: Botania: dados (88 arquivos em kubejs/data/botania + 16 mesclados; conferindo formato 1.21), configs ok,
  startup parcial (globalRegistry, NPCs, fish pond, preços, tapper da wise oak -> lótus negra, loom), server parcial (14 arquivos).
  Mana: a API BotaniaCapabilityBuilder da 1.20.1 não existe; unidade própria pesquisando capability (manaClock,
  sparkstoneRecycler, seedMaker, manaFruit, manaSprinkler, manaMilker). Erros do log: loot (20 arquivos), receitas com guard
  recipeIdsExist121, youkai cucumber_crate/red_velvet_cake voltaram ao substituto (não registrados); em curso: random_chance linear,
  suco de uva do Vinery, urn loot, advancements, caminhos inválidos. Quests do Botania: capítulo + 4 merges; fechando lang 12 idiomas.
  Pendente final: lc_ids.py (ids com subpasta), U4 save, validator, commit.
- 20:00: FEITO: Botania completo em kubejs (startup/client/assets/server/data gap 0; 388/388 Rhino OK), quests (botania.snbt 32/32
  + 4 merges + lang 12 idiomas), configs. Mana das máquinas: kubejs/startup_scripts/000_port_mana.js (RegisterCapabilitiesEvent +
  JavaAdapter ManaReceiver) para mana_clock, sparkstone_recycler, mana_fruit_crop, mana_sprinkler, mana_milker; aguardando prova
  de que o listener chega ao mod bus. mana_sprinkler: aspersor do Sturdy Farmland -> farm_and_charm:water_sprinkler. Aspersores
  por nível do Sturdy Farmland ficam fora (saída era do mod). trials:* -> minecraft:* (33 ids, também no id_map do save).
  lc_ids.py indexa subpastas. Puffish skills "nbt" de silk touch: conferir no próximo log.
  Pendente: prova do mod bus (mana), erros restantes do log (round 3), U4 refazer save (id_map sem botania/fantasyfurniture, com trials),
  validator, commit, push.
- 2026-11-13 (brain, round 3/4): save "Solito solamente" refeito (0 decode errors, 0 itens perdidos, 180 BEs caídas, sobras só de mods fora do pack: verdantvibes, splendid_slimes spawner, meadow cheese block/inky wool, species). Round 3: random_chance linear, urn_loot epic/rare, forge:loot_table_id -> neoforge (80 arquivos, conferido no jar), set_nbt -> set_enchantments (balloonbox, livro com mending), 15 stubs de advancement forge:false -> neoforge:false, canonicalItemLoot protege o item substituto. Ruído de jar (não é nosso): brewinandchewin pizza_from_dough, bakery dough_liquids, Invalid path do youkai/longwings. Vinery 1.21.1 sem fluidos de suco: receitas de fluido não voltam.
  Em andamento: ícones de inventário de 95 itens society (minor-operator), validator da unidade. Depois: commit + push 1.21.1.
  Validator: PASS em 6/7; o 7º (236 stubs antigos forge:conditions/forge:false em kubejs/data) corrigido pelo brain com /tmp forge2neo.py (236 arquivos, todos parseiam). Tags forge:* do próprio pack continuam (kubejs/data/forge/tags).
- 2026-11-13 (brain): commits f09f07294 + 4652c6182 enviados. Dono instalou Sunrise Gardening (sucessor do Sturdy Farmland, mesmos ids em sunrisegardening:*). Em andamento: backend-operator restaura conteúdo (rename de namespace, receitas de fertilizante, loot, quests, aspersores, config); conversor refaz o save com dew_drop -> sunrisegardening. Depois: validator, commit, push.
- 2026-11-13 (brain): Sunrise Gardening fechado. Rename dew_drop -> sunrisegardening (28 arquivos), 15 receitas de fertilizante/vaso, 7 receitas de aspersor + remoções do mod, hay golem, loot (floricultura, balloonbox, FFB farmland), 11 quests + 21 chaves de lang, reward table fertilizer.snbt, save round 5. Validator PASS 7/7. Commit em andamento.
- 2026-11-13 (erros no chat do "Mapa solo", log 19:31): helper custom() de 5 scripts de receitas (crushing, bottle, mixer,
  grape juice, pressing) não retornava a receita e o .id() encadeado abortava o resto do arquivo: agora retorna (stub quando
  pulada). hideJEIItems.js aceita "@modid" (Platform.isLoaded) em vez de Item.exists. Tag forge:crops/potato -> #c:crops/potato
  (snuffles). Almanac do Patchouli vazio: beachparty:coconut_hanging -> hanging_coconut, brewery:hop_trellis -> hops_crop.
  farm_and_charm:sweets não existe na 1.21.1 (quebrava o JEED no EMI): 3 comidas society trocadas por minecraft:speed.
  31 JSON de kubejs/data no formato 1.20 corrigidos (rotton_beam removido, saída não existe; winter rune snow_block no lugar
  do raw_snowflake; ancient_cookie usa #c:eggs no lugar do ovo do Species; chai_tea com herbalbrews:tough 6000).
  Pendente com o dono: extrusor 1.21 só aceita blocos laterais; blackstone (tinta do CEI, fluido não existe mais) e
  cobbled_limestone (apple_juice sem bloco, o id do bloco é da garrafa do Vinery) seguem falhando até escolher substitutos.
  Ruído de jar (não é nosso): Sable copycat_catwalk (copycats), overlays do hobbit_hill_village, smallships ao sair.
