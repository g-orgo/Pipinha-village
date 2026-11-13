#!/usr/bin/env python3
"""Writes the five profession contact shops (phone-only, stage-gated).

Shops: grocer, bait_shop, farm_coop, feed_store, vintner. Each one is gated by
its profession stage and has no entity or villager profession.

Pricing: sellable goods use cost = ceil(1.5 * sell_value * count), where
sell_value comes from the price audit dump ("trades"[item]["v"]). Items with a
FIXED price use that price. The request coin is the largest coin whose value
is <= cost, with count = round(cost / coin).

Run from the instance root. Order matters: run this generator first, then
mercantil_discounts.py, because the generator rewrites the base shop files and
mercantil_discounts.py adds the discounted copies on top of them:
  python3 sunlit_tools/profession_contacts.py [--dump PATH] [--ids]
  python3 sunlit_tools/mercantil_discounts.py
--ids prints the trade_id lists to paste into GROUPS in mercantil_discounts.py.
Idempotent: the shop files are rebuilt from scratch on every run.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

SHOPS = Path("kubejs/data/society_trading/shops")
DEFAULT_DUMP = "/home/Orgo/.claude/jobs/7cb7e8be/tmp/audit/dump.json"
SEASONS = {
    "Sp": ["early_spring", "mid_spring", "late_spring"],
    "Su": ["early_summer", "mid_summer", "late_summer"],
    "Au": ["early_autumn", "mid_autumn", "late_autumn"],
    "Wi": ["early_winter", "mid_winter", "late_winter"],
}
COINS = [
    ("numismatics:sun", 4096), ("numismatics:crown", 512), ("numismatics:cog", 64),
    ("numismatics:sprocket", 16), ("numismatics:bevel", 8), ("numismatics:spur", 1),
]
# Entry: (item, count, season code or None for all year, fixed cost or None for value-priced).
ALL = None
SHOP_SPECS = {
    "grocer": {
        "name": "shop.society_trading.grocer",
        "texture": "farmersdelight:textures/block/cabbage_crate_top",
        "jei": "farmersdelight:cabbage_crate",
        "stage": "profession_cook",
        "entries": [
            ("minecraft:egg", 8, ALL, None), ("society:milk", 4, ALL, None),
            ("kaleidoscope_cookery:flour", 4, ALL, None), ("kaleidoscope_cookery:rice", 8, ALL, None),
            ("farm_and_charm:butter", 2, ALL, None),
            ("minecraft:beef", 2, ALL, None), ("minecraft:porkchop", 2, ALL, None),
            ("minecraft:chicken", 2, ALL, None), ("minecraft:mutton", 2, ALL, None),
            ("minecraft:cod", 2, ALL, None),
            ("kaleidoscope_cookery:tomato", 4, "SpSuAu", None),
            ("veggiesdelight:turnip", 4, "Sp", None), ("farm_and_charm:strawberry", 4, "Sp", None),
            ("farm_and_charm:onion", 4, "Sp", None), ("veggiesdelight:cauliflower", 4, "Sp", None),
            ("kaleidoscope_cookery:lettuce", 4, "Sp", None), ("minecraft:carrot", 4, "SpAu", None),
            ("minecraft:potato", 4, "Sp", None), ("veggiesdelight:garlic", 4, "Sp", None),
            ("vintagedelight:cucumber", 4, "Sp", None), ("society:blueberry", 4, "Su", None),
            ("minecraft:wheat", 4, "SuAu", None), ("veggiesdelight:bellpepper", 4, "Su", None),
            ("minecraft:melon_slice", 8, "Su", None), ("culturaldelights:corn_cob", 4, "SuAu", None),
            ("farm_and_charm:oat", 4, "Su", None), ("society:eggplant", 4, "Au", None),
            ("society:cranberry", 4, "Au", None), ("farm_and_charm:barley", 8, "AuWi", None),
            ("minecraft:beetroot", 4, "Au", None), ("minecraft:pumpkin", 1, "Au", None),
            ("farmersdelight:cabbage", 2, "AuWi", None), ("veggiesdelight:sweet_potato", 4, "Au", None),
            ("snowyspirit:ginger", 4, "Wi", None),
        ],
    },
    "bait_shop": {
        "name": "shop.society_trading.bait_shop",
        "texture": "aquaculture:textures/item/worm",
        "jei": "aquaculture:worm",
        "stage": "profession_fisher",
        "entries": [
            ("aquaculture:worm", 16, ALL, 256), ("aquaculture:minnow", 4, ALL, None),
            ("aquaculture:leech", 1, ALL, None), ("crabbersdelight:crab_trap_bait", 16, ALL, 96),
            ("aquaculture:fishing_line", 4, ALL, 64),
        ],
    },
    "farm_coop": {
        "name": "shop.society_trading.farm_coop",
        "texture": "dew_drop_farmland_growth:textures/item/weak_fertilizer",
        "jei": "dew_drop_farmland_growth:weak_fertilizer",
        "stage": "profession_farmer",
        "entries": [
            ("dew_drop_farmland_growth:weak_fertilizer", 8, ALL, 512),
            ("dew_drop_farmland_growth:low_quality_fertilizer", 8, ALL, 512),
            ("dew_drop_farmland_growth:hydrating_fertilizer", 8, ALL, 256),
            ("dew_drop_farmland_growth:strong_fertilizer", 1, ALL, 192),
            ("dew_drop_farmland_growth:deluxe_hydrating_fertilizer", 1, ALL, 512),
            ("minecraft:bone_meal", 16, ALL, 64),
        ],
    },
    "feed_store": {
        "name": "shop.society_trading.feed_store",
        "texture": "minecraft:textures/block/hay_block_side",
        "jei": "society:animal_feed",
        "stage": "profession_rancher",
        "entries": [
            ("society:animal_feed", 16, ALL, 256), ("society:animal_feed", 64, ALL, 1024),
            ("minecraft:hay_block", 1, ALL, None), ("minecraft:wheat", 16, ALL, None),
        ],
    },
    "vintner": {
        "name": "shop.society_trading.vintner",
        "texture": "vinery:textures/item/red_grape",
        "jei": "vinery:red_grape",
        "stage": "profession_winemaker",
        "entries": [
            ("vinery:red_grape_seeds", 1, "SpAu", 256), ("vinery:white_grape_seeds", 1, "SpAu", 256),
            ("vinery:savanna_grape_seeds_red", 1, "SpSu", 512),
            ("vinery:savanna_grape_seeds_white", 1, "SpSu", 512),
            ("vinery:jungle_grape_seeds_red", 1, "Su", 512),
            ("vinery:jungle_grape_seeds_white", 1, "Su", 512),
            ("vinery:taiga_grape_seeds_red", 1, "Wi", 512),
            ("vinery:taiga_grape_seeds_white", 1, "Wi", 512),
            ("vinery:red_grape", 8, "SpAu", None), ("vinery:white_grape", 8, "SpAu", None),
            ("vinery:savanna_grapes_red", 8, "SpSu", None), ("vinery:savanna_grapes_white", 8, "SpSu", None),
            ("vinery:jungle_grapes_red", 8, "Su", None), ("vinery:jungle_grapes_white", 8, "Su", None),
            ("vinery:taiga_grapes_red", 8, "Wi", None), ("vinery:taiga_grapes_white", 8, "Wi", None),
        ],
    },
}


def coin_request(cost):
    for item, value in COINS:
        if cost >= value:
            return {"item": item, "count": round(cost / value)}
    raise ValueError(f"cost {cost} is below the smallest coin")


def seasons_for(code):
    return [s for pair in re.findall(r"..", code) for s in SEASONS[pair]]


def build_trades(shop_id, entries, values):
    trades = []
    for item, count, code, fixed in entries:
        if fixed is None:
            if item not in values:
                sys.exit(f"missing sell value for {item} in the audit dump")
            cost = math.ceil(1.5 * values[item] * count)
        else:
            cost = fixed
        trade = {
            "offer": {"item": item, "count": count},
            "request": coin_request(cost),
            "numismatics_cost": cost,
        }
        if code is not None:
            trade["seasons_required"] = seasons_for(code)
        trade["trade_id"] = f"{shop_id}_{item.split(':', 1)[1]}_x{count}"
        trades.append(trade)
    ids = [t["trade_id"] for t in trades]
    if len(ids) != len(set(ids)):
        sys.exit(f"duplicate trade_id in {shop_id}")
    return trades


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", default=DEFAULT_DUMP)
    parser.add_argument("--ids", action="store_true", help="print trade_id lists for GROUPS")
    args = parser.parse_args()

    dump = json.loads(Path(args.dump).read_text(encoding="utf-8"))["trades"]
    values = {item: rec["v"] for item, rec in dump.items() if "v" in rec}

    for shop_id, spec in SHOP_SPECS.items():
        trades = build_trades(shop_id, spec["entries"], values)
        shop = {
            "shop_id": shop_id,
            "name": spec["name"],
            "texture": spec["texture"],
            "jei_catalyst": {"item": spec["jei"]},
            "stage_required": spec["stage"],
            "selector_weight": -94,
            "trades": trades,
        }
        path = SHOPS / f"{shop_id}.json"
        path.write_text(json.dumps(shop, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{shop_id}: {len(trades)} trades")
        if args.ids:
            print("  " + ", ".join(f'"{t["trade_id"]}"' for t in trades))


if __name__ == "__main__":
    main()
