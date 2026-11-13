"""F6: port config/ftbquests from the 1.20.1 instance (read only) into a staging folder.
Usage: python3 -I port.py <out_quests_dir>"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snbt, convert
from snbt import Raw
from convert import stack, LOG, K

SRC = "/var/home/Orgo/Documentos/curseforge/minecraft/Instances/Society: Sunlit Valley/config/ftbquests/quests"
OUT = sys.argv[1]
DROP_CHAPTERS = {'botania', 'slimes'}  # owner decision 2026-11-12
# Quests kept alive only by checkmark/stat tasks whose whole text is about Splendid Slimes or Botania.
TEXT_REMOVE_QUESTS = {'6EBAA004C1A50E98', '747B28CA5F55AFA7', '07A551F04BB9A117', '1030BCF34FEAE03C', '668AEE0B5CD49EE4'}
# Description lines (lang key suffixes) that only talk about Splendid Slimes, in quests that stay.
DESC_DROP = {'3225DF52212FAF3E': ['description2'], '66C03C4DA3F21900': ['description1', 'description2']}
CHAPTER_SUBTITLE_DROP = {'abandoned_farm'}  # "Reward: Botania Unlocked"
removed = {'chapters': set(DROP_CHAPTERS), 'quests': {}, 'objects': set(), 'keys': []}


def fix_icon(o):
    if 'icon' in o:
        new = stack(o['icon'], 'icon')
        if new is None: del o['icon']
        else: o['icon'] = new


def port_task(t):
    fix_icon(t)
    ty = t.get('type')
    if ty == 'item':
        match = t.pop('match_nbt', None) == 'true'
        t.pop('weak_nbt_match', None)
        new = stack(t['item'], 'task', match)
        if new is None: return None
        t['item'] = new
        t['match_components'] = 'fuzzy' if isinstance(new, dict) and new['id'] != 'ftbfiltersystem:smart_filter' else 'none'
    elif ty == 'observation' and t.get('observe_type') == '5':
        if str(t['to_observe']).split(':')[0] in convert.REMOVED_NS or t['to_observe'] not in K['entity']:
            LOG['task removed'][t['to_observe']] += 1; return None
    elif ty == 'structure':
        t['structure'] = convert.STRUCT_RENAME.get(t['structure'], t['structure'])
    elif ty == 'questsadditions:break':  # Quests Additions has no 1.21.1 port
        block = t.pop('block')
        for k in ('block_type', 'checkItem', 'value'): t.pop(k, None)
        t.update(type='gamestage', stage='quest_broke_' + block.split(':')[1])
        t.setdefault('icon', block)
    return t


def port_reward(r):
    fix_icon(r)
    if 'table_id' in r and int(str(r['table_id']).rstrip('L')) in EMPTY_TABLES: return None
    if r.get('type') == 'item' or ('type' not in r and 'item' in r):  # reward table entries have no type
        new = stack(r['item'], 'reward')
        if new is None: return None
        r['item'] = new
    return r


def port_list(owner, key, fn):
    if key not in owner: return
    keep = []
    for x in owner[key]:
        y = fn(x)
        if y is not None: keep.append(y)
        elif x.get('id'): removed['objects'].add(x['id'])
    owner[key] = keep


def port_chapter(ch):
    fix_icon(ch)
    quests = []
    for q in ch.get('quests', []):
        fix_icon(q)
        had = bool(q.get('tasks'))
        port_list(q, 'tasks', port_task)
        port_list(q, 'rewards', port_reward)
        for suf in DESC_DROP.get(q['id'], []):
            lines = q.get('description', [])
            for i, l in enumerate(lines):
                if l.endswith('.' + suf + '}'):
                    del lines[i:i + (2 if i + 1 < len(lines) and lines[i + 1] == '' else 1)]
                    removed['keys'].append(l.strip('{}')); break
            if lines and lines[-1] == '': lines.pop()
        if q['id'] in TEXT_REMOVE_QUESTS or (had and not q['tasks']):
            removed['quests'][q['id']] = q.get('dependencies', []); removed['objects'].add(q['id'])
            for r in q.get('rewards', []): removed['objects'].add(r['id'])
            continue
        if 'min_required_tasks' in q and int(q['min_required_tasks']) > len(q['tasks']):
            q['min_required_tasks'] = Raw(str(len(q['tasks'])))
        quests.append(q)
    ch['quests'] = quests


def resolve(dep, seen=()):
    if dep not in removed['quests']: return [dep]
    out = []
    for d in removed['quests'][dep]:
        if d not in seen: out += resolve(d, seen + (dep,))
    return out


EMPTY_TABLES = set()
tables = {}
for f in sorted(glob.glob(SRC + '/reward_tables/*.snbt')):
    rt = snbt.loads(open(f, encoding='utf-8').read())
    fix_icon(rt)
    port_list(rt, 'rewards', port_reward)
    if not rt['rewards']:  # every entry belonged to a removed mod: drop the table and rewards using it
        EMPTY_TABLES.add(int(rt['id'], 16)); removed['objects'].add(rt['id']); continue
    tables[os.path.basename(f)] = rt


chapters = {}
for f in sorted(glob.glob(SRC + '/chapters/*.snbt')):
    name = os.path.basename(f)[:-5]
    ch = snbt.loads(open(f, encoding='utf-8').read())
    if name in DROP_CHAPTERS:
        removed['objects'].add(ch['id'])
        for q in ch.get('quests', []): removed['quests'][q['id']] = []; removed['objects'].add(q['id'])
        continue
    port_chapter(ch); chapters[name] = ch
    if name in CHAPTER_SUBTITLE_DROP:
        removed['keys'] += [x.strip('{}') for x in ch.pop('subtitle', [])]
gone_chapter_quests = {q for q, deps in removed['quests'].items() if deps == []}
for ch in chapters.values():  # rewire dependencies around removed quests
    for q in ch['quests']:
        if 'dependencies' in q:
            new = []
            for d in q['dependencies']:
                for x in resolve(d):
                    if x not in new: new.append(x)
            q['dependencies'] = new
            if 'min_required_dependencies' in q and int(q['min_required_dependencies']) > len(new):
                q['min_required_dependencies'] = Raw(str(len(new)))
    ch['quest_links'] = [l for l in ch.get('quest_links', []) if l.get('linked_quest') not in removed['quests']]
    ch['images'] = [i for i in ch.get('images', []) if not i.get('click') or str(i['click']).lstrip('#') not in removed['objects']]

os.makedirs(OUT + '/chapters', exist_ok=True); os.makedirs(OUT + '/reward_tables', exist_ok=True)
for name, ch in chapters.items():
    open(f'{OUT}/chapters/{name}.snbt', 'w', encoding='utf-8').write(snbt.dumps(ch) + '\n')
for name, rt in tables.items():
    open(f'{OUT}/reward_tables/{name}', 'w', encoding='utf-8').write(snbt.dumps(rt) + '\n')
data = snbt.loads(open(SRC + '/data.snbt', encoding='utf-8').read())
fix_icon(data)
data['title'] = "&l&6Pipinha's Village"
open(OUT + '/data.snbt', 'w', encoding='utf-8').write(snbt.dumps(data) + '\n')
open(OUT + '/chapter_groups.snbt', 'w', encoding='utf-8').write(open(SRC + '/chapter_groups.snbt', encoding='utf-8').read())
json.dump({'keys': removed['keys'], 'chapters': sorted(removed['chapters']), 'objects': sorted(removed['objects']),
           'quests_rewired': {k: v for k, v in removed['quests'].items() if k not in gone_chapter_quests}},
          open(os.path.dirname(os.path.abspath(__file__)) + '/removed.json', 'w'), indent=1)
for what, c in LOG.items():
    print(f'## {what}: {sum(c.values())}')
    for k, n in c.most_common(): print(f'  {n}x {k}')
