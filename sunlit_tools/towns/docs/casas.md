# Casas de schematic

## Alto nível

As casas da vila não são montadas à mão no datapack. Cada uma parte de um **schematic** (arquivo `.schem` ou `.nbt`) que já existe, recorta uma janela dele, limpa o que não serve, mobília os cômodos e grava o resultado como **predio** do Lost Cities. Quem faz isso é o `schematics.py`, que substitui as casas antigas geradas pelo `vila.py`.

A ordem do pipeline é: `houses`, `cozy_expansion` e `vila` primeiro, depois o `schematics.py`, depois o `finalize.py`, o `polish.py` (ver [[polish]]) e por último o `validate.py`, que precisa dar OK antes de qualquer entrega. A mobília em si vem de [[clutter]] e a troca de mobília vanilla por mobília de mod vem de [[vanilla_furni]].

Cada casa do catálogo `CASAS` tem uma **janela** (`x0`, `z0`, `cw`, `cl`, em chunks de 16 blocos), um **chão** (`ground`, o `y` do schematic que marca a rua) e opcionalmente um **porão** (`cellar`, camadas abaixo do chão). A janela diz qual pedaço do schematic entra. O chão separa o que é terreno do que é prédio. O porão vira o subsolo jogável do Lost Cities.

Cada definição gera várias variantes. A primeira são as **rotações**: o Lost Cities não gira prédios, então a casa sai em 4 rotações (0, 90, 180 e 270 graus). A segunda são as **colorways**: a casa sai em 3 cores de casca, `c0` (a cor original), `c1` e `c2` (recolorações), para o Lost Cities sortear por chunk sem repetir sempre a mesma cor do lado. A terceira são os **temas**: cada casa base ganha 5 das 7 versões temáticas, com o interior trocado (ver [[temas]]).

Quando a janela cobre mais de um chunk, a casa vira um **multibuilding**: um prédio por chunk, amarrados num JSON de múltiplos. Janela de 1 chunk vira prédio simples.

O **retoque** (ver [[retoque]]) é o ponto que mais muda o resultado. Ele roda depois da casa ser montada e antes da recoloração, então uma correção feita ali chega às três cores e a todos os temas.

Para adicionar uma casa nova, o caminho está na seção "Como adicionar uma casa nova" deste documento. Em resumo: linha nova em `CASAS`, retoque opcional registrado em `RETOUCH`, geração só dessa chave e checagens.

## Baixo nível

```py title:CasaSchematic
CasaSchematic(
    key,          # nome base, ex. 'vermelha'; vira parte do nome do predio
    file,         # arquivo dentro de SRC, ex. 'm-pinkhouse.nbt'
    x0, z0,       # canto da janela no schematic, em blocos
    cw, cl,       # tamanho da janela em chunks (cw x cl)
    ground,       # y do chão no schematic; None = detecção automática
    weight,       # peso de sorteio no Lost Cities
    cellar=0,     # camadas de porão abaixo do chão, máximo 6 (padrão 0)
)
```

```py title:Variante
Variante(
    base,         # key da casa original, ex. 'vermelha' para 'vermelhaenc'
    key,          # base + código do tema, ex. 'vermelhaenc'
    theme,        # ex. 'encantamento'
    weight,       # peso original * 0.35
)
```

```py title:Colorway
Colorway(
    key,          # ckey(key, i): 'vermelha' (i=0), 'vermelha_c1', 'vermelha_c2'
    salt,         # f"{key}|c{i}" para i > 0
    recolor,      # mapping.recolor(state): troca a cor da família casca
)
```

```py title:Predio
Predio(
    name,         # bname(ckey, rot, cx, cz), um por chunk da janela
    rot,          # 0, 90, 180 ou 270
    partes,       # blocos de 6 fatias (FLOOR_H), com condição "floor"
    multi,        # sunlit:multi_vila_<ckey>_r<rot> quando cw * cl > 1
)
```

```py title:Retoque
Retoque(
    base,         # chave registrada em RETOUCH, ex. 'robella'
    funcao,       # def retouch_<nome>(v): recebe o Vox e altera blocos
)
```

```py title:Pipeline
build(cfg):
    g, gy, cel = crop(cfg)           # recorte, chão e porão
    convert_states(g)                # estados vanilla convertidos
    house = VF.House(...)            # mobília vanilla -> mod, cômodos
    house.run()
    RETOUCH[base](v)                 # se a base estiver registrada
    fix_windows(v)                   # janelas e persianas, todas as casas
    house.map_rooms()                # mapeia de novo depois do retoque
    CL.Clutter(house, theme).run()   # mobília densa, caminhos livres
    ladder_mouths(house, v, cel)     # escada das bocas de porão
    for i in range(NCOLORS):         # c0, c1, c2
        for rot in ROTS:             # 0, 90, 180, 270
            grava chunks e multibuilding
```

#### Regras de negócio

- Cada casa gera 3 colorways em 4 rotações. Cada posição de chunk da janela sai com 12 variantes de prédio.
- O retoque roda antes da recoloração, então uma correção vale para `base`, `_c1`, `_c2` e para todos os temas.
- A janela e o chão de uma casa vêm de `CASAS`. Mudar um deles exige gerar a casa de novo e conferir o recorte.
- Casa sem porta de verdade usa uma frente fixa na rotação 0 (hoje só a moderna, via `FRONT_R0`).
- Depois de gravar, `write_fronts()` atualiza o arquivo de frentes que o KubeJS lê.
- Os temas são distribuídos em rodízio, para que cada tema apareça em várias casas da vila.

## Casas como componentes

Cada casa é um componente. As cores (`_c1`, `_c2`) e os temas são instâncias da mesma estrutura, então qualquer correção (retoque, chão, porão, telhado, varanda, janelas e persianas) precisa entrar no nível da base. Assim, todas as variantes herdam a correção sem precisar de uma regra própria para cada uma.

Na prática, a correção vai em `RETOUCH[base]` no `schematics.py` (que roda antes do laço das cores) ou em uma regra que filtra pelo nome base. Nunca se corrige o arquivo de uma variante só.

Isso já causou um bug de "variant drift": uma correção foi aplicada só em uma variante e as outras ficaram com o defeito antigo, como a persiana que faltava e as cercas e escadas enterradas embaixo da varanda da cerejeira.

#### Regras de negócio

- Toda correção vale para base, _c1, _c2 e temas.
- Ao revisar, conferir pelo menos uma variante de cor e um tema além da base.
- Nunca editar o arquivo gerado de uma variante a mão.

## Chão e porão

O **chão** (`ground`) é o `y` do schematic que separa terreno de prédio. Se for `None`, `auto_ground` procura sozinho um nível dentro da janela. Todas as casas atuais têm `ground` explícito.

O **porão** (`cellar`) são camadas abaixo do chão que viram `cellar` do Lost Cities. O valor efetivo é `min(cellar, FLOOR_H, gy)`, então nunca passa de 6 nem da altura do chão. O terreno do schematic vem junto com o porão. Existe a opção `dig`, que escava um porão quando o schematic não tem subsolo, mas nenhuma casa atual a usa.

Depois da montagem, `ladder_mouths` procura bocas de porão dentro de cômodos do térreo e põe uma escada nelas. Sem escada o porão existe mas não tem acesso.

#### Regras de negócio

- Porão só existe onde o schematic tem terreno abaixo do chão, ou quando a casa é marcada para escavar.
- Toda boca de porão dentro de um cômodo ganha escada. Depressão de terreno fora de cômodo não conta.
- Porão nunca passa de 6 camadas.

## Temas

Cada casa base sai também em 5 dos 7 temas, em rodízio. O código do tema vira o sufixo da chave e a mobília muda. A casca é a mesma.

| Tema | Código |
|---|---|
| encantamento | enc |
| alquimia | alq |
| create | cre |
| ferreiro | fer |
| artesao | art |
| biblioteca | bib |
| fazendeiro | faz |

O catálogo de mobília por tema fica em `clutter.py`. O mobiliário vanilla do schematic é trocado por mobília de mod em `vanilla_furni.py`.

#### Regras de negócio

- Cada tema usa o prédio da casa base e só o interior muda.
- O peso de um tema é 35% do peso da base, para as variantes temáticas não dominarem o sorteio.
- O retoque da base também vale para o tema, porque o `build` busca o retoque por `cfg['base']`.

## Retoque

O retoque é uma função que recebe o `Vox` (a grade de blocos já convertida) e corrige o que o schematic ou o mobiliador automático fizeram errado. Ele fica no `schematics.py` e é ligado à casa pelo dicionário `RETOUCH`. Hoje há retoques para vermelha, moderna, medieval, fada e robella.

Além do retoque por casa, `fix_windows` roda em todas as casas: janela não tem parede no meio e persiana fica dos dois lados.

#### Regras de negócio

- Conserto específico de uma casa entra como retoque registrado em `RETOUCH`, não como remendo no arquivo gerado.
- `fix_windows` vale para todas as casas, não só para a que originou a regra.
- Conserto de geometria é feito no `Vox` antes da mobília.

## Como adicionar uma casa nova

1. Colocar o schematic na pasta `SRC` definida em `schematics.py`.
2. Acrescentar uma linha em `CASAS` com `key`, `file`, janela, `ground`, `weight` e `cellar` se houver porão.
3. Se a casa precisar de conserto próprio, escrever `retouch_<nome>(v)` e registrar em `RETOUCH`.
4. Gerar só essa casa passando a chave como argumento: `python3 schematics.py <key>`. Use `--stats` antes, para ver o que muda sem gravar.
5. Conferir o resultado visual.
6. Rodar `python3 validate.py` e só seguir se der OK.

#### Regras de negócio

- A casa nova só entra no datapack depois do `validate.py` dar OK.
- A chave precisa ser única em `CASAS`, porque o nome do predio sai dela.
- Para adicionar uma casa, não se altera nenhum `.py` fora de `schematics.py`.

## Variedade e espalhamento

A meta agora é ter mais **tipos** de casa diferentes, e não mais cores da mesma casa. Ao mesmo tempo, as casas ficam mais espalhadas: menos por bairro e com vãos maiores entre elas. A ideia de que as cidades são grandes, mas difíceis de achar, continua valendo.

Os botões que controlam isso estão abaixo, com os valores atuais lidos do código.

```py title:Espalhamento
# convert.py:509-511, multiplicador de peso por família (sobre o peso base do schematics.py)
VARIETY = {'vermelha': 0.5, 'fada': 0.5, 'robella': 1.0, 'cerejeira': 1.0, 'serrana': 1.0,
           'medieval': 3.0, 'moderna': 2.0, 'solar': 2.5}

# convert.py:575, primeiro bairro (comentário de 2026-10-16)
parkchance = 0.55       # chance de lote vazio virar parque
buildingchance = 0.12   # chance de lote virar casa

# convert.py:582, centro comercial (retail_district)
parkchance = 0.45
buildingchance = 0.26

# convert.py:611
parkchance = 0.8
buildingchance = 0.18
maxfloors = 3

# convert.py:617
parkchance = 0.6
buildingchance = 0.22
maxfloors = 3

# convert.py:649, multisettings (lotes com varias casas)
areasize = 8
minimum = 1
maximum = 2

# complexes.py nao tem fator de parque proprio. O parque e controlado
# pelo parkchance de cada bairro acima.
```

#### Regras de negócio

- Tipos novos de casa valem mais que cores novas de uma casa só.
- Para diminuir a densidade, mexa em `buildingchance` ou no fator de parque, nunca apague casas.
- A raridade das cidades (`towns.json` e chance da cidade) fica como está.

## Casas

As seções seguem a ordem de `CASAS`. Cada uma traz a origem, a janela, o chão, o porão, o retoque e as regras específicas.

### Vermelha

A **vermelha** é a casa de um chunk, feita de `m-pinkhouse.nbt`, com chão na fatia 0 e porão de 0 camadas. O retoque remove uma **floreira** de laje de andesito que flutuava um bloco para fora da fachada sul, logo abaixo das janelas.

```py title:Vermelha
CasaSchematic(key='vermelha', file='m-pinkhouse.nbt', x0=0, z0=0, cw=1, cl=1, ground=0, weight=0.6, cellar=0)
Retoque(base='vermelha', funcao=retouch_vermelha)  # tira polished_andesite_slab em z=15
```

#### Regras de negócio

- A floreira da fachada sul sai, porque flutuava sem apoio.
- Casa de um chunk vira prédio simples nas 4 rotações.

### Fada

A **fada** é a cabana de um chunk, feita de `cozy-fairy-hut.schem`, com chão na fatia 1 e sem porão. O schematic trazia cerca de 24 **lanternas** num único chunk, o que deixava a cabana sobrecarregada de luz. O retoque mantém umas 8, com distância mínima de 7 blocos entre elas.

```py title:Fada
CasaSchematic(key='fada', file='cozy-fairy-hut.schem', x0=-3, z0=-1, cw=1, cl=1, ground=1, weight=0.5)
Retoque(base='fada', funcao=retouch_fada)  # reduz lanterns para ~8, distancia minima 7
```

#### Regras de negócio

- Uma cabana tem umas 8 lanternas, espalhadas com distância mínima de 7 blocos.
- A fada não tem porão.

### Robella

A **robella** é a casa de dois por dois chunks, feita de `robella-house1.schem`, com chão na fatia 0 e sem porão. O problema antigo era a **privada** e o **lavatório** do térreo: alguns nasciam colados na cerca da varanda da frente, ou com três ou mais lados abertos, ficando para fora da casa. O retoque remove esses casos e mantém os que estão em banheiro fechado.

```py title:Robella
CasaSchematic(key='robella', file='robella-house1.schem', x0=-3, z0=-3, cw=2, cl=2, ground=0, weight=0.7)
Retoque(base='robella', funcao=retouch_robella)  # tira privada/lavatorio colado em cerca ou com 3+ lados abertos
```

#### Regras de negócio

- Privada e lavatório colados na cerca da varanda, ou com três ou mais lados abertos, saem.
- Banheiro fechado mantém privada e lavatório.
- Casa de 2x2 chunks vira multibuilding com 4 prédios por rotação.

### Cerejeira

A **cerejeira** é a casa de dois por dois chunks feita de `cherry-robella.schem`, com chão na fatia 2 e sem porão. Não tem retoque próprio, então segue as regras gerais (janelas, mobília e recoloração).

```py title:Cerejeira
CasaSchematic(key='cerejeira', file='cherry-robella.schem', x0=-1, z0=-1, cw=2, cl=2, ground=2, weight=0.6)
# sem Retoque: nao ha entrada em RETOUCH
```

#### Regras de negócio

- Sem retoque próprio. Defeito específico desta casa pede `retouch_cerejeira` registrado em `RETOUCH`.
- Casa de 2x2 chunks vira multibuilding.

### Serrana

A **serrana** é a casa de dois por dois chunks feita de `dtbh-cottage.schem`, com chão na fatia 3 e porão de 0 camadas. Não tem retoque próprio.

```py title:Serrana
CasaSchematic(key='serrana', file='dtbh-cottage.schem', x0=0, z0=-4, cw=2, cl=2, ground=3, weight=0.7, cellar=0)
# sem Retoque: nao ha entrada em RETOUCH
```

#### Regras de negócio

- Sem retoque próprio. Segue as regras gerais do pipeline.
- Casa de 2x2 chunks vira multibuilding.

### Medieval

A **medieval** é a casa de dois por dois chunks feita de `medieval-cozy-house.schem`, com chão na fatia 12 e porão de 6 camadas, o máximo permitido. O térreo é um **salão aberto** com **cozinha em U** e uma **península de pedra**, e a parte de baixo tem um **estábulo** com baias. O mobiliário automático espalhava peças fora de lugar: cama em cima da península, cama, baú e escrivaninha no salão, privada ou cama nas baias. O retoque apaga o que o mobiliador inventou no salão (y 11 e 12) e nas baias (y 7).

```py title:Medieval
CasaSchematic(key='medieval', file='medieval-cozy-house.schem', x0=7, z0=1, cw=2, cl=2, ground=12, weight=0.6, cellar=6)
Retoque(base='medieval', funcao=retouch_medieval)  # limpa o salao (y 11-12) e as baias (y 7)
```

#### Regras de negócio

- O salão do térreo fica sem o mobiliário automático.
- A península de pedra não recebe cama.
- As baias do estábulo não recebem privada nem cama.
- O porão de 6 camadas precisa de escada na boca, como qualquer porão.

### Moderna

A **moderna** é a casa de três por dois chunks feita de `cozymdoerncabin.schem`, com chão na fatia 6 e sem porão. Alguns móveis foram montados com bloco vanilla que o `vanilla_furni.py` não reconhece, então o retoque os reconstrói com as coordenadas desta casa. A moderna também não tem porta de verdade: a entrada é aberta, e por isso a frente é fixada no lado sul, na rotação 0.

```py title:Moderna
CasaSchematic(key='moderna', file='cozymdoerncabin.schem', x0=3, z0=8, cw=3, cl=2, ground=6, weight=0.3)
Retoque(base='moderna', funcao=retouch_moderna)  # moveis vanilla que o vanilla_furni nao reconhece
FRONT_R0 = {'moderna': 'south'}  # entrada aberta, frente na rotacao 0
```

#### Regras de negócio

- Móveis montados com bloco vanilla que o mobiliador não reconhece são reconstruídos pelo retoque.
- A frente vem de `FRONT_R0` e gira com a rotação.
- Casa de 3x2 chunks vira multibuilding com 6 prédios por rotação.

### Solar

A **solar** é a casa de três por dois chunks feita de `copper-cottage.schem`, com chão na fatia 35, porão de 6 camadas e peso de sorteio baixo (0.15). Por ter porão, depende da escada gerada por `ladder_mouths`. Não tem retoque próprio.

```py title:Solar
CasaSchematic(key='solar', file='copper-cottage.schem', x0=78, z0=34, cw=3, cl=2, ground=35, weight=0.15, cellar=6)
# sem Retoque: nao ha entrada em RETOUCH
```

#### Regras de negócio

- Porão de 6 camadas precisa de escada na boca.
- Sem retoque próprio. Segue as regras gerais do pipeline.
- Casa de 3x2 chunks vira multibuilding com 6 prédios por rotação.

## Construções temáticas

Além das casas de vila, o `schematics.py` coloca nove construções temáticas, uma por tema, fora do sorteio de rotação. Cada uma tem peso **0.25** em `CASAS` e nasce de uma das casas base já existentes, com um **retoque** próprio que coloca os blocos do tema sobre o mesmo schematic. O loot de cada tema vai para as lostcities em arquivos próprios, gerados por `write_theme_files()`. As regras de bloqueio continuam as de [[blacklist]] e de [[estudo_do_modpack]].

### Floricultura

A **floricultura** é a casa pequena de cerejeira que vira estufa. O retoque da cerejeira roda primeiro, e depois as escadas e lajes da camada de cima viram **painéis de vidro**, então o telhado lê como estufa. Usa a base `cerejeira` e entrou antes das demais.

```py title:Floricultura
CasaTematica(key='floricultura', base='cerejeira', theme='floricultura', weight=0.25)
Retoque(base='floricultura', funcao=retouch_floricultura)  # cerejeira primeiro, depois vidro no telhado
Loot(theme='floricultura', chests=(3, 6))  # sementes, fertilizantes e regador
```

#### Regras de negócio

- O retoque chama o da cerejeira antes de trocar o telhado.
- Escadas e lajes da camada mais alta viram `glass_pane`.
- O contador `floricultura_vidro` conta os blocos trocados.

### Adega

A **adega** é a casa medieval com barricas de envelhecimento. O retoque da medieval roda primeiro, e depois duas **barricas** (aging cask e ancient cask) vão encostadas numa parede da camada mais baixa, a pelo menos 3 blocos uma da outra, virradas para longe da parede. Usa a base `medieval`.

```py title:Adega
CasaTematica(key='adega', base='medieval', theme='adega', weight=0.25)
Retoque(base='adega', funcao=retouch_adega)  # duas barricas na parede do piso mais baixo
Loot(theme='adega', chests=(3, 6))  # adega com garrafas e um item raro
```

#### Regras de negócio

- As barricas ficam na camada mais baixa, de preferência no porão quando existe.
- Duas barricas no mínimo 3 blocos de distância uma da outra.
- O contador `adega_barrica` conta as barricas colocadas.

### Torre de raio

A **torre de raio** é a casa solar, a mais alta do conjunto. O retoque coloca um **charging rod** no bloco mais alto do telhado livre, perto do centro da grade, e um **lightning rod** ao lado dele na mesma camada. Usa a base `solar` e tem 41 camadas.

```py title:TorreRaio
CasaTematica(key='torre_raio', base='solar', theme='torre_raio', weight=0.25)
Retoque(base='torre_raio', funcao=retouch_torre_raio)  # charging rod no topo e lightning rod ao lado
Loot(theme='torre_raio', chests=(2, 5))  # barras de cobre, blaze rod e blocos de cobre
```

#### Regras de negócio

- O charging rod fica no bloco mais alto que ainda tem ar em cima dele.
- O lightning rod fica numa face livre na mesma camada.
- Os contadores são `torre_carregador` e `torre_para_raios`.

### Laticínio

O **laticínio** é a casa moderna com uma **cheese press** e uma **mayonnaise machine** encostadas nas paredes do piso mais baixo. O retoque da moderna roda primeiro. Usa a base `moderna`.

```py title:Laticinio
CasaTematica(key='laticinio', base='moderna', theme='laticinio', weight=0.25)
Retoque(base='laticinio', funcao=retouch_laticinio)  # cheese press e mayonnaise machine na parede
Loot(theme='laticinio', chests=(1, 3))  # animal feed sack, steamed milk e bolo
```

#### Regras de negócio

- As máquinas ficam de frente para longe da parede.
- O contador `laticinio_maquina` conta as máquinas colocadas.

### Vinícola

A **vinícola** é a casa medieval com **wine kegs** e um **preserves jar** nas paredes do piso mais baixo. O retoque da medieval roda primeiro. O loot usa os quatro primeiros itens de adega e uma garrafa de vidro. Usa a base `medieval`. Ainda não fica ao lado do vinhedo dos bairros rurais, então a adjacência com o vinhedo não foi feita.

```py title:Vinicola
CasaTematica(key='vinicola', base='medieval', theme='vinicola', weight=0.25)
Retoque(base='vinicola', funcao=retouch_vinicola)  # dois wine kegs e um preserves jar na parede
Loot(theme='vinicola', chests=(2, 4))  # CELLAR[:4] e garrafa de vidro
```

#### Regras de negócio

- Dois wine kegs e um preserves jar, cada um em uma parede do piso mais baixo.
- O contador `vinicola_barrica` conta os blocos colocados.
- Não há vinhedo de bairro rural junto da casa.

### Celeiro de neve

O **celeiro de neve** é a casa vermelha com um **cocho** (feeding trough) encostado numa parede e até dois blocos de gelo ao lado. O retoque da vermelha roda primeiro. Usa a base `vermelha`. Ainda não fica restrito a bioma nevado: ele aparece em qualquer bioma.

```py title:CeleiroNeve
CasaTematica(key='celeiro_neve', base='vermelha', theme='celeiro_neve', weight=0.25)
Retoque(base='celeiro_neve', funcao=retouch_celeiro_neve)  # cocho na parede e gelo nas celulas livres
Loot(theme='celeiro_neve', chests=(1, 3))  # casacos de calor
```

#### Regras de negócio

- O cocho fica na parede mais baixa, virado para longe dela.
- Até dois blocos de gelo (`packed_ice` e `blue_ice`) nas celulas livres ao lado do cocho.
- Os contadores são `celeiro_cocho` e `celeiro_gelo`.
- Ainda não fica restrito a bioma nevado.

### Cabana do pescador

A **cabana do pescador** é a casa robella com um **fish pond**, uma **fish pond basket** e um **crab trap** encostados nas paredes do piso mais baixo. O retoque da robella roda primeiro. Usa a base `robella`. Ainda não há posicionamento perto das docas.

```py title:CabanaPescador
CasaTematica(key='cabana_pescador', base='robella', theme='cabana_pescador', weight=0.25)
Retoque(base='cabana_pescador', funcao=retouch_cabana_pescador)  # fish pond, basket e crab trap
Loot(theme='cabana_pescador', chests=(1, 3))  # isca de crab trap
```

#### Regras de negócio

- Os três blocos ficam em paredes diferentes do piso mais baixo.
- O retoque só roda se houver três paredes livres.
- O contador `cabana_pesca` conta as cabanas com pesca montada.
- Ainda não fica perto das docas.

### Alfaiataria

A **alfaiataria** é a casa fada com uma **sewing table** encostada numa parede e dois blocos de **lã** (branca e cinza) nos próximos lugares livres. O retoque da fada roda primeiro. Usa a base `fada`. Ainda não tem manequins (armor stands).

```py title:Alfaiataria
CasaTematica(key='alfaiataria', base='fada', theme='alfaiataria', weight=0.25)
Retoque(base='alfaiataria', funcao=retouch_alfaiataria)  # sewing table na parede e duas lãs
Loot(theme='alfaiataria', chests=(1, 3))  # casacos de calor e de frio
```

#### Regras de negócio

- A sewing table fica na primeira parede livre, virada para longe dela.
- As duas lãs ficam nos dois lugares livres seguintes.
- O contador `alfaiataria_mesa` conta as mesas colocadas.
- Ainda não tem manequins.

### Seringueiro

O **seringueiro** é a casa serrana no meio de troncos, com até dois **tappers** nas celulas livres ao lado dos troncos, dois **barris** nas paredes e um **pomar** pequeno. O retoque da serrana roda primeiro. Usa a base `serrana`.

O pomar tem quatro mudas (`pamhc2trees:apple_sapling`, `orange_sapling`, `cherry_sapling` e `lemon_sapling`) nas celulas livres mais baixas, com pelo menos 2 blocos de distância entre elas. As mudas são o único cultivo do pomar e não estão na [[blacklist]].

```py title:Seringueiro
CasaTematica(key='seringueiro', base='serrana', theme='seringueiro', weight=0.25)
Retoque(base='seringueiro', funcao=retouch_seringueiro)  # tappers, barris e pomar de 4 mudas
Loot(theme='seringueiro', chests=(2, 4))  # xarope, pine tar e balde
```

#### Regras de negócio

- Até dois tappers nas celulas livres ao lado dos troncos.
- Dois barris nas paredes do piso mais baixo.
- Quatro mudas de fruta nas celulas livres mais baixas, sem bloco proibido.
- O contador `seringueiro_pomar` conta as mudas plantadas.

## Guia para o agente

Esta seção é o roteiro para uma IA criar uma casa nova ou consertar uma existente sem quebrar o resto. Ela não repete o que já foi explicado acima, então leia as seções de **Alto nível** e **Baixo nível** antes de começar. Os números entre parênteses nas listas são as **issues** já corrigidas, citadas na tabela de armadilhas.

### Fluxo para criar ou consertar uma casa

1. Escolha o schematic em `sunlit_tools/schematics/` e confira o recorte (`x0`, `z0`, `cw`, `cl`) com `python3 schematics.py <key> --stats`, que mostra o que mudaria sem gravar nada.
2. Fixe o **chão** (`ground`) pela camada onde a rua encontra a parede. Se as janelas ficam no nível da rua, a casa está enterrada (issues 1, 8 e 9). Só depois defina o **porão** (`cellar`), e nunca passe de 6 camadas.
3. Acrescente a linha em `CASAS`. Se a casa tiver defeito próprio, escreva `retouch_<nome>(v)` e registre em `RETOUCH`. Nunca edite o JSON gerado à mão, porque a próxima geração apaga a correção.
4. Gere só essa casa com `python3 schematics.py <key>` e confira o interior: mesa, cadeira, geladeira, banheiro, sótão e horta.
5. Se o defeito for de mobília, corrija `clutter.py` (posição, facing, quantidade) ou `vanilla_furni.py` (conversão para mod). Se o defeito aparecer só no datapack montado (porta fantasma, cerca solta, bloco flutuando), corrija a regra correspondente em `polish.py`.
6. Rode o pipeline completo da seção "Como validar" e só depois atualize o datapack.

### Checklist obrigatório

- [ ] Chão confere: janelas acima da rua, nada enterrado, sem andar fantasma (1, 8, 9).
- [ ] Sala de jantar completa, com uma mesa e cadeiras de mod, nunca escada ou laje como assento (2).
- [ ] No máximo 2 mesas soltas por cômodo, e nenhuma mesa encostada em bancada, armário, cadeira ou outra mesa (2).
- [ ] Assentos só dentro do cômodo, nunca na varanda ou no lado de fora (2).
- [ ] Gavetas e armários voltados para dentro do cômodo (3).
- [ ] Nenhum bloco vanilla onde existe móvel de mod equivalente (4).
- [ ] Banheiro sem teto de vidro, com iluminação padrão e sem escada de quartzo como decoração (3, 5).
- [ ] Sótão sem alçapão solto nos cantos e sem feno como decoração (6).
- [ ] Móvel virado para o lado certo: cadeira e sofá de frente para a mesa ou a sala, cama com cabeceira na parede (7).
- [ ] Nenhuma porta de vidro fantasma, e nenhum alçapão que não leva a lugar nenhum (10).
- [ ] Cercas e hedges conectados entre si (11).
- [ ] Horta no nível do chão, 100% preenchida, só com cultivos de todas as estações e cerca de spruce (13).
- [ ] Privada, porta e alavanca só dentro da casa, nunca na entrada ou na varanda (14).
- [ ] Nenhum buraco de escada ou alçapão interior que não leve a nada (15).
- [ ] Nada flutuando e altura do prédio igual à projetada (16).
- [ ] Nenhuma casa vazia: ou ela é mobiliada, ou é substituída (17).
- [ ] Casa `vila_*` ou qualquer prédio com chão, paredes ou porão nunca é **lote**. Um quintal com plantação não transforma o prédio em lote. Só entram em `global.sunlitLoteBuildings` (gerado pelo `complexes.py` em `kubejs/startup_scripts/sunlitTownsLotes.js`) e são rebaixados como jardim de lote. O `validate.py` confere que a lista está completa e não tem `vila_*`.
- [ ] O rebaixamento de jardim de lote (`townLoteGardenColumn` em `kubejs/server_scripts/sunlitTownsLife.js`) mexe só nas colunas de jardim. Qualquer coluna com bloco de construção acima (tábua, tora, escada, laje, porta, vidro, tijolo, concreto, armário) fica no lugar, senão o chão e o interior afundam enquanto as paredes e a fundação ficam, o que enterra a casa e quebra a escada do porão.
- [ ] O pós-processamento em jogo não pode depender do primeiro PostGen do chunk. O **Distant Horizons** dispara PostGen pelas próprias threads para chunks que o servidor nunca carrega. Uma chave em `sunlitTownSeen` só fica depois de um populate bem-sucedido, e um item descartado deixa o próximo PostGen real enfileirar de novo.
- [ ] Uma peça de parque é colocada 1 bloco acima do gramado e descida 1 bloco em jogo (`townLowerPark`). Tudo que sai para fora com ar embaixo (beirais de telhado, toldos, marquises, coberturas) desce junto com a peça. Ao desenhar, prefira telhados cujo anel apoia em postes ou paredes. Se um beiral tem ar embaixo, confira em jogo que ele desceu junto.
- [ ] Nada de decoração empilhada em **blocos de armazenamento** (caixotes, fardos, sacos, cestos, barris). Só o mesmo bloco ou o telhado e o piso estrutural podem ir em cima. Feno só em cima de feno.
- [ ] Uma **lanterna** fica só em cima de mesa, balcão, cerca ou poste, nunca em bancada de trabalho (moedor, fogão, pia, forno).
- [ ] Geladeira com as costas numa parede de verdade e a frente livre.
- [ ] Nenhuma terracota e nenhum concrete powder no resultado (regra global).
- [ ] Todo conserto vale para `base`, `_c1`, `_c2` e para os temas.
- [ ] Toda letra usada no schematic existe na paleta (`validate.py`: "char sem paleta").
- [ ] `validate.py` termina em OK.

#### Armadilhas comuns

| Sintoma | Causa | Correção |
|---|---|---|
| Casa enterrada, janelas no nível da rua (1, 8, 9) | `ground` errado ou porão sobrando, com escada lateral levando para um subsolo que não existe | Corrigir `ground` pela camada da rua, limitar `cellar`, tirar a escada lateral e a cerca enterrada |
| Sala de jantar com uma mesa e uma cadeira (2) | Mobília vanilla não convertida, assento feito de escada ou laje | `vanilla_furni.seats()` precisa converter para cadeira de mod, com o jantar completo |
| Mesa em varanda ou colada na bancada (2) | `clutter.py` sem o limite de mesas por cômodo | Limitar a 2 mesas e exigir que a mesa fique livre |
| Gaveta de cozinha virada para a parede (3) | Facing errado | Facing corrigido em `clutter.py`, não manualmente no schematic |
| Escada de quartzo no banheiro, alçapão flutuando (3) | Decoração vanilla sem móvel de mod | Trocar por móvel de mod e deixar o alçapão só onde tem apoio |
| Teto de vidro e luz de farol no banheiro (5) | Iluminação fora do padrão | Trocar o teto por bloco sólido e usar a iluminação padrão |
| Sótão com alçapão nos cantos e feno (6) | Decoração automática sobrando | Retirar o alçapão solto e o feno, e colocar só mobília de mod |
| Cadeira de costas ou de lado para a mesa (7) | Orientação do móvel não considerada | Conferir o lado do móvel no retoque ou no `clutter.py` |
| Porta de vidro que não abre para nada (10) | Porta fantasma | `rule_door_visible` em `polish.py` remove a porta sem acesso |
| Cerca de hedge solta (11) | Blocos de conexão sem vizinho | `rule_hedge_links` em `polish.py`, e em jogo `townFixConnections` religa por chunk |
| Horta um bloco alta, com falhas ou com cultivo de inverno (13) | Horta fora do nível do chão | Horta no nível do chão, 100% preenchida, só cultivos de todas as estações, cerca de spruce |
| Porão sem acesso do térreo (cellar_access) | Região de ar do porão sem escada nem entrada, como sala lacrada | `cellar_access.py` abre poço de escada em porões sem acesso, e `validate.py` barra porão sem acesso; grupos sem solução ficam na lista `EXCEPTIONS` do `cellar_access.py` com o motivo |
| Privada e alavanca do lado de fora (14) | Móvel colado à cerca ou com 3 ou mais lados abertos | Retoque como o de `retouch_robella`, que tira esses casos e mantém os de banheiro fechado |
| Buraco de escada que não leva a lugar (15) | Escada interior sem destino | Remover a escada ou criar o andar que ela promete |
| Bloco flutuando, prédio mais alto que o projetado (16) | Peça sem apoio ou prédio fora da altura | `rule_float` em `polish.py`, e conferir a altura do prédio no `CASAS` |
| Casa sem ninguém dentro (17) | Mobília automática não cobriu o cômodo | Mobiliar (`furnish_empty`) ou substituir a casa |
| Porão com boca aberta e sem acesso | Escada da boca de porão ausente | `ladder_mouths` em `schematics.py` põe a escada |
| Geladeira na frente do fogão | Frente livre não respeitada | `rule_fridges` em `polish.py` gira a geladeira para o melhor lado |
| Duas casas enterradas, porão sem acesso | Casa `vila_*` tratada como lote por causa da plantação no quintal, então o chão afundou e as paredes não | Só os prédios listados são lote; o rebaixamento de jardim pula colunas de construção (18, 19) |
| Fazenda cercada 1 bloco alta demais | Chunk gerado primeiro pelo Distant Horizons; o pós-processamento foi marcado como feito e nunca rodou no chunk real | Chave em `sunlitTownSeen` só depois do populate; item descartado libera a chave (20) |
| Telhado de laje de spruce cortado ou invertido sobre barraca ou celeiro | Colunas da borda com ar embaixo não foram rebaixadas junto com a peça | Rebaixar o segmento inteiro acima do gramado, incluindo os beirais (21) |
| Feno em caixote ou fardo, lanterna no moedor | Desenho da peça | Rearranjar em `parks.py`; o `validate.py` bloqueia (22, 23) |
| Mudança em `parks.py` não aparece no jogo | `parks.py` é biblioteca, não etapa do pipeline; e `complexes.py` pula o lote se `buildings/lote/<park>.json` já existe | Gravar as fatias novas em `parts/parks/<park>.json` e atualizar à mão `parts/lote/<park>_ground.json` e `_top.json` (o `g[0]` é a fatia 0 com `' '` trocado por `'?'`), depois rodar o pipeline até o `validate.py` |

#### Como validar

Rode o pipeline nesta ordem: `houses.py`, `cozy_expansion.py`, `vila.py`, `remodel.py`, `schematics.py`, `finalize.py`, `polish.py`, `complexes.py`, `cellar_access.py` e `validate.py`. O `cellar_access.py` põe escada do térreo até o piso de cada porão real sem acesso (grupo de multipredio conta como um; idempotente). O `validate.py` precisa terminar em OK antes de qualquer entrega. Depois, atualize o `Modpack.zip` com o datapack gerado.

O `validate.py` agora também confere se a lista de lotes está completa e se há decoração empilhada em blocos de armazenamento. Depois de mudar o pós-processamento do KubeJS, regenere os chunks afetados do save solo (`--apenas-forceload`) antes de testar.

O save solo só é regenerado com o jogo fechado, depois de backup e de um dry run. Nunca mexa no "Nosso mapa".

Em jogo, confira as coordenadas da casa, cada variante (`c0`, `_c1`, `_c2` e os temas) em cada rotação, e ande por todos os cômodos procurando as armadilhas da tabela acima.

## Anotações

> Por que a vermelha não tem porão? Porque `cellar=0` no `CASAS`. O terreno vem do schematic.

> Por que o retoque da medieval usa alturas fixas (y 11-12 e y 7)? Porque o salão e as baias são recortes fixos do schematic. Se a janela mudar, os valores precisam ser reconferidos.

> Por que a moderna tem coordenadas fixas no retoque? Porque o retoque reconstrói móveis em posições conhecidas do schematic. Trocar o arquivo exige reescrever o retoque.

> Por que a solar tem peso 0.15? Não está registrado no código. Pergunta para o dono do projeto.

> Os valores de lanternas da fada (cerca de 8, distância 7) e o peso da solar são escolhas de ajuste, não regras documentadas.

**Ainda em aberto:** `vdump`, citado no pedido de documentação, não existe no projeto. As checagens disponíveis são `--stats` do `schematics.py` e `validate.py`. Confirmar se existe outra ferramenta de visualização.

**Ainda em aberto:** a robella tem o retoque da varanda, mas não foi verificado se ele cobre todos os chunks da casa de 2x2.

**Ainda em aberto:** a escada do porão da solar não foi conferida para todas as rotações.

> O DeceasedCraft foi desinstalado do modpack, e o `convert.py` é legado. O conteúdo convertido que já está no datapack é a fonte de verdade, então não rode o `convert.py` para recriar casas.

**Ainda em aberto:** as casas que apareceram nos screenshots da conferência como "cerejeira?" e "filmworkstower_2?" não têm chave de vila confirmada. Não está registrado se a cerejeira da issue 9 é a casa `cerejeira` de `CASAS`.

**Ainda em aberto:** a mobília das casas de 2x2 chunks (serrana, medieval) ainda não foi conferida em jogo em todas as rotações depois da última correção de geladeira e cozinha.

> Por que não deduzir lote pela fazenda no quintal? Porque as casas schematic têm quintal com plantação, e a dedução afundou o chão de duas casas.

**Ainda em aberto:** confirmar em jogo, em chunks novos, que os beirais do celeiro e da barraca de mercado descem junto com a peça, e que os chunks pré-gerados pelo Distant Horizons recebem o pós-processamento.

> As construções temáticas seguem as restrições do mapa?
> Sim. O `validate.py` checa a [[blacklist]] (sem batata nem cenoura, sem concrete powder) também nas construções novas e no pomar do seringueiro. Os blocos das construções temáticas são conferidos com as mesmas regras das casas de vila.
