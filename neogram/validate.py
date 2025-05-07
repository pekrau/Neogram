"Validate the contents of the YAML file(s) against the schema."

import sys

import click
import jsonschema
import yaml

import schema


@click.command()
@click.argument("infilepaths", required=True, nargs=-1)
def validate(infilepaths):
    validator = schema.get_validator()
    for infilepath in infilepaths:
        with open(infilepath) as infile:
            data = yaml.safe_load(infile)
        try:
            validator.validate(data)
        except jsonschema.exceptions.ValidationError as error:
            path = "".join([f"['{p}']" for p in error.path])
            sys.exit(f"{error.message}\n  instance {path}:\n    {error.instance}")


if __name__ == "__main__":
    validate()
