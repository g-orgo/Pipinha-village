"""Guarda da lista de resourcepacks do options.txt (Sunlit Valley).

Problema: as vezes o jogo cai numa corrida de threads (ConcurrentModificationException
no ModelBakery, com o mixin do Jade no meio) durante a recarga de recursos; o fallback
do jogo esvazia a selecao de packs e SALVA o options.txt com `resourcePacks:[]`. Na
proxima abertura (inclusive via QuickPlay) os visuais somem (Excalibur, FreshAnimations...).

O que este script faz: vigia o options.txt e, se a linha resourcePacks aparecer vazia
(`resourcePacks:[]`), recoloca a linha canonica (packs_canonical.txt). Qualquer outra
linha do options.txt nunca e tocada.

Uso:
  python3 guard_packs.py --once     confere e corrige uma vez, mostra o que fez
  python3 guard_packs.py --daemon   vigia em loop (para oautostart do sistema)
  python3 guard_packs.py --status   mostra o estado atual sem alterar nada
"""
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
INSTANCE = os.path.dirname(BASE)
OPTIONS = os.path.join(INSTANCE, "options.txt")
CANON_FILE = os.path.join(BASE, "packs_canonical.txt")
INTERVAL = 5


def read_options():
    with open(OPTIONS, encoding="utf-8") as f:
        return f.read().splitlines()


def packs_line(lines):
    return [l for l in lines if l.startswith("resourcePacks:")]


def canon_line():
    with open(CANON_FILE, encoding="utf-8") as f:
        for l in f.read().splitlines():
            if l.startswith("resourcePacks:"):
                return l
    raise RuntimeError("linha resourcePacks ausente em packs_canonical.txt")


def needs_fix(lines):
    pl = packs_line(lines)
    return len(pl) != 1 or pl[0].strip() == "resourcePacks:[]"


def fix_once():
    lines = read_options()
    if not needs_fix(lines):
        return False
    canon = canon_line()
    out = [(canon if l.startswith("resourcePacks:") else l) for l in lines]
    if len(packs_line(lines)) != 1:
        out = [l for l in out if not l.startswith("resourcePacks:")] + [canon]
    tmp = OPTIONS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    os.replace(tmp, OPTIONS)
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--once"
    if mode == "--status":
        print("vazia?" , needs_fix(read_options()))
        return
    if mode == "--once":
        print("restaurado" if fix_once() else "ok")
        return
    if mode == "--daemon":
        last_mtime = 0.0
        while True:
            try:
                mt = os.path.getmtime(OPTIONS)
                if mt != last_mtime:
                    last_mtime = mt
                    if fix_once():
                        print(time.strftime("%Y-%m-%d %H:%M:%S"),
                              "resourcePacks vazio, linha canonica recolocada", flush=True)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S"), "erro:", e, flush=True)
            time.sleep(INTERVAL)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
