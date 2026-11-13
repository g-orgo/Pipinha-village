"""Ultima etapa antes do validate.py: o datapack sai com um namespace so (sunlit).
Move data/<origem>/ para data/sunlit/ e reescreve as referencias "<origem>:" nos JSON.
Para nao haver colisao de nomes, aborta se o arquivo ja existir no destino."""
import os, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'moonlight-global-datapacks', 'sunlit_towns')
SRC_NS = 'deceased' + 'craft'  # namespace das pecas importadas
src = os.path.join(OUT, 'data', SRC_NS)
dst = os.path.join(OUT, 'data', 'sunlit')

moved = 0
if os.path.isdir(src):
    for root, _, files in os.walk(src):
        for f in files:
            a = os.path.join(root, f)
            b = os.path.join(dst, os.path.relpath(a, src))
            if os.path.exists(b):
                raise SystemExit(f'colisao ao unificar namespace: {b}')
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.move(a, b)
            moved += 1
    shutil.rmtree(src)

fixed = 0
for root, _, files in os.walk(OUT):
    for f in files:
        if not f.endswith(('.json', '.mcfunction', '.mcmeta')):
            continue
        p = os.path.join(root, f)
        t = open(p, encoding='utf-8').read()
        if SRC_NS in t:
            open(p, 'w', encoding='utf-8').write(t.replace(SRC_NS + ':', 'sunlit:').replace(SRC_NS, 'sunlit'))
            fixed += 1
print(f'namespace unificado: {moved} arquivos movidos, {fixed} reescritos')


# --- Lista "blocks" com "random": o Lost Cities preenche 128 posicoes com os pesos
# e aborta o chunk ("Not enough blocks in the random list (factor should go up to 128)")
# se a soma ficar abaixo de 128. Escala proporcionalmente.
import glob, json, math, re, hashlib, zipfile

LC = os.path.join(OUT, 'data', 'sunlit', 'lostcities')
scaled = 0
for p in glob.glob(os.path.join(LC, 'palettes', '**', '*.json'), recursive=True):
    d = json.load(open(p, encoding='utf-8'))
    hit = False
    for e in d.get('palette', []):
        bl = e.get('blocks')
        if not bl:
            continue
        tot = sum(b.get('random', 0) for b in bl)
        if tot < 128:
            k = math.ceil(128 / max(tot, 1))
            for b in bl:
                b['random'] = max(b.get('random', 0), 1) * k if tot else k
            hit = True
            scaled += 1
    if hit:
        json.dump(d, open(p, 'w', encoding='utf-8'))
print(f'listas random escaladas para >=128: {scaled}')

# --- Partes do proprio Lost Cities que a cidade ainda usa (rodovia em curva/T, pontes,
# escadas) leem os chars da paleta do style (sunlit:common). Completa com o que falta
# a partir de default/common do Lost Cities (ex.: 'w' de highway_bridge_bend).
jar = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(OUT)), 'mods', 'lostcities-*.jar')))[-1]
z = zipfile.ZipFile(jar)
cp = os.path.join(LC, 'palettes', 'common.json')
common = json.load(open(cp, encoding='utf-8'))
have = {e['char'] for e in common['palette']}
added = []
for name in ('default', 'common'):
    for e in json.loads(z.read(f'data/lostcities/lostcities/palettes/{name}.json'))['palette']:
        if e['char'] not in have:
            common['palette'].append(e)
            have.add(e['char'])
            added.append(e['char'])
json.dump(common, open(cp, 'w', encoding='utf-8'))
print(f'chars do Lost Cities adicionados em sunlit:common: {"".join(added) or "nenhum"}')

# --- Sem terracota nas cidades (2026-10-09, dono): os chars herdados do Lost Cities
# (ex. 'R' cyan_terracotta, '9' com terracotas) viram concreto da mesma cor.
import re as _re
_fixed = 0
for _e in common['palette']:
    def _fix(s):
        global _fixed
        m = _re.match(r'^minecraft:([a-z_]+)_terracotta$', s.split('[')[0])
        if m and m.group(1) in ('white', 'light_gray', 'gray', 'black', 'brown', 'red', 'orange',
                                'yellow', 'lime', 'green', 'cyan', 'light_blue', 'blue', 'purple',
                                'magenta', 'pink'):
            _fixed += 1
            return f'minecraft:{m.group(1)}_concrete'
        m = _re.match(r'^minecraft:(?:[a-z]+_)?glazed_terracotta$', s.split('[')[0])
        if m:
            _fixed += 1
            return 'minecraft:white_concrete'
        return s
    if 'block' in _e:
        _e['block'] = _fix(_e['block'])
    for _b in _e.get('blocks', []):
        _b['block'] = _fix(_b['block'])
json.dump(common, open(cp, 'w', encoding='utf-8'))
print(f'terracota do common virada em concreto: {_fixed}')

# --- Caminhos curtos: o Windows (Explorer) nao extrai zip com caminho > 260 chars.
# palettes/multi_x_10/multi_x_10part2_floor20_palette.json -> palettes/x_10/part2_floor20.json
KINDS = ('palettes', 'parts', 'buildings', 'multibuildings')
MAXSEG = 24


def cut(s):
    return s if len(s) <= MAXSEG else s[:MAXSEG - 7] + '_' + hashlib.md5(s.encode()).hexdigest()[:6]


def short(path):
    segs = path.split('/')
    f = segs[-1]
    if len(segs) > 1:
        for pre in (segs[-2], re.sub(r'^(building|multi)_', '', segs[-2])):
            if f.startswith(pre) and f != pre + '_main':
                f = f[len(pre):].lstrip('_')
                break
    f = re.sub(r'_?palette$', '', f) or 'main'
    dirs = [cut(re.sub(r'^(building|multi)_', '', d)) for d in segs[:-1]]
    return '/'.join(dirs + [cut(f)])


other = set()  # resource locations de outros tipos (loot, scattered...) que nao podem ser tocados
for root, _, files in os.walk(os.path.join(OUT, 'data', 'sunlit')):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), os.path.join(OUT, 'data', 'sunlit')).split(os.sep)
        if rel[0] == 'lostcities' and rel[1] in KINDS:
            continue
        start = 2 if rel[0] == 'lostcities' else 1
        other.add('sunlit:' + '/'.join(rel[start:]).rsplit('.', 1)[0])

ren, moves, stale = {}, [], []
for k in KINDS:
    seen = {}
    for p in sorted(glob.glob(os.path.join(LC, k, '**', '*.json'), recursive=True), key=lambda q: short(
            os.path.relpath(q, os.path.join(LC, k))[:-5].replace(os.sep, '/')) == os.path.relpath(
            q, os.path.join(LC, k))[:-5].replace(os.sep, '/'), reverse=True):
        old = os.path.relpath(p, os.path.join(LC, k))[:-5].replace(os.sep, '/')
        new = short(old)
        if new in seen and seen[new] != old:
            # convert skipped (pack not wiped): an earlier finalize already left a copy at the short path.
            # Already-short paths are listed first, so `old` is the long one; the newer file wins.
            if seen[new] != new:
                raise SystemExit(f'colisao ao encurtar {k}: {old} / {seen[new]} -> {new}')
            sp = os.path.join(LC, k, *new.split('/')) + '.json'
            if k == 'palettes':
                # The short copy may hold chars a later step (polish) allocated for parts that persist across
                # rebuilds; the fresh long copy lacks them. Merge: long entries win, short-only chars are kept.
                a, b = json.load(open(p, encoding='utf-8')), json.load(open(sp, encoding='utf-8'))
                have = {e.get('char') for e in a['palette']}
                a['palette'] += [e for e in b['palette'] if e.get('char') not in have]
                json.dump(a, open(p, 'w', encoding='utf-8'))
            elif os.path.getmtime(p) < os.path.getmtime(sp):
                stale.append(p)
                ren['sunlit:' + old] = 'sunlit:' + new
                continue
        seen[new] = old
        if new != old:
            if 'sunlit:' + old in other or 'sunlit:' + old in ren:
                raise SystemExit(f'nome ambiguo entre tipos: sunlit:{old}')
            ren['sunlit:' + old] = 'sunlit:' + new
            moves.append((p, os.path.join(LC, k, *new.split('/')) + '.json'))
for p in stale:
    os.remove(p)
for a, b in moves:
    os.makedirs(os.path.dirname(b), exist_ok=True)
    os.rename(a, b)
for root, dirs, files in os.walk(LC, topdown=False):
    if not os.listdir(root):
        os.rmdir(root)
rx = re.compile(r'"(sunlit:[^"]+)"')
rew = 0
for root, _, files in os.walk(OUT):
    for f in files:
        if not f.endswith('.json'):
            continue
        p = os.path.join(root, f)
        t = open(p, encoding='utf-8').read()
        n = rx.sub(lambda m: '"' + ren.get(m.group(1), m.group(1)) + '"', t)
        if n != t:
            open(p, 'w', encoding='utf-8').write(n)
            rew += 1
longest = max((len(os.path.relpath(os.path.join(r, f), os.path.dirname(os.path.dirname(OUT))))
               for r, _, fs in os.walk(OUT) for f in fs), default=0)
print(f'nomes encurtados: {len(ren)} ({rew} arquivos reescritos), maior caminho na instancia: {longest}')
