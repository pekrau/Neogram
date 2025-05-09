"Diagram entity lookup, retrieve function and parser."

import pathlib

import yaml

from diagram import *
from timelines import *

_entity_lookup = {}


def register_entity(cls):
    "Register the diagram or entity for parsing."
    assert issubclass(cls, Entity)
    key = cls.__name__.casefold()
    if key in _entity_lookup:
        raise KeyError(f"entity '{key}' already registered")
    _entity_lookup[key] = cls


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


def parse(key, data):
    "Parse the data for the entity given by the key."
    try:
        cls = _entity_lookup[key]
    except KeyError:
        raise ValueError(f"no such entity '{key}'")
    return cls(**data)


register_entity(Timelines)
register_entity(Event)
register_entity(Period)
