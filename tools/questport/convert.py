"""Item stack conversion: 1.20.1 FTB Quests NBT -> 1.21.1 ids and data components."""
import json, os, pickle, collections, sys
from snbt import Raw

HERE = os.path.dirname(os.path.abspath(__file__))
K, _ = pickle.load(open(HERE + '/known.pkl', 'rb'))
ROOT = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Pipinha's Village"
sys.path.insert(0, ROOT + '/tools/dataport')
from fix_shops import VILLAGER_ICON_CMD  # face number per villager type (models/item/villager.json)
RENAME = json.load(open(ROOT + '/tools/kjsport/idscan_renames.json'))
RENAME.update({  # each target checked in the 1.21.1 jars (lang/model) on 2026-11-13
    'bakery:bakery_standard': 'bakery:bakery_banner',
    'candlelight:candlelight_standard': 'candlelight:candlelight_banner',
    'crabbersdelight:frog_leg_kebob': 'crabbersdelight:frog_leg_kebab',
    'crabbersdelight:squid_kebob': 'crabbersdelight:squid_kebab',
    'meadow:fire_log': 'meadow:firewood',
    'toms_storage:ts.crafting_terminal': 'toms_storage:crafting_terminal',
    'toms_storage:ts.inventory_connector': 'toms_storage:inventory_connector',
    'trials:ominous_bottle': 'minecraft:ominous_bottle',
    'trials:trial_key_ominous': 'minecraft:ominous_trial_key',
    'supplementaries:sign_post_oak': 'supplementaries:way_sign_oak',
})
STRUCT_RENAME = {'trials:trials_chambers': 'minecraft:trial_chambers'}
TAG_RENAME = {'forge:eggs': 'c:eggs', 'forge:crops': 'c:crops'}
REMOVED_NS = {'splendid_slimes', 'create_slime'}  # botania and botania_seeds restored (2026-11-13)
QUALITY = {1: 'iron', 2: 'gold', 3: 'diamond'}
LOG = collections.defaultdict(collections.Counter)  # what -> Counter(detail)


def item_id(i):
    """Renamed id, or None when the item is gone (removed mod or no 1.21.1 registration)."""
    i = RENAME.get(str(i), str(i))
    if i.split(':')[0] == 'botania_seeds': return i  # no 1.21.1 port yet: KubeJS recreates these ids
    if i.split(':')[0] in REMOVED_NS:
        LOG['removed (owner decision)'][i] += 1; return None
    if i not in K['item']:
        LOG['missing in 1.21.1'][i] += 1; return None
    return i


def as_int(v): return int(str(v).rstrip('bsLlBS'))


def filter_of(st):
    """itemfilters stack -> FTB Filter System expression (or None when nothing is left)."""
    tag = st.get('tag', {})
    if st['id'] == 'itemfilters:tag':
        t = TAG_RENAME.get(tag['value'], tag['value'])
        return [f'item_tag({t})']
    parts = []
    for x in tag.get('items', []):
        i = item_id(x['id'] if isinstance(x, dict) else x)
        if i and f'item({i})' not in parts: parts.append(f'item({i})')
    return parts


def components(st, role):
    """Map the old tag to 1.21.1 components. role: icon | task | reward."""
    tag, iid, out, custom = st.get('tag', {}), str(st['id']), {}, {}
    for k, v in tag.items():
        if k == 'Damage':
            if as_int(v) and role == 'reward': out['minecraft:damage'] = Raw(str(as_int(v)))
        elif k == 'display':
            if 'Name' in v: out['minecraft:custom_name'] = v['Name']
            if 'Lore' in v: out['minecraft:lore'] = list(v['Lore'])
        elif k == 'BlockEntityTag' and iid.startswith('trofers:'):
            out['trofers:trophy'] = v['Trophy']
        elif k == 'patchouli:book': out['patchouli:book'] = v
        elif k == 'variant' and iid.startswith('longwings:'): out['longwings:variant'] = v
        elif k == 'quality_food':
            lv = as_int(v['quality'])
            out['quality_food:quality'] = {'type': 'quality_food:' + QUALITY[lv], 'level': Raw(str(lv))}
        elif k == 'type' and iid == 'society:villager':
            # 1.20.1 {type:{id:"society:X"}} -> custom_data {type:"X"} plus the face number,
            # same shape as the shop icons (tools/dataport/fix_shops.py).
            t = str(v['id'] if isinstance(v, dict) else v).split(':')[-1]
            custom['type'] = t
            if t in VILLAGER_ICON_CMD: out['minecraft:custom_model_data'] = Raw(str(VILLAGER_ICON_CMD[t]))
            else: LOG['villager type without face'][t] += 1
        elif k == 'type' and iid == 'society:invitation':
            # npcInvite.js reads getString("type"): keep "society:X" as a plain string.
            custom['type'] = str(v['id'] if isinstance(v, dict) else v)
        elif k == 'StoredEnchantments':
            out['minecraft:stored_enchantments'] = {'levels': {e['id']: Raw(str(as_int(e['lvl']))) for e in v}}
        elif k == 'Potion': out['minecraft:potion_contents'] = {'potion': v}
        elif iid.startswith('portable_blueprints:'): custom[k] = v
        else: LOG['nbt dropped (' + role + ')'][f'{iid} {k}'] += 1
    if custom: out['minecraft:custom_data'] = custom
    if role == 'icon':  # icons keep only what changes the look
        keep = ('trofers:trophy', 'longwings:variant', 'patchouli:book', 'minecraft:potion_contents',
                'minecraft:custom_data', 'minecraft:custom_model_data', 'minecraft:stored_enchantments')
        out = {k: v for k, v in out.items() if k in keep and not (k == 'minecraft:custom_data' and 'type' not in v)}
    return out


def stack(st, role, match=False):
    """Return the 1.21.1 stack (string or compound) or None when it must go."""
    if isinstance(st, str):
        return item_id(st)
    iid = str(st['id'])
    if iid.startswith('itemfilters:'):
        parts = filter_of(st)
        if not parts: return None
        if len(parts) == 1 and parts[0].startswith('item('): return parts[0][5:-1]
        expr = parts[0] if len(parts) == 1 else 'or(' + ''.join(parts) + ')'
        return {'id': 'ftbfiltersystem:smart_filter', 'count': Raw('1'),
                'components': {'ftbfiltersystem:filter': expr}}
    i = item_id(iid)
    if not i: return None
    st = dict(st, id=i)
    comp = components(st, role) if (role != 'task' or match) else {}
    for k in st.get('tag', {}):
        if role == 'task' and not match: LOG['nbt ignored (task without match_nbt)'][f'{i} {k}'] += 1
    count = as_int(st.get('Count', st.get('count', 1)))
    if not comp and count == 1: return i
    out = {'id': i, 'count': Raw(str(count))}
    if comp: out['components'] = comp
    return out
