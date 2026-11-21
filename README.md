# Pipinha's Village (Minecraft 1.21.1, NeoForge 21.1.265)

Modpack de fazenda, comércio e vida na cidade, baseado no Society: Sunlit Valley.

Esta é a versão 1.21.1, que existe porque queríamos o **Create Aeronautics** no pack, e ele não existe para 1.20.1. Ela vem com Create Aeronautics, Aeronautics Camera Sync, Create High Seas, Sable, Let it Walk! (máquinas que andam), Create Waystones Integration e FTB Stuff & Things. Quem quiser a edição 1.20.1 encontra na branch [`1.20.1`](https://github.com/g-orgo/Pipinha-village/tree/1.20.1).

## Estado

- Mods, configs e o conteúdo estático (receitas, tags e dados) já estão no formato 1.21, e o save de teste foi convertido sem perda.
- Em andamento: missões, lojas, vilas e a cidade gerada pelo Lost Cities. Scripts e blocos ainda sem porte ficam listados em `docs/context/state.md`.
- Plano, fases e decisões: `docs/migracao/PLANO.md` e `docs/context/`.

## Instalação

Leva uns 5 minutos. Feche o launcher e o Minecraft antes de começar.

1. **Crie o perfil.** No seu launcher (CurseForge, Prism, MultiMC, Modrinth App...), crie um perfil com **Minecraft 1.21.1** e **NeoForge 21.1.265**.
2. **Baixe o pack.** Nesta página, clique em **Code > Download ZIP**. Não extraia.
3. **Coloque na pasta do perfil.** Abra a pasta do perfil (CurseForge: botão direito no perfil > **Open Folder**) e coloque o zip lá. Abra o zip, entre na pasta `Pipinha-village-main` e arraste para a pasta do perfil o instalador do seu sistema: `install.bat` (Windows) ou `install.sh` (Linux).
4. **Instale.** Windows: dois cliques no `install.bat`. Linux: abra um terminal na pasta do perfil e rode `bash install.sh`.
5. **Jogue.** Abra o perfil no launcher. Reserve 8 GB de memória para ele.

O instalador troca as pastas `mods`, `kubejs`, `resourcepacks` e `moonlight-global-datapacks` pelas do pack e mantém suas opções. Se o perfil não for 1.21.1 com NeoForge 21.1.265, ele avisa antes de mudar qualquer coisa.

- **Recebeu um `Modpack.zip`?** Faça igual, usando ele no lugar do zip do GitHub (o instalador está dentro dele).
- **O instalador não rodou?** Apague as quatro pastas acima da pasta do perfil e extraia nela o conteúdo do zip (no zip do GitHub, o que está dentro de `Pipinha-village-main`), substituindo o que for perguntado.
- **Tem mundo da 1.20.1?** Abra só uma cópia do save, e não misture arquivos das duas edições.

## Para quem mantém o pack

- `python3 tools/pack_tools/build_modpack.py` gera o `Modpack.zip` na raiz da instância (`--dry-run` mostra o resumo sem gravar).
- Num clone do repositório, o instalador aceita a pasta do perfil: `bash install.sh "/caminho/do/perfil"`, ou arraste a pasta para cima do `install.bat`.
- `python3 tools/pack_tools/sync_repo.py -m "mensagem"` espelha a instância nesta branch (conteúdo do `Modpack.zip` mais `docs/`, `tools/` e os arquivos de instruções), faz o commit e o push.
- Como publicar no CurseForge: `docs/PUBLICAR.md`.
