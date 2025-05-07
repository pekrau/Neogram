"All currently implemented diagrams."

import icecream

icecream.install()

import pathlib

import yaml

import constants
import diagram
import piechart
import timelines
import gantt


_entity_lookup = {}


def register(cls):
    "Add the entity class to the lookup table."
    assert issubclass(cls, diagram.Entity)
    _entity_lookup[cls.__name__.casefold()] = cls


def retrieve(filepath_or_stream):
    """Read and parse the YAML file given by its path, or an open file object.
    Return a Diagram instance.
    """
    if isinstance(filepath_or_stream, (str, pathlib.Path)):
        with open(filepath_or_stream) as infile:
            data = yaml.safe_load(infile)
    else:
        data = yaml.safe_load(filepath_or_stream)
    version = data.pop(constants.SOFTWARE.casefold(), None)
    if version != constants.__version__:
        raise ValueError(f"YAML file has wrong version {version}.")
    if len(data) != 1:
        raise ValueError("YAML file must contain exactly one top-level diagram.")
    return parse(*data.popitem())


def parse_dict(data):
    "Parse the single item in the dictionary for the entity instance given by the key."
    assert len(data) == 1
    return parse(*data.popitem())


def parse(entity, data):
    "Parse the data for the entity entity given by the key."
    try:
        cls = _entity_lookup[entity]
    except KeyError:
        raise ValueError(f"no such entity '{entity}'")
    return cls(**data)


register(piechart.Piechart)
register(piechart.Slice)

register(timelines.Timelines)
register(timelines.Event)
register(timelines.Period)

register(gantt.Gantt)
register(gantt.Task)
