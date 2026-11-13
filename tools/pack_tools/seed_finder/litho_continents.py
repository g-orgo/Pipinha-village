"""Evaluates Lithosphere's overworld continentalness (router 'continents') for a seed, without the game.
Port of 1.20.1 Xoroshiro / ImprovedNoise / PerlinNoise / NormalNoise and the density-function types used.
Usage as module: Continents(seed, datadir).at(blockX, blockZ) -> continentalness (ocean < -0.19).
"""
import hashlib, json, math, os, re

M = (1 << 64) - 1
def s64(v): v &= M; return v - (1 << 64) if v >> 63 else v
def rotl(v, n): return ((v << n) | (v >> (64 - n))) & M
def mix13(z):
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return z ^ (z >> 31)

class Xoro:
    def __init__(self, lo, hi):
        self.lo, self.hi = lo & M, hi & M
        if self.lo == 0 and self.hi == 0: self.lo, self.hi = 0x9E3779B97F4A7C15, 0x6A09E667F3BCC909
    @staticmethod
    def from_seed(seed):
        lo = (seed ^ 0x6A09E667F3BCC909) & M
        return Xoro(mix13(lo), mix13((lo + 0x9E3779B97F4A7C15) & M))
    def next_long(self):
        l, m = self.lo, self.hi
        n = (rotl((l + m) & M, 17) + l) & M
        m ^= l
        self.lo = rotl(l, 49) ^ m ^ ((m << 21) & M)
        self.hi = rotl(m, 28)
        return n
    def next_double(self): return (self.next_long() >> 11) * 1.1102230246251565E-16
    def next_int(self, bound):
        l = self.next_long() & 0xFFFFFFFF
        m = l * bound; n = m & 0xFFFFFFFF
        if n < bound:
            i = ((1 << 32) - bound) % bound
            while n < i:
                l = self.next_long() & 0xFFFFFFFF; m = l * bound; n = m & 0xFFFFFFFF
        return m >> 32
    def fork_positional(self): return Positional(self.next_long(), self.next_long())

class Positional:
    def __init__(self, lo, hi): self.lo, self.hi = lo, hi
    def from_hash(self, s):
        b = hashlib.md5(s.encode()).digest()
        return Xoro(int.from_bytes(b[:8], 'big') ^ self.lo, int.from_bytes(b[8:], 'big') ^ self.hi)

G = [(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(1,0,1),(-1,0,1),(1,0,-1),(-1,0,-1),(0,1,1),(0,-1,1),(0,1,-1),(0,-1,-1),(1,1,0),(0,-1,1),(-1,1,0),(0,-1,-1)]
def gd(h, x, y, z): g = G[h & 15]; return g[0]*x + g[1]*y + g[2]*z
def sm(t): return t*t*t*(t*(t*6-15)+10)
def lerp(t, a, b): return a + t*(b-a)

class Improved:
    def __init__(self, r):
        self.xo, self.yo, self.zo = r.next_double()*256, r.next_double()*256, r.next_double()*256
        p = list(range(256))
        for i in range(256):
            j = r.next_int(256 - i); p[i], p[i+j] = p[i+j], p[i]
        self.p = p
    def noise(self, x, y, z):
        d, e, f = x + self.xo, y + self.yo, z + self.zo
        i, j, k = math.floor(d), math.floor(e), math.floor(f)
        d -= i; e -= j; f -= k
        P = self.p
        def h(v): return P[v & 255]
        l = h(i); m = h(i+1); n = h(l+j); o = h(l+j+1); q1 = h(m+j); q = h(m+j+1)
        a = gd(h(n+k), d, e, f); b = gd(h(q1+k), d-1, e, f); c = gd(h(o+k), d, e-1, f); dd = gd(h(q+k), d-1, e-1, f)
        u = gd(h(n+k+1), d, e, f-1); v = gd(h(q1+k+1), d-1, e, f-1); w = gd(h(o+k+1), d, e-1, f-1); xx = gd(h(q+k+1), d-1, e-1, f-1)
        tx, ty, tz = sm(d), sm(e), sm(f)
        return lerp(tz, lerp(ty, lerp(tx, a, b), lerp(tx, c, dd)), lerp(ty, lerp(tx, u, v), lerp(tx, w, xx)))

def wrap(d): return d - math.floor(d / 3.3554432E7 + 0.5) * 3.3554432E7

class Perlin:
    def __init__(self, r, first, amps):
        pos = r.fork_positional()
        self.levels = [Improved(pos.from_hash('octave_%d' % (first + i))) if a != 0 else None for i, a in enumerate(amps)]
        self.amps = amps
        self.inf = 2.0 ** first
        n = len(amps)
        self.vf = 2.0 ** (n - 1) / (2.0 ** n - 1)
    def value(self, x, y, z):
        d = 0.0; e = self.inf; f = self.vf
        for lv, a in zip(self.levels, self.amps):
            if lv: d += a * lv.noise(wrap(x*e), wrap(y*e), wrap(z*e)) * f
            e *= 2.0; f /= 2.0
        return d

class Normal:
    def __init__(self, r, first, amps):
        self.a = Perlin(r, first, amps); self.b = Perlin(r, first, amps)
        nz = [i for i, a in enumerate(amps) if a != 0]
        n = nz[-1] - nz[0]
        self.vf = 0.16666666666666666 / (0.1 * (1.0 + 1.0 / (n + 1)))
    def value(self, x, y, z):
        k = 1.0181268882175227
        return (self.a.value(x, y, z) + self.b.value(x*k, y*k, z*k)) * self.vf

def load_json(p): return json.loads(re.sub(r'//[^\n]*', '', open(p).read()))

def clamped_map(v, a, b, c, d):
    t = min(max((v - a) / (b - a), 0.0), 1.0)
    return c + t * (d - c)

class Continents:
    def __init__(self, seed, datadir, root='minecraft:overworld/continents'):
        self.dd = datadir
        self.pos = Xoro.from_seed(seed).fork_positional()
        self.noises = {}; self.dfs = {}
        self.root = self.df(root)
    def noise(self, key):
        if key not in self.noises:
            ns, p = key.split(':'); j = load_json(os.path.join(self.dd, ns, 'worldgen/noise', p + '.json'))
            self.noises[key] = Normal(self.pos.from_hash(key), j['firstOctave'], j['amplitudes'])
        return self.noises[key]
    def df(self, ref):
        if ref not in self.dfs:
            ns, p = ref.split(':'); self.dfs[ref] = load_json(os.path.join(self.dd, ns, 'worldgen/density_function', p + '.json'))
        return self.dfs[ref]
    def ev(self, n, x, z, y=0.0):
        if isinstance(n, (int, float)): return float(n)
        if isinstance(n, str): return self.ev(self.df(n), x, z, y)
        t = n['type'].replace('minecraft:', '')
        if t == 'flat_cache': return self.ev(n['argument'], x - x % 4, z - z % 4, 0.0)
        if t in ('cache_2d', 'cache_once', 'interpolated', 'cache_all_in_cell'): return self.ev(n['argument'], x, z, y)
        if t in ('add', 'mul', 'min', 'max'):
            a = self.ev(n['argument1'], x, z, y); b = self.ev(n['argument2'], x, z, y)
            return a + b if t == 'add' else a * b if t == 'mul' else min(a, b) if t == 'min' else max(a, b)
        if t == 'abs': return abs(self.ev(n['argument'], x, z, y))
        if t == 'square': v = self.ev(n['argument'], x, z, y); return v * v
        if t == 'cube': v = self.ev(n['argument'], x, z, y); return v * v * v
        if t == 'clamp': return min(max(self.ev(n['input'], x, z, y), n['min']), n['max'])
        if t == 'y_clamped_gradient': return clamped_map(y, n['from_y'], n['to_y'], n['from_value'], n['to_value'])
        if t == 'noise':
            return self.noise(n['noise']).value(x * n['xz_scale'], y * n['y_scale'], z * n['xz_scale'])
        if t == 'shifted_noise':
            sx = self.ev(n['shift_x'], x, z, y); sy = self.ev(n['shift_y'], x, z, y); sz = self.ev(n['shift_z'], x, z, y)
            return self.noise(n['noise']).value(x * n['xz_scale'] + sx, y * n['y_scale'] + sy, z * n['xz_scale'] + sz)
        if t == 'shift_a': return self.noise(n['argument']).value(x * 0.25, 0.0, z * 0.25) * 4.0
        if t == 'shift_b': return self.noise(n['argument']).value(z * 0.25, x * 0.25, 0.0) * 4.0
        if t == 'shift': return self.noise(n['argument']).value(x * 0.25, y * 0.25, z * 0.25) * 4.0
        if t == 'spline': return self.spline(n['spline'], x, z, y)
        raise ValueError('unsupported density function ' + t)
    def spline(self, s, x, z, y=0.0):
        if isinstance(s, (int, float)): return float(s)
        c = self.ev(s['coordinate'], x, z, y)
        pts = s['points']; locs = [p['location'] for p in pts]
        i = -1
        for k, l in enumerate(locs):
            if l <= c: i = k
            else: break
        last = len(pts) - 1
        if i < 0: return self.spline(pts[0]['value'], x, z, y) + pts[0]['derivative'] * (c - locs[0])
        if i == last: return self.spline(pts[last]['value'], x, z, y) + pts[last]['derivative'] * (c - locs[last])
        l0, l1 = locs[i], locs[i+1]; t = (c - l0) / (l1 - l0)
        v0 = self.spline(pts[i]['value'], x, z, y); v1 = self.spline(pts[i+1]['value'], x, z, y)
        d0, d1 = pts[i]['derivative'], pts[i+1]['derivative']
        f8 = d0 * (l1 - l0) - (v1 - v0); f9 = -d1 * (l1 - l0) + (v1 - v0)
        return lerp(t, v0, v1) + t * (1 - t) * lerp(t, f8, f9)
    def at(self, bx, bz):
        return self.ev(self.root, float(bx), float(bz))

    def surface(self, bx, bz, lo=-64, hi=512):
        """Highest y where depth > 0 (terrain approximation, no 3D noise): bisection on the depth function."""
        f = lambda yy: self.ev(self.root, float(bx), float(bz), float(yy))
        if f(hi) > 0: return hi
        if f(lo) <= 0: return lo
        while hi - lo > 1:
            m = (lo + hi) // 2
            if f(m) > 0: lo = m
            else: hi = m
        return lo
