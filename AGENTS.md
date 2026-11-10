Demais regras e detalhes: docs/context/INDEX.md (ler o índice primeiro, depois só a entrada necessária).

# REGRA OBRIGATÓRIA: SAVE SOLO

- Sempre considerar o save `saves/Solito solamente` como alvo de correções, regenerações e edições de mundo.
- NUNCA alterar o save `saves/Nosso mapa` (o outro save) a menos que o dono peça explicitamente.

Data da regra: 2026-10-18

# REGRA OBRIGATÓRIA: O AGENTE É O CRIVO FINAL (2026-11-03, pedido do dono)

- O agente decide se a mudança funciona. Não pede ao dono para abrir o jogo nem
  para testar, não passa checklist e não deixa a entrega "aguardando teste", a
  menos que o dono peça isso ou avise que algo não funciona.
- Verificar com o que dá para rodar sem o jogo: compilar, `sunlit_tools/js_harness/`
  (Rhino do mod), conferir nomes e assinaturas nos jars, validar dados, e ler
  `logs/kubejs/*.log` e `logs/latest.log` (tail/grep) quando houver sessão de jogo
  posterior à mudança.
- Nunca esperar o dono em background (sem Monitor aguardando o jogo abrir).
- Honestidade no relatório: dizer o que foi verificado e como, sem afirmar que algo
  foi visto no jogo se não foi. O que só o jogo mostra fica citado em uma linha, sem
  pedido de teste.
- Se o dono avisar que algo não funciona, investigar pelos logs e corrigir.

# REGRA OBRIGATÓRIA: BOM SENSO ANTES DE PERGUNTAR (2026-11-03, pedido do dono)

- Se o agente já sabe qual opção é a melhor e a mudança é reversível, aplica e relata.
  Não transforma isso em decisão do dono.
- Exemplo: faltava `defaultconfigs/quality_food-server.toml`, então mundo novo usaria
  chance aleatória de qualidade enquanto os saves usam 0. O agente recomendou copiar e
  perguntou; o certo era já ter copiado.
- Perguntar só quando for gosto do dono ou quando uma regra deste arquivo exigir
  autorização (`options.txt`, resource packs, `saves/Nosso mapa`).

# REGRA OBRIGATÓRIA — NÃO MODIFICAR OPTIONS SEM AUTORIZAÇÃO

> Esta regra vale para qualquer agente, script, automação ou edição manual futura nesta pasta
> (`Society: Sunlit Valley`).

## Proibido sem autorização explícita do dono

- NUNCA modificar, sobrescrever, deletar ou "restaurar" o arquivo `options.txt`.
- NUNCA alterar a linha `resourcePacks:` dentro de `options.txt` ou de
  `configureddefaults/options.txt`.
- NUNCA alterar `keybinding presets/`, atalhos de teclas, idioma (`lang`),
  `guiScale`, `renderDistance`, volume ou qualquer outra linha de `options.txt`.
- NUNCA reordenar, ativar ou desativar resourcepacks
  (`resourcepacks/*.zip`, `sunlit_overrides.zip`, Excalibur, FreshAnimations etc.)
  sem pedir antes.
- NUNCA tocar em `servers.dat`, `usernamecache.json`, `usercache.json`.

## O que fazer em vez disso

- Se um fix precisar de mudança visual ou de resourcepack, apenas DESCREVA a
  mudança sugerida no chat e espere o dono autorizar com "pode aplicar".
- Configs de geração (Lost Cities, datapacks, KubeJS, profiles) PODEM ser
  ajustadas, pois são o objetivo do projeto Sunlit — mas `options.txt` NÃO.
- Se o CurseForge/ConfiguredDefaults tentar sobrescrever `options.txt` no
  launch, avise o dono em vez de "corrigir" por conta própria.

## Bug que reseta resource packs (2026-10-10, pedido do dono)

- Quando o bug acontece, ele reseta os resource packs E as configs junto
  (atalhos, idioma, guiScale, renderDistance, volume etc.).
- ATUALIZADO 2026-10-26 (pedido do dono): o padrão oficial é
  `sunlit_tools/options_canonical.txt` (cópia do options.txt ideal), espelhado
  em `atalhos.md` (bloco Geral + packs + atalhos). Esta é a única exceção
  autorizada à regra acima.
- Sempre que o agente perceber que o `options.txt` foi resetado por erro (log com
  "Caught error loading resourcepacks", `resourcePacks:[]`, atalhos voltando ao
  padrão dos mods), ele DEVE restaurar sem pedir: conferir com
  `python3 sunlit_tools/restore_options.py --status` e aplicar com `--apply`
  (só com o jogo fechado, senão o jogo sobrescreve ao sair; o script recusa se o
  jogo estiver aberto). Avisar o dono do que foi restaurado.
- O agente NUNCA muda o padrão por conta própria. Se o dono mudar algo no jogo
  e pedir para virar padrão: jogo fechado, `--save` e depois `--md`.

Data da regra: 2026-10-02
Autor: pedido do dono da instância.

# REGRA OBRIGATÓRIA — TODA MUDANÇA VAI PARA O `Modpack.zip`

> ATENÇÃO (2026-10-06, pedido do dono): o antigo `Backup.zip` NÃO EXISTE MAIS.
> Ele foi substituído por `Modpack.zip` na raiz da instância. Toda menção a
> `Backup.zip` nesta regra e nas demais (ex.: "Backups e caches de save nunca
> entram no `Backup.zip`") deve ser lida como `Modpack.zip`. NUNCA recriar um
> `Backup.zip`.

Sempre que algo for alterado nesta instância (configs, KubeJS, datapacks,
`moonlight-global-datapacks/`, `sunlit_tools/`, profiles de Lost Cities, mods,
resourcepacks autorizados etc.), o arquivo alterado ou criado DEVE ser
adicionado/atualizado dentro de `Modpack.zip`, na raiz da instância, mantendo o
mesmo caminho relativo.

- Atualize o `Modpack.zip` ao final de cada sessão de trabalho, cobrindo tudo
  que mudou nela. Ex.: `zip -u Modpack.zip caminho/do/arquivo` a partir da raiz.
- Arquivos deletados na instância também devem ser removidos do zip
  (`zip -d Modpack.zip caminho/do/arquivo`).
- O `Modpack.zip` é também o pacote de distribuição para outras instalações
  (Windows): preserve `READ_FIRST.txt`, `READ_FIRST_PT-BR.txt` e `install.bat` na raiz do zip.
- ZGC foi REMOVIDO do modpack em 2026-10-14 (pedido do dono: exige RAM
  demais). O coletor é o padrão do CurseForge (G1; `javaArgsOverride` = null
  no `minecraftinstance.json` e no registro do CurseForge
  (`%APPDATA%\CurseForge\agent\GameInstances\MinecraftGameInstance.json` —
  nesta máquina, nos dois arquivos equivalentes do Linux). O `install.bat`
  (raiz da instância) NÃO mexe em Java args; não reintroduzir flag de GC sem
  pedido do dono; `minecraftinstance.json`
  nunca entra no zip.
- `options.txt` entra no zip apenas como cópia de leitura; ele próprio nunca é
  modificado (ver regra acima).
- Não incluir saves (`saves/`), logs, caches nem `servers.dat`,
  `usernamecache.json`, `usercache.json`.
- Ao terminar, informe no chat quais arquivos foram adicionados ou removidos
  do zip.

Data da regra: 2026-10-03

# REGRA OBRIGATÓRIA: REPOSITÓRIO PIPINHA-VILLAGE (2026-11-10, pedido do dono)

- O repositório privado https://github.com/g-orgo/Pipinha-village.git é o espelho
  do `Modpack.zip`: tem tudo que o `install.bat` precisa (mods, resourcepacks,
  config, kubejs, datapacks, defaultconfigs, patchouli_books, docs). Clone local:
  `/var/home/Orgo/Documentos/Pipinha-village` (só o `README.md` e o
  `.gitattributes` existem apenas lá).
- Quando atualizar: depois de atualizar o `Modpack.zip` em qualquer mudança que
  chega ao jogador (mods, configs, KubeJS, datapacks, packs, changelog, instalador,
  docs). Mudanças só de save, logs ou ferramentas internas que não entram no zip
  não pedem sync.
- Como: `python3 sunlit_tools/sync_repo.py -m "<o que mudou, em inglês>"`. O script
  copia cada arquivo listado no zip a partir da instância, remove o que saiu do
  zip, faz o commit e o push para `main`. `--dry-run` mostra o resumo sem gravar.
  Avisos de "missing in the instance" querem dizer que o zip está desatualizado:
  corrigir o zip (`zip -d`) e rodar de novo.
- Este protocolo é a autorização permanente do dono para esses commits e pushes,
  só neste repositório e nunca com force-push. Nenhum arquivo acima de 95 MB (o
  script recusa) nem dado pessoal, token ou save.
- Se o changelog do menu inicial (`config/fancymenu/assets/changelog_*.markdown`)
  ganhar novidade, ela entra na seção "Novidades"/"New", sem data.
- Ao terminar, informar no chat o commit enviado.

# REGRA OBRIGATÓRIA: CARA DE CONTEÚDO ORIGINAL (2026-10-24, pedido do dono)

- Toda mudança no pack (quests, itens, textos, lojas, receitas, estruturas, telas) tem que parecer conteúdo original do modpack Society: Sunlit Valley.
- Mesmo estilo de texto e tom, mesmos ícones, mesmo layout e espaçamento das quests, mesma formatação de cores e títulos.
- Antes de criar algo novo, copiar o padrão de um item equivalente que já existe no pack.
