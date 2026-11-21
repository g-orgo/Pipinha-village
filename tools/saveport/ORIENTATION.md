# Orientação e conexão de móveis na conversão 1.20.1 -> 1.21.1

Decisões de `state_rules.tsv`, medidas em 2026-11-18 com `orient_check.py` e com vistas dos
modelos em voxels (de cima, de lado e profundidade de cada face) dos jars das duas instâncias.

| família | giro | conexão | como foi conferido |
|---|---|---|---|
| CFM park bench -> Another Furniture bench | 180° | `type` -> `horizontal_1` e `horizontal_2`, mesmo valor | encosto do CFM em z=3..5 (lado norte com `facing=north`), do AF numa placa em z=13 (lado sul); perfil em x de left/right igual depois do giro |
| CFM blinds -> Beautify blinds | 180° | `extension` sai | CFM em z=0..2, Beautify em z=14..15 com `facing=north` |
| Re:Deco sofa -> Another Furniture sofa | 180° | `shape` -> `type` (`straight` = `single`) | encosto oposto (IoU 0.65 no sul); cantos inner/outer batem pelo nome; sofá reto do Re:Deco tem braços dos dois lados |
| CFM kitchen counter -> Refurbished kitchen cabinetry | 0 | `left_corner`/`right_corner` -> `inside_corner_*`, `*_inverted` -> `outside_corner_*` | rodapé recuado no mesmo lado; camada do corpo de cada canto |
| CFM desk / desk cabinet -> Refurbished desk / drawer | 0 | `type` -> `left`/`right` (single = false/false, left = true/false, right = false/true, middle = true/true) | painel de fundo no mesmo lado; ponta lateral pelo perfil em x |
| CFM sofa -> Refurbished sofa | 0 | `type` -> `shape` (`single` = `default`) | IoU 1.00 em todos os tipos |
| Re:Deco shelf -> Another Furniture shelf | 0 | conexões absolutas -> `horizontal` relativo ao facing | suporte no mesmo lado; `east=true` com `facing=north` = `right` |
| trials crafter -> crafter vanilla | 0 | `facing` -> `orientation` (`<dir>_up`) | estado vanilla |

Ficam como estão (giro 0 conferido ou bloco simétrico): cadeiras, sofás e armários CFM -> Refurbished
(porta do armário no mesmo lado), pias, cooler, Meadow (mesmo mod), Re:Deco -> Redecorate, floreira
e vaso do Vinery -> Meadow, escadas e baús vanilla, lixeira e mesas (simétricas).

Sem referência (ficam no padrão): banquinho do Re:Deco sem `facing` -> cadeira do Candlelight;
armário do Re:Deco -> armário do Refurbished (a porta do Re:Deco é desenhada pelo renderer, não pelo
JSON; nenhum no Solito nem nas paletas).

Aplicado em 2026-11-18: paletas do Lost Cities (`fix_orientation.py palettes --apply`, 1622
entradas em 677 arquivos; backup em `backups/moonlight-global-datapacks antes-orientacao-2026-11-18.tar.gz`).
Save do Solito: dry-run com 81 posições a corrigir (55 bancos, 18 persianas, 4 sofás, 4 bancadas),
aplicado em 2026-11-18 pela sessão que regenerou o mapa (81, segunda passada 0). Depois do regen estrito
(43 chunks mantidos) sobram 17 posições convertidas, todas certas; o resto do mapa sai das paletas já corrigidas.
