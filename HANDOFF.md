# Progress (9 items + reset item + docs)

Items: 1 day longer | 2 external items into groups | 3 quality stars + cooking inheritance + meal prices
| 4 zero purified water/milk bottles price | 5 cooking skill tree + welcome guide | 6 profession quests (winery, cook...)
| 7 homogenize quests (skill tree quest -> parkour) | 8 new world: HARD locked, no worldtype change, Lost Cities preset
| 9 welcome MMO professions text + lock unchosen professions (bold red) + AGENTS.md "blend in" rule
| 10 profession reset consumable sold by guild for 16000, icon like skill-reset items
| 11 update docs (removed mods, changed buttons)
| 12 XP boost in the skill trees of the chosen professions (see handoff/quests-professions.md)

Order after explores: 4 -> 8 -> 2 -> 3 -> 5 -> 6/7/9/10 (quest files, sequential) -> 11.

## Status 2026-11-03: itens antigos 5, 6, 7, 9, 10 e 12 (conferidos no codigo depois do rework)
- 5 FEITO. Arvore Culinaria e guia no Welcome (6CB695EFC40CBAFC) ja existiam. Feito agora: Extra Portions e Double Harvest
  tambem no corte (culinariaSkills.js; o texto dos nos prometia, so a panela aplicava) e guia sem o "quando for Cozinheiro".
- 6 FEITO (ja estava). Cinco linhas com contrato em profissoes.snbt, inclusive vinicola e cozinheiro.
- 7 FEITO. Skills and Levels (459BA5CC983CFAB9) ja citava Parkour e Cooking. Feito agora: fontes de XP Mercantil na description11.
- 9 FEITO EM PARTE, RESTO OBSOLETO. Texto MMO e regra "cara de conteudo original" ja estavam. Feito agora: trava em vermelho e
  negrito (&c&l) na missao Profissoes do Welcome. OBSOLETO: travar arvores (arvores abertas com Especialidades), duas profissoes
  e ordem entre elas (profissao unica + vagas). Linhas e contratos seguem trancados; nenhum outro capitulo depende deles.
- 10 FEITO (ja estava, pelo rework). society:crystal_of_regret_professions, 16000 na Guilda, icone no padrao dos cristais.
- 12 FEITO (ja estava). +50% XP: experience.json de farming/husbandry/fishing e global.professionBoostedXp nas demais rotas.

## Done
- 1: config/betterdays-common.toml daySpeed 1.0 -> 0.8 (night 1.0, RATIO). Zip updated. In-game check pending.

## Facts (Explore A: quality/puffish/crystals/hooks)
- quality NBT {quality_food:{quality:N}} 1 iron 2 gold 3 diamond(purple). Mod random chances 0 (serverconfig).
- Built-in inheritance mixins: FD pot/board/feast/pie, Kaleidoscope, MinersDelight, Create, Herbalbrews, VintageDelight.
  Gaps: BnC keg, Create Central Kitchen.
- Price: globalShippingBinHandlers.js calculateQualityValue L2-12 (1.25/1.5/2), crops w/ stage 1.5/2/3 L154-167,
  getVariationMultiplier L18-55.
- Puffish trees kubejs/data/society/puffish_skills/{config.json,categories/<n>/...}. XP via
  `puffish_skills experience add <p> society:<tree> <n>` (see startup forgeEvents/parkourSkills.js:16-23).
  Perks = command reward `kubejs stages add <stage>`.
- Crystals: registerItems.js:350-414, server itemEvents/regretCrystals.js, witch.json:458-517. PNGs in mods/society-1.22.jar.
- No crafting/BE output hooks in KubeJS; MoreJS installed unused. No JDK17 javac on machine.

## Facts (Explore D: docs)
- Changelog = config/fancymenu/assets/changelog_{pt_br,en_us}.markdown (L27-49); L30 still mentions Animal Pen.
- Disabled jars: vminus, journeymap, jmi, xaeroworldmap, ConstructionSticks, animal_pen. AGENTS.md list has only V-Minus.
- Modpack.zip animal_pen: DONE 2026-10-24 (jar removed, .jar.disabled added).
- atalhos.md stale: ftbchunks map m, add waypoint '.', waypoint manager Backspace; jei recipeBack/parcool Dodge/treechop
  overlay now unbound; journeymap/xaero/constructionstick entries obsolete; Xaero Excalibur pack inactive (42 packs);
  renderDistance 9, simulationDistance 10. options.txt read-only.

## Facts (Explore B: item groups / bottles)
- Prices: startup globalRegistry.js lists (crops 297, animalProducts 503, fruits 610 -> L697 auto preserves/dried at prio -20,
  preserves 668, artisanGoods 739, cocktails 823, herbalBrews 845, wines 949, brews 1029, cooking 1087, fish 1623, misc 1747).
  Addon patches: globalRegistryAddonFoods.js(-21), ExtraPrices(-21), DrinkPrices(-22), FoodPrices(-23, skips priced ids).
- Category tags by multiplier: server tags/handleItemBlockFluidTags.js:638-657 (crop->farmer, wood->artisan, gem->geologist).
- Machine Maps: customMachines/wineKeg.js:4-55, preservesJar.js:4-79 roe /81+ fruit, dehydrator.js:4, seedMaker.js:4.
- Gaps: external crops missing from machines (kaleidoscope grapes/chili/lettuce/rice/tea, hearthandharvest blueberries/cherry,
  culturaldelights avocado/eggplant/cucumber/corn, youkai black_grape/cucumber/coffee/tea, farmersrespite tea/coffee);
  AddonFoods fruits (L770-796) run after preserves gen; AddonFoods pushes raw crops into cooking (L62-72, L152-154);
  wines/beers/drinks priced as crop instead of wood (hh cherry_wine L101, tavern wines L244-256, BnC beer L178, DrinkPrices L33/48);
  hh cheddar wheel unpriced; BnC/miners/oceans foods flat 20 (AddonFoods 688-768).
- Bottles (item 4): purified_water_bottle AddonFoods:286; farmersdelight:milk_bottle ExtraPrices:28;
  hearthandharvest:goat_milk_bottle AddonFoods:103; vintagedelight:nut_milk_bottle globalRegistry.js:1441.

## Facts (Explore C: quests/shops/world)
- Chapters config/ftbquests/quests/chapters/*.snbt; text in kubejs/assets/ftbquestlocalizer/lang/*.json (12 langs) lang keys.
  pt_br mostly broken (numeric keys) except welcome/guias ~L1535-1552.
- welcome.snbt: root 2B6877708A709B5C; Parkour quest 3C6C8A3075250D1A L94-136 (reward cmd L121); guides root 68F93F0E30C84F4A L415.
- Skill quests (en_us lines): Skills and Levels 498-504, Wrong Skills 522-526, Skill Mastery 986-991, + 32,607,632,742,1038,1061,1097,1124,1554.
- Gamestage tasks via KubeJS player.stages (ftbxmodcompat). Coin rewards numismatics items.
- Shops kubejs/data/society_trading/shops/*.json; guild.json has no NPC binding / no openshop guild found.
- World: defaultconfigs/lostcities-server.toml selectedProfile sunlit_cozy; config/defaultoptions-common.toml defaultDifficulty NORMAL, lockDifficulty false; no world preset mod.

## Zip changes so far
- updated: config/betterdays-common.toml

## Done (cont.)
- 4 (static only, in-game pending): price lines removed for hearthandharvest:goat_milk_bottle (AddonFoods ~L103),
  purified_water_bottle (AddonFoods ~L286), farmersdelight:milk_bottle (ExtraPrices ~L28),
  vintagedelight:nut_milk_bottle (globalRegistry.js ~L1441). New kubejs/startup_scripts/globalUnsellableItems.js
  (priority -100) deletes the 4 ids from global.trades. Side effect: they left society:dish tag. Syntax not parsed (no JS runtime).
- 8 (partial): config/defaultoptions-common.toml defaultDifficulty HARD, lockDifficulty true. Lost Cities profile
  sunlit_cozy already default. PENDING: world-type lock via FancyMenu CreateWorldScreen (identifiers unverified; ask owner in game).

## Zip changes so far (full list)
- updated: config/betterdays-common.toml, config/defaultoptions-common.toml,
  kubejs/startup_scripts/{globalRegistryAddonFoods.js,globalRegistryExtraPrices.js,globalRegistry.js,globalUnsellableItems.js}
- HANDOFF.md never goes into Modpack.zip.

## Session rule (anti auto-compact thrashing)
- ONE item per fresh session (/clear between items). Read only this file at start, then only the file regions needed.
- After any compaction: update this file and stop, asking for a new session.
- Never read subagent .output files; wait for the hand-back message.

## Pending, in order
0. Slim AGENTS.md: move detail into docs/context/{INDEX,conventions,decisions,state,history}.md via minor-operator;
   keep in AGENTS.md only the hard prohibitions (options.txt, saves, Modpack.zip, test in game) + pointer to the index.
1. Item 2 (external items into groups/machines; gaps listed in Explore B): DONE 2026-11-03. Not in scope, left open: flat-priced foods (BnC/miners/oceans, goes with item 3), season tags on canonical crops, Seed Maker seeds selling above the crop value.
2. Item 3 (quality stars + cooking inheritance + meal prices): DONE 2026-11-03. Mini mod sunlit_qualityfix (pots via automation and held bowl, BnC keg), feast and drink tags, dish prices (sunlit_tools/dish_prices.py). Left open: 9 dishes with no resolvable recipe keep flat or no price (hearthandharvest:skewered_sausage, kaleidoscope_cookery:pork_bone_soup, qingtuan, slime_ball_meal, youkaishomecoming:mayonnaise_bottle, milk_popsicle, oyaki, vintagedelight:oatmeal, nut_milk_bottle); no defaultconfigs/quality_food-server.toml, so new worlds use the mod's default random chances.
3. Item 5: FEITO 2026-11-03 (ver Status 2026-11-03).
4. Items 6/7/9/10/12: FEITOS 2026-11-03, partes de 9 obsoletas pelo rework (ver Status 2026-11-03).
5. Item 11: DONE 2026-11-03, changelog updated, disabled list checked (docs: changelog L30 Animal Pen, atalhos.md staleness, AGENTS.md disabled mods list:
   vminus, journeymap, jmi, xaeroworldmap, ConstructionSticks, animal_pen).
6. Item 8 world-type lock: DONE 2026-10-24 (pending in-game test). FancyMenu layout `config/fancymenu/customization/create_world_screen_layout.txt` hides `world_type_button` + `customize_world_type_button`; `CreateWorldScreen` registered in `config/fancymenu/customizablemenus.txt`. Both in Modpack.zip. Fallback if FancyMenu cannot hide tab widgets: KubeJS client script.
7. Modpack.zip animal_pen swap: DONE 2026-10-24.
8. In-game checklist: day length, HARD locked on new world, 4 bottles refused by bin / no price tooltip,
   startup.log without errors from globalUnsellableItems.js.

## Done 2026-10-25 (quality NPE + juice prices, in-game pending)
- globalShippingBinHandlers.js: dish lookup uses plain objects (JS Set threw NPE for quality items in tooltips).
- Juices repriced to ingredient cost x1.25 (+10% seasonal crop): FD/LSO/tavern/vinery/nethervinery/HH juices.
- culinariaSkills.js:27 getPlayer -> getEntity. All in Modpack.zip.
- 2026-10-25 (2nd pass): quality NPE persisted (logs 02:39-02:44: cheese_block, large_duck_egg, fine_wool, large_egg).
  Cause: dish tables on `global` are Java maps, missing-key read -> NPE in NativeJavaMap.get. Now script-local
  `cookedDishIds`/`premiumDishIds`/`ensureDishSets` in globalShippingBinHandlers.js. Zip updated. In-game pending.

## Done 2026-10-25 (3rd pass, in-game pending)
- Contracts: customTask keyed by task id (professionContractTasks in professions.js); kits per profession (professionKits) + lang key society.profession.kit.
- Grapes quest 22E91DAAE230FF19 accepts kaleidoscope_tavern grape/green/gold/ice.
- New world: startup forgeEvents/worldCreationLock.js (ScreenEvent Render Pre: HARD, minecraft:normal, LC "Cities" button inactive);
  server_scripts/worldCreationLock.js (gameTime<=100 -> difficulty hard + locked). config/defaultoptions-common.toml is orphan (no DefaultOptions mod).
- culinariaSkills.js local var renamed player -> clicker.

## Rework profissoes, item 1: refund dos pontos das skill trees (2026-10-26, CONCLUIDO por ordem do dono; logs sem execucao registrada)
- Novo `kubejs/server_scripts/playerEvents/skillRefund.js`: no login, uma vez por jogador (persistentData
  `sunlit_skill_refund_v1`; subir o numero para um novo refund), 40 ticks depois do login.
- Itera `SkillsAPI.streamCategories()` (as categorias que o Puffish carregou do config.json, inclui mercantil
  se existir). Por categoria: abre temporariamente se estiver travada (resetSkills/getSpentPoints so agem em
  categoria destravada), `resetSkills`, trava de novo. XP/niveis preservados (nao usa `category erase`).
- Depois roda todos os `lock_command` dos rewards `puffish_skills:command` de `categories/<cat>/definitions.json`
  (lidos com JsonIO.readJson + Gson): remove os stages de perks e volta os multiplicadores da caixa a 1.
- Mensagem `society.skill_refund.done` (en_us/pt_br, inserida na linha 2) so se havia pontos gastos.
- Modpack.zip: skillRefund.js, lang en_us.json e pt_br.json.
- Checklist no jogo: logs sem erro de skillRefund.js; `[skillRefund] <nome>: N points refunded` no server.log;
  arvores com pontos livres e sem nos; niveis iguais; profissoes travadas continuam travadas.

## Rework profissoes, item 2: profissao unica + Especialidades (2026-10-26, codigo pronto, teste no jogo pendente)
- Desenho e tabela de chances: `docs/context/decisions.md` (2026-10-26). API no topo de `kubejs/startup_scripts/professions/professionGlobals.js`:
  `professionLimit(player)` (padrao 1 + `persistentData.sunlitProfessionSlots`), `addProfessionSlots(player, n)` para a Guilda,
  `hasProfession`, `professionBlocker` (already/limit), `specialtyTier/specialtyChance/rollSpecialty`, `SPECIALTY_PERKS`, `bumpQuality`.
- Arvores sempre destravadas (category.json + unlock no login); Maestria volta a exigir as 5 arvores base.
- Nos novos `specialty_1/2` em farming/husbandry/fishing/vinicultura/culinaria (stages `specialty_<arvore>_1/2`).
- Hooks: loot/professionLoot.js, blockEvents/specialtyFarming.js (uva, terra arada +1 dia via bots_lib Util), forgeEvents/husbandryTwins.js,
  chamadas `applySpecialty*` em globalAnimalHandlers.js, animalBase.js, fishingSkills.js, globalBlockEntityHandlers.js, culinariaCooking.js; replantio em havestHandling.js.
- Contrato com limite atingido nao completa a quest (fica aberta para quando comprar vaga). Quem ja tinha varias profissoes mantem.
- Modpack.zip atualizado com todos esses arquivos + lang + puffish JSON + docs.
- Pendente: teste no jogo (checklist no relatorio da sessao).

## Rework profissoes, item 3: arvore Mercantil (2026-10-26, codigo pronto, teste no jogo pendente)
- Categoria `society:mercantil` (config.json + `kubejs/data/society/puffish_skills/categories/mercantil/`): Nocoes de Comercio, Pechincha I/II/III (stages `mercantil_haggle_1..3`), Livro-Caixa e Balanco (+1 vida cada).
- API `kubejs/startup_scripts/professions/mercantilGlobals.js`: `MERCANTIL_DISCOUNTS` 10/15/25%, `MERCANTIL_GROUPS` (grupo -> profissoes), `mercantilTier`, `syncMercantilStages`, `mercantilSaleXp`, `grantMercantilXp`.
- XP: `processValueOutput` (globalShippingBinHandlers.js) chama `grantMercantilXp` quando a venda entra; sem Maestria.
- Lojas: society_trading nao tem preco por jogador; `sunlit_tools/mercantil_discounts.py` (idempotente, `--check`) poe 3 copias com desconto depois de cada troca do oficio em market/shepherd/fisher/wandering_winemaker/barkeeper. Originais intactas (Auto Trader ignora trocas com stage). Sync dos stages em `kubejs/server_scripts/playerEvents/mercantil.js` (login + 100 ticks).
- Para mudar itens ou percentuais: editar o script (e `MERCANTIL_DISCOUNTS` no JS) e rodar `python3 sunlit_tools/mercantil_discounts.py`.
- Checklist no jogo: aba Mercantil aparece; vender na caixa da XP Mercantil; com Pechincha I e profissao Rancheiro/Cozinheiro, o Pastor mostra a Pocao Milagrosa por 922 ao lado da de 1024; sem a profissao, so o preco normal; trocar de Pechincha troca o preco mostrado.

## Rework profissoes, item 4: Guilda (cristais de profissao) (2026-10-26, codigo pronto, teste no jogo pendente)
- Itens em `kubejs/startup_scripts/registration/registerProfessionItems.js` (recriado): `society:crystal_of_regret_professions`
  (textura antiga) e `society:crystal_of_ambition_professions` (textura nova, mesmo cristal em dourado).
- Uso e preco escalonado em `kubejs/server_scripts/itemEvents/professionCrystals.js`. Reset: remove stages `profession_<id>`,
  `ftbquests change_progress <p> reset <missao de contrato>`, `global.syncProfessions` + `global.syncMercantilStages`; vagas mantidas.
  Ambicao: `global.addProfessionSlots(player, 1)`; cristal marcado (`sunlit_slot_bought`) ao entrar no inventario soma em
  `persistentData.sunlitProfessionSlotsBought`; stage `profession_slot_offer_<n>` escolhe a troca da Guilda.
- guild.json: reset 16000; ambicao 32768/65536/131072/262144 (limit 1 cada). Lang: society en_us/pt_br, society_trading en_us.
- Checklist no jogo: Guilda mostra o cristal de reset e so a 1a faixa da ambicao; comprar ambicao troca para a 2a faixa;
  usar ambicao com contrato ja assinado deixa assinar outro; reset limpa as profissoes, reabre os contratos e mantem as vagas.

## Rework profissoes, item 5: questbook (2026-10-26, textos prontos, teste no jogo pendente)
- Textos em `kubejs/assets/ftbquestlocalizer/lang/{pt_br,en_us}.json` (script de reescrita idempotente por chave; formato do JSON preservado).
- Capitulo Profissoes: intro C99D677431A0387C (subtitulo novo, profissao unica, Especialidades, Mercantil, cristais; ganhou description5/6 no snbt);
  contratos 5B1F0A3C7D2E4F61..65: d1 cita profissao unica e vagas da Guilda, d2 = +50% XP e resumo das Especialidades do oficio, d3 = itens da Pechincha.
- Welcome 4E6A1C2B9D3F5A07: d1-d3 e d5 reescritos, d6 novo (cristais). getting_started (so en_us; pt_br desse capitulo ja usa o en_us):
  459BA5CC983CFAB9 d1 "9 skill trees", d10 reescrito, d11 novo (XP Mercantil); 681EECD8B1D07F34 d4 aponta o cristal de profissao da Guilda.
- Nomes dos cristais ficam em ingles tambem no pt_br (displayName do item nao tem traducao), como Spice of Life/Ancient Aging.
- Outros 10 idiomas nao tem chaves de profissao: caem no en_us. Modpack.zip: os 2 lang, 3 snbt, state.md e history.md.
- Checklist no jogo: abrir o capitulo Profissoes (intro com 6 paragrafos, contratos com textos novos), Welcome > Profissoes, Getting Started > Skills and Levels; nenhum texto aparecendo como chave crua.

# 2026-10-27: KubeJS fix + Cinematic x Tom's Storage compat
- DONE: kubejs/server_scripts/tags/canonicalItemTags.js (Java list had no .includes; now a JS array). In Modpack.zip.
- IN PROGRESS: addon mod `sunlit_cinematic_toms` (source: /var/home/Orgo/Documentos/curseforge/minecraft/cinematic-toms-compat/mod,
  refs in ../ref/official). Build: docker eclipse-temurin:17-jdk, volume sunlit-gradle, `./gradlew build` (see build-log.txt).
  Scene: storage/crafting terminal as Cinematic add-on station; item flies into the screen; E opens the normal window.
- PENDING: copy jar to mods/, add to Modpack.zip, in-game test (terminal scene, store via click and shift-click, E opens window, no log errors).
- DONE (2nd pass): canonicalItemTags.js walks tag entries itself (getObjectIds overflowed on 41 cyclic alias tags in
  kubejs/data/forge/tags/items, e.g. forge:lettuce <-> forge:crops/lettuce; cycles left as they are, vanilla loads them fine).
- DONE: 60 sunlit_towns palettes: vinery:wine_bottle -> vinery:red_wine, vinery:red_grapejuice -> vinery:apple_juice (not blocks in vinery 1.4.41).
- PENDING: /reload in game, check KubeJS server.log has 0 errors; terminal scene test.
- DONE (3rd pass): TagWrapper.entries is not exposed to JS, so the cycles were fixed at the source: 42 JSONs in
  kubejs/data/**/tags/items had their back-references removed (44 edges), with the lost items inlined (no tag loses members).
  Tool + backup: /var/home/Orgo/Documentos/curseforge/minecraft/cinematic-toms-compat/tools/ (break_cycles.py, kubejs-data-tags-backup.tgz).
  canonicalItemTags.js back to getObjectIds() + JS array.
- FIX: station side is FACING.getOpposite() (Tom's FACING points into the wall). Needs game restart to test.
- 2026-10-28: split 8261955e done: vertical camera + StorageStrip (items of connected chests, hover magnify, click pulls). Build OK, jar installed + zip. PENDING in-game test.
- 2026-10-28: SceneScreen mixin (IDataReceiver -> StorageTerminalMenu) so Tom's item list reaches the scene; onPacket nulled in tick (NPE). Installed + zip. PENDING in-game. Connector lang (%d) fix awaits owner OK for sunlit_overrides.zip.
- 2026-10-28: NetworkHandler mixin routes Tom's DataPacket to StorageTerminalMenu when screen is not Tom's (full list was lost during Cinematic intro); SceneScreenMixin removed; [CinematicToms] diagnostics. Installed + zip. PENDING in-game.
- 2026-10-29: Terminal grid in-world; fixed plane to real screen depth (5/16 from back) + layout from owner print (CELL 0.125). Installed 2026-10-29 06:2x (cmp OK) + zip; earlier "game open" was a pgrep -f false positive. JEI still missing in scenes: split jei-cena-ainda-nao-aparece. PENDING: copy jar with game closed, zip, in-game test.
- 2026-10-29 (barra do painel de itens, pedido do dono): StorageStrip (painel que abre no hover dentro da cena do
  terminal) ganhou a abinha superior com os botoes do proprio Tom's + barra de pesquisa.
  Layout: painel 172 de largura, BASE_H=28, CHROME_H=34, EXPAND_H=92, chrome top = localH - 119, linhas ancoradas
  embaixo; 4 botoes de 17px em PAD + i*17, campo 162x12; clique/tecla so com expand > 0.9.
  Icones de toms_storage:textures/gui/storage_terminal.png (u=194, v=30+tile*16; tile 0 ordenar, 1 direcao,
  2 busca, 6 tall) porque o crafting_terminal.png do Excalibur nao tem nada depois de x=194 (icones invisiveis).
  Botoes: tipo de ordenacao (quantidade/nome/mod), direcao, busca padrao/manter, fixar aberto. Tipo e direcao vao
  pro bloco via menu.sendMessage({"c":{"d":int}}) (te.setSorting), entao E abre o terminal na mesma ordem; pesquisa,
  "manter" e "fixar" sao locais e voltam ao padrao em onEnd (strip.reset()).
  Busca: nome, id, @mod, #tag, $nbt (comparadores de StoredItemStack.SortingTypes), caret + placeholder + scroll;
  sem resultado mostra strip.no_match. Digitacao em ScreenEvent.CharacterTyped.Pre; teclas em
  TerminalStation.keyPressed -> strip (ESC fecha o painel, E so abre a janela com a busca sem foco); clique direito
  limpa; clique fora tira o foco; tooltips em pt_br/en_us do proprio mod (o pt_br do Tom's nao tem sorting_2).
  Arquivos: client/StorageStrip.java, client/TerminalStation.java, client/TerminalStripEvents.java, lang/{en_us,pt_br}.json.
  Jar sunlit_cinematic_toms-1.0.0.jar rebuildado (50368 bytes, cmp OK) em mods/ e no Modpack.zip; docs/context
  state+history tambem no zip. PENDENTE teste no jogo.
- 2026-10-29 (ícones + rebalance de preços, pedido do dono):
  ICONES: o pack "Excalibur Tom's Simple Storage 1.3" substitui storage_terminal.png e a area dos botoes
  (x>=194) vem 100% transparente -> os tiles do atlas do Tom's sao invisiveis em jogo (vale para o terminal
  real tambem). StorageStrip passou a usar os icones do proprio pack (sprites/icons: sort_amount, sort_name,
  sort_by_mod, sort_asc, sort_desc, search_mode + search_mode_keep, tall_terminal_off/on), copiados para
  mod/src/main/resources/assets/sunlit_cinematic_toms/textures/gui/strip/, e a barra ganhou placa escura
  (51,38,33) atras para os icones lerem em qualquer fundo. Jar 63551 bytes.
  PRECOS: kubejs/startup_scripts/globalPriceBalance.js (priority -30) roda depois dos registries e reescreve
  global.crops/global.cocktails + global.trades: faceis /3 (berries, graos, cana, cacau, nether wart, uvas,
  cha/cafe, cogumelos, maca, cereja), hortalicas /1.5 (raizes, folhosas, melao/abobora e fatias), raras
  intactas; caixas/sacos/fardos/blocos seguem o fator do base (match por nome + aliases); 4 sucos = fruta x1.35.
  Bonus sazonal +20% -> +8% (globalShippingBinHandlers.js; tooltip addPriceTooltips.js agora calcula o %).
  conventions.md: etapa x1.25 -> x1.35, sazonal +8% na etapa (x1.46), secao nova do preco das colheitas.
  NAO editar a mao esses valores no globalRegistry.js: o script sobrescreve.
  PENDENTE teste no jogo: icones da barra, precos de blueberry/wheat/caixas na caixa de envio e tooltip,
  linha "[SOCIETY] globalPriceBalance.js: N precos rebalanceados" no kubejs/server.log (startup.log).
- 2026-10-29 (tooltip de subprocesso): globalProcessValue.js (priority -40) monta global.processValue a partir dos
  global.*Recipes (wineKeg, cheesePress, mayonnaise, preservesJar, dehydrator, oilMaker, loom, pickling, fishSmoker,
  espresso, tapper, mushroomLog, baitMaker, deluxeWormFarm, recycling, seedMaker, extractinator): para cada saida,
  coins = valor - custo do ingrediente / qtd de saida, pct = coins/custo*100; receita alternativa fica com o
  ingrediente mais caro. 152 itens. addPriceTooltips.js: linha "Subprocessos: +N moedas (+M% em valor)" abaixo do
  sazonal, e o sazonal virou "Colheita sazonal: +8% (8% em valor)" (tambem no caminho do shift, que ainda tinha
  value*1.2 cravado). Lang: item.society.seasonal_bonus / item.society.subprocess_bonus em pt_br e en_us.
  ATENCAO: como o preco de vinho tem base fixa (12x fruta + 288), o % de subprocesso fica enorme (ex. uva 1 ->
  creepers_crush 336 = +33500%); se o dono achar exagerado, trocar por "% do valor final" (coins/valor).
  PENDENTE teste no jogo.
- 2026-10-29 (erros de startup + ordem do grid):
  ERROS: globalPriceBalance.js tinha `const finalCocktails` dentro de um `if` no topo do script -> Rhino do KubeJS
  hoista para o escopo do script e quebra com "redeclaration of var", mesmo na primeira execucao. Corpo inteiro agora
  esta dentro de `applyPriceBalance()` com flag `global.priceBalanceApplied` (nao corta o preco 2x). globalProcessValue.js
  quebrava com "Cannot find function get" porque `global.extractinatorRecipes` e LISTA (lista tem .keys(), entao o teste
  antigo passava e chamava .get()); agora Array.isArray() vem primeiro, aceita Map JS, Map Java e lista, e le `pickle`
  da prensa de conserva. `global.processValue` virou tabela de texto (id -> "moedas|%") e o tooltip le por colchete (objeto aninhado pode chegar como JSON entre scripts).
  VALIDADOR: sunlit_tools/js_harness/run.sh roda os startup scripts fora do jogo com o Rhino do mod (docker), duas
  avaliacoes seguidas (cliente+servidor). Foi ele que reproduziu os dois erros.
  GRID: StorageStrip numera as linhas de cima para baixo (item 1 no topo esquerdo). `rowY()` interpola a posicao com
  `expand`, entao fechado sobra a primeira linha embaixo e ao abrir as linhas sobem. Barra de rolagem: thumb desce
  quando `row` cresce. Jar 63663 bytes.
  PENDENTE teste no jogo: erros nao devem aparecer ao abrir/fechar o mapa, item 1 no topo esquerdo, clique puxando o
  item certo, rolagem.
- 2026-10-29 (tooltip sazonal em moedas): "Colheita sazonal: +8% (8% em valor)" virou "+8% (3 moedas)". `seasonalBonusCoins()`
  em addPriceTooltips.js calcula a diferenca no valor final com a qualidade aplicada (mesma conta do formatNumber), nos
  dois caminhos (tooltip normal e shift). Se der 0 moedas, cai em item.society.seasonal_bonus_only ("+8%" sozinho).
  Lang pt_br/en_us atualizados. Subprocessos continua "+N moedas (+M% em valor)".

## 2026-11-03: owner confirmed in game
- Profession rework items 2-5, trash slot and Shift+click in the terminal scene all pass.
- New rule in AGENTS.md: the agent is the final verifier; do not wait for owner tests.

## 2026-11-03: headless verification
- Replay confirmed in the headless client. sunlitLongerDay.js fixed and measured at 0.8x.

## 2026-11-03: login crash
- sunlit_texturefix installed; 3 of 3 headless logins clean. Wheat and chestnut season bonus added.


## Animacao completa de comida, primeira e terceira pessoa (2026-11-04)

Concluido. Detalhes em `docs/context/state.md` e `docs/context/decisions.md`.

## Ajustes das animacoes de primeira pessoa (2026-11-06, pedido do dono)
1. Braco esquerdo levantado em toda animacao -> so tigela/prato usam as duas maos (gen_ie_foods.py animation()).
2/5. Comida de mao (hand/slice/skewer, 1059 itens) aparece deitada/plana -> em pe, segurada pelo cabo (osso/palito), mordidas a partir da ponta (gen_ie_foods_all.py voxel_bones).
3. Colher escondida pela tigela -> colher mais longa e visivel dentro da tigela (gen_ie_foods.py utensil/geometry/poses).
4. Hotbar travada durante a animacao -> trocar de item cancela a animacao pelo caminho do addon (AnimationUtils.stopAnimationControl) no mini mod sunlit_eating.
Fatos: trava do addon = InputEvents.onMouseScroll (cancela scroll), KeyboardHandlerMixin.food$blockHotbarKeys (lockedHotbarSlot>=0),
InputEvents.onClientTick (forca o slot). Clique esquerdo ja cancela via stopAnimationControl (StopAnimationPacket + Empty.stopEatAnimation + clearAnimationState).
Status: CONCLUIDO 2026-11-06 (detalhes em docs/context/decisions.md). Modpack.zip atualizado.

## Garfo, modelos 3D e terceira pessoa (2026-11-07)
- FEITO: garfo +30 graus em z (gen_ie_foods.py utensil_bones), icone 2D de itens separate_transforms (gen_ie_foods_all.py gui_model/icon_for), regeneracao e --check ok.
- FEITO, NAO CONFERIDO NO JOGO: ThirdPersonFood (upright: segura no pivo da mao + giro de 180 graus no osso orient; tigela/prato ignoram a inclinacao da raiz). Jar compilado em mods/.
- PENDENTE: rodada sunlit_tools/headless_client com os cenarios em scratchpad uh (terceira pessoa, fov 30) quando houver memoria livre (~8 GB). Se a comida aparecer de ponta-cabeca, trocar o giro de 180 graus; se tigela/prato ficarem errados, rever skipRootRotation.

## Potes, tigelas e colher (2026-11-07, pedido do dono)
1. Maionese modelada como caneca -> tipo jar (79 potes), tampa sai e goles. FEITO.
2. Ensopado de carneiro com cenoura sem pedacos -> gen_ie_dishes.py (tigela redonda, caldo, ingredientes da receita). FEITO.
3. Colher escondida pela tigela -> inclinada 30 graus, mergulho com giro e recuo (UTENSIL_DIP*). FEITO.
Verificacao: --check PASS; jogo sem janela (sunlit_tools/headless_client) e preview.py. Detalhes em docs/context/decisions.md.
