#!/usr/bin/env python3
"""Food inventory of the pack, from sunlit_tools/eating dumps of the real game.

Writes docs/animacoes-inventario.md: item, mod, kind, pose, bite frames, Immersive Eating.
Run from the instance root with the game closed. Dumps come from sunlit_tools/headless_client.
"""
import collections
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, "sunlit_tools")
from eating_assets import active_sources, load_model_dump, is_flat, has_frames  # noqa: E402

DUMP = "sunlit_tools/eating/foods_dump.txt"
POSES = "sunlit_tools/eating/food_poses.txt"
OUT = "docs/animacoes-inventario.md"
IE_JAR = "mods/kaleidoscope_immersiveEating-forge1.20.1-1.4.3.jar"
ID = re.compile(r'["\']([a-z0-9_.-]+:[a-z0-9_/.-]+)["\']')


def ids_in(path):
    with open(path, encoding="utf-8") as f:
        return set(ID.findall(f.read()))


def ie_definitions():
    items = {}
    with zipfile.ZipFile(IE_JAR) as jar:
        for name in jar.namelist():
            if name.startswith("assets/food/definitions/") and name.endswith(".json"):
                items[json.loads(jar.read(name))["item"]] = name
    try:
        from glob import glob
        for path in glob("kubejs/assets/food/definitions/*.json"):
            with open(path, encoding="utf-8") as f:
                items[json.load(f)["item"]] = path
    except OSError:
        pass
    return items


def main():
    removed = ids_in("kubejs/startup_scripts/globalRemovedItems.js")
    canon_src = open("kubejs/startup_scripts/globalCanonicalItems.js", encoding="utf-8").read()
    duplicates = set(re.findall(r'^\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"\s*:', canon_src, re.M))
    ie = ie_definitions()
    poses = dict(l.strip().split("|") for l in open(POSES, encoding="utf-8"))
    models = load_model_dump()
    src = active_sources()
    rows = []
    by_path = collections.defaultdict(list)
    for line in open(DUMP, encoding="utf-8"):
        f = line.rstrip("\n").split("|")
        item, edible, anim = f[0], f[1] == "true", f[2]
        status = "removido" if item in removed else "duplicado" if item in duplicates else "ativo"
        kind = "comida" if edible and anim == "EAT" else "bebida" if anim == "DRINK" and edible else "outro"
        model = models.get(item)
        ns, path = item.split(":", 1)
        frames = has_frames(model) or os.path.isfile(f"kubejs/assets/{ns}/models/item/sunlit_bite/{path}_0.json")
        flat = is_flat(model, src, item) if model else False
        if status == "ativo":
            by_path[item.split(":", 1)[1]].append(item)
        rows.append((item, item.split(":")[0], kind, status, poses.get(item, "-"), frames, flat, item in ie))
    rows.sort()
    active = [r for r in rows if r[3] == "ativo"]
    collisions = {p: v for p, v in by_path.items() if len(v) > 1}
    with open(OUT, "w", encoding="utf-8") as o:
        o.write("# Inventário de comidas e bebidas\n\n")
        o.write("Gerado por `sunlit_tools/food_inventory.py` a partir do registro do jogo real. Não editar à mão.\n\n")
        o.write(f"- Itens com uso de comer ou beber no registro: **{len(rows)}**. Ativos (nem removidos, nem duplicados): **{len(active)}**.\n")
        kinds = collections.Counter(r[2] for r in active)
        o.write(f"- Ativos por tipo: {kinds['comida']} comidas, {kinds['bebida']} bebidas, {kinds['outro']} outros (usam a animação de comer ou beber, mas não têm dados de comida).\n")
        o.write(f"- Comidas ativas com frames de mordida: {sum(1 for r in active if r[2] == 'comida' and r[5])}. Sem frames e com ícone 3D, sem como gerar: {sum(1 for r in active if r[2] == 'comida' and not r[5] and not r[6])}.\n")
        o.write(f"- Com animação completa de primeira pessoa (Immersive Eating): {sum(1 for r in active if r[7])}.\n\n")
        o.write("## Colisões de path\n\n")
        o.write("O Immersive Eating escolhe o modelo pelo path do item, sem o namespace, mas antes confere o id completo na lista de definições. Só há problema se dois itens com o mesmo path tiverem definição.\n\n")
        hit = {p: v for p, v in collisions.items() if sum(1 for i in v if i in ie) > 1}
        o.write(f"- Colisões entre itens ativos: {len(collisions)}.\n")
        o.write("- Colisões que afetam animação completa: " + (", ".join(f"`{p}` ({', '.join(v)})" for p, v in sorted(hit.items())) or "nenhuma") + ".\n\n")
        o.write("## Itens ativos\n\n| Item | Mod | Tipo | Pose em terceira pessoa | Mordidas | Ícone | Animação completa |\n| --- | --- | --- | --- | --- | --- | --- |\n")
        for r in active:
            o.write(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[4]} | {'sim' if r[5] else 'não'} | {'plano' if r[6] else '3D'} | {'sim' if r[7] else 'não'} |\n")
    print(f"{len(rows)} rows, {len(active)} active, {len(collisions)} collisions, IE hits {list(hit)}")


if __name__ == "__main__":
    main()
