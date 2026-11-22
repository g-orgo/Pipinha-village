# Estado atual

O que está pronto, em andamento e pendente na migração para a 1.21.1. O plano completo e as fases F0 a F11 estão em `../migracao/PLANO.md`. O progresso detalhado, launch por launch, fica em `HANDOFF.md` na raiz da instância.

## Alto nível

A migração saiu da fundação e entrou na reta final. A instância 1.21.1 (NeoForge 21.1.265, KubeJS 2101, **364 mods** no boot, **388 jars** hoje) abriu com boot limpo em 2026-11-12, e desde então o trabalho é converter conteúdo: **configs**, **dados**, **scripts KubeJS**, **quests**, **Lost Cities**, **save** e **menu**. A razão do pack existir nesta versão é o **Create Aeronautics**, que não tem versão para 1.20.1; o pacote completo (Aeronautics, Simulated, Offroad), o **Aeronautics Camera Sync** e o **Sable** já estão em `mods/`.

O grosso do código já foi convertido. O port estático do **KubeJS** fechou em 379 de 379 scripts com sintaxe Rhino válida (commit `10f2eb5e`), e os launches seguintes serviram para caçar o que só aparece em execução: formato de receita 1.21, ciclo de tags, loot com LootJS 3.7, ids de mods renomeados, itens do mod `society` que não existem mais. Cada launch gerou um lote de correções e um commit na branch **1.21.1**; desde 2026-11-20 a própria pasta da instância é a worktree.

O **save** "Solito solamente" foi convertido em cópia, com a origem intacta por md5, e o **validator** passou. Como o dono reinstalou o **Botania** (via Botania Revived, mesmo mod id) e o port do **Fantasy's Furniture**, o save foi refeito sem as linhas desses dois no mapa de ids. O que falta de verdade é: abrir o jogo uma vez para ler `logs/kubejs/*.log`, fechar **F6** (quests) e **F7** (o que o mod `society` fazia), terminar **F8** (Lost Cities), e então **F10** e **F11**.

Do lado dos mods, o quadro mudou bastante em 2026-11-13. Saíram **Splendid Slimes** e **Splendid Cogs**, sem port. Voltaram **Botania** e **Botania Seeds** (as 16 sementes recriadas em KubeJS). Entraram os sucessores escolhidos pelo dono: **Redecorate** no lugar do Re:Deco, **Redomesticate** no lugar do Domestication Innovation, **Quartz Arsenal** no lugar do Refined Storage Addons, **Youkai's Homecoming**, **Fantasy's Furniture** e **Sunrise Gardening** no lugar do Sturdy Farmland.

Entre 2026-11-16 e 2026-11-20 o dono adicionou mais quatro mods, e a instância está com **388 jars**. **Let it Walk!** traz máquinas que andam para o Create, com pernas, pés e controles de piloto movidos pela física do Sable, e o **Let it Walk: Remote Control** é o controle de mão que pilota esses andadores à distância depois de ligado aos controles de bordo. **Create Waystones Integration** deixa as contraptions do Create carregarem **waystones**: em movimento a pedra recusa teleporte e, ao montar de novo, continua funcionando no lugar novo com o mesmo nome. **FTB Stuff & Things** traz máquinas e blocos pequenos: martelos e auto-martelos, peneiras (sluice), geradores de pedregulho e basalto, blocos comprimidos, ferro fundido, jarros e barris. A lista completa de jars está em `../migracao/mods_instalados.tsv`.

## Baixo nível

```py title:Fases
F0 = "concluída (2026-11-11)"          # instância nova no CurseForge
F1 = "concluída (2026-11-11, boot limpo em 2026-11-12)"  # 364 jars
F3 = "concluída, com sobras"           # configs mescladas; relics e ~100 'manual'
F4 = "concluída, com sobras"           # dados no formato 1.21; 988 JSON para a F8
F5 = "port estático pronto (379/379)"  # falta ler os logs do dono
F6 = "em andamento"                    # 30 capítulos, ícones restaurados
F7 = "em andamento"                    # society: VillageLoot, EmbersTextAPI
F8 = "em andamento"                    # paletas e loot prontos; perfis e estruturas faltam
F9 = "cópia convertida, validator PASS"# refeita após Botania, Fantasy's Furniture e Sunrise
F10 = "pendente"                       # resource packs, FancyMenu, atalhos
F11 = "em parte"                       # main virou a 1.21.1 (2026-11-21); Modpack.zip novo pendente
```

```py title:Ambiente
minecraft = "1.21.1"
neoforge = "21.1.265"
kubejs = "2101"                        # Rhino 2101; proibido const/let no topo de bloco
render = ["Sodium", "Iris"]
menu = "FancyMenu 3.9.1"
aeronautics = "bundled 1.3.2"          # + aero_cam_sync 1.4.0 + sable 2.0.6
memoria = 6880                         # minecraftinstance.json, era 8096
```

```py title:Ferramentas
tools = ["modcheck", "configport", "dataport", "kjsport", "lcport", "pack_tools", "questport", "saveport"]
rerun_forbidden = ["tools/kjsport/mechanical.py"]   # regenera do OLD e apaga o port manual
rerun_careful = ["tools/dataport/port_data.py"]     # não conhece renomes de pasta de mod
tag_cycle_scanner = "python3 tools/dataport/tag_cycles.py ."
```

```py title:RenomesDeMod
# Aplicados no pack, nos dados e no id_map do save
miners_delight = "miners_delight -> minersdelight"
largemeals = "largemeals -> large_meals"
domesticationinnovation = "domesticationinnovation -> redomesticate"
numismatics_utils = "numismatics_utils -> numismaticsutils"
bonsaitrees3 = "bonsaitrees3 -> bonsaitrees4"        # pareamento fraco
sturdy_farmland = "dew_drop -> sunrisegardening"
redeco = "redeco -> redecorate"
crabbersdelight = "crabbersdelight *_kebob -> *_kebab"
vinery = "vinery *_crate -> *_bag, cherries -> cherry"
trials = "trials:* -> minecraft:*"
```

```py title:FuncoesDesligadas
# Sem API equivalente no KubeJS 7 ou sem mod na 1.21.1; o dono foi avisado
maxDamage = 21                          # 21 itens em modifyItems.js sem maxDamage/digSpeed/attackDamage
minimap_heads = false                   # FTB Chunks sem EntityIcons
noSneakEating = false                   # bloqueio de beber fluido agachado
hay_golem_fertilizer = false            # mod ausente
bountiful_role_tag = false              # Bountiful 8 usa componentes
fish_pond_clipboard = false             # escrita na prancheta do Create
dew_drop_fertilizer = false             # virou Sunrise Gardening
```

```py title:SaveConvertido
origem = "saves/ intocado, md5 conferido"
convert = "tools/saveport/convert_save.py"   # scan + dry-run antes da cópia real
validator = "PASS 7/7"
removidos = ["verdantvibes", "splendid_slimes", "species", "balloonbox", "meadow sheep_cheese_block/inky_wool"]
sturdy_farmland = "terra arada -> farmland, aspersores -> ar"
```

#### Regras de negócio

- Toda decisão de conteúdo passa por `../context/decisions.md`; decisão nova do dono entra datada e com o porquê.
- Commit e push na `main` (a 1.21.1 desde 2026-11-21), sempre por unidade fechada; a branch `1.20.1` não é tocada.
- O agente não roda o jogo nem cliente headless. Verificação leve é jar, dado, grep e `logs/latest.log`.
- `options.txt`, atalhos, idioma, escala de GUI e resource packs só mudam quando o dono autoriza.
- Nenhum arquivo de dados `meadow:` pode usar um id da lista antiga do `DataFixerMixin`, senão duplica receita e derruba a criação do mundo.
- Tags do pack nunca incluem `#forge:x` quando o jar do mod cria a ponte `forge` para `#c:x`, porque fecha ciclo e derruba todo o `ServerEvents.tags`.
- Receita nova ou convertida entra por `global.toRecipe121` (em `000_recipe121.js`) e testa `Item.exists` antes de registrar.
- Item do pack que some da 1.21.1 sai da receita, da loja e da quest; se tem equivalente instalado, o equivalente entra no lugar.
- Renome de namespace de mod exige três passos: pack, `kubejs/assets` e `tools/modcheck/namespace_renames.tsv`.
- Não rodar `tools/kjsport/mechanical.py` de novo, e rodar `port_data.py` só sabendo que ele recria pastas com os nomes antigos.
- Loot usa LootJS 3.7: `addTableModifier`, `addTypeModifier`, `addBlockModifier` e `customAction` no lugar de `apply`.
- Script de startup roda duas vezes por sessão, então preço e contador precisam de flag de idempotência.
- Texto para o jogador é em pt-BR; código e comentário em inglês.
- Roupa de mod novo ganha valor de temperatura do LSO na mesma entrega (ver [[conventions]], Harmonização).
- Animal de mod novo ganha doma na mesma entrega: grupo em `taming` e caixa no `tools/pack_tools/pet_guide/content.json`, depois `build_pet_guide.py` (ver [[decisions]], 2026-11-20).
- Todo texto novo (menu, quests, docs) sobre o pack de origem se resume à linha de crédito de rodapé, sem outras menções.
- Skills do Puffish (2026-11-21): nós espelho dos 25 livros na árvore própria e reaplicação dos comandos das skills no login e no desbloqueio (`skillPerkSync.js`); aguardando o dono testar no jogo.
- Roupa de mod novo entra nos slots do Curios por regra automática em `harmonizeClothingCurios.js` (2026-11-21); armadura de verdade fica fora.
- Mob hostil só nasce em caverna ou outra dimensão: `surfaceHostileSpawns.js` barra na superfície do overworld o que vier de patrulha, cerco, estrutura ou mod (2026-11-21).

## Anotações

O que foi feito em 2026-11-20 e 2026-11-21 e ainda não foi visto no jogo?
> Ficou sem teste no jogo: caixas do capítulo "Companheiros" com o propósito de cada animal, doma universal de 61 animais, EMI na crafting station, saída e clique duplo da crafting station, tags de comida, câmera livre montada, roupas no Curios, temperatura segurada do LSO, skills do Puffish, hostis só fora da superfície, porta alta do Dramatic Doors e cidades no modo LEGACY do Lost Cities. O histórico de cada item está em `history.md`.

A migração está perto do fim?
> Sim, no papel. F0, F1, F3 e F4 estão fechadas e a F5 está pronta em modo estático; F6, F7, F8 e F9 andam em paralelo, e F10 e F11 dependem do dono.

O que separa o estado atual da entrega?
> O dono abrir o jogo para o agente ler os logs, fechar as quests e o que o mod `society` fazia, terminar o Lost Cities e refazer o save depois do Botania.

Por que o save foi refeito mais de uma vez?
> Porque cada rodada trouxe decisão nova do dono: Botania de volta, Fantasy's Furniture instalado, Sunrise Gardening no lugar do Sturdy Farmland. Refazer a cópia é barato, a origem fica intacta e o validator confirma.

Por que o Botania voltou se tinha saído em 2026-11-12?
> A remoção partiu de "não há port". Existe o Botania Revived, port não oficial com o mesmo mod id `botania` e todos os ids da 1.20.1. O dono pediu de volta exatamente como era, e o Botania Seeds foi recriado em KubeJS porque não tem port.

O que ainda depende do dono no jogo?
> Ver a câmera do Sable com o Shoulder Surfing 5.3.1, a mana das máquinas do Botania (listener no mod bus), os tooltips de preço e moeda, os textos flutuantes, a chave do carro, as plushies, a aposta da corrida de porcos e as 34 tarefas de quest marcadas como `ftbquests:missing_item`.

O FTB Stuff & Things já conversa com o resto do pack?
> Ainda não. Martelos, peneiras, geradores de pedregulho e blocos comprimidos entraram com as receitas do próprio mod; nenhuma receita, tag ou loja do pack usa esses itens ainda, e o ferro fundido não está ligado às tags de lingote.

Ovo, carne, peixe e leite valem "qualquer um da espécie" nas receitas?
> Sim desde 2026-11-20, pelas famílias de `harmonizeFoodTags.js` e pelos alvos novos de `normalizeEquivalentItems.js` (ver [[conventions]], Harmonização). **Ainda em aberto:** confirmar no jogo; o `logs/kubejs/server.log` deve ter a linha `[sunlit] harmonizeFoodTags:` com o tamanho de cada família, e as receitas de `veggiesdelight:compat/culturaldelight/*` não devem mais aparecer com `is not allowed to be empty`.

**Ainda em aberto:** a prova de que o listener de mana do Botania chega ao mod bus; o Sable com o Shoulder Surfing 5.3.1 (os mixins de compat miram classes renomeadas); 10 lojas do `society_trading` que falham inteiras por ids ausentes (renomear ou tirar a oferta); o extrusor 1.21, que só aceita blocos laterais, com `blackstone` e `cobbled_limestone` sem substituto escolhido; o Fantasy's Furniture nas paletas, se o port mantiver os ids; os 11 mods próprios a portar; a lista de resource packs na F10; e o ajuste do `export_curseforge.py` antes de gerar o zip.

O que ainda falta decidir com o dono?
> Quatro coisas: **Ainda em aberto:** substitutos de hyper_experience (CEI 2 não tem), sap e aloe_gel (Central Kitchen 1.21 não registra) e o ovo do Species (mod ausente), cujas receitas o guard pula; o vidro da estufa, hoje `minecraft:glass` x24 no lugar do vidro do More Minecarts (reversível, avisar o dono); nomes com a origem (Crystal, Flux, Singing Frog, Market) e o link da wiki; e a F11, que só vai para a `main` e gera Modpack.zip novo com confirmação do dono.
