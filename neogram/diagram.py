"Neogram. Core classes; Diagram, Style, Path."

from icecream import ic

import copy
import io
import pathlib

import cairosvg
import yaml

import constants
from color import Color, Palette
from degrees import Degrees
from minixml import Element
from vector2 import Vector2


__all__ = [
    "Diagram",
    "Style",
    "Degrees",
    "Element",
    "Vector2",
    "Color",
    "Palette",
    "Path",
    "N",
    "write",
    "read",
    "parse",
    "add_diagram",
]

_diagram_lookup = {}


def add_diagram(cls):
    "Add the diagram class to the parse lookup table."
    assert issubclass(cls, Diagram)
    _diagram_lookup[cls.__name__.casefold()] = cls.parse


def get_parse_function(name):
    "Get the parse function for the diagram."
    try:
        return _diagram_lookup[name]
    except KeyError:
        raise ValueError(f"no parse function for item '{key}' in YAML data")


def write(diagram, outfile):
    "Write the YAML of the diagram into the open file object."
    assert isinstance(diagram, Diagram)
    yaml.safe_dump(diagram.as_dict(), outfile)


def read(filepath_or_stream):
    """Read and parse the file given by its path, or an open file object.
    Returns a Diagram instance.
    """
    if isinstance(filepath_or_stream, (str, pathlib.Path)):
        with open(filepath_or_stream) as infile:
            data = yaml.safe_load(infile)
    else:
        data = yaml.safe_load(filepath_or_stream)
    if len(data) != 1:
        raise ValueError("YAML file must contain exactly one top-level diagram.")
    return parse(*data.popitem())


def parse(key, data):
    return _diagram_lookup[key](data)


class Style:
    "Container of style specifications."

    def __init__(self, **styles):
        self.style = {}
        for key, value in styles.items():
            self[key] = value

    def __len__(self):
        return len(self.style)

    def __getitem__(self, key):
        return self.style[key]

    def __setitem__(self, key, value):
        self.style[key.replace("_", "-")] = value

    def __str__(self):
        "Return the values as a string appropriate for the 'style' attribute."
        parts = []
        for key, value in self.style.items():
            if isinstance(value, float):
                parts.append(f"{key}: {N(value)};")
            else:
                parts.append(f"{key}: {value};")
        return " ".join(parts)

    def set(self, key, value):
        if key == "palette" and isinstance(value, (tuple, list)):
            self.style["palette"] = Palette(*value)
        else:
            self.style[key] = copy.deepcopy(value)

    def update(self, other):
        if isinstance(other, dict):
            for key, value in other.items():
                self.set(key, value)
        elif isinstance(other, Style):
            self.update(other.style)
        else:
            raise ValueError("invalid value for Style update")

    def setattrs(self, elem, *attrnames):
        "Set the attributes given by the names, if existing, in the element."
        for attrname in attrnames:
            try:
                elem[attrname] = self.style[attrname]
            except KeyError:
                pass

    def as_dict(self):
        "Return as a dictionary of basic YAML values."
        data = {}
        for key, value in self.style.items():
            if isinstance(value, Color):
                data[key] = str(value)
            elif isinstance(value, Palette):
                data[key] = [str(c) for c in value.colors]
            elif isinstance(value, float):
                result[key] = N(value)
            else:
                data[key] = value
        return {"style": data}


class Diagram:
    "Abstract diagram."

    DEFAULT_STYLE = Style(
        stroke=Color("black"),
        fill=Color("white"),
        palette=Palette("red", "green", "blue"),
    )

    def __init__(self, id=None, klass=None, style=None):
        assert id is None or isinstance(id, str)
        assert klass is None or isinstance(klass, str)
        assert style is None or isinstance(style, Style)
        self.id = id
        self.klass = klass
        self.style = copy.deepcopy(self.DEFAULT_STYLE)
        if style is not None:
            self.style.update(style)

    @property
    def extent(self):
        "Extent of this diagram."
        return Vector2(0, 0)

    def svg(self):
        "Return the SVG root element with content in minixml representation."
        origin = Vector2(0, 0) - (extent := self.extent) / 2
        result = Element(
            "svg",
            xmlns=constants.SVG_XMLNS,
            width=N(extent.x),
            height=N(extent.y),
            viewBox=f"{N(origin.x)} {N(origin.y)} {N(extent.x)} {N(extent.y)}",
        )
        result += self.svg_content()
        return result

    def svg_content(self):
        "Return the SVG content element in minixml representation."
        result = Element("g")
        if self.id:
            result["id"] = self.id
        if self.klass:
            result["class"] = self.klass
        return result

    def write(self, filepath_or_stream):
        "Write the this diagram as SVG root to a new file or the open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg()))
        else:
            filepath_or_stream.write(repr(self.svg()))

    def write_content(self, filepath_or_stream):
        "Write the the SVG content of this diagram to a new file or the open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg_content()))
        else:
            filepath_or_stream.write(repr(self.svg_content()))

    def write_png(self, filepath_or_stream, scale=1.0):
        "Write this diagram as a PNG image to a new file or the open stream."
        assert scale > 0.0
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "wb") as outfile:
                inputfile = io.StringIO(repr(self.svg()))
                outfile.write(cairosvg.svg2png(file_obj=inputfile, scale=scale))
        else:
            inputfile = io.StringIO(repr(self.svg()))
            filepath_or_stream.write(cairosvg.svg2png(file_obj=inputfile, scale=scale))

    def as_dict(self):
        "Return as a dictionary of basic YAML values."
        return {self.__class__.__name__.casefold(): self.as_dict_content()}

    def as_dict_content(self):
        "Return the content as a dictionary of basic YAML values."
        data = {}
        if self.id:
            data["id"] = self.id
        if self.klass:
            data["class"] = self.klass
        if self.style:
            data.update(self.style.as_dict())
        return data

    @classmethod
    def parse(cls, data):
        "Parse the data into an Diagram subclass instance."
        try:
            data["klass"] = data.pop("class")
        except KeyError:
            pass
        if style := data.pop("style"):
            data["style"] = Style(**style)
        return cls(**data)


PRECISION = 0.0005


def N(x):
    "Return a compact representation of the numerical value."
    assert isinstance(x, (int, float))
    if (x < 0.0 and -x % 1.0 < PRECISION) or x % 1.0 < PRECISION:
        return f"{round(x):d}"
    else:
        return f"{x:.3f}"


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
        self._add("M", v0, *v, concatenate=False)
        return self

    def m(self, v0, *v):
        "Moveto, then lineto any v's. Relative coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self._add("m", v0, *v, concatenate=False)
        return self

    def L(self, v0, *v):
        "Lineto. Absolute coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self._add("L", v0, *v)
        return self

    def l(self, v0, *v):
        "Lineto. Relative coordinates."
        assert isinstance(v0, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self._add("l", v0, *v)
        return self

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
        self._add("C", v1, v2, v)
        return self

    def c(self, v1, v2, v):
        "Cubic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        self._add("c", v1, v2, v)
        return self

    def S(self, v2, v):
        "Shorthand cubic Beziér curveto. Absolute coordinates."
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        self._add("S", v2, v)
        return self

    def s(self, v2, v):
        "Shorthand cubic Beziér curveto. Relative coordinates."
        assert isinstance(v2, Vector2)
        assert isinstance(v, Vector2)
        self._add("s", v2, v)
        return self

    def Q(self, v1, v):
        "Quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v, Vector2)
        self._add("Q", v1, v)
        return self

    def q(self, v1, *v):
        "Quadratic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert isinstance(v, Vector2)
        self._add("q", v1, v)
        return self

    def T(self, v1, *v):
        "Shorthand quadratic  Beziér curveto. Absolute coordinates."
        assert isinstance(v1, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self._add("T", v1, v)
        return self

    def t(self, v1, *v):
        "Shorthand quadratic Beziér curveto. Relative coordinates."
        assert isinstance(v1, Vector2)
        assert all([isinstance(w, Vector2) for w in v])
        self._add("t", v1, v)
        return self

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

    def _add(self, command, *v, concatenate=True):
        bits = []
        if not (concatenate and self.parts[-1][0] == command):
            bits.append(command)
        bits.append(" ".join([f"{N(w.x)} {N(w.y)}" for w in v]))
        self.parts.append(" ".join(bits))
