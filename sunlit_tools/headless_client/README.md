# Jogo real sem janela

Roda o cliente de verdade, com todos os mods, sob Xvfb e renderização por software, numa cópia isolada da instância. Serve para o agente verificar mudanças sem depender do dono: mixins aplicados, carregamento de assets, consumo de comida, poses e capturas de tela.

```
sunlit_tools/headless_client/run_probe.sh /tmp/minha-pasta cenarios.json
```

- A instância só é lida: `mods/` e `resourcepacks/` viram links, `config/`, `kubejs/` e o save `Solito solamente` são copiados. `options.txt` também é uma cópia, ajustada só na pasta de teste.
- Um cenário é `{"id": "minecraft:bread", "cam": "FIRST_PERSON", "pitch": -30, "n": 8, "timeout": 200, "shots": [20, 40]}`. O resultado sai em `logs/kubejs/client.log`, nas linhas `PROBE|`, e as capturas em `screenshots/`.
- Em primeira pessoa a GUI precisa ficar visível: `hideGui` esconde a mão e o Immersive Eating só avança a animação quando o modelo é desenhado.
- Espere cerca de 40 ticks entre um cenário e o próximo: trocar o item à força durante a cauda de 0,25 s da animação deixa a trava do Immersive Eating presa. Um jogador não consegue fazer isso, porque a hotbar fica travada.
- Consome cerca de 6 GB de RAM. Com outras sessões pesadas abertas, o processo pode ser morto pelo OOM killer; é só repetir.
- `dump_foods.js` regenera `sunlit_tools/eating/foods_dump.txt`. `PROBE_DUMP = true` em `probe.js` regenera `models_dump.txt`. Depois: `custom-mods/sunlit_eating/tools/PoseDump.java` para as poses, `food_inventory.py` e `gen_bite_frames.py`.

Armadilhas ao escrever cenários (2026-11-03):

- O KubeJS bloqueia `java.io.File`. Para achar um arquivo, percorra `mc.gameDirectory.listFiles()`.
- `Path.resolve(string)` é ambíguo no Rhino e `mc.tell` é do KubeJS (mensagem de chat), não da fila de tarefas; use `mc.execute`.
- `doJump` e `endReplay` rodam ticks dentro da chamada. Avance o passo do cenário antes de chamá-los, ou o handler reentra em laço.
- Nunca chame `loadLevel` de dentro de JS: o script segura o lock do Rhino e a thread do servidor trava esperando por ele. Dispare por um mod Java descartável, só na pasta de teste.
- Inclua `pack.mcmeta` no mod de teste: uma rodada sem ele não chegou a registrar a tela inicial, e a rodada com ele registrou (causa não confirmada).
- Use `systemd-run --user --scope -p MemoryMax=9G` para um estouro de memória derrubar só o teste.
- Item que não empilha: `item replace` com `n` acima do limite falha e deixa o item anterior, o que aparece como `consumed=true after=1`. Use `n: 1`.
- Prato do Cuisine Delight criado por comando não tem dados de cozimento, usa 72000 ticks e não termina em terceira pessoa. Isso é do teste.
- `fondant_pie` e outras comidas do addon têm `eat` longo (16 s): use `timeout` acima de 340.
- Se o jogo ficar no menu sem linhas `PROBE`, o `quickPlay` não entrou: encerre pelo pid e repita.
