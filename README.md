# Society: Sunlit Valley - Pipinha's Village Edition

Versão da Pipinha's Village do modpack **Society: Sunlit Valley** (Minecraft 1.20.1, Forge). Este repositório guarda tudo que o `install.bat` precisa para transformar uma instância do Sunlit Valley normal (4.1.5A) na Pipinha's Village: mods, resource packs, configs (com a tela de título do FancyMenu e o changelog), KubeJS, datapacks da Moonlight, `defaultconfigs`, o livro Almanac do Patchouli, shaders e o `options.txt` com a ordem dos packs.

O que muda em relação ao Sunlit normal está no changelog do menu inicial: `config/fancymenu/assets/changelog_pt_br.markdown`.

## Instalação (Windows)

Feche o Minecraft e o app do CurseForge antes de começar. No CurseForge, instale o Society: Sunlit Valley normal e abra a pasta dele (clique com o botão direito no perfil > Open Folder).

O jeito recomendado é instalar pelo `Modpack.zip`, que é o pacote oficial de distribuição do modpack: basta um clique duplo no `install.bat`. O zip do GitHub e o clone ficam como alternativa.

**Pelo Modpack.zip (recomendado)**

1. Coloque o `Modpack.zip` e o `install.bat` na pasta da instância e dê dois cliques no `install.bat`.

**Pelo zip do GitHub**

1. Em **Code > Download ZIP**, baixe o zip deste repositório.
2. Coloque o zip e o `install.bat` (que está dentro do zip) na pasta da instância.
3. Arraste o zip para cima do `install.bat`. O script também encontra sozinho um arquivo `Pipinha-village*.zip` que esteja na pasta.

**Por um clone**

1. `git clone git@github.com:g-orgo/Pipinha-village.git`
2. Arraste a pasta da instância para cima do `install.bat` que está no clone.

Nos três casos, o script apaga as pastas `mods`, `resourcepacks` e `kubejs` da instância e copia tudo por cima, sobrescrevendo o que já existe. Ele não mexe nos argumentos do Java: o perfil usa o coletor padrão do CurseForge (G1). Mais detalhes e a instalação manual estão em `READ_FIRST_PT-BR.txt` (e, em inglês, em `READ_FIRST.txt`).

## Avisos

- O `options.txt` do pacote substitui o seu, porque é ele que guarda a ordem dos resource packs: atalhos e configurações de vídeo voltam ao padrão do pack.
- Mundos já criados mantêm o terreno antigo. Só os chunks novos usam as vilas novas.
- Se o Windows reclamar de caminho longo, use uma pasta de instância com caminho curto (por exemplo `C:\Sunlit`).

## Documentação

- `docs/PUBLICAR.md`: como gerar o zip no formato do CurseForge e publicar.
- `docs/context/INDEX.md`: regras do projeto, decisões, estado atual e histórico.
- `docs/animacoes-de-comida.md` e `docs/animacoes-inventario.md`: as animações próprias do pack.
- `atalhos.md`: atalhos de teclado e a ordem padrão dos resource packs.
- `AGENTS.md`: regras para agentes que trabalham na instância, incluindo como atualizar este repositório.

## Manutenção

O repositório é um espelho do `Modpack.zip` da instância de desenvolvimento. Para atualizá-lo, rode `python3 sunlit_tools/sync_repo.py -m "mensagem"` na instância: ele copia cada arquivo listado no zip, remove os que saíram, faz o commit e o push.
