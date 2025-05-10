"Schema handling."

import json

import jsonschema
import webcolors

import constants
import lib


# Schema for YAML file contents.
SCHEMA = {
    "$schema": constants.JSONSCHEMA_VERSION,
    "$id": constants.JSONSCHEMA_ID,
    "$defs": {
        "title": {
            "$anchor": "title",
            "oneOf": [
                {
                    "title": "Title of the diagram with default styling.",
                    "type": "string",
                },
                {
                    "title": "Title of the diagram with styling options..",
                    "type": "object",
                    "required": ["text"],
                    "additionalProperties": False,
                    "properties": {
                        "text": {"type": "string"},
                        "size": {
                            "type": "number",
                            "exclusiveMinimum": 0, #Default depends on the diagram.
                        },
                        "bold": {"type": "boolean", "default": False},
                        "italic": {"type": "boolean", "default": False},
                        "color": {
                            "type": "string",
                            "format": "color",
                            "default": "black",
                        },
                        "anchor": {
                            "enum": ["start", "middle", "end"],
                            "default": "middle",
                        },
                    },
                },
            ],
        },
        "width": {
            "title": "Width of chart, in pixels.",
            "$anchor": "width",
            "type": "number",
            "default": constants.DEFAULT_WIDTH,
            "exclusiveMinimum": 0,
        },
    },
    "type": "object",
    "required": ["neogram"],
    "additionalProperties": False,
    "minProperties": 2,
    "maxProperties": 2,
    "properties": {
        "neogram": {
            "oneOf": [
                {"const": None},
                {"type": "string"},
            ],
        },
        "timelines": lib.Timelines.SCHEMA,
        "piechart": lib.Piechart.SCHEMA,
        "column": lib.Column.SCHEMA,
        "row": lib.Row.SCHEMA,
    },
}


def get_validator(schema):
    format_checker = jsonschema.FormatChecker()

    @format_checker.checks("color")
    def color_format(value):
        try:
            webcolors.normalize_hex(value)
        except ValueError:
            try:
                webcolors.name_to_hex(value)
            except ValueError:
                return False
        return True

    return jsonschema.Draft202012Validator(schema=schema, format_checker=format_checker)


def check_schema(schema):
    get_validator(schema).check_schema(schema)


def is_valid(instance, schema=SCHEMA):
    try:
        get_validator(schema).validate(instance)
    except jsonschema.exceptions.ValidationError as error:
        return False
    return True


def validate(instance, schema=SCHEMA, path=None):
    try:
        get_validator(schema).validate(instance)
    except jsonschema.exceptions.ValidationError as error:
        if path:
            path = [path] + list(error.path)
        else:
            path = list(error.path)
        path = ".".join(path)
        raise ValueError(f"{error.message} in instance '{path}'")


if __name__ == "__main__":
    check_schema(SCHEMA)
    with open("schema.json", "w") as outfile:
        json.dump(SCHEMA, outfile, indent=2, sort_keys=False)
