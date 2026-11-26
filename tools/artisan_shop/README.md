# Precificação da loja da Artesã

`create_prices.py` calcula o preço de compra, em moedas Numismatics, dos trades da
Artesã (`librarian`) cujo item oferecido é do namespace `create`, `simulated`, `aeronautics` ou `offroad`.

## Uso

```
python3 -I tools/artisan_shop/create_prices.py --out <arquivo.json>
python3 -I tools/artisan_shop/create_prices.py --write
```

- Sem `--write` o script só imprime a tabela e grava o relatório em `--out`. É o modo padrão e não altera nada.
- Com `--write` ele reescreve apenas `request` e `numismatics_cost` dos trades no `--shop`
  (padrão: `kubejs/data/society_trading/shops/librarian.json`).

## Regras

- Insumo bruto custa 2 vezes o valor de venda (literal em `kubejs/startup_scripts`). Sem valor de venda, usa a tabela `BASE` dividida por `OLD_BASE_RATIO` (64/22). Moedas valem o valor de face.
- Receita custa a soma dos ingredientes dividida pela quantidade de saída, multiplicada por 1,35 por etapa, em cascata. Se houver mais de uma receita, vale a mais barata.
- Se o item tiver valor de venda, o preço não fica abaixo de 2 vezes esse valor (comprar e vender na caixa nunca dá lucro).
- A loja ignora a trava de netherite: receita do `kubejs/data` que consome netherite (latão no misturador, mão de latão) é precificada pela receita original do jar. No jogo a receita continua com a trava.
- Broca, serra e colheitadeira mecânicas ficam em 2 moedas ancestrais (`GATES`). Motores portáteis de qualquer cor custam o mesmo que o vermelho.
- Item alcançado dentro de um ciclo de receitas é recalculado até estabilizar; o relatório não deve ter `unresolved`.
- Fontes de receita: jar do Create, jar do Aeronautics bundle (com os jars aninhados), jar da vanilla e as pastas `kubejs/data/<ns>/recipe`, com `removeRecipes.js` aplicado.
- Duas execuções seguidas dão o mesmo resultado; conferir com `cmp` antes de usar `--write`.
