# Passagem de trabalho: Sunlit Towns (Claude Code -> opencode)

Atualizado: 2026-10-04 04:50. Este arquivo descreve a TAREFA INTEIRA em andamento, nao so a etapa atual.
Quem continuar (opencode ou outra sessao) deve ler tudo antes de agir e atualizar a secao "Estado" ao terminar
cada item.

## Regras do projeto (obrigatorias)

- Leia `AGENTS.md` na raiz da instancia. Resumo: NUNCA mexer em `options.txt`, resourcepacks, `servers.dat`,
  `usernamecache.json`, `usercache.json`.
- Toda mudanca entra no zip de distribuicao `Modpack.zip` (raiz da instancia; antes se chamava Backup.zip):
  `zip -qu Modpack.zip <arquivos>`; arquivo apagado sai com `zip -d`. Na raiz do zip ficam `install.bat`,
  `READ_FIRST.txt`, `READ_FIRST_PT-BR.txt`. `AGENTS.md`, saves, logs e caches NUNCA entram no zip.
- Mudou a geracao do mundo (datapack, pipeline, scripts que mexem em chunk novo) => regenerar os saves com o
  jogo FECHADO (procedimento no AGENTS.md):
  `cd saves && zip -qr "<save> backup-antes-regen-<versao>-<data>.zip" "<save>" &&
   python3 ../sunlit_tools/regen_chunks.py "<save>" --radius 0 --so-jogadores --baus --fazendas`
  e mover `<save>/data/DistantHorizons.sqlite` para `saves/dh_backup_<data>/`.
- Falar com o usuario sempre em portugues do Brasil. Codigo e comentarios de codigo em ingles.
- Nao pedir permissao entre etapas; so perguntar o que for realmente necessario. Dar status curto a cada passo.
  Nunca encerrar a vez so para esperar um processo: esperar dentro dela, com timeout.

## Como o projeto funciona

- Cidades do Lost Cities (perfil `config/lostcities/profiles/sunlit_cozy.json`, worldStyle `sunlit:towns`) vem
  do datapack `moonlight-global-datapacks/sunlit_towns`, GERADO pelo pipeline em `sunlit_tools/towns`
  (base convertida uma vez do DeceasedCraft; edite pelos scripts, exceto o loot, que agora e editado direto). Detalhes em `sunlit_tools/towns/README.md`.
- Pipeline (a partir de `sunlit_tools/towns`, ~6 min no total):
  `for s in houses cozy_expansion vila remodel schematics finalize polish complexes validate; do python3 $s.py || break; done`
  `validate.py` tem que terminar em `OK: nenhum problema encontrado`.
- Em jogo (KubeJS):
  - `kubejs/startup_scripts/sunlitTownsLostCities.js`: fila de chunks gerados (PostGen) e casa virada para a
    rua (PreGen, troca a rotacao via `BuildingInfo.setBuildingType`). `sunlitTownsFronts.js` e GERADO pelo
    `schematics.py`.
  - `kubejs/server_scripts/sunlitTownsLife.js`: processa a fila no tick (orcamento de 25 ms, a cada 2 ticks):
    baixa parques 1 bloco, limita waystones (5 chunks), armor stands (marcador `structure_void`), fauna,
    1 morador por casa, golens nas ruas.
  - `kubejs/server_scripts/sunlitTownsLoot.js`: GERADO pelo `loot.py`; pools extras de loot via LootJS,
    filtrados pelo registro real.
  - `kubejs/server_scripts/sunlitTownsCheck.js`: confere estados de bloco das paletas ao carregar o mundo e
    exporta o registro real em `kubejs/exported/sunlit_registry.json`.
- Saves do usuario: `saves/Solamente unicamente` (ativo) e `saves/Nosso mapa`.

## Pedidos do usuario nesta rodada e estado

Feito (datapack reconstruido, validate OK, Modpack.zip atualizado):
1. Baus vazios: loot table invalida por item desligado; agora pools extras pelo LootJS.
2. Praca/parques 1 bloco acima: convencao da camada do chao (polish.rule_park_ground) + validate.
3. Portoes de cerca alinhados; casa de fada mobiliada; varanda nao conta como comodo.
4. Waystones a 5+ chunks; mais fauna; 1 morador por casa; golens nas ruas.
5. Hortas sempre plantadas; NENHUMA cebola nas cidades (so na loja; validate barra).
6. "Block vomit consciente": `clutter.py` mobilia densamente todas as casas de schematic (caminho livre).
7. 5 versoes tematicas por casa (7 temas: encantamento, alquimia, create, ferreiro, artesao, biblioteca,
   fazendeiro); armor stands por tema.
8. Lotes de 3 e 4 chunks + fazenda 6x6 (`complexes.py`).
9. install.bat: usa Modpack.zip, grava ZGC no perfil do CurseForge e regenera saves (precisa Python no
   Windows). READ_FIRST.txt + READ_FIRST_PT-BR.txt.
10. (DESFEITO, ver A) ZGC na instancia: `javaArgsOverride` em `minecraftinstance.json` e em
    `~/.config/CurseForge/agent/GameInstances/MinecraftGameInstance.json`
    (`-XX:+UseZGC -XX:+DisableExplicitGC -XX:+PerfDisableSharedMem -XX:+ParallelRefProcEnabled`).
    Backups dos dois arquivos originais: `sunlit_tools/backup_jvm_2026-10-04/`.
11. Tick com orcamento de tempo e fallback de setBlock (NPE na coluna 4,8 dos parques).

PENDENTE (nesta ordem):
A. **O mundo travava em 0%** (RESOLVIDO e confirmado: sessao das 17:17 entrou no mundo em 3,5 min, igual a sessao boa das 04:24; a abertura e lenta porque o mod vminus recarrega todos os recursos 6 vezes, uma por dimensao). Causa: ZGC do Java 17. Todas as sessoes com
   ZGC (04:41, 16:56, 17:06) ficaram lentissimas no reload de dados (tags/receitas do KubeJS: 85 s contra 14 s
   sem ZGC na sessao boa das 04:24) e no preparo do spawn. O ZGC foi removido: `javaArgsOverride` = null nos dois
   arquivos do perfil (memoria ficou 8032 MB, escolhida pelo usuario), e saiu do install.bat e dos READ_FIRST.
   Se ainda demorar: a primeira carga depois de uma regeneracao gera as cidades em volta do jogador (Lost Cities
   carrega milhares de assets na primeira vez); medir no latest.log o tempo entre "Found ... recipes",
   "Started DhClientServerLevel" e o fim do "Preparing spawn area".
A2. Rodada 17:30 (FEITO no codigo, datapack reconstruido, validate OK, Modpack.zip atualizado):
   chunk que falhava (filler de jardim de lote fora da paleta do estilo; validate agora barra), "virar casa para
   a rua" ambiguo no Rhino (agora mapa por getIterable), Error setting loot (fix_loot no fim do polish), casa
   rosa com degraus virando cama (vanilla_furni.beds), sotao sem moveis (regra de varanda so no terreo), subsolo
   baixo fica deposito, catalogo Create sem manivela/eixo/serra soltos, nada em cima de caixote/barril/saco,
   mesa solta ganha cadeiras, colmeias no max 2 por parque, vegetacao do LC debaixo de peca de parque sai,
   vinhedo sem trigo, menos parques (openLotParkChance 0.5, parkChance 0.4, parkchance x0.6) e 4 rotacoes por
   parque com pesos iguais. Save regenerado (v13, 17:55): 2158 apagados, 15 preservados; backup `saves/Solamente unicamente backup-antes-regen-v13-2026-10-04.zip`, DH em `saves/dh_backup_2026-10-04_v13/`. Casa rosa renomeada para `vermelha`; mesa sem peca solta entre cadeiras (clutter: nada solto encostado em mesa/assento).
B. Teste em jogo (pedir ao usuario) e conferir `[Sunlit Towns]` no log:
   - baus com itens (LootJS) e sem erro "Couldn't parse element loot_tables:sunlit";
   - casas viradas para a rua (log "virada para a rua"; antes falhava por metodo ambiguo, ja corrigido);
   - parques no nivel certo; portoes; cebola ausente; interiores densos; armor stands; lotes e fazenda;
   - `INVALIDO` do sunlitTownsCheck tem que ser 0.
C. Pendencias conhecidas (melhorias, fazer depois de A e B):
   - `POI data mismatch` no log ao mover/trocar blocos de profissao (so ruido).
   - Fazenda 6x6 raramente cabe dentro da cidade (tambem existe como scattered no campo).
   - O clutter so roda nas casas de schematic; casas importadas e construcoes proprias (galpao) nao.
   - Depois de qualquer mudanca de geracao: regenerar os saves e atualizar Modpack.zip.

## Arquivos-chave

`sunlit_tools/towns/`: convert.py (legado, nao rodar: DeceasedCraft desinstalado), mapping.py, mix.py, loot.py, parks.py, schematics.py, vanilla_furni.py,
clutter.py, complexes.py, polish.py, lcparts.py, validate.py, README.md. `sunlit_tools/regen_chunks.py`.
`install.bat`, `READ_FIRST.txt`, `READ_FIRST_PT-BR.txt`, `AGENTS.md`.

## Rodada 2026-10-05 03:15 (FEITO, datapack reconstruido, validate OK, Modpack.zip atualizado)

- Loot em niveis (`loot.py` gera `kubejs/server_scripts/sunlitTownsLoot.js`): bau comum = 2 a 4 itens reais
  (tema + BASIC ate pouco acima de ferro) + 1 comida + 1 bebida + warm/cold string pareadas; bau rico (12%,
  deposito sempre) = 10 a 16 itens de qualquer nivel, max 3 strings, sem comida/bebida. O resto e
  PREENCHIMENTO DE ESPACO VAZIO com drops de mobs ate 75-100% do container.
- `itemcheck.py`: tira guias/manuais, itens de `globalRemovedItems.js`, namespace quark e itens com icone
  quebrado (modelo/textura ausente nos jars; cache em `item_icons.json`).
- `polish.py`: partes _90/_270 importadas com blocos de eixo sem girar trocam x/z (flywheel saindo da parede,
  postes deitados; 1926 blocos); RETOUCH `park_12` (bancos de quartzo soltos na borda, postes sem lanterna).
- Save ativo agora e `saves/Solo`: regenerado v14 (2271 apagados, 13 preservados), backup
  `saves/Solo backup-antes-regen-v14-2026-10-05.zip`, DH em `saves/dh_backup_2026-10-05_v14/`; flywheel do
  chunk preservado (231,75,248) corrigido direto no .mca.
- Nao verificado em jogo: abrir baus e conferir `[Sunlit Towns] loot` / `niveis de loot registrados` no log.
