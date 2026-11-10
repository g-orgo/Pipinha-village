"""Regenera so as loot tables dos temas (data/sunlit/loot_tables/chests/{t}.json) no datapack de saida,
usando loot.loot_table, e reescreve o sunlitTownsLoot.js gerido pelo loot.py. Nao roda o pipeline inteiro.
Nao importa convert.py (tem efeitos colaterais); o caminho de saida e o helper de escrita sao copiados dele."""
import json, os, sys

import loot

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'moonlight-global-datapacks', 'sunlit_towns')


def write(path, obj):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        json.dump(obj, f, separators=(',', ':'))


def main():
    written, empty = 0, []
    for t in loot.THEMES:
        obj = loot.loot_table(t)
        pools = obj.get('pools') or []
        if not pools or any(not p.get('entries') for p in pools):
            empty.append(t)
        write(f'data/sunlit/loot_tables/chests/{t}.json', obj)
        written += 1
    loot.write_extra_js()  # escreve apenas kubejs/server_scripts/sunlitTownsLoot.js (gerido pelo loot.py)
    print(f'loot tables escritas: {written} em {OUT}')
    print('temas com pools vazios: ' + (', '.join(empty) if empty else 'nenhum'))


if __name__ == '__main__':
    sys.exit(main())
