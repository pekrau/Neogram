"Neogram. JSON Schema definitions of YAML content."

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
        "style": style.SCHEMA,
    },
    "type": "object",
    "properties": {
        constants.SOFTWARE.casefold(): {"type": "string"},
        "piechart": lookup.piechart.SCHEMA,
        "timelines": lookup.timelines.SCHEMA,
        "gantt": lookup.gantt.SCHEMA,
    },
    "additionalProperties": False,
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

    return jsonschema.Draft202012Validator(
        schema=SCHEMA, format_checker=format_checker
    )

def check_schema():
    get_validator().check_schema(SCHEMA)
    

def validate(instance):
    get_validator().validate(instance)


if __name__ == "__main__":
    import json
    check_schema()
    print(json.dumps(SCHEMA, indent=2))
