"Schema handling."

import json

import jsonschema

# import webcolors

import constants
import lib


# Schema for YAML file contents.
SCHEMA = {
    "$schema": constants.JSONSCHEMA_VERSION,
    "$id": constants.JSONSCHEMA_ID,
    "title": "Generate SVG for diagrams of different kinds from YAML specification.",
    "$defs": {
        "text": {
            "$anchor": "text",
            "oneOf": [
                {
                    "title": "Text with default styling.",
                    "type": "string",
                },
                {
                    "title": "Text with styling options.",
                    "type": "object",
                    "required": ["text"],
                    "additionalProperties": False,
                    "properties": {
                        "text": {
                            "title": "The text to display.",
                            "type": "string",
                        },
                        "size": {
                            "title": "Size of font. Default depends on context.",
                            "type": "number",
                            "exclusiveMinimum": 0,
                        },
                        "bold": {
                            "title": "Bold font.",
                            "type": "boolean",
                            "default": False,
                        },
                        "italic": {
                            "title": "Italics font.",
                            "type": "boolean",
                            "default": False,
                        },
                        "color": {
                            "title": "Color of text.",
                            "type": "string",
                            "format": "color",
                            "default": "black",
                        },
                        "placement": {
                            "title": "Placement of text. Ignored in some contexts.",
                            "enum": constants.PLACEMENTS,
                            "default": constants.CENTER,
                        },
                        "anchor": {
                            "title": "Anchor location in text. Ignored in some contexts.",
                            "enum": constants.ANCHORS,
                            "default": constants.MIDDLE,
                        },
                    },
                },
            ],
        },
        "fuzzy_number": {
            "$anchor": "fuzzy_number",
            "type": "object",
            "required": ["value"],
            "additionalProperties": False,
            "minProperties": 2,
            "properties": {
                "value": {
                    "title": "Central value for the fuzzy number.",
                    "type": "number",
                },
                "low": {
                    "title": "Low value for the fuzzy number.",
                    "type": "number",
                },
                "high": {
                    "title": "High value for the fuzzy number.",
                    "type": "number",
                },
                "error": {
                    "title": "Symmetrical error around the central value.",
                    "type": "number",
                    "exclusiveMinimum": 0,
                },
            },
        },
        "include": {
            "$anchor": "include",
            "title": "Include another YAML file from the URI reference.",
            "type": "string",
            "format": "uri-reference",
        },
        "timelines_ref": {
            "$anchor": "timelines_ref",
            "title": "Timelines",
            "oneOf": [
                {
                    "title": "Specification",
                    "$ref": "#timelines",
                },
                {
                    "title": "URI reference for specification.",
                    "$ref": "#include",
                },
            ],
        },
        "piechart_ref": {
            "$anchor": "piechart_ref",
            "title": "Piechart",
            "oneOf": [
                {
                    "title": "Specification",
                    "$ref": "#piechart",
                },
                {
                    "title": "URI reference for specification.",
                    "$ref": "#include",
                },
            ],
        },
        "note_ref": {
            "$anchor": "note_ref",
            "title": "Note",
            "oneOf": [
                {
                    "title": "Specification",
                    "$ref": "#note",
                },
                {
                    "title": "URI reference for specification.",
                    "$ref": "#include",
                },
            ],
        },
        "column_ref": {
            "$anchor": "column_ref",
            "title": "Column",
            "oneOf": [
                {
                    "title": "Specification",
                    "$ref": "#column",
                },
                {
                    "title": "URI reference for specification.",
                    "$ref": "#include",
                },
            ],
        },
        "row_ref": {
            "$anchor": "row_ref",
            "title": "Row",
            "oneOf": [
                {
                    "title": "Specification",
                    "$ref": "#row",
                },
                {
                    "title": "URI reference for specification.",
                    "$ref": "#include",
                },
            ],
        },
    },
    "type": "object",
    "required": ["neogram"],
    "additionalProperties": False,
    "minProperties": 2,  # Ensure that there is one...
    "maxProperties": 2,  # ...and only one diagram.
    "properties": {
        "neogram": {
            "title": "Identitification marker for the YAML file.",
            "oneOf": [
                {
                    "title": "Version of the Neogram sofware.",
                    "type": "string",
                },
                {
                    "title": "Unspecified version; no check performed.",
                    "const": None,
                },
            ],
        },
        # Full subschemas here, use $ref in other parts of the schema.
        "timelines": lib.Timelines.SCHEMA,
        "piechart": lib.Piechart.SCHEMA,
        "column": lib.Column.SCHEMA,
        "row": lib.Row.SCHEMA,
        "note": lib.Note.SCHEMA,
        "board": lib.Board.SCHEMA,
    },
}


def get_validator(schema):
    format_checker = jsonschema.FormatChecker(["color", "uri-reference"])

    # How to add more checkers:
    # @format_checker.checks("color")
    # def color_format(value):
    #     try:
    #         webcolors.normalize_hex(value)
    #     except ValueError:
    #         try:
    #             webcolors.name_to_hex(value)
    #         except ValueError:
    #             return False
    #     return True

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
        path = ".".join([str(p) for p in path])
        raise ValueError(f"{error.message} in instance '{path}'")
