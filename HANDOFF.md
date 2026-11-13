# HANDOFF: migração para 1.21.1

Fonte única de progresso da migração. Plano completo: `docs/migracao/PLANO.md`.
Origem (só leitura): `../Society: Sunlit Valley`.

## Decisões do dono (2026-11-12)

- Botania, Botania Seeds, Splendid Slimes e Create: Splendid Cogs saem do pack:
  quests, ofertas de loja e receitas ligadas a eles são removidas.
- O save "Solito solamente" vai ser convertido numa CÓPIA (F9); o original não é tocado.
- Versionamento: branch `1.21.1` do Pipinha-village (worktree `/var/home/Orgo/Documentos/Pipinha-village-1.21.1`).

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
