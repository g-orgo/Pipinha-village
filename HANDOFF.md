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

## Pendente, em ordem

1. F5 KubeJS (374 arquivos): pesquisar mudanças KubeJS 6 -> 2101, portar startup, server, client.
2. F6 FTB Quests (30 capítulos), tirando conteúdo de Botania/Slimes.
3. F7 o que o mod `society` (Society Tweaks) fazia: VillageLootModifier, EmbersTextAPI, serializer patch.
4. F8 Lost Cities: profiles, estruturas e trocar nas paletas os blocos de mods que saíram
   (cfm -> refurbished_furniture, redeco/botania/slimes -> equivalentes instalados).
5. F9 conversão da cópia do save.
6. F10 resource packs, FancyMenu (sem menções ao Sunlit), atalhos (options.txt só com autorização).
7. F11 sincronizar a branch a cada unidade fechada.
