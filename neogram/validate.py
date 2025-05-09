"Validate the contents of the YAML file(s) against the schema."

import sys

import click
import yaml

import schema


@click.command()
@click.argument("infilepaths", required=True, nargs=-1)
def validate(infilepaths):
    for infilepath in infilepaths:
        with open(infilepath) as infile:
            data = yaml.safe_load(infile)
        try:
            schema.validate(data)
        except ValueError as error:
            sys.exit(str(error))


if __name__ == "__main__":
    validate()
