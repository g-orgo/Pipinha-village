"""Minimal FTB-style SNBT parser/writer (newline separated, tabs)."""
import re

class Raw(str):
    """Unquoted token (numbers with suffix, booleans, bare words)."""

class Arr(list):
    """Typed array like [I; 1, 2]."""
    def __init__(self, kind, items):
        super().__init__(items); self.kind = kind

_WS = re.compile(r'[\s,]*')
_BARE = re.compile(r'[A-Za-z0-9_\-.+:]+')
_KEY = re.compile(r'[A-Za-z0-9_\-.+]+')

class Parser:
    def __init__(self, s): self.s, self.i = s, 0
    def ws(self): self.i = _WS.match(self.s, self.i).end()
    def peek(self): self.ws(); return self.s[self.i] if self.i < len(self.s) else ''
    def string(self):
        q = self.s[self.i]; self.i += 1; out = []
        while True:
            c = self.s[self.i]
            if c == '\\':
                n = self.s[self.i + 1]
                out.append({'n': '\n', 't': '\t'}.get(n, n)); self.i += 2
            elif c == q: self.i += 1; return ''.join(out)
            else: out.append(c); self.i += 1
    def key(self):
        if self.peek() in '"\'': return self.string()
        m = _KEY.match(self.s, self.i); self.i = m.end(); return m.group()
    def value(self):
        c = self.peek()
        if c == '{':
            self.i += 1; d = {}
            while self.peek() != '}':
                k = self.key(); self.ws(); assert self.s[self.i] == ':', (self.i, self.s[self.i-40:self.i+40]); self.i += 1
                d[k] = self.value()
            self.i += 1; return d
        if c == '[':
            self.i += 1; m = re.match(r'\s*([BIL]);', self.s[self.i:])
            kind = None
            if m: kind = m.group(1); self.i += m.end()
            items = []
            while self.peek() != ']': items.append(self.value())
            self.i += 1; return Arr(kind, items) if kind else items
        if c in '"\'': return self.string()
        m = _BARE.match(self.s, self.i); self.i = m.end(); return Raw(m.group())

def loads(s):
    p = Parser(s); v = p.value(); return v

def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'

def dumps(v, ind=0):
    t = '\t'
    if isinstance(v, Raw): return str(v)
    if isinstance(v, str): return q(v)
    if isinstance(v, dict):
        if not v: return '{ }'
        lines = []
        for k in sorted(v):
            kk = k if re.fullmatch(r'[A-Za-z0-9_\-.+]+', k) else q(k)
            lines.append(t * (ind + 1) + kk + ': ' + dumps(v[k], ind + 1))
        return '{\n' + '\n'.join(lines) + '\n' + t * ind + '}'
    if isinstance(v, Arr):
        return '[' + v.kind + '; ' + ', '.join(dumps(x) for x in v) + ']'
    if isinstance(v, list):
        if not v: return '[ ]'
        if len(v) == 1 and isinstance(v[0], dict):
            return '[' + dumps(v[0], ind) + ']'
        if all(not isinstance(x, (dict, list)) for x in v) and sum(len(dumps(x)) for x in v) < 80:
            return '[' + ', '.join(dumps(x) for x in v) + ']'
        return '[\n' + '\n'.join(t * (ind + 1) + dumps(x, ind + 1) for x in v) + '\n' + t * ind + ']'
    raise TypeError(type(v))
