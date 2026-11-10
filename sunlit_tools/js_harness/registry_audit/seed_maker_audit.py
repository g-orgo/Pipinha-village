#!/usr/bin/env python3
"""Audits the Seed Maker against the sale prices in a registry_audit dump.

Usage: seed_maker_audit.py <dump.json> [--list]
Exits 1 when any recipe can sell its output for more than its inputs.

A run takes 3 crops (handleBERightClick and artisanHopper use stageCount 3). Sale values follow
globalShippingBinHandlers.js: value x quality multiplier, rounded, then x season bonus, rounded.
"""
import json
import math
import re
import sys

INPUTS_PER_RUN = 3
QUALITY_MULTS = [1, 1.25, 1.5, 2, 3]
SEASON_BONUS = 1.08


def js_round(value):
    return math.floor(value + 0.5)


def sale(value, mult=1, season=1):
    return js_round(js_round(value * mult) * season)


def fits(seed, count, crop):
    """Same season on both sides, plus the bonus on the output alone when it multiplies units."""
    for mult in QUALITY_MULTS:
        for season in (1, SEASON_BONUS):
            if count * sale(seed, mult, season) > INPUTS_PER_RUN * sale(crop, mult, season):
                return False
        if count > INPUTS_PER_RUN and count * sale(seed, mult, SEASON_BONUS) > INPUTS_PER_RUN * sale(crop, mult):
            return False
    return True


def main():
    trades = json.load(open(sys.argv[1], encoding="utf-8"))
    recipes = trades["machines"]["seedMakerRecipes"]
    trades = trades["trades"]
    priced = base_profit = strict_profit = unpriced = 0
    rows = []
    for crop, output in sorted(recipes.items()):
        match = re.match(r"(\d+)\s*x\s*(.+)", output[0])
        count, seed = int(match[1]), match[2]
        crop_price = trades.get(crop, {}).get("v")
        seed_price = trades.get(seed, {}).get("v")
        if crop_price is None or seed_price is None:
            unpriced += 1
            rows.append(f"no price  {crop} ({crop_price}) -> {count}x {seed} ({seed_price})")
            continue
        priced += 1
        total = count * seed_price
        base = total > INPUTS_PER_RUN * crop_price
        strict = not fits(seed_price, count, crop_price)
        base_profit += base
        strict_profit += strict
        mark = "PROFIT" if base else "ROUNDING" if strict else "ok"
        rows.append(f"{mark:9} {crop} {INPUTS_PER_RUN}x{crop_price:g}={INPUTS_PER_RUN * crop_price:g} -> {count}x {seed} {seed_price:g}={total:g}")
    if "--list" in sys.argv:
        print("\n".join(rows))
    print(
        f"recipes={len(recipes)} priced={priced} unpriced={unpriced} "
        f"profit_base={base_profit} profit_with_quality_and_season={strict_profit}"
    )
    return 1 if base_profit or strict_profit else 0


if __name__ == "__main__":
    sys.exit(main())
