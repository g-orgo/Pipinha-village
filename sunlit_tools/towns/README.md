# Sunlit Towns (Lost Cities)

A base foi convertida uma vez do DCTweaks do DeceasedCraft (modpack ja desinstalado). O datapack `moonlight-global-datapacks/sunlit_towns` convertido agora e a base que os scripts editam.

## Regenerar

```sh
cd sunlit_tools/towns
python3 build_registry.py   # sempre que mods entrarem/sairem ou mudar globalRemovedItems.js / quark-common.toml
python3 houses.py           # casas comfy (casafazenda, padariacomfy, oficinacreate)
python3 cozy_expansion.py   # cozinhas kaleidoscope, adega/vinhedo, porto
python3 vila.py             # 4 depositos (loot sunlit:deposito); as casas da vila vem do schematics.py
python3 remodel.py          # refaz as 10 construcoes proprias com a casca de galpao.py (ver abaixo)
python3 schematics.py       # casas da vila a partir de ../schematics/*.schem|.nbt (--stats so mostra)
python3 finalize.py         # unifica tudo no namespace sunlit
python3 polish.py           # polimento 3D das partes (ver abaixo); --detalhe lista o que mudou
python3 complexes.py        # lotes tematicos de 3-4 chunks e fazenda 6x6 (depois do polish)
python3 cellar_access.py     # escada ate poroes sem acesso (antes do validate)
python3 validate.py         # tem que terminar em "OK"
```

> O datapack nao e mais apagado: `houses.py` e `cozy_expansion.py` regravam
> o proprio conteudo (predios, parques, multibuildings, scattered e loot proprio)
> por cima do pack existente.

## Arquivos

- `convert.py`: legado, nao rodar (DeceasedCraft desinstalado).

- `build_registry.py`: blocos/itens validos (blockstates e modelos dos jars, menos itens removidos pelo KubeJS e modulos desligados do Quark).
- `mapping.py`: troca de blocos DC pelos daqui (forma + material + madeira/cor + tipo de movel). Conteudo apocaliptico vira ar.
- `loot.py`: temas de loot e escolha do tema por predio + movel.
- `enrich.py`: decoracao extra nos cantos dos comodos (Create nas oficinas).
- `parks.py`: hortas, curral, pomar, praca, feira, jardim, fonte, canteiro, poco, postes.
- `houses.py`: casa fazenda, padaria e oficina Create (predios 16x16 + wiring da vila/centro).
- `cozy_expansion.py`: cozinhas kaleidoscope, adega/vinhedo vinery e porto (ver abaixo).
- `interior.py`: mobilia dos predios de `houses.py`/`cozy_expansion.py`. Aloca os chars da
  paleta sozinho, resolve o `facing` pela convencao de cada mod e aborta se um movel
  "de parede" nao tiver parede atras ou se algo bloquear porta/escada.
- `functions/`: funcoes manuais copiadas para `sunlit:` (`/function sunlit:villagers_here` etc.).

## Expansao cozy (`cozy_expansion.py`)

- `building_cozinhakaleido` (vila): casinha com cozinha INTEIRA de
  kaleidoscope no terreo (stove + pot + stockpot + chopping_board +
  kitchenware_racks + oil_pot + enamel_basin) e sala de jantar; quartos em cima.
- `building_adegavinho` (vila, centro): adega vinery no terreo
  (fermentation_barrel + wine_rack + apple_press + mesa de degustacao) e
  moradia em cima. Loot novo `sunlit:cellar` (uvas, sucos e vinhos).
- `building_armazemporto` (vila, industrial): armazem/trapiche com deck de
  madeira, caixas, barris e escritorio da doca. Loot novo `sunlit:dock`
  (peixes, corda, lanterna, barco).
- parque `vinhedo`: talhoes de parreira red/white grape em farmland com
  mouroes de tora + mesa de degustacao (seletor `parks` da vila). Sem `vinery:*_lattice`: o estado
  real dela vem do block entity e o Lost Cities a coloca torta.
- `multi_porto` (1x1, reusa o armazem): entra no `scattered` de
  `worldstyles/towns.json` com bioma `if_any: [is_river, is_beach]` — ou
  seja, o porto nasce FORA das cidades, perto de rio/praia. O Lost Cities
  nao tem seletor "perto do rio" dentro da cidade, por isso o porto urbano
  (vila/industrial) e o porto ribeirinho (scattered) sao a mesma construcao
  nos dois lugares.

## Mistura geral (2026-10-03, v2)

- `mix.py`: fogao, panela, tabua, caixotes/sacos, cestos e colheitas viram lista `blocks`
  com `random`: o Lost Cities sorteia o mod em cada bloco (casas importadas, parques e casas
  proprias). Trocando refurbished <-> outro mod o facing gira 180.
- `vila.py`: depositos (as casas variadas que ele gerava foram trocadas pelas de `schematics.py`;
  os temas de comodo ficam no arquivo so como referencia). `convert.py:mixed_pool()` poe esse conteudo em TODOS os bairros com peso maior
  que as casas importadas (0.07 por rotacao). O porto (armazemporto/doca) so existe nas docas.
- `finalize.py`: move o namespace importado para `sunlit` (o datapack inteiro fica `sunlit:`).
  Depois: escala listas `random` para soma >= 128 (abaixo disso o Lost Cities aborta o chunk com
  "Not enough blocks in the random list"), completa `sunlit:common` com os chars de default/common do
  Lost Cities (rodovia em curva/T usa partes dele, ex.: `w` de `highway_bridge_bend`) e encurta os nomes
  de palettes/parts/buildings/multibuildings (o Explorer do Windows nao extrai caminho > 260;
  `validate.py` exige no maximo 120 chars a partir da instancia).
- Praca com waystone em todos os bairros (parks) e `waystone_rua` no slot fountains.

## Polimento 3D (`polish.py` + `lcparts.py`, 2026-10-03 v4)

Roda no datapack final (tudo `sunlit:`). `lcparts.py` le parte + paleta + `sunlit:common` e nunca edita
entrada existente de paleta (sao compartilhadas): cada mudanca aloca um char novo (pool ASCII, Latin-1,
grego, cirilico). As categorias olham so o NOME do bloco (sem namespace): `buildersdelight`/`farmersdelight`
contem "light", `vinery` contem "vine", `candlelight` contem "candle".

- movel de chao em cima de movel: pia/vaso/fogao em cima de armario desce com o que estava preso nele
  (espelho) e o armario vai para baixo do teto com prateleira do Another Furniture embaixo; o resto sai.
- bau em cima de fogao/pia/geladeira/assento sai; nada apoiado em bau, saco, cesto, panela, assento, vaso,
  abajur (lista random de caixotes/sacos vira so blocos cheios naquela posicao, re-escalada para >= 128).
- Refurbished: freezer EMBAIXO e geladeira EM CIMA (handle do modelo); facing = costas/parede (porta e
  torneira ficam do lado oposto ao facing). Movel de parede com a frente na parede gira 180 (eram os
  convertidos de outros mods: armario de loot e pia). Coifa sobe ate o teto. Banheira: facing aponta da
  metade `bottom` para a `head` (a head e a ponta fechada).
- folhas/hedge: coluna no maximo 4; parte usada acima do terreo perde a coluna que comeca na fatia 0.
  As colunas que o proprio Lost Cities poe na divisa predio/rua (`randomLeafBlockChance`) sao aparadas
  em jogo por `townTrimLeaves` (sunlitTownsLife.js).
- lanterna vanilla solta ganha corrente ate o teto (ate 4 blocos) ou sai.
- vaso/relogio/maquina de costura no chao (dentro de casa) vai para cima de um movel vizinho ou ganha
  mesinha `redeco:*_side_table`; prateleira vazia ganha enfeite em cima (70%).
- cadeiras da mesma mesa: modelo da maioria, facing aprendido da propria cadeira escolhida.
- cerca de horta (componente de cerca encostado em terra arada/caminho num canteiro com terra arada)
  sobe 1 bloco; embaixo vira tora descascada da mesma madeira (portao fica sobre dirt_path).
- `furniture:street_lantern` vira Illuminant Column (`simplylight:lamp_post` bottom/middle/top); parques
  e fontes ganham fatias se faltar altura.
- loot so fica em bloco cujo block entity e `RandomizableContainerBlockEntity` (lista `LOOT_OK`); o
  resto so gerava "Error setting loot at" no log.
- Bancos, sofas, mesas, bancadas, prateleiras, comodas: a conexao com o vizinho e recalculada em jogo
  pelo updateShape de cada mod (`TOWN_CONNECTABLE` em sunlitTownsLife.js).

## Zonas e mescla de mods (2026-10-03)

- `mapping.py`: `pick()` sorteia por predio (`M.SALT = bname` no `convert_palette`), entao o
  mesmo bloco DC vira fogao do Refurbished, Farmer's Delight, Candlelight, Kaleidoscope ou
  Let's Do dependendo do predio; caixotes/cestos/estoque tambem misturam Hearth & Harvest,
  Cultural Delights, Crabber's Delight, Let's Do etc.
- `parks.py`: `horta_sobrevivencia` (Legendary Survival + Cultural Delights + Kaleidoscope),
  `horta_graos`, `pomar_frutas` (Hearth & Harvest, Farmer's Respite, Vinery), `celeiro`, `doca`
  (Crabber's Delight, Youkai) e `praca_waystone` (a Waystones gera nome e registra sozinha).
- Citystyles novos: `sunlit:rural` (peso alto em plains/meadow/savanna/flower_forest) e
  `sunlit:docas` (rio/praia). Pesos em `RURAL_PARK_WEIGHTS` / `DOCAS_PARK_WEIGHTS`.

## Hedges

- `tidy_hedges` (convert.py): hedge que comeca na fatia 0 de andar superior e continuacao do
  andar de baixo (vira ar/musgo); hedge sem apoio vira folha persistente; altura maxima 4;
  luminaria em cima de hedge some; pilar (muro/cerca) em cima substitui a hedge.
- `fix_hedges`: tudo vira Refurbished (a hedge do cfm so liga com cfm; a do Refurbished liga
  com qualquer Refurbished, folha e face solida).
- Em jogo, `sunlitTownsLife.js` recalcula com `Block.updateFromNeighbourShapes` (chunk + anel
  dos vizinhos). `updateNeighborsAt` nao serve: so chama neighborChanged.

## Saves ja existentes (jogo fechado, faca backup antes)

- `../regen_chunks.py "<save>"`: apaga do overworld os chunks sem jogador (raio 5 em volta da
  posicao/spawn dos jogadores + InhabitedTime >= 10 min ficam) e as entradas de entities/poi;
  o jogo regenera com a worldgen atual. Mova `data/DistantHorizons.sqlite` para o LOD refazer.
- `../retrofit_hedges.py "<save>"`: religa as hedges dos chunks que sobraram.

## Regras que nao podem quebrar

- Estado de bloco invalido numa paleta faz o Lost Cities abortar o chunk inteiro (foi o bug do pack antigo).
- **Cada andar de predio tem que ter 6 fatias** (`FLOORHEIGHT = 6` no codigo do
  Lost Cities): ele empilha as partes de 6 em 6 e qualquer parte menor deixa
  uma fatia de ar entre os andares (predio "desconectado", escada quebrada).
  `shell_ground`/`shell_floor` ja retornam 6 fatias com teto duplo; o `top`
  pode ter 2 (nada empilha em cima dele).
- A escada (`ladder_shaft`) precisa cobrir as fatias do teto/piso tambem
  (layers `(1..5)` no terreo, `(0..2)` no andar): ladder nao e solido, entao
  ela atravessa a laje e a subida fica continua.
- O char `G` e o filler do building JSON: tem que existir na paleta
  (`base_palette` ja inclui `G = stone_bricks`), senao o preenchimento abaixo
  do predio fica indefinido. Nao reuse `G` para moveis.
- Predio com `floor` explicito em todas as partes precisa cobrir todos os
  slots `0..maxfloors` (ex.: cabanas DC com partes 0/1/2 e min/maxfloors=3
  quebram o chunk com "Misconfiguration! No part condition matches" — o
  `convert.py` trava no maior floor declarado e o `validate.py` acusa).
- Convencao de `facing` (medida nos predios DC): `refurbished_furniture` aponta para a
  PAREDE (costas; cadeira/sofa apontam para longe da mesa); farmersdelight, bakery,
  vinery, kaleidoscope, another_furniture, candlelight, supplementaries e bau/barril
  vanilla apontam para a FRENTE (cadeira kaleidoscope/another_furniture olha para a
  mesa); cama aponta a cabeceira. Em `simplylight` o `facing` aponta para longe do
  apoio (`facing=down` = preso no teto): `convert.py`/`defloat` usa isso.
- Interior dos predios novos: faixa de janela em y2, entao moveis altos so nos cantos,
  arandelas e lanternas em y3 (encostadas no teto/parede), nunca bloco de luz solto no ar.
- O KubeJS confere tudo de novo ao carregar o mundo: procure `[Sunlit Towns]` no `logs/latest.log`.
- Vida nas cidades: `kubejs/startup_scripts/sunlitTownsLostCities.js` (fila) + `kubejs/server_scripts/sunlitTownsLife.js` (povoa).
- Perfil: `config/lostcities/profiles/sunlit_cozy.json` com `worldStyle = sunlit:towns`. Desde 2026-10-03 v4 as faixas
  `cityLevelNHeight` vao de 12 em 12 (78, 90, 102...) com `useAvgHeightmap`: menos degraus de nivel na cidade.
- Packs antigos ficaram em `sunlit_tools/backup_datapacks_2026-10-02/`.

## Casas da vila de schematics (`schematics.py` + `vanilla_furni.py`, 2026-10-03 v5)

As casas da vila (antes geradas em `vila.py`) vem dos schematics em `sunlit_tools/schematics/`
(.schem Sponge v2/v3 e .nbt de structure block, lidos por `schem.py`). `CASAS` define por casa a
janela recortada (x0/z0 no schematic, cw x cl chunks) e a altura do chao (fatia 0 = grama/caminho;
o que fica abaixo sai, buraco no chao vira grama).

- 4 rotacoes por casa (`rot_state` gira facing/axis/rotation/north..west/shape de trilho).
- 1 chunk -> predio `sunlit:vila_<casa>/r<rot>c00`; maior -> `sunlit:multi_vila_<casa>_r<rot>`
  (multibuilding `buildings[x][z]`, ordem conferida no cafe original). Cada chunk sobe em partes de
  6 fatias com condicao `floor: k`; o resto vai na parte `top`.
- `convert.py` poe `SCH.NAMES` nos buildings e `SCH.MULTIS` nos multibuildings de todos os bairros
  (`mixed_pool`/`mixed_multis`); `towns.json` aceita ate 6 multibuildings por area de 8x8 chunks.
- `polish.py` nao roda `rule_leaves`/`rule_fences` nessas partes (arvores e cercas do jardim sao do
  modelo) e o `sunlitTownsLife.js` nao apara copa de arvore em chunk `vila_*`.

`vanilla_furni.py` troca os moveis "de vanilla" pelos dos mods, so encostados num comodo fechado
(regiao de piso coberta que so abre para fora por vaos de porta; cerca/muro com rua do outro lado
conta como abertura):
- fornalha/defumador/alto-forno (fora de oficina com bigorna/mesa de ferraria) -> fogao (sorteio do mix);
- caldeirao na bancada -> pia de cozinha; sozinho -> lavatorio; funil -> privada;
- 2 blocos de ferro/concreto branco/quartzo com puxador (ou porta de ferro encostada) -> freezer + geladeira;
- bancada (escada/laje de cima ou bloco liso com algo baixo em cima) ligada a fogao/pia/geladeira ->
  kitchen cabinetry/drawer (botao na frente = gaveta), cantos em L incluidos;
- cerca/muro com placa/tapete/laje em cima, laje de cima "suspensa" sobre alcapoes, ou tampo com
  cadeira encostada -> mesa; escada de baixo que nao e degrau nem friso de parede -> cadeira, 2+ lado a
  lado de material macio ou com braco -> sofa; andaime com alcapao de encosto -> cadeira;
- laje dupla/la/concreto + escada do mesmo material -> cama; beacon -> luminaria; redstone e luz invisivel saem.
Comodos com poucos moveis ganham mobilia pelo tema (sala, cozinha, quarto, banheiro, sotao/porao com
pe-direito <= 2) encostada na parede, longe de portas/escadas, mais lanterna no teto se estiver escuro.
Containers sem loot recebem o tema do comodo.

## Remodelacao das construcoes proprias (`galpao.py` + `remodel.py`, 2026-10-03 v7)

Depositos (4), oficina Create, casa de fazenda, padaria, casa da cozinha kaleidoscope, adega e armazem
do porto deixaram de ser a caixa de 16x16: paredes recuadas 1 bloco (x1..14, z1..14), rodape de pedra,
enxaimel com pilares em 1/5/10/14, janelas em pares (y2-y3) com venezianas, alpendre com postes e
lanterna nas portas N/S, telhado de duas aguas com beiral (z0/z15) e empena avancada (x0/x15),
chamine, canteiros, bancos e estoque no quintal. Interior util 12x12 (x2..13, z2..13); escada de mao
em (13,13). `remodel.py` grava os mesmos nomes de parte/predio que houses.py, cozy_expansion.py e
vila.py (por cima), entao o convert.py continua pesando igual. `facade.py` ficou sem alvo.
A oficina ganhou ilha de montagem no meio (crafters, eixo com caixa de engrenagem, mo, deposito).

## Correcoes de 2026-10-03 v7

- `vanilla_furni.py`: cama de la (1-2 x 2-4, cabeceira na parede, tapete/cerca/neve de cima saem);
  cama de casal no canto (near_room com raio 2); funil com gancho/alavanca em cima = lavatorio, escada
  ou laje branca com alcapao de tampa (ou perto da pia) = privada; alcapao/placa em cima da bancada vira
  comida (Display Delight, Cluttered, Kaleidoscope) ou utensilio, panela/frigideira no fogao; alcapao ou
  escada de cima 2-3 blocos acima da bancada = armario de parede (coifa em cima do fogao); mesa suspensa
  aceita vaso em cima (desce junto) e tira a saia de alcapao; laje de madeira com alcapao de encosto e
  tampo do outro lado = cadeira + escrivaninha; movel de mod nao conta como piso de comodo.
- Porao: `CASAS[...]['cellar']` (serrana 3, medieval 6, solar 6) vira parte `cellar` (floor -1) do
  Lost Cities; a boca da escada no chao fica aberta.
- `polish.py`: prateleira so fica baixa quando sustenta container ou e degrau (vira a do another_furniture,
  tampo no alto: a do Candlelight tem a tabua embaixo e tudo em cima flutua); o resto sobe na parede com
  enfeite. Mesinha so sob vaso no chao de verdade. Sensor de luz/redstone solto sai. Cerca de parque nao sobe.
- `sunlitTownsLife.js`: em chunk sem predio, caminho/terra arada/agua em cima do gramado desce para a
  camada dele (o Lost Cities poe a fatia 0 do parque 1 bloco acima da grama); block entity que falta e
  criado (camas sem block entity ficavam invisiveis).

## Correcoes de 2026-10-04

- `galpao.py`: os pilares de tora do enxaimel sairam 1 bloco para fora da parede (meio de cada parede
  em 5/10 e um no canto de fora; o canto da parede continua tora), com sapata de rodape no chao; o poste
  do alpendre virou o proprio pilar. O pendural da empena (z7-8) tambem saiu para x0/x15, apoiado numa
  misula de escada invertida no ultimo andar (`gable_corbel`). Vale para todas as construcoes da casca.
- `remodel.py`: o sotao dos depositos (dentro da parte top) agora tem acesso e uso: escada de madeira na
  parede leste (x13, de z12/y1 a z8/y5) com escada invertida por baixo, teto/forro abertos sobre ela,
  estoque no vao de baixo e guarda-corpo de cerca no piso do sotao. No sotao: catre, bau, gaveteiro com
  vela e estantes no oitao oeste, tapete, caixotes/barris (loot `sunlit:deposito`) nas aguas do telhado,
  sacos onde so cabe 1 bloco e 2 lanternas penduradas na cumeeira. `Build.attic()` devolve o Furnish da
  parte top (y0 = piso).
- `schematics.py`: `RETOUCH` por casa, depois do vanilla_furni e antes da rotacao. `moderna`: mesa de
  escadas invertidas vira mesa refurbished 9x2 com cadeiras dos dois lados, sofa de granito com encosto
  de alcapao vira sofa de verdade virado para a lareira, mesa de centro de vidro fume vira coffee table,
  sai a cama deitada no consolo da lareira, ancient debris (cabeceira) vira tabua de dark oak, bigorna
  sob folhas vira vaso decorado, criados-mudos de escada de deepslate viram gaveteiros com abajur.
  `vermelha`: sai a laje de andesito boiando fora da fachada sul sob as janelas.
- `sunlitTownsLife.js` (`townSinkGround`): o nivel do gramado do parque e detectado (ground ou ground-1,
  o que tiver mais colunas grama + chao de parte em cima). No mapa a horta/jardim estava em ground+1 com
  a grama em ground, e a versao anterior so olhava ground-1 (pegava so colunas soltas). Chunks ja gerados
  precisam ser regerados.

## Correcoes de 2026-10-04 (v10)

- Parques 1 bloco alto: o Lost Cities poe o gramado na altura da rua e a parte do parque em height + 1
  (`generateParkSection` + `generatePart(height + 1)`). `townLowerPark` (sunlitTownsLife.js) baixa a parte
  inteira em chunk com `streetType == PARK`: fatia 0 de chao (caminho, terra arada, agua, piso cheio, tronco)
  desce no lugar da grama, fatia 0 vazia faz o que esta acima descer, objeto na fatia 0 (cerca, banco, poste)
  fica. Block entity desce com os dados. Erro por coluna nao para o chunk (a versao anterior parava com NPE
  e deixava meio parque em cima). O startup ignora PostGen repetido (`global.sunlitTownSeen`).
- Casa virada para a rua: `schematics.py` grava `kubejs/startup_scripts/sunlitTownsFronts.js` (lados com porta
  externa por rotacao); no `PreGenCityChunkEvent` o startup pontua o contorno da casa (rua 3, parque 1) e troca
  o predio do chunk pela rotacao certa com `BuildingInfo.setBuildingType` (multibuilding: mesma rotacao em
  todos os chunks; 3x2 so gira 180).
- Portas duplas: a porta sul da casca (`galpao.py`) tinha as dobradicas trocadas (hinge=left e o lado
  esquerdo de quem olha para `facing`).
- `polish.py`: `rule_multiblock` completa os moveis de varias partes do Cluttered (armario 2x2, poltrona,
  manequim, costura) ou troca por movel de 1 bloco; `rule_table_food` poe comida de bloco nas mesas.
- `loot.py`: comida so em cozinha/mercado/padaria/restaurante; os outros temas ganham pools de equipamento
  (gasto, as vezes encantado), bebidas (agua purificada, sucos, chas, vinhos, pocoes), coisas para cozinhar
  e itens aleatorios dos mods. Item so entra se tiver nome no en_us.json de algum jar (`lang_items.json`,
  cache): o registry.json tem modelos que nao sao itens e item inexistente invalida a loot table.

## Interiores densos, casas tematicas e lotes (2026-10-04 v11)

- `clutter.py` ("block vomit consciente"): depois do `vanilla_furni` e do `RETOUCH`, cada comodo das casas de
  schematic ganha um caminho livre (menor caminho entre portas, escadas, aberturas e o acesso de cada movel
  interativo; celula a mais de 2 blocos do caminho ganha um ramal) e todo o resto e preenchido pelo catalogo
  do comodo: moveis de parede, moveis soltos virados para o caminho, decoracao/comida em cima de toda
  superficie, tapete no meio do caminho, estandartes e prateleiras altas com enfeite nas paredes. Cada peca
  tematica tem limite por comodo; os temas se misturam com moveis comuns. So entra bloco que existe de verdade
  (registry + nome no en_us do mod) e de 1 bloco so.
- Armor stand: `clutter.py` grava `minecraft:structure_void`; o `sunlitTownsLife.js` troca por um armor stand
  vestido pelo tema da casa (sufixo do nome: fer, cre, enc/alq, o resto couro/malha).
- Casas tematicas: cada casa de schematic tem 5 versoes (de 7 temas: encantamento, alquimia, create, ferreiro,
  artesao, biblioteca, fazendeiro), `<casa><cod>` (ex. `vermelhaenc`). O tema toma todos os comodos menos
  cozinha, banheiro e o quarto principal.
- `complexes.py`: parques viram predios de 1 chunk (`sunlit:lote/<parque>`) e entram em lotes de 3 chunks
  (3x1 e 1x3) e 4 chunks (2x2) e na fazenda 6x6 (`multi_cx_fazenda_grande`, rural + scattered no campo).
  Todo predio de um lote e copiado com o mesmo numero de andares (o Lost Cities da a todos os chunks os andares
  do chunk do canto; `validate.py` confere). Casa de schematic no lote e copiada nas 4 rotacoes e vira para a
  rua sozinha.
- `validate.py` tambem barra: parque fora da convencao da camada do chao ou com bloco solto no ar, cebola em
  qualquer paleta, multibuilding com andares diferentes.

## Variedade e espalhamento das casas (2026-10-16)

- `convert.py:509-511` `VARIETY`: vermelha 0.5, fada 0.5, robella 1.0, cerejeira 1.0, serrana 1.0, medieval 3.0, moderna 2.0, solar 2.5.
- `convert.py:575` bairro 1: `parkchance` 0.55, `buildingchance` 0.12.
- `convert.py:582` centro comercial (`retail_district`): `parkchance` 0.45, `buildingchance` 0.26.
- `convert.py:611`: `parkchance` 0.8, `buildingchance` 0.18, `maxfloors` 3.
- `convert.py:617`: `parkchance` 0.6, `buildingchance` 0.22, `maxfloors` 3.
- `convert.py:649` `multisettings`: `areasize` 8, `minimum` 1, `maximum` 2.
- `complexes.py` nao tem fator de parque proprio; o parque e controlado pelo `parkchance` de cada bairro.

Regra de componentes: ver `docs/casas.md`, secao "Casas como componentes".

## Construcoes tematicas (2026-10-18)

- 9 construcoes tematicas em `schematics.py` `CASAS`, todas com peso 0.25: `floricultura` (cerejeira), `adega` (medieval) e `torre_raio` (solar) vieram antes; `laticinio` (moderna), `vinicola` (medieval), `celeiro_neve` (vermelha), `cabana_pescador` (robella), `alfaiataria` (fada) e `seringueiro` (serrana) entraram agora.
- Cada uma tem `retouch_<key>` registrado em `RETOUCH`, que roda o retoque da base antes do seu.
- `seringueiro`: ate 2 tappers nos troncos, 2 barris e pomar de 4 mudas (`pamhc2trees:apple_sapling`, `orange_sapling`, `cherry_sapling`, `lemon_sapling`) nas celulas livres mais baixas. Contador `seringueiro_pomar`.
- `loot.py` `write_theme_files()` gera, por tema, `data/sunlit/lostcities/conditions/<tema>.json` e `data/sunlit/lostcities/loot_tables/chests/<tema>.json`.
- Ordem para regenerar: `python3 schematics.py`, `finalize.py`, `polish.py`, `complexes.py`, `cellar_access.py`, `validate.py`. O `validate.py` tem que terminar em "OK: nenhum problema encontrado".
- Detalhes e regras: `docs/casas.md`, secao "Construcoes tematicas".
