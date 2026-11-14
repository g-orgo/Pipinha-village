# Pipinha's Village (Minecraft 1.21.1, NeoForge 21.1.265)

Modpack de fazenda, comércio e vida na cidade, baseado no Society: Sunlit Valley.

Esta branch é a versão 1.21.1, que existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1. Ela vem com Create Aeronautics, Aeronautics Camera Sync, Create High Seas e Sable. A branch `main` ainda é a 1.20.1 até a migração terminar.

## Estado

- Mods, configs e dados no formato 1.21 já estão no lugar, e o pack abre limpo.
- Scripts KubeJS, missões, lojas e vilas estão sendo portados por etapas. Até o fim da migração, a 1.20.1 continua sendo a edição jogável.
- Plano, fases e decisões: `docs/migracao/PLANO.md` e `docs/context/`.

## Instalação

Você só precisa criar o perfil com a versão certa no seu launcher. O instalador resolve o resto: mods, configs, KubeJS, resource packs, datapacks e a ordem dos resource packs.

1. No launcher (CurseForge, Prism Launcher, MultiMC, Modrinth App...), crie um perfil com **Minecraft 1.21.1** e **NeoForge 21.1.265**.
2. Abra a pasta do perfil (CurseForge: botão direito no perfil > Open Folder).
3. Coloque nela o `Modpack.zip` e o instalador do seu sistema:
   - **Windows:** `install.bat`, e dê dois cliques nele.
   - **Linux:** `install.sh`, e rode `bash install.sh` no terminal, dentro da pasta.
4. Abra o perfil no launcher e jogue.

Feche o launcher e o Minecraft antes de rodar o instalador. Ele confere se o perfil é 1.21.1 com NeoForge 21.1.265 e pergunta antes de continuar se não for. Ele apaga as pastas `mods`, `kubejs`, `resourcepacks` e `moonlight-global-datapacks` do perfil, copia as do pack e, num `options.txt` já existente, troca só as linhas dos resource packs.

O zip do GitHub (**Code > Download ZIP** desta branch) funciona no lugar do `Modpack.zip`. Num clone do repositório, rode o instalador do clone passando a pasta do perfil (`bash install.sh "/caminho/do/perfil"`, ou arraste a pasta para cima do `install.bat`).

Recomendado: 8 GB de memória para o perfil. Num PC com 16 GB de RAM, mais do que isso joga o sistema no swap.

### Instalação manual

1. Crie o perfil 1.21.1 com NeoForge 21.1.265.
2. Apague as pastas `mods`, `kubejs`, `resourcepacks` e `moonlight-global-datapacks` da pasta do perfil.
3. Extraia o `Modpack.zip` na pasta do perfil, mantendo as pastas, e substitua os arquivos quando perguntado.

Não misture arquivos da edição 1.20.1 com esta: jars e scripts da 1.20.1 não carregam na 1.21.1. Mundos da 1.20.1 só devem ser abertos numa cópia do save.

## Para quem mantém o pack

- `python3 tools/pack_tools/build_modpack.py` gera o `Modpack.zip` na raiz da instância (`--dry-run` mostra o resumo sem gravar).
- `python3 tools/pack_tools/sync_repo.py -m "mensagem"` espelha a instância nesta branch (conteúdo do `Modpack.zip` mais `docs/`, `tools/` e os arquivos de instruções), faz o commit e o push.
- Como publicar no CurseForge: `docs/PUBLICAR.md`.
