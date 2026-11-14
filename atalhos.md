# Atalhos e configurações padrão do Pipinha's Village 1.21.1

> Padrão definido pelo dono em 2026-10-26 na edição 1.20.1 e conferido contra os jars da 1.21.1
> em 2026-11-13. Fonte: `tools/pack_tools/options_canonical.txt`. Este arquivo é só referência:
> nada aqui é aplicado sozinho, e o `options.txt` só muda quando o dono pedir.

A edição 1.21.1 existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1.
Os atalhos abaixo são os mesmos que o dono usava na 1.20.1. Cada id de atalho foi procurado nas
traduções dos jars 1.21.1 (mods, jars embutidos, Minecraft 1.21.1 e `kubejs/assets`). Quem está marcado
com **não existe na 1.21.1** mudou de nome ou saiu junto com o mod; quando há id novo, ele aparece ao lado.

## Alto nível

O resultado da conferência, em resumo:

- **276 de 315** atalhos existem na 1.21.1 com o mesmo id e continuam valendo.
- O **ReplayMod** (ReForgedPlay) segue com os mesmos ids `key.replaymod.*`; ele monta as traduções
  na hora, por isso não aparece nas buscas, mas o jar registra os mesmos nomes.
- **ParCool 4**, **Refined Storage 2**, **Relics** e **Punchy** renomearam as teclas: o atalho
  continua existindo com outro id, e quem usava precisa refazer no menu de controles.
- **Splendid Slimes**, **Species**, **Refined Storage Addons** e o **Better Advanced
  Tooltips Backport** saíram, e as teclas deles somem junto. O **Botania** saiu em 2026-11-12 e
  voltou em 2026-11-13 (Botania Revived, mesmo mod id `botania`), então as teclas dele valem de novo.
- Teclas novas da 1.21.1 que não estavam no padrão: Aeronautics Camera Sync
  (`key.aero_cam_sync.toggle`, `key.aero_cam_sync.open_config`), a tecla alternativa do
  Create Aeronautics (`simulated.key.alt`) e o editor do Veil (`key.veil.editor`).

Os presets do Visual Keybinder vieram da pasta `keybinding presets` da 1.20.1 para
`visual_keybinder/presets/`, que é onde a versão 1.21.1 do mod procura. Ela só tem o arquivo de
carga com o nome do preset em branco, então nenhum preset é aplicado.

## Geral

- lang: `en_us`
- guiScale: `3`
- renderDistance: `9`
- simulationDistance: `10`
- graphicsMode: `1`
- maxFps: `260`
- gamma: `0.0`
- fov: `0.5`
- particles: `0`
- ao: `true`
- renderClouds: `"false"`
- chatVisibility: `0`
- mouseSensitivity: `0.3204225352112676`

## Resource packs (43, base em cima, topo embaixo)

Ordem do padrão da edição 1.20.1. Os marcados como **ausente** não estão em `resourcepacks/` hoje.

1. `vanilla`
2. `mod_resources`
3. `mod/punchy:punchy`
4. `file/sunlit_overrides.zip`
5. `file/glow_up-1.5-1.20.1.zip`
6. `file/MobCrates_1.20.1_v1.zip`
7. `file/JadeStardewValleyTheme.zip`
8. `file/Stardew_plaques v1.0.zip`
9. `file/Better_Cats_V0.09.zip`
10. `file/DerpWood.zip`
11. `file/Create Style for Refined Storage.zip`
12. `Moonlight Mods Dynamic Assets`
13. `food_dynamic`
14. `generated/fragmentum_layer`
15. `create_central_kitchen:create_styled`
16. `file/-1.21.2 Fresh Moves v3.1 (With Animated Eyes).zip`
17. `file/CreateSophBackpacks.zip`
18. `file/EatAnimation Farmer's Delight's Compat 1.20-26.x.zip`
19. `file/Enhanced Audio Ambience r2.zip`
20. `file/Excalibur Rechiseled Support.zip`
21. `file/Excalibur Sophisticated v1.2.zip`
22. `file/Excalibur Tom's Simple Storage 1.3.zip`
23. `file/Excalibur_Create-6 Addon_Forge_v2.32.zip`
24. `file/Excalibur_Lootr_v1.1.zip`
25. `file/Excalibur_Supplementaries_1.1_1.20.1.zip`
26. `file/Excalibur_Twigs_0.2_1.20.1.zip`
27. `file/Excalibur_V1.20.zip`
28. `file/Excalibur_Vinery_0.3_1.20.1.zip`
29. `file/Fancy Crops v1.3.zip`
30. `file/FarmersDelightExcaliburSupport.zip`
31. `file/FreshAnimations_v1.10.4.zip`
32. `file/SocietyCoins.zip`
33. `file/excalibur_ftbsuite.zip`
34. `vinery:bushy_leaves`
35. `eatinganimations_compat`
36. `scholar:colored_books`
37. `supplementaries:darker_ropes`
38. `file/Fairy Wings Elytra.zip`
39. `file/Lopy-Create-Pipez.zip`
40. `file/updated_aquaculture-1.1.zip`
41. `file/FA+Classic_Horses-v1.5.zip`
42. `vanillabackport:freshly_animated`
43. `file/Fluid-Foolish-1.0.1.zip`

## key (166 ativos, 86 sem tecla)

- attack: **Botão esq. mouse**
- use: **Botão dir. mouse**
- forward: **w**
- left: **a**
- back: **s**
- right: **d**
- jump: **Espaço**
- sneak: **Shift esq.**
- sprint: **Ctrl esq.**
- drop: **q**
- inventory: **i**
- chat: **Enter**
- pickItem: **Botão meio mouse**
- command: **slash**
- screenshot: **f2**
- togglePerspective: **f5**
- fullscreen: **f11**
- swapOffhand: **f**
- advancements: **l**
- hotbar 1: **1**
- hotbar 2: **2**
- hotbar 3: **3**
- hotbar 4: **4**
- hotbar 5: **5**
- hotbar 6: **6**
- hotbar 7: **7**
- hotbar 8: **8**
- hotbar 9: **9**
- puffish skills open: **k**
- rehooked fire hook key: **Botão mouse 4**
- rehooked retract hook key: **c + Shift**
- rehooked remove all hooks key: **Espaço**
- replaymod playeroverview: **b**
- replaymod lighting: **z**
- replaymod quickmode: **q**
- replaymod thumbnail: **n**
- replaymod playpause: **p**
- replaymod rollclockwise: **l**
- replaymod rollcounterclockwise: **j**
- replaymod resettilt: **k**
- replaymod pathpreview: **h**
- replaymod keyframerepository: **x**
- replaymod clearkeyframes: **c**
- replaymod synctimeline: **v**
- replaymod positionkeyframe: **i**
- replaymod timekeyframe: **o**
- libtooltips expand: **Shift esq.**
- toms storage open terminal: **e**
- scholar toggle book tools: **f1**
- scholar import book: **f6**
- scholar export book: **f7**
- scholar insert empty page left: **insert + Shift**
- scholar remove page left: **delete + Shift**
- scholar insert empty page right: **insert + Alt**
- scholar remove page right: **delete + Alt**
- cinematic sit: **Botão dir. mouse**
- cinematic look: **Alt esq.**
- punchy open main menu: **f8**
- punchy inspect: **n**
- shouldersurfing adjust camera left: **Seta esq.**
- shouldersurfing adjust camera right: **Seta dir.**
- shouldersurfing adjust camera in: **Seta cima**
- shouldersurfing adjust camera out: **Seta baixo**
- shouldersurfing adjust camera up: **PageUp**
- shouldersurfing adjust camera down: **PageDown**
- shouldersurfing swap shoulder: **o**
- shouldersurfing toggle first person: **Botão mouse 5**
- shouldersurfing free look: **Alt esq.**
- craftingtweaks compress one: **k + Control**
- craftingtweaks compress all: **k + Shift**
- trashslot toggle: **t**
- trashslot delete: **delete**
- trashslot delete all: **delete + Shift**
- sophisticatedcore sort: **Botão meio mouse**
- sophisticatedcore transfer to storage: **left.bracket**
- sophisticatedcore transfer to inventory: **right.bracket**
- sophisticatedbackpacks open backpack: **b**
- sophisticatedbackpacks toggle upgrade 2: **x + Alt**
- sophisticatedbackpacks toggle upgrade 1: **z + Alt**
- carry desc: **Shift esq.**
- refinedstorage clearGridCraftingMatrix: **x + Control** (não existe na 1.21.1: Refined Storage 2 dividiu em `clear_crafting_grid_matrix_to_network` e `..._to_inventory`)
- moreoverlays lightoverlay desc: **f7**
- moreoverlays chunkbounds desc: **f9**
- toastcontrol clear: **j**
- buildinggadgets2 settings menu: **g**
- buildinggadgets2 undo: **u**
- betteradvancedtooltips view tags: **Shift esq.** (não existe na 1.21.1: Better Advanced Tooltips Backport não tem versão 1.21.1)
- betteradvancedtooltips view nbt: **Alt esq.** (não existe na 1.21.1: Better Advanced Tooltips Backport não tem versão 1.21.1)
- cycleLeft: **g** (não existe na 1.21.1: vinha do Puzzles API dos mods do Fuzs, que não traz isso na 1.21.1)
- jei focusSearch: **f + Control**
- jei nextSearch: **Seta baixo**
- jei showRecipe: **r**
- jei maxTransferRecipeBookmark: **Botão esq. mouse + Control**
- jei cheatOneItem: **Botão esq. mouse**
- jei transferRecipeBookmark: **Botão esq. mouse + Shift**
- jei toggleOverlay: **o + Control**
- jei recipeBack: **Backspace**
- jei cheatItemStack2: **Botão meio mouse**
- jei toggleHideIngredient: **Botão esq. mouse + Control**
- jei cheatItemStack: **Botão esq. mouse + Shift**
- jei clearSearchBar: **Botão dir. mouse**
- jei toggleCheatModeConfigButton: **Botão esq. mouse + Control**
- jei toggleWildcardHideIngredient: **Botão dir. mouse + Control**
- jei previousRecipePage: **PageUp**
- jei previousCategory: **PageUp + Shift**
- jei closeRecipeGui: **Esc**
- jei previousSearch: **Seta cima**
- jei bookmark: **a**
- jei nextCategory: **PageDown + Shift**
- jei cheatOneItem2: **Botão dir. mouse**
- jei showUses: **u**
- jei nextRecipePage: **PageDown**
- extend: **Seta cima** (não existe na 1.21.1: vinha do Species, que não tem versão 1.21.1)
- retract: **Seta baixo** (não existe na 1.21.1: vinha do Species, que não tem versão 1.21.1)
- plonk place: **r**
- splendid slimes slime vac mode: **v** (não existe na 1.21.1: Splendid Slimes saiu do pack)
- mount jump: **f7**
- food animation: **u**
- stardew fishing minigame button: **Botão esq. mouse**
- relics ability list: **Alt esq.** (não existe na 1.21.1: Relics renomeou: `key.relics.active_abilities_list`)
- ok zoomer zoom: **z**
- legendarysurvivaloverhaul added desc: **Shift esq.**
- legendarysurvivaloverhaul body health: **h**
- curios open desc: **Tab**
- spatial-gui toggle mouse free: **Alt esq.**
- spatial-gui open profile picker: **Acento grave**
- ftbultimine: **Acento grave**
- findme search: **y**
- findme pull one: **keypad.0**
- findme pull stack: **keypad.1**
- ftbchunks map: **m**
- ftbchunks minimap zoomIn: **equal**
- ftbchunks minimap zoomOut: **minus**
- ftbchunks add waypoint: **period**
- ftbchunks waypoint manager: **Backspace**
- openManual: **f1**
- toolbelt slot: **v**
- raws visual keybinder open screen: **f10**
- jade config: **keypad.0**
- jade show overlay: **keypad.1**
- jade toggle liquid: **keypad.2**
- jade show recipes: **keypad.3**
- jade show uses: **keypad.4**
- jade narrate: **keypad.5**
- jade show details: **Shift esq.**
- parcool Enable: **p + Control** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.enable`)
- parcool Crawl: **c** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.crawl`)
- parcool ClingToCliff: **Botão dir. mouse** (não existe na 1.21.1: ParCool 4 não tem tecla própria para esse movimento)
- parcool Breakfall: **Espaço** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.breakfall`)
- parcool FastRun: **Ctrl esq.** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.fast_move`)
- parcool RideZipline: **Botão dir. mouse** (não existe na 1.21.1: ParCool 4 não tem tecla própria para esse movimento)
- parcool WallSlide: **Botão dir. mouse** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.slide_down`)
- parcool WallJump: **Espaço** (não existe na 1.21.1: ParCool 4 não tem tecla própria para esse movimento)
- parcool Vault: **Botão dir. mouse** (não existe na 1.21.1: ParCool 4 não tem tecla própria para esse movimento)
- parcool HorizontalWallRun: **r** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.horizontal_wall_run`)
- parcool HideInBlock: **c** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.hide_in_block`)
- parcool openSetting: **p + Alt** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.open_setting_skilltree`)
- parcool HangDown: **Botão dir. mouse** (não existe na 1.21.1: ParCool 4 renomeou: `key.parcool.hang`)
- paraglider paragliderSettings: **p + Control**
- ponder ponder: **w**
- refinedstorageaddons openWirelessCraftingGrid: **g + Control** (não existe na 1.21.1: Refined Storage Addons não tem versão 1.21.1)
- punchy triggerable punchy sword inspect old: **j** (não existe na 1.21.1: Punchy 3.2 juntou as inspeções em `key.punchy.inspect`)
- punchy triggerable punchy sword inspect rework: **g** (não existe na 1.21.1: Punchy 3.2 juntou as inspeções em `key.punchy.inspect`)
- punchy moves camera toggle v: sem tecla na 1.21.1 (a câmera própria do Punchy Moves briga com o Shoulder Surfing; desvinculada em 2026-11-14)
- punchy moves camera editor: **f7**
- punchy moves emote menu: **e**

Sem tecla: `playerlist`, `socialInteractions`, `smoothCamera`, `spectatorOutlines`, `saveToolbarActivator`, `loadToolbarActivator`, `modernfix config`, `replaymod settings`, `replaymod marker`, `replaymod positiononlykeyframe`, `replaymod bothkeyframes`, `exposure camera controls`, `botania corporea request`, `togglecleanview`, `shouldersurfing toggle third person front`, `shouldersurfing toggle third person back`, `shouldersurfing toggle camera coupling`, `shouldersurfing toggle x offset presets`, `shouldersurfing toggle y offset presets`, `shouldersurfing toggle z offset presets`, `open muffler gui`, `craftingtweaks rotate`, `craftingtweaks rotate counter clockwise`, `craftingtweaks balance`, `craftingtweaks spread`, `craftingtweaks clear`, `craftingtweaks force clear`, `craftingtweaks compress stack`, `craftingtweaks decompress one`, `craftingtweaks decompress stack`, `craftingtweaks decompress all`, `craftingtweaks refill last`, `craftingtweaks refill last stack`, `craftingtweaks transfer stack`, `trashslot toggle lock`, `sophisticatedbackpacks inventory interaction`, `sophisticatedbackpacks tool swap`, `sophisticatedbackpacks toggle upgrade 5`, `sophisticatedbackpacks toggle upgrade 4`, `sophisticatedbackpacks toggle upgrade 3`, `refinedstorage focusSearchBar` (não existe na 1.21.1), `refinedstorage openWirelessGrid` (não existe na 1.21.1), `refinedstorage openWirelessFluidGrid` (não existe na 1.21.1), `refinedstorage openWirelessCraftingMonitor` (não existe na 1.21.1), `refinedstorage openPortableGrid` (não existe na 1.21.1), `buildinggadgets2 anchor`, `buildinggadgets2 range`, `toggleVisualItemContents` (não existe na 1.21.1), `toggleSelectedItemTooltips` (não existe na 1.21.1), `toggleCarriedItemTooltips` (não existe na 1.21.1), `cycleRight` (não existe na 1.21.1), `jei toggleEditMode`, `jei nextPage`, `jei toggleBookmarkOverlay`, `jei showUses2`, `jei showRecipe2`, `jei previousPage`, `jei copy recipe id`, `jei toggleCheatMode`, `solonion open food book`, `ok zoomer decrease zoom`, `ok zoomer increase zoom`, `ok zoomer reset zoom`, `spatial-gui open config`, `spatial-gui reload profiles`, `spatial-gui open editor`, `ftbteams open gui`, `golemoverhaul netherite golem summon`, `ftbchunks toggle minimap`, `ftbchunks claim manager`, `ftbquests quests`, `smallships ship sail`, `toolbelt open`, `toolbelt cycle left`, `toolbelt cycle right`, `parcool Dodge` (não existe na 1.21.1), `parcool QuickTurn` (não existe na 1.21.1), `parcool Flipping` (não existe na 1.21.1), `pickup item`, `createrailwaysnavigator route overlay options`, `observable profile`, `punchy moves camera toggle v`, `punchy moves free camera`, `punchy moves emote hello`, `punchy moves emote hello b`, `punchy moves emote cool emote` (não existe na 1.21.1), `punchy moves emote shuuba dance` (não existe na 1.21.1)

## simplemagnets (0 ativos, 1 sem tecla)


Sem tecla: `keys toggle`

## iris (0 ativos, 3 sem tecla)


Sem tecla: `keybind reload`, `keybind toggleShaders`, `keybind shaderPackSelection`

## cos (0 ativos, 1 sem tecla)


Sem tecla: `key opencosarmorinventory`

## placebo (2 ativos, 0 sem tecla)

- toggleTrails: **keypad.9**
- toggleWings: **keypad.8**

## keyinfo (1 ativos, 0 sem tecla)

- copycats fill copycat: **Alt esq.**

## crafting_on_a_stick (1 ativos, 0 sem tecla)

- key open curios: **v**

## portable_blueprints (6 ativos, 0 sem tecla)

- key mapping move origin up: **PageUp**
- key mapping move origin down: **PageDown**
- key mapping move origin px: **Seta esq.**
- key mapping move origin nx: **Seta dir.**
- key mapping move origin pz: **Seta cima**
- key mapping move origin nz: **Seta baixo**

## tooltipoverhaul (1 ativos, 0 sem tecla)

- binds compare bind: **Shift esq.**

## soundsbegone (0 ativos, 1 sem tecla)


Sem tecla: `config`

## gnetum (1 ativos, 0 sem tecla)

- config keyMapping: **end**

## treechop (0 ativos, 4 sem tecla)


Sem tecla: `key toggle chopping`, `key toggle felling`, `key cycle sneak behavior`, `key open settings overlay`

## railways (2 ativos, 0 sem tecla)

- keyinfo bogey menu: **Alt esq.**
- keyinfo cycle menu: **Alt esq.**

## crashutils (1 ativos, 2 sem tecla)

- openscreen: **u + Control**

Sem tecla: `copycontainer`, `slottooltips`

## desc (0 ativos, 1 sem tecla)


Sem tecla: `seasonhud keybind options`

## quark (2 ativos, 29 sem tecla)

- keybind camera mode: **f12**
- keybind change hotbar: **z**

Sem tecla: `keybind autorun`, `keybind back`, `keybind transfer insert`, `keybind transfer extract`, `keybind shift lock`, `emote no`, `emote yes`, `emote wave`, `emote salute`, `emote cheer`, `emote clap`, `emote think`, `emote point`, `emote shrug`, `emote headbang`, `emote weep`, `emote facepalm`, `keybind patreon emote dance`, `keybind patreon emote tpose`, `keybind patreon emote dab`, `keybind patreon emote jet`, `keybind patreon emote exorcist`, `keybind patreon emote zombie`, `keybind sort player`, `keybind sort container`, `keybind lock rotation`, `keybind narrator readout`, `keybind narrator full readout`, `keybind variant selector`

## create (2 ativos, 1 sem tecla)

- keyinfo toolmenu: **Alt esq.**
- keyinfo toolbelt: **Alt esq.**

Sem tecla: `keyinfo rotate menu`

## supplementaries (1 ativos, 0 sem tecla)

- keybind quiver: **v**

## Anotações

Por que os atalhos não foram passados para o `options.txt` da 1.21.1?
> Pela regra do pack, `options.txt`, atalhos e resource packs só mudam quando o dono pedir.
> Este arquivo serve de guia para refazer no menu de controles ou para uma restauração autorizada.

O `restore_options.py --md` pode regerar este arquivo?
> Não por enquanto: ele foi copiado de `sunlit_tools/` para `tools/pack_tools/` e procura o
> `options.txt` e o `atalhos.md` em `tools/`, não na raiz da instância, e não faz a conferência
> com os jars 1.21.1. Antes de usar o `--apply` aqui, o caminho precisa ser corrigido.

**Ainda em aberto:** a ordem dos resource packs da 1.21.1 é decidida na F10 do
[[docs/migracao/PLANO]]; a lista acima ainda é a da 1.20.1.
