"Diagram base class."

__all__ = ["Diagram", "Vector2", "Element", "Entity"]

import io
import pathlib

import yaml

import constants
import lookup
from minixml import Element
from vector2 import Vector2
from style import Style
from utils import N


class Entity:
    "Diagram entity; diagram itself or part of diagram."

    def as_dict(self):
        "Return as a dictionary of basic YAML values."
        return {self.__class__.__name__.casefold(): self.as_dict_content()}

    def as_dict_content(self):
        "Return the content as a dictionary of basic YAML values."
        raise NotImplementedError


class Diagram(Entity):
    "Abstract diagram."

    def __init__(self, entries=None, style=None, id=None, title=None):
        assert entries is None or isinstance(entries, (tuple, list))
        assert style is None or isinstance(style, dict)
        assert id is None or isinstance(id, str)
        assert title is None or isinstance(title, str)

        self.entries = []
        if entries:
            for entry in entries:
                self.append(entry)
        self.id = id
        self.title = title
        style = style or {}
        self.style = Style(**style)

    def __eq__(self, other):
        if not isinstance(other, Diagram) or self.__class__ != other.__class__:
            return False
        return self.as_dict() == other.as_dict()

    def __iadd__(self, other):
        self.append(other)
        return self

    def append(self, entry):
        if isinstance(entry, dict):
            entry = lookup.parse_dict(entry)
        self.check_entry(entry)
        self.entries.append(entry)

    def check_entry(self, entry):
        "Check validity of entry. Raise ValueError if any problem."
        pass

    def svg_document(self, antialias=True):
        "Return the SVG minixml element for the entire document."
        self.style.init_svg_attributes()
        svg = self.svg()  # Also sets 'origin' and 'extent'.
        if antialias:
            self.extent = self.extent + Vector2(1, 1)
            transform = "translate(0.5, 0.5)"
        else:
            transform = None
        result = Element(
            "svg",
            xmlns=constants.SVG_XMLNS,
            width=N(self.extent.x),
            height=N(self.extent.y),
            viewBox=f"{N(self.origin.x)} {N(self.origin.y)} {N(self.extent.x)} {N(self.extent.y)}",
            transform=transform,
        )
        result += svg
        assert len(self.style) == 1
        return result

    def svg(self):
        """Return the SVG minixml element for the diagram content.
        To be elaborated by inheriting class; set 'origin' and 'extent'.
        """
        self.height = 0
        self.style.init_svg_attributes()
        g = Element("g")
        if self.id:
            g["id"] = self.id
        self.style.set_svg_attribute(g, "stroke")
        self.style.set_svg_attribute(g, "stroke_width")
        if self.title:
            with self.style:
                self.height += self.style["title.font_size"] + self.style["padding"]
                g += (
                    title := Element(
                        "text", self.title, x=self.style["width"] / 2, y=self.height
                    )
                )
                self.style.set_svg_text_attributes(title, "title")
            self.height += self.style["title.descend"] + self.style["padding"]
        return g

    def as_dict_content(self):
        "Return the content as a dictionary of basic YAML values."
        result = {}
        if self.id:
            result["id"] = self.id
        if self.title:
            result["title"] = self.title
        result["entries"] = [e.as_dict() for e in self.entries]
        result.update(self.style.as_dict())
        return result

    def render(self, filepath_or_stream):
        "Render the this diagram as SVG root to a new file or open stream."
        if not self.entries:
            raise ValueError("no entries in diagram to render")
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                outfile.write(repr(self.svg_document()))
        else:
            filepath_or_stream.write(repr(self.svg_document()))

    def save(self, filepath_or_stream):
        "Write the YAML specification to the new file or open stream."
        data = {constants.SOFTWARE.casefold(): constants.__version__}
        data.update(self.as_dict())
        if isinstance(filepath_or_stream, (str, pathlib.Path)):
            with open(filepath_or_stream, "w") as outfile:
                yaml.safe_dump(data, outfile, sort_keys=False)
        else:
            yaml.safe_dump(data, filepath_or_stream, sort_keys=False)
