"Abstract Diagram and Entity classes."

import pathlib

import yaml

import constants
from minixml import Element
from vector2 import *
from utils import N


class Entity:
    "Abstract graphical entity: diagram or part thereof."

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        if self.__class__ != other.__class__:
            return False
        return self.as_dict() == other.as_dict()

    def as_dict(self):
        return {self.__class__.__name__.casefold(): self.data_as_dict()}

    def data_as_dict(self):
        raise NotImplementedError


class Diagram(Entity):
    "Abstract diagram."

    DEFAULT_WIDTH = 500

    def __init__(self, title=None, width=None):
        assert title is None or isinstance(title, str)
        assert width is None or (isinstance(width, (int, float)) and width > 0)

        self.title = title
        self.width = width or self.DEFAULT_WIDTH
        self.height = 0

    def data_as_dict(self):
        result = {}
        if self.title:
            result["title"] = self.title
        if self.width != self.DEFAULT_WIDTH:
            result["width"] = self.width
        return result

    def render(self, target=None, antialias=True, indent=2):
        """Render diagram and return SVG.
        If target is provided, write into file given by path or open file object.
        """
        self.build()
        if antialias:
            extent = Vector2(self.width + 1, self.height + 1)
            transform = "translate(0.5, 0.5)"
        else:
            extent = Vector2(self.width, self.height)
            transform = None
        document = Element(
            "svg",
            xmlns=constants.SVG_XMLNS,
            width=N(extent.x),
            height=N(extent.y),
            viewBox=f"0 0 {N(extent.x)} {N(extent.y)}",
            transform=transform,
        )
        document += self.svg
        document.repr_indent = indent
        if isinstance(target, (str, pathlib.Path)):
            with open(target, "w") as outfile:
                outfile.write(repr(document))
        elif target is None:
            return repr(document)
        else:
            target.write(repr(document))

    def build(self):
        """Create and set the 'svg' and 'height' attributes.
        To be extended in subclasses.
        """
        self.height = 0
        self.svg = Element("g")
        self.svg["stroke"] = "black"
        self.svg["fill"] = "white"
        self.svg["font-family"] = constants.DEFAULT_FONT_FAMILY
        self.svg["font-size"] = constants.DEFAULT_FONT_SIZE
        if self.title:
            self.height += constants.DEFAULT_FONT_SIZE
            self.svg += (
                title := Element("text", self.title, x=self.width / 2, y=self.height)
            )
            title["stroke"] = "none"
            title["fill"] = "black"
            title["font-family"] = constants.DEFAULT_FONT_FAMILY
            title["font-size"] = constants.DEFAULT_FONT_SIZE
            title["text-anchor"] = "middle"
            self.height += constants.DEFAULT_PADDING + constants.DEFAULT_FONT_DESCEND

    def save(self, target=None):
        """Output the diagram as YAML.
        If target is provided, write into file given by path or open file object.
        """
        data = {"neogram": constants.__version__}
        data.update(self.as_dict())
        if isinstance(target, (str, pathlib.Path)):
            with open(target, "w") as outfile:
                yaml.dump(data, outfile, sort_keys=False)
        elif target is None:
            return yaml.dump(data, sort_keys=False)
        else:
            yaml.dump(data, outfile, sort_keys=False)
