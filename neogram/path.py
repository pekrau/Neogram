"Neogram: SVG path synthesizer."

__all__ = ["Path", "Vector2"]

from utils import N
from vector2 import Vector2


class Path:
    "SVG path synthesizer."

    def __init__(self, v0, *v):
        "Moveto v0, then lineto any v's. Absolute coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self.parts = []
        self.M(v0, *v)

    def __str__(self):
        return " ".join(self.parts)

    def M(self, v0, *v):
        "Moveto, then lineto any v's. Absolute coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("M", v0, *v, concatenate=False)

    def m(self, v0, *v):
        "Moveto, then lineto any v's. Relative coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("m", v0, *v, concatenate=False)

    def L(self, v0, *v):
        "Lineto. Absolute coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("L", v0, *v)

    def l(self, v0, *v):
        "Lineto. Relative coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("l", v0, *v)

    def H(self, x):
        "Horizontal lineto. Absolute coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"H {x:.5g}")
        return self

    def h(self, x):
        "Horizontal lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"h {x:.5g}")
        return self

    def V(self, x):
        "Vertical lineto. Absolute coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"V {x:.5g}")
        return self

    def v(self, x):
        "Vertical lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"v {x:.5g}")
        return self

    def C(self, v1, v2, v):
        "Cubic Beziér curveto. Absolute coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        return self.append("C", v1, v2, v)

    def c(self, v1, v2, v):
        "Cubic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        return self.append("c", v1, v2, v)

    def S(self, v2, v):
        "Shorthand cubic Beziér curveto. Absolute coordinates."
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        return self.append("S", v2, v)

    def s(self, v2, v):
        "Shorthand cubic Beziér curveto. Relative coordinates."
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        return self.append("s", v2, v)

    def Q(self, v1, v):
        "Quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v, Vector2)
        return self.append("Q", v1, v)

    def q(self, v1, *v):
        "Quadratic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v, Vector2)
        return self.append("q", v1, v)

    def T(self, v1, *v):
        "Shorthand quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(v1, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("T", v1, v)

    def t(self, v1, *v):
        "Shorthand quadratic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        return self.append("t", v1, v)

    def A(self, xr, yr, xrot, laf, sf, v):
        "Elliptical arc. Absolute coordinates."
        assert isinstance(xr, (int, float))
        assert isinstance(yr, (int, float))
        assert isinstance(xrot, (int, float))
        assert isinstance(laf, int)
        assert isinstance(sf, int)
        assert isinstance(v, Vector2)
        self.parts.append(
            f"A {N(xr)} {N(yr)} {N(xrot)} {N(laf)} {N(sf)} {N(v.x)} {N(v.y)}"
        )
        return self

    def a(self, rx, ry, xrot, laf, sf, v):
        "Elliptical arc. Relative coordinates."
        assert isinstance(xr, (int, float))
        assert isinstance(yr, (int, float))
        assert isinstance(xrot, (int, float))
        assert isinstance(laf, int)
        assert isinstance(sf, int)
        assert isinstance(v, Vector2)
        self.parts.append(
            f"a {N(xr)} {N(yr)} {N(xrot)} {N(laf)} {N(sf)} {N(v.x)} {N(v.y)}"
        )
        return self

    def Z(self):
        "Close path."
        self.parts.append("Z")
        return self

    def append(self, command, *v, concatenate=True):
        bits = []
        if not (concatenate and self.parts[-1][0] == command):
            bits.append(command)
        bits.append(" ".join([f"{N(w.x)} {N(w.y)}" for w in v]))
        self.parts.append(" ".join(bits))
        return self
