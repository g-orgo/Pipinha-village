"""Final 1.21.1 formatting for FTB quest chapters: item stacks become inline {count, id} maps.
Usage: python3 -I finalize.py <in.snbt> <out.snbt>
Porter output keeps bare item strings; the current 1.21.1 chapters store every stack as a map."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snbt
from snbt import Raw

KEY = re.compile(r'[A-Za-z0-9_\-.+]+')


def inline(v):
    """One-line SNBT, same spacing as the 1.21.1 chapters: { a: 1, b: "x" }."""
    if isinstance(v, Raw): return str(v)
    if isinstance(v, str): return snbt.q(v)
    if isinstance(v, dict):
        if not v: return '{ }'
        return '{ ' + ', '.join((k if KEY.fullmatch(k) else snbt.q(k)) + ': ' + inline(v[k]) for k in sorted(v)) + ' }'
    if isinstance(v, list): return '[' + ', '.join(inline(x) for x in v) + ']'
    return snbt.dumps(v)


def stacks(o):
    """Rewrite every 'item' value (task or reward) as an inline stack map."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'item' and isinstance(v, str): o[k] = Raw(inline({'count': Raw('1'), 'id': v}))
            elif k == 'item' and isinstance(v, dict): o[k] = Raw(inline(v))
            else: stacks(v)
    elif isinstance(o, list):
        for x in o: stacks(x)
    return o


def render(text):
    return snbt.dumps(stacks(snbt.loads(text))) + '\n'


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, 'w', encoding='utf-8').write(render(open(src, encoding='utf-8').read()))
