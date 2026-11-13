# Estado atual

O que está feito e em andamento agora na 1.21.1. O plano completo e as fases estão em `../migracao/PLANO.md`.

## Alto nível

A migração está na fase F1 concluída. Já existe a base 1.21.1 com os jars em `mods/` (364 arquivos) e um checker de mods com `versionRange`, desde 2026-11-12. O checker é a ferramenta que diz o que já tem porta para NeoForge e o que falta.

Os números de compatibilidade de mods, do último levantamento:

- 342 mods com versão NeoForge ok.
- 59 mods faltando na 1.21.1.
- 348 mods do mesmo projeto, já portados.
- 9 portas conferidas.
- 11 dependências novas.

Saíram por decisão do dono em 2026-11-12: Botania, Splendid Slimes e Splendid Cogs. A lista "fora" (Radium, Sodium Options API, Create: Extra Gauges, Redecorate / Farmer's Cutting: Quark, PowerfulJS) também fica fora.

## Baixo nível

```py title:Fases
F0 = "concluída (2026-11-11)"
F1 = "concluída (2026-11-11)"
F2_F11 = "pendentes"
F9 = "conversão do save 'Solito solamente' em cópia, vira o mundo principal"
F11 = "troca da main para 1.21.1, por decisão do dono"
```

```py title:Renderização e menu
render = ["Sodium", "Iris"]
menu = "FancyMenu 3.9.1"
water = ["WaterMedia 2.1.37", "YT Plugin"]
```

```py title:Ferramentas
tools_dir = "tools/"   # modcheck, configport, dataport, kjsport, lcport, pack_tools
```

## Regras de negócio

#### Em andamento agora

- Fase F2 em diante ainda não começou. O foco é conferir os mods que faltam e as dependências novas.
- Pastas de dados mudam para o formato 1.21 (F4): `recipe/`, `tags/item/`.
- Receitas trocam `item` por `id` no resultado e `nbt` por `components`.

#### Ainda não portado (a portar da 1.20.1)

Estes itens existem na 1.20.1 e ainda não foram portados. Ficam listados para não se perderem:

- Pipeline das cidades (loot, casas, interiores, fauna e moradores).
- Durabilidade infinita com perda na morte.
- Correção de ordenação (sortfix), replayfix, handsonfix e trashslot.
- Lithosphere, Punchy Moves e Spatial GUI.
- Profissões refeitas e Mercantil.
- Cristais e questbook.
- Cenas de terminal e ajustes de cena no EMI.
- Rebalanceamento de preços e tooltips.
- Botão do Replay Viewer.
- Distribuição em zip e changelog.
- Qualidade de comida e animações de comida.
- Claims e regen (regra de 2026-11-11).
- Ctrl+A, afeição de pets e contatos de profissão.
- Primeiro prato do cozinheiro e alternância de hostis.
- Metais do Create.
- Sistema de temperatura do LSO.
- Puffish Skills e ajustes de Quark.
- Mula do Vinery, que fica fora do jogo.

## Anotações

> A lista "a portar" foi resumida. O detalhe de cada item está no histórico da 1.20.1, não aqui.

**Ainda em aberto:** a contagem de 59 mods faltando é do último levantamento e precisa ser refeita quando o checker rodar de novo.
