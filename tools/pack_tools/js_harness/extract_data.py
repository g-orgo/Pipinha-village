#!/usr/bin/env python3
"""Extrai os dados reais (listas de preço e receitas das máquinas) para o harness JS.

Uso: extract_data.py <raiz da instancia> <arquivo de saida>
Gera um data.js com `global.crops`, `global.cocktails` e os `global.*Recipes` que
são Map literal (os construídos com .set() depois ficam de fora).
"""
import os
import sys

SCRIPT_DIR = "kubejs/startup_scripts"

ARRAYS = ["crops", "cocktails"]

MAPS = [
    ("customMachines/mayonnaiseMachine.js", "mayonnaiseMachineRecipes"),
    ("customMachines/cheesePress.js", "cheesePressRecipes"),
    ("customMachines/wineKeg.js", "wineKegRecipes"),
    ("customMachines/preservesJar.js", "preservesJarRecipes"),
    ("customMachines/dehydrator.js", "dehydratorRecipes"),
    ("customMachines/oilMaker.js", "oilMakerRecipes"),
    ("customMachines/loom.js", "loomRecipes"),
    ("powerfulMachines/picklingCan.js", "picklingRecipes"),
    ("customMachines/espressoMachine.js", "espressoMachineRecipes"),
    ("customMachines/tapper.js", "tapperRecipes"),
    ("customMachines/mushroomLog.js", "mushroomLogRecipes"),
    ("customMachines/deluxeWormFarm.js", "deluxeWormFarmRecipes"),
    ("customMachines/recyclingMachine.js", "recyclingMachineRecipes"),
    ("customMachines/seedMaker.js", "seedMakerRecipes"),
]


def extract_array(text, name):
    marker = "global.%s = [" % name
    if marker not in text:
        return None
    start = text.index(marker)
    end = text.index("\n];", start)
    return text[start:end + 3]


def extract_map(text, name):
    marker = "global.%s = new Map([" % name
    if marker not in text:
        return None
    start = text.index(marker)
    bracket = text.index("[", start)
    depth = 0
    for i in range(bracket, len(text)):
        ch = text[i]
        if ch in "[({":
            depth += 1
        elif ch in "])}":
            depth -= 1
            if depth == 0:
                return text[start:text.index(";", i) + 1]
    return None


def main():
    root = sys.argv[1]
    out_path = sys.argv[2]
    base = os.path.join(root, SCRIPT_DIR)

    with open(os.path.join(base, "globalRegistry.js"), encoding="utf-8") as handle:
        registry = handle.read()

    parts = []
    for name in ARRAYS:
        block = extract_array(registry, name)
        if block:
            parts.append(block)

    for path, name in MAPS:
        full = os.path.join(base, path)
        if not os.path.exists(full):
            continue
        with open(full, encoding="utf-8") as handle:
            block = extract_map(handle.read(), name)
        if block:
            parts.append(block)

    # extractinator é lista de { input, output } (não Map): serve para testar esse caminho
    parts.append(
        'global.extractinatorRecipes = [{ input: "society:relic_trove", '
        'output: [{ drop: "#society:omni_geode_special", drop_chance: 0.03 }] }];'
    )

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")
    print("data.js: %d blocos" % len(parts))


if __name__ == "__main__":
    main()
