# Estudo do modpack

Levantamento das mecânicas do **Society: Sunlit Valley** (wiki em sunlitvalley.miraheze.org, missões e configs da instância) que podem virar conteúdo nosso. Este estudo tem três usos: dar tema às **construções** das vilas (ver [[casas]]), embasar o texto do **menu inicial** sobre o que muda na nossa edição e servir de pauta para **guias** ao jogador.

## Alto nível

O Sunlit Valley é um Stardew dentro do Minecraft. O jogador planta, cria animais, processa produtos em **máquinas artesanais** e vende tudo no **Shipping Bin**, que paga às 6h. Quase todo item vendável mostra moedas no tooltip, e a **qualidade** (Normal, Prata, Ouro, Irídio) multiplica o preço.

O ponto que mais rende tema é que várias regras do Minecraft comum **não valem** aqui. Água ao lado não molha a farmland, semente não cai de planta quebrada e animal triste dá produto ruim. Cada regra quebrada é um problema que o jogador precisa resolver com uma **ferramenta** ou **bloco**, e esse item pode ser o loot de uma casa temática. Assim a vila ensina a mecânica sem tutorial.

Por cima do pack, a nossa edição soma o **Legendary Survival Overhaul** (LSO), com temperatura no modo HARD, sede, vida extra e dano por parte do corpo. Atrelada ao **Serene Seasons**, a temperatura cai até -12 no meio do inverno, então o jogador precisa de **roupa de frio**. O pack base não tem nada disso.

## Baixo nível

```py title:Plantio
hidratacao: "regador, sprinkler, chuva, garrafa ou poção splash"  # água adjacente NÃO hidrata
solo_seco: "chance alta de virar terra e destruir planta e semente"
crescimento: "1x por dia às 6h, só com solo hidratado e estação certa"
quebrar_planta: "não devolve semente"  # colher com clique direito mantém a semente
fertilizante: "clique direito na farmland: velocidade, qualidade, hidratação, rendimento"
irridio: "exige Pristine Quality Fertilizer"
enxada: "diamante ou melhor ara 5x5, as outras 3x3"
seed_pouch: "planta 3x3 agachado"
greenhouse_glass: "ignora estação e bioma infértil"
taiga_e_neve: "sempre inverno"
deserto_selva_savana: "sempre verão (estação úmida ou seca)"
```

```py title:FerramentasDePlantio
regadores: ["meadow:watering_can", "dew_drop_watering_cans:copper_watering_can",
            "dew_drop_watering_cans:iron_watering_can", "...:gold_...", "...:diamond_...", "...:netherite_..."]
sprinklers: ["dew_drop_farmland_growth:iron_sprinkler", "...:gold_sprinkler",
             "...:diamond_sprinkler", "...:netherite_sprinkler",
             "farm_and_charm:water_sprinkler", "society:mana_sprinkler"]
fertilizantes: ["dew_drop_farmland_growth:weak_fertilizer", "...:strong_fertilizer",
                "...:hyper_fertilizer", "...:hydrating_fertilizer", "...:high_quality_fertilizer",
                "farm_and_charm:fertilizer"]
```

```py title:MaquinasArtesanais
"society:tapper": "1 por tronco, receita: balde de madeira, bloco de cobre, 2 fire logs, earth crystal"
    # seiva, pine tar, resina, xarope de bordo, Black Lotus (Wise Oak), Mystic Syrup
"society:auto_tapper": "versão que sai em fluido"
"society:mayonnaise_machine": "1 dia"
"society:cheese_press": "2 dias"
"society:preserves_jar": "5 itens, 3 dias"
"society:wine_keg": "3 itens, 6 dias"
"society:aging_cask": "queijo 3 dias, vinho 6, cerveja 4"  # Broken Clock corta pela metade
"society:ancient_cask": "13 ou 20 dias, exige skill Ancient Aging"
"society:dehydrator": "frutas e cogumelos secos"
"society:seed_maker": "transforma colheita em semente"
"society:charging_rod": "blaze rods + raio = bateria em 4 dias"  # parado no inverno sem Frosted Tip
```

```py title:Animais
afeicao: "0 a 1000, 100 por coração"  # sobe com carinho, ordenha, comida na mão; cocho não conta
humor: "0 a 256, decide a qualidade do produto"
penalidades: ["sem carinho", "sem comida", "espaço apertado", "fora na chuva ou no inverno"]
amantes_do_frio: "precisam de bloco com tag society:cold_block"  # Frostbiter, Penguin, Snow Pig
utilidades: ["Sunlit Crystal (humor bom permanente)", "Magic Shears"]
```

```py title:Pesca
fatores: ["estação", "local (oceano, rio, água doce)", "clima", "hora"]
crab_trap: "crabbersdelight, funciona em qualquer fonte de água ou lava"
fish_pond: ["society:fish_pond", "society:fish_pond_basket", "society:fish_pond_manager",
            "society:fish_pond_hatchery"]  # gera ova; ova sobrando vai para o roe recycler
```

```py title:ArvoresFrutiferas
primavera: ["cereja", "limão", "lichia", "maracujá"]
verao: ["banana", "limão", "manga", "laranja", "pêssego"]
outono: ["maçã", "canela", "avelã", "pawpaw", "ameixa"]
inverno: ["canela", "pitaya"]
regras: "só cresce e só colhe na estação dele; Tree Fertilizer acelera"
```

```py title:Vilarejo
moradores: ["Ace (carpinteiro e convites)", "Aiden (ferreiro)", "Leon (mercado)", "Maria (pastora)",
            "Haruna (pesca)", "Caroline (banco, vende o Phone)", "Veronica (biblioteca)",
            "Evelyne (bruxa, depois do Nether)", "Carlos (mercador, depois do Skull Cavern)"]
villager_home: "bloco que fixa a casa do morador; quebrou, ele vai embora"
convite: "1 a cada 10 dias"
lojas_escondidas: ["Ribbit Merchant", "Ribbit Fisher", "Wandering Baker", "Wandering Winemaker"]
```

```py title:Sobrevivencia  # só na nossa edição (LSO 2.4.7)
temperatura: "HARD, ligada ao Serene Seasons"
    # primavera -3/0/+3, verão +6/+10/+6, outono +3/0/-3, inverno -7/-12/-7
casacos: ["heating_coat (I a III)", "cooling_coat (I a III)", "thermal_coat (I a III)"]
    # costurados na armadura pela sewing_table; resistência 2, 3 e 4
blocos: ["heater", "cooler", "thermometer"]
sede: "ligada; canteen e large_canteen, versões purificadas"
vida: "Health Overhaul ligado, até 10 corações extras"
dano_localizado: "ligado, headshot causa o dobro"
```

#### Regras de negócio

- Toda construção nova segue o [[casas]]: componentes, tema, retoque e loot por andar.
- Horta de vila continua só com cultura de todas as estações, então o tema de rega não muda a lista de culturas. Batata e cenoura estão na blacklist, então ficam fora da horta.
- Ferramenta de mecânica (regador, sprinkler, fertilizante) é loot raro e de nível baixo, como cobre, ferro e weak. As versões diamante e netherite ficam para o jogador fazer.
- Máquina artesanal entra como decoração funcional da casa, nunca como pilha dentro do baú.
- Bloco de frio (`society:cold_block`) entra em celeiro de bioma nevado, para que o animal de lá não nasça triste.
- Nenhum item de construção pode estar na lista de bloqueados das vilas.

## Temas de construção propostos

- **Floricultura / casa do jardineiro**: estufa com Greenhouse Glass, canteiros com sprinkler embaixo de laje e regador pendurado. O loot traz o regador de cobre ou ferro, sprinkler de ferro, weak e hydrating fertilizer, Seed Pouch e sementes. Ensina na prática que água não rega.
- **Casa do seringueiro (tapper)**: cabana no meio de árvores grandes, com tappers nos troncos e barris de seiva e resina. O loot traz xarope, pine tar e as peças da receita do tapper. O pomar de seringueira não entra na lista de culturas da horta de vila.
- **Adega artesanal**: porão com Aging Cask e Ancient Cask decorativos. O loot traz um Broken Clock raro e garrafas. Junta com a adega que já existe no [[casas]].
- **Vinícola**: casa grande ao lado do vinhedo dos bairros rurais, com Wine Keg e Preserves Jar.
- **Laticínio**: celeiro com cheese press e mayonnaise machine. O loot traz Animal Feed Sack (`society:animal_feed_sack`), Steamed Milk (`society:steamed_milk`) e bolo.
- **Celeiro de neve**: só em bioma nevado, com cold blocks e cocho. Bom lugar para os casacos de calor.
- **Torre de raio**: torre alta com Charging Rod no topo (sem Frosted Tip ela fica parada no inverno, o que vira dica de guia).
- **Cabana do pescador**: perto das docas, com Fish Pond, Crab Trap e isca no loot.
- **Alfaiataria**: sewing table, manequins (armor stands) e lã. O loot traz casacos de calor e de frio e um termômetro. É a ponte direta para o guia de frio.

Os nove temas já estão implementados, ver [[casas]], seção "Construções temáticas". Ficaram de fora: a restrição ao bioma nevado do celeiro de neve, a posição perto das docas da cabana do pescador, os manequins (armor stands) da alfaiataria e o vinhedo do bairro rural da vinícola.

## Pauta para o menu inicial

O changelog do menu (`config/fancymenu/assets/changelog_pt_br.markdown` e `changelog_en_us.markdown`) agora abre com uma intro curta por categoria: Sobrevivência, Vilas, Movimento e ferramentas, Fazenda, cozinha e decoração, Mods desativados, e Removido. Cada categoria precisa de um ou dois itens reais do jogo:

- Sobrevivência: frio e calor de verdade, o inverno chega a -12, então leve casaco costurado na armadura.
- Vilas: casas mobiliadas e moradores que aparecem com o avanço.
- Movimento e ferramentas: regador, sprinkler e a pesca com armadilha.
- Fazenda, cozinha e decoração: qualidade, máquinas e blocos de casa.

## Pauta para guias

- **Frio e calor**: estações e temperatura, casacos, sewing table, heater e cooler, termômetro.
- **Rega**: por que a água não serve, regador, sprinkler, fertilizante hidratante.
- **Qualidade**: fertilizante, humor dos animais, Pristine para Irídio.
- **Máquinas e tempos**: tabela de dias por máquina.
- **Moradores**: ordem de convites e o que cada um vende.
- **Pesca**: fatores de captura, crab trap, fish pond e ova.

Os seis guias já estão no capítulo Guias da árvore de missões (`config/ftbquests/quests/chapters/guias_pipinha.snbt`). Cada um aponta para a missão que tem mais detalhe.

## Anotações

Os IDs acima existem?
> Os de `society`, `dew_drop_*`, `meadow`, `farm_and_charm` e `crabbersdelight` aparecem nos scripts KubeJS da instância. Os do LSO foram conferidos no jar: `legendarysurvivaloverhaul:heating_coat_1` a `_3`, idem `cooling_coat` e `thermal_coat`, mais `sewing_table`, `heater`, `cooler`, `thermometer`, `canteen` e `large_canteen`.

O casaco pode ir pronto no baú?
> Sim. O coat é um item avulso que o jogador aplica na armadura pela sewing table, então cabe no baú da alfaiataria e do celeiro de neve.

Esses itens estão na lista de bloqueados das vilas?

> Nenhum deles. A lista fica em [[blacklist]], e o validate.py confere as construções novas contra ela.

O menu ainda tem a seção "O que muda para você"?

> Não. O changelog do menu ganhou uma intro curta por categoria, em pt-BR e en_us, em vez da seção "O que muda para você".

**Ainda em aberto:** páginas da wiki ainda não lidas: Skills, Create, Bundles, Slimes, Longwings, Sell Values.
