"Neogram. JSON Schema definitions of YAML content."

import json

import jsonschema
import webcolors
import yaml

import constants
import lookup
import style


SCHEMA = {
    "$id": constants.JSONSCHEMA_ID,
    "$schema": constants.JSONSCHEMA_VERSION,
    "title": "Neogram",
    "description": "Neogram YAML format specification.",
    "$defs": {
        "text": style.TEXT_SCHEMA,
        "style": style.SCHEMA,
    },
    "type": "object",
    "properties": {
        constants.SOFTWARE.casefold(): {
            "oneOf": [{"type": "string"}, {"const": None}],
        },
        "piechart": lookup.piechart.SCHEMA,
        "timelines": lookup.timelines.SCHEMA,
        "gantt": lookup.gantt.SCHEMA,
    },
    "additionalProperties": False,
    "required": [constants.SOFTWARE.casefold()],
    "minProperties": 2,
    "maxProperties": 2,
}


def get_validator():
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

    return jsonschema.Draft202012Validator(schema=SCHEMA, format_checker=format_checker)


def check_schema():
    get_validator().check_schema(SCHEMA)


def validate(instance):
    get_validator().validate(instance)


if __name__ == "__main__":
    check_schema()
    with open("schema.json", "w") as outfile:
        json.dump(SCHEMA, outfile, indent=2, sort_keys=False)
