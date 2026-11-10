# Publicar o modpack

Este documento explica como gerar o zip de modpack no formato do CurseForge, como um amigo instala esse zip e o que precisa ser verificado antes de publicar.

## O que o export contém e por que ele é pequeno

O script `sunlit_tools/export_curseforge.py` não copia os mods para dentro do zip. Ele lê o `minecraftinstance.json` da instância e escreve um `manifest.json` com a lista de mods do CurseForge (projeto e arquivo de cada um). Na instalação, o próprio app do CurseForge baixa esses mods.

O zip final tem três partes:

- **manifest.json**: lista os **arquivos do CurseForge** (cada um com `projectID` e `fileID`). Mods desativados (arquivo `.disabled` no disco) entram com `required: false`.
- **modlist.html**: uma lista simples dos mods, com link para a página de cada um quando o `minecraftinstance.json` tem o endereço.
- **overrides/**: as pastas de conteúdo do pack (configs, kubejs, datapacks da Moonlight, Lost Cities, quests etc.) e apenas os arquivos que **não** vêm do CurseForge (os dois mods próprios do autor e os resource packs que não são do CurseForge).

Por isso o zip é bem menor que o `Modpack.zip` da instância, que carrega todos os mods.

## Como gerar

Na raiz da instância:

```
python3 sunlit_tools/export_curseforge.py --version 1.0.0
```

Opções úteis:

- `--name "Nome do pack"`: nome do modpack. Se não for passado, usa o nome do `minecraftinstance.json`.
- `--author "Seu nome"`: autor que aparece no manifesto.
- `--out dist/`: pasta de saída (padrão `dist/`).
- `--dry-run`: mostra o resumo (quantos mods, quantos arquivos em overrides, tamanho) sem gravar nada.

O arquivo gerado fica em `dist/<nome>-<versão>.zip`. A pasta `dist/` não entra no próprio zip.

## Como um amigo instala no CurseForge

1. Abra o app do CurseForge.
2. Clique em **Create Custom Profile**.
3. Clique em **Import** e escolha o arquivo `.zip`.
4. Confirme o nome do perfil e espere o app baixar os mods.
5. Abra o perfil e entre no mundo.

Como alternativa, o zip completo `Modpack.zip` da instância continua funcionando pelo caminho manual ou pelo `install.bat`, descritos em `READ_FIRST_PT-BR.txt`. Esse caminho não baixa mods pelo app, então o zip é bem maior.

## Publicar no CurseForge

1. Entre na conta de autor em authors.curseforge.com (conferir a página de autores no CurseForge caso o endereço tenha mudado).
2. Crie um projeto do tipo **Modpack**.
3. Envie o zip gerado em `dist/`.
4. Escolha a versão do jogo (1.20.1) e o loader (Forge 47.4.0).
5. Aguarde a revisão do CurseForge. O prazo e as regras de aprovação ficam na própria página de autores; conferir lá.

Limite de tamanho do arquivo e regras de conteúdo: conferir na página do CurseForge antes do envio. Não foi verificado aqui.

## Os mods próprios dentro de overrides

Os mods `sunlit_cinematic_toms-1.0.0.jar`, `sunlit_sortfix-1.0.0.jar`, `sunlit_replayfix-1.0.0.jar`, `sunlit_eating-1.0.0.jar`, `sunlit_qualityfix-1.0.0.jar` e `sunlit_texturefix-1.0.0.jar` não existem no CurseForge, então vão dentro de `overrides/mods/`. Isso é válido porque são mods do próprio autor do pack.

Se quiser, publique cada um como projeto próprio no CurseForge. Depois, o manifesto pode referenciá-los pelo `projectID` e `fileID`, em vez de carregá-los dentro do zip. Isso exige ajustar o script para tratá-los como addons externos.

## Modrinth

O Modrinth usa outro formato, o `.mrpack`. Pontos a verificar antes de publicar lá:

- Mods precisam estar no Modrinth, ou estar dentro do pack com permissão do autor original.
- Dá para converter o zip do CurseForge, por exemplo com o packwiz ou exportando a instância pelo Prism Launcher. Não foi testado aqui; confirmar as ferramentas e os passos na documentação oficial de cada uma antes de usar.

## Permissão do autor original

Este pack é uma **versão modificada** do modpack **Society: Sunlit Valley** (projeto CurseForge 1093382, versão base 4.1.5A).

- Publicar este pack publicamente precisa da **permissão do autor original**.
- O nome público definido pelo dono é **Society: Sunlit Valley - Pipinha's Village Edition** (padrão do script). Como ele contém o nome do original, deixe claro na página que é uma edição não oficial e dê os créditos ao projeto original.
- Confira a licença do pack original na página dele no CurseForge antes de publicar qualquer coisa.

## Checklist de release

1. Aumentar a versão (`--version`).
2. Rodar o export e conferir o resumo (`--dry-run` primeiro).
3. Testar a importação em um perfil novo do CurseForge (perfil limpo, sem o `Modpack.zip`).
4. Abrir o save solo e conferir o mundo, as configs e os textos das quests.
5. Escrever o changelog da versão.
6. Só então enviar o zip para publicação.

## Anotações

**Ainda em aberto:** a tradução e os passos do Modrinth e os limites do CurseForge não foram verificados nesta versão do documento.
