"Neogram. JSON Schema definitions of YAML content."

import jsonschema
import webcolors
import yaml


style_content = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "palette": {"type": "array"},
        "stroke-width": {"type": "number"},
        "stroke": {"type": "string", "format": "color"},
    },
}

if __name__ == "__main__":
    data = yaml.safe_load(
        """
style:
  palette:
  - '#4c78a8'
  - '#9ecae9'
  - '#f58518'
  stroke: black
  stroke-width: 1
"""
    )
    jsonschema.validate(instance=data["style"], schema=style_content)
    # validator = jsonschema.validators.extend(
    #     jsonschema.Draft202012Validator,
    #     format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    # )
    # validator.check_schema(style_content)
    # validator(style_content).validate(data["style"])
