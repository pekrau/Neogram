"Abstract Diagram and Entity classes."

from icecream import ic

import pathlib

import yaml

import constants
from minixml import Element
from vector2 import *
import utils


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

    DEFAULT_FONT_SIZE = 14
    DEFAULT_TITLE_FONT_SIZE = 18

    def __init__(self, title=None, entries=None):
        assert title is None or isinstance(title, (str, dict))
        assert entries is None or isinstance(entries, (tuple, list))

        self.title = title
        self.height = 0
        self.entries = []
        if entries:
            for entry in entries:
                self.append(entry)

    def __iadd__(self, entry):
        self.append(entry)
        return self

    def append(self, entry):
        "Append the entry to the diagram."
        if isinstance(entry, dict):
            assert len(entry) == 1
            entry = parse(*entry.popitem())
        self.check_entry(entry)
        self.entries.append(entry)

    def check_entry(self, entry):
        "Check that the entry is valid for the diagram."
        raise NotImplementedError

    def data_as_dict(self):
        result = {}
        if self.title:
            if isinstance(self.title, dict):
                result["title"] = title = {"text": self.title["text"]}

                if (
                    size := self.title.get("size")
                ) is not None and size != self.DEFAULT_TITLE_FONT_SIZE:
                    title["size"] = size
                if self.title.get("bold"):
                    title["bold"] = True
                if self.title.get("italic"):
                    title["italic"] = True
                if (color := self.title.get("color")) is not None and color != "black":
                    title["color"] = color
                if (
                    anchor := self.title.get("anchor")
                ) is not None and anchor != "middle":
                    title["anchor"] = anchor
            else:
                result["title"] = self.title
        result["entries"] = [e.as_dict() for e in self.entries]
        return result

    def render(self, target=None, antialias=True, indent=2):
        """Render diagram and return SVG.
        If target is provided, write into file given by path or open file object.
        """
        if not self.entries:
            raise ValueError("no entries in diagram to render.")
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
            width=utils.N(extent.x),
            height=utils.N(extent.y),
            viewBox=f"0 0 {utils.N(extent.x)} {utils.N(extent.y)}",
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
        """Create the SVG elements in the 'svg' attribute.
        Requires that the 'width' attribute has been set. Sets the width' attributes.
        To be extended in subclasses.
        """
        assert hasattr(self, "width")
        self.height = 0
        self.svg = Element("g", stroke="black", fill="white")
        self.svg["font-family"] = constants.DEFAULT_FONT_FAMILY
        self.svg["font-size"] = self.DEFAULT_FONT_SIZE
        if self.title:
            if isinstance(self.title, dict):
                title = self.title["text"] or ""
                size = self.title.get("size") or self.DEFAULT_TITLE_FONT_SIZE
                color = self.title.get("color") or "black"
                anchor = self.title.get("anchor") or "middle"
            else:
                title = self.title
                size = self.DEFAULT_TITLE_FONT_SIZE
                color = "black"
                anchor = "middle"
            self.height += size
            self.svg += (
                title := Element(
                    "text",
                    title,
                    x=utils.N(self.width / 2),
                    y=utils.N(self.height),
                    stroke="none",
                    fill=color,
                )
            )
            title["font-size"] = size
            title["text-anchor"] = anchor
            if isinstance(self.title, dict):
                if self.title.get("bold"):
                    title["font-weight"] = "bold"
                if self.title.get("italic"):
                    title["font-style"] = "italic"
            self.height += constants.DEFAULT_PADDING + constants.FONT_DESCEND * size

    def save(self, target=None):
        """Output the diagram as YAML.
        If target is provided, write into file given by path or open file object.
        """
        import schema

        data = {"neogram": constants.__version__}
        data.update(self.as_dict())
        assert schema.is_valid(data)
        if isinstance(target, (str, pathlib.Path)):
            with open(target, "w") as outfile:
                yaml.dump(data, outfile, allow_unicode=True, sort_keys=False)
        elif target is None:
            return yaml.dump(data, allow_unicode=True, sort_keys=False)
        else:
            yaml.dump(data, outfile, allow_unicode=True, sort_keys=False)


# Key: name of class (lower case); value: class
_entity_lookup = {}


def register(cls):
    "Register the diagram or entity for parsing."
    assert issubclass(cls, Entity)
    key = cls.__name__.casefold()
    if key in _entity_lookup:
        raise KeyError(f"entity '{key}' already registered")
    _entity_lookup[key] = cls


def parse(key, data):
    "Parse the data for the entity given by the key."
    try:
        cls = _entity_lookup[key]
    except KeyError:
        raise ValueError(f"no such entity '{key}'")
    return cls(**data)


def retrieve(source):
    """Read and parse the YAML file given by its path or open file object.
    Return a Diagram instance.
    """
    import schema

    if isinstance(source, (str, pathlib.Path)):
        with open(source) as infile:
            original_data = yaml.safe_load(infile)
    else:
        original: data = yaml.safe_load(source)
    # Perform some basic tests on a copy of the data.
    data = original_data.copy()
    try:
        version = data.pop("neogram")
    except KeyError:
        raise ValueError(
            f"YAML file lacks marker for software: 'neogram: {constants.__version__}' "
        )
    # Check version compatibility.
    if version:
        major, minor, micro = version.split(".")
        if int(major) != constants.VERSION[0]:
            raise ValueError(f"YAML file incompatible version {version}")
    # Require one and only one diagram in a file.
    if len(data) != 1:
        raise ValueError("YAML file must contain exactly one diagram")
    # Schema validation must be done on the original data.
    schema.validate(original_data)
    # The copy of the original data now contains only the item to be parsed.
    return parse(*data.popitem())
