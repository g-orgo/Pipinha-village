"""Leitura e escrita das partes do datapack final (depois do finalize.py, tudo em sunlit:).

Uma parte e uma grade slices[y][z][x] de chars; cada char vem da paleta da parte
(refpalette) ou, se nao estiver la, da paleta do style (sunlit:common). Paletas sao
compartilhadas entre partes: mudar uma posicao nunca edita uma entrada existente, sempre
aloca (ou reaproveita) um char com o estado novo.
"""
import glob, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'moonlight-global-datapacks', 'sunlit_towns')
LC = os.path.join(OUT, 'data', 'sunlit', 'lostcities')

# chars livres para estados novos: ASCII, Latin-1, grego e cirilico (o Lost Cities le um char Java)
POOL = [chr(c) for c in list(range(33, 127)) + list(range(161, 256)) + list(range(0x391, 0x3CA)) + list(range(0x410, 0x450))
        if chr(c) not in '"\\']
AIR = 'minecraft:air'


def rl_path(kind, rl):
    return os.path.join(LC, kind, *rl.split(':', 1)[1].split('/')) + '.json'


class Palette:
    def __init__(self, rl, entries, path, new=False):
        self.rl, self.entries, self.path, self.new = rl, entries, path, new
        self.by = {e['char']: e for e in entries if 'char' in e}
        self.dirty = new
        self.cache = {}

    def alloc(self, entry, taken):
        key = json.dumps(entry, sort_keys=True)
        if key in self.cache:
            return self.cache[key]
        for e in self.entries:
            if {k: v for k, v in e.items() if k != 'char'} == entry:
                self.cache[key] = e['char']
                return e['char']
        c = next((ch for ch in POOL if ch not in self.by and ch not in taken), None)
        if c is None:
            raise SystemExit(f'paleta {self.rl} sem chars livres')
        e = dict(entry, char=c)
        self.entries.append(e)
        self.by[c] = e
        self.cache[key] = c
        self.dirty = True
        return c


class Store:
    def __init__(self):
        self.pals = {}
        self.common = self.palette('sunlit:common')
        self.parts = {}
        for p in sorted(glob.glob(os.path.join(LC, 'parts', '**', '*.json'), recursive=True)):
            rel = os.path.relpath(p, os.path.join(LC, 'parts'))[:-5].replace(os.sep, '/')
            self.parts['sunlit:' + rel] = (p, json.load(open(p, encoding='utf-8')))
        # chars usados em alguma parte que dependem do common: nunca reusar esses numa paleta
        self.common_chars = set(self.common.by)

    def palette(self, rl):
        if rl not in self.pals:
            path = rl_path('palettes', rl)
            d = json.load(open(path, encoding='utf-8'))
            self.pals[rl] = Palette(rl, d['palette'], path)
        return self.pals[rl]

    def part_palette(self, name, part):
        rl = part.get('refpalette')
        if rl:
            return self.palette(rl)
        # parte sem paleta propria (ruas): cria uma so dela, usada apenas quando precisar de char novo
        rl = 'sunlit:polish/' + name.split(':', 1)[1].replace('/', '_')
        if rl not in self.pals:
            self.pals[rl] = Palette(rl, [], rl_path('palettes', rl), new=True)
        return self.pals[rl]

    def save(self):
        n = 0
        for pal in self.pals.values():
            if pal.dirty and pal.entries:
                os.makedirs(os.path.dirname(pal.path), exist_ok=True)
                json.dump({'palette': pal.entries}, open(pal.path, 'w', encoding='utf-8'))
                n += 1
        return n


class Grid:
    """slices[y][z][x] editavel com resolucao de estados."""

    def __init__(self, store, name, part):
        self.store, self.name, self.part = store, name, part
        self.pal = store.part_palette(name, part)
        self.s = [[list(r) for r in sl] for sl in part['slices']]
        self.H, self.Z, self.X = len(self.s), part['zsize'], part['xsize']
        self.changed = False

    def inside(self, y, z, x):
        return 0 <= y < self.H and 0 <= z < self.Z and 0 <= x < self.X

    def entry(self, y, z, x):
        if not self.inside(y, z, x):
            return None
        c = self.s[y][z][x]
        e = self.pal.by.get(c) or self.store.common.by.get(c)
        if e is None and c == ' ':
            return {'block': AIR}
        return e

    def opts(self, y, z, x):
        """estados possiveis da celula ([] = fora da parte; ['?'] = variante/desconhecido)"""
        e = self.entry(y, z, x)
        if e is None:
            return [] if not self.inside(y, z, x) else ['?']
        if 'block' in e:
            return [e['block']]
        if e.get('blocks'):
            return [b['block'] for b in e['blocks']]
        return ['?']

    def b(self, y, z, x):
        o = self.opts(y, z, x)
        return o[0] if o else None

    def put(self, y, z, x, block, loot=None):
        entry = {'block': block}
        if loot:
            entry['loot'] = loot
        self.put_entry(y, z, x, entry)

    def air_char(self):
        e = self.pal.by.get(' ') or self.store.common.by.get(' ')
        if e is None or (set(e) == {'char', 'block'} and block_is_air(e['block'])):
            return ' '
        return None

    def put_entry(self, y, z, x, entry):
        c = None
        if set(entry) == {'block'} and block_is_air(entry['block']):
            c = self.air_char()
        if c is None:
            c = self.pal.alloc(entry, self.store.common_chars)
        if self.pal.new and not self.part.get('refpalette'):
            self.part['refpalette'] = self.pal.rl
        if self.s[y][z][x] != c:
            self.s[y][z][x] = c
            self.changed = True

    def copy_cell(self, src, dst):
        """move o conteudo (char) de uma celula para outra"""
        (y0, z0, x0), (y1, z1, x1) = src, dst
        if self.s[y1][z1][x1] != self.s[y0][z0][x0]:
            self.s[y1][z1][x1] = self.s[y0][z0][x0]
            self.changed = True

    def clear(self, y, z, x):
        self.put(y, z, x, AIR)

    def commit(self):
        if self.changed:
            self.part['slices'] = [[''.join(r) for r in sl] for sl in self.s]
        return self.changed


def block_is_air(s):
    return s.split('[')[0] in ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air')
