"""Tiny pure Python stand-in for the few numpy calls preview.py uses (no numpy on this machine)."""


class A(list):
    """Vector or matrix as nested lists, with @, +, -, * and [:3] slicing that keep the type."""

    def __matmul__(self, o):
        if isinstance(o[0], list):
            return A(A(sum(self[i][k] * o[k][j] for k in range(len(o))) for j in range(len(o[0]))) for i in range(len(self)))
        return A(sum(r[k] * o[k] for k in range(len(o))) for r in self)

    def __add__(self, o):
        return A(a + b for a, b in zip(self, o))

    def __sub__(self, o):
        return A(a - b for a, b in zip(self, o))

    def __mul__(self, o):
        if isinstance(o, (int, float)):
            return A(a * o for a in self)
        return A(a * b for a, b in zip(self, o))

    __rmul__ = __mul__

    def __getitem__(self, k):
        r = list.__getitem__(self, k)
        return A(r) if isinstance(k, slice) else r


def array(x, dtype=None):
    return A(A(r) if isinstance(r, (list, tuple)) else float(r) for r in x)


def eye(n):
    return A(A(1.0 if i == j else 0.0 for j in range(n)) for i in range(n))


def diag(v):
    return A(A(float(v[i]) if i == j else 0.0 for j in range(len(v))) for i in range(len(v)))


def append(v, x):
    return A(list(v) + [x])


def set_block(m, rows, cols, block):
    for i in range(rows):
        for j in range(cols):
            m[i][j] = block[i][j]


def set_col(m, col, vals):
    for i, v in enumerate(vals):
        m[i][col] = v
