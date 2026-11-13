import sys
ROOT = sys.argv[1]
rows = {}   # old -> (new, kind, ren, sets)
order = []
def put(old, new, kind, ren='', sets=''):
    if old not in rows:
        order.append(old)
    rows[old] = (new, kind, ren, sets)
def split_props(new):
    base, _, brk = new.partition('[')
    props = brk.rstrip(']').replace(',', ';')
    return base, props
# block rows
blk = [l.rstrip('\n').split('\t') for l in open(ROOT + '/tools/lcport/block_map.tsv', encoding='utf-8') if l.strip()]
blk = [r for r in blk if r[0] != 'old_id']
for old, new, _rule in blk:
    base, props = split_props(new)
    ren = 'upholstery>fabric' if base.startswith('redecorate:') else ''
    kind = 'block' if base == 'minecraft:air' else 'any'
    put(old, new, kind, ren, '')
# loot rows (items only, do not override block rows)
for l in open(ROOT + '/tools/lcport/loot_map.tsv', encoding='utf-8'):
    cols = l.rstrip('\n').split('\t')
    if len(cols) < 2 or cols[0] == 'old_id':
        continue
    if cols[0] not in rows and not cols[0].startswith('dew_drop_farmland_growth:'):
        put(cols[0], cols[1], 'item')
# explicit rows
put('meadow:fire_log', 'meadow:firewood', 'any')
colors = [o[len('redeco:'):-len('_pet_bed')] for o in rows if o.startswith('redeco:') and o.endswith('_pet_bed')]
for c in sorted(colors):
    put(f'redeco:{c}_upholstery', f'redecorate:{c}_fabric', 'item', 'upholstery>fabric')
    # redeco block names as item rows following the block row's new id, no props
    if f'redeco:{c}_pet_bed' in rows:
        pass
put('redeco:crate_block_entity', 'refurbished_furniture:crate', 'be')
put('redeco:pedestal_block_entity', 'supplementaries:pedestal', 'be')
for old in ('minecraft:grass', 'society:earth_crystal', 'society:geode_node', 'society:skull_cavern'):
    put(old, '', 'ignore')
# rows that need a block and a be entry for the same old id, or that the
# dict above cannot express (round 2 and round 3 additions), written verbatim
EXTRA = [
    ('supplementaries:sign_post', 'supplementaries:way_sign', 'block', '', ''),
    ('supplementaries:sign_post', 'supplementaries:way_sign', 'be', '', ''),
    ('quark:lootr_nether_brick_trapped_chest', 'minecraft:trapped_chest', 'any', '', ''),
    ('quark:lootr_nether_brick_trapped_chest', 'minecraft:trapped_chest', 'be', '', ''),
    ('toms_storage:ts.inventory_hopper_basic', 'toms_storage:basic_inventory_hopper', 'any', '', ''),
    ('toms_storage:ts.inventory_hopper_basic', 'toms_storage:basic_inventory_hopper', 'be', '', ''),
    # Sunrise Gardening (successor of Sturdy Farmland): every old dew_drop_farmland_growth id exists under sunrisegardening.
    # Blockstate props compared with the source: farmland keeps 'moisture' and sprinklers keep 'sticklogged', so no prop renames.
    # kind 'any' keeps block, item and block entity data (sprinkler and pot BEs are not dropped).
    ('dew_drop_farmland_growth:weak_fertilized_farmland', 'sunrisegardening:weak_fertilized_farmland', 'any', '', ''),
    ('dew_drop_farmland_growth:low_quality_fertilized_farmland', 'sunrisegardening:low_quality_fertilized_farmland', 'any', '', ''),
    ('dew_drop_farmland_growth:iron_sprinkler', 'sunrisegardening:iron_sprinkler', 'any', '', ''),
    ('dew_drop_farmland_growth:gold_sprinkler', 'sunrisegardening:gold_sprinkler', 'any', '', ''),
    # Sunrise Gardening fertilizer items (old dew_drop fertilizers were loot rows pointing to bone meal)
    ('dew_drop_farmland_growth:bountiful_fertilizer', 'sunrisegardening:bountiful_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:deluxe_hydrating_fertilizer', 'sunrisegardening:deluxe_hydrating_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:high_quality_fertilizer', 'sunrisegardening:high_quality_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:hydrating_fertilizer', 'sunrisegardening:hydrating_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:hyper_fertilizer', 'sunrisegardening:hyper_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:low_quality_fertilizer', 'sunrisegardening:low_quality_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:strong_fertilizer', 'sunrisegardening:strong_fertilizer', 'item', '', ''),
    ('dew_drop_farmland_growth:weak_fertilizer', 'sunrisegardening:weak_fertilizer', 'item', '', ''),
    # trials mod content that became vanilla in 1.21 (sounds and enchantments are not block/item rows, so they are not listed)
    ('trials:tuff_slab', 'minecraft:tuff_slab', 'any', '', ''),
    ('trials:tuff_stairs', 'minecraft:tuff_stairs', 'any', '', ''),
    ('trials:tuff_bricks', 'minecraft:tuff_bricks', 'any', '', ''),
    ('trials:tuff_brick_stairs', 'minecraft:tuff_brick_stairs', 'any', '', ''),
    ('trials:tuff_brick_slab', 'minecraft:tuff_brick_slab', 'any', '', ''),
    ('trials:chiseled_tuff', 'minecraft:chiseled_tuff', 'any', '', ''),
    ('trials:chiseled_tuff_bricks', 'minecraft:chiseled_tuff_bricks', 'any', '', ''),
    ('trials:polished_tuff', 'minecraft:polished_tuff', 'any', '', ''),
    ('trials:polished_tuff_slab', 'minecraft:polished_tuff_slab', 'any', '', ''),
    ('trials:polished_tuff_stairs', 'minecraft:polished_tuff_stairs', 'any', '', ''),
    ('trials:copper_bulb', 'minecraft:copper_bulb', 'any', '', ''),
    ('trials:crafter', 'minecraft:crafter', 'any', '', ''),
    ('trials:trial_spawner', 'minecraft:trial_spawner', 'any', '', ''),
    ('trials:trial_vault', 'minecraft:vault', 'any', '', ''),
    ('trials:trial_vault_ominous', 'minecraft:vault', 'any', '', ''),
    ('trials:waxed_copper_door', 'minecraft:waxed_copper_door', 'any', '', ''),
    ('trials:waxed_copper_trapdoor', 'minecraft:waxed_copper_trapdoor', 'any', '', ''),
    ('trials:waxed_copper_trapdoor_oxidized', 'minecraft:waxed_oxidized_copper_trapdoor', 'any', '', ''),
    ('trials:waxed_copper_grate_oxidized', 'minecraft:waxed_oxidized_copper_grate', 'any', '', ''),
    ('trials:waxed_chiseled_copper', 'minecraft:waxed_chiseled_copper', 'any', '', ''),
    ('trials:waxed_chiseled_copper_exposed', 'minecraft:waxed_exposed_chiseled_copper', 'any', '', ''),
    ('trials:waxed_chiseled_copper_weathered', 'minecraft:waxed_weathered_chiseled_copper', 'any', '', ''),
    ('trials:waxed_chiseled_copper_oxidized', 'minecraft:waxed_oxidized_chiseled_copper', 'any', '', ''),
    ('trials:chiseled_copper', 'minecraft:chiseled_copper', 'any', '', ''),
    ('trials:chiseled_copper_exposed', 'minecraft:exposed_chiseled_copper', 'any', '', ''),
    ('trials:chiseled_copper_weathered', 'minecraft:weathered_chiseled_copper', 'any', '', ''),
    ('trials:chiseled_copper_oxidized', 'minecraft:oxidized_chiseled_copper', 'any', '', ''),
    ('trials:scrape_pottery_sherd', 'minecraft:scrape_pottery_sherd', 'item', '', ''),
    ('trials:guster_pottery_sherd', 'minecraft:guster_pottery_sherd', 'item', '', ''),
    ('trials:flow_pottery_sherd', 'minecraft:flow_pottery_sherd', 'item', '', ''),
]
with open(ROOT + '/tools/saveport/id_map.tsv', 'w', encoding='utf-8') as f:
    f.write('old_id\tnew_id\tkind\tprop_renames\tprop_set\n')

    for old in order:
        new, kind, ren, sets = rows[old]
        if kind in ('block', 'any'):
            base, props = split_props(new)
            new_out = base
            sets = props
        else:
            new_out = new
        f.write(f'{old}\t{new_out}\t{kind}\t{ren}\t{sets}\n')
    for old, new, kind, ren, sets in EXTRA:
        f.write(f'{old}\t{new}\t{kind}\t{ren}\t{sets}\n')
print('rows', len(order), 'extra', len(EXTRA), 'colors', len(colors))
