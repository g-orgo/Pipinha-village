"""Quest lang: drop keys of removed objects, replace the old pack name. Usage: lang.py <lang_dir> [--write]"""
import json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(HERE + '/removed.json'))
hexes = {i.lstrip('0') for i in r['objects'] if re.fullmatch(r'[0-9A-F]{1,16}', i)}
def signed(h):
    v = int(h, 16); return v - (1 << 64) if v >= 1 << 63 else v
decs = {str(signed(i)) for i in r['objects'] if re.fullmatch(r'[0-9A-F]{1,16}', i)}
NAME = [("in the Sunlit Valley", "in Pipinha's Village"), ("on Sunlit Valley", "in Pipinha's Village"),
        ("Society: Sunlit Valley", "Pipinha's Village"), ("Sunlit Valley", "Pipinha's Village"),
        ("阳光谷", "Pipinha's Village"),
        ("Requires Create or Botania", "Requires Create"), ("Nécessite Create ou Botania", "Nécessite Create"),
        ("크리에이트 또는 보타니아 진행 필요", "크리에이트 진행 필요"), ("需要机械动力或植物魔法", "需要机械动力")]
KEY = re.compile(r'^\s*"(ftbquests\.[^"]+)"\s*:')
def gone(k):
    if k in r['keys']: return True
    p = k.split('.')
    if p[1] == 'chapter' and p[2] in r['chapters']: return True
    for x in p:
        if x.startswith('quest') and x[5:] in hexes: return True
    for a, b in zip(p, p[1:]):
        if a in ('task', 'reward', 'loot_table', 'chapter_groups') and b in decs: return True
    return False
stats = collections.Counter()
for fn in sorted(os.listdir(sys.argv[1])):
    path = os.path.join(sys.argv[1], fn); lines = open(path, encoding='utf-8').read().split('\n')
    out = []
    for ln in lines:
        m = KEY.match(ln)
        if m and gone(m.group(1)): stats[fn + ' removed'] += 1; continue
        if m:
            new = ln
            for a, b in NAME: new = new.replace(a, b)
            if new != ln: stats[fn + ' renamed'] += 1
            ln = new
        out.append(ln)
    last = max(i for i, l in enumerate(out) if KEY.match(l) or l.strip().startswith('"'))
    out[last] = out[last].rstrip().rstrip(',')
    text = '\n'.join(out); json.loads(text)  # must stay valid JSON
    if '--write' in sys.argv: open(path, 'w', encoding='utf-8').write(text)
for k, v in sorted(stats.items()): print(v, k)
