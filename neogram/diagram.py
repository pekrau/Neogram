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
    "retrieve",
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


def retrieve(filepath_or_stream):
    """Read and parse the YAML file given by its path, or an open file object.
    Return a Diagram instance.
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
    "Parse the data for the diagram instance given by the key."
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

    def __eq__(self, other):
        if not isinstance(other, Style):
            return False
        return self.as_dict() == other.as_dict()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key, value):
        if key == "palette" and isinstance(value, (tuple, list)):
            self.style["palette"] = Palette(*value)
        elif isinstance(value, dict):
            self.style[key].update(value)
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

    def setattrs_text(self, elem, background=None):
        """Set the attributes for the text element.
        If 'background' is provided and no color has been set,
        then select the best of white or black.
        """
        try:
            text = self["text"]
        except KeyError:
            return
        try:
            elem["font-family"] = text["font"]
        except KeyError:
            pass
        try:
            elem["font-size"] = text["size"]
        except KeyError:
            pass
        try:
            elem["font-weight"] = text["bold"] and "bold" or "normal"
        except KeyError:
            pass
        try:
            elem["font-style"] = text["italic"] and "italic" or "normal"
        except KeyError:
            pass
        try:
            elem["text-decoration"] = text["underline"] and "underline" or "none"
        except KeyError:
            pass
        try:
            elem["text-anchor"] = text["anchor"]
        except KeyError:
            pass
        color = text.get("color")
        if color is None:
            if background is None:
                elem["fill"] = "black"
            else:
                if not isinstance(background, Color):
                    background = Color(background)
                elem["fill"] = background.best_contrast
        else:
            elem["fill"] = str(color)
        elem["stroke"] = "none"

    def as_dict(self):
        "Return as a dictionary of simple YAML-compatible values."
        return {"style": self.as_simple_values(self.style)}

    def as_simple_values(self, data=None):
        "Return content converted to simple YAML-compatible values."
        if data is None:
            data = self.style
        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                result[key] = self.as_simple_values(value)
            elif isinstance(value, Color):
                result[key] = str(value)
            elif isinstance(value, Palette):
                result[key] = [str(c) for c in value.colors]
            elif isinstance(value, float):
                result[key] = N(value)
            else:
                result[key] = value
        return result


DEFAULT_STYLE = Style(
    stroke=Color("black"),
    fill=Color("white"),
    stroke_width=1,
    padding=2,
    rounded=2,
    palette=Palette("red", "green", "blue"),
    text=dict(size=14, anchor="middle", font="sans-serif"),
)

class Diagram:
    "Abstract diagram."

    def __init__(self, id=None, klass=None, style=None):
        assert id is None or isinstance(id, str)
        assert klass is None or isinstance(klass, str)
        assert style is None or isinstance(style, Style)
        self.id = id
        self.klass = klass
        self.style = copy.deepcopy(DEFAULT_STYLE)
        if style is not None:
            self.style.update(style)

    def __eq__(self, other):
        if not isinstance(other, Diagram) or self.__class__ != other.__class__:
            return False
        return self.as_dict() == other.as_dict()

    def viewbox(self):
        "Return tuple of Vector2(x, y) and Vector2(width, height)."
        raise NotImplementedError

    def svg(self, antialias=True):
        "Return the SVG root element including content in minixml representation."
        xy, extent = self.viewbox()
        if antialias:
            extent = extent + Vector2(1, 1)
            transform = "translate(0.5, 0.5)"
        else:
            transform = None
        svg = Element(
            "svg",
            xmlns=constants.SVG_XMLNS,
            width=N(extent.x),
            height=N(extent.y),
            viewBox=f"{N(xy.x)} {N(xy.y)} {N(extent.x)} {N(extent.y)}",
            transform=transform,
        )
        if background := self.style.get("background"):
            origin, extent = self.viewbox()
            svg += Element(
                "rect",
                x=origin.x - 1,
                y=origin.y - 1,
                width=extent.x + 2,
                height=extent.y + 2,
                fill=str(background),
                stroke="none",
            )
        svg += self.svg_content()
        return svg

    def svg_content(self):
        "Return the SVG content element in minixml representation."
        g = Element("g")
        if self.id:
            g["id"] = self.id
        if self.klass:
            g["class"] = self.klass
        return g

    def save(self, filepath_or_stream):
        "Write the YAML specification to the new file or open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                yaml.safe_dump(self.as_dict(), outfile)
        else:
            yaml.safe_dump(self.as_dict(), filepath_or_stream)

    def write(self, filepath_or_stream):
        "Write the this diagram as SVG root to a new file or open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg()))
        else:
            filepath_or_stream.write(repr(self.svg()))

    def write_content(self, filepath_or_stream):
        "Write the the SVG content of this diagram to a new file or open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg_content()))
        else:
            filepath_or_stream.write(repr(self.svg_content()))

    def write_png(self, filepath_or_stream, scale=1.0, antialias=True):
        "Write this diagram as a PNG image to a new file or open stream."
        assert scale > 0.0
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "wb") as outfile:
                inputfile = io.StringIO(repr(self.svg(antialias=antialias)))
                outfile.write(cairosvg.svg2png(file_obj=inputfile, scale=scale))
        else:
            inputfile = io.StringIO(repr(self.svg(antialias=antialias)))
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
        return self.parts.append(f"H {x:.5g}")

    def h(self, x):
        "Horizontal lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        return self.parts.append(f"h {x:.5g}")

    def V(self, x):
        "Vertical lineto. Absolute coordinates."
        assert isinstance(x, (int, float))
        return self.parts.append(f"V {x:.5g}")

    def v(self, x):
        "Vertical lineto. Relative coordinates."
        assert isinstance(x, (int, float))
        return self.parts.append(f"v {x:.5g}")

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

    def append(self, command, *v, concatenate=True):
        bits = []
        if not (concatenate and self.parts[-1][0] == command):
            bits.append(command)
        bits.append(" ".join([f"{N(w.x)} {N(w.y)}" for w in v]))
        self.parts.append(" ".join(bits))
        return self
