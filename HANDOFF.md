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
- F5a (backend-operator): copiar scripts + renames mecânicos + checagem de sintaxe com o Rhino 2101
  (docker detached) + `tools/kjsport/WORKLIST.md` com o trabalho manual por arquivo.
- Próximo na F5: unidades manuais por pasta a partir do WORKLIST (startup, server, client); depois o dono
  abre o jogo e o agente corrige pelos `logs/kubejs/*.log`.

## Pendente, em ordem

1. F5 KubeJS (374 arquivos): pesquisar mudanças KubeJS 6 -> 2101, portar startup, server, client.
2. F6 FTB Quests (30 capítulos), tirando conteúdo de Botania/Slimes.
3. F7 o que o mod `society` (Society Tweaks) fazia: VillageLootModifier, EmbersTextAPI, serializer patch.
4. F8 Lost Cities: profiles, estruturas e trocar nas paletas os blocos de mods que saíram
   (cfm -> refurbished_furniture, redeco/botania/slimes -> equivalentes instalados).
5. F9 conversão da cópia do save.
6. F10 resource packs, FancyMenu (sem menções ao Sunlit), atalhos (options.txt só com autorização).
7. F11 sincronizar a branch a cada unidade fechada.
