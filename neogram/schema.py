"Functions for schema handling."

import jsonschema
import webcolors

import constants
import lookup


# Schema for YAML file contents.
SCHEMA = {
    "type": "object",
    "properties": {
        "neogram": {
            "oneOf": [
                {"const": None},
                {"type": "string"},
            ],
        },
        "timelines": lookup.Timelines.SCHEMA,
    },
    "required": ["neogram"],
    "additionalProperties": False,
    "minProperties": 2,
    "maxProperties": 2,
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


def validate(instance, schema=SCHEMA):
    try:
        get_validator(schema).validate(instance)
    except jsonschema.exceptions.ValidationError as error:
        path = "".join([f"['{p}']" for p in error.path])
        raise ValueError(f"{error.message}\n  instance {path}:\n    {error.instance}")
