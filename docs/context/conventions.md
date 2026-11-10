# Convenções do projeto Sunlit (regras estáveis)

Regras de geração, mundo e conteúdo que valem para qualquer mudança nesta instância. As regras de save solo, testes no jogo, `options.txt` e `Modpack.zip` ficam em `AGENTS.md`.

## Regen dos saves ativos

# REGRA OBRIGATÓRIA: MUDOU A GERAÇÃO, OS SAVES ATIVOS SÃO REGENERADOS

Sempre que uma mudança afetar a geração do mundo (datapack `sunlit_towns`,
pipeline `sunlit_tools/towns`, profile do Lost Cities, scripts KubeJS que
mexem em chunk recém-gerado), os saves ativos em `saves/` também devem ser
atualizados: os chunks antigos do overworld são apagados para o jogo gerar de
novo com a versão atual quando alguém passar por lá.

Apenas o save `Solito solamente` é regenerado; `Nosso mapa` não entra nessa regra.

### O que fica intacto

- O chunk onde cada jogador está e o chunk da cama/spawn dele.
- Todo chunk com claim do FTB Chunks (`<save>/ftbchunks/*.snbt`), incluindo os
  com forceload ativo (`force_loaded_time > 0` na entrada do chunk; forceload
  exige claim, então é um subconjunto, mas o `regen_chunks.py` conta os dois
  separados no log: `claims=X forceloaded=Y`).
- Nether e End não são tocados.
- SEMPRE, em qualquer modo (2026-11-09, pedido do dono, depois de perder uma vaca e um cervo):
  chunk com animal do jogador. Conta como do jogador: carinho do Society
  (`KubeJSPersistentData.affection`), dono ou domado (`Owner`, `Tame`, `Trusting`),
  golem/stoneling feito pelo jogador, animal na guia, nome dado com name tag
  (`CustomName` com `text`) ou passageiro de um desses. NPC de cidade (`easy_npc`) e
  nome gerado (só `translate`) não contam. Motivo no `--dry`: `animal:<tipo>:<id>@x,y,z`.
- NUNCA casa cortada (2026-11-09, pedido do dono): manter um chunk e regenerar o vizinho
  deixa meio prédio velho ao lado do layout novo. Por isso todo chunk mantido leva junto a
  área inteira do Lost Cities: a de multibuilding da cidade (8x8, `floorDiv(chunk, 8)`) e a
  de construção avulsa (7x7, `(chunk + 2000000) / 7`); tamanhos lidos de
  `worldstyles/towns.json`. Depois, `sunlit_tools/regen_continuity.py` mantém o vizinho
  sempre que blocos de construção atravessam a borda em 3+ alturas, e toda área 8x8 tocada
  passa a ficar inteira, até estabilizar. Motivos no `--dry`: `area_lc:` e `predio_cruza:`.
  Efeito: perto de base, cidade inteira fica na versão antiga; o resto regenera.
  2026-11-10 (pedido do dono, "deleta TUDO que não estiver forceloaded ou que tenha um animal meu"):
  a área 8x8 em cascata segurava cidades inteiras velhas (21 chunks base viravam 2624 mantidos) e o
  regen parecia não atualizar nada. Regen do `Solito solamente` agora é
  `--apenas-forceload --so-predio`: mantém só forceload + animais do jogador + o prédio que cruza a
  borda de um chunk mantido (`regen_continuity`), sem a área inteira do Lost Cities.

### Como fazer (jogo FECHADO)

1. Confirme que o Minecraft não está rodando (`logs/latest.log` terminou e não
   há processo java da instância).
2. Faça backup de cada save antes:
   `zip -qr "saves/<save> backup-antes-regen-<versao>-<data>.zip" "saves/<save>"`.
3. Rode a partir de `saves/`, primeiro com `--dry` para conferir os números:
   `python3 ../sunlit_tools/regen_chunks.py "<save>" --apenas-forceload --so-predio`
   (padrão desde 2026-11-10; o `--politica-solo` antigo continua disponível)
   (`--politica-solo` preserva só o chunk do jogador, os chunks force loaded do
   FTB Chunks e os chunks com armazenamento do jogador: inventário sem
   `LootTable`, InhabitedTime >= 1200, ignorando prateleiras, dispensers e
   Lootr da vila; limpa também `entities/` e `poi/` dos chunks apagados).
4. Mova `<save>/data/DistantHorizons.sqlite` para
   `saves/dh_backup_<data>/`, senão o LOD continua mostrando as cidades antigas
   de longe.
5. Informe no chat quantos chunks foram preservados/apagados em cada save e
   onde ficaram os backups.

Se o usuário pedir para preservar mais (ex.: uma base sem claim), use
`--radius N` ou rode sem `--so-jogadores` (mantém chunks com 10+ minutos de
InhabitedTime). Backups e caches de save nunca entram no `Modpack.zip`.

Data da regra: 2026-10-03

## Baús das cidades

# REGRA OBRIGATÓRIA — CONTEÚDO DOS BAÚS DAS CIDADES (2026-10-06, rev. 2026-10-09)

Todo baú comum das cidades Sunlit TEM que ter estas categorias (regra pedida
pelo dono; implementada em `sunlit_tools/towns/loot.py`, que gera o datapack
`sunlit:chests/*` (agora editado direto; `convert.py` e legado) + `kubejs/server_scripts/sunlitTownsLoot.js`
via `write_extra_js()`):

- 1 drop de mob (pool `mob`, que inclui `minecraft:blaze_rod` raro);
- 1 comida OU 1 bebida (nunca os dois no mesmo baú);
- `warm_string` + `cold_string` (1 a 3 no comum, no máximo 3 no rico);
- 1 equipamento (pool `machine`: ferramenta e miudeza VANILLA — NADA com
  namespace `create` em baú comum, NENHUMA bancada/bloco que já exista como
  mobília no mapa; panela só sai no tema da cozinha) e 1 material (pool
  `material`, sem Create);
- 1 a 3 itens "de verdade" (comum; 4 a 6 no rico), TEMÁTICOS com o contexto
  (cozinha = coisas de cozinha, oficina = peças do Create, quarto = coisas de
  quarto...): o tema do container primeiro, depois a pool do próprio tema,
  por último BASIC. Create SÓ sai em oficina (tema workshop) e depósito.
  Só o depósito (e o raro baú rico) dropa itens aleatórios de qualquer nível;
- NENHUMA backpack em baú (2026-10-10, pedido do dono): nada com namespace
  `sophisticatedbackpacks` em nenhum pool (`loot.py` removeu de `DEP_DEVICES` e
  `BASIC_MACHINES` + filtro em `_js_entries`);
- sem repetir o mesmo item dentro do baú;
- preenchimento pequeno: só 1 a 3 drops de mobs (não encher o baú).
- Baú rico (raro; depósito sempre): 4 a 6 itens de qualquer nível, sem
  comida/bebida, mesmo preenchimento pequeno.
- POUCO BAÚ COM LOOT (2026-10-09, pedido do dono): no máximo 2 containers
  com loot por andar de cada construção (3 se o andar for maior, i.e. mais
  de 6 candidatos), baú/barril de verdade primeiro. Vale para TODAS as
  estruturas. Implementado em `polish.py:rule_loot_cap` (corta o `loot` dos
  excedentes na ordem fixa bau/barril > geladeira > resto, por posição),
  cobrado por `validate.py` (`loot demais no andar (max 3)`) e corrigido nos
  chunks antigos em jogo (`sunlitTownsLife.js:townCapLoot`, só loot `sunlit:`).

Mudou o loot? Edite direto as loot tables em `moonlight-global-datapacks/sunlit_towns/data/sunlit/loot_tables/chests/*.json` e `kubejs/server_scripts/sunlitTownsLoot.js`, depois `finalize.py` + `validate.py`,
atualize o `Modpack.zip` e regenere os saves (regra acima).

## Hortas

# REGRA OBRIGATÓRIA — HORTAS SÓ COM PLANTAS DO ANO TODO (2026-10-06)

As hortas das cidades (`sunlit_tools/towns/parks.py` + mistura de `mix.py` +
pool `SEEDS` de `loot.py`) SÓ plantam culturas que crescem em QUALQUER estação
do Serene Seasons. Fora de estação a planta mostra "Cannot grow" e não nasce;
planta sem tag sazonal é sempre fértil, então as hortas usam: nabo, brócolis, couve-flor, alho, batata-doce (alface e pimenta do Kaleidoscope também aparecem nos templates, mas o jar as trava em duas estações: alface na primavera e outono, pimenta no verão e outono)
e berinjela (+ abóbora/melancia só como semente clássica no baú; batata e cenoura estão na blacklist, ver sunlit_tools/towns/docs/blacklist.md). Trigo,
beterraba, repolho, tomate, cevada, aveia, morango, alface/morango do Let's Do,
abobrinha, pepino, samambaias do LSO e que tais NÃO entram em mapa nem em baú.
Planta com trava de bioma (só nasce no bioma X) também não entra: na cidade
ela nasceria onde não pode. O pomar usa só arbustos de 1 bloco (fileiras de
chá baixo + trevo; nada de tea_bush/coffee alto). Coelho NÃO spawna nos
parques (`TOWN_FAUNA_PARK` sem `minecraft:rabbit`): coelho vanilla come
plantação de cenoura madura e deixava slots vazios. Porta do cercado é o char
`E` (2026-10-09: `G` colidia com o alho no dict da `horta` e as porteiras
nasciam como alho, que quebrava e deixava vãos). Perda em jogo é reposta
sozinha (`sunlitTownsLife.js:townRefillGarden` replanta a cultura vizinha em
toda farmland com ar em cima, em parques e prédios; só copia cultura do ano todo e, sem
nenhuma no chunk, usa nabo, brócolis, couve-flor ou alho). Parque ou horta de lote cujo
pós-processamento nunca rodou (fila perdida ao fechar o jogo, chunk gerado pelo Distant
Horizons) ficava 1 bloco acima do gramado: a fila agora é salva no mundo
(`persistentData` do overworld, `sunlitTownPending*`) e o retrofit de cada chunk carregado
reenfileira o parque com terra arada/caminho 1 bloco acima e nenhum no nível do gramado
(`townNeverLowered`, 2026-11-10). Mudou as hortas? Rebuild
completo (`houses.py` + `cozy_expansion.py` + `vila.py` +
`remodel.py` + `schematics.py` + `finalize.py` + `polish.py` + `complexes.py` +
`validate.py`), `Modpack.zip` e regen dos saves.

## Casas: variação de material

# REGRA OBRIGATÓRIA — CASAS COM VARIAÇÃO DE MATERIAL (2026-10-06, rev. 2026-10-09)

As casas não podem ser todas iguais. Dois níveis de variação:

1. Por TIPO (`mapping.swap_material` com `vary`, chamado no `convert_palette` E
   no `convert_states` do `schematics.py` com `M.SALT = key`): madeira troca o
   tipo (8 vanilla), tijolos alternam `bricks`/`stone_bricks`, quartz vira
   concreto cinza (branco/cinza-claro/cinza), calcita vira concreto colorido,
   tijolo de calcita alterna com tijolo de pedra. 2026-10-09: `pick()` filtrava
   por `exists()` (só ids completos) e SEMPRE devolvia None para cor/madeira —
   a variação NUNCA funcionou; `vary()` sorteia sem esse filtro.
2. Por CHUNK: cada casa schematic sai em 3 colorways (`vila_<key>` = c0 legada,
   `vila_<key>_c1/_c2`), segunda passada `mapping.recolor` (só casca
   `minecraft:` madeira/tijolo/concreto + calcita do Create; mobília de mod
   intacta), registradas como prédios separados com peso dividido. O Lost
   Cities sorteia por chunk. Repetição exata num raio de 9 chunks é
   matematicamente inevitável (361 chunks, K cores), mas fica rara e distante.
   KubeJS acompanha: regex de frentes aceita `_cN`, `sunlitTownsLife.js` tira o
   sufixo antes de ler o tema (armor stands) — sem isso o tema quebra.

TERRACOTA NÃO EXISTE nas cidades (2026-10-09, pedido do dono): toda terracota
(lisa, colorida, esmaltada) vira `minecraft:*_concrete` com cor SORTEADA
(nunca powder, nunca mantendo a cor — era o "mar de rosa"). Quebrou a
variação? Checar `HOUSE_WOODS`/`HOUSE_BRICKS`/`HOUSE_COLORS` + rebuild +
`Modpack.zip` + regen.

## Interiores e mobília

# REGRA OBRIGATÓRIA — INTERIORES E MOBÍLIA (2026-10-06)

- `clutter.py`: no máximo 2 mesas soltas por cômodo e mesa nunca encostada em
  bancada/armário/cadeira/outra mesa (cozy_cabin ficava com mesa sem sentido).
- MESA/CAMADEIRA/SOFÁ SÓ DENTRO DO CÔMODO (2026-10-10): `vanilla_furni.seats()`
  exige `inroom` estrito (não `near_room`): varanda coberta colada no cômodo
  virava mesa do lado de fora. Sofá em fileira (`run>=2`) só vira sofá com as
  costas em parede de verdade, senão vira cadeira. Móvel que cair no caminho
  vira tapete (`clutter.py:rug`: sofá/cadeira/mesa/crate/pote no `path` vira
  `minecraft:*_carpet` em vez de bloquear a passagem).
- JANELA SEM WALL E COM PERSIANA DOS DOIS LADOS (2026-10-10, 3ª correção):
  `schematics.py:fix_windows` (todas as casas) + `polish.py:rule_windows`
  (datapack montado): wall entre dois vidros ou grudado no vidro com ar do
  outro lado sai; trapdoor aberto de um lado só do vidro é espelhado.
- `polish.py` (`rule_float`): vaso/quadro/tapete sem apoio embaixo sai; móvel
  de parede sem parede (tool rack no vazio, sword mount solto) gira para a
  parede oposta ou sai. (`rule_chimney`): chapéu industrial no topo de coluna
  de alvenaria com céu aberto vira fogueira acesa (era o "dispenser" da chaminé).
  Dispenser de chaminé da casa vermelha vira fogueira no RETOUCH.
- Lareiras (`galpao.py` + `remodel.py`, 2026-10-18, pedido do dono): chaminé
  MACIÇA de tijolos, sem fogueira dentro de casa e sem duto aberto atravessando
  os andares. O núcleo é de tijolos do chão até o topo e a fogueira acesa fica
  em cima da chaminé. As antigas células de lareira (oficina 2,12; casa_fazenda
  13,2) viram tijolo. Não reabrir o duto.
- Porão (`schematics.py:ladder_mouths`): boca de escada ABERTA para o porão
  ganha escada (ladder) automaticamente. A casa VERMELHA TEM subsolo no
  schematic (`m-pinkhouse.nbt` camadas 1-2, pilares de quartzo; térreo = camada
  3): usa `ground=3 + cellar=2` SEM `dig` (2026-10-09: o `dig=True` antigo
  cavava uma sala FANTASMA embaixo do porão real). O RETOUCH abre o poço de
  acesso no chão da sala em (8,2,12) + escada com apoio no pilar (9,.,12) e
  põe despensa no porão real; a serrana NÃO tem porão (`cellar=0`: o "subsolo"
  dela era podium/jardim aberto — como cellar o LC escavava um fosso e a casa
  nascia 3 abaixo; medieval/solar têm porão real e vêm seladas — se alguma
  precisar de acesso, copiar o esquema da vermelha.
- SUPORTE SOLTO DO LADO DE FORA (2026-11-08, pedido do dono): `npc.py:drop_loose_supports`
  tira o `decorative_blocks:*_support` com ar em cima e a frente para o céu aberto
  (mão-francesa presa na fachada sem segurar nada, parecia prateleira do lado de fora;
  mercado basic, ferreiro/carpinteiro/pescador/bruxa rurais). Suporte que segura
  telhado, viga, floreira ou outro bloco fica. Só as casas de NPC têm `_support`.
- SUPORTE SEM NADA EM CIMA, CASA DE NPC SOTERRADA (2026-11-09, pedido do dono, casa do ferreiro
  basic em -10403 72 8052): (1) `drop_loose_supports` agora tira TODO suporte em pé (`up=true`) com ar
  em cima, mesmo embaixo do beiral, salvo se algo pendura nele; suporte de ponta-cabeça fica.
  (2) `npc.py:parse_value` passa os valores do `.bp` para minúsculas (`face=FLOOR`, `type=TOP`): antes
  o `clean_props` descartava a propriedade, a floreira virava `face=wall`, quebrava sem parede e o
  suporte ficava "prateleira"; cortinas, sofás e baús duplos também perdiam a forma. (3)
  `npc.py:lift_onto_ground`: a camada 0 dos blueprints é a primeira ACIMA do chão (degrau, banco,
  fogueira, caixotes, trilho, tapetes); a casa vai em cima de uma camada nova de grama e terra/caminho
  solto da camada 0 afunda para o gramado. Exceção: camada 0 com maioria de terra natural
  (witch pineconetown) continua sendo o chão. Não voltar a pôr a camada 0 na altura da grama (as
  escadas meio enterradas e cobertas de neve pareciam privadas na rua).
- Bancos (`sunlitTownsLife.js:townFixSeats`): em jogo o banco vira para parede
  + aberto, ou (no meio da praça) para outro banco/mesa por perto; nunca para
  o nada. Hedges/cercas/móveis de conexão se religam sozinhos por chunk
  (`townFixConnections`).
- Armazém do estacionamento: a lojinha do posto (`polish.py:
  retouch_convenience` em `sunlit:convenientstore_1/ground`) tem padrão FIXO:
  bancada de hortifruti com caixotes determinados (maçã, framboesa, mirtilo,
  berinjela, pepino, brócolis, arroz, chá, pepino japonês, maçã, maçã) + 2
  armários verdes de vidro com geleias em cima; sem produce empilhado em
  cima de lampada e sem sorteio de caixote.
- GELADEIRA E COZINHA (2026-10-09, pedido do dono): geladeira SEMPRE com as
  costas em parede de verdade (nunca escada/laje, nunca móvel) e a frente
  livre (nunca abrindo para dentro do fogão/pia). `vanilla_furni` só converte
  e só mobília com essas duas condições (`kitchen()` + `furnish_empty`) e
  `polish.py:rule_fridges` gira para o melhor lado em todo o datapack; em jogo
  `sunlitTownsLife.js:townFixFridges` corrige os chunks antigos. Cozinha de
  schematic NÃO leva tralha solta do `clutter.py` (só peça de parede; o resto
  da casa continua com 45% de preenchimento, 25% em cômodo pequeno, sem armor
  stand em cômodo com menos de 16 células).

## Fauna e moradores espaçados

# REGRA OBRIGATÓRIA — FAUNA E MORADORES ESPAÇADOS (2026-10-10, pedido do dono)

- `sunlitTownsLife.js:townPopulate` é o ÚNICO ponto de spawn (Lost Cities com
  `generateSpawners:false`; `convert.py` remove `mob` das paletas). Todo GRUPO
  (villagers, curral, parque, quintal, pet, rua) entra na regra dos 8 chunks:
  `sunlitFauna` em `persistentData` (mesmo padrão do waystone); se outro grupo
  a menos de 8 chunks (Chebyshev), o grupo não nasce.
- Quantidades reduzidas: curral 2 fixo; pet 8%; quintal 7% com 1; parque 50%
  vazio senão 1; rua 5% com 1. Coelho fora da rua (come cenoura madura).
- VILLAGERS + IRON GOLEM (2026-10-18, pedido do dono): grupo de 2 a 3
  villagers + SEMPRE 1 iron golem, 5% por casa / 4% por comércio, com lista
  própria `sunlitVillagers` a 6 chunks (Chebyshev); os animais seguem em
  `sunlitFauna` a 8 chunks. Só profissões que abrem loja do Sunlit
  (society_trading, `ShopData.getShopFromEntity`): cartographer=banker,
  toolsmith=blacksmith, fisherman=fisher, weaponsmith=librarian/witch,
  farmer=market, shepherd=shepherd, fletcher=trader. barkeeper (`beach_guy`)
  não dá (profissão de mod, fora do `$TownProfession`); NPCs nomeados do
  Sunlit são Easy NPC e não nascem por aqui.
- GOLEM COM ESPAÇO (2026-10-18, pedido do dono): o iron golem só nasce em
  ponto com 3 blocos de ar de altura em toda a coluna 3x3 em volta
  (`townSpots(..., tall=true)` + `townTallClear`); primeiro ao ar livre, depois
  dentro do prédio; sem ponto válido o grupo fica sem golem.

## Baú bônus e kit inicial

# REGRA OBRIGATÓRIA — BAÚ BÔNUS E KIT INICIAL (2026-10-09, pedido do dono)

Com baú bônus ligado na criação do mapa ele SEMPRE tem o mesmo conteúdo
(`kubejs/data/minecraft/loot_tables/chests/spawn_bonus_chest.json`): picareta
e machado de ferro, mochila de cobre (`sophisticatedbackpacks:copper_backpack`),
3 pães e 1 cantil VAZIO (`legendarysurvivaloverhaul:canteen` puro, sem NBT —
cantil novo já nasce vazio; `canteen_purified`/`canteen_empty` NÃO existem como
item, são estado do item base e quebrariam a loot table). Sem baú
bônus, o kit entra no inventário no primeiro login junto dos guias
(`addQuestbook.js`: só dá o kit se NÃO achar baú perto do spawn).

## Nada bloqueado nasce nas cidades

# REGRA OBRIGATÓRIA — NADA BLOQUEADO NASCE NAS CIDADES (2026-10-06)

As towns NUNCA geram (nem como bloco colocado, nem em baú) itens de
`kubejs/startup_scripts/globalRemovedItems.js` (`removedItems`/`hiddenItems`)
nem das `stripTags` de `handleItemBlockFluidTags.js` quando a cadeia
semente/produto está quebrada. Casos já removidos: `farm_and_charm:tomato_crop`
(colhia `farm_and_charm:tomato`, REMOVIDO), crates `carrot/potato/beetroot` do
Farmer's Delight, `rich_soil_farmland` (REMOVIDO) e sementes/loot bloqueados em
`loot.py`/`clutter.py`.

- `*_concrete_powder` NUNCA entra nas cidades como bloco colocado (2026-10-09):
  powder obedece gravidade e a casa "se desmancha" ao gerar; usar sempre o
  bloco pronto (`minecraft:*_concrete`). `mapping.swap_material` converte
  powder em concreto, `mapping.FURN` não gera powder e `validate.py` barra
  (`concrete powder nas cidades`).

- `farmersdelight:rich_soil` NÃO entra nas hortas: o modpack desativou a enxada
  nele (`disableHoeRichSoil.js`), removeu a receita e a variante molhada; a
  farmland continua vanilla. Adubo válido é o `farm_and_charm:fertilizer`
  (vende no Market).
- Conferência antes de cada rebuild:
  `python3 -c` comparando os ids usados em `sunlit_tools/towns/*.py` com
  `removedItems` + `hiddenItems` + `stripTags` (ver `itemcheck.BANNED`, que
  já une as três listas; `bad_item` barra no loot e `bad_crop` na plantação;
  blocos colocados precisam da conferência manual).

## Backups: manter apenas um

# REGRA OBRIGATÓRIA — BACKUPS: MANTER SEMPRE APENAS UM (2026-10-10, pedido do dono)

- A pasta `backups/` (AromaBackup) mantém SEMPRE apenas UM arquivo: o mais
  recente. Ao final de cada sessão, apagar os mais antigos e ficar só com o
  último (`ls -t backups/*.zip`).
- O mesmo vale para `options.txt.bak-*`: cópias de segurança do `options.txt`
  não se acumulam; manter só a mais recente (ou apagar todas quando o
  `options.txt` atual estiver confirmado).
- Backups e caches de save nunca entram no `Modpack.zip`.

## Mods desativados

# REGRA OBRIGATÓRIA — MODS DESATIVADOS (2026-10-14, pedido do dono)

- Mods desativados ficam em `mods/` renomeados para `.jar.disabled` e com
  `isEnabled: false` em `minecraftinstance.json` (padrão do CurseForge). Não
  reativar nem atualizar esses mods sem pedido do dono. No `Modpack.zip` vai o
  `.jar.disabled` no lugar do `.jar`.
- Lista atual (2026-10-24):
  - `vminus-3.1.2-forge-1.20.1.jar.disabled` (V-Minus). Motivo: a flag
    `hasExecuted` do `LevelLoadEventHandler` é zerada a cada unload de
    dimensão, e o mod chama `server.reloadResources` uma vez por dimensão ao
    entrar no mundo (5 recargas de ~50 s com 29 mil receitas), deixando o
    carregamento em 0% por ~5 min. O Botania também avisa que o V-Minus quebra
    receitas customizadas. Dependência apenas opcional de Botania e Every
    Compat. O `Compat_FarmersDelight.jar` continua ativo: é um datapack
    (lowcodefml) sem dependência declarada; só os arquivos
    `block_visions`/`item_visions` dele ficam sem efeito.
  - `journeymap-1.20.1-5.10.3-forge.jar.disabled`: mapa fica no FTB Chunks.
  - `jmi-forge-1.20.1-0.14-48.jar.disabled`: integração do JourneyMap, sai junto.
  - `xaeroworldmap-forge-1.20.1-1.46.0.jar.disabled`: um mapa só (FTB Chunks).
  - `ConstructionSticks-1.20.1-1.2.7.jar.disabled`: Construction Wand + FTB Ultimine já cobrem.
  - `animal_pen-forge-1.20-2.4.3.jar.disabled`: desativado pelo dono em 2026-10.
- Ao adicionar mods novos, conferir que nenhum exige `vminus` como dependência
  obrigatória (`META-INF/mods.toml`, `mandatory=true`).

## Ajustes de gameplay

# REGRA OBRIGATÓRIA: AJUSTES DE GAMEPLAY (2026-10-18)

### Durabilidade

- Ferramentas e armaduras NÃO perdem durabilidade com o uso; só perdem ao morrer.
- Implementado em `kubejs/server_scripts/playerEvents/infiniteDurability.js` (fonte da verdade).
- Usa a tag NBT de piso `SunlitWear`, mantida a cada tick na hotbar, armadura e mão secundária, e a cada 20 ticks no inventário principal.
- Ao morrer, hotbar e armadura perdem `floor((max*0.15+15)/(1+unbreaking))`, sempre preservando pelo menos `min(max-1, max(10, ceil(max*5%)))`.
- Elytra fica fora da regra.
- Reparo único por jogador, controlado pela flag `sunlitWearMigrated` no `persistentData`.
- `config/unbreakable-common.toml` é config órfã: o mod Unbreakable/Durability Rework não está carregado. Não editar esse arquivo para mudar durabilidade.

### Puffish Skills: valores de velocidade reduzidos

- Parkour `fast_feet` sprinting_speed: 0.25 -> 0.075.
- Adventuring `quick_feet`: 0.2 -> 0.1.
- Farming speed: 0.05 -> 0.03.
- Arquivos de lang (en_us, es_es, fr_fr, ko_kr, zh_cn) já atualizados.
- NÃO aumentar esses valores de volta.

### Quark: botões de baú

- `config/quark-common.toml`, "Chest Button Slot Target" = 9 (era 27).
- Motivo: os botões de sort/transfer do Quark precisam funcionar nos drawers/armários do MrCrayfish Refurbished Furniture, que usam ChestMenu vanilla com 1 ou 2 linhas (9 ou 18 slots).
- Manter em 9.
- O Slot Target só controla se os botões aparecem. O sort não funcionava porque o
  `canPlaceItem` do `BasicLootBlockEntity` (Refurbished) recusa slots com stack cheio
  ou item não empilhável, e o `SortingHandler` do Quark aborta em silêncio quando
  `isItemValid` falha em qualquer slot.
- Correção: mini mod próprio `mods/sunlit_sortfix-1.0.0.jar` (mixin que faz o
  `canPlaceItem` desse block entity aceitar qualquer item, como o baú vanilla).
  Fonte e `build.sh` em `custom-mods/sunlit_sortfix/` (precisa de um JDK 17).
  Não remover o jar; se o Refurbished for atualizado, conferir se o bug persiste.

Data da regra: 2026-10-18

## Preços e etapas de processamento

# REGRA OBRIGATÓRIA: CADA ETAPA DE PROCESSAMENTO SOMA VALOR (2026-10-25, pedido do dono)

- Todo produto processado vale mais que a soma dos seus ingredientes: cada etapa
  do processo (cortar, espremer, cozinhar, misturar etc.) adiciona um acréscimo
  pequeno sobre o custo dos ingredientes daquela etapa.
- Referência: custo dos ingredientes x1,35 por etapa (era x1,25 até 2026-10-29;
  o dono pediu etapa mais forte). Um produto de duas etapas é calculado em
  cascata (a saída da primeira etapa vira o custo da segunda).
- Se o insumo for sazonal (colheita com tag de uma ou mais estações do Serene
  Seasons, mas não de todas), o acréscimo da etapa é maior: +8% extra, ou seja,
  x1,46 por etapa em vez de x1,35.
- Já aplicado nos sucos (`kubejs/startup_scripts/globalRegistry*.js` e
  `globalPriceBalance.js`). Preços novos de produtos processados seguem a mesma conta.

### Exemplo: ovo frito

- Ovo cru = 4, ovo frito = 5 (4 x1,35 = 5,4 -> 5).
- Em cascata, com o ovo frito como ingrediente: Bacon com Ovos 34 -> 35 e
  Arroz Frito 84 -> 85 (arredondados para moeda).
- **Ainda em aberto:** `farmersdelight:fried_egg` vende por 20 em
  `kubejs/startup_scripts/globalRegistryExtraPrices.js`, mas pela regra seria 5.
  Não alterado até o dono decidir.

### Preço das colheitas cruas (2026-10-29, pedido do dono)

- Colheita fácil (multi-colheita ou ciclo curto: berries, grãos, cana, cacau,
  nether wart, uvas, folhas de chá/café, cogumelos, maçã, cereja): valor / 3.
- Hortaliça de colheita única (raízes, folhosas, frutos grandes como melão e
  abóbora, e as fatias deles): valor / 1,5.
- Colheita rara ou lenta (frutas de árvore, `society:ancient_fruit`,
  `society:mana_fruit`, `society:sparkpod`, `society:mossberry`,
  `society:tubabacco_leaf`, `minecraft:torchflower`, `supplementaries:flax`):
  valor não muda.
- Caixas, sacos, fardos e blocos acompanham o fator do item base.
- Implementado em `kubejs/startup_scripts/globalPriceBalance.js` (priority -30,
  roda depois de todos os registries e reescreve `global.crops` + `global.trades`).
  Não editar os valores à mão no `globalRegistry.js` para esses itens: o script
  sobrescreve.

### Bônus sazonal da caixa de envio

- O bônus de +8% da caixa de envio na estação certa vale só para colheitas
  cruas com tag do Serene Seasons (`global.getSeasonalMultiplier` em
  `kubejs/startup_scripts/globalShippingBinHandlers.js`). Era +20% até
  2026-10-29 (o dono achou alto demais).
- Produto processado não recebe esse bônus na venda: o peso sazonal dele já
  entra no preço pelo acréscimo maior da etapa.
- Colheitas do ano todo (com as quatro tags de estação) não recebem bônus.
- Colheita externa cuja planta cresce o ano todo usa a tag própria `society:<estação>_bonus_crops` (`bonusSeasonCrops` em `handleSeasonTags.js`): dá o bônus, não muda o crescimento e não conta como insumo sazonal para o x1,46. Fruto de planta já sazonal no próprio mod usa a tag do Serene Seasons, com a estação do bloco. Duplicado conta também as estações do item canônico.

### Tooltip de preço: bônus sazonal e de subprocesso (2026-10-29)

- `kubejs/client_scripts/tooltips/addPriceTooltips.js` mostra, abaixo do valor:
  - `Colheita sazonal: 3 moedas (+8%)` quando a colheita crua está na estação
    dela — as moedas são quanto o bônus soma no valor final (já com a qualidade)
    e a porcentagem vai entre parênteses;
    se o arredondamento der 0 moedas, a linha fica só `Colheita sazonal: +8%`
    (`item.society.seasonal_bonus_only`);
  - `Subprocessos: 316 moedas (+1580%)` para itens feitos nas máquinas da
    Society (bebidas, queijos, conservas, óleos, tecidos etc.), calculado em
    `kubejs/startup_scripts/globalProcessValue.js` (priority -40): valor da saída
    menos o custo do ingrediente dividido pela quantidade de saída.
- Itens sem receita de máquina conhecida (comidas de mods) não mostram a linha de
  subprocessos. Receitas alternativas usam o ingrediente mais caro (bônus menor).
- Textos em `kubejs/assets/society/lang/{pt_br,en_us}.json`
  (`item.society.seasonal_bonus`, `item.society.subprocess_bonus`).

### Itens de mods externos (2026-11-03)

- Colheita externa entra nas listas `EASY_CROPS`/`NORMAL_CROPS` de
  `globalPriceBalance.js`; o script agora também lê `global.fruits` e o item canônico
  (`global.canonicalItems`) recebe o mesmo preço do duplicado que substitui.
- Sucos de Hearth and Harvest e Tavern: (2 frutas + 1 açúcar) x1,35, em `globalPriceBalance.js`.
- `kubejs/startup_scripts/globalRegistryExternalItems.js` (priority -25) tira colheita crua,
  semente e saco de `global.cooking` (ficam sem a tag `society:dish`), corrige vinho abaixo
  do custo e dá preço a item sem preço: torta, bolo e queijo inteiros valem a soma das fatias.
- Máquinas: fruta ou colheita externa sem produto próprio reaproveita a saída do equivalente
  (uva de ouro e de gelo viram conserva de uva branca e passas).
- `sunlit_tools/js_harness/registry_audit/run.sh` carrega todos os registros no Rhino do mod e
  grava `dump.json` com preços, listas e máquinas, para comparar antes e depois.

### Exceções

- Produtos artesanais das máquinas da Society (conserva, barril, chás e sidras
  envelhecidos) seguem a fórmula original do pack. Não recalcular esses preços
  com a regra das etapas.
- Saídas do Seed Maker não são etapa de processamento: não recebem o fator de etapas nem bônus de
  subprocesso. A venda de uma operação (3 colheitas) nunca passa do valor das colheitas, com qualidade
  e bônus sazonal incluídos. `globalPriceBalance.js` limita o preço sozinho; ao mudar receita ou preço,
  conferir com `sunlit_tools/js_harness/registry_audit/seed_maker_audit.py <dump.json> --list`.

Data da regra: 2026-10-25

## KubeJS: pegadinhas do Rhino (2026-10-29)

- **NUNCA declarar `const`/`let` dentro de bloco no topo de um script de startup**
  (`if (...) { const x = ... }`, `for (...) { let y = ... }`). O Rhino do KubeJS
  hoista a declaração para o escopo do script e o script morre com
  `TypeError: redeclaration of var <nome>`, mesmo na primeira execução. Ou
  declare no topo do script, ou ponha o corpo dentro de uma função.
  Exemplo corrigido: `kubejs/startup_scripts/globalPriceBalance.js`.
- Declarações dentro de função (inclusive arrow functions de `forEach`) estão OK.
- **`Map`/`Set` guardados em `global` mudam de tipo quando outro script lê.**
  `global.wineKegRecipes` é `Map` no script que o criou, mas pode chegar como
  lista (`Array`) em outro script. Nunca chamar `.get()` direto: testar
  `Array.isArray()` **antes** de `typeof x.keys === "function"` (lista também tem
  `.keys()`, e aí `.get()` estoura `Cannot find function get`). Para dados que
  atravessam scripts, guardar **texto** (`global.processValue[id]` =
  `"moedas|porcentagem"`) e ler por colchete; objeto aninhado pode chegar como
  JSON e quebrar `info.coins`.
- Script de startup roda mais de uma vez por sessão (cliente + servidor). Script
  que multiplica/dividir preço precisa de flag de idempotência
  (`global.priceBalanceApplied`).
- `global.extractinatorRecipes` é lista de `{ input, output }`, não `Map`; as
  receitas de máquina usam `output`, a prensa de conserva usa `pickle`.

