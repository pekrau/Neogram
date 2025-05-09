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

    def __init__(self, title=None, width=None, entries=None):
        assert title is None or isinstance(title, str)
        assert width is None or (isinstance(width, (int, float)) and width > 0)
        assert entries is None or isinstance(entries, (tuple, list))

        self.title = title
        self.width = width or constants.DEFAULT_WIDTH
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
            result["title"] = self.title
        if self.width != constants.DEFAULT_WIDTH:
            result["width"] = self.width
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
            title["text-anchor"] = "middle"
            self.height += constants.DEFAULT_PADDING + constants.DEFAULT_FONT_DESCEND

    def save(self, target=None):
        """Output the diagram as YAML.
        If target is provided, write into file given by path or open file object.
        """
        import schema
        data = {"neogram": constants.__version__}
        data.update(self.as_dict())
        schema.validate(data)
        if isinstance(target, (str, pathlib.Path)):
            with open(target, "w") as outfile:
                yaml.dump(data, outfile, sort_keys=False)
        elif target is None:
            return yaml.dump(data, sort_keys=False)
        else:
            yaml.dump(data, outfile, sort_keys=False)


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
    if isinstance(source, (str, pathlib.Path)):
        with open(source) as infile:
            data = yaml.safe_load(infile)
    else:
        data = yaml.safe_load(source)
    try:
        version = data.pop("neogram")
    except KeyError:
        raise ValueError(
            f"YAML file must contain marker for software: 'neogram: {constants.__version__}' "
        )
    if version and version != constants.__version__:
        raise ValueError(f"YAML file has wrong version {version}.")
    if len(data) != 1:
        raise ValueError("YAML file must contain exactly one top-level diagram.")
    return parse(*data.popitem())
