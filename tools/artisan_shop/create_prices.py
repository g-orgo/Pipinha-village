"""Deterministic buy-price calculator for the librarian trades of the Artisan shop.

Scope: trades whose offer namespace is create, simulated, aeronautics or offroad.
Default mode is dry-run: prints a table and writes a JSON report to --out.
--write rewrites only `request` and `numismatics_cost` of those trades in --shop.

Pricing rules:
- Base prices come from BASE (values agreed with the existing shops).
- A recipe costs the sum of its ingredient prices, divided by the output count,
  times STEP (1.35) per crafting step. Cascades recursively, cycle guarded.
- The cheapest recipe wins.
- If a sell literal exists for the item (kubejs startup scripts), the price is
  at least 2 * sell (anti-arbitrage floor).
- Items without any price get the sell literal (2 * sell) or stay unresolved.
"""
import argparse, glob, io, json, math, os, re, sys, zipfile

STEP = 1.35
# Gates keep 2 ancient coin whatever their recipe costs (value in numismatics base units).
GATES = {'create:mechanical_drill': 2 * 262144, 'create:mechanical_saw': 2 * 262144,
         'create:mechanical_harvester': 2 * 262144}
NETHERITE_SWAPS = []  # recipe ids whose kubejs override needs netherite; the jar recipe is priced instead
OLD_BASE_RATIO = 64 / 22  # old base iron ingot 64, new base 2 x sell 11
NAMESPACES = ('create', 'simulated', 'aeronautics', 'offroad')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHOP = os.path.join(ROOT, 'kubejs/data/society_trading/shops/librarian.json')
CREATE_JAR = os.path.join(ROOT, 'mods/create-1.21.1-6.0.10.jar')
AERO_JAR = os.path.join(ROOT, 'mods/create-aeronautics-bundled-1.21.1-1.3.2.jar')
VANILLA_JAR = '/var/home/Orgo/Documentos/curseforge/minecraft/Install/versions/1.21.1/1.21.1.jar'
KUBE_RECIPES = os.path.join(ROOT, 'kubejs/data')
REMOVE_JS = os.path.join(ROOT, 'kubejs/server_scripts/recipes/removeRecipes.js')
STARTUP_DIR = os.path.join(ROOT, 'kubejs/startup_scripts')

DEN = [('numismatics:ancient_coin', 262144), ('numismatics:sun', 4096), ('numismatics:crown', 512),
       ('numismatics:cog', 64), ('numismatics:sprocket', 16), ('numismatics:bevel', 8), ('numismatics:spur', 1)]

# Prices of raw materials and existing shop items (already in coin-equivalent units).
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
    'meadow:fire_log': 410,
    'minecraft:netherrack': 1, 'minecraft:string': 2, 'minecraft:paper': 2,
    'minecraft:slime_ball': 8, 'supplementaries:rope': 2, 'minecraft:white_wool': 4,
    'create:blaze_burner': 1037,
    'minecraft:obsidian': 16, 'minecraft:ender_pearl': 64, 'minecraft:blaze_rod': 64,
    'minecraft:crafting_table': 4, 'minecraft:chest': 8, 'minecraft:barrel': 7,
    'minecraft:lever': 1, 'minecraft:redstone_torch': 17, 'minecraft:observer': 40,
    'minecraft:piston': 80, 'minecraft:sticky_piston': 90, 'minecraft:hopper': 330,
    'minecraft:dispenser': 30, 'minecraft:shears': 128, 'minecraft:compass': 320,
    'minecraft:clock': 1040, 'minecraft:lightning_rod': 48, 'minecraft:bucket': 192,
    'minecraft:iron_bars': 24, 'minecraft:chain': 105, 'minecraft:rail': 25,
    'minecraft:minecart': 320, 'minecraft:smooth_stone': 2, 'minecraft:bone_meal': 2,
    'minecraft:diamond': 512, 'minecraft:netherite_ingot': 4 * 2048 + 4 * 256,
    'minecraft:netherite_upgrade_smithing_template': 49556,
    'minecraft:honeycomb': 8, 'minecraft:kelp': 4, 'minecraft:tinted_glass': 20,
    'minecraft:sculk_sensor': 64, 'minecraft:lectern': 20, 'minecraft:bell': 512,
    'minecraft:note_block': 20, 'minecraft:daylight_detector': 40, 'minecraft:comparator': 40,
    'minecraft:repeater': 40, 'minecraft:tripwire_hook': 70, 'minecraft:target': 50,
    'minecraft:sand': 1, 'minecraft:gravel': 0.5, 'minecraft:flint': 2,
    'minecraft:soul_sand': 4, 'minecraft:glass_pane': 1, 'minecraft:feather': 4,
    'create:powdered_obsidian': 22,
    'create:rose_quartz': 16,  # no recipe and no sell literal; comparable to amethyst shard (sell 8, 2x)
    'society:kinetic_blueprint': 0, 'create:cardboard': 8, 'create:cardboard_block': 8 * 4 * STEP,
    'minecraft:dried_kelp_block': 9 * 30, 'minecraft:iron_trapdoor': 4 * 64 * STEP,
    'minecraft:stone_pressure_plate': 2,
    'oreganized:silver_sheet': 128 * STEP, 'oreganized:lead_sheet': 64 * STEP,
    'oreganized:electrum_block': 9 * (256 + 128) / 2 * STEP * STEP,
}

# Nugget -> ingot and block -> ingot conversions (nugget = ingot / 9, block = ingot * 9).
NUG = {'minecraft:iron_nugget': 'minecraft:iron_ingot', 'minecraft:gold_nugget': 'minecraft:gold_ingot',
       'create:copper_nugget': 'minecraft:copper_ingot', 'create:zinc_nugget': 'create:zinc_ingot',
       'oreganized:lead_nugget': 'oreganized:lead_ingot', 'oreganized:silver_nugget': 'oreganized:silver_ingot',
       'create:brass_nugget': 'create:brass_ingot'}
BLK = {'minecraft:iron_block': 'minecraft:iron_ingot', 'minecraft:redstone_block': 'minecraft:redstone',
       'oreganized:lead_block': 'oreganized:lead_ingot', 'minecraft:copper_block': 'minecraft:copper_ingot',
       'minecraft:gold_block': 'minecraft:gold_ingot', 'create:andesite_alloy_block': 'create:andesite_alloy',
       'create:brass_block': 'create:brass_ingot'}

# Item aliases: the target item stands in for the old name.
ALIAS = {'create:sail_frame': 'create:white_sail', 'create:stressometer': 'create:speedometer',
         'create:secondary_linear_chassis': 'create:linear_chassis', 'create:repackager': 'create:packager'}

# Fallback for forge-style tags when no tag file resolves.
TAGS = {
    'forge:plates/lead': 'oreganized:lead_sheet',  # no c:plates/lead tag; Oreganized's lead sheet is the plate
    'forge:ingots/iron': 'minecraft:iron_ingot', 'forge:ingots/copper': 'minecraft:copper_ingot',
    'forge:ingots/zinc': 'create:zinc_ingot', 'forge:ingots/gold': 'minecraft:gold_ingot',
    'forge:ingots/brass': 'create:brass_ingot', 'forge:ingots/lead': 'oreganized:lead_ingot',
    'forge:ingots/silver': 'oreganized:silver_ingot', 'forge:nuggets/iron': 'minecraft:iron_nugget',
    'forge:nuggets/gold': 'minecraft:gold_nugget', 'forge:nuggets/copper': 'create:copper_nugget',
    'forge:nuggets/zinc': 'create:zinc_nugget', 'forge:nuggets/brass': 'create:brass_nugget',
    'forge:dusts/redstone': 'minecraft:redstone', 'forge:gems/diamond': 'minecraft:diamond',
    'forge:storage_blocks/iron': 'minecraft:iron_block', 'forge:storage_blocks/lead': 'oreganized:lead_block',
    'forge:storage_blocks/brass': 'create:brass_block',
    'minecraft:planks': 'minecraft:oak_planks', 'minecraft:logs': 'minecraft:oak_log',
    'forge:rods/wooden': 'minecraft:stick', 'forge:stone': 'minecraft:stone', 'forge:cobblestone': 'minecraft:cobblestone',
    'forge:glass': 'minecraft:glass', 'forge:glass_panes': 'minecraft:glass_pane',
    'forge:slimeballs': 'minecraft:slime_ball', 'forge:string': 'minecraft:string',
    'forge:obsidian': 'minecraft:obsidian', 'forge:sand': 'minecraft:sand',
    'forge:feathers': 'minecraft:feather', 'forge:rods/blaze': 'minecraft:blaze_rod',
    'society:raw_logs': 'minecraft:oak_log',  # no jar defines it; oak is the representative log
    'c:stones': 'minecraft:stone', 'c:cobblestones': 'minecraft:cobblestone', 'c:strings': 'minecraft:string',
    'c:glass_blocks': 'minecraft:glass', 'c:barrels/wooden': 'minecraft:barrel', 'forge:plates/silver': 'oreganized:silver_sheet',
    'forge:rope': 'supplementaries:rope', 'minecraft:buttons': 'minecraft:stone_pressure_plate',
    'minecraft:wool': 'minecraft:white_wool', 'forge:stripped_logs': 'minecraft:stripped_oak_log', 'forge:chests/wooden': 'minecraft:chest',
}

# Items that kubejs replaces with JS shaped recipes (removed from the recipe jars).
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

ITEM_RE = re.compile(r'"([a-z0-9_.-]+:[a-z0-9_/.-]+)"')
SELL_RE = re.compile(r'\{\s*item:\s*"([a-z0-9_.-]+:[a-z0-9_/.-]+)"\s*,\s*value:\s*(\d+(?:\.\d+)?)\s*\}')
CRAFT_TYPES = ('minecraft:crafting_shapeless',)  # every create:* processing type is accepted (see index_recipes)


# Portable engines only have a recipe for the red one; the other colours are a dye swap
# and the shop sells every colour at the same price (decision of 2026-11-22).
for _colour in ('white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray', 'light_gray',
                'cyan', 'purple', 'blue', 'brown', 'green', 'black'):
    ALIAS.setdefault(f'simulated:{_colour}_portable_engine', 'simulated:red_portable_engine')


def read_recipes_from_zip(zf, prefix, out):
    """Collect recipe JSON files under data/<ns>/recipe/ (1.21.1 singular folder)."""
    for name in zf.namelist():
        m = re.match(r'data/([a-z0-9_.-]+)/recipe/(.+)\.json$', name)
        if m:
            out.setdefault(f'{m.group(1)}:{m.group(2)}', json.loads(zf.read(name)))


def load_sources():
    recipes, tags = {}, {}
    with zipfile.ZipFile(VANILLA_JAR) as zf:
        read_recipes_from_zip(zf, '', recipes)
        load_tags(zf, tags)
    with zipfile.ZipFile(CREATE_JAR) as zf:
        read_recipes_from_zip(zf, '', recipes)
        load_tags(zf, tags)
    with zipfile.ZipFile(AERO_JAR) as outer:
        for name in outer.namelist():
            if name.startswith('META-INF/jarjar/') and name.endswith('.jar'):
                with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                    read_recipes_from_zip(inner, '', recipes)
                    load_tags(inner, tags)
    # Tags of every other mod: NeoForge common tags (c:) are provided by several mods.
    for jar in sorted(glob.glob(os.path.join(ROOT, 'mods', '*.jar'))):
        with zipfile.ZipFile(jar) as zf:
            load_tags(zf, tags)
    # kubejs overlay: same id replaces the jar recipe, except when the overlay
    # needs netherite (pricing ignores the netherite gate, see NETHERITE_SWAPS)
    for p in sorted(glob.glob(os.path.join(KUBE_RECIPES, '*/recipe/**/*.json'), recursive=True)):
        ns = os.path.relpath(p, KUBE_RECIPES).split(os.sep)[0]
        rel = os.path.relpath(p, os.path.join(KUBE_RECIPES, ns, 'recipe'))[:-5].replace(os.sep, '/')
        try:
            with open(p, encoding='utf-8') as fh:
                text = fh.read()
            rid = f'{ns}:{rel}'
            # the netherite ingot's own recipe is not a gate, only recipes that consume netherite
            if 'netherite' in text and rid in recipes and 'netherite' not in rel:
                NETHERITE_SWAPS.append(rid)
                continue
            recipes[rid] = json.loads(text)
        except (OSError, ValueError):
            pass
    # kubejs tag files
    for p in sorted(glob.glob(os.path.join(KUBE_RECIPES, '*/tags/item*/**/*.json'), recursive=True)):
        ns = os.path.relpath(p, KUBE_RECIPES).split(os.sep)[0]
        rel = re.sub(r'^.*?/tags/items?/', '', p.replace(os.sep, '/'))[:-5]
        try:
            with open(p, encoding='utf-8') as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            continue
        tags.setdefault(f'{ns}:{rel}', []).extend(v for v in data.get('values', []) if isinstance(v, str))
    return recipes, tags


def load_tags(zf, tags):
    for name in zf.namelist():
        m = re.match(r'data/([a-z0-9_.-]+)/tags/items/(.+)\.json$', name) or \
            re.match(r'data/([a-z0-9_.-]+)/tags/item/(.+)\.json$', name)
        if m:
            data = json.loads(zf.read(name))
            tags.setdefault(f'{m.group(1)}:{m.group(2)}', []).extend(
                v for v in data.get('values', []) if isinstance(v, str))


def removals():
    """Return (ids removed by output, ids removed by recipe id, inputs removed) from removeRecipes.js."""
    src = open(REMOVE_JS, encoding='utf-8').read()

    def block(name, nxt):
        start = src.index(name)
        end = src.index(nxt, start) if nxt else len(src)
        return set(ITEM_RE.findall(src[start:end]))
    return (block('removeByOutput', 'removeById'),
            block('removeById', 'removeByInput'),
            block('removeByInput', None))


def ingredient_items(x, tags):
    """Return the list of item ids an ingredient can take (alternatives)."""
    if isinstance(x, list):
        return [i for e in x for i in ingredient_items(e, tags)]
    if not isinstance(x, dict):
        return []
    if 'item' in x:
        return [x['item']]
    if 'tag' in x:
        return expand_tag(x['tag'], tags, set()) or ['#' + x['tag']]
    return []


def expand_tag(name, tags, seen):
    """Items of a tag, following nested #tag references; forge fallback names when no file resolves."""
    if name in seen:
        return []
    seen.add(name)
    found = []
    for v in tags.get(name, []):
        if v.startswith('#'):
            found += expand_tag(v[1:], tags, seen)
        else:
            found.append(v)
    if name.startswith('c:'):
        found += expand_tag('forge:' + name[2:], tags, seen)
    if name.startswith('forge:'):  # old forge tags in pack recipes resolve through their c: name
        found += expand_tag('c:' + name[6:], tags, seen)
    if name in TAGS:  # representative priced member, so the cheapest priced alternative always exists
        found.append(TAGS[name])
    return found


def unwrap(r):
    """NeoForge conditional wrappers: price the first inner recipe."""
    while isinstance(r, dict) and r.get('type') == 'neoforge:conditional':
        r = r['recipes'][0]['recipe']
    return r


def index_recipes(recipes, tags):
    out_rm, id_rm, in_rm = removals()
    by_out = {}
    for rid, r in recipes.items():
        if rid in id_rm or not isinstance(r, dict):
            continue
        try:
            r = unwrap(r)
            t = r.get('type', '')
            ings, results = [], []
            if t in ('minecraft:crafting_shaped', 'create:mechanical_crafting'):
                for row in r['pattern']:
                    for ch in row:
                        if ch != ' ':
                            ings.append(ingredient_items(r['key'][ch], tags))
            elif t == 'create:sequenced_assembly':
                # only the first result is priced, weighted by its chance share
                ings.append(ingredient_items(r['ingredient'], tags))
                trans = (r.get('transitional_item') or r.get('transitionalItem') or {}).get('id')
                for _ in range(r.get('loops', 1)):
                    for s in r['sequence']:
                        for i in s.get('ingredients', [])[1:]:
                            ings.append([x for x in ingredient_items(i, tags) if x != trans])
                tot = sum(x.get('chance', 1) for x in r['results'])
                first = r['results'][0]
                results = [(first['id'], first.get('count', 1) * first.get('chance', 1) / tot)]
            elif t == 'minecraft:stonecutting' or t.startswith(('minecraft:smelting', 'minecraft:blasting')):
                ings.append(ingredient_items(r['ingredient'], tags))
                results = [(r['result'] if isinstance(r['result'], str) else r['result']['id'], r.get('count', 1))]
            elif t == 'minecraft:smithing_transform':
                for k in ('template', 'base', 'addition'):
                    ings.append(ingredient_items(r[k], tags))
                res = r['result']
                results = [(res['id'] if isinstance(res, dict) else res, res.get('count', 1) if isinstance(res, dict) else 1)]
            elif t in CRAFT_TYPES or t.startswith('create:'):
                for i in r.get('ingredients', []):
                    if 'fluid' in i or 'fluidTag' in i or 'amount' in i:
                        continue
                    ings.append(ingredient_items(i, tags))
            else:
                continue
            if t not in ('create:sequenced_assembly', 'minecraft:stonecutting') and not t.startswith(('minecraft:smelting', 'minecraft:blasting', 'minecraft:smithing')):
                res = r.get('result', r.get('results', [None]))
                res = res[0] if isinstance(res, list) and res else res
                if isinstance(res, dict):
                    results = [(res.get('id', res.get('item')), res.get('count', 1))]
                else:
                    results = [(res, 1)]
        except (KeyError, TypeError, IndexError):
            continue
        for o, n in results:
            if not o or o in out_rm or any(i in in_rm for slot in ings for i in slot):
                continue
            by_out.setdefault(o, []).append((rid, ings, n))
    for o, (ings, n) in JS.items():
        by_out.setdefault(o, []).append(('js:' + o, [[i] for i in ings], n))
    return by_out


def load_sell():
    sell = {}
    for p in sorted(glob.glob(os.path.join(STARTUP_DIR, '*.js'))):
        for item, v in SELL_RE.findall(open(p, encoding='utf-8').read()):
            sell[item] = max(sell.get(item, 0), float(v))
    return sell


class Pricer:
    def __init__(self):
        recipes, tags = load_sources()
        self.by_out = index_recipes(recipes, tags)
        self.tags = tags
        self.sell = load_sell()
        self.memo, self.marks, self.stack = {}, {}, set()

    def cost(self, item):
        if item in self.memo:
            return self.memo[item]
        if item in BASE:
            # Coins keep their face value. Other raw inputs cost 2x their shipping-bin
            # sell value; without a sell literal the old base (blacksmith scale, iron 64
            # vs 2x sell 22) is scaled down by OLD_BASE_RATIO.
            if item.startswith('numismatics:'):
                return self._set(item, BASE[item], 'base')
            if self.sell.get(item):
                return self._set(item, 2 * self.sell[item], 'sell')
            return self._set(item, BASE[item] / OLD_BASE_RATIO, 'fallback')
        if item in ALIAS:
            v = self.cost(ALIAS[item])
            return self._set(item, v, 'alias')
        if item in NUG or item in BLK:
            v = self.cost(NUG[item]) / 9 if item in NUG else self.cost(BLK[item]) * 9
            return self._set(item, v, 'derived')
        if item in self.stack:
            return math.inf
        self.stack.add(item)
        best, how = math.inf, None
        for rid, ings, n in self.by_out.get(item, []):
            if any(item in slot for slot in ings):
                continue
            if rid.endswith('_from_conversion') or rid.endswith('_clear'):
                continue
            # alternatives inside one ingredient slot are priced as the cheapest one
            total = 0.0
            for slot in ings:  # an empty slot is a step with no added item (e.g. pressing)
                total += min((self.cost(a) for a in slot), default=0.0)
            value = total / n * STEP
            if value < best:
                best, how = value, ('js' if rid.startswith('js:') else 'recipe')
        self.stack.discard(item)
        sell = self.sell.get(item)
        if sell:
            floor = 2 * sell
            if best == math.inf:
                return self._set(item, floor, 'sell')
            if floor > best:
                return self._set(item, floor, 'floor')
        if best == math.inf:
            self.marks[item] = 'unresolved'
            self.memo[item] = math.inf  # memoized: without it the recursion explodes
            return math.inf
        return self._set(item, best, how)

    def _set(self, item, value, mark):
        self.memo[item] = value
        self.marks.setdefault(item, mark)
        return value


def coins(p):
    for name, d in DEN:
        n = round(p / d)
        if 1 <= n <= 64 and abs(n * d - p) / p <= 0.15:
            return name, n, n * d
    for name, d in reversed(DEN):
        n = round(p / d)
        if n <= 64:
            return name, max(n, 1), max(n, 1) * d
    name, d = DEN[0]
    n = max(1, round(p / d))
    return name, n, n * d


def in_scope(trade):
    return trade['offer']['id'].split(':')[0] in NAMESPACES


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', help='write the JSON report here')
    ap.add_argument('--write', action='store_true', help='rewrite request and numismatics_cost in --shop')
    ap.add_argument('--shop', default=SHOP)
    args = ap.parse_args()

    with open(args.shop, encoding='utf-8') as fh:
        raw = fh.read()
    shop = json.loads(raw)
    pricer = Pricer()
    # An item reached inside a recipe cycle is memoized as unresolved even when another
    # recipe prices it later; drop those entries and price again until nothing changes.
    offers = [t['offer']['id'] for t in shop['trades'] if in_scope(t) and t['offer']['id'] not in GATES]
    for _ in range(5):
        for offer in offers:
            pricer.cost(offer)
        stale = [k for k, v in pricer.memo.items() if v == math.inf]
        if not stale:
            break
        before = sum(1 for o in offers if pricer.memo.get(o) == math.inf)
        for k in stale:
            del pricer.memo[k]
            pricer.marks.pop(k, None)
        for offer in offers:
            pricer.cost(offer)
        if sum(1 for o in offers if pricer.memo.get(o) == math.inf) == before:
            break
    report, mark_count, unresolved = [], {}, set()
    for t in shop['trades']:
        if not in_scope(t):
            continue
        offer = t['offer']['id']
        if offer in GATES:  # gate: fixed price, not derived from the recipe
            unit = GATES[offer] / t['offer']['count']
            pricer.marks[offer] = 'gate'
        else:
            unit = pricer.cost(offer)
        if unit == math.inf:
            unresolved.add(offer)
            report.append({'trade_id': t.get('trade_id'), 'offer': offer, 'price': None})
            continue
        price = unit * t['offer']['count']
        name, n, total = coins(price)
        mark = pricer.marks.get(offer, '?')
        mark_count[mark] = mark_count.get(mark, 0) + 1
        report.append({'trade_id': t.get('trade_id'), 'offer': offer, 'count': t['offer']['count'],
                       'price': round(price, 1), 'mark': mark,
                       'request': {'id': name, 'count': n}, 'numismatics_cost': total})
        t['request'] = {'id': name, 'count': n}
        t['numismatics_cost'] = total
        print(f'{offer:45s} x{t["offer"]["count"]:<3d} {price:12.1f} -> {n:3d} {name.split(":")[1]:9s} ({total}) [{mark}]')

    print('marks:', dict(sorted(mark_count.items())))
    print('unresolved:', sorted(unresolved))
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as fh:
            json.dump(sorted(report, key=lambda r: (r['offer'], r['trade_id'] or 0)), fh, indent=2,
                      ensure_ascii=False)
            fh.write('\n')
    if args.write:
        with open(args.shop, 'w', encoding='utf-8') as fh:
            fh.write(json.dumps(shop, indent=2, ensure_ascii=False) + '\n')
        print('shop rewritten:', args.shop)


if __name__ == '__main__':
    main()
