# F6: FTB Quests 2101 (2026-11-13)

Origem (só leitura): `../Society: Sunlit Valley/config/ftbquests/quests`. Destino: `config/ftbquests/quests`.
Refazer: `python3 -I known.py && python3 -I port.py <saida>` e depois `python3 -I validate.py <saida>` e
`python3 -I integrity.py <saida>`. `lang.py <pasta lang> --write` limpa os textos (idempotente).

## O que mudou

- 28 capítulos (saíram `botania` e `slimes`), 18 reward tables (saíram `slime` e `fertilizer`), 1185 -> 1079 quests.
- Itens no formato 1.21: `{id, count, components}`. NBT convertido: Damage -> `minecraft:damage` (só recompensa),
  display -> `minecraft:custom_name`/`minecraft:lore`, troféus -> `trofers:trophy`, Longwings -> `longwings:variant`,
  qualidade -> `quality_food:quality {type, level}`, convite/aldeão -> `minecraft:custom_data {type}`,
  Portable Blueprints -> `minecraft:custom_data` (o mod lê CUSTOM_DATA), livros -> `patchouli:book`,
  livros encantados -> `minecraft:stored_enchantments`, poção -> `minecraft:potion_contents`.
- Tarefas de item: `match_nbt`/`weak_nbt_match` -> `match_components` ("fuzzy" quando a tarefa exige dado, senão "none").
- Item Filters (sem 1.21) -> FTB Filter System 21.1.4 (`ftbfiltersystem:smart_filter` com `or(item(a)item(b))` /
  `item_tag(t)`); jar do maven oficial da FTB em `mods/`, sha1 a48e54ed...; o adaptador vem no FTB XMod Compat.
- Quests Additions (sem 1.21): 5 tarefas "quebrar pedregulho" viraram `gamestage` (`quest_broke_<pedregulho>`),
  dado por `kubejs/server_scripts/blockEvents/boulderQuestStages.js`.
- Renomes: `idscan_renames.json` + 10 conferidos nos jars (`convert.py`, RENAME), trial chambers -> vanilla.
- Removidas: tarefas/recompensas/itens de filtro de Botania, Botania Seeds, Splendid Slimes, Create: Splendid Cogs
  e de mods sem 1.21 (lista em `port_log.txt`); quests sem tarefa restante e 5 quests só de texto sobre slimes/Botania.
  Dependências religadas para as dependências da quest removida (36 quests); `removed.json` lista tudo.
- Textos (`kubejs/assets/ftbquestlocalizer/lang`, 13 idiomas): chaves das quests removidas apagadas, "Sunlit Valley" ->
  "Pipinha's Village", título do livro "Pipinha's Village". "Sunlit Crystal" ficou (nome de item).

## Perdido sem substituto (dono decidir)

- Sturdy Farmland (`dew_drop_farmland_growth`): 13 itens (aspersores e fertilizantes de qualidade); reward table de fertilizante.
- More Minecarts (13), NetherVinery (12), Domestication Innovation (4), Species (2), Refined Storage Addons,
  Verdant Vibes, Fantasy's Furniture, Croptania, Farm Life.
- Itens que sumiram em mods que continuam: candlelight hearth/khinkali, beachparty chocolate_icecream/sweetberry_milkshake,
  brewery hop_trellis_seed, CEI disenchanter/hyper_experience_bottle, create_central_kitchen cooking_guide,
  netherdepthsupgrade baked_lava_pufferfish_stew, unusualfishmod raw_snowflake.
- Dado descartado em recompensa: decreto do Bountiful (estação "spring"), jarra de lava do Supplementaries (vai vazia),
  madeira cherry do barril de ferro do Sophisticated Storage, habilidades pré-roladas de 3 relíquias.

## Não verificado (precisa do jogo)

- Formato aceito pelo FTB Quests 2101 só foi lido por strings do jar (sem decompilar): `match_components`, itens com
  `components`, migração de `title/description` inline para `lang/en_us.snbt` no primeiro save.
- Qualidade: tarefas de ouro usam "fuzzy"; se o item colhido trouxer `effects` no componente, pode não casar.
