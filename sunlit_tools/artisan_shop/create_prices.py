"""Recipe-based buy price for Create items sold by the Artisan shop.
Usage: python3 create_prices.py <instance> <extracted create jar dir> <registry_audit dump.json> items.txt out.json

Cost = sum(ingredient buy prices) / output count * 1.35 per step (pack rule),
cascading. Base buy prices come from existing shops (blacksmith/carpenter) or
2x the shipping-bin sell value (same ratio the blacksmith uses for redstone/coal).
"""
import json, os, sys, glob, re, math

INST = sys.argv[1]
JAR = sys.argv[2]          # extracted create jar root (data/create/recipes)
DUMP = sys.argv[3]
STEP = 1.35

sell = json.load(open(DUMP))['trades']

BASE = {
    'numismatics:spur': 1, 'numismatics:bevel': 8, 'numismatics:sprocket': 16,
    'numismatics:cog': 64, 'numismatics:crown': 512, 'numismatics:sun': 4096,
    'numismatics:ancient_coin': 262144,
    'minecraft:iron_ingot': 64, 'minecraft:copper_ingot': 16, 'create:zinc_ingot': 128,
    'minecraft:gold_ingot': 256, 'minecraft:redstone': 16, 'minecraft:coal': 16,
    'oreganized:lead_ingot': 64, 'oreganized:silver_ingot': 128,
    'minecraft:cobblestone': 0.5, 'minecraft:stone': 1, 'minecraft:andesite': 1,
    'minecraft:glass': 3, 'minecraft:oak_planks': 1, 'minecraft:oak_log': 4,
    'minecraft:stripped_oak_log': 4, 'minecraft:stick': 0.5, 'minecraft:oak_slab': 0.5,
    'meadow:fire_log': 410,  # carpenter: 10 fire logs for building supplies (4096)
    'minecraft:netherrack': 1, 'minecraft:string': 2, 'minecraft:paper': 2,
    'minecraft:slime_ball': 8, 'supplementaries:rope': 2, 'minecraft:white_wool': 4,
    'minecraft:obsidian': 16, 'minecraft:ender_pearl': 64, 'minecraft:blaze_rod': 64,
    'minecraft:crafting_table': 4, 'minecraft:chest': 8, 'minecraft:barrel': 7,
    'minecraft:lever': 1, 'minecraft:redstone_torch': 17, 'minecraft:observer': 40,
    'minecraft:piston': 80, 'minecraft:sticky_piston': 90, 'minecraft:hopper': 330,
    'minecraft:dispenser': 30, 'minecraft:shears': 128, 'minecraft:compass': 320,
    'minecraft:clock': 1040, 'minecraft:lightning_rod': 48, 'minecraft:bucket': 192,
    'minecraft:iron_bars': 24, 'minecraft:chain': 90, 'minecraft:rail': 25,
    'minecraft:minecart': 320, 'minecraft:smooth_stone': 2, 'minecraft:bone_meal': 2,
    'minecraft:diamond': 512, 'minecraft:netherite_ingot': 4 * 2048 + 4 * 256,
    'minecraft:netherite_upgrade_smithing_template': 49556,  # blacksmith price
    'minecraft:honeycomb': 8, 'minecraft:kelp': 4, 'minecraft:tinted_glass': 20,
    'minecraft:sculk_sensor': 64, 'minecraft:lectern': 20, 'minecraft:bell': 512,
    'minecraft:note_block': 20, 'minecraft:daylight_detector': 40, 'minecraft:comparator': 40,
    'minecraft:repeater': 40, 'minecraft:tripwire_hook': 70, 'minecraft:target': 50,
    'minecraft:sand': 1, 'minecraft:gravel': 0.5, 'minecraft:flint': 2,
    'minecraft:soul_sand': 4, 'minecraft:glass_pane': 1, 'minecraft:feather': 4,
    'create:powdered_obsidian': 22,
    'society:kinetic_blueprint': 0, 'create:cardboard': 8, 'create:cardboard_block': 8 * 4 * 1.35,
    'minecraft:dried_kelp_block': 9 * 30, 'minecraft:iron_trapdoor': 4 * 64 * 1.35,
    'minecraft:stone_pressure_plate': 2, '#minecraft:wooden_buttons': 1, '#forge:dyes/light_blue': 4,
    'minecraft:chain': 105, 'numismatics:ancient_coin': 262144,
    'oreganized:silver_sheet': 128 * STEP, 'oreganized:lead_sheet': 64 * STEP,
}
for k, v in list(BASE.items()):
    for metal in ('iron', 'gold'):
        pass
NUG = {'minecraft:iron_nugget': 'minecraft:iron_ingot', 'minecraft:gold_nugget': 'minecraft:gold_ingot',
       'create:copper_nugget': 'minecraft:copper_ingot', 'create:zinc_nugget': 'create:zinc_ingot',
       'oreganized:lead_nugget': 'oreganized:lead_ingot', 'oreganized:silver_nugget': 'oreganized:silver_ingot'}
BLK = {'minecraft:iron_block': 'minecraft:iron_ingot', 'minecraft:redstone_block': 'minecraft:redstone',
       'oreganized:lead_block': 'oreganized:lead_ingot', 'minecraft:copper_block': 'minecraft:copper_ingot',
       'minecraft:gold_block': 'minecraft:gold_ingot'}

TAGS = {
    'forge:nuggets/iron': 'minecraft:iron_nugget', 'forge:nuggets/gold': 'minecraft:gold_nugget',
    'forge:nuggets/copper': 'create:copper_nugget', 'forge:nuggets/zinc': 'create:zinc_nugget',
    'forge:nuggets/brass': 'create:brass_nugget',
    'forge:ingots/iron': 'minecraft:iron_ingot', 'forge:ingots/copper': 'minecraft:copper_ingot',
    'forge:ingots/zinc': 'create:zinc_ingot', 'forge:ingots/gold': 'minecraft:gold_ingot',
    'forge:ingots/brass': 'create:brass_ingot', 'forge:ingots/lead': 'oreganized:lead_ingot',
    'forge:ingots/silver': 'oreganized:silver_ingot',
    'forge:plates/iron': 'create:iron_sheet', 'forge:plates/copper': 'create:copper_sheet',
    'forge:plates/gold': 'create:golden_sheet', 'forge:plates/brass': 'create:brass_sheet',
    'forge:plates/lead': 'oreganized:lead_sheet', 'forge:plates/silver': 'oreganized:silver_sheet',
    'forge:storage_blocks/lead': 'oreganized:lead_block', 'forge:storage_blocks/iron': 'minecraft:iron_block',
    'forge:dusts/redstone': 'minecraft:redstone', 'forge:gems/quartz': 'minecraft:quartz',
    'forge:gems/diamond': 'minecraft:diamond',
    'minecraft:planks': 'minecraft:oak_planks', 'minecraft:logs': 'minecraft:oak_log',
    'minecraft:wooden_slabs': 'minecraft:oak_slab', 'forge:stripped_logs': 'minecraft:stripped_oak_log',
    'society:raw_logs': 'minecraft:oak_log', 'forge:rods/wooden': 'minecraft:stick',
    'forge:stone': 'minecraft:stone', 'forge:cobblestone': 'minecraft:cobblestone',
    'forge:glass': 'minecraft:glass', 'forge:glass/colorless': 'minecraft:glass',
    'forge:glass_panes': 'minecraft:glass_pane', 'forge:glass_panes/colorless': 'minecraft:glass_pane',
    'forge:slimeballs': 'minecraft:slime_ball', 'forge:rope': 'supplementaries:rope',
    'forge:netherrack': 'minecraft:netherrack', 'minecraft:wool': 'minecraft:white_wool',
    'forge:chests/wooden': 'minecraft:chest', 'forge:string': 'minecraft:string',
    'forge:obsidian': 'minecraft:obsidian', 'forge:ender_pearls': 'minecraft:ender_pearl',
    'forge:rods/blaze': 'minecraft:blaze_rod', 'create:sleepers': 'minecraft:smooth_stone',
    'forge:sand': 'minecraft:sand', 'minecraft:sand': 'minecraft:sand',
    'forge:feathers': 'minecraft:feather', 'forge:barrels/wooden': 'minecraft:barrel',
    'forge:dyes/white': 'minecraft:bone_meal', 'forge:dyes': 'minecraft:bone_meal',
    'minecraft:wooden_pressure_plates': 'minecraft:oak_planks', 'minecraft:buttons': 'minecraft:oak_planks',
    'forge:ingots/netherite': 'minecraft:netherite_ingot',
}

# recipes: jar overlaid by kubejs, minus removeById
recipes = {}
for root in (os.path.join(JAR, 'data/create/recipes'), os.path.join(INST, 'kubejs/data/create/recipes')):
    for p in glob.glob(root + '/**/*.json', recursive=True):
        rid = 'create:' + os.path.relpath(p, root)[:-5]
        try:
            recipes[rid] = json.load(open(p))
        except Exception:
            pass
rm = open(os.path.join(INST, 'kubejs/server_scripts/recipes/removeRecipes.js')).read()
rm_out_block = rm[rm.index('removeByOutput'):rm.index('removeById')]
rm_id_block = rm[rm.index('removeById'):rm.index('removeByInput')]
removed_out = set(re.findall(r'"([a-z0-9_]+:[a-z0-9_/]+)"', rm_out_block))
for rid in re.findall(r'"([a-z0-9_]+:[a-z0-9_/]+)"', rm_id_block):
    recipes.pop(rid, None)

def ing_item(x):
    if isinstance(x, list):
        x = x[0]
    if 'item' in x:
        return x['item']
    if 'tag' in x:
        return TAGS.get(x['tag'], '#' + x['tag'])
    return '?'

by_out = {}
for rid, r in recipes.items():
    t = r.get('type', '')
    outs = []
    if 'result' in r:
        res = r['result']
        outs = [(res['item'] if isinstance(res, dict) else res, res.get('count', 1) if isinstance(res, dict) else 1)]
    elif 'results' in r and r['results']:
        res = r['results'][0]
        outs = [(res.get('item'), res.get('count', 1))]
    for o, c in outs:
        if not o or o in removed_out:
            continue
        ings = []
        if t in ('minecraft:crafting_shaped', 'create:mechanical_crafting'):
            for row in r['pattern']:
                for ch in row:
                    if ch != ' ':
                        ings.append(ing_item(r['key'][ch]))
        elif t == 'minecraft:crafting_shapeless' or t in ('create:mixing', 'create:item_application', 'create:pressing', 'create:compacting', 'create:sandpaper_polishing', 'create:deploying', 'create:milling', 'create:crushing', 'create:filling', 'create:cutting'):
            for i in r.get('ingredients', []):
                if 'fluid' in i or 'fluidTag' in i or 'amount' in i:
                    continue
                ings.append(ing_item(i))
        elif t == 'create:sequenced_assembly':
            ings.append(ing_item(r['ingredient']))
            trans = r['transitionalItem']['item']
            for _ in range(r.get('loops', 1)):
                for s in r['sequence']:
                    for i in s.get('ingredients', [])[1:]:
                        if 'fluid' in i or 'amount' in i:
                            continue
                        it = ing_item(i)
                        if it != trans:
                            ings.append(it)
            tot = sum(x.get('chance', 1) for x in r['results'])
            c = r['results'][0].get('chance', 1) / tot
        else:
            continue
        if t in ('create:crushing', 'create:milling'):
            continue
        by_out.setdefault(o, []).append((rid, ings, c))

# kubejs JS shaped recipes that replaced removed outputs
JS = {
    'create:windmill_bearing': (['oreganized:lead_block', 'create:shaft'] + ['create:andesite_casing'] * 4, 1),
    'create:water_wheel': (['oreganized:lead_ingot'] * 4 + ['meadow:fire_log'] * 4, 1),
    'create:steam_engine': (['oreganized:lead_block', 'create:copper_casing'], 1),
    'create:mechanical_bearing': (['oreganized:lead_block'] * 2 + ['society:battery', 'create:shaft'] + ['create:andesite_casing'] * 2, 1),
    'create:cart_assembler': (['oreganized:electrum_block'] + ['create:brass_casing'] * 2 + ['oreganized:lead_ingot'] * 2, 1),
    'create:mechanical_saw': (['create:powdered_obsidian'] * 2 + ['numismatics:ancient_coin'] + ['minecraft:netherite_ingot'] * 3 + ['minecraft:netherite_upgrade_smithing_template'] * 2 + ['create:andesite_casing'], 1),
    'create:mechanical_harvester': (['society:prismatic_shard'] * 2 + ['numismatics:ancient_coin'] + ['minecraft:netherite_ingot'] * 3 + ['create:powdered_obsidian'] * 2 + ['create:andesite_casing'], 1),
    'create:mechanical_drill': (['numismatics:ancient_coin'] + ['minecraft:netherite_ingot'] * 4 + ['create:powdered_obsidian'] * 2 + ['society:prismatic_shard', 'create:andesite_casing'], 1),
}
for o, (ings, c) in JS.items():
    by_out.setdefault(o, []).append(('js:' + o, ings, c))
BASE['oreganized:electrum_block'] = 9 * (256 + 128) / 2 * STEP * STEP

ALIAS = {'create:sail_frame': 'create:white_sail', '#forge:storage_blocks/brass': 'create:brass_block', 'create:stressometer': 'create:speedometer', 'create:secondary_linear_chassis': 'create:linear_chassis',
         'create:repackager': 'create:packager', '#create:postboxes': 'create:white_postbox',
         '#forge:stripped_wood': 'minecraft:stripped_oak_log', '#forge:plates/obsidian': 'create:sturdy_sheet'}
NUG['create:brass_nugget'] = 'create:brass_ingot'
BLK['create:andesite_alloy_block'] = 'create:andesite_alloy'
BLK['create:brass_block'] = 'create:brass_ingot'
TAGS['forge:storage_blocks/brass'] = 'create:brass_block'
memo, stack, missing = {}, set(), set()

def cost(item):
    if item in memo:
        return memo[item]
    if item in BASE:
        return BASE[item]
    if item in ALIAS:
        return cost(ALIAS[item])
    if item in NUG:
        return cost(NUG[item]) / 9
    if item in BLK:
        return cost(BLK[item]) * 9
    if item in stack:
        return math.inf
    stack.add(item)
    best = math.inf
    for rid, ings, c in by_out.get(item, []):
        if item in ings or rid.endswith('_from_conversion') or rid.endswith('_clear'):
            continue
        s = sum(cost(i) for i in ings)
        best = min(best, s / c * STEP)
    stack.discard(item)
    if best == math.inf:
        v = sell.get(item)
        if v:
            best = v['v'] * 2
        else:
            missing.add(item)
    memo[item] = best
    return best

DEN = [('numismatics:ancient_coin', 262144), ('numismatics:sun', 4096), ('numismatics:crown', 512), ('numismatics:cog', 64),
       ('numismatics:sprocket', 16), ('numismatics:bevel', 8), ('numismatics:spur', 1)]

def coins(p):
    for name, d in DEN:
        n = round(p / d)
        if n >= 1 and n <= 64 and abs(n * d - p) / p <= 0.15:
            return name, n, n * d
    for name, d in reversed(DEN):
        n = round(p / d)
        if n <= 64:
            return name, max(n, 1), max(n, 1) * d
    name, d = DEN[0]
    n = max(1, round(p / d))
    return name, n, n * d

if __name__ == '__main__':
    items = [l.split()[0] for l in open(sys.argv[4]) if l.strip() and not l.startswith('#')]
    out = []
    for it in items:
        p = cost(it)
        if p == math.inf:
            print('NOPRICE', it, by_out.get(it))
            continue
        name, n, total = coins(p)
        out.append((it, round(p, 1), name, n, total))
        print(f'{it:45s} {p:12.1f} -> {n:3d} {name.split(":")[1]:9s} ({total})')
    print('missing:', sorted(missing))
    json.dump(out, open(sys.argv[5], 'w'))
