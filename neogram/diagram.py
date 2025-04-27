"Diagram base class."

__all__ = ["Diagram", "Element"]

import io
import pathlib

import yaml

import constants
from minixml import Element
from vector2 import Vector2
from style import Style
from utils import N


class Diagram:
    "Abstract diagram."

    def __init__(self, id=None, klass=None, style=None):
        assert id is None or isinstance(id, str)
        assert klass is None or isinstance(klass, str)
        assert style is None or isinstance(style, dict)

        self.id = id
        self.klass = klass
        style = style or {}
        self.style = Style(**style)

    def __eq__(self, other):
        if not isinstance(other, Diagram) or self.__class__ != other.__class__:
            return False
        return self.as_dict() == other.as_dict()

    def viewbox(self):
        "Return tuple of Vector2(x, y) and Vector2(width, height)."
        raise NotImplementedError

    def svg_document(self, antialias=True):
        "Return the SVG minixml element for the entire document."
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
        svg += self.svg()
        assert len(self.style) == 1
        return svg

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        assert len(self.style) == 1
        g = Element("g")
        if self.id:
            g["id"] = self.id
        if self.klass:
            g["class"] = self.klass
        return g

    def write(self, filepath_or_stream):
        "Write the this diagram as SVG root to a new file or open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg_document()))
        else:
            filepath_or_stream.write(repr(self.svg_document()))

    def save(self, filepath_or_stream):
        "Write the YAML specification to the new file or open stream."
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                yaml.safe_dump(self.as_dict(), outfile, sort_keys=False)
        else:
            yaml.safe_dump(self.as_dict(), filepath_or_stream, sort_keys=False)

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
        data.update(self.style.as_dict())
        return data

    @classmethod
    def parse(cls, data):
        "Parse the data into an Diagram subclass instance."
        try:
            data["klass"] = data.pop("class")
        except KeyError:
            pass
        return cls(**data)
