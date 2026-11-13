# Plano de migração do Pipinha's Village para 1.21.1 (NeoForge)

O pack é baseado no Society: Sunlit Valley (1.20.1 Forge); daqui em diante ele é o Pipinha's Village.

Esta versão existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1.

Criado em 2026-11-11. Tabelas de apoio nesta pasta:
`mods_1.21.1.tsv` (status de cada um dos 441 mods da 1.20.1), `mods_instalados.tsv` e `modpacks_comparados.tsv`
(134 modpacks 1.21.1 comparados com a nossa lista).

## Alto nível

A ideia era achar um **modpack 1.21.1** parecido com o nosso e usar como base.
Comparei 134 packs (Modrinth e CurseForge) pelos mods exatos (hash do jar e ID
do projeto). O melhor chegou a **128 dos nossos 441 mods (29%)**: Farbound
(Modrinth) e Create Cozy Horizons (CurseForge). Depois vêm Fern & Fable, Farmtastic,
Hearth and Hollow e farmersmc, por volta de 100 cada. Nenhum tem o que faz o
Pipinha's Village ser o que é: moedas, lojas, mercado, o pack mod `society` e os scripts KubeJS.

Por isso a recomendação é **portar o nosso próprio pack**, não adotar outro:
**342 dos 441 mods já têm versão NeoForge 1.21.1** com o mesmo projeto. Os packs
acima servem só de referência: para qual NeoForge usar (os mais recentes estão em
`21.1.265`) e para ver qual substituto eles escolheram quando um mod nosso não existe.

O trabalho pesado não são os mods, é o **conteúdo próprio**:
- `kubejs/`: 374 arquivos JS, cerca de 60 mil linhas, 243 itens/blocos `society:`
  registrados em startup, 94 arquivos que mexem com NBT e 183 pastas de dados.
- `config/ftbquests`: 30 capítulos.
- Datapacks `sunlit_towns`, `zzz_sunlit_harmony`, `deceasedcraft_houses` e os
  profiles do Lost Cities.

## Baixo nível

```py title:Status dos mods (mods_1.21.1.tsv)
ok_neoforge        = 342  # mesmo projeto tem arquivo NeoForge 1.21.1
pack_ou_sem_loader = 27   # quase todos resource packs (Excalibur, Fresh Animations...)
so_forge           = 5    # Daily Weather, Fragmentum, YUNG's API, Bot's Lib, My Server Is Compatible
so_fabric          = 1    # XXL Packets
desativado         = 7    # já fora do jogo hoje, não migram
faltando           = 59   # sem 1.21.1 no CurseForge (ver tabela abaixo)
```

```py title:Faltando, por destino
nucleo_do_pack = ["Society Tweaks (mod 'society', 3 mixins)", "Splendid Slimes",
                  "Create: Splendid Cogs"]   # tudo do Chakyl, sem port
substituto_candidato = {  # existe algo 1.21.1 no Modrinth, conferir antes de usar
  "Create: Steam 'n' Rails": "Steam 'n' Rails Neoforge",
  "Farmer's Respite": "Farmer's Respite Unofficial Port",
  "Create Utilities": "Create Utilities (Unofficial Port)",
  "Vintage Delight": "Vintage Delight - KOTS",
  "Large Meals": "Large Meals", "Extractinator": "ExtractinatorForked",
  "Construction Wand": "Construction Wands Revived", "Decorative Blocks": "Decorative Blocks Reborn",
  "Oculus": "Iris (NeoForge)", "Automobility": "Automobility",
}
vanilla_ou_inutil = ["Trials Chambers Reuploaded",  # trial chambers são vanilla na 1.21
  "Better Advanced Tooltips Backport", "SerializerDebug", "FTB Quest Localizer",
  "Item Filters", "ServerConfig Updater", "Serene Seasons Fix - Revived",  # conferir se ainda precisa
  "Refined Storage (Fixes) Mixin", "Libnonymous"]
# Com sucessor/port (2026-11-13): Botania -> Botania Revived (+ Botania Seeds em KubeJS),
# Re:Deco -> Redecorate, Domestication Innovation -> Redomesticate, Fantasy's Furniture (port).
# Candidato a conferir: Sturdy Farmland -> Sunrise Gardening (sucessor declarado, build 1.21.1 a confirmar).
sem_substituto = ["Dracovita Farm Life", "Little Tractor",
  "Croptania", "Gensokyo Delight", "Quark Delight", "Farmer's Delight Compat",
  "NetherVinery", "Rainbow Oaks Renewed", "Species", "Hamsters Plus Lite", "Legendary Creatures",
  "Sturdy Farmland", "Balloon Box", "Fluid & Foolish", "More Minecarts and Rails",
  "Refined Storage Addons", "Max Enchant X", "Loot Journal", "Quests Additions",
  "VerdantVibes", "Radiant Gear", "Longwing Nuker", "Online Detector", "..."]  # resto no tsv
```

```py title:Fases
F0_instancia   # instância NOVA no CurseForge: "Pipinha's Village", NeoForge 21.1.265. FEITO
               # A instância 1.20.1, o Modpack.zip e a main do Pipinha-village não são tocados.
F1_mods        # instalar os 342 ok_neoforge; resolver os 6 só Forge/Fabric e os 59 faltando. FEITO (ver Estado)
F2_boot        # dono abre o jogo só com mods + configs padrão; agente lê latest.log
F3_configs     # portar config/ e defaultconfigs/ chave a chave (muitos .toml mudaram)
F4_dados       # converter pastas de dados para o formato 1.21 (script)
F5_kubejs      # portar scripts para KubeJS 2101 (1.21), por pasta
F6_quests      # FTB Quests 2101: itens com NBT viram components
F7_society     # reimplementar o que o mod 'society' faz, ou dropar
F8_mundo       # Lost Cities, sunlit_towns, estruturas; teste num mundo novo
F9_save        # teste numa CÓPIA do save "Solito solamente"
F10_extras     # resource packs (pack_format 34), FancyMenu, atalhos dos mods novos
F11_entrega    # 1.21.1 vai para a main + Modpack.zip novo; 1.20.1 numa branch própria (dono, 2026-11-13)
```

#### Regras de negócio

- Nada da instância 1.20.1 é alterado durante a migração; ela continua sendo a jogável.
- O save só é testado em cópia. Blocos e itens de mods que não migram somem do mundo
  na conversão, então a lista "sem substituto" tem que estar fechada antes da F9.
- O agente não roda o jogo: ele monta a instância, valida jars e dados e lê os logs.
  Cada boot e cada teste no jogo é feito pelo dono.
- F4 é mecânica e vira script: renomear `recipes`→`recipe`, `loot_tables`→`loot_table`,
  `tags/items`→`tags/item`, `tags/blocks`→`tags/block`, `advancements`→`advancement`,
  `functions`→`function`, `structures`→`structure`; nas receitas o resultado passa de
  `"item"` para `"id"` e `nbt` vira `components`.
- F5 é a maior fase. Pontos que quebram de 6 para 7 no KubeJS: NBT de itens
  (agora data components), formato das receitas, alguns nomes de eventos e o Rhino novo.
  O `sunlit_tools/js_harness/` precisa ser atualizado para o Rhino da 1.21 antes, porque é
  ele que valida os scripts sem abrir o jogo.
- Itens e IDs `society:*` ficam com os mesmos nomes (KubeJS registra com namespace próprio),
  para não quebrar quests, lojas e receitas.
- Substituto "candidato" só entra depois de conferir no jar: mod id, IDs dos itens e se é port
  fiel. Se os IDs mudaram, entra no script de remap.
- Mesmas regras de sempre valem na versão nova: cara de conteúdo original e harmonização
  entre mods.

#### Ordem do primeiro teste (o que dá para testar já)

1. F0 + F1 só com os 342 ok_neoforge e os substitutos já conferidos, sem KubeJS e sem quests.
2. Dono abre o jogo uma vez, fecha. Eu leio o log e corrijo conflitos e dependências.
3. Com o boot limpo, entram F3 e F4, depois F5 por pastas (startup, depois server, depois client).

## Estado (2026-11-11)

F0 e F1 prontas: 364 jars em `mods/`, lista em `mods_instalados.tsv`. Conferido sem abrir o
jogo: todo jar tem `neoforge.mods.toml`, toda dependência obrigatória está presente (incluindo
as que vêm dentro de outros jars) nenhuma incompatibilidade declarada bate com a versão
instalada e as faixas de versão das dependências conferem (checker com versionRange desde 2026-11-12).

```py title:Decisões da F1
mods_mesmo_projeto = 348   # 342 do CurseForge + 6 só no Modrinth (Daily Weather, Fragmentum,
                           # Loot Journal, Automobility, YUNG's API, Bot's Lib)
ports_conferidos   = 9     # mesmo mod id e mesmos itens: Steam 'n' Rails, Create Utilities,
                           # Large Meals, Extractinator, Construction Wands, Decorative Blocks,
                           # Creeper Confetti, Vintage Delight (KOTS), Farmer's Respite (58/78 itens)
dependencias_novas = 11    # ACI, Create Dragons Plus, DragonLib, Lodestone, Mechanicals, owo-lib,
                           # Prickle, Reese's Sodium Options, WATERMEDIA Binaries, Sodium, Iris
renderizacao = "Sodium + Iris"   # Embeddium saiu: na 1.21.1 os addons exigem Sodium.
                                 # Iris substitui o Oculus; Colorwheel volta a funcionar
fora = {"Radium": "incompatível com Create 6",
        "Sodium Options API": "a versão 1.21.1 conflita com Reese's Sodium Options",
        "Create: Extra Gauges": "versões 1.21.1 exigem Deployer API, incompatível com Factory Logistics",
        "Farmer's Cutting: Quark": "não é port do original",
        "PowerfulJS": "crash na construção do Create 6.0.10"}
large_meals_id = "largemeals -> large_meals"   # entra no script de remap da F4/F5
redecorate = "sucessor do Re:Deco (2026-11-13): 45 blocos com o mesmo nome + renomeados; resto segue em block_map.tsv"
watermedia = "2.1.37 + YT Plugin"   # o CurseForge troca para 2.x no launch por causa do Waterframes 2.1.23;
fancymenu  = "3.9.1"               # último sem exigir WaterMedia 3; Drippy fica em 3.1.2 (pede FancyMenu >= 3.9.0)
                                   # WaterMedia Binaries (152 MB) saiu junto com a 3.x
fora_powerfuljs = "mixin no Spout do Create referencia FluidIngredient, que não existe no Create 6.0.10; o pack não usa"
checagens = "tools/modcheck (ranges.py e mixscan.py), rodar depois de qualquer troca de jar"
```

Próximo passo: o dono abre o jogo uma vez (sem mundo), fecha, e o agente lê `logs/latest.log`.

## Anotações

O pack de origem (Society: Sunlit Valley) tem versão 1.21.1?
> Não achei nenhuma. Os sites de hosting só listam builds 1.20.1 Forge, e os mods do
> autor (society, Splendid Slimes, Splendid Cogs) só existem para 1.20.1.

Vale usar um dos packs 1.21.1 como base em vez do nosso?
> Não. O mais parecido divide só 29% dos mods e nenhum tem a nossa economia.
> Começar dele seria refazer o pack inteiro; portar o nosso aproveita 342 mods direto.

Botania, Splendid Slimes e Splendid Cogs não existem na 1.21.1. Dropar ou recriar em KubeJS?
> Saem do pack, junto com quests, ofertas e receitas ligadas a eles (decisão do dono, 2026-11-12).

A versão 1.21.1 ganha repositório próprio?
> Por enquanto é a branch `1.21.1` do Pipinha-village. Depois o repositório passa a ser
> só desta versão (decisão do dono, 2026-11-11).

Migrar o save "Solito solamente" ou começar mundo novo na 1.21.1?
> Converter uma cópia (F9), e ela vira o mundo principal; o original não é tocado (dono, 2026-11-13).
