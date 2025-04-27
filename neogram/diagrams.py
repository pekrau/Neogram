"Neogram. All currently implemented diagrams."

import icecream
icecream.install()

import pathlib

import yaml

from diagram import *
from piechart import *
from timelines import *


_diagram_lookup = {}


def add_diagram(cls):
    "Add the diagram class to the parse lookup table."
    assert issubclass(cls, Diagram)
    _diagram_lookup[cls.__name__.casefold()] = cls.parse


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


add_diagram(Piechart)
add_diagram(Timelines)
