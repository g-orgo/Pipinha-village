# AGENTS.md: Pipinha's Village (Minecraft 1.21.1, NeoForge 21.1.265)

Modpack de fazenda, comércio e vida na cidade, baseado no Society: Sunlit Valley (1.20.1).
Está em migração: o plano e as fases estão em `docs/migracao/PLANO.md`.
A instância 1.20.1 de origem fica em `../Society: Sunlit Valley` e é só leitura para este projeto.

# REGRA OBRIGATÓRIA: TESTES NO JOGO SÃO DO DONO

- O agente NÃO roda o jogo nem cliente headless. Pesa demais no PC do dono.
- Verificar só com o que é leve: conferir jars (`META-INF/neoforge.mods.toml`, dependências,
  mod ids), validar dados e ler `logs/latest.log` (tail/grep) de sessões que o dono jogou.
- No relatório, dizer o que foi verificado e como, e listar o que o dono deve olhar no jogo.

# REGRA OBRIGATÓRIA: BOM SENSO ANTES DE PERGUNTAR

- Se a melhor opção é clara e a mudança é reversível, aplicar e relatar.
- Perguntar só quando for gosto do dono ou quando uma regra deste arquivo exigir autorização.

# REGRA OBRIGATÓRIA: OPTIONS E RESOURCE PACKS

- NUNCA modificar `options.txt`, atalhos, idioma, guiScale, renderDistance, volume, nem
  ativar/reordenar resource packs sem o dono pedir.
- NUNCA tocar em `servers.dat`, `usernamecache.json`, `usercache.json`.

# REGRA OBRIGATÓRIA: NADA DA 1.20.1 É ALTERADO

- A instância `Society: Sunlit Valley`, o `Modpack.zip` dela, os saves dela e a `main` do
  repositório Pipinha-village não são tocados durante a migração.
- Conteúdo da 1.20.1 só é copiado para cá e convertido aqui.

# REGRA OBRIGATÓRIA: IDENTIDADE DO PACK

- O nome do pack é Pipinha's Village. Textos, menus, quests e docs não citam o Sunlit,
  a não ser na linha de crédito "baseado no Society: Sunlit Valley".
- IDs internos (`society:*`, nomes de mods de terceiros) continuam como estão, para não
  quebrar receitas, lojas e quests.
- Toda mudança tem cara de conteúdo original do pack: mesmo tom, ícones e layout.
- Harmonização entre mods: itens equivalentes de mods diferentes entram nas mesmas receitas,
  tags e lojas; todo insumo novo precisa de uso prático.

# REGRA OBRIGATÓRIA: REPOSITÓRIO

- Versionado na branch `1.21.1` do https://github.com/g-orgo/Pipinha-village.git
  (worktree local: `/var/home/Orgo/Documentos/Pipinha-village-1.21.1`). A `main` segue sendo
  a 1.20.1 até o dono decidir trocar. A 1.20.1 trabalha na branch `1.20.1` (clone
  `/var/home/Orgo/Documentos/Pipinha-village`); esta instância nunca escreve nela.
- Commits e pushes nessa branch são autorizados pelo dono; nunca force-push, nunca na `main`.
- Nenhum arquivo acima de 95 MB, nenhum save, log, cache, token ou dado pessoal.
