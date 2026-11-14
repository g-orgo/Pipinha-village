# Erros comuns

## Alto nível

Este arquivo junta os erros que já custaram mais de uma rodada de teste no Pipinha's Village 1.21.1. A maior parte vem do **Rhino 2101**, o interpretador do **KubeJS 7**, que se comporta diferente do JavaScript normal e do KubeJS 6 da 1.20.1. O resto vem de **compatibilidade entre mods** que mudaram de versão na migração.

A regra de ouro é simples: o agente não roda o jogo, então todo erro só aparece no **log** depois que o dono testa. Por isso cada correção vai com **logs de diagnóstico** atrás de uma chave, e eles só saem depois que o dono confirma no jogo (ver [[conventions]] e [[state]]).

Leia este arquivo **antes de escrever ou revisar qualquer script em `kubejs/`**.

## Baixo nível

```py title:Rhino 2101 (KubeJS 7)
const_or_let_in_nested_block = "TypeError: redeclaration of var X"   # vale em if/try/for, em qualquer função, em startup, server e client
const_in_loop = "guarda só o 1º valor"     # const dentro de laço não é recriado a cada volta
fix = "declarar com let no topo da função e só atribuir dentro do bloco"
top_of_arrow_callback = "ok"               # forEach((x) => { const y = ...; }) no início do corpo funciona

ambiguous_overload = "InternalError: The choice of Java method ... is ambiguous"
fix_overload = 'obj["metodo(tipo.Completo,int,float)"](args)'   # assinatura explícita; classe interna usa $
# casos já vistos: GuiGraphics.drawString (String/float x Component/int),
# Font.width (String x FormattedText), Component.Serializer.fromJson (String x JsonElement),
# FTB Icon.combineWith (Icon x Icon[])

kubejs_string_helpers = ["path", "namespace"]   # "ns:id".path existe no KubeJS, não em JS puro
no_getClass = "TypeError: Cannot find function getClass"   # o Rhino esconde getClass(); para log use String(obj)

nbt_tag_objects = "campo de CompoundTag chega como Tag (StringTag, DoubleTag), não como texto ou número"
string_tag = ["Map.get(tag) = undefined", 'tag.equals("x") = false', '"" é truthy', 'String(tag) e `${tag}` saem com aspas']
numeric_tag = "nbt.merge({ n: 0 }) grava DoubleTag; Number(DoubleTag) = NaN; tag += 1 vira texto"
fix_nbt = "global.nbtStr(tag) e global.nbtNum(tag) (globalBlockEntityHandlers.js)"   # testado no Rhino 2101 real
fix_nbt_bool = "global.nbtBool(tag) (globalBlockEntityHandlers.js)"   # ByteTag é sempre truthy como objeto: if (tag) vale mesmo para 0b
java_string_key = "Map.get(cx.getString(k)) também falha: use String(...) ou global.nbtStr"
level_block_entity = "block.entity (getEntity())"   # block.blockEntity não existe e dá undefined

json_text_as_literal = "Text.of(NBT.stringTag('{\"translate\":...}')) mostra o JSON cru na tela"   # na 1.20.1 virava texto traduzido
fix_json_text = 'Component["translatableWithFallback(java.lang.String,java.lang.String)"](key, fallback)'   # nunca montar texto como string JSON
# casos já vistos: HUD do animal (nome) e HUD das máquinas ("Currently making", via global.translatableWithFallback)
```

```py title:Onde o erro aparece
server_scripts = "logs/kubejs/server.log"
client_scripts = "logs/kubejs/client.log"
startup_scripts = "logs/kubejs/startup.log"
scheduled_callback = "Error occurred while handling scheduled event callback"   # erro dentro de scheduleInTicks
render_handler = "[paintHud] HUD disabled after render error"   # o HUD se desliga até sair do mundo
crash = "crash-reports/"   # erro de mod Java, não de script
```

```py title:Diagnóstico
debug_flag = "PAINT_DEBUG em client_scripts/paintHud.js"   # liga logs de recebimento, desenho e autoteste
remove_logs_when = "dono confirmou no jogo"                 # nunca na mesma entrega de uma correção não vista
syntax_check = "tools/kjsport/syntax/SyntaxCheck.java"     # só pega erro de sintaxe, não os de execução acima
```

#### Regras de negócio

- Quebra de API do KubeJS 7: ao achar um padrão quebrado, varrer todo o `kubejs/` pelo mesmo padrão e corrigir todos os usos na mesma entrega.
- Nenhum `const` ou `let` dentro de `if`, `try`, `for` ou outro bloco aninhado, em nenhum tipo de script. Declare no topo da função e atribua dentro do bloco.
- Todo campo lido de NBT de bloco (`nbt.data.x`, `getServerData().x`), de entidade (`getNbt().x`, `entity.nbt.x`) ou de `persistentData.x` (jogador, servidor, bloco, animal) passa por `global.nbtStr`, `global.nbtNum` ou `global.nbtBool` antes de virar chave de `Map`, ser comparado, somado ou testado como verdadeiro. Leituras por `getInt`, `getString`, `getBoolean` e `contains` já são seguras e ficam como estão. Em 2026-11-14 isso travava todas as máquinas artesanais: o tapper ficava com "!", o HUD de progresso não abria e nada amadurecia.
- Toda chamada Java com mais de uma versão (sobrecarga) que recebe número ou string do JS usa a assinatura explícita.
- `catch` vazio é proibido: toda falha é registrada no log pelo menos uma vez.
- Código de debug nunca pode derrubar a função que observa: cada mensagem de debug roda dentro do próprio `try` (`paintDebug` em `paintHud.js`). Em 2026-11-14 um `getClass()` num log desligou o HUD inteiro.
- Código que roda a cada quadro (HUD) fica dentro de `try`, registra o erro uma vez e para de desenhar, para não derrubar o cliente.
- Logs de diagnóstico ficam atrás de uma chave e só são desligados depois da confirmação do dono no jogo.
- Antes de culpar um script por algo visual (ícone sumindo, HUD), procure mixins de outros mods no mesmo ponto da tela.
- Jar de terceiro só é alterado quando não há versão compatível, com o original guardado em `backups/` e a alteração anotada aqui.

## Compatibilidade entre mods

- **Sunrise Gardening 1.2 x Cultural Delights 0.19.8**: o Sunrise usa `CornUpperBlock`, que o Cultural Delights removeu na 0.18. Crash ao secar terra arada perto de plantação. O jar foi alterado para não ativar essa compatibilidade (`isLoaded("culturaldelights")` virou `"culturaldelightx"`); o original está em `backups/sunrisegardening-1.2.original.jar`. Ao atualizar o Sunrise, conferir se o autor corrigiu e trocar pelo jar oficial.
- **Amendments 2.2.7 + resource pack Excalibur**: a animação nova do slot selecionado da hotbar escondia o item do slot ativo. A animação foi desligada (`config/amendments-client.toml`, `hotbar_slot_animation.speed = 0.0`).
- **KubeJS 7 removeu APIs da 1.20.1**: `entity.entityType` (usar `global.checkEntityTag`), `player.paint` (usar `global.paintUi`), `e.entity` no tick de bloco (fachada em `zz_port_be_ticks.js`, que lê `e.block.entity`; `e.block.blockEntity` não existe), `getGameTime()` direto (usar `overworld.getLevelData().getGameTime()`).
- **`ClientEvents.generateAssets` + `loadTexture`** só lê `kubejs/assets` e o jar do mod dono do namespace, nunca resource packs.
- **Mod atualizado na migração com trava nova por padrão**: ParCool 4.x passou a exigir árvore de habilidades própria (`enable_skill_tree`), e nenhuma ação funcionava. Ao portar um mod que mudou de versão maior, procurar no config opções novas de desbloqueio, árvore ou limitação e alinhar com o comportamento da 1.20.1.
- **Tags do Serene Seasons mudam com o jar**: mod atualizado pode trazer tags de estação novas (Hearth & Harvest 1.4) ou perder as que tinha (Youkai's Homecoming 4.x, que só gera no datagen), e a planta passa a mostrar "Cannot grow" ou a crescer o ano todo. Ao trocar um mod de cultivo, comparar a tag efetiva de bloco e item com a 1.20.1 e acertar em `handleSeasonTags.js` (`jarSeasonStrip` / `jarSeasonRestore`). Na 1.21.1 a pasta é `tags/block`; jar com `tags/blocks` não vale mais.

## Anotações

- O tint de item (`.color(0, 0xRRGGBB)`) deixa o item invisível na 1.21?
  > Não. O KubeJS 2101 força alfa `FF` em cor numérica de 6 dígitos (conferido no código-fonte). O sumiço na hotbar era o slot ativo.
- Por que o HUD do animal mostrava o nome como JSON cru?
  > A conversão `fromJson` caía na ambiguidade de sobrecarga e o erro era engolido. `Text.of(JSON.parse(...))` funciona (autoteste no log: `literal{Teste}`). **Ainda em aberto:** o desenho do HUD com essa conversão ainda não foi confirmado no jogo.
- A animação do Amendments era mesmo a causa do ícone sumindo?
  > **Ainda em aberto:** desligada em 2026-11-14, aguardando o dono confirmar.
