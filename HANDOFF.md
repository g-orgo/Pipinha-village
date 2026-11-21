# HANDOFF: migração para 1.21.1

O que já foi feito está em `docs/context/history.md` (uma linha por unidade) e o estado atual em `docs/context/state.md`, cuja seção "## Anotações" lista o que o dono precisa testar no jogo. Este arquivo guarda só as decisões do dono que continuam valendo e o que ainda está aberto e não está em `state.md`. Plano completo: `docs/migracao/PLANO.md`. Origem (só leitura): `../Society: Sunlit Valley`.

## Decisões do dono que continuam valendo

- Motivo da 1.21.1: o Create Aeronautics. Sucessores aprovados e instalados: Botania Revived (o Botania voltou como estava na 1.20.1; o Botania Seeds foi recriado em KubeJS), Fantasy's Furniture (port não oficial), Youkai's Homecoming, Redomesticate, Refined Storage Quartz Arsenal, Sunrise Gardening (no lugar do Sturdy Farmland) e Redecorate (no lugar do Re:Deco).
- Splendid Slimes e Splendid Cogs seguem fora do pack (sem port).
- Save "Solito solamente": a cópia convertida é o mundo principal. O original, a 1.20.1 e a `main` não são tocados. "Mapa solo" é só mundo de teste.
- Options e atalhos: só com autorização do dono, e só `key_*` e configs de tecla. A tecla V do Punchy Moves fica sem tecla e não deve ser religada. O dodge do ParCool também fica sem tecla.
- Resource packs: cada zip da 1.20.1 foi trocado pela versão 1.21.1 na mesma posição (autorizado em 2026-11-12).
- Mods próprios: triar um por um. Se o bug ainda existe na 1.21.1, portar para NeoForge ou refazer em KubeJS. Mostrar a lista ao dono antes de portar.
- Identidade: o pack é Pipinha's Village. Só a linha de crédito cita a origem.
- Entrega (F11): a 1.21.1 vai para a `main` e sai um Modpack.zip novo somente com confirmação do dono. A 1.20.1 fica numa branch própria. Push na branch `1.21.1` é autorizado; nunca force-push e nunca na `main` sem confirmação.

## Pendente

### Decisões do dono

- Substitutos sem equivalente: hyper_experience (CEI 2 não tem), sap e aloe_gel (Central Kitchen 1.21 não registra) e ovo do Species (mod ausente). As receitas que dependem deles são puladas pelo guard.
- Extrusor: blackstone e cobbled_limestone seguem sem substituto (já está em `state.md`).
- Nomes de itens com o nome da origem (Crystal, Flux, Singing Frog, Market) e link da wiki (conferir: a wiki pode já estar como "Society Wiki").
- Vidro da estufa: `minecraft:glass` x24 no lugar do vidro do More Minecarts. Decisão reversível, avisar o dono.
- Tapper da wise oak: o item de lótus negra foi reposto ou segue removido? (conferir)
- Itens sem receita a decidir: gnome, quality_washer, mana_sprinkler, relics:blazing_flask, quark:slime_in_a_bucket e conchas do unusualfishmod.
- Itens sem par no save convertido, que somem: verdantvibes (103 plantas), spawner do splendid_slimes, meadow sheep_cheese_block e inky_wool, species, balloonbox e botania:lexicon. Decidir se ficam ou se são trocados.
- Bountiful: quadro de recompensas não restaurado. Potes do Supplementaries (1 item cada) e o texto da prancheta do Create ("No verão, plante cotton, tomate, e wheat") também não (conferir).
- Cinemática: qual cena faltou no pacote do Cinematic Interactions 0.18.30 (o terminal do Tom's já foi refeito).

### Técnico

- F3: `config/relics/**` (formato pode ter mudado) e os ~100 arquivos "manual" de `tools/configport/REPORT.md` (conferir).
- F4/F5: sobram cerca de 1400 referências a mods ausentes em tabelas e 221 texturas sem par (`tools/kjsport/IDSCAN.md`). Corrigir só o que aparecer no log (conferir).
- F6: conferir se alguma quest ainda cita Splendid Slimes ou Splendid Cogs (já está em `state.md`).
- Bugs de mods que não são nossos, a reportar aos autores (conferir se já foram reportados): erro do Small Ships 2.0.2 ao fechar o mundo; Sunrise Gardening 1.2 (jar patcheado: `culturaldelights` -> `culturaldelightx` em CommonModEvents; original em `backups/sunrisegardening-1.2.original.jar`; autor: github.com/Chakyl/sunrise-gardening); Iron's RPG Tweaks 2.2.3 e Tanuki Decor 21.1.0.2 (jars patcheados, originais em `backups/`).
- Diagnósticos temporários a remover depois que o dono confirmar: `PAINT_DEBUG` e o log "sending" em `paintHud.js` e `checkAnimal`; `global.ARTISAN_DEBUG` (`[artisandebug]`); `[fovdebug]` em `parcoolFastRunFov.js`; `[harvestdebug]` em `harvestDebug.js`; `[parcooluse]` e `BREAKFALL_GUARD_DEBUG` do ParCool.
- Scripts de startup novos (`petMobScare.js`, `petGuideInteract.js`) só entram depois de reiniciar o jogo.

### Testes no jogo sem retorno do dono (conferir se já foram vistos)

- Carinho e HUD do animal; botão 5 e F5 (câmera); cena do terminal do Tom's; ticks das máquinas; Face Note (botão direito com a nota na mão); nomes dos NPCs na loja; ícones coloridos de moeda no tooltip; orientação dos móveis; casa cortada a oeste e sudoeste da cama (-10227 78 8339); plantação do Solito; ParCool (guarda de queda e breakfall); entrada no mundo sem modo seguro (Iron's e Tanuki); deerfix e skinfix (sessão com a Mojang fora); FOV da corrida rápida; enxada em área.

## Cuidados que seguem valendo

- Não rodar `tools/kjsport/mechanical.py`: ele regenera do OLD e apaga o port manual.
- `tools/dataport/port_data.py` não conhece todos os renames de pasta de 2026-11-13 (miners_delight, domesticationinnovation etc.). Rodar de novo recria as pastas antigas.
- Nenhum arquivo de dados `meadow:` pode usar o id antigo da lista do DataFixer (`meadow:fire_log` -> `meadow:firewood`).
- Regen de chunks só em modo `--so-claims-estrito`, sempre com backup zip antes.
- Tags do pack nunca incluem `#forge:x` quando o jar faz forge -> c (checar com `tools/dataport/tag_cycles.py`).
- No KubeJS (Rhino 2101), nunca `const` dentro de laço nem nome de topo repetido entre scripts (checar com `tools/kjsport/find_dup_toplevel.js`).
