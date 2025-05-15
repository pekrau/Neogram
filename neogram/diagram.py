"Abstract Diagram and Entity classes."

from icecream import ic

import json
import pathlib
import urllib.parse

import requests
import requests.exceptions
import yaml

import constants
import memo
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
        "Check that the entry is valid for the diagram. Raise ValueError otherwise."
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
        result.update(self.data_as_dict_entries())
        return result

    def data_as_dict_entries(self):
        result = []
        for entry in self.entries:
            if isinstance(entry, str):
                result.append(entry)
            else:
                result.append(entry.as_dict())
        return {"entries": result}

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
        """Create the SVG elements in the 'svg' attribute. Adds the title, if given.
        Sets the 'svg' and 'height' attributes.
        Requires the 'width' attribute.
        To be extended in subclasses.
        """
        self.height = 0
        assert hasattr(self, "width")

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
        try:
            schema.validate(data)
        except ValueError:
            with open("error.json", "w") as outfile:
                json.dump(data, outfile, sort_keys=False)
            raise
        if isinstance(target, (str, pathlib.Path)):
            with open(target, "w") as outfile:
                yaml.dump(data, outfile, allow_unicode=True, sort_keys=False)
        elif target is None:
            return yaml.dump(data, allow_unicode=True, sort_keys=False)
        else:
            yaml.dump(data, outfile, allow_unicode=True, sort_keys=False)


class Container(Diagram):
    "Diagram containing other diagrams, which may also be part of other diagrams."

    ALIGN_VALUES = None  # Must be set in inheriting class.

    def __init__(
        self,
        title=None,
        entries=None,
        align=None,
    ):
        super().__init__(title=title, entries=entries)
        assert align is None or align in self.ALIGN_VALUES

        self.align = align or self.DEFAULT_ALIGN

    def check_entry(self, entry):
        if isinstance(entry, str):
            reader = Reader(entry)
            memo.check_add(reader)
            try:
                reader.read()
                reader.read()
                reader.parse_yaml()
                reader.check_diagram_yaml()
                entry = reader.get_diagram()
            except ValueError as error:
                raise ValueError(f"error reading from '{reader}': {error}")
            memo.remove(reader)
        if not isinstance(entry, Diagram):
            raise ValueError(f"invalid entry for board: {entry}; not a Diagram")

    def data_as_dict(self):
        result = super().data_as_dict()
        if self.align != self.DEFAULT_ALIGN:
            result["align"] = self.align
        return result


# Lookup for end-use classes. Key: name of class (lower case); value: class
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
    if isinstance(data, dict):
        return cls(**data)
    elif isinstance(data, str):  # Get and parse YAML from the location.
        reader = Reader(data)
        try:
            reader.read()
            reader.read()
            reader.parse_yaml()
            reader.check_diagram_yaml()
            return reader.get_diagram()
        except ValueError as error:
            raise ValueError(f"error reading from '{reader}': {error}")


def retrieve(location):
    """Read and parse the YAML file given by its path or URI.
    Return a Diagram instance.
    """
    reader = Reader(location)
    reader.read()
    reader.parse_yaml()
    reader.check_diagram_yaml()
    return reader.get_diagram()


class Reader:
    "Read data from a location; URI or file path."

    def __init__(self, location):
        self.location = str(location)
        parts = urllib.parse.urlparse(self.location)
        self.scheme = parts.scheme
        if self.scheme:
            self.location = self.location
        elif pathlib.Path(self.location).is_absolute():
            self.scheme = "file"
        else:
            self.location = str(pathlib.Path.cwd().joinpath(self.location).resolve())
            self.scheme = "file"

    def __repr__(self):
        return f"Reader('{self.location}')"

    def read(self):
        "Read the data from the location. Raise ValueError if any problem."
        if self.scheme == "file":
            try:
                with open(self.location) as infile:
                    self.data = infile.read()
            except OSError as error:
                raise ValueError(str(error))
        else:
            try:
                response = requests.get(self.location)
                response.raise_for_status()
                self.data = response.text
            except requests.exceptions.RequestException as error:
                raise ValueError(str(error))

    def parse_yaml(self):
        "Parse the YAML data. Raise ValueError if any problem."
        try:
            self.yaml = yaml.safe_load(self.data)
        except yaml.YAMLError as error:
            raise ValueError(f"cannot interpret data as YAML: {error}")

    def check_diagram_yaml(self):
        """Check that the YAML data is valid and prepare it for diagram parsing.
        - The software marker is present, which is removed.
        - The given version is compatible with the current version.
        - There is one and only one diagram instance in it.
        - Check against the schema.
        Raise ValueError if any problem.
        """
        import schema

        copy = self.yaml.copy()
        try:
            version = copy.pop("neogram")
        except KeyError:
            raise ValueError("YAML data lacks the software marker")
        if version:
            # XXX Currently strict check.
            if version != constants.__version__:
                raise ValueError(f"YAML data incompatible version {version}")
        if len(copy) != 1:
            raise ValueError("YAML data contains more than one instance")
        # Schema validation must be done on the original data.
        schema.validate(self.yaml)
        self.prepared = copy

    def get_diagram(self):
        return parse(*self.prepared.popitem())
