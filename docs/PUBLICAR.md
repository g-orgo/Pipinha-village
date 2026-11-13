# Publicar o modpack

Este documento explica como gerar o zip de modpack no formato do CurseForge para o Pipinha's Village 1.21.1, como alguém instala esse zip, como publicar e o que conferir antes.

Esta versão só existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1. O pack é baseado no Society: Sunlit Valley (1.20.1), e a linha de crédito deve dizer isso.

## Alto nível

O pacote é um **zip de perfil** do CurseForge. Ele não carrega os mods de terceiros: traz um `manifest.json` com a lista de arquivos do CurseForge, e o próprio app baixa cada mod na instalação. Só o que não vem do CurseForge entra dentro do zip, como as configs, o KubeJS e os resource packs que não são do CurseForge.

O repositório fica na branch **1.21.1** do https://github.com/g-orgo/Pipinha-village.git. A worktree local é `/var/home/Orgo/Documentos/Pipinha-village-1.21.1`. A `main` continua sendo a 1.20.1 até a fase F11, quando a 1.21.1 vai para a `main` e a 1.20.1 vai para uma branch própria. Essa troca é decisão do dono.

O zip final tem três partes: o **manifest.json**, a **modlist.html** (lista simples dos mods, com link para a página de cada um) e a pasta **overrides/**, com o conteúdo do pack que não vem do CurseForge.

## Baixo nível

```py title:ExportacaoCurseForge
# Script: tools/pack_tools/export_curseforge.py (existe na instância)
# Lê o minecraftinstance.json e escreve manifest.json + modlist.html + overrides/
python3 tools/pack_tools/export_curseforge.py --version 1.0.0
--name "Pipinha's Village"       # nome do modpack
--author "Seu nome"              # autor no manifesto
--out dist/                      # pasta de saída (padrão dist/)
--dry-run                        # mostra resumo sem gravar nada
```

```py title:ManifestoCurseForge
# Campos do manifest.json que o script precisa escrever para a 1.21.1
minecraft.version = "1.21.1"
minecraft.modLoaders = [{ id = "neoforge-21.1.265", primary = True }]
files = [{ projectID, fileID, required }]   # desativados (.disabled) entram com required = False
```

Saída: `dist/<nome>-<versão>.zip`. A pasta `dist/` não entra no próprio zip.

### Ponto de atenção no script

O script `tools/pack_tools/export_curseforge.py` ainda grava `minecraft 1.20.1` e `forge-47.4.0` no manifesto, e o texto de uso ainda cita `sunlit_tools/`. Isso foi conferido no script em 2026-11-13 e continua assim. Antes de gerar o zip da 1.21.1, esses valores precisam virar `1.21.1` e `neoforge-21.1.265`, e o caminho de uso precisa apontar para `tools/pack_tools/`. A alteração é pequena e reversível, mas ainda não foi feita: o item está **pendente** na fase F11, e o script não foi editado.

## Como um amigo instala no CurseForge

1. Abra o app do CurseForge.
2. Clique em **Create Custom Profile**.
3. Clique em **Import** e escolha o arquivo `.zip`.
4. Confirme o nome do perfil e espere o app baixar os mods.
5. Abra o perfil e entre no mundo.

Como alternativa, o zip completo `Modpack.zip` da instância continua funcionando pelo caminho manual ou pelo `install.bat`, descritos em `READ_FIRST_PT-BR.txt`. Esse caminho não baixa mods pelo app, então o zip é bem maior.

## Publicar no CurseForge

1. Entre na conta de autor em authors.curseforge.com (conferir a página de autores, porque o endereço pode ter mudado).
2. Crie um projeto do tipo **Modpack**.
3. Envie o zip gerado em `dist/`.
4. Escolha a versão do jogo (1.21.1) e o loader (NeoForge 21.1.265).
5. Aguarde a revisão do CurseForge. O prazo e as regras de aprovação ficam na própria página de autores.

Limite de tamanho do arquivo e regras de conteúdo: conferir na página do CurseForge antes do envio. Não foi verificado aqui.

## Mods próprios

Os mods próprios do autor não existem no CurseForge, então vão dentro de `overrides/mods/`. Na lista da 1.20.1 eram seis (`sunlit_cinematic_toms`, `sunlit_sortfix`, `sunlit_replayfix`, `sunlit_eating`, `sunlit_qualityfix` e `sunlit_texturefix`). Na instância 1.21.1 eles ainda não estão em `mods/`, e a lista precisa ser refeita quando forem portados.

Se quiser, publique cada um como projeto próprio no CurseForge. Depois, o manifesto pode referenciá-los pelo `projectID` e `fileID`, em vez de carregá-los dentro do zip. Isso exige ajustar o script para tratá-los como addons externos.

## Modrinth

O Modrinth usa outro formato, o `.mrpack`. Pontos a verificar antes de publicar lá:

- Mods precisam estar no Modrinth, ou estar dentro do pack com permissão do autor original.
- Dá para converter o zip do CurseForge, por exemplo com o packwiz ou exportando a instância pelo Prism Launcher. Não foi testado aqui; confirmar as ferramentas e os passos na documentação oficial de cada uma antes de usar.

## Permissão do autor original

Este pack é uma **versão modificada** do modpack Society: Sunlit Valley (projeto CurseForge 1093382, versão base 4.1.5A).

- Publicar este pack publicamente precisa da **permissão do autor original**.
- O nome público do pack é **Pipinha's Village**. A linha de crédito diz "baseado no Society: Sunlit Valley" e deixa claro que é uma edição não oficial.
- Confira a licença do pack original na página dele no CurseForge antes de publicar qualquer coisa.

## Checklist de release

1. Aumentar a versão (`--version`).
2. Ajustar o script para 1.21.1 e NeoForge 21.1.265, se ainda não foi feito.
3. Rodar o export com `--dry-run` primeiro e conferir o resumo.
4. Conferir que nenhum arquivo passa de 95 MB e que não há save, log, cache, token ou dado pessoal no zip.
5. Testar a importação em um perfil novo do CurseForge (perfil limpo, sem o `Modpack.zip`). O teste é do dono, no PC dele.
6. Abrir o save solo e conferir o mundo, as configs e os textos das quests. Quem confere é o dono.
7. Escrever o changelog da versão.
8. Só então enviar o zip para publicação.

## Anotações

> Por que a branch é a 1.21.1 e não a `main`? Porque a `main` segue sendo a 1.20.1 até a fase F11. A troca só acontece quando o dono decidir.

> O nome público vai ser o mesmo do pack? Sim, Pipinha's Village. O nome da edição com o original não entra como título, só na linha de crédito.

**Ainda em aberto:** o script de export precisa ser ajustado para 1.21.1 (valores do manifesto e caminho de uso). Também falta a lista dos mods próprios da 1.21.1, os passos e limites do Modrinth, e os limites do CurseForge, que não foram verificados nesta versão do documento.
