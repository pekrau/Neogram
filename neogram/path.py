"SVG path synthesizer."

from utils import N


class Path:
    "SVG path synthesizer."

    def __init__(self, x, y):
        "Moveto x, y. Absolute coordinates."
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        self.parts = []
        self.M(x, y)

    def __str__(self):
        return " ".join(self.parts)

    def M(self, x, y):
        "Moveto, then lineto any v's. Absolute coordinates."
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("M", x, y, concatenate=False)

    def m(self, x, y):
        "Moveto, then lineto any v's. Relative coordinates."
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("m", x, y, concatenate=False)

    def L(self, x, y):
        "Lineto. Absolute coordinates."
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("L", x, y)

    def l(self, x, y):
        "Lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("l", x, y)

    def H(self, x):
        "Horizontal lineto. Absolute coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"H {N(x)}")
        return self

    def h(self, x):
        "Horizontal lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        self.parts.append(f"h {N(x)}")
        return self

    def V(self, y):
        "Vertical lineto. Absolute coordinates."
        assert isinstance(y, (int, float))
        self.parts.append(f"V {N(y)}")
        return self

    def v(self, y):
        "Vertical lineto. Relative coordinates."
        assert isinstance(y, (int, float))
        self.parts.append(f"v {N(y)}")
        return self

    def C(self, x1, y1, x2, y2, x, y):
        "Cubic Beziér curveto. Absolute coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        assert isinstance(x2, (int, float))
        assert isinstance(y2, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("C", x1, y1, x2, y2, x, y)

    def c(self, x1, y1, x2, y2, x, y):
        "Cubic Beziér curveto. Relative coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        assert isinstance(x2, (int, float))
        assert isinstance(y2, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("c", x1, y1, x2, y2, x, y)

    def S(self, x2, y2, x, y):
        "Shorthand cubic Beziér curveto. Absolute coordinates."
        assert isinstance(x2, (int, float))
        assert isinstance(y2, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("S", x2, y2, x, y)

    def s(self, x2, y2, x, y):
        "Shorthand cubic Beziér curveto. Relative coordinates."
        assert isinstance(x2, (int, float))
        assert isinstance(y2, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("s", x2, y2, x, y)

    def Q(self, x1, y1, x, y):
        "Quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("Q", x1, y1, x, y)

    def q(self, x1, y1, x, y):
        "Quadratic Beziér curveto. Relative coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        return self.append("q", x1, y1, x, y)

    def T(self, x1, y1):
        "Shorthand quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        return self.append("T", x1, y1)

    def t(self, x1, y1):
        "Shorthand quadratic Beziér curveto. Relative coordinates."
        assert isinstance(x1, (int, float))
        assert isinstance(y1, (int, float))
        return self.append("t", x1, y1)

    def A(self, xr, yr, xrot, laf, sf, x, y):
        "Elliptical arc. Absolute coordinates."
        assert isinstance(xr, (int, float))
        assert isinstance(yr, (int, float))
        assert isinstance(xrot, (int, float))
        assert isinstance(laf, int)
        assert isinstance(sf, int)
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        self.parts.append(f"A {N(xr)} {N(yr)} {N(xrot)} {N(laf)} {N(sf)} {N(x)} {N(y)}")
        return self

    def a(self, xr, yr, xrot, laf, sf, x, y):
        "Elliptical arc. Relative coordinates."
        assert isinstance(xr, (int, float))
        assert isinstance(yr, (int, float))
        assert isinstance(xrot, (int, float))
        assert isinstance(laf, int)
        assert isinstance(sf, int)
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        self.parts.append(f"a {N(xr)} {N(yr)} {N(xrot)} {N(laf)} {N(sf)} {N(x)} {N(y)}")
        return self

    def Z(self):
        "Close path."
        self.parts.append("Z")
        return self

    def append(self, command, *v, concatenate=True):
        bits = []
        if not (concatenate and self.parts[-1][0] == command):
            bits.append(command)
        bits.append(" ".join([f"{N(w)}" for w in v]))
        self.parts.append(" ".join(bits))
        return self
