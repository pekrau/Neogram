"Neogram. JSON Schema definitions of YAML content."

import jsonschema
import webcolors
import yaml

import lookup
import style


SCHEMA = {
    "$id": "https://neogram.org/schema",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Neogram",
    "description": "Neogram YAML format specification.",
    "$defs": {
        "style": style.SCHEMA,
    },
    "type": "object",
    "properties": {
        "piechart": lookup.piechart.SCHEMA,
        "timelines": lookup.timelines.SCHEMA,
        "gantt": lookup.gantt.SCHEMA,
    },
    "additionalProperties": False,
}


def validate(instance):
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

    validator = jsonschema.Draft202012Validator(
        schema=SCHEMA, format_checker=format_checker
    )
    validator.check_schema(SCHEMA)
    validator.validate(instance)
    

if __name__ == "__main__":
    for filename in ["pyramid.yaml", "universe.yaml", "project.yaml"]:
        with open(filename) as infile:
            data = yaml.safe_load(infile)
        validate(data)
